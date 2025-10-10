# CarePill - 모든 웹 페이지 목록

서버 실행: `python manage.py runserver`

## 웹 페이지 (브라우저에서 바로 사용)

### 1. 음성 업로드 페이지 (NEW!)
**URL**: http://localhost:8000/api/tts/upload/

**기능:**
- 직접 녹음 탭: 브라우저에서 음성 녹음 (5-30초)
  - 실시간 타이머 및 파형 애니메이션
  - 오디오 미리듣기
  - "다시 녹음" / "이 녹음 사용" 버튼
- 파일 업로드 탭: 드래그 앤 드롭으로 음성 파일 업로드
  - 실시간 파일 검증 (형식, 크기)
  - 프로그레스 바
- 현재 등록된 음성 샘플 확인
- 페이지 간 네비게이션 메뉴
- 자동 로그인 (voice_user)

**지원 포맷**: WAV, MP3, M4A, FLAC
**최대 크기**: 10MB
**권장 길이**: 5~30초

---

### 2. Django 관리자 페이지
**URL**: http://localhost:8000/admin/

**기능:**
- 약물 데이터 관리
- 사용자 관리
- 음성 샘플 관리
- TTS 캐시 관리

**로그인 필요**: 슈퍼유저 계정

---

### 3. 약물 메인 페이지
**URL**: http://localhost:8000/api/medicines/

**기능:**
- 약물 검색 및 조회
- 약물 정보 표시

---

### 4. 약물 상세 페이지
**URL**: http://localhost:8000/api/medicines/detail/195900043/

**기능:**
- 특정 약물의 상세 정보 표시

---

### 5. 내 복용 약물 페이지
**URL**: http://localhost:8000/api/medicines/my-medications/

**기능:**
- 사용자가 복용 중인 약물 관리

---

### 6. OCR 페이지
**URL**: http://localhost:8000/ocr/

**기능:**
- 약물 이미지 업로드
- OCR로 약물명 인식

---

## 📡 API 엔드포인트 (JSON 응답)

### TTS API

#### Health Check
**URL**: http://localhost:8000/api/tts/health/
**메서드**: GET
**인증**: 불필요

```json
{
  "status": "healthy",
  "service": {
    "is_available": true,
    "model_loaded": true,
    "device": "cpu",
    "mock_mode": true
  },
  "timestamp": "2025-10-10T12:34:56.789"
}
```

#### TTS 생성
**URL**: http://localhost:8000/api/tts/generate/
**메서드**: POST
**인증**: 필요 (Token)

**요청:**
```json
{
  "text": "약을 드실 시간입니다",
  "use_cache": true,
  "language": "ko"
}
```

**헤더:**
```
Authorization: Token 7df8c822d68f5a2f5ca9c152bffda571637ad3db
Content-Type: application/json
```

#### 음성 업로드 API
**URL**: http://localhost:8000/api/tts/upload-voice/
**메서드**: POST
**인증**: 필요 (Token)
**본문**: multipart/form-data

---

### 약물 API

#### 약물 검색
**URL**: http://localhost:8000/api/medicines/search/?q=타이레놀
**메서드**: GET
**인증**: 불필요

#### 약물 통계
**URL**: http://localhost:8000/api/medicines/stats/
**메서드**: GET
**인증**: 불필요

#### 약물 상세 (API)
**URL**: http://localhost:8000/api/medicines/api-detail/195900043/
**메서드**: GET
**인증**: 불필요

#### 바코드 검색
**URL**: http://localhost:8000/api/medicines/search/barcode/
**메서드**: POST
**인증**: 불필요

#### 이미지 검색
**URL**: http://localhost:8000/api/medicines/search/image/
**메서드**: POST
**인증**: 불필요

#### 동영상 있는 약물
**URL**: http://localhost:8000/api/medicines/videos/
**메서드**: GET
**인증**: 불필요

---

### OCR API

#### OCR 처리
**URL**: http://localhost:8000/ocr/process/
**메서드**: POST
**인증**: 불필요

---

## 🎯 빠른 접속 가이드

### 음성 업로드 (추천!)
```
http://localhost:8000/api/tts/upload/
```
→ 예쁜 UI로 드래그 앤 드롭 업로드!

### 관리자 페이지
```
http://localhost:8000/admin/
```
→ 모든 데이터 관리

### API 테스트
```
Health Check:  http://localhost:8000/api/tts/health/
약물 검색:     http://localhost:8000/api/medicines/search/?q=타이레놀
약물 통계:     http://localhost:8000/api/medicines/stats/
```

---

## 🔑 인증 정보

### API 토큰
```
Token: 7df8c822d68f5a2f5ca9c152bffda571637ad3db
```

### 슈퍼유저 생성
```bash
python manage.py createsuperuser
```

---

## 💡 사용 예시

### 1. 음성 샘플 업로드하기
1. http://localhost:8000/api/tts/upload/ 접속
2. 음성 파일 드래그 앤 드롭 (또는 클릭해서 선택)
3. "업로드" 버튼 클릭
4. 완료!

### 2. 약물 검색하기
1. http://localhost:8000/api/medicines/ 접속
2. 검색창에 약물명 입력
3. 검색 결과 확인

### 3. TTS 테스트하기
```bash
# 1. Health Check
curl http://localhost:8000/api/tts/health/

# 2. TTS 생성
curl -X POST http://localhost:8000/api/tts/generate/ \
  -H "Authorization: Token 7df8c822d68f5a2f5ca9c152bffda571637ad3db" \
  -H "Content-Type: application/json" \
  -d '{"text":"약을 드실 시간입니다","use_cache":true,"language":"ko"}'
```

---

## 📱 모바일/라즈베리파이 접속

서버가 실행 중인 PC의 IP 주소를 확인 후:

```
http://192.168.x.x:8000/api/tts/upload/
http://192.168.x.x:8000/api/tts/health/
```

**설정 변경 필요:**
```python
# settings.py
ALLOWED_HOSTS = ['*']  # 또는 ['192.168.x.x']
```

---

## 페이지 스크린샷 설명

### 음성 업로드 페이지
- 보라색 그라데이션 배경
- 탭 시스템 (직접 녹음 / 파일 업로드)
- 녹음 탭:
  - "녹음 시작" / "녹음 중지" 버튼
  - 실시간 타이머 (00:00)
  - 파형 애니메이션 (20개 바)
  - 오디오 플레이어 (미리듣기)
  - "다시 녹음" / "이 녹음 사용" 버튼
- 업로드 탭:
  - 드래그 앤 드롭 영역
  - 실시간 파일 정보 표시
  - 프로그레스 바
- 현재 등록된 음성 정보
- 페이지 간 네비게이션 메뉴 (음성 업로드, 약물 검색, 약 사진 인식, API 상태, 관리자)

### 관리자 페이지
- Django 기본 Admin UI
- 테이블 형식 데이터 관리
- 필터링, 검색 기능
- CRUD 작업

---

**서버 시작**: `python manage.py runserver`
**첫 페이지**: http://localhost:8000/api/tts/upload/
