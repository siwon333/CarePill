from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/medicines/', include('medicines.urls')),
    path('ocr/', include('ocr.urls')),  # 👈 추가
]

# 미디어 파일 서빙 (개발 환경)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)