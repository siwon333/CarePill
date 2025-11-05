from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("scan/", views.scan, name="scan"),
    path("scan_choice/", views.scan_choice, name="scan_choice"),
    path("meds/", views.meds, name="meds"),
    path("voice/", views.voice, name="voice"),
    path("how2prescription/", views.how2prescription, name="how2prescription"),
    path("how2otc/", views.how2otc, name="how2otc"),

    path("meds_hos/", views.meds_hos, name="meds_hos"),
    path("meds_hos2/", views.meds_hos2, name="meds_hos2"),
    path("how2green/", views.how2green, name="how2green"),
    path("how2green_result/", views.how2green_result, name="how2green_result"),
    path("stt_test/", views.stt_test, name="stt_test"),

    # WebRTC용 에페메럴 세션 토큰 발급 (클라 직결)
    path("api/realtime/session/", views.issue_ephemeral, name="rt_ephemeral"),
    path("api/realtime/sdp-exchange/", views.realtime_sdp_exchange, name="rt_sdp_exchange"),


    path("api/conversation/summarize_and_save/", views.api_conversation_summarize_and_save, name="api_conversation_summarize_and_save"),
    path("api/conversation/download/", views.api_conversation_download),

    path("api/scan/envelope/", views.api_scan_envelope, name="api_scan_envelope"),

    # ElevenLabs 음성 관련 API
    path("voice_setup/", views.voice_setup, name="voice_setup"),
    path("api/voice/upload/", views.api_voice_upload, name="api_voice_upload"),
    path("api/tts/", views.api_text_to_speech, name="api_text_to_speech"),
]





