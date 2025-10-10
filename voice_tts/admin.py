"""
Voice TTS Admin
Django Admin 인터페이스
"""
from django.contrib import admin
from .models import UserVoice, TTSCache


@admin.register(UserVoice)
class UserVoiceAdmin(admin.ModelAdmin):
    """사용자 음성 샘플 관리"""

    list_display = ['user', 'duration_seconds', 'is_active', 'uploaded_at']
    list_filter = ['is_active', 'uploaded_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['uploaded_at', 'updated_at']
    list_per_page = 20

    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'voice_file', 'is_active')
        }),
        ('메타데이터', {
            'fields': ('duration_seconds', 'uploaded_at', 'updated_at')
        }),
    )


@admin.register(TTSCache)
class TTSCacheAdmin(admin.ModelAdmin):
    """TTS 캐시 관리"""

    list_display = ['user', 'text_preview', 'access_count', 'created_at', 'accessed_at']
    list_filter = ['created_at', 'accessed_at']
    search_fields = ['user__username', 'text']
    readonly_fields = ['text_hash', 'created_at', 'accessed_at', 'access_count']
    list_per_page = 50

    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'text', 'text_hash')
        }),
        ('음성 파일', {
            'fields': ('audio_file', 'duration_seconds')
        }),
        ('사용 통계', {
            'fields': ('access_count', 'created_at', 'accessed_at')
        }),
    )

    def text_preview(self, obj):
        """텍스트 미리보기"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = '텍스트'

    actions = ['clear_old_cache']

    def clear_old_cache(self, request, queryset):
        """오래된 캐시 삭제"""
        from datetime import timedelta
        from django.utils import timezone

        cutoff_date = timezone.now() - timedelta(days=30)
        old_caches = queryset.filter(accessed_at__lt=cutoff_date)
        count = old_caches.count()
        old_caches.delete()

        self.message_user(request, f"{count}개의 오래된 캐시가 삭제되었습니다.")
    clear_old_cache.short_description = "30일 이상 미사용 캐시 삭제"
