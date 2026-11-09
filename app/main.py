"""
도자기 원데이 클래스 리뷰 API 애플리케이션.

FastAPI 앱을 생성하고 리뷰 라우터와
사용자 정의 예외 처리기를 등록한다.
"""

from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers
from app.routers.review_router import router as review_router


app = FastAPI(
    title="도자기 원데이 클래스 리뷰 API",
    description="수강 후기를 등록하고 강사 답글을 생성하는 API",
    version="0.1.0",
)


# 사용자 정의 예외 처리기를 FastAPI 앱에 등록한다.
register_exception_handlers(app)

# 리뷰 등록 및 조회 라우터를 FastAPI 앱에 등록한다.
app.include_router(review_router)