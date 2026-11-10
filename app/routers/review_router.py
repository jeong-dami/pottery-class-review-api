"""
도자기 원데이 클래스 리뷰 라우터.

HTTP 요청을 받아 ReviewService에 전달하고,
서비스가 반환한 DTO를 응답으로 반환한다.
"""

import threading

from fastapi import APIRouter

from app.dependencies import ReviewServiceDep, ReplyServiceDep
from app.schemas.review import (
    ReviewCreateRequest, 
    ReviewResponse,
    ReplyResponse,
)


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


@router.post(
    "/{review_id}/reply",
    summary="도자기 클래스 강사 답글 생성",
)
async def create_reply(
    review_id: int,
    service: ReplyServiceDep,
) -> ReplyResponse:
    """
    저장된 리뷰를 바탕으로 강사 답글 초안을 비동기로 생성한다.

    생성된 답글은 리뷰에 저장되며,
    리뷰 조회 응답에서도 확인할 수 있다.
    """

    thread_name = threading.current_thread().name

    print(
        f"[POST /api/reviews/{review_id}/reply] "
        f"thread={thread_name}"
    )

    return await service.create_reply(review_id)