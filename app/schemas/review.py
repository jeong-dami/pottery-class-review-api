"""
도자기 원데이 클래스 리뷰 요청 및 응답 DTO.

ReviewCreateRequest는 리뷰 등록 요청값을 검증하고,
ReviewResponse와 ReplyResponse는 API 응답 형태를 정의한다.
"""

from pydantic import Field

from app.domain.review import Review
from app.schemas.base import CamelModel


class ReviewCreateRequest(CamelModel):
    """리뷰 등록 요청 DTO."""

    # 수강생 이름: 1글자 이상 30글자 이하
    student_name: str = Field(min_length=1, max_length=30)

    # 수강한 클래스 이름: 1글자 이상 100글자 이하
    class_name: str = Field(min_length=1, max_length=100)

    # 별점: 1점 이상 5점 이하
    rating: int = Field(ge=1, le=5)

    # 후기 내용: 1글자 이상 1000글자 이하
    content: str = Field(min_length=1, max_length=1000)


class ReviewResponse(CamelModel):
    """리뷰 등록 및 조회 응답 DTO."""

    review_id: int
    student_name: str
    class_name: str
    rating: int
    content: str
    reply: str | None

    @classmethod
    def from_review(cls, review: Review) -> "ReviewResponse":
        """
        Review 엔티티를 ReviewResponse DTO로 변환한다.

        Args:
            review (Review): 저장소에서 조회한 리뷰 엔티티

        Returns:
            ReviewResponse: API 응답으로 사용할 리뷰 DTO
        """

        return cls(
            review_id=review.review_id,
            student_name=review.student_name,
            class_name=review.class_name,
            rating=review.rating,
            content=review.content,
            reply=review.reply,
        )


class ReplyResponse(CamelModel):
    """강사 답글 생성 응답 DTO."""

    review_id: int
    reply: str
