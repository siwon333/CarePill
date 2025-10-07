from django.urls import path
from . import views

app_name = 'medicines'

urlpatterns = [
    path('', views.index, name='index'),  # 메인 페이지
    path('detail/<int:item_seq>/', views.medicine_detail_page, name='detail'),  # 상세 페이지
    
    # API 엔드포인트 (api/ prefix 제거!)
    path('stats/', views.get_stats, name='stats'),
    path('search/', views.search_medicine, name='search'),
    path('api-detail/<int:item_seq>/', views.medicine_detail, name='api_detail'),
    path('search/barcode/', views.search_by_barcode, name='search_barcode'),
    path('search/image/', views.search_by_image, name='search_image'),
    path('videos/', views.medicines_with_video, name='videos'),
]