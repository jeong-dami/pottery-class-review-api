# 도자기 원데이 클래스 리뷰 API

도자기 원데이 클래스 수강 후기를 등록하고 조회하며,  
저장된 후기를 바탕으로 LLM이 강사 답글 초안을 생성하는 FastAPI 프로젝트입니다.

## 주요 기능

- 수강 후기 등록
- 수강 후기 단일 조회
- camelCase 형식의 JSON 요청 및 응답
- 사용자 정의 예외를 이용한 404 응답
- OpenAI API를 이용한 비동기 강사 답글 생성
- OpenAI 호출 실패 시 502 응답
- 별점에 따른 답글 말투 변경
- 생성된 답글을 리뷰에 저장
- 실제 OpenAI 호출 없이 확인할 수 있는 Fake LLM 지원

## 기술 스택

- Python 3.14 이상
- FastAPI
- Pydantic
- pydantic-settings
- OpenAI Responses API
- uv

## 프로젝트 구조

```text
pottery-class-review-api/
├── app/
│   ├── clients/
│   │   └── llm_client.py          # OpenAI 및 Fake LLM 클라이언트
│   ├── core/
│   │   ├── config.py              # 환경 설정
│   │   └── exceptions.py          # 사용자 정의 예외와 예외 처리기
│   ├── domain/
│   │   └── review.py              # 리뷰 엔티티
│   ├── repositories/
│   │   └── review_repository.py   # 딕셔너리 기반 리뷰 저장소
│   ├── routers/
│   │   └── review_router.py       # 리뷰 및 답글 API
│   ├── schemas/
│   │   ├── base.py                # camelCase 공통 모델
│   │   └── review.py              # 요청 및 응답 DTO
│   ├── services/
│   │   ├── review_service.py      # 리뷰 등록 및 조회 서비스
│   │   └── reply_service.py       # 강사 답글 생성 서비스
│   ├── dependencies.py            # FastAPI 의존성 함수
│   └── main.py                    # FastAPI 애플리케이션 진입점
├── .env.example                   # 환경 변수 예시
├── .gitignore
├── pyproject.toml
└── README.md
```

## 실행 방법

### 1. 저장소 복제

```bash
git clone https://github.com/jeong-dami/pottery-class-review-api.git
cd pottery-class-review-api
```

### 2. 라이브러리 설치

```bash
uv sync
```

### 3. 환경 설정

프로젝트 최상위에 `.env` 파일을 만들고 `.env.example`의 내용을 참고하여 작성합니다.

```dotenv
OPENAI_API_KEY=
OPENAI_MODEL=gpt-6-luna
OPENAI_REASONING_EFFORT=none
OPENAI_MAX_OUTPUT_TOKENS=300
OPENAI_TIMEOUT_SECONDS=30

FAKE_LLM=true
FAKE_LLM_DELAY_SECONDS=1
```

실제 OpenAI API를 호출하려면 API 키를 환경 변수 또는 `.env`에 설정하고 다음과 같이 변경합니다.

```dotenv
FAKE_LLM=false
```

개발 과정에서 실제 OpenAI API를 호출하지 않으려면 다음 설정을 사용합니다.

```dotenv
FAKE_LLM=true
```

> `.env`에는 API 키가 포함될 수 있으므로 GitHub에 커밋하지 않습니다.

### 4. 서버 실행

```bash
uv run fastapi dev
```

서버가 실행되면 다음 주소에서 API 문서를 확인할 수 있습니다.

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## API

| Method | URL | 기능 | 성공 상태 코드 |
|---|---|---|---:|
| POST | `/api/reviews` | 수강 후기 등록 | 201 |
| GET | `/api/reviews/{review_id}` | 수강 후기 단일 조회 | 200 |
| POST | `/api/reviews/{review_id}/reply` | 강사 답글 생성 | 200 |

## API 사용 예시

### 리뷰 등록

```http
POST /api/reviews
Content-Type: application/json
```

```json
{
  "studentName": "김민지",
  "className": "초보 물레 체험",
  "rating": 2,
  "content": "수업은 재미있었지만 물레를 사용하기까지 너무 오래 기다렸어요."
}
```

성공 응답:

```json
{
  "reviewId": 1,
  "studentName": "김민지",
  "className": "초보 물레 체험",
  "rating": 2,
  "content": "수업은 재미있었지만 물레를 사용하기까지 너무 오래 기다렸어요.",
  "reply": null
}
```

별점은 1점 이상 5점 이하만 입력할 수 있습니다.  
범위를 벗어난 값을 입력하면 `422 Unprocessable Entity`가 응답됩니다.

### 리뷰 조회

```http
GET /api/reviews/1
```

리뷰가 존재하면 `200 OK`와 함께 리뷰가 반환됩니다.

리뷰가 존재하지 않으면 사용자 정의 예외 처리기를 통해 다음과 같이 `404 Not Found`가 응답됩니다.

```json
{
  "code": "ERROR_CODE_00001",
  "description": "리뷰 조회 실패",
  "detail": "해당 리뷰가 존재하지 않습니다. reviewId=999"
}
```

### 강사 답글 생성

```http
POST /api/reviews/1/reply
```

요청 본문은 필요하지 않습니다.

저장된 리뷰를 조회한 후 리뷰 내용을 LLM에 전달하고, 비동기로 강사 답글을 생성합니다.

```json
{
  "reviewId": 1,
  "reply": "김민지님, 기다리게 해드려 죄송합니다. 수업은 재미있었지만 물레 사용까지 오래 기다리셔서 불편하셨을 것 같습니다. 대기 시간을 줄일 수 있도록 수업 운영을 개선하겠습니다."
}
```

생성된 답글은 리뷰에 저장되므로 이후 리뷰 조회 API에서도 확인할 수 있습니다.

OpenAI 호출에 실패하면 다음과 같이 `502 Bad Gateway`가 응답됩니다.

```json
{
  "code": "ERROR_CODE_00011",
  "description": "강사 답글 생성 실패",
  "detail": "OpenAI 호출 실패: 오류 내용"
}
```

## 별점별 답글 말투

| 별점 | 답글 생성 방식 |
|---:|---|
| 1~2점 | 사과로 시작하고 불편 사항을 인정한 뒤 개선 의지를 표현 |
| 3점 | 수강에 감사하고 아쉬운 점을 인정한 뒤 개선 의지를 표현 |
| 4~5점 | 감사 인사와 만족한 부분을 언급하고 다음 수업 참여를 권유 |

답글은 정중한 한국어 2~3문장으로 생성하며, 리뷰에 없는 사실이나 보상을 임의로 만들지 않도록 프롬프트를 구성했습니다.

## 주요 응답 상태 코드

| 상태 코드 | 설명 |
|---:|---|
| 200 | 리뷰 조회 또는 답글 생성 성공 |
| 201 | 리뷰 등록 성공 |
| 404 | 해당 번호의 리뷰가 존재하지 않음 |
| 422 | 요청값 검증 실패 |
| 502 | OpenAI API 호출 실패 |

## 비동기 처리 확인

강사 답글 API는 `async def`와 `await`를 사용하여 LLM을 비동기로 호출합니다.

답글 생성 API를 호출하면 서버 터미널에서 다음과 같은 로그를 확인할 수 있습니다.

```text
[POST /api/reviews/1/reply] thread=MainThread
```

## 참고 사항

- 리뷰는 데이터베이스가 아닌 메모리의 딕셔너리에 저장됩니다.
- 서버를 종료하거나 재시작하면 등록한 리뷰와 답글이 사라집니다.
- `FAKE_LLM=true`이면 실제 OpenAI API를 호출하지 않고 개발용 답글을 반환합니다.
- 실제 별점별 답글 결과를 확인하려면 OpenAI API 키를 설정하고 `FAKE_LLM=false`로 실행해야 합니다.
- `.env` 파일은 `.gitignore`에 포함되어 있으므로 GitHub에 올리지 않습니다.