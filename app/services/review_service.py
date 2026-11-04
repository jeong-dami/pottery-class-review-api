"""
도자기 원데이 클래스 리뷰 서비스.

요청 DTO를 Review 엔티티로 변환해 저장하고,
저장소에서 조회한 엔티티를 응답 DTO로 변환한다.
"""

from app.core.exceptions import ReviewNotFoundError
from app.domain.review import Review
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import ReviewCreateRequest, ReviewResponse


class ReviewService:
    """리뷰 등록 및 조회 비즈니스 로직."""

    def __init__(self, repository: ReviewRepository):
        # 의존성 함수에서 전달받은 리뷰 저장소를 보관한다.
        self.repository = repository

    def create_review(
        self,
        request: ReviewCreateRequest,
    ) -> ReviewResponse:
        """
        새로운 리뷰를 등록한다.

        Args:
            request (ReviewCreateRequest): 검증이 완료된 리뷰 등록 요청

        Returns:
            ReviewResponse: 저장된 리뷰 응답
        """

        # 요청 DTO를 Review 엔티티로 변환한다.
        # 신규 리뷰이므로 review_id는 0으로 설정한다.
        review = Review(
            review_id=0,
            student_name=request.student_name,
            class_name=request.class_name,
            rating=request.rating,
            content=request.content,
        )

        # 저장소가 신규 리뷰 번호를 부여하고 딕셔너리에 저장한다.
        saved_review = self.repository.save(review)

        # 엔티티를 API 응답 DTO로 변환한다.
        return ReviewResponse.from_review(saved_review)

    def find_review(self, review_id: int) -> ReviewResponse:
        """
        리뷰 번호로 리뷰 하나를 조회한다.

        Args:
            review_id (int): 조회할 리뷰 번호

        Returns:
            ReviewResponse: 조회된 리뷰 응답

        Raises:
            ReviewNotFoundError: 해당 번호의 리뷰가 존재하지 않을 때
        """

        review = self.repository.find_by_id(review_id)

        # 저장소는 없는 리뷰를 조회하면 None을 반환한다.
        # 서비스가 이를 사용자 정의 예외로 변환한다.
        if review is None:
            raise ReviewNotFoundError(review_id)

        return ReviewResponse.from_review(review)