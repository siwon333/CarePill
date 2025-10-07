from django.db import models

class OCRImage(models.Model):
    """OCR 처리용 이미지"""
    image = models.ImageField(upload_to='ocr_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ocr_result = models.TextField(blank=True, null=True)
    extracted_medicine_names = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"OCR Image {self.id} - {self.uploaded_at}"