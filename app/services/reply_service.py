"""
저장된 리뷰를 바탕으로 강사 답글을 생성하는 서비스.

리뷰를 조회하고 별점에 맞는 프롬프트를 만든 뒤,
LLM을 비동기로 호출하여 생성된 답글을 리뷰에 저장한다.
"""

from app.clients.llm_client import LlmClient
from app.core.exceptions import ReviewNotFoundError
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import ReplyResponse


class ReplyService:
    """강사 답글 생성 비즈니스 로직."""

    def __init__(
        self,
        repository: ReviewRepository,
        llm_client: LlmClient,
    ):
        self.repository = repository
        self.llm_client = llm_client

    async def create_reply(
        self,
        review_id: int,
    ) -> ReplyResponse:
        """
        저장된 리뷰를 이용해 강사 답글을 생성한다.

        Args:
            review_id (int): 답글을 생성할 리뷰 번호

        Returns:
            ReplyResponse: 리뷰 번호와 생성된 답글

        Raises:
            ReviewNotFoundError: 리뷰가 존재하지 않을 때
            AiRequestError: LLM 호출에 실패했을 때
        """

        review = self.repository.find_by_id(review_id)

        if review is None:
            raise ReviewNotFoundError(review_id)

        instructions = self._build_instructions(review.rating)

        input_text = (
            f"수강생 이름: {review.student_name}\n"
            f"클래스 이름: {review.class_name}\n"
            f"별점: {review.rating}점\n"
            f"후기 내용: {review.content}"
        )

        # LLM 응답을 기다리는 동안 이벤트 루프는 다른 요청을 처리할 수 있다.
        reply = await self.llm_client.ask_async(
            instructions,
            input_text,
        )

        # 생성한 답글을 리뷰 엔티티에 저장한다.
        review.reply = reply
        self.repository.save(review)

        return ReplyResponse(
            review_id=review.review_id,
            reply=reply,
        )

    @staticmethod
    def _build_instructions(rating: int) -> str:
        """
        별점에 맞는 답글 작성 규칙을 만든다.
        """

        common_instruction = (
            "당신은 도자기 원데이 클래스의 친절한 강사입니다. "
            "수강생의 후기에 정중한 한국어로 2~3문장의 답글을 작성하세요. "
            "후기에서 언급하지 않은 사실이나 보상을 만들어내지 마세요. "
            "수강생 이름은 답글에서 한 번만 사용하세요."
        )

        if rating <= 2:
            tone_instruction = (
                "사과로 답글을 시작하고, 수강생이 겪은 불편을 인정한 뒤 "
                "개선 의지를 표현하세요."
            )
        elif rating == 3:
            tone_instruction = (
                "수강에 대한 감사와 함께 아쉬웠던 점을 인정하고 "
                "개선 의지를 표현하세요."
            )
        else:
            tone_instruction = (
                "감사 인사를 전하고 만족한 부분을 구체적으로 언급한 뒤 "
                "다음 클래스 참여를 자연스럽게 권유하세요."
            )

        return f"{common_instruction} {tone_instruction}"