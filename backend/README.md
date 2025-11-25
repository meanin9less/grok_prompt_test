# Grok API Backend

FastAPI를 사용한 Grok API 백엔드 서버

## 프로젝트 구조

```
backend/
├── main.py                 # FastAPI 진입점
├── requirements.txt        # Python 패키지
├── .env                    # 환경 변수 (로컬)
├── .env.example            # 환경 변수 템플릿
├── config/
│   ├── __init__.py
│   └── settings.py         # 설정 관리
├── routes/
│   ├── __init__.py
│   └── grok.py             # Grok API 엔드포인트
├── services/
│   ├── __init__.py
│   └── grok_service.py     # Grok API 호출 로직
└── utils/
    ├── __init__.py
    └── exceptions.py       # 커스텀 에러
```

## 설치 및 실행

### 1. 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example`을 참고하여 `.env` 파일 생성:

```bash
# .env
GROK_API_KEY=your_grok_api_key_here
GROK_API_BASE_URL=https://api.x.ai/v1
GROK_MODEL=grok-4-1-fast-reasoning
DEBUG=True
```

### 3. 서버 실행

```bash
python main.py
```

서버가 `http://localhost:8000`에서 시작됩니다.

## API 엔드포인트

### 1. 채팅 (POST /api/grok/chat)

사용자 메시지를 Grok API에 보내고 응답을 받습니다.

**요청:**
```json
{
  "message": "안녕하세요"
}
```

**응답:**
```json
{
  "response": "안녕하세요! 어떻게 도와드릴까요?"
}
```

### 2. 헬스 체크 (GET /api/grok/health)

서버 상태를 확인합니다.

**응답:**
```json
{
  "status": "healthy",
  "service": "grok-api"
}
```

## 주요 파일 설명

### config/settings.py

환경 변수를 로드하고 설정을 관리합니다.

```python
class Settings(BaseSettings):
    grok_api_key: str
    grok_api_base_url: str
    grok_model: str
    debug: bool
```

### services/grok_service.py

Grok API와 통신하는 핵심 로직입니다.

```python
async def chat(self, message: str) -> str:
    # Grok API에 메시지 전송
    # 전체 응답 반환
```

**동작 흐름:**
1. 사용자 메시지를 Grok API에 POST
2. JSON 응답 수신
3. `choices[0].message.content` 추출
4. 전체 텍스트 반환

### routes/grok.py

FastAPI 라우터로 HTTP 엔드포인트를 정의합니다.

```python
@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    # 요청 검증
    # grok_service.chat() 호출
    # 응답 반환
```

## 설정값

| 설정 | 설명 | 기본값 |
|------|------|--------|
| `GROK_API_KEY` | Grok API 인증 키 | 필수 |
| `GROK_API_BASE_URL` | Grok API 기본 URL | `https://api.x.ai/v1` |
| `GROK_MODEL` | 사용할 모델 | `grok-4-1-fast-reasoning` |
| `DEBUG` | 디버그 모드 | `False` |

## 오류 처리

API는 다음과 같은 오류를 반환합니다:

- **400**: 빈 메시지
- **500**: Grok API 오류

```json
{
  "detail": "오류 메시지"
}
```

## 자동 문서

FastAPI는 자동으로 API 문서를 생성합니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 기술 스택

- **FastAPI**: 웹 프레임워크
- **httpx**: 비동기 HTTP 클라이언트
- **Pydantic**: 데이터 검증
- **python-dotenv**: 환경 변수 관리

## 실행 예제

```bash
# 서버 실행
python main.py

# 다른 터미널에서 테스트
curl -X POST http://localhost:8000/api/grok/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕"}'
```

## 라이선스

MIT
