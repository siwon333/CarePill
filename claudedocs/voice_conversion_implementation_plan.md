# Voice Conversion Implementation Plan

**Date**: 2025-10-10
**Branch**: `feature/voice-conversion`
**Status**: Research & POC Phase

---

## 🎯 목표

네이버 TTS의 고정된 목소리("나라") 대신 **사용자가 제공한 음색**으로 음성을 합성

---

## 📊 Technical Decision: Seed-VC는 라즈베리파이에 적합하지 않음

### ❌ Seed-VC 한계점
- **GPU 권장**: 실시간 변환을 위해 NVIDIA GPU 필요
- **높은 리소스**: 최소 25M 파라미터, 실시간 처리에 상당한 연산 필요
- **CPU 모드 성능**: 라즈베리파이에서 실행 시 극도로 느릴 것으로 예상 (분 단위 처리 가능성)

### ⚠️ sherpa-onnx 한계점
- **Voice Conversion 미지원**: TTS와 STT만 지원, VC 기능 없음
- **대안 불가**: 직접적인 음색 변환 불가능

---

## 🔄 수정된 전략: 하이브리드 접근법

### 옵션 1: 클라우드 기반 Voice Conversion (추천 ⭐⭐⭐⭐⭐)

```
[라즈베리파이]                    [클라우드 서버]
네이버 TTS → MP3 파일 생성
      ↓
   파일 업로드 ----------------→  Seed-VC 25M 모델
                                   (GPU 서버)
                                        ↓
                                  Voice Conversion
                                        ↓
   변환된 파일 다운로드 ←--------  사용자 음색 MP3
      ↓
  라즈베리파이에서 재생
```

**장점**:
- ✅ 라즈베리파이 리소스 부담 없음
- ✅ 빠른 처리 속도 (GPU 활용)
- ✅ 고품질 음성 변환
- ✅ 확장성 좋음 (여러 라즈베리파이 지원 가능)

**단점**:
- ⚠️ 인터넷 연결 필수
- ⚠️ 클라우드 서비스 비용 발생
- ⚠️ 네트워크 지연 (약 1-2초 추가)

**구현 방법**:
```python
# 라즈베리파이 코드
def text_to_speech_cloud(text, user_id):
    # 1. 네이버 TTS로 기본 음성 생성
    base_audio = naver_tts(text)

    # 2. 클라우드 서버로 전송
    response = requests.post(
        "https://your-cloud-server.com/api/voice-convert",
        files={"audio": base_audio},
        data={"user_id": user_id}
    )

    # 3. 변환된 음성 다운로드
    converted_audio = response.content

    # 4. 재생
    play_audio(converted_audio)
```

---

### 옵션 2: 사전 변환 캐싱 (추천 ⭐⭐⭐⭐)

```
자주 사용하는 문장들을 미리 변환하여 저장

[초기 설정 단계 - 클라우드에서 실행]
1. "약 드실 시간입니다"
2. "아침 약을 준비했습니다"
3. "복용 완료되셨나요?"
... (100개 정도 문장)
   ↓
Seed-VC로 일괄 변환 (사용자 음색)
   ↓
변환된 MP3들을 라즈베리파이에 저장

[실시간 실행 - 라즈베리파이]
Intent 분류 → 미리 변환된 파일 찾기 → 재생
```

**장점**:
- ✅ 오프라인 동작 가능
- ✅ 즉시 재생 (지연 없음)
- ✅ 라즈베리파이 리소스 부담 없음
- ✅ 안정적이고 예측 가능

**단점**:
- ⚠️ 제한된 문장만 지원
- ⚠️ 새로운 문장은 실시간 처리 불가
- ⚠️ 초기 설정에 시간 필요

**구현 방법**:
```python
# 사전 변환된 음성 파일 관리
CACHED_VOICES = {
    "morning_medicine": "voices/user_voice_morning_medicine.mp3",
    "lunch_medicine": "voices/user_voice_lunch_medicine.mp3",
    "remind_dosage": "voices/user_voice_remind_dosage.mp3",
    # ... 100개 패턴
}

def text_to_speech_cached(intent, time_slot):
    # Intent 기반으로 미리 변환된 파일 선택
    cache_key = f"{intent}_{time_slot}"

    if cache_key in CACHED_VOICES:
        # 캐시된 음성 재생
        play_audio(CACHED_VOICES[cache_key])
    else:
        # 캐시 없으면 네이버 TTS 기본 음성
        fallback_tts(text)
```

---

### 옵션 3: 라즈베리파이 5 + 경량 모델 (실험적 ⭐⭐)

```
최신 라즈베리파이 5 (8GB RAM)
   +
초경량 Voice Conversion 모델 (ONNX 양자화)
   +
비실시간 처리 허용 (5-10초 대기)
```

**장점**:
- ✅ 완전 오프라인
- ✅ 클라우드 비용 없음
- ✅ 모든 문장 처리 가능

**단점**:
- ❌ 처리 속도 매우 느림 (5-10초)
- ❌ 라즈베리파이 5 필요 (기존 모델로는 불가능)
- ❌ 품질 저하 가능성 (경량 모델)

---

## 🎯 최종 추천: 옵션 1 + 옵션 2 하이브리드

```yaml
Architecture: "Cloud-First with Local Cache Fallback"

Primary Flow (자주 쓰는 문장):
  1. Intent 분류
  2. 캐시된 음성 파일 확인
  3. 있으면 즉시 재생 ✅

Secondary Flow (새로운 문장):
  1. 네이버 TTS 생성
  2. 클라우드로 전송 → Voice Conversion
  3. 변환된 음성 재생
  4. 캐시에 저장 (다음번 사용)

Fallback Flow (오프라인):
  1. 네이버 TTS 기본 음성 사용 (원래 목소리)
```

**이점**:
- ✅ 자주 쓰는 문장: 즉시 재생 (0초 지연)
- ✅ 새로운 문장: 클라우드 처리 (1-2초 지연)
- ✅ 오프라인: 기본 TTS로 동작
- ✅ 점진적 학습: 사용할수록 캐시 증가

---

## 🛠️ 구현 단계

### Phase 1: 클라우드 서버 구축 (우선순위 높음)

1. **서버 선택**: AWS EC2 (GPU 인스턴스) or Google Cloud GPU
2. **Seed-VC 25M 모델 배포**
3. **REST API 구축**:
   ```python
   POST /api/voice-convert
   {
       "audio_base64": "...",
       "user_id": "user123"
   }

   Response:
   {
       "converted_audio_base64": "...",
       "processing_time_ms": 1500
   }
   ```

### Phase 2: 캐시 시스템 구축

1. **자주 사용하는 문장 100개 정의**
2. **Intent별 템플릿 매핑**
3. **초기 음성 변환 배치 처리**
4. **라즈베리파이에 캐시 저장**

### Phase 3: 라즈베리파이 통합

1. **voice_conversion.py 모듈 작성**
2. **text_to_speech() 함수 수정**
3. **캐시 관리 로직 추가**
4. **오프라인 폴백 처리**

---

## 💰 비용 예측

### 클라우드 GPU 서버 (AWS g4dn.xlarge)

```yaml
On-Demand 가격: $0.526/hour

사용 시나리오:
  - 하루 평균 음성 변환 요청: 50회
  - 1회 처리 시간: 1.5초
  - 하루 총 GPU 사용: 75초 (약 0.02 시간)

월간 비용: $0.526 × 0.02 × 30 = $0.32/월 (약 450원)

실제 권장: Spot Instance 사용 시 70% 절감
월간 비용: ~$0.10/월 (약 140원)
```

### 대안: 서버리스 (AWS Lambda + GPU)

```yaml
AWS Lambda GPU (in preview):
  - 요청당 과금
  - 50회/일 × 30일 = 1,500회/월
  - 추정 비용: ~$0.50/월 (약 700원)
```

---

## 📊 성능 예측

| 시나리오 | 처리 시간 | 품질 | 비용 |
|---------|----------|------|------|
| **캐시 히트** (자주 쓰는 문장) | 0ms | ⭐⭐⭐⭐⭐ | 무료 |
| **클라우드 변환** (새 문장) | 1-2초 | ⭐⭐⭐⭐⭐ | ~$0.0003/회 |
| **오프라인 폴백** | 500ms | ⭐⭐⭐ | 무료 |

---

## 🧪 POC (Proof of Concept) 테스트 계획

### Test 1: 로컬 Seed-VC 설치 (Windows PC)
```bash
# Windows PC에서 테스트 (GPU 있으면 더 좋음)
git clone https://github.com/Plachtaa/seed-vc
cd seed-vc
pip install -r requirements.txt

# 25M 모델 다운로드
python download_models.py --model 25M

# 테스트
python convert.py \
  --source naver_tts_output.mp3 \
  --reference user_voice_sample.wav \
  --output converted.mp3
```

### Test 2: 품질 검증
```python
# 1. 네이버 TTS로 "약 드실 시간입니다" 생성
# 2. Seed-VC로 사용자 음색 변환
# 3. 품질 비교:
#    - 발음 명확도
#    - 자연스러움
#    - 음색 유사도
```

### Test 3: 클라우드 API 개발
```python
# Flask/FastAPI로 간단한 API 서버
from fastapi import FastAPI, File, UploadFile
import base64

app = FastAPI()

@app.post("/api/voice-convert")
async def convert_voice(audio: UploadFile, user_id: str):
    # 1. 파일 저장
    # 2. Seed-VC 실행
    # 3. 결과 반환
    pass
```

---

## 🚀 Next Steps

1. ✅ Branch created: `feature/voice-conversion`
2. ✅ Research completed
3. ⏳ **POC Test on Windows PC** (Seed-VC 로컬 테스트)
4. ⏳ **Cloud API Development** (Flask/FastAPI 서버)
5. ⏳ **Cache System Design** (자주 쓰는 문장 100개 정의)
6. ⏳ **Raspberry Pi Integration**
7. ⏳ **Quality Validation**
8. ⏳ **Production Deployment**

---

**Status**: Ready to proceed with local POC testing
**Next Action**: Test Seed-VC on Windows PC first
**Estimated Time**: 1-2 days for POC, 1 week for full cloud deployment
**Risk Level**: Low (fallback to original TTS always available)
