"""
강사 답글을 생성하기 위한 LLM 클라이언트.

OpenAiLlmClient는 실제 OpenAI를 비동기로 호출하고,
OpenAiSyncLlmClient는 실제 OpenAI를 동기로 호출한다.
FakeLlmClient와 FakeSyncLlmClient는 실제 API를 호출하지 않고
개발 및 테스트용 가짜 응답을 반환한다.
"""

import asyncio
import time

import openai

from app.core.config import Settings
from app.core.exceptions import AiRequestError


class OpenAiLlmClient:
    """OpenAI Responses API를 비동기로 호출하는 클라이언트."""

    def __init__(self, settings: Settings):
        # 호출에 필요한 모델명, 토큰 수, 제한 시간 등의 설정을 보관한다.
        self.settings = settings

        # lifespan을 통하지 않고 이 클래스를 직접 생성할 경우를 대비한 검사다.
        if settings.openai_api_key is None:
            raise ValueError(
                "OPENAI_API_KEY가 없어 OpenAI 클라이언트를 만들 수 없습니다."
            )

        # SecretStr에 저장된 실제 API 키 문자열을 꺼낸다.
        api_key = settings.openai_api_key.get_secret_value()

        # AsyncOpenAI는 await를 사용해 비동기 요청을 보낼 수 있는 클라이언트다.
        self._client = openai.AsyncOpenAI(
            api_key=api_key,
            timeout=settings.openai_timeout_seconds,
            max_retries=1,
        )

    async def ask_async(
        self,
        instructions: str,
        input_text: str,
    ) -> str:
        """
        OpenAI에 비동기 요청을 보내고 생성된 답글을 반환한다.

        Args:
            instructions (str): LLM의 역할과 답변 규칙
            input_text (str): LLM에 전달할 리뷰 정보

        Returns:
            str: LLM이 생성한 강사 답글

        Raises:
            AiRequestError: OpenAI 호출에 실패하거나 빈 응답을 반환한 경우
        """

        try:
            response = await self._client.responses.create(
                # 사용할 OpenAI 모델
                model=self.settings.openai_model,

                # 강사의 역할과 답글 작성 규칙
                instructions=instructions,

                # 저장된 리뷰 정보가 포함된 입력
                input=input_text,

                # 답글이 지나치게 길어지는 것을 제한한다.
                max_output_tokens=self.settings.openai_max_output_tokens,

                # 모델의 추론 정도
                reasoning={
                    "effort": self.settings.openai_reasoning_effort,
                },

                # 입력과 응답을 OpenAI 서버에 저장하지 않는다.
                store=False,
            )
        except openai.OpenAIError as error:
            # OpenAI 라이브러리 예외를 우리 API의 사용자 정의 예외로 변환한다.
            raise to_ai_request_error(error) from error

        # 공백을 제거한 실제 답글을 꺼낸다.
        reply = response.output_text.strip()

        # 정상 응답이지만 답글 내용이 비어 있는 경우도 실패로 처리한다.
        if not reply:
            raise AiRequestError("OpenAI가 빈 답글을 반환했습니다.")

        return reply

    async def close(self) -> None:
        """OpenAI 비동기 클라이언트의 네트워크 연결을 종료한다."""

        await self._client.close()


def to_ai_request_error(
    error: openai.OpenAIError,
) -> AiRequestError:
    """
    OpenAI 라이브러리 예외를 사용자 정의 예외로 변환한다.

    Args:
        error (openai.OpenAIError): OpenAI 호출 중 발생한 예외

    Returns:
        AiRequestError: API에서 502로 처리할 사용자 정의 예외
    """

    # API 키가 잘못됐거나 사용할 수 없는 경우
    if isinstance(error, openai.AuthenticationError):
        return AiRequestError(
            "OpenAI API 키가 올바르지 않습니다. "
            "OPENAI_API_KEY를 확인하세요."
        )

    # 요청 한도 초과 또는 계정의 사용 가능 금액이 부족한 경우
    if isinstance(error, openai.RateLimitError):
        return AiRequestError(
            "OpenAI 요청 한도를 넘었거나 충전 잔액이 부족합니다."
        )

    # 설정한 제한 시간 안에 응답을 받지 못한 경우
    # APITimeoutError는 APIConnectionError보다 먼저 검사해야 한다.
    if isinstance(error, openai.APITimeoutError):
        return AiRequestError(
            "OpenAI 응답이 제한 시간 안에 오지 않았습니다."
        )

    # 인터넷 연결, 방화벽 등의 문제로 서버에 연결하지 못한 경우
    if isinstance(error, openai.APIConnectionError):
        return AiRequestError(
            "OpenAI 서버에 연결할 수 없습니다."
        )

    # 잘못된 모델명, 요청 형식 오류, OpenAI 서버 오류 등
    return AiRequestError(f"OpenAI 호출 실패: {error}")


class OpenAiSyncLlmClient:
    """OpenAI Responses API를 동기로 호출하는 클라이언트."""

    def __init__(self, settings: Settings):
        # 호출에 필요한 모델명, 토큰 수, 제한 시간 등의 설정을 보관한다.
        self.settings = settings

        # API 키 없이 실제 OpenAI 클라이언트를 생성하지 않도록 검사한다.
        if settings.openai_api_key is None:
            raise ValueError(
                "OPENAI_API_KEY가 없어 OpenAI 클라이언트를 만들 수 없습니다."
            )

        # SecretStr에 저장된 실제 API 키 문자열을 꺼낸다.
        api_key = settings.openai_api_key.get_secret_value()

        # OpenAI는 await를 사용하지 않는 동기 클라이언트다.
        self._client = openai.OpenAI(
            api_key=api_key,
            timeout=settings.openai_timeout_seconds,
            max_retries=1,
        )

    def ask(
        self,
        instructions: str,
        input_text: str,
    ) -> str:
        """
        OpenAI에 동기 요청을 보내고 생성된 답글을 반환한다.

        Args:
            instructions (str): LLM의 역할과 답변 규칙
            input_text (str): LLM에 전달할 리뷰 정보

        Returns:
            str: LLM이 생성한 강사 답글

        Raises:
            AiRequestError: OpenAI 호출에 실패하거나 빈 응답을 반환한 경우
        """

        try:
            response = self._client.responses.create(
                # 사용할 OpenAI 모델
                model=self.settings.openai_model,

                # 강사의 역할과 답글 작성 규칙
                instructions=instructions,

                # 저장된 리뷰 정보가 포함된 입력
                input=input_text,

                # 답글이 지나치게 길어지는 것을 제한한다.
                max_output_tokens=self.settings.openai_max_output_tokens,

                # 모델의 추론 정도
                reasoning={
                    "effort": self.settings.openai_reasoning_effort,
                },

                # 입력과 응답을 OpenAI 서버에 저장하지 않는다.
                store=False,
            )
        except openai.OpenAIError as error:
            # 비동기 클라이언트와 동일한 사용자 정의 예외로 변환한다.
            raise to_ai_request_error(error) from error

        # 공백을 제거한 실제 답글을 꺼낸다.
        reply = response.output_text.strip()

        # 답글 내용이 비어 있는 경우도 실패로 처리한다.
        if not reply:
            raise AiRequestError("OpenAI가 빈 답글을 반환했습니다.")

        return reply

    def close(self) -> None:
        """OpenAI 동기 클라이언트의 네트워크 연결을 종료한다."""

        self._client.close()


class FakeLlmClient:
    """
    실제 OpenAI를 호출하지 않는 비동기 개발용 클라이언트.

    비동기 응답 대기 시간만 흉내 내고 정해진 답글을 반환한다.
    """

    def __init__(self, settings: Settings):
        self.delay_seconds = settings.fake_llm_delay_seconds

    async def ask_async(
        self,
        instructions: str,
        input_text: str,
    ) -> str:
        """
        설정된 시간만큼 비동기로 기다린 후 가짜 답글을 반환한다.

        Args:
            instructions (str): 실제 클라이언트와 동일한 지시문
            input_text (str): 실제 클라이언트와 동일한 리뷰 정보

        Returns:
            str: 개발 및 테스트용 가짜 답글
        """

        # time.sleep과 달리 이벤트 루프를 막지 않는다.
        # 기다리는 동안 FastAPI가 다른 요청을 처리할 수 있다.
        await asyncio.sleep(self.delay_seconds)

        return (
            "(가짜 비동기 답글) 소중한 후기를 남겨주셔서 감사합니다. "
            "더 좋은 수업을 준비하겠습니다."
        )

    async def close(self) -> None:
        """가짜 클라이언트는 닫을 연결이 없으므로 아무 작업도 하지 않는다."""

        pass


class FakeSyncLlmClient:
    """
    실제 OpenAI를 호출하지 않는 동기 개발용 클라이언트.

    현재 작업 스레드를 설정된 시간 동안 기다리게 한 뒤
    정해진 답글을 반환한다.
    """

    def __init__(self, settings: Settings):
        self.delay_seconds = settings.fake_llm_delay_seconds

    def ask(
        self,
        instructions: str,
        input_text: str,
    ) -> str:
        """
        설정된 시간만큼 동기로 기다린 후 가짜 답글을 반환한다.

        Args:
            instructions (str): 실제 클라이언트와 동일한 지시문
            input_text (str): 실제 클라이언트와 동일한 리뷰 정보

        Returns:
            str: 개발 및 테스트용 가짜 동기 답글
        """

        # 현재 요청을 처리하는 작업 스레드를 지정된 시간 동안 멈춘다.
        time.sleep(self.delay_seconds)

        return (
            "(가짜 동기 답글) 소중한 후기를 남겨주셔서 감사합니다. "
            "더 좋은 수업을 준비하겠습니다."
        )

    def close(self) -> None:
        """가짜 클라이언트는 닫을 연결이 없으므로 아무 작업도 하지 않는다."""

        pass


# 비동기 서비스와 의존성 함수에서 사용할 공통 타입 이름이다.
LlmClient = OpenAiLlmClient | FakeLlmClient

# 동기 서비스와 의존성 함수에서 사용할 공통 타입 이름이다.
SyncLlmClient = OpenAiSyncLlmClient | FakeSyncLlmClient