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
from django.contrib.auth.models import User
from medicines.models import Medicine, UserMedication
from datetime import datetime

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
    
    # 사용자 정보 (일단 임시로 첫 번째 사용자 사용)
    # TODO: 실제로는 로그인된 사용자를 사용해야 함
    try:
        user = User.objects.first()
        if not user:
            # 사용자가 없으면 자동 생성
            user = User.objects.create_user(username='guest', password='guest123')
    except:
        user = None
    
    file_path = default_storage.save(f'ocr_temp/{image_file.name}', image_file)
    
    try:
        # OpenAI Vision으로 처방전 정보 추출
        with default_storage.open(file_path, 'rb') as f:
            result = call_openai_vision(f)
        
        if not result['success']:
            return JsonResponse({
                'success': False,
                'error': result['error']
            })
        
        prescription_data = result['data']
        
        # 약품명 리스트 추출
        medicine_names = [med.get('name') for med in prescription_data.get('medicines', []) if med.get('name')]
        
        # DB에서 의약품 검색
        medicines = search_medicines_by_names(medicine_names)
        
        # 🎯 여기서 사용자 DB에 저장!
        saved_count = 0
        if user:
            # 처방전 정보
            prescription_date_str = prescription_data.get('dispensing_date')
            prescription_date = None
            if prescription_date_str:
                try:
                    prescription_date = datetime.strptime(prescription_date_str, '%Y-%m-%d').date()
                except:
                    pass
            
            pharmacy_name = prescription_data.get('pharmacy_name')
            hospital_name = prescription_data.get('hospital_name')
            
            # 각 약품 저장
            for med_info in prescription_data.get('medicines', []):
                med_name = med_info.get('name')
                if not med_name:
                    continue
                
                # DB에서 약품 찾기
                try:
                    medicine = Medicine.objects.filter(
                        Q(item_name__icontains=med_name) |
                        Q(item_name__contains=med_name)
                    ).first()
                    
                    if medicine:
                        # 사용자 복용약에 저장
                        UserMedication.objects.create(
                            user=user,
                            medicine=medicine,
                            dosage=med_info.get('dosage'),
                            frequency=med_info.get('frequency'),
                            days=med_info.get('days'),
                            prescription_date=prescription_date,
                            pharmacy_name=pharmacy_name,
                            hospital_name=hospital_name,
                        )
                        saved_count += 1
                except Exception as e:
                    print(f"약품 저장 실패: {med_name} - {str(e)}")
                    continue
        
        # 처방전 정보와 DB 정보 매칭
        for med_info in prescription_data.get('medicines', []):
            med_name = med_info.get('name')
            if med_name:
                for db_med in medicines:
                    if med_name in db_med['item_name'] or db_med['item_name'] in med_name:
                        med_info['db_info'] = db_med
                        break
        
        return JsonResponse({
            'success': True,
            'prescription': prescription_data,
            'medicines': medicines,
            'count': len(medicines),
            'saved_count': saved_count,  # 저장된 약품 수
            'message': f'✅ {saved_count}개 약품이 내 복용약에 저장되었습니다!'
        })
    
    except Exception as e:
        import traceback
        print(f"오류: {str(e)}")
        print(traceback.format_exc())
        
        return JsonResponse({
            'success': False,
            'error': f'처리 중 오류: {str(e)}'
        }, status=500)
    
    finally:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)