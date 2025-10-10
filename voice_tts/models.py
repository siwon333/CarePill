"""
Voice TTS Models
사용자 음성 샘플 및 TTS 캐시 관리
"""
from django.db import models
from django.contrib.auth.models import User
import hashlib


class UserVoice(models.Model):
    """사용자 음성 샘플 모델"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='voice_sample',
        verbose_name='사용자'
    )
    voice_file = models.FileField(
        upload_to='user_voices/',
        help_text='5-10초 음성 샘플 (WAV 권장)'
    )
    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text='음성 샘플 길이(초)'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True,
        help_text='활성 상태'
    )

    class Meta:
        verbose_name = '사용자 음성'
        verbose_name_plural = '사용자 음성 샘플'
        db_table = 'voice_user_voice'

    def __str__(self):
        return f"{self.user.username}의 음성 샘플"


class TTSCache(models.Model):
    """TTS 캐시 모델 (자주 쓰는 문장 저장)"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tts_caches',
        verbose_name='사용자'
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
        blank=True,
        help_text='음성 길이(초)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accessed_at = models.DateTimeField(auto_now=True)
    access_count = models.IntegerField(
        default=0,
        help_text='접근 횟수'
    )

    class Meta:
        verbose_name = 'TTS 캐시'
        verbose_name_plural = 'TTS 캐시'
        db_table = 'voice_tts_cache'
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
