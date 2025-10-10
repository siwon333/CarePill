"""
CarePill Voice Assistant Prototype
Complete flow: Wake Word → STT → Intent Classification → Response → TTS
"""

import os
import sys
import json
import struct
import pyaudio
import pvporcupine
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

class Config:
    # Porcupine (Wake Word)
    PORCUPINE_ACCESS_KEY = os.getenv('PORCUPINE_ACCESS_KEY')
    PORCUPINE_MODEL_PATH = os.getenv('PORCUPINE_MODEL_PATH')
    WAKE_WORD_MODEL_PATH = os.getenv('WAKE_WORD_MODEL_PATH')

    # Naver Clova (STT only)
    NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
    NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Django TTS API
    DJANGO_TTS_URL = os.getenv('DJANGO_TTS_URL', 'http://localhost:8000')
    DJANGO_TTS_TOKEN = os.getenv('DJANGO_TTS_TOKEN', '')

    # Audio settings
    SAMPLE_RATE = 16000
    RECORD_SECONDS = 3  # STT recording duration after wake word

# ============================================================================
# 1. Wake Word Detection
# ============================================================================

def detect_wake_word():
    """Detect 'carepill' wake word"""
    print("\n[WAKE WORD] Listening for 'carepill' (케어필)...")

    porcupine = pvporcupine.create(
        access_key=Config.PORCUPINE_ACCESS_KEY,
        keyword_paths=[Config.WAKE_WORD_MODEL_PATH],
        model_path=Config.PORCUPINE_MODEL_PATH,
        sensitivities=[0.7]
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print("[DETECTED] Wake word detected!")
                break

    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        porcupine.delete()
        pa.terminate()

# ============================================================================
# 2. Speech-to-Text (STT)
# ============================================================================

def record_audio(duration=5):
    """Record audio from microphone"""
    print(f"[RECORDING] Speak now! ({duration} seconds)...")

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=Config.SAMPLE_RATE,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=1024
    )

    frames = []
    for _ in range(0, int(Config.SAMPLE_RATE / 1024 * duration)):
        data = stream.read(1024, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    pa.terminate()

    # Save to file
    import wave
    audio_file = "temp_recording.wav"
    wf = wave.open(audio_file, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(Config.SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("[RECORDED] Audio saved")
    return audio_file

def speech_to_text(audio_file):
    """Convert speech to text using Naver Clova STT"""
    print("[STT] Converting speech to text...")

    url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor"

    headers = {
        "X-NCP-APIGW-API-KEY-ID": Config.NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": Config.NAVER_CLIENT_SECRET,
        "Content-Type": "application/octet-stream"
    }

    with open(audio_file, 'rb') as f:
        response = requests.post(url, headers=headers, data=f)

    if response.status_code == 200:
        result = response.json()
        text = result.get('text', '')
        print(f"[STT RESULT] '{text}'")
        return text
    else:
        print(f"[STT ERROR] {response.status_code}: {response.text}")
        return None

# ============================================================================
# 3. Intent Classification & Processing
# ============================================================================

def classify_intent(user_text):
    """Classify user intent using OpenAI"""
    print("[INTENT] Classifying user intent...")

    client = OpenAI(api_key=Config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """당신은 음성 명령 의도 분류기입니다.
                사용자 명령을 분석하고 다음 JSON 형식으로만 답변하세요:
                {
                    "intent": "get_medicine|list_medicine|ask_time|ask_dosage|unknown",
                    "time_slot": "morning|lunch|evening|all",
                    "medicine_name": "약 이름 (있다면)",
                    "confidence": 0.0-1.0
                }

                Intent 설명:
                - get_medicine: 약 가져오기/복용 요청 (예: "아침약 줘", "약 먹을 시간")
                - list_medicine: 약 목록 조회 (예: "아침약 뭐 있어?", "어떤 약 먹어?")
                - ask_time: 복용 시간 질문 (예: "아침약 언제 먹어?", "몇 시에 먹어?")
                - ask_dosage: 복용량 질문 (예: "아침약 몇 알?", "얼마나 먹어?")
                - unknown: 알 수 없는 명령
                """
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        temperature=0.1,
        max_tokens=200
    )

    result_text = response.choices[0].message.content

    # Parse JSON
    try:
        # Remove code block markers if present
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.replace('```', '').strip()

        intent_data = json.loads(result_text)
        print(f"[INTENT RESULT] {intent_data}")
        return intent_data
    except json.JSONDecodeError as e:
        print(f"[INTENT ERROR] JSON parsing failed: {e}")
        print(f"Raw response: {result_text}")
        return {"intent": "unknown", "time_slot": "all", "confidence": 0.0}

def process_intent(intent_data):
    """Process intent and get database info (mock for prototype)"""
    print("[PROCESSING] Getting medicine data...")

    # Mock database (실제로는 Django ORM 사용)
    mock_db = {
        "morning": [
            {"name": "타이레놀", "dosage": "1알", "time": "오전 8시"},
            {"name": "비타민C", "dosage": "1알", "time": "오전 8시"}
        ],
        "lunch": [
            {"name": "소화제", "dosage": "1알", "time": "점심 12시"}
        ],
        "evening": [
            {"name": "혈압약", "dosage": "1알", "time": "저녁 7시"},
            {"name": "비타민D", "dosage": "1알", "time": "저녁 7시"}
        ]
    }

    intent = intent_data.get("intent")
    time_slot = intent_data.get("time_slot", "all")

    # Get relevant data
    if time_slot == "all":
        data = mock_db
    else:
        data = {time_slot: mock_db.get(time_slot, [])}

    return {"intent": intent, "data": data}

# ============================================================================
# 4. Response Generation
# ============================================================================

def generate_response(intent, data):
    """Generate natural language response using OpenAI"""
    print("[RESPONSE] Generating response...")

    client = OpenAI(api_key=Config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """당신은 친절한 약 복용 도우미입니다.
                사용자의 의도와 약 정보를 바탕으로 자연스럽고 간결한 답변을 생성하세요.

                규칙:
                - 1-2 문장으로 간결하게
                - 존댓말 사용
                - 약 이름, 개수, 시간 명확히 전달
                - TTS로 음성 출력될 것을 고려
                """
            },
            {
                "role": "user",
                "content": f"의도: {intent}\n약 정보: {json.dumps(data, ensure_ascii=False)}\n\n위 정보로 답변 생성:"
            }
        ],
        temperature=0.7,
        max_tokens=100
    )

    response_text = response.choices[0].message.content.strip()
    print(f"[RESPONSE] '{response_text}'")
    return response_text

# ============================================================================
# 5. Text-to-Speech (TTS) - Django API with Custom Voice
# ============================================================================

def text_to_speech(text):
    """Convert text to speech using Django TTS API with custom voice"""
    print("[TTS] Converting text to speech (custom voice)...")

    # Django TTS API endpoint
    api_url = f"{Config.DJANGO_TTS_URL}/api/tts/generate/"

    headers = {
        "Authorization": f"Token {Config.DJANGO_TTS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "use_cache": True,  # Enable caching for faster responses
        "language": "ko"
    }

    try:
        # Call Django TTS API
        response = requests.post(api_url, json=data, headers=headers)

        if response.status_code == 200:
            result = response.json()

            if result.get('success'):
                # Get audio file URL
                audio_url = f"{Config.DJANGO_TTS_URL}{result['audio_url']}"

                # Download audio file
                audio_response = requests.get(audio_url)

                if audio_response.status_code == 200:
                    audio_file = "response_audio.wav"
                    with open(audio_file, "wb") as f:
                        f.write(audio_response.content)

                    cache_status = "CACHED" if result.get('cache_hit') else "GENERATED"
                    print(f"[TTS] Audio saved to {audio_file} ({cache_status})")
                    print(f"[TTS] Processing time: {result.get('processing_time_ms', 0):.0f}ms")

                    # Play audio (Windows)
                    import subprocess
                    subprocess.run(["start", audio_file], shell=True)
                    return True
                else:
                    print(f"[TTS ERROR] Failed to download audio: {audio_response.status_code}")
                    return text_to_speech_fallback(text)
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"[TTS ERROR] API error: {error_msg}")
                return text_to_speech_fallback(text)
        else:
            print(f"[TTS ERROR] API request failed: {response.status_code}")
            return text_to_speech_fallback(text)

    except Exception as e:
        print(f"[TTS ERROR] Exception: {e}")
        return text_to_speech_fallback(text)


def text_to_speech_fallback(text):
    """Fallback to Naver TTS if Django API fails"""
    print("[TTS] Falling back to Naver TTS...")

    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

    headers = {
        "X-NCP-APIGW-API-KEY-ID": Config.NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": Config.NAVER_CLIENT_SECRET,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "speaker": "nara",
        "volume": "0",
        "speed": "0",
        "pitch": "0",
        "format": "mp3",
        "text": text
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        audio_file = "response_audio.mp3"
        with open(audio_file, "wb") as f:
            f.write(response.content)
        print(f"[TTS] Fallback audio saved to {audio_file}")

        # Play audio (Windows)
        import subprocess
        subprocess.run(["start", audio_file], shell=True)
        return True
    else:
        print(f"[TTS ERROR] Fallback also failed: {response.status_code}")
        return False

# ============================================================================
# Main Pipeline
# ============================================================================

def main():
    """Main voice assistant pipeline"""
    print("="*60)
    print("CarePill Voice Assistant Prototype")
    print("="*60)
    print("\nFlow: Wake Word → STT → Intent → Response → TTS")
    print("\nPress Ctrl+C to stop\n")

    try:
        while True:
            # 1. Wait for wake word
            detect_wake_word()

            # 2. Record user speech
            audio_file = record_audio(duration=Config.RECORD_SECONDS)

            # 3. Convert to text
            user_text = speech_to_text(audio_file)

            if not user_text:
                print("[ERROR] No speech detected, try again...")
                continue

            # 4. Classify intent
            intent_data = classify_intent(user_text)

            # 5. Process intent and get data
            result = process_intent(intent_data)

            # 6. Generate response
            response_text = generate_response(
                intent=result["intent"],
                data=result["data"]
            )

            # 7. Convert to speech and play
            text_to_speech(response_text)

            print("\n" + "="*60)
            print("Waiting for next wake word...")
            print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\n[STOPPED] Voice assistant stopped")

        # Cleanup
        for temp_file in ["temp_recording.wav", "response_audio.mp3", "response_audio.wav"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        print("[CLEANUP] Temporary files removed")

if __name__ == "__main__":
    # Verify configuration
    if not all([
        Config.PORCUPINE_ACCESS_KEY,
        Config.NAVER_CLIENT_ID,
        Config.OPENAI_API_KEY
    ]):
        print("[ERROR] Missing API keys in .env file!")
        sys.exit(1)

    main()
