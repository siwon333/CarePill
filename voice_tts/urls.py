"""
Voice TTS URLs
TTS API 및 웹 페이지 URL 라우팅
"""
from django.urls import path
from .views import (
    TTSGenerateView,
    UserVoiceUploadView,
    TTSHealthCheckView,
    upload_voice_page
)

app_name = 'voice_tts'

urlpatterns = [
    # 웹 페이지
    path('upload/', upload_voice_page, name='upload_page'),

    # TTS API
    path('generate/', TTSGenerateView.as_view(), name='generate'),
    path('upload-voice/', UserVoiceUploadView.as_view(), name='upload-voice'),
    path('health/', TTSHealthCheckView.as_view(), name='health'),
]
