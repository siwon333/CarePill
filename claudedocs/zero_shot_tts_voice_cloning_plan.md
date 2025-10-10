# Zero-Shot TTS with Voice Cloning - 최종 솔루션

**Date**: 2025-10-10
**Branch**: `feature/voice-conversion`
**Status**: Updated Implementation Plan

---

## 🎯 수정된 목표

**변경 전**: Voice Conversion (네이버 TTS → 음성 변환)
**변경 후**: **Zero-Shot TTS with Voice Cloning** (직접 특정 목소리로 TTS 생성)

> "유저와 관련있는 사람의 목소리 스타일로 TTS를 생성하고 싶다"

---

## ✨ 이게 훨씬 더 좋은 이유

### Voice Conversion 방식 (이전)
```
텍스트 → 네이버 TTS (나라 목소리) → Voice Conversion → 사용자 목소리
         [500ms]                      [1-2초, GPU 필요]

총 처리 시간: 2-3초
필요 리소스: 클라우드 GPU 서버
```

### Zero-Shot TTS 방식 (새로운 접근) ⭐
```
텍스트 → Zero-Shot TTS (직접 사용자 목소리로 생성)
         [1-2초, CPU/GPU]

총 처리 시간: 1-2초
필요 리소스: 로컬 또는 클라우드 (선택)
```

**장점**:
- ✅ **단계 감소**: 2단계 → 1단계
- ✅ **속도 향상**: 2-3초 → 1-2초
- ✅ **품질 향상**: 중간 변환 없이 직접 생성
- ✅ **유연성**: 네이버 TTS 의존성 제거

---

## 🏆 최적 솔루션: GPT-SoVITS

### 핵심 스펙

```yaml
Model: GPT-SoVITS v2 ProPlus
Languages: Korean (한국어), English, Japanese, Chinese, Cantonese
Voice Cloning: Zero-shot (5초 샘플) & Few-shot (1분 학습)
License: MIT (상업적 이용 가능)

Performance:
  CPU (M4): RTF 0.526 (실시간보다 느림)
  GPU (CUDA): RTF < 0.1 (실시간보다 빠름)
  First Token: 0.3-0.4초 (스트리밍)

Requirements:
  Python: 3.9-3.11
  CUDA: 12.4-12.8 (GPU 사용 시)
  RAM: 4GB+ (CPU), 8GB+ (GPU)
  Storage: ~5GB (모델)
```

### 주요 특징

1. **Zero-Shot Voice Cloning**
   - 5초 음성 샘플만으로 즉시 TTS
   - 추가 학습 불필요
   - 실시간 목소리 변경 가능

2. **Few-Shot Fine-Tuning** (선택)
   - 1분 음성 데이터로 모델 파인튜닝
   - 특정 인물 목소리 최적화
   - 품질 향상

3. **Cross-Lingual Support**
   - 한국어 학습 → 영어로도 추론 가능
   - 언어 간 목소리 특징 유지

4. **API Server 지원**
   - `api_v2.py` 내장
   - REST API로 간편 통합
   - 스트리밍 지원

---

## 📐 전체 아키텍처

### 옵션 A: 클라우드 기반 (추천 ⭐⭐⭐⭐⭐)

```
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi (CarePill)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Wake Word → STT → Intent → Response Generation             │
│                                      ↓                       │
│                              "약 드실 시간입니다"              │
│                                      ↓                       │
│                          ┌───────────────────┐              │
│                          │  Cache Check?     │              │
│                          └────┬──────────┬───┘              │
│                               │          │                   │
│                          Hit (80%)   Miss (20%)              │
│                               │          │                   │
│                      Play cached.mp3    │                   │
│                                          ↓                   │
└──────────────────────────────────────────┼───────────────────┘
                                           │ HTTPS
                                           ↓
┌─────────────────────────────────────────────────────────────┐
│               Cloud Server (AWS/GCP)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                  GPT-SoVITS API Server                       │
│                         ↓                                    │
│         POST /tts                                            │
│         {                                                    │
│           "text": "약 드실 시간입니다",                        │
│           "user_id": "user123",                              │
│           "reference_audio": "user_voice_5s.wav"             │
│         }                                                    │
│                         ↓                                    │
│         ┌──────────────────────────┐                        │
│         │  GPT-SoVITS v2 Model     │                        │
│         │  (GPU/CPU Inference)      │                        │
│         └──────────┬───────────────┘                        │
│                    ↓                                         │
│         Zero-Shot TTS Generation                            │
│         (1-2초, 사용자 목소리)                                │
│                    ↓                                         │
│         {                                                    │
│           "audio_base64": "...",                             │
│           "duration_ms": 1500                                │
│         }                                                    │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTPS Response
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi (CarePill)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Download → Save to cache → Play                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**장점**:
- ✅ 라즈베리파이 부담 없음
- ✅ GPU 활용으로 빠른 처리
- ✅ 여러 디바이스 지원
- ✅ 캐시로 오프라인 대응

**비용**: ~$2-5/월 (Spot Instance)

---

### 옵션 B: 로컬 CPU 추론 (실험적 ⭐⭐⭐)

```
┌─────────────────────────────────────────────────────────────┐
│            Raspberry Pi 5 (8GB RAM)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Wake Word → STT → Intent → Response Generation             │
│                                      ↓                       │
│                              "약 드실 시간입니다"              │
│                                      ↓                       │
│                  ┌──────────────────────────┐               │
│                  │ GPT-SoVITS (CPU Mode)    │               │
│                  │ + User Voice Sample      │               │
│                  └──────────┬───────────────┘               │
│                             ↓                                │
│                  Zero-Shot TTS Generation                   │
│                  (3-5초, 비실시간)                            │
│                             ↓                                │
│                      Play Audio                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**장점**:
- ✅ 완전 오프라인
- ✅ 클라우드 비용 없음
- ✅ 프라이버시 보장

**단점**:
- ⚠️ 처리 느림 (3-5초)
- ⚠️ 라즈베리파이 5 필요 (기존 모델로는 어려움)
- ⚠️ 메모리 부족 가능성

---

### 옵션 C: 하이브리드 (최고 효율 ⭐⭐⭐⭐⭐)

```yaml
Primary: Cloud API (새로운 문장, 빠른 처리)
Cache: Local Storage (자주 쓰는 문장, 즉시 재생)
Fallback: Naver TTS (API 장애 시)

캐시 히트율 목표: > 80%
평균 응답 시간: < 500ms (캐시) / < 2초 (API)
오프라인 대응: 캐시 + 네이버 TTS
```

---

## 🛠️ 구현 계획

### Phase 1: GPT-SoVITS API 서버 구축 (3-5일)

#### 1.1 서버 구조

**디렉토리**:
```
gpt-sovits-api/
├── app/
│   ├── main.py              # FastAPI 앱
│   ├── config.py            # 환경 설정
│   ├── services/
│   │   ├── tts_service.py   # GPT-SoVITS 래퍼
│   │   └── storage.py       # S3 사용자 음성 관리
│   └── routers/
│       └── tts.py           # API 엔드포인트
├── models/                  # GPT-SoVITS 모델
├── user_voices/             # 사용자 음성 샘플
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

#### 1.2 핵심 코드

**`app/main.py`**:
```python
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="CarePill GPT-SoVITS TTS API")

from app.routers import tts
app.include_router(tts.router, prefix="/api/v1", tags=["tts"])

@app.get("/health")
async def health():
    return {"status": "healthy", "model": "GPT-SoVITS v2"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
```

**`app/services/tts_service.py`**:
```python
import torch
from GPTSoVITS.TTS_infer_pack.TTS import TTS

class GPTSoVITSService:
    """GPT-SoVITS TTS 서비스"""

    def __init__(self, model_path: str, device: str = "cuda"):
        self.device = device
        self.tts = TTS()
        self.tts.load_model(model_path, device=device)

    def generate_speech(
        self,
        text: str,
        reference_audio_path: str,
        output_path: str,
        language: str = "ko"  # Korean
    ) -> dict:
        """
        Zero-shot TTS 생성

        Args:
            text: 생성할 텍스트 (예: "약 드실 시간입니다")
            reference_audio_path: 참조 음성 파일 (5초+)
            output_path: 출력 파일 경로
            language: 언어 코드 (ko, en, ja, zh, yue)

        Returns:
            dict: 생성 결과 및 메타데이터
        """
        import time
        start_time = time.time()

        try:
            # Zero-shot TTS 생성
            self.tts.generate(
                text=text,
                ref_audio_path=reference_audio_path,
                language=language,
                output_path=output_path
            )

            processing_time = (time.time() - start_time) * 1000  # ms

            return {
                "success": True,
                "output_path": output_path,
                "processing_time_ms": processing_time,
                "text_length": len(text)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

**`app/routers/tts.py`**:
```python
from fastapi import APIRouter, Form, HTTPException
import base64
import os
from pathlib import Path

from app.services.tts_service import GPTSoVITSService
from app.services.storage import S3Storage

router = APIRouter()

# 전역 TTS 서비스 (서버 시작 시 로드)
tts_service = None

@router.on_event("startup")
async def load_model():
    global tts_service
    tts_service = GPTSoVITSService(
        model_path="./models/gpt-sovits-v2",
        device="cuda"  # or "cpu"
    )

@router.post("/tts")
async def text_to_speech(
    text: str = Form(...),
    user_id: str = Form(...),
    api_key: str = Form(...)
):
    """
    Zero-Shot TTS API

    Request:
        - text: 생성할 텍스트
        - user_id: 사용자 ID (음성 샘플 조회용)
        - api_key: API 인증 키

    Response:
        - audio_base64: 생성된 음성 (base64)
        - processing_time_ms: 처리 시간
    """

    # API 키 검증
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # 1. S3에서 사용자 음성 샘플 다운로드
        s3 = S3Storage()
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        reference_path = temp_dir / f"{user_id}_reference.wav"
        await s3.download_file(
            key=f"users/{user_id}/voice_sample.wav",
            local_path=str(reference_path)
        )

        # 2. TTS 생성
        output_path = temp_dir / f"{user_id}_output.wav"
        result = tts_service.generate_speech(
            text=text,
            reference_audio_path=str(reference_path),
            output_path=str(output_path),
            language="ko"
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])

        # 3. Base64 인코딩
        with open(output_path, "rb") as f:
            audio_bytes = f.read()

        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        # 4. 응답
        return {
            "success": True,
            "audio_base64": audio_base64,
            "processing_time_ms": result["processing_time_ms"],
            "text_length": result["text_length"]
        }

    finally:
        # 임시 파일 정리
        if reference_path.exists():
            os.remove(reference_path)
        if output_path.exists():
            os.remove(output_path)
```

**`requirements.txt`**:
```txt
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# GPT-SoVITS
# (실제 설치는 GitHub에서)
torch==2.1.2
torchaudio==2.1.2

# Utilities
boto3==1.34.34
python-dotenv==1.0.0
```

**설치 스크립트** (`setup.sh`):
```bash
#!/bin/bash

# 1. GPT-SoVITS 클론
git clone https://github.com/RVC-Boss/GPT-SoVITS
cd GPT-SoVITS

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 모델 다운로드
python download_models.py

# 4. API 서버 라이브러리 설치
cd ..
pip install -r requirements.txt
```

---

### Phase 2: 라즈베리파이 통합 (2-3일)

#### 2.1 TTS 클라이언트

**`gpt_sovits_client.py`**:
```python
"""
GPT-SoVITS TTS Client for Raspberry Pi
"""

import requests
import base64
from pathlib import Path
import hashlib
import logging

logger = logging.getLogger(__name__)

class GPTSoVITSClient:
    """GPT-SoVITS API 클라이언트"""

    def __init__(
        self,
        api_url: str,
        api_key: str,
        user_id: str,
        cache_dir: str = "./tts_cache"
    ):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def text_to_speech(
        self,
        text: str,
        use_cache: bool = True
    ) -> str:
        """
        텍스트를 음성으로 변환

        Args:
            text: 변환할 텍스트
            use_cache: 캐시 사용 여부

        Returns:
            생성된 음성 파일 경로
        """

        # 1. 캐시 확인
        if use_cache:
            cache_key = self._get_cache_key(text)
            cached_file = self.cache_dir / f"{cache_key}.wav"

            if cached_file.exists():
                logger.info(f"Cache hit for: {text[:20]}...")
                return str(cached_file)

        # 2. API 호출
        try:
            logger.info(f"Calling TTS API for: {text}")

            response = requests.post(
                f"{self.api_url}/api/v1/tts",
                data={
                    "text": text,
                    "user_id": self.user_id,
                    "api_key": self.api_key
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                # 3. Base64 디코딩 및 저장
                audio_bytes = base64.b64decode(result["audio_base64"])

                output_path = self.cache_dir / f"{cache_key}.wav"
                with open(output_path, "wb") as f:
                    f.write(audio_bytes)

                logger.info(f"TTS generated in {result['processing_time_ms']}ms")

                return str(output_path)
            else:
                logger.error(f"API error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None

    def _get_cache_key(self, text: str) -> str:
        """텍스트의 캐시 키 생성"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{self.user_id}_{text_hash}"

    def upload_voice_sample(self, voice_sample_path: str) -> bool:
        """사용자 음성 샘플 업로드"""
        # 구현은 Voice Conversion 클라이언트와 유사
        pass
```

#### 2.2 `voice_assistant_prototype.py` 수정

```python
# 기존 import에 추가
from gpt_sovits_client import GPTSoVITSClient
import os

# Config 클래스 수정
class Config:
    # ... 기존 설정 ...

    # GPT-SoVITS TTS
    GPTSOVITS_API_URL = os.getenv('GPTSOVITS_API_URL')
    GPTSOVITS_API_KEY = os.getenv('GPTSOVITS_API_KEY')
    USER_ID = os.getenv('USER_ID', 'default_user')
    ENABLE_CUSTOM_VOICE = os.getenv('ENABLE_CUSTOM_VOICE', 'true').lower() == 'true'

# TTS 클라이언트 초기화
tts_client = GPTSoVITSClient(
    api_url=Config.GPTSOVITS_API_URL,
    api_key=Config.GPTSOVITS_API_KEY,
    user_id=Config.USER_ID
) if Config.ENABLE_CUSTOM_VOICE else None

def text_to_speech(text):
    """Convert text to speech"""
    print("[TTS] Converting text to speech...")

    # 커스텀 목소리 사용
    if Config.ENABLE_CUSTOM_VOICE and tts_client:
        print("[TTS] Using GPT-SoVITS custom voice...")
        audio_file = tts_client.text_to_speech(text)

        if audio_file:
            print(f"[TTS] Custom voice generated")
        else:
            print("[TTS] Custom voice failed, using Naver TTS fallback")
            audio_file = naver_tts_fallback(text)
    else:
        # 네이버 TTS (기본)
        audio_file = naver_tts_fallback(text)

    # 재생
    import subprocess
    subprocess.run(["start", audio_file], shell=True)
    return True

def naver_tts_fallback(text):
    """네이버 TTS (폴백)"""
    # 기존 네이버 TTS 코드
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    # ... (기존 코드 유지)
    return "naver_tts_output.mp3"
```

#### 2.3 `.env` 업데이트

```env
# ... 기존 설정 ...

# GPT-SoVITS TTS
GPTSOVITS_API_URL=https://your-api-server.com
GPTSOVITS_API_KEY=your_api_key_here
USER_ID=carepill_user_001
ENABLE_CUSTOM_VOICE=true
```

---

### Phase 3: 배포 및 최적화 (2-3일)

#### 3.1 AWS EC2 배포

**인스턴스 타입**: `g4dn.xlarge` (GPU) 또는 `t3.large` (CPU 테스트)

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  gpt-sovits-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    runtime: nvidia  # GPU 사용 시
    volumes:
      - ./models:/app/models
      - ./user_voices:/app/user_voices
    restart: unless-stopped
    env_file:
      - .env
```

**배포 스크립트**:
```bash
# EC2 인스턴스 접속
ssh -i key.pem ubuntu@your-ec2-ip

# Docker 및 NVIDIA Runtime 설치
sudo apt-get update
sudo apt-get install -y docker.io nvidia-docker2

# 프로젝트 클론
git clone https://github.com/your-repo/gpt-sovits-api
cd gpt-sovits-api

# 환경 변수 설정
cp .env.example .env
nano .env

# Docker Compose 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

#### 3.2 성능 최적화

1. **모델 캐싱**: 서버 시작 시 한 번만 로드
2. **스트리밍**: 첫 음절부터 재생 (지연 감소)
3. **배치 처리**: 여러 요청 동시 처리
4. **결과 캐싱**: 동일 텍스트는 재생성 안 함

#### 3.3 비용 최적화

```yaml
Option 1: Spot Instance
  Instance: g4dn.xlarge
  Cost: $0.158/hour × 24h × 30d = $113.76/월
  실사용 (1시간/일): $0.158 × 30 = $4.74/월

Option 2: Serverless (Lambda GPU)
  Cost: ~$0.50/월 (1,500 requests)

Option 3: CPU Instance (t3.large)
  Cost: $0.0832/hour × 24h × 30d = $59.90/월
  Spot: ~$20/월
  실사용 (1시간/일): $2.50/월

추천: Option 1 (Spot Instance) - $4.74/월
```

---

## 📊 솔루션 비교

| 특징 | GPT-SoVITS (새) | Voice Conversion (이전) | 네이버 TTS (현재) |
|------|----------------|------------------------|------------------|
| **목소리** | 완전 커스텀 ⭐⭐⭐⭐⭐ | 커스텀 ⭐⭐⭐⭐ | 고정 (나라) ⭐ |
| **속도** | 1-2초 ⭐⭐⭐⭐ | 2-3초 ⭐⭐⭐ | 500ms ⭐⭐⭐⭐⭐ |
| **품질** | 매우 높음 ⭐⭐⭐⭐⭐ | 높음 ⭐⭐⭐⭐ | 높음 ⭐⭐⭐⭐ |
| **비용** | $2-5/월 ⭐⭐⭐⭐ | $1-5/월 ⭐⭐⭐⭐ | 무료 ⭐⭐⭐⭐⭐ |
| **오프라인** | 캐시 가능 ⭐⭐⭐⭐ | 캐시 가능 ⭐⭐⭐⭐ | 불가 ⭐ |
| **설정 난이도** | 중간 ⭐⭐⭐ | 높음 ⭐⭐ | 낮음 ⭐⭐⭐⭐⭐ |

---

## 🧪 테스트 계획

### Test 1: 로컬 GPT-SoVITS 테스트 (Windows PC)

```bash
# 1. GPT-SoVITS 설치
git clone https://github.com/RVC-Boss/GPT-SoVITS
cd GPT-SoVITS
pip install -r requirements.txt

# 2. 모델 다운로드
python download_models.py

# 3. 웹 UI 실행
python webui.py

# 4. 브라우저에서 테스트
# - 5초 음성 샘플 업로드
# - "약 드실 시간입니다" 입력
# - 생성 및 품질 확인
```

### Test 2: API 서버 테스트

```bash
# API 서버 시작
python app/main.py

# 테스트 요청
curl -X POST http://localhost:8000/api/v1/tts \
  -F "text=약 드실 시간입니다" \
  -F "user_id=test_user" \
  -F "api_key=test_key"
```

### Test 3: 라즈베리파이 통합 테스트

```python
# voice_assistant_prototype.py 실행
python voice_assistant_prototype.py

# 테스트 시나리오:
# 1. Wake word: "케어필"
# 2. 명령: "아침약 줘"
# 3. 응답: GPT-SoVITS로 생성 (커스텀 목소리)
```

---

## 📅 타임라인

| Week | 작업 | 예상 시간 |
|------|------|----------|
| **Week 1** | GPT-SoVITS 로컬 테스트 | 1-2일 |
| | API 서버 개발 | 2-3일 |
| **Week 2** | 라즈베리파이 클라이언트 개발 | 2일 |
| | 통합 테스트 | 2일 |
| **Week 3** | AWS 배포 | 1일 |
| | 성능 최적화 | 2일 |
| | 문서화 및 안정화 | 2일 |

**총 예상 시간**: 약 2-3주

---

## 🎯 성공 지표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **TTS 응답 시간** | < 2초 | API 로그 |
| **음성 품질** | 사용자 만족도 > 85% | A/B 테스트 |
| **캐시 히트율** | > 80% | Application logs |
| **가용성** | > 99.5% | Uptime monitoring |
| **월간 비용** | < $10 | AWS Cost Explorer |

---

## 🚀 Next Steps

### 즉시 시작 가능한 작업:

1. **Windows PC에서 GPT-SoVITS 테스트**
   ```bash
   git clone https://github.com/RVC-Boss/GPT-SoVITS
   cd GPT-SoVITS
   pip install -r requirements.txt
   python webui.py
   ```

2. **5초 음성 샘플 준비**
   - 사용자 또는 관련 인물 목소리 녹음
   - 깨끗한 음질, 배경 소음 없이
   - WAV 또는 MP3 형식

3. **테스트 문장 정의**
   - "약 드실 시간입니다"
   - "아침 약을 준비했습니다"
   - "복용하셨나요?"
   - ... (20-30개)

어떤 단계부터 시작하시겠습니까?

---

**Status**: Ready to implement
**Recommended**: Start with local GPT-SoVITS testing
**Risk Level**: Low (always have Naver TTS fallback)
**Expected Quality**: ⭐⭐⭐⭐⭐ (Much better than Voice Conversion)
