# Django TTS Integration Plan - GPT-SoVITS

**Date**: 2025-10-10
**Branch**: `feature/voice-conversion`
**Framework**: Django 5.2.7

---

## 🎯 목표

기존 Django 프로젝트에 **GPT-SoVITS TTS 앱 추가**하여 사용자 맞춤 음성 생성 API 제공

---

## 📐 현재 Django 구조

```
CarePill/
├── medicine_project/          # Django 프로젝트
│   ├── settings.py           # Django 설정
│   ├── urls.py               # 메인 URL 설정
│   └── wsgi.py
├── medicines/                 # 의약품 앱
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── ocr/                       # OCR 앱
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── media/                     # 업로드 파일
├── db.sqlite3                 # SQLite DB
└── manage.py
```

**현재 URL 구조**:
- `/admin/` - Django Admin
- `/api/medicines/` - 의약품 API
- `/ocr/` - OCR API

---

## ✨ 새로운 구조 (TTS 추가)

```
CarePill/
├── medicine_project/
│   ├── settings.py           # ← 'voice_tts' 앱 추가
│   ├── urls.py               # ← '/api/tts/' 경로 추가
│   └── wsgi.py
├── medicines/                 # 기존 앱
├── ocr/                       # 기존 앱
├── voice_tts/                 # 🆕 TTS 앱
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py             # UserVoice, TTSCache 모델
│   ├── views.py              # TTS API 뷰
│   ├── urls.py               # TTS URL 라우팅
│   ├── services/             # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── gpt_sovits.py    # GPT-SoVITS 래퍼
│   │   └── storage.py       # 파일 저장 관리
│   ├── serializers.py        # DRF Serializers
│   ├── admin.py              # Admin 인터페이스
│   └── migrations/
├── models/                    # 🆕 GPT-SoVITS 모델 파일
│   └── gpt-sovits-v2/
├── user_voices/               # 🆕 사용자 음성 샘플
├── tts_cache/                 # 🆕 TTS 캐시 파일
└── requirements.txt           # ← GPT-SoVITS 의존성 추가
```

**새로운 URL 구조**:
- `/api/tts/generate/` - TTS 생성 API (POST)
- `/api/tts/upload-voice/` - 사용자 음성 업로드 (POST)
- `/api/tts/cache/<cache_key>/` - 캐시된 음성 조회 (GET)
- `/admin/voice_tts/` - TTS 관리 페이지

---

## 🛠️ Django 앱 구조 (voice_tts)

### 1. 모델 (`models.py`)

```python
from django.db import models
from django.contrib.auth.models import User
import hashlib

class UserVoice(models.Model):
    """사용자 음성 샘플 모델"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='voice_sample'
    )
    voice_file = models.FileField(
        upload_to='user_voices/',
        help_text='5-10초 음성 샘플 (WAV 권장)'
    )
    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text='음성 샘플 길이'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = '사용자 음성'
        verbose_name_plural = '사용자 음성 샘플'

    def __str__(self):
        return f"{self.user.username}의 음성 샘플"


class TTSCache(models.Model):
    """TTS 캐시 모델 (자주 쓰는 문장 저장)"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tts_caches'
    )
    text = models.TextField(
        help_text='TTS 텍스트'
    )
    text_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text='텍스트 MD5 해시'
    )
    audio_file = models.FileField(
        upload_to='tts_cache/',
        help_text='생성된 음성 파일'
    )
    duration_seconds = models.FloatField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accessed_at = models.DateTimeField(auto_now=True)
    access_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'TTS 캐시'
        verbose_name_plural = 'TTS 캐시'
        unique_together = ('user', 'text_hash')
        ordering = ['-accessed_at']

    def __str__(self):
        return f"{self.user.username} - {self.text[:30]}..."

    @staticmethod
    def generate_hash(text):
        """텍스트 해시 생성"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def increment_access(self):
        """접근 횟수 증가"""
        self.access_count += 1
        self.save(update_fields=['access_count', 'accessed_at'])
```

### 2. Serializers (`serializers.py`)

```python
from rest_framework import serializers
from .models import UserVoice, TTSCache

class UserVoiceSerializer(serializers.ModelSerializer):
    """사용자 음성 샘플 Serializer"""

    class Meta:
        model = UserVoice
        fields = ['id', 'voice_file', 'duration_seconds', 'uploaded_at', 'is_active']
        read_only_fields = ['id', 'uploaded_at']


class TTSGenerateSerializer(serializers.Serializer):
    """TTS 생성 요청 Serializer"""

    text = serializers.CharField(
        max_length=500,
        help_text='생성할 텍스트 (한글 권장)'
    )
    use_cache = serializers.BooleanField(
        default=True,
        help_text='캐시 사용 여부'
    )


class TTSResponseSerializer(serializers.Serializer):
    """TTS 생성 응답 Serializer"""

    success = serializers.BooleanField()
    audio_url = serializers.CharField(allow_null=True)
    audio_base64 = serializers.CharField(allow_null=True)
    cache_hit = serializers.BooleanField()
    processing_time_ms = serializers.FloatField(allow_null=True)
    text_length = serializers.IntegerField()
    message = serializers.CharField(allow_null=True)
```

### 3. GPT-SoVITS 서비스 (`services/gpt_sovits.py`)

```python
"""
GPT-SoVITS TTS Service
"""
import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class GPTSoVITSService:
    """GPT-SoVITS TTS 서비스 클래스"""

    _instance = None
    _model_loaded = False

    def __new__(cls):
        """싱글톤 패턴 (서버당 모델 1개만 로드)"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._model_loaded:
            self.model_path = os.getenv('GPTSOVITS_MODEL_PATH', './models/gpt-sovits-v2')
            self.device = os.getenv('GPTSOVITS_DEVICE', 'cpu')  # 'cuda' or 'cpu'
            self._load_model()

    def _load_model(self):
        """모델 로드 (서버 시작 시 1회)"""
        try:
            logger.info(f"Loading GPT-SoVITS model from {self.model_path}")

            # TODO: 실제 GPT-SoVITS 모델 로드 코드
            # from GPTSoVITS.TTS_infer_pack.TTS import TTS
            # self.tts = TTS()
            # self.tts.load_model(self.model_path, device=self.device)

            # 현재는 Mock으로 대체
            self.tts = None  # Mock

            self._model_loaded = True
            logger.info("GPT-SoVITS model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load GPT-SoVITS model: {e}")
            raise

    def generate_speech(
        self,
        text: str,
        reference_audio_path: str,
        output_path: str,
        language: str = "ko"
    ) -> dict:
        """
        Zero-shot TTS 생성

        Args:
            text: 생성할 텍스트
            reference_audio_path: 참조 음성 파일 경로
            output_path: 출력 파일 경로
            language: 언어 코드 (ko, en, ja, zh, yue)

        Returns:
            dict: {
                'success': bool,
                'output_path': str,
                'processing_time_ms': float,
                'error': str (optional)
            }
        """
        start_time = time.time()

        try:
            logger.info(f"Generating TTS for text: {text[:50]}...")

            # TODO: 실제 GPT-SoVITS TTS 생성 코드
            # self.tts.generate(
            #     text=text,
            #     ref_audio_path=reference_audio_path,
            #     language=language,
            #     output_path=output_path
            # )

            # 현재는 Mock (더미 파일 생성)
            import shutil
            shutil.copy(reference_audio_path, output_path)

            processing_time = (time.time() - start_time) * 1000

            logger.info(f"TTS generated in {processing_time:.2f}ms")

            return {
                'success': True,
                'output_path': output_path,
                'processing_time_ms': processing_time
            }

        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def is_ready(self) -> bool:
        """모델 로드 완료 여부"""
        return self._model_loaded
```

### 4. Views (`views.py`)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.files.base import ContentFile
import base64
import os
from pathlib import Path
import logging

from .models import UserVoice, TTSCache
from .serializers import (
    UserVoiceSerializer,
    TTSGenerateSerializer,
    TTSResponseSerializer
)
from .services.gpt_sovits import GPTSoVITSService

logger = logging.getLogger(__name__)


class TTSGenerateView(APIView):
    """TTS 생성 API"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST /api/tts/generate/

        Request:
            {
                "text": "약 드실 시간입니다",
                "use_cache": true
            }

        Response:
            {
                "success": true,
                "audio_url": "/media/tts_cache/xxx.wav",
                "audio_base64": "...",  # 선택적
                "cache_hit": true,
                "processing_time_ms": 50.5,
                "text_length": 10
            }
        """

        serializer = TTSGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        text = serializer.validated_data['text']
        use_cache = serializer.validated_data['use_cache']
        user = request.user

        # 1. 캐시 확인
        if use_cache:
            text_hash = TTSCache.generate_hash(text)
            cached = TTSCache.objects.filter(
                user=user,
                text_hash=text_hash
            ).first()

            if cached:
                logger.info(f"Cache hit for user {user.username}")
                cached.increment_access()

                return Response({
                    'success': True,
                    'audio_url': cached.audio_file.url,
                    'cache_hit': True,
                    'processing_time_ms': 0,
                    'text_length': len(text)
                })

        # 2. 사용자 음성 샘플 확인
        try:
            user_voice = UserVoice.objects.get(user=user, is_active=True)
        except UserVoice.DoesNotExist:
            return Response({
                'success': False,
                'message': '사용자 음성 샘플이 없습니다. 먼저 음성을 업로드해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. TTS 생성
        tts_service = GPTSoVITSService()

        if not tts_service.is_ready():
            return Response({
                'success': False,
                'message': 'TTS 서비스가 준비되지 않았습니다.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 임시 출력 파일 경로
        output_dir = Path(settings.MEDIA_ROOT) / 'tts_cache'
        output_dir.mkdir(exist_ok=True)

        text_hash = TTSCache.generate_hash(text)
        output_filename = f"{user.id}_{text_hash}.wav"
        output_path = output_dir / output_filename

        # TTS 생성
        result = tts_service.generate_speech(
            text=text,
            reference_audio_path=user_voice.voice_file.path,
            output_path=str(output_path),
            language='ko'
        )

        if not result['success']:
            return Response({
                'success': False,
                'message': f"TTS 생성 실패: {result.get('error')}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 4. 캐시 저장
        cache_entry, created = TTSCache.objects.get_or_create(
            user=user,
            text_hash=text_hash,
            defaults={
                'text': text,
                'audio_file': f'tts_cache/{output_filename}'
            }
        )

        if not created:
            cache_entry.increment_access()

        # 5. Base64 인코딩 (선택적)
        audio_base64 = None
        if request.GET.get('format') == 'base64':
            with open(output_path, 'rb') as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        return Response({
            'success': True,
            'audio_url': cache_entry.audio_file.url,
            'audio_base64': audio_base64,
            'cache_hit': False,
            'processing_time_ms': result['processing_time_ms'],
            'text_length': len(text)
        })


class UserVoiceUploadView(APIView):
    """사용자 음성 샘플 업로드 API"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST /api/tts/upload-voice/

        Request (multipart/form-data):
            voice_file: <file>

        Response:
            {
                "success": true,
                "message": "음성 샘플이 업로드되었습니다",
                "voice_id": 1
            }
        """

        if 'voice_file' not in request.FILES:
            return Response({
                'success': False,
                'message': '음성 파일이 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        voice_file = request.FILES['voice_file']
        user = request.user

        # 기존 음성 샘플 비활성화
        UserVoice.objects.filter(user=user).update(is_active=False)

        # 새 음성 샘플 저장
        user_voice = UserVoice.objects.create(
            user=user,
            voice_file=voice_file,
            is_active=True
        )

        logger.info(f"Voice sample uploaded for user {user.username}")

        return Response({
            'success': True,
            'message': '음성 샘플이 업로드되었습니다.',
            'voice_id': user_voice.id
        })


class TTSHealthCheckView(APIView):
    """TTS 서비스 상태 확인"""

    def get(self, request):
        """
        GET /api/tts/health/

        Response:
            {
                "status": "healthy",
                "model_loaded": true,
                "device": "cpu"
            }
        """

        tts_service = GPTSoVITSService()

        return Response({
            'status': 'healthy' if tts_service.is_ready() else 'unavailable',
            'model_loaded': tts_service.is_ready(),
            'device': tts_service.device
        })
```

### 5. URLs (`urls.py`)

```python
from django.urls import path
from .views import (
    TTSGenerateView,
    UserVoiceUploadView,
    TTSHealthCheckView
)

app_name = 'voice_tts'

urlpatterns = [
    path('generate/', TTSGenerateView.as_view(), name='generate'),
    path('upload-voice/', UserVoiceUploadView.as_view(), name='upload-voice'),
    path('health/', TTSHealthCheckView.as_view(), name='health'),
]
```

### 6. Admin (`admin.py`)

```python
from django.contrib import admin
from .models import UserVoice, TTSCache

@admin.register(UserVoice)
class UserVoiceAdmin(admin.ModelAdmin):
    list_display = ['user', 'duration_seconds', 'is_active', 'uploaded_at']
    list_filter = ['is_active', 'uploaded_at']
    search_fields = ['user__username']
    readonly_fields = ['uploaded_at', 'updated_at']


@admin.register(TTSCache)
class TTSCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'text_preview', 'access_count', 'created_at', 'accessed_at']
    list_filter = ['created_at', 'accessed_at']
    search_fields = ['user__username', 'text']
    readonly_fields = ['text_hash', 'created_at', 'accessed_at']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = '텍스트'
```

---

## 🔧 설정 업데이트

### 1. `settings.py` 수정

```python
# medicine_project/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # 🆕 DRF 추가
    'medicines',
    'ocr',
    'voice_tts',  # 🆕 TTS 앱 추가
]

# 🆕 DRF 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# 🆕 GPT-SoVITS 설정
GPTSOVITS_MODEL_PATH = os.getenv('GPTSOVITS_MODEL_PATH', './models/gpt-sovits-v2')
GPTSOVITS_DEVICE = os.getenv('GPTSOVITS_DEVICE', 'cpu')  # 'cuda' for GPU
```

### 2. `urls.py` 수정

```python
# medicine_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/medicines/', include('medicines.urls')),
    path('ocr/', include('ocr.urls')),
    path('api/tts/', include('voice_tts.urls')),  # 🆕 TTS API
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 3. `requirements.txt` 업데이트

```txt
# ... 기존 패키지 ...

# Django REST Framework
djangorestframework==3.14.0

# GPT-SoVITS dependencies
torch==2.1.2
torchaudio==2.1.2
librosa==0.10.1
soundfile==0.12.1
scipy==1.11.4

# Audio processing
pydub==0.25.1
```

---

## 📦 Django 앱 생성 및 설정

### 단계별 명령어

```bash
# 1. Django 앱 생성
python manage.py startapp voice_tts

# 2. 디렉토리 구조 생성
mkdir voice_tts/services
touch voice_tts/services/__init__.py
touch voice_tts/services/gpt_sovits.py
touch voice_tts/serializers.py

# 3. 모델 폴더 생성
mkdir -p models/gpt-sovits-v2
mkdir -p user_voices
mkdir -p tts_cache

# 4. 마이그레이션 생성
python manage.py makemigrations voice_tts

# 5. 마이그레이션 적용
python manage.py migrate

# 6. 의존성 설치
pip install -r requirements.txt
```

---

## 🧪 테스트

### 1. Django Shell 테스트

```python
python manage.py shell

from django.contrib.auth.models import User
from voice_tts.models import UserVoice, TTSCache
from voice_tts.services.gpt_sovits import GPTSoVITSService

# 사용자 생성
user = User.objects.create_user('testuser', password='testpass123')

# TTS 서비스 테스트
tts = GPTSoVITSService()
print(f"TTS Ready: {tts.is_ready()}")
```

### 2. API 테스트 (cURL)

```bash
# 1. 사용자 로그인 (토큰 획득)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# 2. 음성 샘플 업로드
curl -X POST http://localhost:8000/api/tts/upload-voice/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "voice_file=@user_voice_sample.wav"

# 3. TTS 생성
curl -X POST http://localhost:8000/api/tts/generate/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "약 드실 시간입니다", "use_cache": true}'

# 4. Health Check
curl http://localhost:8000/api/tts/health/
```

### 3. Python 클라이언트 테스트

```python
import requests

# 설정
API_URL = "http://localhost:8000"
TOKEN = "your_auth_token"

headers = {
    "Authorization": f"Token {TOKEN}"
}

# TTS 생성
response = requests.post(
    f"{API_URL}/api/tts/generate/",
    headers=headers,
    json={
        "text": "약 드실 시간입니다",
        "use_cache": True
    }
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Audio URL: {result['audio_url']}")
print(f"Cache Hit: {result['cache_hit']}")
```

---

## 🚀 라즈베리파이 통합

### 기존 `voice_assistant_prototype.py` 수정

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Django API 설정
DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'http://localhost:8000')
DJANGO_API_TOKEN = os.getenv('DJANGO_API_TOKEN')

def text_to_speech_django(text):
    """Django TTS API 사용"""
    print("[TTS] Using Django GPT-SoVITS API...")

    try:
        response = requests.post(
            f"{DJANGO_API_URL}/api/tts/generate/",
            headers={
                "Authorization": f"Token {DJANGO_API_TOKEN}"
            },
            json={
                "text": text,
                "use_cache": True
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            if result['success']:
                # 오디오 다운로드
                audio_url = DJANGO_API_URL + result['audio_url']
                audio_response = requests.get(audio_url)

                # 로컬에 저장
                audio_file = "django_tts_output.wav"
                with open(audio_file, 'wb') as f:
                    f.write(audio_response.content)

                print(f"[TTS] Generated in {result['processing_time_ms']}ms")
                print(f"[TTS] Cache hit: {result['cache_hit']}")

                return audio_file

        print(f"[TTS ERROR] {response.status_code}")
        return None

    except Exception as e:
        print(f"[TTS ERROR] {e}")
        return None

# 기존 text_to_speech 함수 수정
def text_to_speech(text):
    """TTS with Django API + Naver fallback"""

    # Django API 시도
    audio_file = text_to_speech_django(text)

    if audio_file:
        # 재생
        import subprocess
        subprocess.run(["start", audio_file], shell=True)
        return True
    else:
        # Fallback to Naver TTS
        print("[TTS] Falling back to Naver TTS...")
        return naver_tts_fallback(text)
```

---

## 🎯 장점 정리

| 특징 | Django 통합 | FastAPI 별도 |
|------|------------|-------------|
| **기존 코드 재사용** | ✅ User 모델, Admin | ❌ 새로 구축 |
| **데이터베이스 통합** | ✅ 동일 DB | ❌ 별도 DB |
| **인증 시스템** | ✅ 기존 사용 | ❌ 별도 구축 |
| **배포** | ✅ 하나로 통합 | ❌ 2개 서버 |
| **관리 편의성** | ✅ Admin 통합 | ❌ 별도 관리 |
| **학습 곡선** | ✅ Django 익숙 | ⚠️ FastAPI 새로 배움 |

---

## 📅 타임라인

| 단계 | 작업 | 예상 시간 |
|------|------|----------|
| **Day 1** | Django 앱 생성 및 모델 정의 | 2시간 |
| | Views, Serializers 작성 | 2시간 |
| **Day 2** | GPT-SoVITS 서비스 통합 | 3시간 |
| | 테스트 및 디버깅 | 2시간 |
| **Day 3** | 라즈베리파이 클라이언트 통합 | 2시간 |
| | 전체 파이프라인 테스트 | 2시간 |

**총 예상 시간**: 2-3일

---

**Status**: Ready to implement
**Framework**: Django 5.2.7 + DRF
**Advantages**: Integrated, Easy to manage, Uses existing infrastructure
