import os
import django
import pandas as pd
import re

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_project.settings')
django.setup()

from medicines.models import Medicine, PillIdentification, AccessibilityInfo

def extract_column(df, pattern):
    """대괄호 패턴으로 컬럼 찾기"""
    for col in df.columns:
        if f'[{pattern}]' in col:
            return df[col]
    return pd.Series([None] * len(df))

def clean_text(text):
    """텍스트 정제"""
    if pd.isna(text):
        return None
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text if text else None

def optimize_for_tts(text):
    """TTS 최적화"""
    if not text:
        return None
    text = str(text)
    text = text.replace('투여', '복용')
    text = text.replace('경구투여', '먹는 약')
    text = re.sub(r'(\d+)mg', r'\1밀리그램', text)
    text = re.sub(r'(\d+)mL', r'\1밀리리터', text)
    return text

print("📥 데이터 임포트 시작...\n")

# 1. 의약품 정보
print("  📋 의약품 정보 로딩...")
try:
    df1 = pd.read_csv('의약품개요정보 조회_20251004.csv', encoding='cp949')
except:
    df1 = pd.read_csv('의약품개요정보 조회_20251004.csv', encoding='euc-kr')

try:
    df3 = pd.read_csv('의약품 제품 허가 목록_20251004.csv', encoding='cp949')
except:
    df3 = pd.read_csv('의약품 제품 허가 목록_20251004.csv', encoding='euc-kr')

count = 0
for idx, row1 in df1.iterrows():
    try:
        item_seq = extract_column(pd.DataFrame([row1]), 'ITEMSEQ').iloc[0]
        
        if pd.isna(item_seq):
            continue
        
        # 허가정보에서 매칭
        row3_data = df3[extract_column(df3, 'ITEM_SEQ') == item_seq]
        
        defaults = {
            'item_name': clean_text(extract_column(pd.DataFrame([row1]), 'ITEMNAME').iloc[0]),
            'entp_name': clean_text(extract_column(pd.DataFrame([row1]), 'ENTPNAME').iloc[0]),
            'effect': clean_text(extract_column(pd.DataFrame([row1]), 'EFCYQESITM').iloc[0]),
            'usage': clean_text(extract_column(pd.DataFrame([row1]), 'USEMETHODQESITM').iloc[0]),
            'warning_critical': clean_text(extract_column(pd.DataFrame([row1]), 'ATPNWARNQESITM').iloc[0]),
            'warning_general': clean_text(extract_column(pd.DataFrame([row1]), 'ATPNQESITM').iloc[0]),
            'interaction': clean_text(extract_column(pd.DataFrame([row1]), 'INTRCQESITM').iloc[0]),
            'side_effect': clean_text(extract_column(pd.DataFrame([row1]), 'SEQESITM').iloc[0]),
            'storage': clean_text(extract_column(pd.DataFrame([row1]), 'DEPOSITMETHODQESITM').iloc[0]),
        }
        
        if not row3_data.empty:
            defaults['item_name_eng'] = clean_text(extract_column(row3_data, 'ITEM_ENG_NAME').iloc[0])
            defaults['main_ingredient'] = clean_text(extract_column(row3_data, 'ITEM_INGR_NAME').iloc[0])
            defaults['class_type'] = clean_text(extract_column(row3_data, 'SPCLTY_PBLC').iloc[0])
        
        Medicine.objects.update_or_create(
            item_seq=int(item_seq),
            defaults=defaults
        )
        count += 1
        
        if count % 500 == 0:
            print(f"    ... {count}개 처리 중")
            
    except Exception as e:
        continue

print(f"    ✓ {count}개 의약품 임포트 완료\n")

# 2. 낱알 정보
print("  💊 낱알 정보 로딩...")
try:
    df2 = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='utf-8')
except:
    try:
        df2 = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='cp949')
    except:
        df2 = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='euc-kr')

count = 0
for idx, row in df2.iterrows():
    try:
        item_seq = row.get('ITEM_SEQ')
        if pd.isna(item_seq):
            continue
        
        medicine = Medicine.objects.get(item_seq=int(item_seq))
        
        PillIdentification.objects.update_or_create(
            medicine=medicine,
            defaults={
                'image_url': row.get('ITEM_IMAGE') if pd.notna(row.get('ITEM_IMAGE')) else None,
                'shape': row.get('DRUG_SHAPE') if pd.notna(row.get('DRUG_SHAPE')) else None,
                'color_front': row.get('COLOR_CLASS1') if pd.notna(row.get('COLOR_CLASS1')) else None,
                'print_front': row.get('PRINT_FRONT') if pd.notna(row.get('PRINT_FRONT')) else None,
            }
        )
        count += 1
    except Medicine.DoesNotExist:
        continue
    except Exception as e:
        continue

print(f"    ✓ {count}개 낱알 정보 임포트 완료\n")

# 3. 접근성 정보
print("  🎤 접근성 정보 로딩...")
try:
    df4 = pd.read_csv('장애인 의약품 안전사용 정보음성·수어영상_20251004.csv', encoding='cp949')
except:
    df4 = pd.read_csv('장애인 의약품 안전사용 정보음성·수어영상_20251004.csv', encoding='euc-kr')

count = 0
for idx, row in df4.iterrows():
    try:
        item_seq = extract_column(pd.DataFrame([row]), 'ITEM_SEQ').iloc[0]
        
        if pd.isna(item_seq):
            continue
        
        medicine = Medicine.objects.get(item_seq=int(item_seq))
        
        AccessibilityInfo.objects.update_or_create(
            medicine=medicine,
            defaults={
                'video_url': extract_column(pd.DataFrame([row]), 'MVP_FLPTH').iloc[0],
                'std_code': extract_column(pd.DataFrame([row]), 'STD_CD').iloc[0],
                'has_audio': True,
                'has_sign_language': True,
                'effect_tts': optimize_for_tts(medicine.effect),
                'usage_tts': optimize_for_tts(medicine.usage),
                'warning_tts': optimize_for_tts(medicine.warning_general),
            }
        )
        count += 1
    except Medicine.DoesNotExist:
        continue
    except Exception as e:
        continue

print(f"    ✓ {count}개 접근성 정보 임포트 완료\n")

print("✅ 모든 임포트 완료!")
print(f"\n총 의약품: {Medicine.objects.count()}개")
print(f"낱알 정보: {PillIdentification.objects.count()}개")
print(f"접근성 정보: {AccessibilityInfo.objects.count()}개")