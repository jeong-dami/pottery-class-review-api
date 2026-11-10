"""
도자기 원데이 클래스 리뷰 API 애플리케이션.

FastAPI 앱을 생성하고 리뷰 라우터와
사용자 정의 예외 처리기를 등록한다.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.llm_client import FakeLlmClient, OpenAiLlmClient
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.routers.review_router import router as review_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    서버 시작 시 LLM 클라이언트를 생성하고,
    서버 종료 시 연결을 정리한다.
    """

    settings = get_settings()

    if settings.fake_llm or settings.openai_api_key is None:
        llm_client = FakeLlmClient(settings)

        print(
            "[lifespan] 가짜 LLM 클라이언트를 사용합니다. "
            f"응답 지연={settings.fake_llm_delay_seconds}초"
        )
    else:
        llm_client = OpenAiLlmClient(settings)

        print(
            "[lifespan] OpenAI 클라이언트를 사용합니다. "
            f"model={settings.openai_model}"
        )

    # 서버 실행 중 모든 요청이 같은 클라이언트를 공유한다.
    app.state.llm_client = llm_client

    try:
        # 서버가 요청을 처리하는 구간이다.
        yield
    finally:
        # 서버 종료 시 클라이언트 연결을 닫는다.
        await llm_client.close()


app = FastAPI(
    title="도자기 원데이 클래스 리뷰 API",
    description="수강 후기를 등록하고 강사 답글을 생성하는 API",
    version="0.1.0",
    lifespan=lifespan,
)


# 사용자 정의 예외 처리기를 FastAPI 앱에 등록한다.
register_exception_handlers(app)

# 리뷰 등록 및 조회 라우터를 FastAPI 앱에 등록한다.
app.include_router(review_router)