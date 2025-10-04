from django.db import models
from django.utils import timezone

class MedicineAnalysis(models.Model):
    ANALYSIS_TYPES = [
        ('envelope', '약봉투 글씨 인식'),
        ('schedule', '복용시간 인식'),
        ('appearance', '약 외관 식별'),
    ]
    
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    image = models.ImageField(upload_to='medicine_images/')
    analysis_result = models.TextField(blank=True)
    medicine_name = models.CharField(max_length=200, blank=True)
    dosage_schedule = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "약물 분석"
        verbose_name_plural = "약물 분석들"
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"