# ocr/views.py

import base64
import json
from openai import OpenAI
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from medicines.models import Medicine
from django.db.models import Q

def ocr_page(request):
    """OCR 메인 페이지"""
    return render(request, 'ocr/index.html')

def call_openai_vision(image_file):
    """OpenAI Vision API로 처방전 정보 추출"""
    try:
        # API 키 확인
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == 'your-openai-api-key':
            return {
                'success': False,
                'error': 'OpenAI API 키가 설정되지 않았습니다. settings.py에서 OPENAI_API_KEY를 설정하세요.'
            }
        
        client = OpenAI(api_key=api_key)
        
        # 이미지를 base64로 인코딩
        image_file.seek(0)
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """이 처방전/약봉투 사진에서 정보를 추출해주세요.

다음 정보를 JSON 형식으로 출력해주세요:

{
  "medicines": [
    {
      "name": "약품명",
      "dosage": "1회 1정",
      "frequency": "1일 3회",
      "days": "3일분"
    }
  ],
  "dispensing_date": "2024-01-15",
  "patient_name": "홍길동",
  "pharmacy_name": "○○약국",
  "hospital_name": "○○병원"
}

규칙:
1. medicines 배열에 모든 약을 나열
2. 정보가 없으면 null 또는 빈 배열로 표시
3. 날짜는 YYYY-MM-DD 형식
4. 약품명은 정확히 표기 (상품명)
5. 복약안내는 있는 그대로 추출

JSON만 출력하고 다른 설명은 붙이지 마세요."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            timeout=30  # 30초 타임아웃 추가
        )
        
        # 결과 추출
        result_text = response.choices[0].message.content.strip()
        
        # JSON 파싱
        # ```json 같은 마크다운 제거
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        result_json = json.loads(result_text.strip())
        
        return {
            'success': True,
            'data': result_json,
            'raw_text': result_text
        }
    
    except json.JSONDecodeError as e:
        # JSON 파싱 실패 시 텍스트 그대로 반환
        return {
            'success': True,
            'data': {
                'medicines': [],
                'error': 'JSON 파싱 실패',
                'raw': result_text if 'result_text' in locals() else str(e)
            },
            'raw_text': result_text if 'result_text' in locals() else ''
        }
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': f'OpenAI API 오류: {str(e)}',
            'detail': traceback.format_exc()
        }

def search_medicines_by_names(medicine_names):
    """추출된 약 이름으로 DB 검색"""
    found_medicines = []
    
    for name in medicine_names:
        if not name:
            continue
            
        # 정확히 일치하는 약 찾기
        medicines = Medicine.objects.filter(
            Q(item_name__icontains=name) |
            Q(item_name__contains=name)
        ).select_related('pill_info', 'accessibility')[:3]
        
        for med in medicines:
            if med.item_seq not in [m['item_seq'] for m in found_medicines]:
                found_medicines.append({
                    'item_seq': med.item_seq,
                    'item_name': med.item_name,
                    'entp_name': med.entp_name,
                    'effect': med.effect[:100] + '...' if med.effect and len(med.effect) > 100 else med.effect,
                    'image_url': med.pill_info.image_url if hasattr(med, 'pill_info') else None,
                    'has_video': hasattr(med, 'accessibility') and med.accessibility.video_url,
                })
    
    return found_medicines

@csrf_exempt
def process_ocr(request):
    """이미지 업로드 및 OpenAI Vision 처리"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 가능합니다'}, status=400)
    
    if 'image' not in request.FILES:
        return JsonResponse({'error': '이미지 파일을 업로드하세요'}, status=400)
    
    image_file = request.FILES['image']
    
    print("\n" + "="*80)
    print("🔍 OCR 처리 시작")
    print(f"📁 파일명: {image_file.name}")
    print(f"📊 파일 크기: {image_file.size / 1024:.2f} KB")
    print("="*80)
    
    # 파일 저장
    file_path = default_storage.save(f'ocr_temp/{image_file.name}', image_file)
    
    try:
        # OpenAI Vision으로 처방전 정보 추출
        print("\n🤖 OpenAI Vision API 호출 중...")
        
        with default_storage.open(file_path, 'rb') as f:
            result = call_openai_vision(f)
        
        if not result['success']:
            print(f"\n❌ 오류 발생: {result['error']}")
            if 'detail' in result:
                print(f"📋 상세 오류:\n{result['detail']}")
            return JsonResponse({
                'success': False,
                'error': result['error']
            })
        
        prescription_data = result['data']
        
        # 터미널에 결과 출력
        print("\n" + "="*80)
        print("✅ OCR 처리 완료!")
        print("="*80)
        
        # 환자 정보
        print("\n👤 환자 정보:")
        print(f"  - 이름: {prescription_data.get('patient_name', '정보 없음')}")
        
        # 처방 정보
        print("\n📋 처방 정보:")
        print(f"  - 조제일자: {prescription_data.get('dispensing_date', '정보 없음')}")
        print(f"  - 약국: {prescription_data.get('pharmacy_name', '정보 없음')}")
        print(f"  - 병원: {prescription_data.get('hospital_name', '정보 없음')}")
        
        # 의약품 목록
        medicines_list = prescription_data.get('medicines', [])
        print(f"\n💊 처방 의약품 ({len(medicines_list)}개):")
        
        for idx, med in enumerate(medicines_list, 1):
            print(f"\n  [{idx}] {med.get('name', '이름 없음')}")
            if med.get('dosage'):
                print(f"      📌 투약량: {med['dosage']}")
            if med.get('frequency'):
                print(f"      🔄 복용횟수: {med['frequency']}")
            if med.get('days'):
                print(f"      📅 복용기간: {med['days']}")
        
        # 약품명 리스트 추출
        medicine_names = [med.get('name') for med in medicines_list if med.get('name')]
        
        print(f"\n🔍 DB 검색 중... ({len(medicine_names)}개 약품)")
        
        # DB에서 의약품 검색
        medicines = search_medicines_by_names(medicine_names)
        
        print(f"✅ DB에서 {len(medicines)}개 의약품 찾음")
        
        for med in medicines:
            print(f"  - {med['item_name']} ({med['entp_name']})")
        
        # 처방전 정보와 DB 정보 매칭
        for med_info in prescription_data.get('medicines', []):
            med_name = med_info.get('name')
            if med_name:
                # DB에서 찾은 의약품과 매칭
                for db_med in medicines:
                    if med_name in db_med['item_name'] or db_med['item_name'] in med_name:
                        med_info['db_info'] = db_med
                        break
        
        print("\n" + "="*80)
        print("🎉 처리 완료!\n")
        
        return JsonResponse({
            'success': True,
            'prescription': prescription_data,
            'medicines': medicines,
            'count': len(medicines)
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        print("\n" + "="*80)
        print("❌ 처리 중 오류 발생")
        print("="*80)
        print(f"오류: {str(e)}")
        print(f"\n상세 오류:\n{error_trace}")
        print("="*80 + "\n")
        
        return JsonResponse({
            'success': False,
            'error': f'처리 중 오류: {str(e)}'
        }, status=500)
    
    finally:
        # 임시 파일 삭제
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            print(f"🗑️  임시 파일 삭제됨: {file_path}\n")