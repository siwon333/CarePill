# CarePill Project - 코드베이스 분석 보고서

**분석일**: 2025-10-01
**브랜치**: develop-voice
**프로젝트 타입**: Django 4.2.7 기반 의약품 분석 시스템

---

## 📊 프로젝트 개요

CarePill은 OpenAI GPT-4o-mini 비전 API를 활용한 의약품 이미지 분석 플랫폼입니다.

### 핵심 기능
1. **약봉투 글씨 인식** (`envelope`) - 처방전 정보 추출
2. **복용시간 인식** (`schedule`) - 복용 스케줄 분석
3. **약 외관 식별** (`appearance`) - 약물 형태, 색상, 각인 정보 분석

---

## 🏗️ 아키텍처 분석

### Django 앱 구조

```
CarePill/
├── medicine_analyzer/          # 메인 분석 앱
│   ├── models.py              # MedicineAnalysis 모델
│   ├── views.py               # 비즈니스 로직 & API 통합
│   ├── urls.py                # URL 라우팅
│   ├── templates/             # HTML 템플릿
│   │   ├── base.html         # 기본 레이아웃
│   │   ├── home.html         # 메인 페이지
│   │   ├── analysis_detail.html  # 분석 결과 상세
│   │   └── analysis_history.html # 분석 히스토리
│   └── migrations/            # DB 마이그레이션
│
├── medicine_project/          # Django 프로젝트 설정
│   ├── settings.py           # 환경 설정
│   ├── urls.py               # 루트 URL 설정
│   ├── wsgi.py              # WSGI 애플리케이션
│   └── asgi.py              # ASGI 애플리케이션
│
├── media/                    # 업로드된 이미지 저장소
├── .claude/                  # Claude 설정
├── claudedocs/              # 프로젝트 문서
└── requirements.txt         # Python 의존성
```

---

## 📦 데이터 모델 분석

### MedicineAnalysis Model
**파일**: `medicine_analyzer/models.py:4-24`

```python
class MedicineAnalysis(models.Model):
    analysis_type = CharField(max_length=20, choices=ANALYSIS_TYPES)
    image = ImageField(upload_to='medicine_images/')
    analysis_result = TextField(blank=True)
    medicine_name = CharField(max_length=200, blank=True)
    dosage_schedule = CharField(max_length=100, blank=True)
    created_at = DateTimeField(default=timezone.now)
```

**분석 타입**:
- `envelope`: 약봉투 글씨 인식
- `schedule`: 복용시간 인식
- `appearance`: 약 외관 식별

**데이터 흐름**:
1. 사용자 → 이미지 업로드 + 분석 타입 선택
2. `MedicineAnalysis` 레코드 생성
3. OpenAI Vision API 호출
4. 분석 결과 저장 (`analysis_result` 필드)
5. JSON 파싱 → UI 렌더링

---

## 🔌 API 통합 분석

### OpenAI Vision API 사용 패턴
**파일**: `medicine_analyzer/views.py`

#### 1. 클라이언트 초기화 (안전한 패턴)
**라인**: `views.py:13-21`

```python
def get_openai_client():
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your-openai-api-key-here':
        raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
    return openai.OpenAI(api_key=settings.OPENAI_API_KEY)
```

**장점**:
- 지연 초기화로 설정 오류 방지
- API 키 유효성 검증

**개선 필요**:
- 환경변수 미설정 시 명확한 에러 메시지
- API 키 포맷 검증 추가

#### 2. 이미지 인코딩
**라인**: `views.py:39-46`

```python
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
```

**현재 구현**: Base64 인코딩 → OpenAI API 전송

**잠재적 이슈**:
- 대용량 이미지 처리 시 메모리 부담
- 파일 포맷 검증 부재

#### 3. 분석 함수 패턴 (3가지 타입)

##### A. 약봉투 분석 (`analyze_medicine_envelope`)
**라인**: `views.py:48-95`

**프롬프트 구조**:
```json
{
  "medicine_name": "약품명",
  "dosage_instructions": "복용법",
  "frequency": "복용횟수",
  "prescription_number": "처방전 번호"
}
```

**모델**: `gpt-4o-mini`
**Temperature**: `0.1` (일관된 결과)
**Max Tokens**: `500`

##### B. 복용시간 분석 (`analyze_dosage_schedule`)
**라인**: `views.py:97-144`

**프롬프트 구조**:
```json
{
  "morning": "아침 복용 정보",
  "lunch": "점심 복용 정보",
  "evening": "저녁 복용 정보",
  "meal_timing": "식전/식후 여부"
}
```

##### C. 약 외관 식별 (`identify_medicine_appearance`)
**라인**: `views.py:146-195`

**프롬프트 구조**:
```json
{
  "shape": "약물 형태",
  "color": "색상",
  "size": "크기",
  "marking": "각인 정보",
  "estimated_name": "추정 약물명",
  "warnings": "주의사항"
}
```

**Max Tokens**: `600` (더 상세한 정보)

---

## 🔄 비즈니스 로직 흐름

### 1. 메인 페이지 (`home`)
**라인**: `views.py:197-209`

```
GET /
→ 최근 분석 5개 조회
→ API 연결 테스트 (선택적, ?test_api 파라미터)
→ home.html 렌더링
```

### 2. 업로드 및 분석 (`upload_and_analyze`)
**라인**: `views.py:211-267`

```
POST /upload/
→ 분석 타입 & 이미지 검증
→ API 키 확인
→ MedicineAnalysis 레코드 생성
→ 분석 함수 호출 (타입별 분기)
→ 결과 저장
→ 분석 상세 페이지로 리디렉션
```

**에러 처리**:
- 이미지 누락 → 에러 메시지
- API 키 미설정 → 에러 메시지
- 분석 실패 → 예외 캐치 & 로깅

### 3. 분석 결과 상세 (`analysis_detail`)
**라인**: `views.py:269-292`

```
GET /analysis/<id>/
→ MedicineAnalysis 조회
→ JSON 결과 파싱 (코드 블록 제거 로직 포함)
→ analysis_detail.html 렌더링
```

**JSON 파싱 로직** (`views.py:278-286`):
```python
if '```json' in result_text:
    result_text = result_text.split('```json')[1].split('```')[0].strip()
```

**개선 필요**: 정규식 기반 파싱으로 강화

### 4. 분석 히스토리 (`analysis_history`)
**라인**: `views.py:294-297`

```
GET /history/
→ 전체 분석 기록 조회 (최신순)
→ analysis_history.html 렌더링
```

---

## ⚙️ 설정 분석

### Django Settings (`medicine_project/settings.py`)

#### 보안 설정
**라인**: `settings.py:7-9`
```python
SECRET_KEY = ''  # ⚠️ 비어있음 - 환경변수 이동 필요
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']  # ⚠️ 프로덕션에서 위험
```

**개선 사항**:
- `SECRET_KEY`를 `.env`로 이동
- `ALLOWED_HOSTS` 프로덕션용 설정 분리

#### OpenAI 설정
**라인**: `settings.py:86`
```python
OPENAI_API_KEY = ''  # ⚠️ 비어있음
```

**현재 상태**: `.env` 파일에서 로드해야 함
**권장**: `config('OPENAI_API_KEY')` 사용

#### 미디어 파일 설정
**라인**: `settings.py:82-83`
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**정상 작동**: 이미지 업로드 경로 설정됨

#### 데이터베이스
**라인**: `settings.py:51-56`
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**현재**: SQLite (개발용 적합)
**프로덕션 고려**: PostgreSQL 마이그레이션

---

## 🌐 URL 라우팅 분석

### App URLs (`medicine_analyzer/urls.py`)

```python
urlpatterns = [
    path('', views.home, name='home'),                              # 메인
    path('upload/', views.upload_and_analyze, name='upload_and_analyze'),  # 업로드
    path('analysis/<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),  # 상세
    path('history/', views.analysis_history, name='analysis_history'),  # 히스토리
]
```

**API 엔드포인트 구조**:
- `/` - 메인 페이지
- `/upload/` - 분석 요청
- `/analysis/<id>/` - 결과 조회
- `/history/` - 전체 기록

---

## 🎨 프론트엔드 구조

### 템플릿 파일
```
medicine_analyzer/templates/
├── base.html              # 기본 레이아웃
├── home.html             # 업로드 폼
├── analysis_detail.html  # 분석 결과 (JSON 렌더링)
└── analysis_history.html # 목록 뷰
```

**템플릿 엔진**: Django Templates
**정적 파일**: 아직 확인 필요 (static/ 디렉토리 존재 여부)

---

## 🔍 코드 품질 분석

### ✅ 강점

1. **명확한 책임 분리**
   - 모델: 데이터 구조
   - 뷰: 비즈니스 로직
   - 템플릿: 프레젠테이션

2. **에러 처리**
   - API 키 검증 (`views.py:16-17`, `views.py:229-231`)
   - 이미지 인코딩 예외 처리 (`views.py:44-46`)
   - 분석 실패 캐치 (`views.py:262-265`)

3. **디버깅 지원**
   - 풍부한 print 문 (`views.py:217-218`, `views.py:241-254`)
   - API 연결 테스트 기능 (`views.py:202-207`)

4. **안전한 API 클라이언트 초기화**
   - 지연 초기화 패턴 사용

### ⚠️ 개선 필요 사항

#### 1. 보안 이슈
**파일**: `settings.py`

- `SECRET_KEY` 하드코딩 (빈 문자열)
- `ALLOWED_HOSTS = ['*']` (프로덕션 위험)
- `OPENAI_API_KEY` 환경변수 미사용

**권장 조치**:
```python
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])
OPENAI_API_KEY = config('OPENAI_API_KEY')
```

#### 2. 코드 중복
**파일**: `views.py`

3개 분석 함수 (`views.py:48-195`)가 거의 동일한 구조:
```python
def analyze_*():
    client = get_openai_client()
    if not client: return error
    base64_image = encode_image(image_path)
    if not base64_image: return error
    try:
        response = client.chat.completions.create(...)
        return response.choices[0].message.content
    except Exception as e:
        return error
```

**리팩토링 제안**:
```python
def analyze_with_vision(image_path, prompt_template, max_tokens=500):
    """통합 비전 분석 함수"""
    client = get_openai_client()
    if not client:
        return "OpenAI 클라이언트 초기화에 실패했습니다."

    base64_image = encode_image(image_path)
    if not base64_image:
        return "이미지 처리 중 오류가 발생했습니다."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_template},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                    }}
                ]
            }],
            max_tokens=max_tokens,
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        return f"API 호출 중 오류가 발생했습니다: {str(e)}"
```

#### 3. JSON 파싱 취약성
**파일**: `views.py:273-287`

현재 구현:
```python
if '```json' in result_text:
    result_text = result_text.split('```json')[1].split('```')[0].strip()
```

**문제점**:
- 여러 코드 블록 존재 시 오작동
- 중첩된 백틱 처리 불가

**개선안**:
```python
import re

def extract_json_from_response(text):
    """OpenAI 응답에서 JSON 추출"""
    # 정규식으로 JSON 코드 블록 추출
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # 코드 블록 없이 바로 JSON인 경우
    json_match = re.search(r'\{.*?\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)

    return text
```

#### 4. 테스트 코드 부재
**파일**: `medicine_analyzer/tests.py`

현재 상태: 기본 템플릿만 존재

**권장 테스트**:
- 모델 테스트 (MedicineAnalysis CRUD)
- 뷰 테스트 (각 엔드포인트 동작)
- API 통합 테스트 (모킹 사용)
- 이미지 업로드 검증

#### 5. 로깅 개선
**현재**: `print()` 문 사용 (`views.py:20, 94, 143, 195, 217, 242, 254, 263, 286`)

**권장**:
```python
import logging

logger = logging.getLogger(__name__)

logger.info("분석 시작", extra={'analysis_type': analysis_type})
logger.error("API 호출 실패", exc_info=True)
```

#### 6. 이미지 검증 부재

**현재**: 파일 업로드 후 즉시 처리

**권장 검증**:
```python
def validate_image(image):
    """이미지 검증"""
    # 파일 크기 제한 (예: 10MB)
    if image.size > 10 * 1024 * 1024:
        raise ValidationError("파일 크기는 10MB 이하여야 합니다.")

    # 파일 확장자 검증
    ext = image.name.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png']:
        raise ValidationError("지원되는 형식: JPG, PNG")

    # 이미지 유효성 검증
    try:
        from PIL import Image
        img = Image.open(image)
        img.verify()
    except Exception:
        raise ValidationError("유효하지 않은 이미지 파일입니다.")
```

---

## 📝 의존성 분석

### requirements.txt 주요 패키지

```
Django==4.2.7              # 웹 프레임워크
openai==1.3.5             # OpenAI API 클라이언트
opencv-python==4.12.0.88  # 이미지 처리 (현재 미사용)
Pillow==10.1.0            # 이미지 처리
python-decouple==3.8      # 환경변수 관리
requests==2.32.5          # HTTP 클라이언트
numpy==2.0.2              # 수치 계산 (opencv 의존성)
```

**미사용 패키지**:
- `opencv-python`: 코드에서 사용되지 않음 → 제거 또는 활용 계획 수립
- `numpy`: OpenCV 의존성이므로 함께 제거 가능

**누락 패키지**:
- `pytest` / `pytest-django`: 테스트 프레임워크
- `python-dotenv`: `.env` 파일 지원 (decouple로 대체됨)
- `gunicorn`: 프로덕션 WSGI 서버
- `psycopg2-binary`: PostgreSQL 지원 (프로덕션 고려)

---

## 🚀 다음 단계 권장사항

### 즉시 조치 (High Priority)
1. **환경변수 설정**
   - `.env` 파일 생성
   - `SECRET_KEY`, `OPENAI_API_KEY` 설정
   - `.env.example` 템플릿 추가

2. **보안 강화**
   - `settings.py` 민감 정보 제거
   - `ALLOWED_HOSTS` 적절히 설정
   - CSRF 토큰 검증 확인

3. **코드 리팩토링**
   - 중복 분석 함수 통합
   - JSON 파싱 로직 개선
   - 로깅 시스템 도입

### 단기 목표 (Mid Priority)
4. **테스트 작성**
   - 단위 테스트 (모델, 유틸리티)
   - 통합 테스트 (뷰, API)
   - API 모킹 테스트

5. **에러 핸들링 강화**
   - 이미지 검증 추가
   - 사용자 친화적 에러 메시지
   - 재시도 로직 (API 실패 시)

6. **성능 최적화**
   - 이미지 압축 전처리
   - 대용량 파일 스트리밍 처리
   - DB 쿼리 최적화

### 장기 목표 (Low Priority)
7. **기능 확장**
   - 음성 인터페이스 (develop-voice 브랜치 목표)
   - 실시간 분석 진행 상태 표시
   - 다국어 지원

8. **인프라 개선**
   - PostgreSQL 마이그레이션
   - Redis 캐싱
   - Celery 비동기 작업 큐
   - S3 이미지 저장소

9. **모니터링 & 로깅**
   - Sentry 에러 추적
   - Prometheus 메트릭
   - CloudWatch 로그 집계

---

## 📊 위험 요소 평가

| 위험 요소 | 심각도 | 영향 | 완화 방안 |
|---------|--------|------|----------|
| API 키 노출 | 🔴 High | 비용 폭탄, 보안 침해 | `.env` 이동, `.gitignore` 추가 |
| `ALLOWED_HOSTS='*'` | 🔴 High | CSRF, DNS 리바인딩 공격 | 프로덕션용 호스트 명시 |
| 테스트 부재 | 🟡 Medium | 리그레션 버그 | pytest 프레임워크 도입 |
| 이미지 검증 부재 | 🟡 Medium | 악성 파일 업로드 | Pillow 검증 추가 |
| 중복 코드 | 🟢 Low | 유지보수 어려움 | 리팩토링 진행 |

---

## 🎯 develop-voice 브랜치 목표 추정

브랜치 이름으로 추정되는 기능:
- **음성 입력 인터페이스**: 사용자가 음성으로 복용 정보 입력
- **음성 안내 기능**: 분석 결과를 TTS로 읽어주기
- **음성 명령**: "약 분석해줘" 같은 음성 트리거

**필요 기술**:
- Web Speech API (프론트엔드)
- OpenAI Whisper API (음성 → 텍스트)
- TTS 라이브러리 (텍스트 → 음성)

---

## 📚 참고 리소스

- [Django 4.2 공식 문서](https://docs.djangoproject.com/en/4.2/)
- [OpenAI Vision API 문서](https://platform.openai.com/docs/guides/vision)
- [Django 보안 체크리스트](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

---

*분석 완료: 2025-10-01*
*다음 리뷰 예정: 2025-10-15*
