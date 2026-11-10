"""
도자기 원데이 클래스 리뷰 API의 의존성 설정.

FastAPI의 Depends를 사용하여 저장소와 서비스 객체를
라우터의 핸들러에 전달한다.
"""

from typing import Annotated

from fastapi import Depends, Request

from app.clients.llm_client import LlmClient
from app.repositories.review_repository import ReviewRepository
from app.services.reply_service import ReplyService
from app.services.review_service import ReviewService


# 서버에서 하나만 사용할 ReviewRepository 객체다.
# 모든 요청이 같은 딕셔너리 저장소를 공유하도록 모듈에서 한 번만 생성한다.
review_repository = ReviewRepository()


def get_review_repository() -> ReviewRepository:
    """
    서버에서 공통으로 사용하는 리뷰 저장소를 반환한다.

    Returns:
        ReviewRepository: 싱글톤 리뷰 저장소
    """

    return review_repository


def get_llm_client(request: Request) -> LlmClient:
    """
    lifespan에서 생성한 LLM 클라이언트를 반환한다.

    Args:
        request (Request): 현재 요청과 FastAPI 앱 정보를 가진 객체

    Returns:
        LlmClient: 실제 또는 가짜 LLM 클라이언트
    """

    return request.app.state.llm_client


def get_review_service(
    repository: Annotated[
        ReviewRepository,
        Depends(get_review_repository),
    ],
) -> ReviewService:
    """
    리뷰 저장소를 주입받아 ReviewService 객체를 생성한다.

    Args:
        repository (ReviewRepository): FastAPI가 주입한 리뷰 저장소

    Returns:
        ReviewService: 리뷰 등록 및 조회 서비스
    """

    return ReviewService(repository)


def get_reply_service(
    repository: Annotated[
        ReviewRepository,
        Depends(get_review_repository),
    ],
    llm_client: Annotated[
        LlmClient,
        Depends(get_llm_client),
    ],
) -> ReplyService:
    """
    저장소와 LLM 클라이언트를 주입받아 ReplyService를 생성한다.

    Args:
        repository (ReviewRepository): 공통 리뷰 저장소
        llm_client (LlmClient): 실제 또는 가짜 LLM 클라이언트

    Returns:
        ReplyService: 강사 답글 생성 서비스
    """

    return ReplyService(
        repository,
        llm_client,
    )


# 라우터에서 반복되는 Annotated와 Depends 표현을 간단하게 사용하기 위한 별칭이다.
ReviewServiceDep = Annotated[
    ReviewService,
    Depends(get_review_service),
]


ReplyServiceDep = Annotated[
    ReplyService,
    Depends(get_reply_service),
]