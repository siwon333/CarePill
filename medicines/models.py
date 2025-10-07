# models.py - 장고 모델 정의

from django.db import models

class Medicine(models.Model):
    """의약품 기본 정보"""
    item_seq = models.BigIntegerField(primary_key=True, verbose_name='품목기준코드')
    item_name = models.CharField(max_length=500, verbose_name='제품명', db_index=True)
    item_name_eng = models.CharField(max_length=500, blank=True, null=True, verbose_name='영문명')
    entp_name = models.CharField(max_length=300, verbose_name='제조사', db_index=True)
    
    # 핵심 정보
    effect = models.TextField(blank=True, null=True, verbose_name='효능/효과')
    usage = models.TextField(blank=True, null=True, verbose_name='사용방법')
    warning_critical = models.TextField(blank=True, null=True, verbose_name='주의사항 경고')
    warning_general = models.TextField(blank=True, null=True, verbose_name='일반 주의사항')
    interaction = models.TextField(blank=True, null=True, verbose_name='상호작용')
    side_effect = models.TextField(blank=True, null=True, verbose_name='부작용')
    storage = models.TextField(blank=True, null=True, verbose_name='보관방법')
    
    # 추가 정보
    main_ingredient = models.TextField(blank=True, null=True, verbose_name='주성분')
    ingredient_count = models.IntegerField(blank=True, null=True, verbose_name='주성분 개수')
    class_type = models.CharField(max_length=100, blank=True, null=True, verbose_name='전문/일반')
    product_type = models.CharField(max_length=100, blank=True, null=True, verbose_name='분류')
    edi_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='보험코드')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medicines'
        verbose_name = '의약품'
        verbose_name_plural = '의약품 목록'
        
    def __str__(self):
        return f"{self.item_name} ({self.entp_name})"


class PillIdentification(models.Model):
    """낱알 식별 정보"""
    medicine = models.OneToOneField(Medicine, on_delete=models.CASCADE, 
                                    primary_key=True, related_name='pill_info')
    
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='이미지 URL')
    shape = models.CharField(max_length=100, blank=True, null=True, verbose_name='모양')
    color_front = models.CharField(max_length=100, blank=True, null=True, verbose_name='앞면 색상')
    color_back = models.CharField(max_length=100, blank=True, null=True, verbose_name='뒷면 색상')
    print_front = models.CharField(max_length=200, blank=True, null=True, verbose_name='앞면 각인')
    print_back = models.CharField(max_length=200, blank=True, null=True, verbose_name='뒷면 각인')
    
    length_long = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, verbose_name='장축')
    length_short = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, verbose_name='단축')
    thickness = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, verbose_name='두께')
    
    line_front = models.CharField(max_length=100, blank=True, null=True, verbose_name='앞면 선')
    line_back = models.CharField(max_length=100, blank=True, null=True, verbose_name='뒷면 선')
    shape_code = models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'pill_identification'
        verbose_name = '낱알 정보'
        
    def __str__(self):
        return f"{self.medicine.item_name} 낱알정보"


class AccessibilityInfo(models.Model):
    """장애인 접근성 정보"""
    medicine = models.OneToOneField(Medicine, on_delete=models.CASCADE, 
                                    primary_key=True, related_name='accessibility')
    
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='음성/수어 영상')
    has_audio = models.BooleanField(default=False, verbose_name='음성 가이드')
    has_sign_language = models.BooleanField(default=False, verbose_name='수어 영상')
    
    # TTS 최적화 텍스트
    effect_tts = models.TextField(blank=True, null=True, verbose_name='효능(TTS)')
    usage_tts = models.TextField(blank=True, null=True, verbose_name='사용법(TTS)')
    warning_tts = models.TextField(blank=True, null=True, verbose_name='주의사항(TTS)')
    
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name='바코드')
    std_code = models.CharField(max_length=100, blank=True, null=True, verbose_name='표준코드')
    
    class Meta:
        db_table = 'accessibility_info'
        verbose_name = '접근성 정보'
        
    def __str__(self):
        return f"{self.medicine.item_name} 접근성정보"


# ===== CSV 데이터 임포트 스크립트 =====
# management/commands/import_medicines.py

from django.core.management.base import BaseCommand
import pandas as pd
import re
from medicines.models import Medicine, PillIdentification, AccessibilityInfo

class Command(BaseCommand):
    help = 'CSV 파일에서 의약품 데이터 임포트'

    def handle(self, *args, **options):
        self.stdout.write('📥 데이터 임포트 시작...\n')
        
        # 1. 의약품 기본 정보
        self.import_medicines()
        
        # 2. 낱알 정보
        self.import_pills()
        
        # 3. 접근성 정보
        self.import_accessibility()
        
        self.stdout.write(self.style.SUCCESS('✅ 임포트 완료!'))

    def extract_column(self, df, pattern):
        """대괄호 패턴으로 컬럼 찾기"""
        for col in df.columns:
            if f'[{pattern}]' in col:
                return df[col]
        return pd.Series([None] * len(df))

    def clean_text(self, text):
        """텍스트 정제"""
        if pd.isna(text):
            return None
        text = str(text).strip()
        text = re.sub(r'\s+', ' ', text)
        return text if text else None

    def import_medicines(self):
        """의약품 정보 임포트"""
        self.stdout.write('  - 의약품 정보 로딩...')
        
        # 개요정보
        df1 = pd.read_csv('의약품개요정보 조회_20251004.csv', encoding='cp949')
        # 허가정보
        df3 = pd.read_csv('의약품 제품 허가 목록_20251004.csv', encoding='cp949')
        
        count = 0
        for _, row1 in df1.iterrows():
            item_seq = self.extract_column(pd.DataFrame([row1]), 'ITEMSEQ').iloc[0]
            
            # 허가정보에서 매칭
            row3 = df3[self.extract_column(df3, 'ITEM_SEQ') == item_seq]
            
            Medicine.objects.update_or_create(
                item_seq=item_seq,
                defaults={
                    'item_name': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'ITEMNAME').iloc[0]),
                    'item_name_eng': self.clean_text(self.extract_column(row3, 'ITEM_ENG_NAME').iloc[0]) if not row3.empty else None,
                    'entp_name': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'ENTPNAME').iloc[0]),
                    'effect': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'EFCYQESITM').iloc[0]),
                    'usage': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'USEMETHODQESITM').iloc[0]),
                    'warning_critical': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'ATPNWARNQESITM').iloc[0]),
                    'warning_general': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'ATPNQESITM').iloc[0]),
                    'interaction': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'INTRCQESITM').iloc[0]),
                    'side_effect': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'SEQESITM').iloc[0]),
                    'storage': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'DEPOSITMETHODQESITM').iloc[0]),
                    'main_ingredient': self.clean_text(self.extract_column(row3, 'ITEM_INGR_NAME').iloc[0]) if not row3.empty else None,
                    'class_type': self.clean_text(self.extract_column(row3, 'SPCLTY_PBLC').iloc[0]) if not row3.empty else None,
                }
            )
            count += 1
            
        self.stdout.write(f'    ✓ {count}개 의약품 임포트')

    def import_pills(self):
        """낱알 정보 임포트"""
        self.stdout.write('  - 낱알 정보 로딩...')
        
        df = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='utf-8')
        
        count = 0
        for _, row in df.iterrows():
            try:
                medicine = Medicine.objects.get(item_seq=row['ITEM_SEQ'])
                PillIdentification.objects.update_or_create(
                    medicine=medicine,
                    defaults={
                        'image_url': row.get('ITEM_IMAGE'),
                        'shape': row.get('DRUG_SHAPE'),
                        'color_front': row.get('COLOR_CLASS1'),
                        'color_back': row.get('COLOR_CLASS2'),
                        'print_front': row.get('PRINT_FRONT'),
                        'print_back': row.get('PRINT_BACK'),
                        'length_long': row.get('LENG_LONG'),
                        'length_short': row.get('LENG_SHORT'),
                        'thickness': row.get('THICK'),
                        'line_front': row.get('LINE_FRONT'),
                        'line_back': row.get('LINE_BACK'),
                        'shape_code': row.get('SHAPE_CODE'),
                    }
                )
                count += 1
            except Medicine.DoesNotExist:
                continue
                
        self.stdout.write(f'    ✓ {count}개 낱알 정보 임포트')

    def import_accessibility(self):
        """접근성 정보 임포트"""
        self.stdout.write('  - 접근성 정보 로딩...')
        
        df = pd.read_csv('장애인 의약품 안전사용 정보음성·수어영상_20251004.csv', encoding='cp949')
        
        count = 0
        for _, row in df.iterrows():
            item_seq = self.extract_column(pd.DataFrame([row]), 'ITEM_SEQ').iloc[0]
            try:
                medicine = Medicine.objects.get(item_seq=item_seq)
                AccessibilityInfo.objects.update_or_create(
                    medicine=medicine,
                    defaults={
                        'video_url': self.extract_column(pd.DataFrame([row]), 'MVP_FLPTH').iloc[0],
                        'std_code': self.extract_column(pd.DataFrame([row]), 'STD_CD').iloc[0],
                        'has_audio': True,
                        'has_sign_language': True,
                        'effect_tts': self.optimize_for_tts(medicine.effect),
                        'usage_tts': self.optimize_for_tts(medicine.usage),
                        'warning_tts': self.optimize_for_tts(medicine.warning_general),
                    }
                )
                count += 1
            except Medicine.DoesNotExist:
                continue
                
        self.stdout.write(f'    ✓ {count}개 접근성 정보 임포트')

    def optimize_for_tts(self, text):
        """TTS 최적화"""
        if not text:
            return None
        text = text.replace('투여', '복용')
        text = re.sub(r'(\d+)mg', r'\1밀리그램', text)
        text = re.sub(r'(\d+)mL', r'\1밀리리터', text)
        return text
    
from django.contrib.auth.models import User

class UserMedication(models.Model):
    """사용자 복용약 정보"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medications')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    
    # 처방 정보
    dosage = models.CharField(max_length=100, blank=True, null=True, verbose_name='투약량')
    frequency = models.CharField(max_length=100, blank=True, null=True, verbose_name='복용횟수')
    days = models.CharField(max_length=50, blank=True, null=True, verbose_name='복용기간')
    
    # 추가 정보
    prescription_date = models.DateField(blank=True, null=True, verbose_name='조제일자')
    start_date = models.DateField(auto_now_add=True, verbose_name='등록일')
    pharmacy_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='약국명')
    hospital_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='병원명')
    
    # 복용 완료 여부
    is_completed = models.BooleanField(default=False, verbose_name='복용완료')
    
    class Meta:
        db_table = 'user_medications'
        ordering = ['-start_date']
        verbose_name = '사용자 복용약'
        verbose_name_plural = '사용자 복용약 목록'
    
    def __str__(self):
        return f"{self.user.username} - {self.medicine.item_name}"