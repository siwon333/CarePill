# CarePill - 음성 인식 약 복용 도우미

Django 기반 음성 인식 약 복용 관리 시스템

## 📋 프로젝트 개요

CarePill은 음성 명령을 통해 약 정보를 조회하고 복용을 도와주는 시스템입니다.

### 주요 기능
- 🎤 **웨이크 워드 감지**: "케어필" 호출로 시스템 활성화
- 🗣️ **음성 인식**: Naver Clova STT로 음성을 텍스트로 변환
- 🧠 **의도 분류**: OpenAI로 사용자 명령 의도 파악
- 💊 **약 정보 관리**: 시간대별 약 정보 제공
- 🔊 **음성 출력**: Naver Clova TTS로 자연스러운 음성 답변

## 🛠️ 기술 스택

### Backend
- **Django 4.2.7**: 웹 프레임워크
- **Python 3.13**: 메인 언어

### AI/ML
- **OpenAI GPT-4o-mini**: 이미지 분석, 의도 분류, 답변 생성
- **Picovoice Porcupine**: 웨이크 워드 감지
- **Naver Clova STT**: 음성-텍스트 변환
- **Naver Clova TTS**: 텍스트-음성 변환

## 📦 설치 및 설정

### 1. 환경 변수 설정 (.env)

```bash
# Django
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Naver Clova
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret

# Porcupine (Wake Word)
PORCUPINE_ACCESS_KEY=your-picovoice-access-key
PORCUPINE_MODEL_PATH=wake_words/porcupine_params_ko.pv
WAKE_WORD_MODEL_PATH=wake_words/carepill_ko_windows.ppn
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 웨이크 워드 모델 설정

1. [Picovoice Console](https://console.picovoice.ai/) 접속
2. Korean 언어 모델 다운로드 → `wake_words/porcupine_params_ko.pv`
3. "케어필" 키워드 모델 훈련 → `wake_words/carepill_ko_windows.ppn`

## 🚀 실행

### 음성 어시스턴트 프로토타입

```bash
python voice_assistant_prototype.py
```

**사용법:**
1. "케어필" 말하기 (웨이크 워드)
2. 명령하기:
   - "아침약 줘"
   - "아침약 뭐 있어?"
   - "저녁약 언제 먹어?"
   - "점심약 몇 알이야?"

### Django 서버

```bash
python manage.py runserver
```

## 📁 프로젝트 구조

```
CarePill/
├── medicine_analyzer/       # Django 앱
│   ├── models.py           # 데이터베이스 모델
│   ├── views.py            # 비즈니스 로직
│   └── urls.py             # URL 라우팅
├── medicine_project/        # Django 프로젝트 설정
│   ├── settings.py
│   └── urls.py
├── wake_words/             # 웨이크 워드 모델
│   ├── porcupine_params_ko.pv      # 한국어 언어 모델
│   └── carepill_ko_windows.ppn     # 케어필 키워드
├── claudedocs/             # 프로젝트 문서
├── voice_assistant_prototype.py    # 음성 어시스턴트 프로토타입
├── test_wake_word.py       # 웨이크 워드 테스트
├── manage.py
├── requirements.txt
└── .env
```

## 🔧 개발 도구

### 웨이크 워드 테스트

```bash
python test_wake_word.py
```

"케어필"이라고 말하면 감지 여부를 확인할 수 있습니다.

## 🎯 음성 명령 플로우

```
1. Wake Word Detection (케어필)
   ↓
2. STT (3초 녹음 → 텍스트)
   ↓
3. Intent Classification (의도 분류)
   - get_medicine: 약 가져오기
   - list_medicine: 약 목록
   - ask_time: 복용 시간
   - ask_dosage: 복용량
   ↓
4. Data Processing (DB 조회)
   ↓
5. Response Generation (자연스러운 답변)
   ↓
6. TTS (음성 출력)
```

## 📊 의도 분류 시스템

OpenAI를 활용한 하이브리드 방식:

1. **의도 분류**: OpenAI로 사용자 명령 분석
2. **데이터 조회**: Django ORM으로 빠른 DB 접근
3. **답변 생성**: OpenAI로 자연스러운 응답 생성

## 🔐 API 키 발급

### Naver Clova
1. [Naver Cloud Platform](https://console.ncloud.com/) 가입
2. AI·NAVER API > CLOVA Voice 활성화
3. Application 등록 → Client ID/Secret 발급

### Picovoice
1. [Picovoice Console](https://console.picovoice.ai/) 가입
2. Access Key 발급
3. Porcupine에서 한국어 모델 & 키워드 훈련

### OpenAI
1. [OpenAI Platform](https://platform.openai.com/) 가입
2. API Keys 페이지에서 키 생성

## 📝 참고 문서

상세 문서는 `claudedocs/` 폴더 참조:
- `voice_architecture.md`: 음성 시스템 아키텍처
- `implementation_strategy_comparison.md`: 구현 전략 비교
- `picovoice_setup_guide.md`: Picovoice 설정 가이드
- `naver-clova-voice-api-research.md`: Naver API 연구

## 🛣️ 개발 로드맵

- [x] Naver Clova API 연동
- [x] Picovoice 웨이크 워드 설정
- [x] 음성 명령 프로토타입
- [ ] 약 정보 DB 모델 설계
- [ ] Django 음성 어시스턴트 통합
- [ ] 복용 알림 기능
- [ ] 라즈베리파이 배포

## 📄 라이선스

이 프로젝트는 개인 학습/연구 목적으로 개발되었습니다.
