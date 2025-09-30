from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_and_analyze, name='upload_and_analyze'),
    path('analysis/<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    path('history/', views.analysis_history, name='analysis_history'),
]