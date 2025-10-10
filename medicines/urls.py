# medicines/urls.py

from django.urls import path
from . import views

app_name = 'medicines'

urlpatterns = [
    # ============================================
    # 🌐 웹 페이지 (추가됨)
    # ============================================
    path('', views.home, name='home'),  # 홈페이지
    path('scan/', views.scan_page, name='scan'),  # 약 스캔
    path('meds/', views.my_medications, name='my_medications'),  # 내 약 목록
    path('voice/', views.voice_page, name='voice'),  # 음성 인터페이스
    path('meds/delete/<int:medication_id>/', views.delete_medication, name='delete_medication'),
    
    # ============================================
    # 🔌 API 엔드포인트 (기존)
    # ============================================
    path('detail/<int:item_seq>/', views.medicine_detail_page, name='detail'),  # 상세 페이지 (HTML)
    path('stats/', views.get_stats, name='stats'),
    path('search/', views.search_medicine, name='search'),
    path('api-detail/<int:item_seq>/', views.medicine_detail, name='api_detail'),
    path('search/barcode/', views.search_by_barcode, name='search_barcode'),
    path('search/image/', views.search_by_image, name='search_image'),
    path('videos/', views.medicines_with_video, name='videos'),
]