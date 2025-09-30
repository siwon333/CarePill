from django.contrib import admin
from .models import MedicineAnalysis

@admin.register(MedicineAnalysis)
class MedicineAnalysisAdmin(admin.ModelAdmin):
    list_display = ['analysis_type', 'medicine_name', 'created_at']
    list_filter = ['analysis_type', 'created_at']
    search_fields = ['medicine_name', 'analysis_result']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')