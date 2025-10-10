"""
Voice TTS Serializers
API 요청/응답 데이터 직렬화
"""
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
    return_base64 = serializers.BooleanField(
        default=False,
        help_text='Base64 인코딩 반환 여부'
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


class UserVoiceUploadSerializer(serializers.Serializer):
    """사용자 음성 업로드 Serializer"""

    voice_file = serializers.FileField(
        help_text='음성 샘플 파일 (WAV, MP3)'
    )
