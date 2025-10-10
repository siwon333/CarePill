# TTS 음성 업로드 웹 인터페이스 구현 내역

최종 업데이트: 2025-10-10

---

## 완료된 작업 (Completed)

### 1. 초기 설정 및 환경 구성

**완료 항목:**
- djangorestframework 설치 및 설정
- rest_framework.authtoken 앱 추가
- API Token 생성 시스템 구축
- .env 파일 설정 (DJANGO_TTS_TOKEN)

**관련 파일:**
- `medicine_project/settings.py` - INSTALLED_APPS 업데이트
- `.env` - API 토큰 추가
- `scripts/generate_token_auto.py` - 자동 토큰 생성 스크립트

**생성된 토큰:**
```
Token: 7df8c822d68f5a2f5ca9c152bffda571637ad3db
```

### 2. 음성 샘플 업로드 API 구현

**완료 항목:**
- UserVoiceUploadView API 엔드포인트
- TTSGenerateView API 엔드포인트
- TTSHealthCheckView API 엔드포인트
- UNIQUE constraint 에러 수정 (update → delete)

**주요 수정:**
```python
# voice_tts/views.py - UNIQUE constraint 수정
# OLD: UserVoice.objects.filter(user=user).update(is_active=False)
# NEW: UserVoice.objects.filter(user=user).delete()
```

**엔드포인트:**
- `POST /api/tts/upload-voice/` - 음성 파일 업로드
- `POST /api/tts/generate/` - TTS 음성 생성
- `GET /api/tts/health/` - 서비스 상태 확인

### 3. 웹 인터페이스 개발

**완료 항목:**
- 음성 업로드 웹 페이지 생성 (`/api/tts/upload/`)
- 드래그 앤 드롭 파일 업로드 기능
- 브라우저 기반 음성 녹음 기능
- 탭 시스템 (직접 녹음 vs 파일 업로드)
- 페이지 간 네비게이션 메뉴
- 자동 로그인 (voice_user)

**주요 기능:**

#### A. 직접 녹음 탭
- MediaRecorder API 활용
- 실시간 타이머 (00:00 형식)
- 파형 애니메이션 (20개 바)
- 5-30초 녹음 제약
- 오디오 미리듣기
- "다시 녹음" / "이 녹음 사용" 버튼

#### B. 파일 업로드 탭
- 드래그 앤 드롭 지원
- 파일 형식 검증 (WAV, MP3, M4A, FLAC)
- 파일 크기 제한 (10MB)
- 실시간 파일 정보 표시
- 프로그레스 바

#### C. 네비게이션 메뉴
- 음성 업로드 (현재 페이지)
- 약물 검색
- 약 사진 인식
- API 상태
- 관리자

**디자인:**
- 보라색 그라데이션 테마 (#667eea → #764ba2)
- 반응형 레이아웃
- 애니메이션 효과 (호버, 전환)
- 깔끔한 UI/UX

**관련 파일:**
- `voice_tts/templates/voice_tts/upload_voice.html` - 메인 템플릿
- `voice_tts/views.py:upload_voice_page` - 뷰 함수
- `voice_tts/urls.py` - URL 라우팅

### 4. 테스트 및 검증

**완료 항목:**
- Dummy 음성 샘플 생성 (`scripts/create_dummy_voice.py`)
- 실제 음성 업로드 스크립트 (`scripts/upload_real_voice.py`)
- TTS API 테스트 성공 (200 응답)
- 음성 비서 프로토타입 연동 테스트

**테스트 결과:**
- Health Check API: 정상 작동
- 음성 업로드: 파일/녹음 모두 정상
- TTS 생성: 캐시 시스템 정상
- 자동 로그인: 정상 작동

### 5. 문서화

**완료 항목:**
- `claudedocs/ALL_WEB_PAGES.md` - 전체 페이지 목록
- `claudedocs/AVAILABLE_WEB_PAGES.md` - 사용 가능한 페이지
- `RUN_SERVER.md` - TTS API 가이드 추가
- `claudedocs/TTS_VOICE_UPLOAD_IMPLEMENTATION.md` (현재 문서)

---

## 현재 시스템 상태

### 작동 방식

1. **사용자 접속:** http://localhost:8000/api/tts/upload/
2. **자동 로그인:** voice_user 계정으로 자동 인증
3. **음성 선택:**
   - 탭 1: 브라우저에서 직접 녹음 (5-30초)
   - 탭 2: 파일 업로드 (WAV, MP3, M4A, FLAC)
4. **업로드:** POST 요청으로 서버에 전송
5. **저장:** UserVoice 모델에 저장 (기존 음성 삭제 후)
6. **사용:** TTS API에서 해당 음성 샘플 참조

### 현재 제약사항

**Mock Mode 운영:**
- GPT-SoVITS 실제 모델 미설치
- TTS 생성 시 참조 음성 파일을 단순 복사
- 실제 음성 합성은 수행하지 않음

**이유:**
- 모델 파일 크기 (수 GB)
- GPU 리소스 필요
- 개발/테스트 단계

### 기술 스택

**Backend:**
- Django 4.2.7
- Django REST Framework 3.14.0
- GPT-SoVITS (Mock 모드)

**Frontend:**
- HTML5
- CSS3 (Gradients, Animations)
- Vanilla JavaScript
- MediaRecorder API
- FormData API

**Database:**
- SQLite (개발)
- Models: UserVoice, TTSCache

---

## 앞으로 할 작업 (TODO)

### Phase 1: GPT-SoVITS 실제 모델 통합 (우선순위: 높음)

**필요 작업:**

1. **모델 다운로드 및 설치**
   - GPT-SoVITS v2 모델 다운로드
   - 모델 파일 배치 (`./models/gpt-sovits-v2/`)
   - 의존성 패키지 설치 (`requirements_gpt_sovits.txt`)

2. **서비스 구현 업데이트**
   - `voice_tts/services/gpt_sovits.py` 수정
   - Mock 모드 제거
   - 실제 TTS 추론 코드 구현
   - GPU/CPU 자동 감지 및 설정

3. **성능 최적화**
   - 모델 로딩 최적화
   - 추론 속도 개선
   - 메모리 사용량 최적화
   - 배치 처리 지원

4. **테스트**
   - 실제 음성 샘플로 TTS 생성 테스트
   - 음성 품질 검증
   - 다양한 텍스트 길이 테스트
   - 캐시 시스템 검증

**예상 소요 시간:** 2-3일
**난이도:** 중상
**리소스 요구사항:** GPU (권장), 최소 8GB RAM

### Phase 2: 음성 품질 개선 (우선순위: 중)

**필요 작업:**

1. **음성 샘플 가이드라인**
   - 최적 녹음 환경 안내
   - 샘플 텍스트 제공
   - 품질 자동 검증 기능
   - 노이즈 제거 전처리

2. **다중 음성 샘플 지원**
   - 여러 음성 샘플 업로드
   - 샘플 간 자동 선택
   - 음성 품질 비교 기능

3. **음성 미리보기**
   - 업로드한 샘플 재생
   - 파형 시각화
   - 음질 분석 정보 표시

**예상 소요 시간:** 1-2일
**난이도:** 중

### Phase 3: UI/UX 개선 (우선순위: 중)

**필요 작업:**

1. **녹음 가이드 개선**
   - 녹음 중 실시간 피드백
   - 볼륨 레벨 미터
   - 최적 녹음 시간 안내
   - 샘플 텍스트 제공

2. **에러 처리 개선**
   - 친절한 에러 메시지
   - 복구 가이드 제공
   - 자동 재시도 기능

3. **진행 상황 표시**
   - 업로드 진행률
   - TTS 생성 진행률
   - 예상 소요 시간 표시

4. **다국어 지원**
   - 한국어/영어 전환
   - 언어별 안내 메시지

**예상 소요 시간:** 2-3일
**난이도:** 하

### Phase 4: 모바일 최적화 (우선순위: 중하)

**필요 작업:**

1. **반응형 디자인 강화**
   - 모바일 화면 크기 최적화
   - 터치 인터랙션 개선
   - 세로/가로 모드 지원

2. **모바일 녹음 최적화**
   - 모바일 브라우저 호환성
   - 권한 요청 UX 개선
   - 백그라운드 녹음 지원

3. **Progressive Web App (PWA)**
   - Service Worker 구현
   - 오프라인 지원
   - 홈 화면 추가 기능

**예상 소요 시간:** 2-3일
**난이도:** 중

### Phase 5: 프로덕션 배포 준비 (우선순위: 중하)

**필요 작업:**

1. **보안 강화**
   - HTTPS 적용
   - CSRF 토큰 검증
   - 파일 업로드 보안 검증
   - Rate limiting 구현

2. **성능 최적화**
   - 정적 파일 CDN 배포
   - 미디어 파일 스토리지 분리
   - 캐시 전략 수립
   - 데이터베이스 최적화

3. **모니터링 및 로깅**
   - 에러 추적 시스템
   - 사용 통계 수집
   - 성능 모니터링
   - 로그 관리 시스템

4. **백업 및 복구**
   - 데이터베이스 백업 자동화
   - 음성 파일 백업
   - 재해 복구 계획

**예상 소요 시간:** 3-5일
**난이도:** 중상

### Phase 6: 라즈베리파이 배포 (우선순위: 낮음)

**필요 작업:**

1. **경량화**
   - 모델 경량화 (Quantization)
   - 의존성 최소화
   - 메모리 사용량 최적화

2. **ARM 아키텍처 지원**
   - ARM용 라이브러리 빌드
   - 호환성 테스트
   - 성능 벤치마크

3. **자동 시작 설정**
   - systemd 서비스 설정
   - 자동 업데이트
   - 로그 로테이션

**예상 소요 시간:** 3-4일
**난이도:** 중상
**리소스 요구사항:** Raspberry Pi 4 (4GB+ RAM)

---

## 기술 부채 (Technical Debt)

### 해결 필요 항목

1. **Mock Mode 제거**
   - 현재: GPT-SoVITS Mock 모드
   - 목표: 실제 TTS 모델 통합
   - 영향도: 높음

2. **에러 처리 일관성**
   - 현재: 일부 API 에러 처리 불완전
   - 목표: 전역 에러 핸들러 구현
   - 영향도: 중

3. **테스트 코드 부재**
   - 현재: 수동 테스트만 존재
   - 목표: Unit/Integration 테스트 작성
   - 영향도: 중

4. **로깅 시스템 미흡**
   - 현재: 기본 Django 로깅
   - 목표: 구조화된 로깅 시스템
   - 영향도: 중하

---

## 참고 자료

### 관련 문서
- `claudedocs/ALL_WEB_PAGES.md` - 전체 웹 페이지 목록
- `claudedocs/AVAILABLE_WEB_PAGES.md` - 사용 가능한 페이지 설명
- `RUN_SERVER.md` - 서버 실행 및 API 테스트 가이드

### 주요 URL
- 음성 업로드 페이지: http://localhost:8000/api/tts/upload/
- TTS Health Check: http://localhost:8000/api/tts/health/
- Django Admin: http://localhost:8000/admin/

### API 토큰
```
Token: 7df8c822d68f5a2f5ca9c152bffda571637ad3db
User: voice_user
```

---

## 변경 이력

### 2025-10-10
- 음성 업로드 웹 인터페이스 완성
- 브라우저 녹음 기능 추가
- 네비게이션 메뉴 추가
- UNIQUE constraint 에러 수정
- 문서 작성 완료

### 향후 업데이트
- GPT-SoVITS 실제 모델 통합 시 업데이트 예정
- 프로덕션 배포 후 업데이트 예정
