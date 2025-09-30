import openai
import base64
import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import MedicineAnalysis

# OpenAI 클라이언트를 함수 내에서 초기화 (더 안전한 방법)
def get_openai_client():
    """OpenAI 클라이언트를 안전하게 가져오기"""
    try:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your-openai-api-key-here':
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
        return openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        print(f"OpenAI 클라이언트 초기화 오류: {e}")
        return None

def test_api_connection():
    """OpenAI API 연결 테스트"""
    try:
        client = get_openai_client()
        if not client:
            return False, "OpenAI 클라이언트 초기화 실패"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, world!"}],
            max_tokens=10
        )
        return True, "API 연결 성공"
    except Exception as e:
        return False, str(e)

def encode_image(image_path):
    """이미지를 base64로 인코딩"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"이미지 인코딩 오류: {e}")
        return None

def analyze_medicine_envelope(image_path):
    """약봉투 글씨 인식"""
    client = get_openai_client()
    if not client:
        return "OpenAI 클라이언트 초기화에 실패했습니다."
    
    base64_image = encode_image(image_path)
    if not base64_image:
        return "이미지 처리 중 오류가 발생했습니다."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """이 약봉투 이미지를 분석해서 다음 정보를 JSON 형태로 추출해주세요:
                            {
                                "medicine_name": "약품명",
                                "dosage_instructions": "복용법",
                                "frequency": "복용횟수",
                                "prescription_number": "처방전 번호"
                            }
                            
                            정확한 JSON 형태로만 응답해주세요. 한국어로 답변해주세요."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        return f"API 호출 중 오류가 발생했습니다: {str(e)}"

def analyze_dosage_schedule(image_path):
    """복용시간 글씨 인식"""
    client = get_openai_client()
    if not client:
        return "OpenAI 클라이언트 초기화에 실패했습니다."
    
    base64_image = encode_image(image_path)
    if not base64_image:
        return "이미지 처리 중 오류가 발생했습니다."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """이 약물 복용 스케줄 이미지를 분석해서 JSON 형태로 추출해주세요:
                            {
                                "morning": "아침 복용 정보",
                                "lunch": "점심 복용 정보",
                                "evening": "저녁 복용 정보",
                                "meal_timing": "식전/식후 여부"
                            }
                            
                            정확한 JSON 형태로만 응답해주세요. 한국어로 답변해주세요."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        return f"API 호출 중 오류가 발생했습니다: {str(e)}"

def identify_medicine_appearance(image_path):
    """약 외관으로 약물 식별"""
    client = get_openai_client()
    if not client:
        return "OpenAI 클라이언트 초기화에 실패했습니다."
    
    base64_image = encode_image(image_path)
    if not base64_image:
        return "이미지 처리 중 오류가 발생했습니다."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """이 약물 이미지를 분석해서 JSON 형태로 추출해주세요:
                            {
                                "shape": "약물 형태 (정제, 캡슐, 시럽 등)",
                                "color": "색상",
                                "size": "크기",
                                "marking": "각인 정보",
                                "estimated_name": "추정 약물명",
                                "warnings": "주의사항"
                            }
                            
                            정확한 JSON 형태로만 응답해주세요. 한국 의약품 기준으로 분석해주세요. 한국어로 답변해주세요."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=600,
            temperature=0.1
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        return f"API 호출 중 오류가 발생했습니다: {str(e)}"

def home(request):
    """메인 페이지"""
    recent_analyses = MedicineAnalysis.objects.order_by('-created_at')[:5]
    
    # API 연결 테스트 (디버깅용)
    if request.GET.get('test_api'):
        success, message = test_api_connection()
        if success:
            messages.success(request, f'✅ {message}')
        else:
            messages.error(request, f'❌ API 연결 실패: {message}')
    
    return render(request, 'home.html', {'recent_analyses': recent_analyses})

def upload_and_analyze(request):
    """이미지 업로드 및 분석"""
    if request.method == 'POST':
        analysis_type = request.POST.get('analysis_type')
        image = request.FILES.get('image')
        
        print(f"🔍 디버깅: analysis_type={analysis_type}, image={image}")
        print(f"🔍 API 키 설정 여부: {bool(settings.OPENAI_API_KEY)}")
        
        if not image:
            messages.error(request, '이미지를 선택해주세요.')
            return redirect('home')
        
        if not analysis_type:
            messages.error(request, '분석 타입을 선택해주세요.')
            return redirect('home')
        
        # API 키 체크
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your-openai-api-key-here':
            messages.error(request, '❌ OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.')
            return redirect('home')
        
        # 분석 객체 생성
        analysis = MedicineAnalysis.objects.create(
            analysis_type=analysis_type,
            image=image
        )
        
        try:
            image_path = analysis.image.path
            print(f"🔍 이미지 경로: {image_path}")
            print(f"🔍 파일 존재 여부: {os.path.exists(image_path)}")
            
            # 분석 타입에 따른 처리
            if analysis_type == 'envelope':
                result = analyze_medicine_envelope(image_path)
            elif analysis_type == 'schedule':
                result = analyze_dosage_schedule(image_path)
            elif analysis_type == 'appearance':
                result = identify_medicine_appearance(image_path)
            else:
                result = "알 수 없는 분석 타입입니다."
            
            print(f"🔍 분석 결과: {result[:200]}...")
            
            analysis.analysis_result = result
            analysis.save()
            
            messages.success(request, '✅ 분석이 완료되었습니다!')
            return redirect('analysis_detail', analysis_id=analysis.id)
            
        except Exception as e:
            print(f"❌ 분석 중 오류: {e}")
            messages.error(request, f'분석 중 오류가 발생했습니다: {str(e)}')
            return redirect('home')
    
    return redirect('home')

def analysis_detail(request, analysis_id):
    """분석 결과 상세 페이지"""
    analysis = get_object_or_404(MedicineAnalysis, id=analysis_id)
    
    # JSON 결과 파싱 시도
    parsed_result = None
    try:
        result_text = analysis.analysis_result
        
        # 코드 블록 제거
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.replace('```', '').strip()
        
        parsed_result = json.loads(result_text)
    except (json.JSONDecodeError, AttributeError, IndexError) as e:
        print(f"JSON 파싱 실패: {e}")
        pass
    
    return render(request, 'analysis_detail.html', {
        'analysis': analysis,
        'parsed_result': parsed_result
    })

def analysis_history(request):
    """분석 히스토리 페이지"""
    analyses = MedicineAnalysis.objects.order_by('-created_at')
    return render(request, 'analysis_history.html', {'analyses': analyses})

# ===== 3. 간단한 API 테스트 스크립트 (test_api.py) =====
# 프로젝트 루트에 이 파일 생성

import os
import django
from django.conf import settings

# Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_project.settings')
django.setup()

def test_openai_simple():
    """간단한 OpenAI API 테스트"""
    try:
        import openai
        from decouple import config
        
        # API 키 확인
        api_key = config('OPENAI_API_KEY', default=None)
        print(f"🔍 API 키 설정: {'✅' if api_key else '❌'}")
        print(f"🔍 API 키 앞 10자리: {api_key[:10] if api_key else 'None'}")
        
        if not api_key or api_key == 'your-openai-api-key-here':
            print("❌ API 키가 설정되지 않았습니다!")
            return
        
        # OpenAI 클라이언트 생성
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI 클라이언트 생성 성공")
        
        # 간단한 API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "안녕하세요! 간단한 테스트입니다."}],
            max_tokens=20
        )
        
        print("✅ API 호출 성공!")
        print(f"응답: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_openai_simple()