"""
도자기 원데이 클래스 리뷰 도메인 객체.

데이터베이스 대신 딕셔너리 저장소를 사용하므로
DB 매핑 기능이 없는 단순한 데이터 클래스다.

파이썬 코드에서는 snake_case를 사용하고,
JSON의 camelCase 변환은 schemas 패키지의 DTO가 담당한다.
"""

from dataclasses import dataclass


@dataclass
class Review:
    """도자기 원데이 클래스 수강 후기."""

    # 리뷰 식별자
    # 신규 리뷰는 0으로 생성하고 저장소가 저장할 때 1, 2, 3... 순서로 번호를 부여한다.
    review_id: int

    # 후기를 작성한 수강생 이름
    student_name: str

    # 수강한 도자기 클래스 이름
    # 예: "초보 물레 체험", "나만의 머그컵 만들기"
    class_name: str

    # 수강생이 남긴 별점
    # 1~5 범위 검증은 요청 DTO에서 Pydantic이 담당한다.
    rating: int

    # 수강생이 작성한 후기 내용
    content: str

    # LLM이 생성한 강사 답글
    # 리뷰를 처음 등록했을 때는 답글이 없으므로 None을 기본값으로 사용한다.
    reply: str | None = None