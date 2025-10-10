# Django 서버 실행 및 API 테스트 가이드

## 1. 서버 실행

### Windows CMD에서:
```cmd
cd C:\Users\woo\Desktop\CarePill
venv\Scripts\activate
python manage.py runserver
```

### 또는 PowerShell에서:
```powershell
cd C:\Users\woo\Desktop\CarePill
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

서버가 실행되면 다음과 같은 메시지가 나타납니다:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## 2. API 테스트 (새 터미널 열기)

### 방법 A: Python 스크립트로 테스트
```cmd
cd C:\Users\woo\Desktop\CarePill
venv\Scripts\activate
python test_api_simple.py
```

### 방법 B: 브라우저에서 테스트

1. **약물 검색**
   - URL: http://localhost:8000/api/search-medicine/?q=부루펜
   - 브라우저에서 직접 접속 가능

2. **약물 상세 정보**
   - URL: http://localhost:8000/api/medicine/195900043/
   - 브라우저에서 직접 접속 가능

3. **상호작용 체크** (POST 요청이므로 curl 또는 Postman 필요)
   ```bash
   curl -X POST http://localhost:8000/api/check-interaction/ \
     -H "Content-Type: application/json" \
     -d "{\"medicine_a_id\": 195900043, \"medicine_b_id\": 197400207}"
   ```

### 방법 C: curl로 테스트 (Git Bash 또는 WSL)

```bash
# 약물 검색
curl "http://localhost:8000/api/search-medicine/?q=부루펜"

# 약물 상세
curl "http://localhost:8000/api/medicine/195900043/"

# 상호작용 체크
curl -X POST http://localhost:8000/api/check-interaction/ \
  -H "Content-Type: application/json" \
  -d '{"medicine_a_id": 195900043, "medicine_b_id": 197400207}'
```

## 3. 테스트 시나리오

### 시나리오 1: 상호작용 없음
```
약물 A: 부루펜정 (이부프로펜) - 비스테로이드소염진통제
약물 B: 아네모정 (제산제)
결과: 상호작용 없음 (안전)
```

### 시나리오 2: 상호작용 있음 (중등도)
```
약물 A: 겔포스현탁액 (제산제)
약물 B: 테트라사이클린 (테트라사이클린계)
결과: contraindicated (병용 금기)
- 제산제의 금속 이온이 테트라사이클린 흡수 방해
- 2-3시간 간격 필요
```

### 시나리오 3: 상호작용 있음 (치명적)
```
약물 A: MAO억제제
약물 B: 삼환계항우울제
결과: critical (치명적)
- 세로토닌 증후군 위험
- 절대 병용 금기
```

## 4. API 엔드포인트 목록

| 엔드포인트 | 메서드 | 설명 |
|----------|--------|------|
| /api/search-medicine/ | GET | 약물명 검색 |
| /api/medicine/{id}/ | GET | 약물 상세 정보 |
| /api/check-interaction/ | POST | 약물 상호작용 체크 |

## 5. 예상 응답 예시

### 검색 API 응답:
```json
{
  "results": [
    {
      "id": 123456,
      "name": "부루펜정200밀리그램(이부프로펜)",
      "manufacturer": "삼진제약(주)",
      "ingredients": "Ibuprofen",
      "categories": ["비스테로이드소염진통제"]
    }
  ],
  "count": 1,
  "query": "부루펜"
}
```

### 상호작용 체크 응답 (상호작용 발견):
```json
{
  "has_interaction": true,
  "interaction_count": 1,
  "interactions": [
    {
      "category_a": "제산제",
      "category_b": "테트라사이클린계",
      "interaction_type": "contraindicated",
      "severity": "moderate",
      "description": "제산제의 금속 이온이 테트라사이클린과 킬레이트 형성",
      "recommendation": "병용 금기. 최소 2-3시간 간격 필요"
    }
  ]
}
```

## 6. 문제 해결

### 오류: "ModuleNotFoundError: No module named 'django'"
- 해결: 가상환경을 활성화하지 않았습니다
- 실행: `venv\Scripts\activate`

### 오류: "Port 8000 is already in use"
- 해결: 다른 포트 사용
- 실행: `python manage.py runserver 8001`

### 오류: "Connection refused"
- 해결: 서버가 실행 중인지 확인
- http://localhost:8000 브라우저에서 접속 확인

## 7. 데이터베이스 통계

- 전체 약물: 4,800개
- 매핑된 약물: 3,150개 (66%)
- 약물 분류: 38개
- 상호작용 규칙: 24개
- 매핑 신뢰도: 91% (WHO ATC 기반)

---

# TTS API 서버 가이드

## 8. TTS API 서버 설정 및 실행

### 8.1. 초기 설정 (최초 1회만)

#### 1) API 토큰 생성
```cmd
python scripts\setup_tts_api_token.py
```

생성된 토큰을 `.env` 파일에 추가:
```env
DJANGO_TTS_TOKEN=your_generated_token_here
```

#### 2) 음성 샘플 업로드

**방법 A: Django 관리자 페이지**
1. 서버 실행: `python manage.py runserver`
2. 관리자 페이지 접속: http://localhost:8000/admin/
3. "Voice Tts" → "User voices" → "Add User Voice"
4. 사용자 선택 및 음성 파일 업로드 (5-30초, WAV/MP3)

**방법 B: API로 업로드**
```bash
curl -X POST http://localhost:8000/api/tts/upload-voice/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "voice_file=@path/to/voice_sample.wav"
```

### 8.2. TTS API 테스트

#### 1) 헬스 체크
```cmd
curl http://localhost:8000/api/tts/health/
```

예상 응답:
```json
{
  "status": "healthy",
  "service": {
    "is_available": true,
    "model_loaded": true,
    "device": "cpu",
    "mock_mode": true
  }
}
```

#### 2) TTS 생성 테스트
```bash
curl -X POST http://localhost:8000/api/tts/generate/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"약을 드실 시간입니다\",\"use_cache\":true,\"language\":\"ko\"}"
```

#### 3) Python 테스트 스크립트 실행
```cmd
python scripts\test_tts_api.py
```

### 8.3. 음성 비서 실행

TTS API 설정 후:
```cmd
python voice_assistant_prototype.py
```

## 9. TTS API 엔드포인트

| 엔드포인트 | 메서드 | 설명 | 인증 |
|----------|--------|------|------|
| /api/tts/health/ | GET | 서비스 상태 확인 | 불필요 |
| /api/tts/generate/ | POST | TTS 음성 생성 | 필요 |
| /api/tts/upload-voice/ | POST | 음성 샘플 업로드 | 필요 |

### TTS 생성 요청 예시:
```json
{
  "text": "약을 드실 시간입니다",
  "use_cache": true,
  "language": "ko"
}
```

### TTS 생성 응답 예시:
```json
{
  "success": true,
  "cache_hit": false,
  "audio_url": "/media/tts_cache/83e5d0e3d5035810f7e09c04b1c8d7f4.wav",
  "duration_seconds": 2.5,
  "processing_time_ms": 2150
}
```

## 10. 캐시 관리

### 캐시 통계 확인
```cmd
python manage.py shell
```

```python
from voice_tts.models import TTSCache
print(f"총 캐시 항목: {TTSCache.objects.count()}")

# 최근 캐시 조회
recent = TTSCache.objects.order_by('-created_at')[:10]
for entry in recent:
    print(f"{entry.text[:30]}... - 접근 횟수: {entry.access_count}")
```

### 자주 사용되는 문구 미리 캐시
```python
common_phrases = [
    "약을 드실 시간입니다",
    "오늘의 약 복용 일정입니다",
    "약 복용을 완료했습니다",
    "다음 약 복용까지 4시간 남았습니다"
]
```

## 11. 문제 해결 (TTS)

### "Authentication credentials were not provided"
- `.env` 파일에 `DJANGO_TTS_TOKEN` 확인
- 토큰이 올바른지 확인: `python scripts\setup_tts_api_token.py`

### "No voice sample found for user"
- Django 관리자 페이지에서 음성 샘플 업로드
- 또는 `/api/tts/upload-voice/` API 사용

### "Service not available"
- Django 서버가 실행 중인지 확인
- Health check: `curl http://localhost:8000/api/tts/health/`

## 12. 음성 비서 전체 플로우

```
사용자 발화 "케어필"
    ↓ (Wake Word Detection)
Porcupine 웨이크워드 감지
    ↓ (Speech-to-Text)
Naver Clova STT → "아침약 줘"
    ↓ (Intent Classification)
OpenAI GPT → {"intent": "get_medicine", "time_slot": "morning"}
    ↓ (Response Generation)
OpenAI GPT → "아침약은 타이레놀 1알과 비타민C 1알입니다"
    ↓ (Text-to-Speech)
Django TTS API → 사용자 목소리로 음성 생성
    ↓ (Audio Playback)
스피커 출력
```

---

**문서 업데이트**: 2025-10-10
**추가 내용**: TTS API 서버 설정 및 사용 가이드
