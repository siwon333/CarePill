import os
import django
import pandas as pd
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_project.settings')
django.setup()

from medicines.models import Medicine, PillIdentification, AccessibilityInfo

def extract_column(df, pattern):
    """공백 무시하고 컬럼 찾기"""
    for col in df.columns:
        # 공백 제거 후 비교
        col_clean = col.strip()
        if f'[{pattern}]' in col_clean:
            return df[col]  # 원본 컬럼명 사용
    return pd.Series([None] * len(df))

def clean_text(text):
    if pd.isna(text):
        return None
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text if text else None

def optimize_for_tts(text):
    if not text:
        return None
    text = str(text)
    text = text.replace('투여', '복용')
    text = text.replace('경구투여', '먹는 약')
    text = re.sub(r'(\d+)mg', r'\1밀리그램', text)
    text = re.sub(r'(\d+)mL', r'\1밀리리터', text)
    return text

print("📥 데이터 임포트 시작...\n")

# ============================================
# 1단계: 허가목록 전부 임포트
# ============================================
print("📋 1단계: 의약품 제품 허가목록 로딩 (44,259개)...")

try:
    df_permit = pd.read_csv('의약품 제품 허가 목록_20251004.csv', encoding='cp949')
except:
    df_permit = pd.read_csv('의약품 제품 허가 목록_20251004.csv', encoding='euc-kr')

print(f"CSV 행 수: {len(df_permit)}")

created = 0
updated = 0
skipped = 0

for idx, row in df_permit.iterrows():
    try:
        item_seq = extract_column(pd.DataFrame([row]), 'ITEM_SEQ').iloc[0]
        
        if pd.isna(item_seq):
            skipped += 1
            continue
        
        item_name = clean_text(extract_column(pd.DataFrame([row]), 'ITEM_NAME').iloc[0])
        
        if not item_name:
            skipped += 1
            continue
        
        medicine, is_created = Medicine.objects.update_or_create(
            item_seq=int(item_seq),
            defaults={
                'item_name': item_name,
                'item_name_eng': clean_text(extract_column(pd.DataFrame([row]), 'ITEM_ENG_NAME').iloc[0]),
                'entp_name': clean_text(extract_column(pd.DataFrame([row]), 'ENTP_NAME').iloc[0]),
                # 'entp_name_eng': clean_text(extract_column(pd.DataFrame([row]), 'ENTP_ENG_NAME').iloc[0]),
                'main_ingredient': clean_text(extract_column(pd.DataFrame([row]), 'ITEM_INGR_NAME').iloc[0]),
                'class_type': clean_text(extract_column(pd.DataFrame([row]), 'SPCLTY_PBLC').iloc[0]),
                'product_type': clean_text(extract_column(pd.DataFrame([row]), 'PRDUCT_TYPE').iloc[0]),
                'edi_code': clean_text(extract_column(pd.DataFrame([row]), 'EDI_CODE').iloc[0]),
            }
        )
        
        if is_created:
            created += 1
        else:
            updated += 1
        
        total = created + updated
        if total % 5000 == 0:
            print(f"    ... {total}개 처리 (생성: {created}, 업데이트: {updated})")
            
    except Exception as e:
        skipped += 1
        if skipped <= 10:
            print(f"    에러 (행 {idx}): {str(e)}")
        continue

print(f"    ✓ 생성: {created}개, 업데이트: {updated}개, 건너뜀: {skipped}개\n")

# ============================================
# 2단계: 개요정보로 상세 정보 업데이트
# ============================================
print("📋 2단계: 의약품 개요정보로 상세 정보 업데이트...")

try:
    df_detail = pd.read_csv('의약품개요정보 조회_20251004.csv', encoding='cp949')
except:
    df_detail = pd.read_csv('의약품개요정보 조회_20251004.csv', encoding='euc-kr')

updated_count = 0
for idx, row in df_detail.iterrows():
    try:
        item_seq = extract_column(pd.DataFrame([row]), 'ITEMSEQ').iloc[0]
        
        if pd.isna(item_seq):
            continue
        
        Medicine.objects.filter(item_seq=int(item_seq)).update(
            effect=clean_text(extract_column(pd.DataFrame([row]), 'EFCYQESITM').iloc[0]),
            usage=clean_text(extract_column(pd.DataFrame([row]), 'USEMETHODQESITM').iloc[0]),
            warning_critical=clean_text(extract_column(pd.DataFrame([row]), 'ATPNWARNQESITM').iloc[0]),
            warning_general=clean_text(extract_column(pd.DataFrame([row]), 'ATPNQESITM').iloc[0]),
            interaction=clean_text(extract_column(pd.DataFrame([row]), 'INTRCQESITM').iloc[0]),
            side_effect=clean_text(extract_column(pd.DataFrame([row]), 'SEQESITM').iloc[0]),
            storage=clean_text(extract_column(pd.DataFrame([row]), 'DEPOSITMETHODQESITM').iloc[0]),
        )
        updated_count += 1
        
        if updated_count % 1000 == 0:
            print(f"    ... {updated_count}개 업데이트 중")
            
    except Exception as e:
        continue

print(f"    ✓ {updated_count}개 상세정보 추가 완료\n")

# ============================================
# 3단계: 낱알 정보
# ============================================
print("💊 3단계: 낱알 식별정보 로딩...")

try:
    df_pill = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='utf-8')
except:
    try:
        df_pill = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='cp949')
    except:
        df_pill = pd.read_csv('의약품 낱알식별정보 데이터2024년.csv', encoding='euc-kr')

pill_count = 0
for idx, row in df_pill.iterrows():
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
                'color_back': row.get('COLOR_CLASS2') if pd.notna(row.get('COLOR_CLASS2')) else None,
                'print_front': row.get('PRINT_FRONT') if pd.notna(row.get('PRINT_FRONT')) else None,
                'print_back': row.get('PRINT_BACK') if pd.notna(row.get('PRINT_BACK')) else None,
                'length_long': float(row.get('LENG_LONG')) if pd.notna(row.get('LENG_LONG')) else None,
                'length_short': float(row.get('LENG_SHORT')) if pd.notna(row.get('LENG_SHORT')) else None,
                'thickness': float(row.get('THICK')) if pd.notna(row.get('THICK')) else None,
                'line_front': row.get('LINE_FRONT') if pd.notna(row.get('LINE_FRONT')) else None,
                'line_back': row.get('LINE_BACK') if pd.notna(row.get('LINE_BACK')) else None,
                'shape_code': int(row.get('SHAPE_CODE')) if pd.notna(row.get('SHAPE_CODE')) else None,
            }
        )
        pill_count += 1
    except Medicine.DoesNotExist:
        continue
    except Exception as e:
        continue

print(f"    ✓ {pill_count}개 낱알 정보 임포트 완료\n")

# ============================================
# 4단계: 접근성 정보
# ============================================
print("🎤 4단계: 장애인 접근성 정보 로딩...")

try:
    df_access = pd.read_csv('장애인 의약품 안전사용 정보음성·수어영상_20251004.csv', encoding='cp949')
except:
    df_access = pd.read_csv('장애인 의약품 안전사용 정보음성·수어영상_20251004.csv', encoding='euc-kr')

access_count = 0
for idx, row in df_access.iterrows():
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
        access_count += 1
    except Medicine.DoesNotExist:
        continue
    except Exception as e:
        continue

print(f"    ✓ {access_count}개 접근성 정보 임포트 완료\n")

# ============================================
# 최종 통계
# ============================================
print("="*60)
print("✅ 모든 임포트 완료!\n")
print(f"📊 총 의약품: {Medicine.objects.count():,}개")
print(f"   - 상세정보 있음: {Medicine.objects.filter(effect__isnull=False).count():,}개")
print(f"   - 기본정보만: {Medicine.objects.filter(effect__isnull=True).count():,}개")
print(f"💊 낱알 정보: {PillIdentification.objects.count():,}개")
print(f"🎤 접근성 정보: {AccessibilityInfo.objects.count():,}개")
print("="*60)