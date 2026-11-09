"""
도자기 원데이 클래스 리뷰 라우터.

HTTP 요청을 받아 ReviewService에 전달하고,
서비스가 반환한 DTO를 응답으로 반환한다.
"""

from fastapi import APIRouter

from app.dependencies import ReviewServiceDep
from app.schemas.review import ReviewCreateRequest, ReviewResponse


router = APIRouter(
    # 이 라우터의 모든 주소 앞에 붙는 공통 경로다.
    prefix="/api/reviews",

    # Swagger 문서에서 API를 묶어 표시할 이름이다.
    tags=["리뷰"],
)



@router.post(
    "",
    status_code=201,
    summary="도자기 클래스 리뷰 등록",
)
def create_review(
    request: ReviewCreateRequest,
    service: ReviewServiceDep,
) -> ReviewResponse:
    """
    새로운 도자기 클래스 리뷰를 등록한다.

    FastAPI가 JSON 요청 본문을 ReviewCreateRequest로 변환하면서
    필드의 길이와 별점 범위를 자동으로 검증한다.
    """

    return service.create_review(request)


@router.get(
    "/{review_id}",
    summary="도자기 클래스 리뷰 하나 조회",
)
def find_review(
    review_id: int,
    service: ReviewServiceDep,
) -> ReviewResponse:
    """
    리뷰 번호로 리뷰 하나를 조회한다.

    리뷰가 존재하지 않으면 ReviewService에서
    ReviewNotFoundError가 발생한다.
    """

    return service.find_review(review_id)