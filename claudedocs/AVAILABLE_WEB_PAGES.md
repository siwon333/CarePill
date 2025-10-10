# CarePill - 사용 가능한 웹 페이지

## Django 서버 실행
```bash
python manage.py runserver
```

## 📱 사용 가능한 페이지들

### 1. Django 관리자 페이지 (Admin)
**URL**: http://localhost:8000/admin/

**기능:**
- 약물 데이터 관리
- 사용자 관리
- 음성 샘플 관리
- TTS 캐시 관리

**로그인:**
- 슈퍼유저 계정 필요
- 없으면 생성: `python manage.py createsuperuser`

**관리 가능한 항목:**
- **Medicines** (약물)
  - Medicines (약물 정보)
  - Ingredient mappings (성분 매핑)
  - Drug categories (약물 분류)
  - Interaction rules (상호작용 규칙)

- **Voice TTS** (음성 TTS)
  - User voices (사용자 음성 샘플)
  - TTS caches (TTS 캐시)

- **Users** (사용자)
  - Users (사용자 계정)
  - Groups (그룹)

---

### 2. TTS API Health Check
**URL**: http://localhost:8000/api/tts/health/

**응답 예시:**
```json
{
  "status": "healthy",
  "service": {
    "is_available": true,
    "model_loaded": true,
    "device": "cpu",
    "mock_mode": true
  },
  "timestamp": "2025-10-10T12:34:56.789Z"
}
```

**인증**: 불필요 (누구나 접근 가능)

---

### 3. 약물 검색 API
**URL**: http://localhost:8000/api/search-medicine/?q=타이레놀

**응답 예시:**
```json
{
  "results": [
    {
      "id": 123456,
      "name": "타이레놀정500밀리그램",
      "manufacturer": "한국얀센",
      "ingredients": "Acetaminophen",
      "categories": ["해열진통제"]
    }
  ],
  "count": 1,
  "query": "타이레놀"
}
```

**인증**: 불필요

---

### 4. 약물 상세 정보 API
**URL**: http://localhost:8000/api/medicine/195900043/

**응답**: 특정 약물의 상세 정보

**인증**: 불필요

---

### 5. 약물 상호작용 체크 API
**URL**: http://localhost:8000/api/check-interaction/

**메서드**: POST

**요청 본문:**
```json
{
  "medicine_a_id": 195900043,
  "medicine_b_id": 197400207
}
```

**인증**: 불필요

---

## 🔐 인증이 필요한 API

### TTS 생성 API
**URL**: http://localhost:8000/api/tts/generate/

**메서드**: POST

**헤더:**
```
Authorization: Token 7df8c822d68f5a2f5ca9c152bffda571637ad3db
Content-Type: application/json
```

**요청 본문:**
```json
{
  "text": "약을 드실 시간입니다",
  "use_cache": true,
  "language": "ko"
}
```

---

### 음성 샘플 업로드 API
**URL**: http://localhost:8000/api/tts/upload-voice/

**메서드**: POST

**헤더:**
```
Authorization: Token 7df8c822d68f5a2f5ca9c152bffda571637ad3db
```

**본문**: multipart/form-data
- `voice_file`: 음성 파일 (WAV/MP3)

---

## 🌐 브라우저에서 바로 테스트 가능한 페이지

1. **관리자 페이지**: http://localhost:8000/admin/
   - 로그인 필요
   - GUI로 모든 데이터 관리

2. **Health Check**: http://localhost:8000/api/tts/health/
   - 로그인 불필요
   - JSON 응답

3. **약물 검색**: http://localhost:8000/api/search-medicine/?q=타이레놀
   - 로그인 불필요
   - JSON 응답

4. **약물 상세**: http://localhost:8000/api/medicine/195900043/
   - 로그인 불필요
   - JSON 응답

---

## 📊 웹 UI가 없는 이유

현재 프로젝트는 **API 서버** 중심으로 설계되어 있습니다:

- **Backend**: Django REST API
- **Frontend**: 음성 비서 (voice_assistant_prototype.py)

웹 UI를 추가하려면:
1. React/Vue.js 등 프론트엔드 프레임워크 추가
2. 또는 Django 템플릿으로 HTML 페이지 생성

하지만 음성 비서가 주 인터페이스이므로, 관리는 Django Admin으로 충분합니다.

---

## 🎯 빠른 접속 가이드

**서버 시작:**
```bash
python manage.py runserver
```

**바로 접속:**
```
관리자 페이지:  http://localhost:8000/admin/
Health Check:  http://localhost:8000/api/tts/health/
약물 검색:      http://localhost:8000/api/search-medicine/?q=타이레놀
```

**슈퍼유저 생성 (처음 1회만):**
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@carepill.local
# Password: (원하는 비밀번호)
```
