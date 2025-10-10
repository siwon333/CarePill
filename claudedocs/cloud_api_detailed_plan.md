# 옵션 B: 클라우드 API 서버 상세 구현 계획

**Date**: 2025-10-10
**Author**: Claude (SuperClaude Framework)
**Status**: Detailed Planning Phase

---

## 🎯 목표

라즈베리파이의 제한된 성능을 보완하기 위해, **클라우드 GPU 서버에서 Voice Conversion을 처리**하는 REST API를 구축하고, 라즈베리파이와 통합

---

## 📐 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                    Raspberry Pi (CarePill)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Wake Word → STT → Intent → Response Generation → TTS           │
│                                                    (Naver API)   │
│                                                         ↓        │
│                                            "안녕하세요.mp3"       │
│                                                         ↓        │
│                            ┌────────────────────────────┘        │
│                            ↓                                     │
│                    Voice Conversion?                             │
│                    ┌──────────┴──────────┐                      │
│                    │                     │                       │
│               Cache Hit?             Cache Miss                  │
│                    │                     │                       │
│            ✅ Yes (80%)            ❌ No (20%)                   │
│                    ↓                     ↓                       │
│    Play cached_user_voice.mp3    Upload to Cloud API            │
│                                           │                       │
└───────────────────────────────────────────┼───────────────────────┘
                                            │
                                            │ HTTPS
                                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Cloud GPU Server (AWS/GCP)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                     FastAPI REST API                             │
│                            ↓                                     │
│            POST /api/v1/voice-convert                            │
│            {                                                     │
│              "audio_base64": "...",                              │
│              "user_id": "user123"                                │
│            }                                                     │
│                            ↓                                     │
│            ┌───────────────────────────┐                        │
│            │   User Voice Database     │                        │
│            │  (S3 or Cloud Storage)    │                        │
│            │                           │                        │
│            │  user123_voice_sample.wav │                        │
│            └───────────┬───────────────┘                        │
│                        ↓                                         │
│            ┌───────────────────────────┐                        │
│            │    Seed-VC 25M Model      │                        │
│            │      (GPU Inference)       │                        │
│            └───────────┬───────────────┘                        │
│                        ↓                                         │
│            Voice Conversion Processing                          │
│            (1-2 seconds on GPU)                                 │
│                        ↓                                         │
│            {                                                     │
│              "converted_audio_base64": "...",                   │
│              "processing_time_ms": 1500                         │
│            }                                                     │
│                                                                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTPS Response
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Raspberry Pi (CarePill)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Download converted audio → Save to cache → Play                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Phase 1: Cloud API Server 구축

### 1.1 서버 선택

#### 옵션 A: AWS EC2 GPU Instance (추천 ⭐⭐⭐⭐⭐)

**인스턴스 타입**: `g4dn.xlarge`

```yaml
Specs:
  GPU: NVIDIA T4 Tensor Core (16GB)
  vCPU: 4
  RAM: 16GB
  Storage: 125GB NVMe SSD
  Network: Up to 25 Gbps

Pricing:
  On-Demand: $0.526/hour
  Spot Instance: ~$0.158/hour (70% 절감)
  Reserved (1년): ~$0.316/hour (40% 절감)

예상 월간 비용 (Spot Instance):
  - 24/7 운영: $0.158 × 24 × 30 = $113.76/월
  - 실제 사용량 기반 (하루 1시간): $0.158 × 30 = $4.74/월
```

**장점**:
- ✅ 검증된 안정성
- ✅ 쉬운 설정 및 관리
- ✅ 다양한 모니터링 도구
- ✅ Auto Scaling 지원

**단점**:
- ⚠️ 24/7 운영 시 비용 높음 (Spot Instance로 해결)

#### 옵션 B: Google Cloud Platform (GCP) - Compute Engine

**인스턴스 타입**: `n1-standard-4` + `NVIDIA Tesla T4`

```yaml
Specs:
  GPU: NVIDIA Tesla T4
  vCPU: 4
  RAM: 15GB
  Storage: 100GB SSD

Pricing:
  On-Demand: ~$0.45/hour (GPU) + $0.19/hour (VM) = $0.64/hour
  Preemptible: ~$0.11/hour (GPU) + $0.04/hour (VM) = $0.15/hour

예상 월간 비용 (Preemptible):
  - 실제 사용량 기반: $0.15 × 30 = $4.50/월
```

**장점**:
- ✅ GCP 크레딧 제공 ($300 free trial)
- ✅ 유연한 가격 정책

**단점**:
- ⚠️ AWS보다 설정 복잡

#### 옵션 C: 서버리스 (AWS Lambda + GPU) - 🆕 Preview

**Lambda GPU 지원** (현재 Preview 단계)

```yaml
Specs:
  GPU: Customizable
  Execution Time: Up to 15 minutes
  Memory: Up to 10GB

Pricing:
  Pay-per-request: $0.0000166667/GB-second

예상 비용 (1,500 requests/월, 2초/request, 4GB):
  - 1,500 × 2 × 4 × $0.0000166667 = $0.20/월
```

**장점**:
- ✅ 진정한 Pay-as-you-go
- ✅ 서버 관리 불필요
- ✅ Auto Scaling 자동

**단점**:
- ❌ 아직 Preview 단계 (안정성 불확실)
- ❌ Cold Start 지연 가능성

---

### 1.2 FastAPI 서버 구축

#### 디렉토리 구조

```
voice-conversion-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 엔트리포인트
│   ├── config.py            # 환경 변수 및 설정
│   ├── models/              # Pydantic 데이터 모델
│   │   ├── __init__.py
│   │   └── request.py
│   ├── services/            # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── voice_converter.py  # Seed-VC 래퍼
│   │   └── storage.py       # S3/Cloud Storage 관리
│   └── routers/             # API 엔드포인트
│       ├── __init__.py
│       └── convert.py
├── models/                  # Seed-VC 모델 파일
│   └── seed-vc-25M/
├── user_voices/             # 사용자 음성 샘플 (임시)
├── temp/                    # 임시 파일 저장소
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```

#### 핵심 코드 구현

**1. `app/main.py` - FastAPI 애플리케이션**

```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.routers import convert
from app.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="CarePill Voice Conversion API",
    description="Zero-shot voice conversion service for CarePill project",
    version="1.0.0"
)

# CORS 설정 (라즈베리파이에서 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(convert.router, prefix="/api/v1", tags=["voice-conversion"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CarePill Voice Conversion API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    import torch
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

**2. `app/config.py` - 환경 설정**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 앱 설정
    DEBUG: bool = False
    API_KEY: str  # API 인증 키 (보안)

    # Seed-VC 모델 설정
    MODEL_PATH: str = "./models/seed-vc-25M"
    MODEL_SIZE: str = "25M"

    # AWS S3 설정 (사용자 음성 샘플 저장)
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str = "carepill-user-voices"
    S3_REGION: str = "ap-northeast-2"  # 서울 리전

    # 파일 업로드 제한
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_AUDIO_FORMATS: list = ["mp3", "wav", "ogg"]

    # GPU 설정
    DEVICE: str = "cuda"  # or "cpu"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

**3. `app/services/voice_converter.py` - Seed-VC 래퍼**

```python
import torch
import torchaudio
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class VoiceConverter:
    """Seed-VC 모델 래퍼"""

    def __init__(self, model_path: str, device: str = "cuda"):
        self.model_path = Path(model_path)
        self.device = device
        self.model = None
        self._load_model()

    def _load_model(self):
        """Seed-VC 모델 로드"""
        logger.info(f"Loading Seed-VC model from {self.model_path}")

        try:
            # Seed-VC 모델 로드 (실제 구현은 Seed-VC 라이브러리에 따라 다름)
            # 여기서는 의사 코드로 표현
            from seed_vc import SeedVC  # 가상의 import

            self.model = SeedVC.load_model(
                model_path=str(self.model_path),
                device=self.device
            )

            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def convert(
        self,
        source_audio_path: str,
        reference_audio_path: str,
        output_path: str
    ) -> dict:
        """
        음성 변환 수행

        Args:
            source_audio_path: 변환할 원본 음성 (네이버 TTS 출력)
            reference_audio_path: 목표 음성 샘플 (사용자 음성)
            output_path: 변환된 음성 저장 경로

        Returns:
            dict: 변환 결과 및 메타데이터
        """
        import time
        start_time = time.time()

        try:
            logger.info(f"Converting {source_audio_path} with reference {reference_audio_path}")

            # 1. 오디오 로드
            source_audio, sr_source = torchaudio.load(source_audio_path)
            reference_audio, sr_ref = torchaudio.load(reference_audio_path)

            # 2. 샘플링 레이트 통일 (16kHz)
            target_sr = 16000
            if sr_source != target_sr:
                source_audio = torchaudio.transforms.Resample(sr_source, target_sr)(source_audio)
            if sr_ref != target_sr:
                reference_audio = torchaudio.transforms.Resample(sr_ref, target_sr)(reference_audio)

            # 3. GPU로 전송
            source_audio = source_audio.to(self.device)
            reference_audio = reference_audio.to(self.device)

            # 4. Voice Conversion 수행
            with torch.no_grad():
                converted_audio = self.model.convert(
                    source=source_audio,
                    reference=reference_audio
                )

            # 5. 결과 저장
            converted_audio = converted_audio.cpu()
            torchaudio.save(
                output_path,
                converted_audio,
                sample_rate=target_sr
            )

            processing_time = (time.time() - start_time) * 1000  # ms

            logger.info(f"Conversion completed in {processing_time:.2f}ms")

            return {
                "success": True,
                "output_path": output_path,
                "processing_time_ms": processing_time,
                "sample_rate": target_sr
            }

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
```

**4. `app/routers/convert.py` - API 엔드포인트**

```python
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
import base64
import os
import uuid
from pathlib import Path
import logging

from app.config import get_settings, Settings
from app.services.voice_converter import VoiceConverter
from app.services.storage import S3Storage

logger = logging.getLogger(__name__)
router = APIRouter()

# 전역 변수로 모델 로드 (서버 시작 시 한 번만)
voice_converter = None

@router.on_event("startup")
async def load_model():
    """서버 시작 시 모델 로드"""
    global voice_converter
    settings = get_settings()
    voice_converter = VoiceConverter(
        model_path=settings.MODEL_PATH,
        device=settings.DEVICE
    )
    logger.info("Voice Converter loaded and ready")

@router.post("/voice-convert")
async def convert_voice(
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    api_key: str = Form(...),
    settings: Settings = Depends(get_settings)
):
    """
    Voice Conversion API

    Request:
        - audio: 변환할 음성 파일 (네이버 TTS 출력)
        - user_id: 사용자 ID (사용자 음성 샘플 조회용)
        - api_key: API 인증 키

    Response:
        - converted_audio_base64: 변환된 음성 (base64 인코딩)
        - processing_time_ms: 처리 시간 (밀리초)
    """

    # 1. API 키 검증
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # 2. 파일 크기 검증
    audio_data = await audio.read()
    file_size_mb = len(audio_data) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
        )

    # 3. 임시 파일 저장
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    request_id = str(uuid.uuid4())
    source_path = temp_dir / f"{request_id}_source.mp3"
    output_path = temp_dir / f"{request_id}_converted.wav"

    with open(source_path, "wb") as f:
        f.write(audio_data)

    try:
        # 4. S3에서 사용자 음성 샘플 다운로드
        s3_storage = S3Storage()
        reference_path = temp_dir / f"{request_id}_reference.wav"

        user_voice_key = f"users/{user_id}/voice_sample.wav"
        await s3_storage.download_file(
            key=user_voice_key,
            local_path=str(reference_path)
        )

        # 5. Voice Conversion 수행
        result = voice_converter.convert(
            source_audio_path=str(source_path),
            reference_audio_path=str(reference_path),
            output_path=str(output_path)
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])

        # 6. 변환된 파일을 base64로 인코딩
        with open(output_path, "rb") as f:
            converted_audio_bytes = f.read()

        converted_audio_base64 = base64.b64encode(converted_audio_bytes).decode('utf-8')

        # 7. 응답 반환
        response = {
            "success": True,
            "converted_audio_base64": converted_audio_base64,
            "processing_time_ms": result["processing_time_ms"],
            "sample_rate": result["sample_rate"]
        }

        logger.info(f"Request {request_id} completed successfully")

        return response

    except Exception as e:
        logger.error(f"Request {request_id} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 8. 임시 파일 정리
        for path in [source_path, reference_path, output_path]:
            if path.exists():
                os.remove(path)

@router.post("/upload-user-voice")
async def upload_user_voice(
    user_id: str = Form(...),
    voice_sample: UploadFile = File(...),
    api_key: str = Form(...),
    settings: Settings = Depends(get_settings)
):
    """
    사용자 음성 샘플 업로드

    Request:
        - user_id: 사용자 ID
        - voice_sample: 사용자 음성 샘플 파일 (3-10초 권장)
        - api_key: API 인증 키

    Response:
        - success: 업로드 성공 여부
        - s3_key: S3 저장 경로
    """

    # API 키 검증
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # S3 업로드
        s3_storage = S3Storage()
        voice_data = await voice_sample.read()

        s3_key = f"users/{user_id}/voice_sample.wav"
        await s3_storage.upload_file(
            key=s3_key,
            data=voice_data
        )

        return {
            "success": True,
            "s3_key": s3_key,
            "message": "User voice sample uploaded successfully"
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**5. `app/services/storage.py` - S3 Storage 관리**

```python
import boto3
from botocore.exceptions import ClientError
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

class S3Storage:
    """AWS S3 Storage 관리 클래스"""

    def __init__(self):
        settings = get_settings()
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, key: str, data: bytes):
        """S3에 파일 업로드"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data
            )
            logger.info(f"Uploaded {key} to S3")
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    async def download_file(self, key: str, local_path: str):
        """S3에서 파일 다운로드"""
        try:
            self.s3_client.download_file(
                Bucket=self.bucket_name,
                Key=key,
                Filename=local_path
            )
            logger.info(f"Downloaded {key} from S3")
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise
```

**6. `requirements.txt` - 의존성**

```txt
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
pydantic-settings==2.1.0

# PyTorch (CUDA 12.1)
--extra-index-url https://download.pytorch.org/whl/cu121
torch==2.1.2+cu121
torchaudio==2.1.2+cu121

# Seed-VC dependencies (예시)
librosa==0.10.1
soundfile==0.12.1
numpy==1.24.3
scipy==1.11.4

# AWS SDK
boto3==1.34.34

# Utilities
python-dotenv==1.0.0
```

**7. `Dockerfile` - 컨테이너화**

```dockerfile
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Python 설치
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Seed-VC 모델 다운로드 (빌드 시)
RUN mkdir -p models/seed-vc-25M
# TODO: 모델 다운로드 스크립트 추가

# 앱 복사
COPY app/ ./app/

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**8. `.env` - 환경 변수 예시**

```env
# API 설정
DEBUG=false
API_KEY=your_super_secret_api_key_here

# Seed-VC 모델
MODEL_PATH=./models/seed-vc-25M
MODEL_SIZE=25M

# AWS S3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_BUCKET_NAME=carepill-user-voices
S3_REGION=ap-northeast-2

# GPU 설정
DEVICE=cuda
```

---

## 🚀 Phase 2: 라즈베리파이 통합

### 2.1 라즈베리파이 클라이언트 코드

**새 파일: `voice_conversion_client.py`**

```python
"""
Voice Conversion Client for Raspberry Pi
Communicates with Cloud API for voice conversion
"""

import requests
import base64
from pathlib import Path
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceConversionClient:
    """클라우드 Voice Conversion API 클라이언트"""

    def __init__(
        self,
        api_url: str,
        api_key: str,
        user_id: str,
        cache_dir: str = "./voice_cache"
    ):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def convert_voice(
        self,
        audio_file_path: str,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        음성 변환 요청

        Args:
            audio_file_path: 변환할 음성 파일 (네이버 TTS 출력)
            use_cache: 캐시 사용 여부

        Returns:
            변환된 음성 파일 경로 (실패 시 None)
        """

        # 1. 캐시 확인
        if use_cache:
            cache_key = self._get_cache_key(audio_file_path)
            cached_file = self.cache_dir / f"{cache_key}.wav"

            if cached_file.exists():
                logger.info(f"Cache hit: {cached_file}")
                return str(cached_file)

        # 2. API 호출
        try:
            logger.info(f"Calling Voice Conversion API for {audio_file_path}")

            with open(audio_file_path, 'rb') as f:
                files = {'audio': f}
                data = {
                    'user_id': self.user_id,
                    'api_key': self.api_key
                }

                response = requests.post(
                    f"{self.api_url}/api/v1/voice-convert",
                    files=files,
                    data=data,
                    timeout=30  # 30초 타임아웃
                )

            if response.status_code == 200:
                result = response.json()

                # 3. base64 디코딩 및 저장
                converted_audio_bytes = base64.b64decode(
                    result['converted_audio_base64']
                )

                output_path = self.cache_dir / f"{cache_key}.wav"
                with open(output_path, 'wb') as f:
                    f.write(converted_audio_bytes)

                logger.info(
                    f"Conversion completed in {result['processing_time_ms']}ms"
                )

                return str(output_path)
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return None
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return None

    def _get_cache_key(self, audio_file_path: str) -> str:
        """오디오 파일의 캐시 키 생성 (해시 기반)"""
        import hashlib

        with open(audio_file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return f"{self.user_id}_{file_hash}"

    def upload_user_voice(self, voice_sample_path: str) -> bool:
        """
        사용자 음성 샘플 업로드

        Args:
            voice_sample_path: 사용자 음성 샘플 파일 (3-10초 권장)

        Returns:
            업로드 성공 여부
        """
        try:
            logger.info(f"Uploading user voice sample: {voice_sample_path}")

            with open(voice_sample_path, 'rb') as f:
                files = {'voice_sample': f}
                data = {
                    'user_id': self.user_id,
                    'api_key': self.api_key
                }

                response = requests.post(
                    f"{self.api_url}/api/v1/upload-user-voice",
                    files=files,
                    data=data,
                    timeout=30
                )

            if response.status_code == 200:
                logger.info("User voice sample uploaded successfully")
                return True
            else:
                logger.error(f"Upload failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Upload error: {e}")
            return False
```

### 2.2 `voice_assistant_prototype.py` 수정

**기존 `text_to_speech()` 함수 수정**:

```python
# 기존 import에 추가
from voice_conversion_client import VoiceConversionClient

# Config 클래스에 추가
class Config:
    # ... 기존 설정 ...

    # Voice Conversion API
    VC_API_URL = os.getenv('VC_API_URL', 'https://your-api-server.com')
    VC_API_KEY = os.getenv('VC_API_KEY')
    USER_ID = os.getenv('USER_ID', 'default_user')
    ENABLE_VOICE_CONVERSION = os.getenv('ENABLE_VOICE_CONVERSION', 'true').lower() == 'true'

# Voice Conversion 클라이언트 초기화
vc_client = VoiceConversionClient(
    api_url=Config.VC_API_URL,
    api_key=Config.VC_API_KEY,
    user_id=Config.USER_ID
) if Config.ENABLE_VOICE_CONVERSION else None

def text_to_speech(text):
    """Convert text to speech using Naver Clova TTS + Voice Conversion"""
    print("[TTS] Converting text to speech...")

    # STEP 1: 네이버 TTS로 기본 음성 생성
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

    headers = {
        "X-NCP-APIGW-API-KEY-ID": Config.NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": Config.NAVER_CLIENT_SECRET,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "speaker": "nara",
        "volume": "0",
        "speed": "0",
        "pitch": "0",
        "format": "mp3",
        "text": text
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print(f"[TTS ERROR] {response.status_code}: {response.text}")
        return False

    # 네이버 TTS 결과 저장
    base_audio_file = "naver_tts_output.mp3"
    with open(base_audio_file, "wb") as f:
        f.write(response.content)
    print(f"[TTS] Naver TTS saved to {base_audio_file}")

    # STEP 2: Voice Conversion (선택적)
    final_audio_file = base_audio_file

    if Config.ENABLE_VOICE_CONVERSION and vc_client:
        print("[VC] Applying voice conversion...")
        converted_file = vc_client.convert_voice(base_audio_file)

        if converted_file:
            final_audio_file = converted_file
            print(f"[VC] Voice converted to user voice")
        else:
            print("[VC] Conversion failed, using original TTS")

    # STEP 3: 재생
    import subprocess
    subprocess.run(["start", final_audio_file], shell=True)

    return True
```

### 2.3 `.env` 업데이트 (라즈베리파이)

```env
# ... 기존 설정 ...

# Voice Conversion API
VC_API_URL=https://your-ec2-server.compute.amazonaws.com
VC_API_KEY=your_super_secret_api_key_here
USER_ID=user_raspberry_pi_001
ENABLE_VOICE_CONVERSION=true
```

---

## 📊 Phase 3: 배포 및 운영

### 3.1 AWS EC2 배포

**단계별 가이드**:

```bash
# 1. EC2 인스턴스 생성 (g4dn.xlarge)
# AWS Console에서 생성 또는 AWS CLI 사용

# 2. SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Docker 설치
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# 4. NVIDIA Docker Runtime 설치 (GPU 지원)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# 5. 프로젝트 클론 및 빌드
git clone https://github.com/your-repo/voice-conversion-api
cd voice-conversion-api

# 6. 환경 변수 설정
cp .env.example .env
nano .env  # API_KEY, AWS credentials 입력

# 7. Docker Compose로 실행
docker-compose up -d

# 8. 로그 확인
docker-compose logs -f
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    runtime: nvidia
    volumes:
      - ./models:/app/models
      - ./temp:/app/temp
    restart: unless-stopped
    env_file:
      - .env
```

### 3.2 모니터링 및 로깅

**CloudWatch 통합**:

```python
# app/main.py에 추가

import watchtower
import logging

# CloudWatch 로거 설정
logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group='carepill-voice-conversion',
    stream_name='api-server'
))
```

**성능 모니터링**:

```python
# app/routers/convert.py에 추가

from prometheus_client import Counter, Histogram
import time

# 메트릭 정의
REQUEST_COUNT = Counter('voice_conversion_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('voice_conversion_duration_seconds', 'Request duration')

@router.post("/voice-convert")
async def convert_voice(...):
    REQUEST_COUNT.inc()

    start_time = time.time()

    # ... 기존 로직 ...

    REQUEST_DURATION.observe(time.time() - start_time)
```

---

## 💡 최적화 전략

### 4.1 성능 최적화

1. **모델 캐싱**: 서버 시작 시 모델 한 번만 로드
2. **배치 처리**: 여러 요청 동시 처리 (GPU 활용도 증가)
3. **비동기 처리**: FastAPI async 활용
4. **결과 캐싱**: 동일 요청은 재처리 없이 캐시 반환

### 4.2 비용 최적화

1. **Spot Instances**: 70% 비용 절감
2. **Auto Scaling**: 트래픽 없을 때 인스턴스 중지
3. **S3 Lifecycle**: 오래된 음성 샘플 자동 삭제
4. **Lambda 대안**: 트래픽 매우 낮을 때 서버리스 전환

### 4.3 보안

1. **API Key 인증**: 무단 접근 방지
2. **HTTPS 강제**: TLS/SSL 암호화
3. **Rate Limiting**: DDoS 방어
4. **Input Validation**: 악의적 파일 업로드 차단

---

## 🧪 테스트 계획

### 5.1 단위 테스트

```python
# tests/test_voice_converter.py

import pytest
from app.services.voice_converter import VoiceConverter

def test_voice_conversion():
    vc = VoiceConverter(model_path="./models/seed-vc-25M")

    result = vc.convert(
        source_audio_path="tests/fixtures/source.mp3",
        reference_audio_path="tests/fixtures/reference.wav",
        output_path="tests/output/converted.wav"
    )

    assert result["success"] == True
    assert result["processing_time_ms"] < 3000  # 3초 이내
```

### 5.2 통합 테스트

```python
# tests/test_api.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_voice_convert_endpoint():
    with open("tests/fixtures/source.mp3", "rb") as f:
        response = client.post(
            "/api/v1/voice-convert",
            files={"audio": f},
            data={
                "user_id": "test_user",
                "api_key": "test_api_key"
            }
        )

    assert response.status_code == 200
    assert "converted_audio_base64" in response.json()
```

### 5.3 부하 테스트

```bash
# Locust로 부하 테스트
pip install locust

# locustfile.py
from locust import HttpUser, task, between

class VoiceConversionUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def convert_voice(self):
        with open("test_audio.mp3", "rb") as f:
            self.client.post(
                "/api/v1/voice-convert",
                files={"audio": f},
                data={"user_id": "test", "api_key": "key"}
            )

# 실행
locust -f locustfile.py --host=http://your-api-server.com
```

---

## 📅 타임라인

| Phase | 작업 | 예상 시간 |
|-------|------|----------|
| **Week 1** | FastAPI 서버 개발 | 2-3일 |
| | Seed-VC 통합 | 2일 |
| | S3 Storage 구현 | 1일 |
| **Week 2** | AWS EC2 배포 | 1일 |
| | 라즈베리파이 클라이언트 개발 | 2일 |
| | 통합 테스트 | 2일 |
| **Week 3** | 성능 최적화 | 2일 |
| | 모니터링 설정 | 1일 |
| | 문서화 | 1일 |
| | 배포 및 안정화 | 2일 |

**총 예상 시간**: 약 3주

---

## 🎯 성공 지표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **API 응답 시간** | < 2초 | CloudWatch Metrics |
| **변환 품질** | 사용자 만족도 > 80% | A/B 테스트 |
| **가용성** | > 99% | Uptime monitoring |
| **비용** | < $10/월 | AWS Cost Explorer |
| **캐시 히트율** | > 70% | Application logs |

---

**Status**: Detailed planning completed
**Next Action**: Start FastAPI server development
**Risk Level**: Medium (cloud dependency, network latency)
**Fallback**: Always use Naver TTS if API unavailable
