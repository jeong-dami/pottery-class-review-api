"""
도자기 원데이 클래스 리뷰 API의 환경 설정.

환경 변수 또는 프로젝트 최상위의 .env 파일에서
OpenAI와 가짜 LLM 관련 설정을 읽는다.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# config.py에서 세 단계 위에 있는 프로젝트 최상위 폴더다.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """환경 변수와 .env 파일에서 읽어 오는 애플리케이션 설정."""

    model_config = SettingsConfigDict(
        # 프로젝트 최상위의 .env 파일을 읽는다.
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",

        # Settings에 정의하지 않은 환경 변수는 무시한다.
        extra="ignore",
    )

    # OpenAI API 키다.
    # SecretStr를 사용하면 출력할 때 실제 값 대신 별표로 표시된다.
    openai_api_key: SecretStr | None = None

    # OpenAI 요청에 사용할 모델이다.
    openai_model: str = "gpt-6-luna"

    # 모델의 추론 정도다.
    openai_reasoning_effort: Literal[
        "none",
        "minimal",
        "low",
        "medium",
        "high",
        "xhigh",
    ] = "none"

    # LLM이 생성할 최대 출력 토큰 수다.
    openai_max_output_tokens: int = Field(
        default=300,
        gt=0,
    )

    # OpenAI 응답을 기다릴 최대 시간이다.
    openai_timeout_seconds: float = Field(
        default=30.0,
        gt=0,
    )

    # 실제 OpenAI 대신 가짜 LLM을 사용할지 결정한다.
    fake_llm: bool = False

    # 가짜 LLM이 응답하기 전 기다릴 시간이다.
    fake_llm_delay_seconds: float = Field(
        default=1.0,
        ge=0,
    )


@lru_cache
def get_settings() -> Settings:
    """
    설정 객체를 한 번만 생성하여 재사용한다.

    Returns:
        Settings: 환경 변수와 .env에서 읽은 설정
    """

    return Settings()