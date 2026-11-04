"""
요청 및 응답 DTO의 공통 부모 모델.

파이썬 코드에서는 snake_case를 사용하고,
JSON에서는 camelCase를 사용하도록 설정한다.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """snake_case 필드를 camelCase JSON으로 변환하는 부모 모델."""

    model_config = ConfigDict(
        # student_name을 studentName처럼 자동으로 변환한다.
        alias_generator=to_camel,

        # camelCase뿐만 아니라 snake_case 이름으로도 값을 넣을 수 있게 한다.
        populate_by_name=True,
    )