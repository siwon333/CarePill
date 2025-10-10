import os
import re
import json
import time
import uuid
import traceback
import datetime
import logging
import requests
from collections import Counter
from typing import List, Dict, Tuple

# ===== Django import =====
from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404  # ⭐ redirect 추가
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User  # ⭐ User 추가
from django.db.models import Q
import local_settings

# ===== medicines 앱 연동 (내 약 목록용) =====
from medicines.models import Medicine, UserMedication  # ⭐ 추가

api_key = local_settings.OPENAI_API_KEY

def meds(request):
    # TODO: 실제 배포 시 request.user 사용
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(username='guest', password='guest123')
    
    # medicines 앱의 UserMedication에서 데이터 가져오기
    medications = UserMedication.objects.filter(
        user=user,
        is_completed=False
    ).select_related('medicine', 'medicine__pill_info')
    
    return render(request, "carepill/meds.html", {
        'medications': medications
    })

def home(request):  return render(request, "carepill/home.html")
def scan(request):  return render(request, "carepill/scan.html")
def voice(request): return render(request, "carepill/voice.html")

def issue_ephemeral(request):
    r = requests.post(
        "https://api.openai.com/v1/realtime/sessions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "realtime=v1",
        },
        json={
            "model": "gpt-4o-mini-realtime-preview-2024-12-17",
            "voice": "verse",
            "modalities": ["audio", "text"],
            "turn_detection": {
                "type": "server_vad", 
                "create_response": True, 
                "silence_duration_ms": 500
            },
            "input_audio_transcription": {"model": "gpt-4o-mini-transcribe"},
            "instructions": (
                "You are 'CarePill', a voice-based medication assistant designed to help visually impaired users. "
                "Speak Korean with clear, precise pronunciation, like a professional news announcer. "
                "Provide guidance about medication usage, dosage, timing, and potential drug interactions. "
                "Offer emotional support and speak warmly, as if you are a trusted friend who cares about the user’s well-being. "
                "Keep your responses short, calm, and friendly, delivering them with confidence and kindness."
            ),
        },
        timeout=20,
    )

    try:
        data = r.json()
    except Exception:
        # OpenAI에서 예외적으로 비JSON이 오면 원문 전달
        return JsonResponse({"error": "upstream_non_json", "text": r.text}, status=r.status_code)

    if r.status_code != 200:
        # 에러 원문 그대로 반환
        return JsonResponse(data, status=r.status_code)

    # ✅ 스키마 정규화: 항상 {value, expires_at, session} 형태로 반환
    value = data.get("value") or (data.get("client_secret") or {}).get("value")
    expires_at = data.get("expires_at") or (data.get("client_secret") or {}).get("expires_at")
    session = data.get("session") or {"id": data.get("id"), "type": "realtime", "object": "realtime.session"}

    if not value:
        return JsonResponse({"error": "no_ephemeral_value", "upstream": data}, status=502)

    return JsonResponse({"value": value, "expires_at": expires_at, "session": session}, status=200)


import os, requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def realtime_sdp_exchange(request):
    """
    브라우저가 직접 OpenAI에 POST하지 않고, 서버가 대신 SDP를 교환해준다.
    - 요청 헤더 Authorization: Bearer <ephemeral_key> (클라가 전달)
    - 요청 body: offer SDP (text)
    - 응답 body: answer SDP (text)
    """
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    # 브라우저가 준 에페메럴 키를 그대로 사용 (주의: 정식 OPENAI_API_KEY 아님)
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ek_"):  # 간단 검증
        return JsonResponse({"error": "missing_or_invalid_ephemeral"}, status=400)

    offer_sdp = request.body or b""
    if not offer_sdp:
        return JsonResponse({"error": "empty_offer_sdp"}, status=400)

    try:
        upstream = requests.post(
            "https://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17",
            headers={
                "Authorization": auth,                   # Bearer ek_... (ephemeral)
                "Content-Type": "application/sdp",
                "OpenAI-Beta": "realtime=v1",
            },
            data=offer_sdp,
            timeout=20,
        )
    except requests.RequestException as e:
        return JsonResponse({"error": "upstream_network_error", "detail": str(e)}, status=502)

    # OpenAI는 answer SDP를 text로 반환
    return HttpResponse(upstream.text, status=upstream.status_code, content_type="application/sdp")






















# views.py
import os
import re
import json
import time
import uuid
import traceback
import datetime
import logging
import requests

from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

# ===== OpenAI 설정 =====
SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL", "gpt-4o-mini")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


# ===== 파일명/저장 유틸 =====
def _sanitize_filename(name: str) -> str:
    if not isinstance(name, str):
        name = str(name or "session")
    name = name.strip()
    # 한글/영문/숫자/공백/일부 특수문자만 허용
    name = re.sub(r'[^0-9A-Za-z\u3131-\u318E\uAC00-\uD7A3 _\-.]', '_', name)
    name = name.replace(" ", "_")
    name = name[:80] or "session"
    # 확장자 보장
    if not name.lower().endswith(".txt"):
        name += ".txt"
    return name


def _save_txt(meta, summary_text, transcript_lines):
    """ media/conversations/에 .txt 저장하고 파일경로/URL/다운로드URL 반환 """
    media_root = getattr(settings, "MEDIA_ROOT", os.path.join(os.getcwd(), "media"))
    media_url  = getattr(settings, "MEDIA_URL", "/media/")
    base_dir   = os.path.join(media_root, "conversations")
    os.makedirs(base_dir, exist_ok=True)

    ts    = meta.get("ended_at") or datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    title = _sanitize_filename(meta.get("title") or "carepill_session")
    # 이미 title에 .txt가 들어가 있으므로 ts_ 접두사만
    fname = f"{ts}_{title}" if not title.startswith(ts + "_") else title

    fpath = os.path.join(base_dir, fname)                      # 실제 파일 경로
    furl  = media_url.rstrip("/") + "/conversations/" + fname  # /media/... 열람 URL
    download_url = "/api/conversation/download/?name=" + fname # 다운로드 URL

    content = []
    content.append("[3-line Summary]")
    content.append((summary_text or "").strip())
    content.append("")
    content.append("[Conversation]")
    content.extend(transcript_lines or [])
    with open(fpath, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    return {"file_name": fname, "path_fs": fpath, "path_url": furl, "download_url": download_url}


def _save_debug(rid, debug_obj):
    try:
        media_root = getattr(settings, "MEDIA_ROOT", os.path.join(os.getcwd(), "media"))
        base_dir   = os.path.join(media_root, "conversations")
        os.makedirs(base_dir, exist_ok=True)
        fname = f"_debug_{rid}.json"
        fpath = os.path.join(base_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(debug_obj, f, ensure_ascii=False, indent=2)
        media_url  = getattr(settings, "MEDIA_URL", "/media/")
        furl  = media_url.rstrip("/") + "/conversations/" + fname
        return furl
    except Exception:
        return None


# ===== 다운로드 엔드포인트 (Content-Disposition) =====
@csrf_exempt
def api_conversation_download(request):
    """
    GET /api/conversation/download/?name=<파일명.txt>
    conversations 폴더 아래의 .txt만 다운로드로 제공
    """
    name = request.GET.get("name", "")
    if not name or "/" in name or "\\" in name or name.startswith("."):
        return JsonResponse({"error": "bad_name"}, status=400)
    if not name.lower().endswith(".txt"):
        return JsonResponse({"error": "bad_ext"}, status=400)

    base_dir = os.path.join(getattr(settings, "MEDIA_ROOT", os.path.join(os.getcwd(),"media")), "conversations")
    fpath = os.path.join(base_dir, name)
    if not os.path.exists(fpath):
        raise Http404("file not found")

    with open(fpath, "rb") as fp:
        resp = HttpResponse(fp.read(), content_type="text/plain; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{name}"'
    return resp


# ===== 3줄 요약 + 저장 (TXT 전용, 디버그 포함) =====
@csrf_exempt
def api_conversation_summarize_and_save(request):
    """
    payload:
      - transcript: [{role:"user|assistant|...","text":"..."}...]  (선택)
      - 또는 lines: ["User: ...","CarePill: ...", ...]             (권장)
      - save: true|false
      - meta: { title?: str, ended_at?: "YYYYMMDDTHHMMSS" }
      - debug: true|false   # 응답에 debug 포함

    response:
      - { "summary_text": str,
          "saved": bool,
          "path": str|null,          # /media/... 열람용 URL
          "download_url": str|null,  # 다운로드 URL (Content-Disposition)
          "file_name": str|null,
          "debug": {...}? }
    """
    rid = str(uuid.uuid4())[:8]
    t0 = time.time()

    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        return JsonResponse({"error": "invalid_json", "detail": str(e)}, status=400)

    do_save    = bool(payload.get("save", False))
    meta       = payload.get("meta", {}) or {}
    debug_mode = bool(payload.get("debug") or request.GET.get("debug") == "1" or os.getenv("SUMMARY_DEBUG") == "1")

    # 입력 표준화: lines 우선, 없으면 transcript → lines로 변환
    lines = payload.get("lines")
    transcript = payload.get("transcript")
    if not lines:
        if not transcript or not isinstance(transcript, list):
            return JsonResponse({"error": "no_transcript_or_lines"}, status=400)
        lines = []
        for x in transcript:
            role = x.get("role")
            text = (x.get("text") or "").strip()
            if not text or role not in ("user", "assistant"):
                continue
            t = text
            # 앞단 접두사 제거
            t = re.sub(r'^\s*(user|사용자)\s*:\s*', '', t, flags=re.I)
            t = re.sub(r'^\s*(carepill|케어필)\s*:\s*', '', t, flags=re.I)
            prefix = "User" if role == "user" else "CarePill"
            lines.append(f"{prefix}: {t}")

    SAFE_MAX = 120
    lines = lines[-SAFE_MAX:]

    debug = {
        "request_id": rid,
        "lines_count": len(lines),
        "lines_first3": lines[:3],
        "lines_last3": lines[-3:],
        "model": SUMMARIZER_MODEL,
        "openai_status": None,
        "openai_elapsed_ms": None,
        "openai_preview": None,
        "saved_path": None,
        "server_elapsed_ms": None,
        "exception": None,
    }

    # 빈 대화 처리
    if not lines:
        summary_text = "대화 요약: (비어 있음)"
        saved_info = None
        if do_save:
            saved_info = _save_txt(meta, summary_text, [])
            debug["saved_path"] = saved_info["path_url"]
        debug["server_elapsed_ms"] = int((time.time() - t0) * 1000)
        resp = {
            "summary_text": summary_text,
            "saved": bool(saved_info),
            "path": (saved_info or {}).get("path_url") if saved_info else None,
            "download_url": (saved_info or {}).get("download_url") if saved_info else None,
            "file_name": (saved_info or {}).get("file_name") if saved_info else None,
        }
        if debug_mode: resp["debug"] = debug
        return JsonResponse(resp, status=200)

    if not api_key:
        return JsonResponse({"error": "missing_api_key"}, status=500)

    # OpenAI 호출
    prompt = (
        "아래는 사용자(User)와 케어필(CarePill)의 대화 로그입니다.\n"
        "핵심만 한국어로 '3줄 요약'을 작성하세요. 각 줄은 1문장으로 간결하게.\n"
        "가능하면 주제/요청/응답 또는 감정/행동계획이 드러나게 정리하세요.\n\n"
        "대화:\n" + "\n".join(lines)
    )

    t1 = time.time()
    try:
        resp = requests.post(
            OPENAI_API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": SUMMARIZER_MODEL,
                "messages": [
                    {"role": "system", "content": "너는 한국어 대화 요약 도우미다. 결과는 텍스트(3줄)로만 답한다."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            },
            timeout=60,
        )
        debug["openai_status"] = resp.status_code
        debug["openai_elapsed_ms"] = int((time.time() - t1) * 1000)

        if resp.status_code != 200:
            debug["openai_preview"] = resp.text[:800]
            debug["server_elapsed_ms"] = int((time.time() - t0) * 1000)
            if debug_mode: _save_debug(rid, debug)
            out = {"error": "summarize_failed", "detail": f"upstream {resp.status_code}", "upstream": resp.text}
            if debug_mode: out["debug"] = debug
            return JsonResponse(out, status=502)

        data = resp.json()
        # 응답 일부 프리뷰 보존
        try:
            debug["openai_preview"] = json.dumps(data, ensure_ascii=False)[:800]
        except Exception:
            debug["openai_preview"] = str(data)[:800]

        summary_text = (data["choices"][0]["message"]["content"] or "").strip()
        if not summary_text:
            summary_text = "대화 요약: (생성 실패)"
    except Exception as e:
        debug["exception"] = (traceback.format_exc() or str(e))[-1000:]
        debug["server_elapsed_ms"] = int((time.time() - t0) * 1000)
        if debug_mode: _save_debug(rid, debug)
        out = {"error": "summarize_failed", "detail": str(e)}
        if debug_mode: out["debug"] = debug
        return JsonResponse(out, status=502)

    # 저장(옵션)
    saved_info = None
    if do_save:
        saved_info = _save_txt(meta, summary_text, lines)
        debug["saved_path"] = saved_info["path_url"]

    debug["server_elapsed_ms"] = int((time.time() - t0) * 1000)
    if debug_mode: _save_debug(rid, debug)

    resp_out = {
        "summary_text": summary_text,
        "saved": bool(saved_info),
        "path": (saved_info or {}).get("path_url") if saved_info else None,
        "download_url": (saved_info or {}).get("download_url") if saved_info else None,
        "file_name": (saved_info or {}).get("file_name") if saved_info else None,
    }
    if debug_mode: resp_out["debug"] = debug
    return JsonResponse(resp_out, status=200)













import os, re, json, time, uuid, traceback, datetime, logging, requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

# (상단: home/scan/meds/voice, realtime, summarize 부분은 이전 버전과 동일)

# -----------------------------
# 약봉투 스캔 API (Multi‑cam 지원)
# -----------------------------

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from medicines.models import Medicine, UserMedication
import json
import re
import requests
from collections import Counter
from typing import List, Dict, Tuple
from datetime import datetime

def _strip_code_fence(text: str) -> str:
    """코드 펜스(```)를 제거하고 순수 JSON 반환"""
    if not isinstance(text, str):
        return text
    t = text.strip()
    if t.startswith("```"):
        if t.startswith("```json") or t.startswith("```JSON"):
            parts = t.split("\n", 1)
            t = parts[1] if len(parts) > 1 else ""
        else:
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        t = t.strip()
    return t


def _call_openai_envelope(image_b64: str, api_key: str, model: str = "gpt-4o") -> str:
    """OpenAI Vision API로 약봉투 이미지 분석"""
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")

    text_prompt = (
        "다음 약봉투 이미지를 분석하여 아래 스키마의 정확한 JSON만 출력하세요.\n"
        "가능하면 숫자/날짜는 포맷을 맞추세요.\n"
        "{\n"
        '  "patient_name": "환자명(문자열)",\n'
        '  "age": "나이(숫자 또는 빈 문자열)",\n'
        '  "dispense_date": "조제일자(YYYY-MM-DD 또는 YYYY.MM.DD)",\n'
        '  "pharmacy_name": "약국명",\n'
        '  "prescription_number": "처방전 또는 조제 번호",\n'
        '  "medicine_name": "약품명",\n'
        '  "dosage_instructions": "복용법(예: 아침, 저녁, 취침 전)",\n'
        '  "frequency": "복용횟수/기간(예: 1일 1회 총 30일분)",\n'
        '  "med_features": {\n'
        '    "description": "약의 한줄 설명",\n'
        '    "indications": "어디에 좋은지(적응증)",\n'
        '    "cautions": "주의사항(상호작용/부작용/주의대상 간단 요약)"\n'
        "  }\n"
        "}\n"
        "주의: 오타를 피하고, 사진 속 정보만 사용하세요. 모를 경우 빈 문자열로 두세요. 설명 문장이나 코드펜스 없이 JSON만 출력합니다."
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "너는 한국 약봉투 OCR/정보추출 전문가다. 반드시 유효한 JSON만 출력한다. 사진에 없는 정보는 공란('')으로 남긴다."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{image_b64}", "detail": "high"}}
                ]
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.1
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60
    )
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI 오류 {r.status_code}: {r.text[:200]}")
    data = r.json()
    return data["choices"][0]["message"]["content"]


def _majority_merge(values: List[str]) -> Tuple[str, float]:
    """다수결로 가장 많이 나온 값 선택"""
    cleaned = [(v or "").strip() for v in values if isinstance(v, str)]
    non_empty = [v for v in cleaned if v]
    if not non_empty:
        return "", 0.0
    cnt = Counter(non_empty)
    top = cnt.most_common()
    top_freq = top[0][1]
    candidates = [v for v, c in top if c == top_freq]
    winner = max(candidates, key=lambda s: len(s))
    conf = cnt[winner] / max(1, len(values))
    return winner, round(conf, 3)


def _merge_envelope_json(json_list: List[Dict]) -> Tuple[Dict, Dict]:
    """여러 샷의 결과를 병합"""
    merged = {}
    diag = {}
    
    # 기본 정보 병합
    for field in ["patient_name", "age", "dispense_date", "pharmacy_name", "hospital_name", "prescription_number"]:
        vals = [str(r.get(field, "") or "").strip() for r in json_list]
        best, conf = _majority_merge(vals)
        merged[field] = best
        diag[field] = {"per_shot": vals, "selected": best, "confidence": conf}
    
    # ⭐ medicines 배열 병합 (모든 약을 수집)
    all_medicines = []
    medicine_names_seen = set()
    
    for result in json_list:
        medicines = result.get("medicines", [])
        if not isinstance(medicines, list):
            continue
        
        for med in medicines:
            med_name = (med.get("medicine_name", "") or "").strip()
            if not med_name:
                continue
            
            # 중복 제거 (같은 약 이름은 한 번만)
            if med_name.lower() not in medicine_names_seen:
                medicine_names_seen.add(med_name.lower())
                all_medicines.append({
                    "medicine_name": med_name,
                    "dosage_instructions": (med.get("dosage_instructions", "") or "").strip(),
                    "frequency": (med.get("frequency", "") or "").strip(),
                    "med_features": med.get("med_features", {})
                })
    
    merged["medicines"] = all_medicines
    diag["medicines"] = {"count": len(all_medicines), "names": [m["medicine_name"] for m in all_medicines]}
    
    return merged, diag


def _find_medicine_in_db(medicine_name: str) -> List[Medicine]:
    """DB에서 약 검색 - 더 유연한 매칭"""
    if not medicine_name:
        return []
    
    # 공백 제거 및 소문자 변환
    search_name = medicine_name.strip()
    
    # 1차 검색: 정확한 이름
    medicines = Medicine.objects.filter(item_name__iexact=search_name)[:1]
    if medicines.exists():
        return list(medicines)
    
    # 2차 검색: 부분 일치 (대소문자 무시)
    medicines = Medicine.objects.filter(item_name__icontains=search_name)[:3]
    if medicines.exists():
        return list(medicines)
    
    # 3차 검색: 공백 제거하고 검색
    search_no_space = search_name.replace(" ", "")
    if search_no_space:
        medicines = Medicine.objects.filter(
            Q(item_name__icontains=search_no_space)
        )[:3]
        if medicines.exists():
            return list(medicines)
    
    return []


def _parse_date(date_str: str) -> str:
    """날짜 문자열을 YYYY-MM-DD 형식으로 변환"""
    if not date_str:
        return ""
    
    # 이미 올바른 형식이면 그대로 반환
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    
    # YYYY.MM.DD 형식 변환
    date_str = date_str.replace(".", "-")
    
    # YYYYMMDD 형식 변환
    if re.match(r'^\d{8}$', date_str):
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    
    return date_str


@csrf_exempt
def api_scan_envelope(request):
    """
    POST { images: [base64_jpeg, ...], meta?: [...] }
    약봉투 스캔 후 자동 DB 저장
    """
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    # API 키 확인
    import local_settings
    api_key = local_settings.OPENAI_API_KEY
    if not api_key:
        return JsonResponse({"error": "missing_api_key"}, status=500)

    # 이미지 데이터 추출
    images_b64 = []
    meta_in = []
    ctype = (request.headers.get('Content-Type') or '').lower()
    
    try:
        if 'application/json' in ctype:
            payload = json.loads(request.body.decode('utf-8'))
            arr = payload.get('images') or []
            if not isinstance(arr, list):
                arr = []
            images_b64 = [str(x or '').strip() for x in arr][:9]
            meta_in = payload.get('meta') or []
        else:
            f = request.FILES.get('image')
            if not f:
                return JsonResponse({"error": "no_image"}, status=400)
            images_b64 = [f.read().decode('latin1')]
            meta_in = [{"camera_index": 1, "shot_index": 1, "deviceId": "upload"}]
    except Exception as e:
        return JsonResponse({"error": "bad_payload", "detail": str(e)}, status=400)

    if not images_b64:
        return JsonResponse({"error": "no_images"}, status=400)

    # OpenAI 호출
    shots_raw = []
    json_list = []
    
    for idx, b64 in enumerate(images_b64, 1):
        b64 = re.sub(r'^data:image\/(png|jpeg);base64,', '', b64, flags=re.I)
        try:
            raw = _call_openai_envelope(b64, api_key)
            cleaned = _strip_code_fence(raw)
            try:
                parsed = json.loads(cleaned)
            except Exception:
                parsed = {}
            
            meta_obj = meta_in[idx - 1] if idx - 1 < len(meta_in) else None
            shots_raw.append({
                "index": idx,
                "raw": cleaned,
                "json": parsed,
                "image_path": f"client_shot_{idx}",
                "meta": meta_obj
            })
            json_list.append(parsed)
        except Exception as e:
            meta_obj = meta_in[idx - 1] if idx - 1 < len(meta_in) else None
            shots_raw.append({
                "index": idx,
                "raw": f"ERROR: {e}",
                "json": {},
                "image_path": None,
                "meta": meta_obj
            })
            json_list.append({})

    # 결과 병합
    merged, diag = _merge_envelope_json(json_list)

    # ⭐⭐⭐ DB 저장 로직 ⭐⭐⭐
    saved_medicines = []
    saved_count = 0
    
    # 사용자 가져오기 (TODO: 실제로는 request.user 사용)
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(username='guest', password='guest123')
    
    # 처방 정보
    pharmacy_name = merged.get('pharmacy_name', '').strip()
    hospital_name = merged.get('hospital_name', '').strip()
    prescription_date = _parse_date(merged.get('dispense_date', ''))
    
    # ⭐ medicines 배열에서 각 약마다 처리
    medicines_list = merged.get('medicines', [])
    
    if not medicines_list:
        return JsonResponse({
            "error": "no_medicines_found",
            "message": "약 정보를 찾을 수 없습니다.",
            "analysis_type": "envelope",
            "shots": shots_raw,
            "merged": merged,
            "diagnostics": diag
        }, status=200)
    
    for med_info in medicines_list:
        medicine_name = med_info.get('medicine_name', '').strip()
        dosage = med_info.get('dosage_instructions', '').strip()
        frequency = med_info.get('frequency', '').strip()
        
        if not medicine_name:
            continue
        
        # DB에서 약 검색
        medicines = _find_medicine_in_db(medicine_name)
        
        if not medicines:
            # DB에 없는 약
            saved_medicines.append({
                'medicine_name': medicine_name,
                'found_in_db': False,
                'message': 'DB에서 약을 찾을 수 없습니다.'
            })
            continue
        
        # 찾은 약마다 UserMedication에 저장
        for medicine in medicines:
            user_med, created = UserMedication.objects.get_or_create(
                user=user,
                medicine=medicine,
                defaults={
                    'dosage': dosage,
                    'frequency': frequency,
                    'pharmacy_name': pharmacy_name,
                    'hospital_name': hospital_name,
                    'prescription_date': prescription_date if prescription_date else None,
                }
            )
            
            if created:
                saved_count += 1
                saved_medicines.append({
                    'medicine_id': medicine.item_seq,
                    'medicine_name': medicine.item_name,
                    'entp_name': medicine.entp_name,
                    'found_in_db': True,
                    'created': True,
                    'dosage': dosage,
                    'frequency': frequency
                })
            else:
                # 이미 있으면 정보 업데이트
                updated_fields = []
                if dosage and dosage != user_med.dosage:
                    user_med.dosage = dosage
                    updated_fields.append('dosage')
                if frequency and frequency != user_med.frequency:
                    user_med.frequency = frequency
                    updated_fields.append('frequency')
                if pharmacy_name and pharmacy_name != user_med.pharmacy_name:
                    user_med.pharmacy_name = pharmacy_name
                    updated_fields.append('pharmacy_name')
                if prescription_date and prescription_date != str(user_med.prescription_date or ''):
                    user_med.prescription_date = prescription_date
                    updated_fields.append('prescription_date')
                
                if updated_fields:
                    user_med.save()
                
                saved_medicines.append({
                    'medicine_id': medicine.item_seq,
                    'medicine_name': medicine.item_name,
                    'entp_name': medicine.entp_name,
                    'found_in_db': True,
                    'created': False,
                    'updated': True,
                    'updated_fields': updated_fields
                })

    # 결과 반환
    out = {
        "analysis_type": "envelope",
        "shots": shots_raw,
        "merged": merged,
        "diagnostics": diag,
        "saved_to_db": saved_count > 0,
        "saved_count": saved_count,
        "saved_medicines": saved_medicines,
        "total_medicines_detected": len(medicines_list)
    }
    
    return JsonResponse(out, status=200)

def delete_medication(request, medication_id):
    from medicines.models import UserMedication
    user = User.objects.first()  # TODO: request.user
    
    medication = UserMedication.objects.get(id=medication_id, user=user)
    medication.delete()
    
    return redirect('/meds/')

def medication_detail(request, medication_id):
    medication = get_object_or_404(
        UserMedication.objects.select_related('medicine', 'medicine__pill_info'),
        id=medication_id,
        user=request.user
    )
    return render(request, 'carepill/medication_detail.html', {
        'medication': medication
    })