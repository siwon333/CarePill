from django.contrib import admin
from .models import Medicine, PillIdentification, AccessibilityInfo, UserMedication

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['item_seq', 'item_name', 'entp_name', 'class_type']
    search_fields = ['item_name', 'entp_name']
    list_filter = ['class_type']

@admin.register(UserMedication)
class UserMedicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'medicine', 'dosage', 'frequency', 'prescription_date']
    list_filter = ['is_completed', 'prescription_date']
    search_fields = ['medicine__item_name', 'user__username']