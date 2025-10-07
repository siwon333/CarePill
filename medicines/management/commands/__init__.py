# medicines/management/commands/import_medicines.py

from django.core.management.base import BaseCommand
import pandas as pd
import re
from medicines.models import Medicine, PillIdentification, AccessibilityInfo

class Command(BaseCommand):
    help = 'CSV 파일에서 의약품 데이터 임포트'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📥 데이터 임포트 시작...\n'))
        
        try:
            # 1. 의약품 기본 정보
            self.import_medicines()
            
            # 2. 낱알 정보
            self.import_pills()
            
            # 3. 접근성 정보
            self.import_accessibility()
            
            self.stdout.write(self.style.SUCCESS('\n✅ 모든 임포트 완료!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ 에러 발생: {str(e)}'))
            raise

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

    def optimize_for_tts(self, text):
        """TTS 최적화"""
        if not text:
            return None
        text = str(text)
        text = text.replace('투여', '복용')
        text = text.replace('경구투여', '먹는 약')
        text = re.sub(r'(\d+)mg', r'\1밀리그램', text)
        text = re.sub(r'(\d+)mL', r'\1밀리리터', text)
        return text

    def import_medicines(self):
        """의약품 정보 임포트"""
        self.stdout.write('  📋 의약품 정보 로딩...')
        
        # 파일 읽기
        try:
            df1 = pd.read_csv('의약품개요정보 조회_20251004.csv', encoding='cp949')
        except:
            df1 = pd.read_csv('의약품개요정보 조회_20251004.csv', encoding='euc-kr')
        
        try:
            df3 = pd.read_csv('의약품 제품 허가 목록_20251004.csv', encoding='cp949')
        except:
            df3 = pd.read_csv('의약품 제품 허가 목록_20251004.csv', encoding='euc-kr')
        
        count = 0
        errors = 0
        
        for idx, row1 in df1.iterrows():
            try:
                item_seq = self.extract_column(pd.DataFrame([row1]), 'ITEMSEQ').iloc[0]
                
                if pd.isna(item_seq):
                    continue
                
                # 허가정보에서 매칭
                row3_data = df3[self.extract_column(df3, 'ITEM_SEQ') == item_seq]
                
                # 기본 정보 추출
                item_name = self.clean_text(self.extract_column(pd.DataFrame([row1]), 'ITEMNAME').iloc[0])
                entp_name = self.clean_text(self.extract_column(pd.DataFrame([row1]), 'ENTPNAME').iloc[0])
                
                defaults = {
                    'item_name': item_name,
                    'entp_name': entp_name,
                    'effect': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'EFCYQESITM').iloc[0]),
                    'usage': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'USEMETHODQESITM').iloc[0]),
                    'warning_critical': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'ATPNWARNQESITM').iloc[0]),
                    'warning_general': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'ATPNQESITM').iloc[0]),
                    'interaction': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'INTRCQESITM').iloc[0]),
                    'side_effect': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'SEQESITM').iloc[0]),
                    'storage': self.clean_text(self.extract_column(pd.DataFrame([row1]), 'DEPOSITMETHODQESITM').iloc[0]),
                }
                
                # 허가정보 추가
                if not row3_data.empty:
                    defaults['item_name_eng'] = self.clean_text(self.extract_column(row3_data, 'ITEM_ENG_NAME').iloc[0])
                    defaults['entp_name_eng'] = self.clean_text(self.extract_column(row3_data, 'ENTP_ENG_NAME').iloc[0])
                    defaults['main_ingredient'] = self.clean_text(self.extract_column(row3_data, 'ITEM_INGR_NAME').iloc[0])
                    
                    ingr_cnt = self.extract_column(row3_data, 'ITEM_INGR_CNT').iloc[0]
                    defaults['ingredient_count'] = int(ingr_cnt) if pd.notna(ingr_cnt) else None
                    
                    defaults['class_type'] = self.clean_text(self.extract_column(row3_data, 'SPCLTY_PBLC').iloc[0])
                    defaults['product_type'] = self.clean_text(self.extract_column(row3_data, 'PRDUCT_TYPE').iloc[0])
                    defaults['edi_code'] = self.clean_text(self.extract_column(row3_data, 'EDI_CODE').iloc[0])
                
                Medicine.objects.update_or_create(
                    item_seq=int(item_seq),
                    defaults=defaults
                )
                count += 1
                
                if count % 500 == 0:
                    self.stdout.write(f'    ... {count}개 처리 중')
                    
            except Exception as e:
                errors += 1
                if errors < 10:  # 처음 10개만 출력
                    self.stdout.write(self.style.WARNING(f'    경고: row {idx} 스킵 - {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {count}개 의약품 임포트 완료 (에러: {errors}개)'))

    def import_pills(self):
        """낱알 정보 임포트"""
        self.stdout.write('  💊 낱알 정보 로딩...')
        
        try:
            df = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='utf-8')
        except:
            try:
                df = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='cp949')
            except:
                df = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='euc-kr')
        
        count = 0
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                item_seq = row.get('ITEM_SEQ')
                if pd.isna(item_seq):
                    continue
                
                medicine = Medicine.objects.get(item_seq=int(item_seq))
                
                # 숫자형 필드 처리
                length_long = row.get('LENG_LONG')
                length_short = row.get('LENG_SHORT')
                thickness = row.get('THICK')
                shape_code = row.get('SHAPE_CODE')
                
                PillIdentification.objects.update_or_create(
                    medicine=medicine,
                    defaults={
                        'image_url': row.get('ITEM_IMAGE') if pd.notna(row.get('ITEM_IMAGE')) else None,
                        'shape': row.get('DRUG_SHAPE') if pd.notna(row.get('DRUG_SHAPE')) else None,
                        'color_front': row.get('COLOR_CLASS1') if pd.notna(row.get('COLOR_CLASS1')) else None,
                        'color_back': row.get('COLOR_CLASS2') if pd.notna(row.get('COLOR_CLASS2')) else None,
                        'print_front': row.get('PRINT_FRONT') if pd.notna(row.get('PRINT_FRONT')) else None,
                        'print_back': row.get('PRINT_BACK') if pd.notna(row.get('PRINT_BACK')) else None,
                        'length_long': float(length_long) if pd.notna(length_long) else None,
                        'length_short': float(length_short) if pd.notna(length_short) else None,
                        'thickness': float(thickness) if pd.notna(thickness) else None,
                        'line_front': row.get('LINE_FRONT') if pd.notna(row.get('LINE_FRONT')) else None,
                        'line_back': row.get('LINE_BACK') if pd.notna(row.get('LINE_BACK')) else None,
                        'shape_code': int(shape_code) if pd.notna(shape_code) else None,
                    }
                )
                count += 1
                
            except Medicine.DoesNotExist:
                errors += 1
            except Exception as e:
                errors += 1
                if errors < 10:
                    self.stdout.write(self.style.WARNING(f'    경고: row {idx} 스킵 - {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {count}개 낱알 정보 임포트 완료 (에러: {errors}개)'))

    def import_accessibility(self):
        """접근성 정보 임포트"""
        self.stdout.write('  🎤 접근성 정보 로딩...')
        
        try:
            df = pd.read_csv('장애인 의약품 안전사용 정보음성·수어영상_20251004.csv', encoding='cp949')
        except:
            df = pd.read_csv('장애인 의약품 안전사용 정보음성·수어영상_20251004.csv', encoding='euc-kr')
        
        count = 0
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                item_seq = self.extract_column(pd.DataFrame([row]), 'ITEM_SEQ').iloc[0]
                
                if pd.isna(item_seq):
                    continue
                
                medicine = Medicine.objects.get(item_seq=int(item_seq))
                
                video_url = self.extract_column(pd.DataFrame([row]), 'MVP_FLPTH').iloc[0]
                std_code = self.extract_column(pd.DataFrame([row]), 'STD_CD').iloc[0]
                
                AccessibilityInfo.objects.update_or_create(
                    medicine=medicine,
                    defaults={
                        'video_url': video_url if pd.notna(video_url) else None,
                        'std_code': std_code if pd.notna(std_code) else None,
                        'has_audio': True,
                        'has_sign_language': True,
                        'effect_tts': self.optimize_for_tts(medicine.effect),
                        'usage_tts': self.optimize_for_tts(medicine.usage),
                        'warning_tts': self.optimize_for_tts(medicine.warning_general),
                    }
                )
                count += 1
                
            except Medicine.DoesNotExist:
                errors += 1
            except Exception as e:
                errors += 1
                if errors < 10:
                    self.stdout.write(self.style.WARNING(f'    경고: row {idx} 스킵 - {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {count}개 접근성 정보 임포트 완료 (에러: {errors}개)'))