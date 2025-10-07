from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.shortcuts import render, get_object_or_404  # 👈 이 줄 추가/수정
from .models import Medicine, PillIdentification, AccessibilityInfo
from medicines.models import UserMedication
from django.contrib.auth.models import User

def my_medications(request):
    """내 복용약 목록"""
    user = User.objects.first()  # 임시
    
    medications = UserMedication.objects.filter(
        user=user,
        is_completed=False
    ).select_related('medicine', 'medicine__pill_info', 'medicine__accessibility')
    
    return render(request, 'medicines/my_medications.html', {
        'medications': medications
    })

@require_http_methods(["GET"])
def search_medicine(request):
    """의약품 검색 API (음성 검색 지원)"""
    query = request.GET.get('q', '').strip()
    
    # 빈 검색어면 전체 목록 반환 (50개 제한)
    if not query:
        medicines = Medicine.objects.select_related('pill_info', 'accessibility')[:50]
    else:
        # 제품명, 제조사, 주성분으로 검색
        medicines = Medicine.objects.filter(
            Q(item_name__icontains=query) |
            Q(entp_name__icontains=query) |
            Q(main_ingredient__icontains=query)
        ).select_related('pill_info', 'accessibility')[:20]
    
    results = []
    for med in medicines:
        # TTS 우선, 없으면 일반 텍스트
        effect_text = (med.accessibility.effect_tts if hasattr(med, 'accessibility') and med.accessibility.effect_tts 
                      else med.effect)
        usage_text = (med.accessibility.usage_tts if hasattr(med, 'accessibility') and med.accessibility.usage_tts 
                     else med.usage)
        
        results.append({
            'item_seq': med.item_seq,
            'item_name': med.item_name,
            'entp_name': med.entp_name,
            'effect': effect_text,
            'usage': usage_text,
            'warning': med.warning_critical or med.warning_general,
            'image_url': med.pill_info.image_url if hasattr(med, 'pill_info') else None,
            'video_url': med.accessibility.video_url if hasattr(med, 'accessibility') else None,
            'has_audio': hasattr(med, 'accessibility') and med.accessibility.has_audio,
        })
    
    return JsonResponse({
        'count': len(results),
        'results': results
    })

@require_http_methods(["GET"])
def medicine_detail(request, item_seq):
    """의약품 상세 정보 API (TTS 최적화)"""
    try:
        medicine = Medicine.objects.select_related('pill_info', 'accessibility').get(item_seq=item_seq)
    except Medicine.DoesNotExist:
        return JsonResponse({'error': '의약품을 찾을 수 없습니다'}, status=404)
    
    # TTS 최적화 텍스트 우선
    has_accessibility = hasattr(medicine, 'accessibility')
    
    data = {
        'basic_info': {
            'item_seq': medicine.item_seq,
            'item_name': medicine.item_name,
            'entp_name': medicine.entp_name,
            'main_ingredient': medicine.main_ingredient,
            'class_type': medicine.class_type,
        },
        'effect': {
            'text': medicine.effect,
            'tts': medicine.accessibility.effect_tts if has_accessibility else medicine.effect,
        },
        'usage': {
            'text': medicine.usage,
            'tts': medicine.accessibility.usage_tts if has_accessibility else medicine.usage,
        },
        'warning': {
            'critical': medicine.warning_critical,
            'general': medicine.warning_general,
            'tts': medicine.accessibility.warning_tts if has_accessibility else medicine.warning_general,
        },
        'side_effect': medicine.side_effect,
        'interaction': medicine.interaction,
        'storage': medicine.storage,
        'accessibility': {
            'video_url': medicine.accessibility.video_url if has_accessibility else None,
            'has_audio': medicine.accessibility.has_audio if has_accessibility else False,
            'has_sign_language': medicine.accessibility.has_sign_language if has_accessibility else False,
            'barcode': medicine.accessibility.barcode if has_accessibility else None,
        } if has_accessibility else None,
        'pill_info': {
            'image_url': medicine.pill_info.image_url,
            'shape': medicine.pill_info.shape,
            'color': f"{medicine.pill_info.color_front or ''} {medicine.pill_info.color_back or ''}".strip(),
            'print_front': medicine.pill_info.print_front,
            'print_back': medicine.pill_info.print_back,
            'size': f"{medicine.pill_info.length_long}mm x {medicine.pill_info.length_short}mm" if medicine.pill_info.length_long else None,
        } if hasattr(medicine, 'pill_info') else None,
    }
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def search_by_barcode(request):
    """바코드로 검색 API"""
    barcode = request.GET.get('barcode', '').strip()
    
    if not barcode:
        return JsonResponse({'error': '바코드를 입력하세요'}, status=400)
    
    try:
        accessibility = AccessibilityInfo.objects.select_related('medicine').get(
            Q(barcode=barcode) | Q(std_code__contains=barcode)
        )
        medicine = accessibility.medicine
        
        return JsonResponse({
            'item_seq': medicine.item_seq,
            'item_name': medicine.item_name,
            'entp_name': medicine.entp_name,
            'effect_tts': accessibility.effect_tts or medicine.effect,
            'usage_tts': accessibility.usage_tts or medicine.usage,
            'video_url': accessibility.video_url,
        })
    except AccessibilityInfo.DoesNotExist:
        return JsonResponse({'error': '해당 바코드의 의약품을 찾을 수 없습니다'}, status=404)

@require_http_methods(["GET"])
def search_by_image(request):
    """이미지 특징으로 검색 API (색상, 모양, 각인)"""
    shape = request.GET.get('shape', '').strip()
    color = request.GET.get('color', '').strip()
    print_text = request.GET.get('print', '').strip()
    
    query = Q()
    if shape:
        query &= Q(shape__icontains=shape)
    if color:
        query &= Q(color_front__icontains=color) | Q(color_back__icontains=color)
    if print_text:
        query &= Q(print_front__icontains=print_text) | Q(print_back__icontains=print_text)
    
    if not query:
        return JsonResponse({'error': '검색 조건을 입력하세요'}, status=400)
    
    pills = PillIdentification.objects.filter(query).select_related('medicine')[:10]
    
    results = []
    for pill in pills:
        results.append({
            'item_seq': pill.medicine.item_seq,
            'item_name': pill.medicine.item_name,
            'entp_name': pill.medicine.entp_name,
            'shape': pill.shape,
            'color': f"{pill.color_front or ''} {pill.color_back or ''}".strip(),
            'print': f"{pill.print_front or ''} / {pill.print_back or ''}",
            'image_url': pill.image_url,
        })
    
    return JsonResponse({
        'count': len(results),
        'results': results
    })

@require_http_methods(["GET"])
def medicines_with_video(request):
    """음성/수어 영상이 있는 의약품 목록"""
    medicines = Medicine.objects.filter(
        accessibility__has_audio=True
    ).select_related('accessibility')[:50]
    
    results = []
    for med in medicines:
        results.append({
            'item_seq': med.item_seq,
            'item_name': med.item_name,
            'video_url': med.accessibility.video_url,
            'has_sign_language': med.accessibility.has_sign_language,
        })
    
    return JsonResponse({
        'count': len(results),
        'results': results
    })

def index(request):
    """메인 웹 페이지"""
    return render(request, 'medicines/base.html')

@require_http_methods(["GET"])
def get_stats(request):
    """통계 API"""
    from django.db.models import Count
    
    total_medicines = Medicine.objects.count()
    total_videos = AccessibilityInfo.objects.filter(has_audio=True).count()
    total_pills = PillIdentification.objects.count()
    
    return JsonResponse({
        'total_medicines': total_medicines,
        'total_videos': total_videos,
        'total_pills': total_pills,
    })

def medicine_detail_page(request, item_seq):
    """의약품 상세 페이지 (HTML)"""
    medicine = get_object_or_404(
        Medicine.objects.select_related('pill_info', 'accessibility'),
        item_seq=item_seq
    )
    
    return render(request, 'medicines/detail.html', {
        'medicine': medicine
    })