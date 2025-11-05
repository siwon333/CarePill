# CarePill 프로젝트 현황 분석

**작성일**: 2025-10-29
**프로젝트**: CarePill - 시각장애인을 위한 스마트 약물 관리 시스템
**개발 환경**: Django 5.0 + SQLite + OpenAI + ElevenLabs

---

## 1. 프로젝트 개요

### 목적
음성 인터페이스 기반으로 시각장애인이 약물을 관리할 수 있는 시스템 개발

### 핵심 기능
- 약봉투 자동 스캔 및 정보 추출 (Vision API)
- 실시간 음성 대화 (GPT-4o Realtime API + WebRTC)
- 개인화된 음성 출력 (ElevenLabs Voice Clone)
- 약물 정보 데이터베이스 관리
- 대화 요약 및 저장

### 타겟 사용자
- 시각장애인
- 노인
- 약물 관리가 필요한 모든 사용자

---

## 2. 기술 스택

### 백엔드
- **Framework**: Django 5.0
- **Database**: SQLite3 (경량화 전략)
- **Python**: 3.8+

### AI/ML
- **OpenAI GPT-4o-mini Realtime API**: 음성 대화, 이미지 분석
- **ElevenLabs**: TTS (음성 복제)
- **Vision API**: 약봉투 OCR

### 프론트엔드
- **JavaScript**: Vanilla JS
- **WebRTC**: 실시간 음성 통신
- **CSS**: 커스텀 스타일

### 주요 라이브러리
- openai (Python SDK)
- requests (HTTP 클라이언트)
- python-dotenv (환경 변수)
- Django built-in (ORM, Templates, Static files)

---

## 3. 현재 구현 상태

### ✅ 완료된 기능

#### 3.1 약봉투 스캔 (Envelope Scanning)
- **파일**: `carepill/views.py:api_scan_envelope` (line 583-676)
- **기능**:
  - 멀티카메라 지원 (1-3대, 각 3연사, 총 9장)
  - OpenAI Vision API로 약봉투 정보 추출
  - Majority voting으로 정확도 향상
  - DB 저장 (PillIdentification 모델)
- **엔드포인트**: `POST /api/scan/envelope/`
- **입력**: `{ images: [base64_jpeg, ...], meta: [...] }`
- **출력**:
  ```json
  {
    "analysis_type": "envelope",
    "merged": {
      "patient_name": "환자명",
      "age": "45",
      "medicine_name": "약품명",
      "dosage_instructions": "복용법",
      "frequency": "복용 횟수"
    },
    "saved_to_db": true,
    "record_id": 123
  }
  ```

#### 3.2 실시간 음성 대화 (Voice Chat)
- **파일**: `carepill/views.py:issue_ephemeral`, `realtime_sdp_exchange`
- **기능**:
  - GPT-4o-mini Realtime API 통합
  - WebRTC 기반 실시간 음성 통신
  - Server VAD (Voice Activity Detection)
  - 한국어 전용 안내 음성
- **엔드포인트**:
  - `POST /api/realtime/session/` - 세션 토큰 발급
  - `POST /api/realtime/sdp-exchange/` - SDP 교환
- **프론트엔드**: `carepill/static/carepill/js/realtime_webrtc_chat.js`

#### 3.3 ElevenLabs 음성 복제 (Voice Clone)
- **파일**: `carepill/views.py:api_voice_upload`, `api_text_to_speech`
- **기능**:
  - 사용자 음성 샘플 업로드 (15초+)
  - ElevenLabs Voice Clone 생성
  - TTS 변환 (개인화된 음성)
  - 사용자별 voice_id 저장
- **엔드포인트**:
  - `POST /api/voice/upload/` - 음성 업로드
  - `POST /api/tts/` - TTS 변환
- **서비스**: `carepill/services/elevenlabs_service.py`

#### 3.4 대화 요약 및 저장 (Conversation Summary)
- **파일**: `carepill/views.py:api_conversation_summarize_and_save`
- **기능**:
  - GPT-4o-mini로 3줄 요약 생성
  - 대화 전체 내용 TXT 파일 저장
  - 다운로드 링크 제공
- **엔드포인트**:
  - `POST /api/conversation/summarize_and_save/`
  - `GET /api/conversation/download/?name=<file>.txt`
- **저장 위치**: `media/conversations/`

#### 3.5 페이지 구현
- **홈 페이지**: `/` - `home.html`
- **스캔 페이지**: `/scan/` - `scan.html` (약봉투 스캔)
- **스캔 선택**: `/scan_choice/` - `scan_choice.html`
- **약 목록**: `/meds/` - `meds.html`
- **음성 대화**: `/voice/` - `voice.html`
- **음성 설정**: `/voice_setup/` - `voice_setup.html`
- **처방전 안내**: `/how2prescription/` - `how2prescription.html`
- **일반의약품 안내**: `/how2otc/` - `how2otc.html`
- **병원약 목록**: `/meds_hos/`, `/meds_hos2/`
- **그린 안내**: `/how2green/`, `/how2green_result/`

### 🔨 부분 구현된 기능

#### DB 모델 정의 (models.py)
- **완료**:
  - `Medicine`: 약물 기본 정보 (식약처 데이터 기반)
  - `UserMedication`: 사용자 복용 약
  - `PillIdentification`: 알약 식별 정보
  - `VoiceTTSCache`: TTS 캐싱
  - `VoiceUserVoice`: 사용자 음성 샘플
  - `AccessibilityInfo`: 접근성 정보
  - `OCRImage`: OCR 이미지

- **문제점**:
  - 대부분 모델이 `managed = False` (Django가 테이블 관리 안 함)
  - 외부 DB 스키마 의존
  - Migration 필요

---

## 4. 디렉토리 구조

```
Jeonggyun/
├── config/                    # Django 프로젝트 설정
│   ├── __init__.py
│   ├── settings.py           # Django 설정
│   ├── urls.py               # 루트 URL 설정
│   ├── wsgi.py
│   └── asgi.py
│
├── carepill/                  # 메인 앱
│   ├── models.py             # DB 모델 (164 lines)
│   ├── views.py              # 뷰 로직 (856 lines)
│   ├── urls.py               # URL 라우팅 (38 lines)
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   │
│   ├── services/             # 서비스 레이어
│   │   ├── __init__.py
│   │   └── elevenlabs_service.py  # ElevenLabs 통합
│   │
│   ├── static/carepill/      # 정적 파일
│   │   ├── css/              # 스타일시트
│   │   ├── js/               # JavaScript
│   │   ├── images/           # 이미지
│   │   └── img/
│   │
│   ├── templates/carepill/   # HTML 템플릿
│   │   ├── home.html
│   │   ├── scan.html
│   │   ├── meds.html
│   │   ├── voice.html
│   │   └── ...
│   │
│   └── migrations/           # DB 마이그레이션
│       └── 0001_initial.py
│
├── proto_test/               # 프로토타입 테스트
│   ├── scan.py              # 스캔 테스트
│   ├── crawling/            # 약물 정보 크롤링
│   ├── captures/            # 스캔 이미지 샘플
│   └── results/             # 테스트 결과
│
├── conversations/            # 대화 기록 저장
│   ├── 20251008T090259_...txt
│   └── _debug_*.json
│
├── media/                    # 업로드 파일
│   ├── conversations/       # 대화 요약 TXT
│   └── voices/              # 사용자 음성 샘플
│
├── templates/                # 전역 템플릿
│   └── base.html
│
├── manage.py                 # Django 관리 스크립트
├── requirements.txt          # Python 의존성
├── todolist.txt             # 개발 TODO
├── plan.md                  # 라즈베리파이 시스템 설계
├── implementation_plan.md   # Django 실행 계획
└── .gitignore
```

---

## 5. 주요 파일 분석

### 5.1 models.py (164 lines)
**구조**:
- 7개 모델 정의
- Foreign Key 관계 설정
- 대부분 `managed = False` (외부 DB 의존)

**모델**:
1. `Medicine` (line 5-33): 약물 기본 정보
2. `UserMedication` (line 36-56): 사용자 복용 약
3. `PillIdentification` (line 59-82): 알약 식별 정보
4. `VoiceTTSCache` (line 85-104): TTS 캐싱
5. `VoiceUserVoice` (line 107-124): 사용자 음성 샘플
6. `AccessibilityInfo` (line 127-146): 접근성 정보
7. `OCRImage` (line 149-163): OCR 이미지

**문제점**:
- `VoiceTTSCache`, `VoiceUserVoice`만 `managed = True`
- 나머지는 외부 DB 스키마에 의존

### 5.2 views.py (856 lines)
**주요 함수**:

| Line | 함수명 | 기능 |
|------|--------|------|
| 5-15 | 페이지 뷰 | home, scan, meds, voice 등 렌더링 |
| 17-66 | `issue_ephemeral` | OpenAI Realtime API 세션 토큰 발급 |
| 74-108 | `realtime_sdp_exchange` | WebRTC SDP 교환 |
| 238-397 | `api_conversation_summarize_and_save` | 대화 요약 및 저장 |
| 583-676 | `api_scan_envelope` | 약봉투 멀티카메라 스캔 |
| 696-766 | `api_voice_upload` | 음성 샘플 업로드 및 Voice Clone 생성 |
| 770-856 | `api_text_to_speech` | ElevenLabs TTS 변환 |

**특징**:
- 모든 API는 JSON 응답
- CSRF 예외 처리 (`@csrf_exempt`)
- 에러 핸들링 및 로깅
- 환경 변수 사용 (`.env`)

### 5.3 urls.py (38 lines)
**엔드포인트**:
- 페이지: `/`, `/scan/`, `/meds/`, `/voice/` 등
- API:
  - `/api/realtime/session/`
  - `/api/realtime/sdp-exchange/`
  - `/api/conversation/summarize_and_save/`
  - `/api/conversation/download/`
  - `/api/scan/envelope/`
  - `/api/voice/upload/`
  - `/api/tts/`

### 5.4 settings.py (144 lines)
**주요 설정**:
- Django 5.0
- SQLite3 DB
- `MEDIA_ROOT`: `BASE_DIR / "media"`
- `MEDIA_URL`: `/media/`
- `TEMPLATES[0]["DIRS"]`: `BASE_DIR / "templates"`
- `.env` 로드 (python-dotenv)

---

## 6. 개발 진행 상황 (todolist.txt 기반)

### 최근 완료 (2025.10.10)
- ✅ 약봉투 스캔 연결
- ✅ 이미지 → JSON 정보 처리 로직 구상
- ✅ 약봉투 면밀히 분석

### 진행 중
- 🔨 3개 이미지 한번에 처리하는 로직 (멀티카메라)
- 🔨 결과값 출력 및 데이터 저장 고려

### 계획 중
- 📋 페이지 넘김 간소화 (단일 페이지 고려)
- 📋 안약/안경 개발
- 📋 서비스 연결고리 흐름 개선

---

## 7. implementation_plan.md 분석

### 확정된 개발 전략
1. **Phase 1**: Django 웹 애플리케이션 완성 (최우선)
2. **Phase 2**: Raspberry Pi 하드웨어 통합 (Django 완성 후)
3. **데이터베이스**: SQLite 유지 (경량화)
4. **팀 협업**: 기존 팀원 코드 최대한 활용

### 최우선 과제
1. **Sprint 1**: 약봉투 인식 및 DB 저장 (2-3일)
   - DB 모델 구현
   - 스캔 API 개선
   - UI 연동

2. **Sprint 2**: ElevenLabs TTS 통합 (1-2일)
   - ElevenLabs API 연동
   - TTS API 엔드포인트 추가
   - 프론트엔드 연동

### 차순위 개발
- **Sprint 3**: 약물 상호작용(DUR) 체크 (2일)
- **Sprint 4**: 복용 스케줄 및 알림 (2-3일)
- **Sprint 5**: 음성 인터페이스 Function Calling (2일)

---

## 8. 주요 이슈 및 해결 방안

### 8.1 DB Migration 필요
**문제**: 대부분 모델이 `managed = False`
**해결**:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 8.2 환경 변수 설정
**필요 변수** (`.env`):
```env
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
SECRET_KEY=django-insecure-...
DEBUG=True
```

### 8.3 PillIdentification 모델 불일치
**문제**: `api_scan_envelope`에서 `PillIdentification.objects.create()` 호출
**현재 모델**: `PillIdentification`는 `Medicine`의 OneToOne (line 59-82)
**불일치**: 약봉투 스캔 결과를 저장할 별도 모델 필요

**해결 방안**:
1. 새로운 모델 생성: `EnvelopeScanResult`
2. 또는 `PillIdentification` 모델 수정

---

## 9. Git 상태

### 현재 브랜치
- **main** (메인 브랜치)

### Staged 파일 (새로 추가)
```
A  .gitignore
A  carepill/__init__.py
A  carepill/admin.py
A  carepill/apps.py
A  carepill/asr/__init__.py
A  carepill/asr/realtime_server.py
A  carepill/migrations/__init__.py
AM carepill/models.py (일부 수정)
A  carepill/services/__init__.py
A  carepill/services/elevenlabs_service.py
AM carepill/static/... (CSS, JS 파일들)
AM carepill/templates/... (HTML 템플릿들)
A  config/... (Django 설정)
A  proto_test/... (프로토타입 코드)
A  requirements.txt
A  templates/base.html
```

### Untracked 파일 (새로 생성, 미추가)
```
?? carepill/migrations/0001_initial.py
?? carepill/static/carepill/css/how2green.css
?? carepill/static/carepill/css/how2green_result.css
?? carepill/static/carepill/css/meds_hos.css
?? carepill/static/carepill/css/meds_hos2.css
?? carepill/static/carepill/css/scan_yujeong.css
?? carepill/static/carepill/img/... (약물 이미지들)
?? carepill/static/carepill/js/notification.js
?? carepill/templates/carepill/how2green.html
?? carepill/templates/carepill/how2green_result.html
?? carepill/templates/carepill/meds_hos.html
?? carepill/templates/carepill/meds_hos2.html
?? carepill/templates/carepill/scan_yujeong.html
```

---

## 10. 다음 액션 아이템

### 즉시 실행 가능
1. **Migration 실행**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **환경 변수 확인**
   ```bash
   # .env 파일에 API 키 확인
   cat .env | grep OPENAI_API_KEY
   cat .env | grep ELEVENLABS_API_KEY
   ```

3. **개발 서버 실행**
   ```bash
   python manage.py runserver
   ```

4. **테스트**
   - 약봉투 스캔 테스트 (http://localhost:8000/scan/)
   - 음성 대화 테스트 (http://localhost:8000/voice/)
   - TTS 테스트 (http://localhost:8000/voice_setup/)

### 단기 목표 (1주일)
1. **Sprint 1 완료**: 약봉투 인식 및 DB 저장
   - `EnvelopeScanResult` 모델 추가
   - `meds.html` DB 연동 (현재 정적)
   - 약 목록 페이지 구현

2. **Sprint 2 완료**: ElevenLabs TTS 통합
   - 이미 구현됨 (확인 필요)
   - 프론트엔드 통합 확인

### 중기 목표 (2-3주)
3. **Sprint 3**: 약물 상호작용(DUR) 체크
4. **Sprint 4**: 복용 스케줄 및 알림
5. **Sprint 5**: 음성 인터페이스 Function Calling

### 장기 목표 (1개월+)
6. **Sprint 6**: 프로덕션 준비 및 최적화
7. **Sprint 7**: Raspberry Pi 통합 (Django 완성 후)

---

## 11. 팀원 정보 및 협업

### 기존 팀원 작업 내용
- Django 프로젝트 구조 설계
- OpenAI Realtime API 통합
- WebRTC 음성 통신 구현
- Vision API 기반 약봉투 스캔
- ElevenLabs Voice Clone 통합
- 대화 요약 및 저장 기능

### 협업 권장 사항
- 기존 코드 최대한 유지
- 리팩토링 지양, 기능 추가 우선
- 테스트 코드는 시간 여유 시
- 매일 진행 상황 공유 (Stand-up)

---

## 12. 기술 부채 및 개선 사항

### 코드 품질
- ✅ 에러 핸들링 잘 되어 있음
- ✅ 로깅 구현됨
- ⚠️ 테스트 코드 없음 (추후 추가)
- ⚠️ 주석이 부족함 (일부 함수만)

### 보안
- ⚠️ `SECRET_KEY` 노출 (settings.py:33)
- ⚠️ `DEBUG = True` (프로덕션 시 False)
- ⚠️ `ALLOWED_HOSTS = []` (프로덕션 시 설정 필요)
- ✅ API 키는 환경 변수로 관리 중

### 성능
- ⚠️ 이미지 캐싱 없음 (중복 스캔 방지 고려)
- ⚠️ TTS 캐싱 모델은 있으나 활용 여부 불명
- ⚠️ DB 인덱스 최적화 필요

### 아키텍처
- ✅ 모듈화 잘 되어 있음 (services/)
- ⚠️ `views.py`가 너무 큼 (856 lines) - 분리 고려
- ⚠️ 하드코딩된 문자열 많음 (상수화 권장)

---

## 13. 참고 문서

### 프로젝트 내부
- `plan.md`: 라즈베리파이 시스템 설계
- `implementation_plan.md`: Django 실행 계획
- `todolist.txt`: 개발 TODO

### 외부 문서
- [Django 공식 문서](https://docs.djangoproject.com/)
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- [ElevenLabs API](https://elevenlabs.io/docs)
- [식약처 공개 API](https://www.data.go.kr/)

---

## 14. 요약

### 현재 상태
- ✅ Django 웹 애플리케이션 기본 구조 완성
- ✅ 핵심 기능 (스캔, 음성, TTS) 구현 완료
- ⚠️ DB Migration 필요
- ⚠️ 일부 페이지 정적 (DB 연동 필요)

### 강점
- OpenAI Realtime API 통합 완료
- ElevenLabs Voice Clone 구현
- 멀티카메라 스캔 지원
- 에러 핸들링 잘 되어 있음

### 약점
- 테스트 코드 없음
- 일부 보안 설정 미흡
- DB 모델 불일치 (PillIdentification)
- 성능 최적화 여지 있음

### 다음 단계
1. Migration 실행
2. Sprint 1 완료 (약봉투 인식 및 DB 저장)
3. Sprint 2 검증 (ElevenLabs TTS)
4. Sprint 3-5 진행 (DUR, 스케줄, Function Calling)

---

**문서 버전**: 1.0
**작성자**: Claude Code
**최종 수정**: 2025-10-29
