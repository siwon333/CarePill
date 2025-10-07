from django.urls import path
from . import views

app_name = 'ocr'

urlpatterns = [
    path('', views.ocr_page, name='index'),
    path('process/', views.process_ocr, name='process'),
]