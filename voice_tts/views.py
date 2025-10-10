"""
Voice TTS Views
TTS API 엔드포인트 및 웹 페이지
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import base64
import os
from pathlib import Path
import logging

from .models import UserVoice, TTSCache
from .serializers import (
    UserVoiceSerializer,
    TTSGenerateSerializer,
    TTSResponseSerializer,
    UserVoiceUploadSerializer
)
from .services.gpt_sovits import GPTSoVITSService

logger = logging.getLogger(__name__)


class TTSGenerateView(APIView):
    """
    TTS 생성 API

    POST /api/tts/generate/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        TTS 생성 요청

        Request Body:
            {
                "text": "약 드실 시간입니다",
                "use_cache": true,
                "return_base64": false
            }

        Response:
            {
                "success": true,
                "audio_url": "/media/tts_cache/xxx.wav",
                "audio_base64": null,
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
        return_base64 = serializer.validated_data.get('return_base64', False)
        user = request.user

        # 1. 캐시 확인
        if use_cache:
            text_hash = TTSCache.generate_hash(text)
            cached = TTSCache.objects.filter(
                user=user,
                text_hash=text_hash
            ).first()

            if cached:
                logger.info(f"Cache hit for user {user.username}: '{text[:30]}...'")
                cached.increment_access()

                # Base64 인코딩 (요청 시)
                audio_base64 = None
                if return_base64:
                    try:
                        with open(cached.audio_file.path, 'rb') as f:
                            audio_base64 = base64.b64encode(f.read()).decode('utf-8')
                    except Exception as e:
                        logger.error(f"Base64 encoding failed: {e}")

                return Response({
                    'success': True,
                    'audio_url': cached.audio_file.url,
                    'audio_base64': audio_base64,
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
                'message': '사용자 음성 샘플이 없습니다. 먼저 /api/tts/upload-voice/로 음성을 업로드해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. TTS 서비스 확인
        tts_service = GPTSoVITSService()

        if not tts_service.is_ready():
            return Response({
                'success': False,
                'message': 'TTS 서비스가 준비되지 않았습니다.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 4. TTS 생성
        output_dir = Path(settings.MEDIA_ROOT) / 'tts_cache'
        output_dir.mkdir(exist_ok=True, parents=True)

        text_hash = TTSCache.generate_hash(text)
        output_filename = f"{user.id}_{text_hash}.wav"
        output_path = output_dir / output_filename

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

        # 5. 캐시 저장
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

        # 6. Base64 인코딩 (요청 시)
        audio_base64 = None
        if return_base64:
            try:
                with open(output_path, 'rb') as f:
                    audio_base64 = base64.b64encode(f.read()).decode('utf-8')
            except Exception as e:
                logger.error(f"Base64 encoding failed: {e}")

        return Response({
            'success': True,
            'audio_url': cache_entry.audio_file.url,
            'audio_base64': audio_base64,
            'cache_hit': False,
            'processing_time_ms': result['processing_time_ms'],
            'text_length': len(text)
        })


class UserVoiceUploadView(APIView):
    """
    사용자 음성 샘플 업로드 API

    POST /api/tts/upload-voice/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        사용자 음성 샘플 업로드

        Request (multipart/form-data):
            voice_file: <file> (WAV, MP3)

        Response:
            {
                "success": true,
                "message": "음성 샘플이 업로드되었습니다",
                "voice_id": 1
            }
        """

        serializer = UserVoiceUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        voice_file = serializer.validated_data['voice_file']
        user = request.user

        # 기존 음성 샘플 삭제 (UNIQUE constraint 회피)
        UserVoice.objects.filter(user=user).delete()

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
    """
    TTS 서비스 상태 확인

    GET /api/tts/health/
    """

    permission_classes = []  # 인증 불필요

    def get(self, request):
        """
        TTS 서비스 상태 확인

        Response:
            {
                "status": "healthy",
                "model_loaded": true,
                "device": "cpu"
            }
        """

        try:
            tts_service = GPTSoVITSService()
            is_ready = tts_service.is_ready()

            return Response({
                'status': 'healthy' if is_ready else 'unavailable',
                'service': tts_service.check_health(),
                'timestamp': __import__('datetime').datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 웹 페이지 뷰
# ============================================================================

def upload_voice_page(request):
    """
    음성 샘플 업로드 웹 페이지

    GET: 업로드 페이지 표시
    POST: 파일 업로드 처리
    """
    # 로그인하지 않은 사용자는 voice_user로 자동 로그인
    if not request.user.is_authenticated:
        from django.contrib.auth.models import User
        try:
            voice_user = User.objects.get(username='voice_user')
            from django.contrib.auth import login
            login(request, voice_user, backend='django.contrib.auth.backends.ModelBackend')
        except User.DoesNotExist:
            pass

    # 현재 사용자의 음성 샘플 가져오기
    current_voice = None
    if request.user.is_authenticated:
        try:
            current_voice = UserVoice.objects.filter(
                user=request.user,
                is_active=True
            ).first()
        except UserVoice.DoesNotExist:
            pass

    # POST 요청 처리 (파일 업로드)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': '로그인이 필요합니다.'
            }, status=401)

        voice_file = request.FILES.get('voice_file')
        if not voice_file:
            return JsonResponse({
                'success': False,
                'error': '파일이 선택되지 않았습니다.'
            }, status=400)

        # 파일 확장자 검증
        ext = os.path.splitext(voice_file.name)[1].lower()
        if ext not in ['.wav', '.mp3', '.m4a', '.flac']:
            return JsonResponse({
                'success': False,
                'error': '지원하지 않는 파일 형식입니다. WAV, MP3, M4A, FLAC만 가능합니다.'
            }, status=400)

        # 파일 크기 검증 (10MB)
        if voice_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': '파일 크기가 너무 큽니다. 10MB 이하로 업로드하세요.'
            }, status=400)

        try:
            # 기존 음성 샘플 삭제 (UNIQUE constraint 회피)
            UserVoice.objects.filter(user=request.user).delete()

            # 새 음성 샘플 저장
            user_voice = UserVoice.objects.create(
                user=request.user,
                voice_file=voice_file,
                is_active=True
            )

            logger.info(f"Voice sample uploaded for user {request.user.username} via web interface")

            return JsonResponse({
                'success': True,
                'message': '음성 샘플이 성공적으로 업로드되었습니다.',
                'voice_id': user_voice.id
            })

        except Exception as e:
            logger.error(f"Voice upload failed: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    # GET 요청 - 페이지 렌더링
    return render(request, 'voice_tts/upload_voice.html', {
        'current_voice': current_voice,
        'user': request.user
    })
