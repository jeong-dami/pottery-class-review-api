# 도자기 원데이 클래스 리뷰 API

도자기 원데이 클래스 수강생이 후기를 등록하고 조회하며,
LLM을 이용해 강사의 답글 초안을 생성하는 FastAPI 프로젝트입니다.

## 주요 기능

- 수강 후기 등록
- 수강 후기 단일 조회
- 존재하지 않는 후기의 404 예외 처리
- LLM을 이용한 비동기 강사 답글 생성
- 별점에 따른 답글 말투 변경
- 생성된 답글 저장

## 기술 스택

- Python
- FastAPI
- Pydantic
- OpenAI API
- uv
- pytest

## API

| Method | URL | 기능 |
|---|---|---|
| POST | `/api/reviews` | 수강 후기 등록 |
| GET | `/api/reviews/{review_id}` | 수강 후기 조회 |
| POST | `/api/reviews/{review_id}/reply` | 강사 답글 생성 |