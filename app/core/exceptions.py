"""
도자기 원데이 클래스 리뷰 API의 사용자 정의 예외와 예외 처리기.

서비스에서 사용자 정의 예외를 발생시키면,
FastAPI 예외 처리기가 해당 예외를 JSON 오류 응답으로 변환한다.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ReviewNotFoundError(Exception):
    """리뷰 번호에 해당하는 리뷰가 없을 때 발생하는 예외."""

    def __init__(self, review_id: int):
        # Exception 부모 클래스에 오류 메시지를 전달한다.
        super().__init__(
            f"해당 리뷰가 존재하지 않습니다. reviewId={review_id}"
        )

        # 어떤 리뷰 번호에서 발생했는지 예외 객체에도 저장한다.
        self.review_id = review_id


def register_exception_handlers(app: FastAPI) -> None:
    """
    사용자 정의 예외 처리기를 FastAPI 앱에 등록한다.

    Args:
        app (FastAPI): 예외 처리기를 등록할 FastAPI 애플리케이션
    """

    @app.exception_handler(ReviewNotFoundError)
    def handle_review_not_found(
        request: Request,
        error: ReviewNotFoundError,
    ) -> JSONResponse:
        """
        ReviewNotFoundError를 404 JSON 응답으로 변환한다.
        """

        return JSONResponse(
            status_code=404,
            content={
                "code": "ERROR_CODE_00001",
                "description": "리뷰 조회 실패",
                "detail": str(error),
            },
        )

