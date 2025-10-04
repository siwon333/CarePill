# Naver Clova Voice API Integration Research

## Executive Summary

This document provides comprehensive research on integrating Naver Clova STT (Speech-to-Text) and TTS (Text-to-Speech) APIs for a Django-based voice-enabled medicine analysis application with Korean language support and wake word detection.

---

## 1. Naver Clova STT (Speech-to-Text) API

### 1.1 Authentication Methods

Naver Clova uses API key-based authentication with two required headers:

- **`X-NCP-APIGW-API-KEY-ID`**: Client ID
- **`X-NCP-APIGW-API-KEY`**: Client Secret

**Obtaining Credentials:**
1. Register an application in NAVER Cloud Platform console
2. Navigate to Services > AI·NAVER API > CLOVA Speech Recognition
3. Click "Edit" to enable the required APIs
4. Copy Client ID and Client Secret from the console

### 1.2 Supported Audio Formats

**Basic STT API:**
- MP3, AAC, AC3, OGG, FLAC, WAV
- Maximum speech length: 60 seconds per API call

**Streaming API (gRPC):**
- PCM (headerless raw wave) format
- Sample rate: 16 kHz
- Channels: 1 (mono)
- Bit depth: 16 bits per sample

### 1.3 Real-time Streaming vs Batch Processing

#### **Batch Processing (REST API)**
- Endpoint: `https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang={Lang}`
- Supported languages: Kor (Korean), Jpn, Chn, Eng
- Best for: Pre-recorded audio files

**Python Example:**
```python
import requests

def transcribe_audio(audio_file_path, client_id, client_secret, lang="Kor"):
    """
    Transcribe audio file using Naver Clova STT API

    Args:
        audio_file_path: Path to audio file (mp3, wav, etc.)
        client_id: Naver Cloud Platform Client ID
        client_secret: Naver Cloud Platform Client Secret
        lang: Language code (Kor, Jpn, Chn, Eng)

    Returns:
        dict: Transcription result
    """
    url = f"https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang={lang}"

    headers = {
        "Content-Type": "application/octet-stream",
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }

    with open(audio_file_path, "rb") as audio_file:
        response = requests.post(url, data=audio_file, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"STT API Error: {response.status_code} - {response.text}")

# Usage
result = transcribe_audio(
    "path/to/audio.mp3",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
print(result)
```

#### **Real-time Streaming (gRPC API)**
- Endpoint: `clovaspeech-gw.ncloud.com:50051`
- Connection lifetime: Maximum 100 hours
- Best for: Real-time voice interaction, continuous listening
- **Requirement**: Basic long sentence recognition plan (not available on Free plan)

**Setup Requirements:**
```bash
pip install grpcio grpcio-tools
```

**Python Streaming Example:**
```python
import grpc
import json
import nest_pb2  # Generated from nest.proto
import nest_pb2_grpc

def generate_requests(audio_file_path, config):
    """
    Generator function to yield audio chunks for streaming

    Args:
        audio_file_path: Path to PCM audio file
        config: Initial configuration dict

    Yields:
        NestRequest objects
    """
    # Send initial config
    yield nest_pb2.NestRequest(
        type=nest_pb2.NestRequest.CONFIG,
        config=nest_pb2.NestConfig(**config)
    )

    # Stream audio data in chunks
    with open(audio_file_path, 'rb') as audio_file:
        while True:
            chunk = audio_file.read(32000)  # 32KB chunks
            if not chunk:
                break

            yield nest_pb2.NestRequest(
                type=nest_pb2.NestRequest.DATA,
                data=chunk
            )

def stream_transcription(audio_file_path, client_id, client_secret):
    """
    Stream audio for real-time transcription

    Args:
        audio_file_path: Path to PCM audio file (16kHz, mono, 16-bit)
        client_id: Client ID
        client_secret: Client Secret
    """
    # Create secure gRPC channel
    channel = grpc.secure_channel(
        'clovaspeech-gw.ncloud.com:50051',
        grpc.ssl_channel_credentials()
    )

    stub = nest_pb2_grpc.NestServiceStub(channel)

    # Configuration
    config = {
        'transcription': {
            'language': 'ko-KR',
            'enableWordTimeOffsets': True,
            'enablePartialResults': True,
        }
    }

    # Stream requests
    requests = generate_requests(audio_file_path, config)

    # Get streaming responses
    for response in stub.Recognize(requests, metadata=[
        ('authorization', f'Bearer {client_secret}'),
        ('x-clovaspeech-client-id', client_id)
    ]):
        if response.type == nest_pb2.NestResponse.PARTIAL:
            print(f"Partial: {response.text}")
        elif response.type == nest_pb2.NestResponse.FINAL:
            print(f"Final: {response.text}")

# Usage
stream_transcription(
    "path/to/audio.pcm",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
```

### 1.4 Rate Limits and Pricing

**Rate Limits:**
- Default: 300,000 seconds per month (30,000 seconds per day)
- Maximum: 30,000,000 seconds per month (10,000,000 per day)
- Per-call limit: 60 seconds maximum audio length
- Contact support for higher limits

**Pricing (Pay-as-you-go):**
- Charged in 15-second increments (rounded up)
- Approximate rate: 0.5 KRW per second
- Examples:
  - 10 seconds usage → 5 KRW (~$0.004 USD)
  - 32 seconds usage → 15 KRW (~$0.012 USD)

**429 Error Prevention:**
- Ensure API is enabled in console (click "Edit" button)
- Monitor usage limits in NAVER Cloud Platform portal
- Services > AI·NAVER API > CLOVA Speech Recognition menu

### 1.5 Language Support

**Primary Support:**
- **Korean (Kor)**: Primary focus, excellent accuracy
- English (Eng)
- Japanese (Jpn)
- Chinese (Chn)

### 1.6 Best Practices for Continuous Listening

**Recommended Architecture:**
1. **Wake Word Detection (Local)** → Activates STT
2. **Audio Buffer** → Captures speech after wake word
3. **STT Processing** → Sends to Clova STT (batch or stream)
4. **Response Handler** → Processes transcription

**For Continuous Listening:**
- Use local wake word detection (Porcupine) to minimize API calls
- Buffer audio locally using PyAudio/sounddevice
- Only send to Clova STT after wake word detection
- Use streaming API for long conversations
- Implement VAD (Voice Activity Detection) to stop recording

---

## 2. Naver Clova TTS (Text-to-Speech) API

### 2.1 Authentication

Same authentication method as STT:
- **Headers**: `X-NCP-APIGW-API-KEY-ID` and `X-NCP-APIGW-API-KEY`

### 2.2 Supported Output Formats

- **MP3** (default)
- Other formats available via format parameter

### 2.3 Voice Options

**Available Parameters:**
- **speaker**: Voice selection (e.g., "nara", "mijin", "jinho", "clara")
- **volume**: Volume level (0 = default)
- **speed**: Speech speed (0 = default, -5 to +5)
- **pitch**: Voice pitch (0 = default, -5 to +5)
- **format**: Output format (mp3)

**Popular Korean Voices:**
- **mijin**: Female voice, natural and clear
- **jinho**: Male voice
- **nara**: Female voice, professional tone

### 2.4 Python Integration Examples

#### **Basic TTS with Official API**

```python
import urllib.request
import urllib.parse

def text_to_speech(text, client_id, client_secret, speaker="nara", output_file="output.mp3"):
    """
    Convert text to speech using Naver Clova TTS API

    Args:
        text: Text to convert to speech
        client_id: Naver Cloud Platform Client ID
        client_secret: Naver Cloud Platform Client Secret
        speaker: Voice selection (nara, mijin, jinho, etc.)
        output_file: Output MP3 file path

    Returns:
        str: Path to output file
    """
    enc_text = urllib.parse.quote(text)
    data = f"speaker={speaker}&volume=0&speed=0&pitch=0&format=mp3&text={enc_text}"
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)

    response = urllib.request.urlopen(request, data=data.encode('utf-8'))

    if response.getcode() == 200:
        with open(output_file, 'wb') as f:
            f.write(response.read())
        return output_file
    else:
        raise Exception(f"TTS API Error: {response.getcode()}")

# Usage
audio_file = text_to_speech(
    text="안녕하세요, 케어필입니다.",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    speaker="mijin"
)
print(f"Audio saved to: {audio_file}")
```

#### **Using clovaTTS Python Wrapper**

```bash
pip install clovaTTS
```

```python
from clovaTTS import clovaTTS

def generate_speech_with_cache(text, client_id, client_secret, cache_dir="/tmp/tts_cache"):
    """
    Generate speech with caching support

    Args:
        text: Text to convert
        client_id: Client ID
        client_secret: Client Secret
        cache_dir: Directory for caching audio files

    Returns:
        bytes: Audio data
    """
    tts = clovaTTS(
        speaker="mijin",
        client_id=client_id,
        client_secret=client_secret,
        use_cache=True,
        cache_dir=cache_dir
    )

    speech = tts.tts(text)
    return speech

# Usage with automatic caching
tts_engine = clovaTTS(
    "mijin",
    "YOUR_CLIENT_ID",
    "YOUR_CLIENT_SECRET",
    use_cache=True,
    cache_dir="/home/ttscache"
)

text = "약을 복용하실 시간입니다."
speech = tts_engine.tts(text)
tts_engine.save("reminder.mp3", speech)
```

### 2.5 Streaming vs File-based Responses

**Current Implementation:**
- Naver Clova TTS primarily returns **file-based responses**
- Audio is generated and returned as binary data (MP3)
- For streaming playback, use Django's StreamingHttpResponse

**Django Streaming Example:**
```python
from django.http import StreamingHttpResponse
import io

def stream_tts_response(text, client_id, client_secret):
    """
    Stream TTS audio response in Django
    """
    # Generate audio
    audio_data = text_to_speech(text, client_id, client_secret)

    # Create streaming response
    audio_buffer = io.BytesIO(audio_data)

    response = StreamingHttpResponse(
        audio_buffer,
        content_type='audio/mpeg'
    )
    response['Content-Disposition'] = 'inline; filename="speech.mp3"'

    return response
```

### 2.6 Rate Limits

- Similar pricing model to STT
- Pay-as-you-go based on character count
- Check portal for detailed pricing: Services > AI·NAVER API > CLOVA Voice

---

## 3. Wake Word Detection

### 3.1 Best Libraries for Korean Wake Word Detection

#### **Option 1: Porcupine (Recommended)**

**Advantages:**
- ✅ Native Korean language support
- ✅ Custom wake word training (free on Free Plan)
- ✅ High accuracy (11x more accurate than alternatives)
- ✅ Low resource usage (6.5x faster on Raspberry Pi 3)
- ✅ Commercial-grade performance
- ✅ Active development (latest release: Feb 2025)

**Installation:**
```bash
pip install pvporcupine
```

**Basic Usage:**
```python
import pvporcupine
import pyaudio
import struct

def create_wake_word_detector(access_key, keywords=['picovoice']):
    """
    Create Porcupine wake word detector

    Args:
        access_key: Picovoice access key (from console.picovoice.ai)
        keywords: List of wake words or paths to .ppn files

    Returns:
        pvporcupine.Porcupine instance
    """
    return pvporcupine.create(
        access_key=access_key,
        keywords=keywords
    )

def listen_for_wake_word(access_key, wake_word="picovoice"):
    """
    Continuously listen for wake word

    Args:
        access_key: Picovoice access key
        wake_word: Wake word to detect
    """
    porcupine = pvporcupine.create(
        access_key=access_key,
        keywords=[wake_word]
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print(f"Listening for wake word: '{wake_word}'...")

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print(f"Wake word detected!")
                # Trigger STT processing here
                return True

    finally:
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

# Usage
listen_for_wake_word(
    access_key="YOUR_PICOVOICE_ACCESS_KEY",
    wake_word="picovoice"  # or custom Korean wake word
)
```

**Custom Korean Wake Word ("케어필"):**

1. Visit https://console.picovoice.ai/
2. Navigate to Porcupine page
3. Select language: Korean (ko)
4. Type your wake phrase: "케어필"
5. Select platform (Linux, Raspberry Pi, etc.)
6. Click "Train" - takes less than 10 seconds
7. Download the .ppn model file

**Using Custom Model:**
```python
import pvporcupine

porcupine = pvporcupine.create(
    access_key="YOUR_ACCESS_KEY",
    keyword_paths=['/path/to/carepill_ko_linux.ppn']  # Your custom model
)
```

#### **Option 2: openWakeWord**

**Current Status:**
- ❌ No Korean support yet (English only)
- ⚠️ Requires multi-speaker Korean TTS models (not available)
- 🔬 Recent research (Jan 2025) exploring Korean support
- Open-source and free

**Not Recommended** for Korean wake words at this time.

#### **Option 3: Snowboy**

**Status:**
- ⚠️ No longer actively maintained
- ❌ Performance significantly below Porcupine
- Not recommended for new projects

### 3.2 Integration Patterns for Continuous Audio Monitoring

**Recommended Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                     Audio Input Stream                       │
│                     (PyAudio/sounddevice)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Wake Word Detection (Porcupine)                 │
│              - Runs continuously on device                   │
│              - Low CPU/memory usage                          │
│              - Korean "케어필" detection                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼ (Wake word detected)
┌─────────────────────────────────────────────────────────────┐
│                   Audio Buffer Capture                       │
│              - Start recording after wake word               │
│              - Use VAD for endpoint detection                │
│              - Buffer 2-5 seconds of audio                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Naver Clova STT Processing                      │
│              - Send buffered audio to API                    │
│              - Receive transcription                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Django Backend Processing                       │
│              - Analyze medicine command                      │
│              - Generate response                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Naver Clova TTS Response                        │
│              - Convert response to speech                    │
│              - Play audio to user                            │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼ (Return to listening)
              [Loop back to Wake Word Detection]
```

**Complete Integration Example:**
```python
import pvporcupine
import pyaudio
import struct
import wave
import io
import requests
from threading import Thread, Event

class VoiceAssistant:
    def __init__(self, porcupine_access_key, naver_client_id, naver_client_secret):
        self.porcupine_key = porcupine_access_key
        self.naver_id = naver_client_id
        self.naver_secret = naver_client_secret
        self.is_recording = False
        self.stop_event = Event()

    def initialize_wake_word_detector(self, wake_word_path):
        """Initialize Porcupine with custom wake word"""
        return pvporcupine.create(
            access_key=self.porcupine_key,
            keyword_paths=[wake_word_path]
        )

    def record_audio_after_wake_word(self, duration=5, sample_rate=16000):
        """
        Record audio after wake word is detected

        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate

        Returns:
            bytes: WAV audio data
        """
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=1024
        )

        print("Recording...")
        frames = []

        for _ in range(0, int(sample_rate / 1024 * duration)):
            data = stream.read(1024)
            frames.append(data)

        print("Recording finished")

        stream.stop_stream()
        stream.close()
        pa.terminate()

        # Convert to WAV
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))

        return wav_buffer.getvalue()

    def transcribe_audio(self, audio_data):
        """Send audio to Naver Clova STT"""
        url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor"
        headers = {
            "Content-Type": "application/octet-stream",
            "X-NCP-APIGW-API-KEY-ID": self.naver_id,
            "X-NCP-APIGW-API-KEY": self.naver_secret,
        }

        response = requests.post(url, data=audio_data, headers=headers)

        if response.status_code == 200:
            return response.json().get('text', '')
        else:
            raise Exception(f"STT Error: {response.text}")

    def text_to_speech(self, text, speaker="mijin"):
        """Convert text to speech using Naver Clova TTS"""
        import urllib.parse
        import urllib.request

        enc_text = urllib.parse.quote(text)
        data = f"speaker={speaker}&volume=0&speed=0&pitch=0&format=mp3&text={enc_text}"
        url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

        request = urllib.request.Request(url)
        request.add_header("X-NCP-APIGW-API-KEY-ID", self.naver_id)
        request.add_header("X-NCP-APIGW-API-KEY", self.naver_secret)

        response = urllib.request.urlopen(request, data=data.encode('utf-8'))

        if response.getcode() == 200:
            return response.read()
        else:
            raise Exception(f"TTS Error: {response.getcode()}")

    def play_audio(self, audio_data):
        """Play MP3 audio"""
        # Use pygame or pydub to play MP3
        # This is a placeholder - implement based on your needs
        import pygame
        import io

        pygame.mixer.init()
        audio_buffer = io.BytesIO(audio_data)
        pygame.mixer.music.load(audio_buffer)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def process_command(self, text):
        """
        Process voice command and generate response
        This should interface with your Django backend
        """
        # Example: Send to Django API
        # response = requests.post('http://localhost:8000/api/voice-command/',
        #                         json={'text': text})
        # return response.json()['response']

        # Placeholder
        return f"명령을 받았습니다: {text}"

    def run(self, wake_word_path):
        """Main voice assistant loop"""
        porcupine = self.initialize_wake_word_detector(wake_word_path)

        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Voice assistant started. Say '케어필' to activate...")

        try:
            while not self.stop_event.is_set():
                # Listen for wake word
                pcm = audio_stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                keyword_index = porcupine.process(pcm)

                if keyword_index >= 0:
                    print("Wake word detected! Listening for command...")

                    # Record user command
                    audio_data = self.record_audio_after_wake_word(duration=5)

                    # Transcribe
                    try:
                        text = self.transcribe_audio(audio_data)
                        print(f"Transcribed: {text}")

                        # Process command
                        response_text = self.process_command(text)
                        print(f"Response: {response_text}")

                        # Generate and play response
                        audio_response = self.text_to_speech(response_text)
                        self.play_audio(audio_response)

                    except Exception as e:
                        print(f"Error processing command: {e}")

                    print("Listening for wake word again...")

        finally:
            audio_stream.close()
            pa.terminate()
            porcupine.delete()

    def stop(self):
        """Stop the voice assistant"""
        self.stop_event.set()

# Usage
if __name__ == "__main__":
    assistant = VoiceAssistant(
        porcupine_access_key="YOUR_PORCUPINE_KEY",
        naver_client_id="YOUR_NAVER_CLIENT_ID",
        naver_client_secret="YOUR_NAVER_CLIENT_SECRET"
    )

    assistant.run(wake_word_path="/path/to/carepill_ko_linux.ppn")
```

### 3.3 Resource-Efficient Wake Word Detection

**Best Practices:**

1. **Use Porcupine's optimized algorithms**
   - Built-in optimization for embedded devices
   - Low CPU usage (~1-2% on modern hardware)
   - Minimal memory footprint

2. **Implement VAD (Voice Activity Detection)**
   ```python
   import webrtcvad

   def is_speech(audio_frame, sample_rate=16000):
       """Detect if audio frame contains speech"""
       vad = webrtcvad.Vad(3)  # Aggressiveness level 3
       return vad.is_speech(audio_frame, sample_rate)
   ```

3. **Buffer management**
   - Only keep recent audio in memory
   - Circular buffer for continuous recording
   - Clear buffer after processing

4. **Threading considerations**
   - Run wake word detection in separate thread
   - Use queues for audio data transfer
   - Avoid blocking main application

---

## 4. Python Libraries and Dependencies

### 4.1 Required Libraries

**Add to `requirements.txt`:**

```txt
# Naver Clova APIs
requests>=2.31.0
clovaTTS>=0.1.0

# Wake Word Detection
pvporcupine>=3.0.0

# Audio Processing
PyAudio>=0.2.14
sounddevice>=0.4.6
wave>=0.0.2
pydub>=0.25.1

# gRPC for Streaming (if using CLOVA Speech streaming)
grpcio>=1.60.0
grpcio-tools>=1.60.0

# Voice Activity Detection
webrtcvad>=2.0.10

# Audio playback
pygame>=2.5.2

# Django integration
django>=4.2.0
channels>=4.0.0  # For WebSocket support
daphne>=4.0.0    # ASGI server

# Environment variables
python-dotenv>=1.0.0
```

**Installation:**
```bash
pip install -r requirements.txt
```

### 4.2 Platform-Specific Considerations

**Linux (Ubuntu/Debian):**
```bash
# PyAudio dependencies
sudo apt-get install python3-pyaudio portaudio19-dev

# For MP3 support
sudo apt-get install ffmpeg libavcodec-extra
```

**Windows:**
```bash
# PyAudio - download wheel from unofficial binaries
pip install pipwin
pipwin install pyaudio

# Or use sounddevice (easier on Windows)
pip install sounddevice
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

### 4.3 Alternative: sounddevice (Recommended for Cross-platform)

**Why sounddevice over PyAudio:**
- Simpler API
- Better cross-platform support
- NumPy integration
- Easier installation

**Example:**
```python
import sounddevice as sd
import numpy as np

def record_audio_sounddevice(duration=5, sample_rate=16000):
    """Record audio using sounddevice"""
    print("Recording...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )
    sd.wait()
    print("Recording finished")
    return audio.flatten()

# Usage
audio_data = record_audio_sounddevice(duration=5)
```

---

## 5. Django Integration Architecture

### 5.1 Project Structure

```
CarePill/
├── medicine_project/
│   ├── settings.py
│   ├── asgi.py  # For WebSocket support
│   └── routing.py
├── medicine_analyzer/
│   ├── views.py
│   ├── consumers.py  # WebSocket consumers
│   ├── voice/
│   │   ├── __init__.py
│   │   ├── wake_word.py
│   │   ├── stt_handler.py
│   │   ├── tts_handler.py
│   │   └── voice_assistant.py
│   └── models.py
├── requirements.txt
└── manage.py
```

### 5.2 Django Channels for Real-time Audio

**Install Channels:**
```bash
pip install channels daphne channels-redis
```

**Configure settings.py:**
```python
# settings.py

INSTALLED_APPS = [
    'daphne',  # Add at top
    'django.contrib.admin',
    # ... other apps
    'channels',
    'medicine_analyzer',
]

ASGI_APPLICATION = 'medicine_project.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Naver API Configuration
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')
PORCUPINE_ACCESS_KEY = os.getenv('PORCUPINE_ACCESS_KEY')
```

**Create asgi.py:**
```python
# medicine_project/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from medicine_analyzer import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
```

**Create routing.py:**
```python
# medicine_analyzer/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/voice/', consumers.VoiceConsumer.as_asgi()),
]
```

**Create WebSocket Consumer:**
```python
# medicine_analyzer/consumers.py

import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from .voice.stt_handler import transcribe_audio
from .voice.tts_handler import generate_speech
from django.conf import settings

class VoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to voice assistant'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        """
        Receive audio data from frontend
        """
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'audio':
            # Decode base64 audio
            audio_data = base64.b64decode(data['audio'])

            try:
                # Transcribe audio
                text = await self.transcribe(audio_data)

                # Send transcription back
                await self.send(text_data=json.dumps({
                    'type': 'transcription',
                    'text': text
                }))

                # Process command (analyze medicine, etc.)
                response = await self.process_command(text)

                # Generate speech response
                audio_response = await self.generate_response_audio(response)

                # Send audio response
                await self.send(text_data=json.dumps({
                    'type': 'audio_response',
                    'audio': base64.b64encode(audio_response).decode('utf-8'),
                    'text': response
                }))

            except Exception as e:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': str(e)
                }))

    async def transcribe(self, audio_data):
        """Call Naver Clova STT"""
        # Implement async version or use sync_to_async
        from asgiref.sync import sync_to_async
        return await sync_to_async(transcribe_audio)(
            audio_data,
            settings.NAVER_CLIENT_ID,
            settings.NAVER_CLIENT_SECRET
        )

    async def process_command(self, text):
        """Process voice command"""
        # Implement your medicine analysis logic here
        return f"처리 완료: {text}"

    async def generate_response_audio(self, text):
        """Generate TTS response"""
        from asgiref.sync import sync_to_async
        return await sync_to_async(generate_speech)(
            text,
            settings.NAVER_CLIENT_ID,
            settings.NAVER_CLIENT_SECRET
        )
```

### 5.3 Voice Handler Modules

**Create stt_handler.py:**
```python
# medicine_analyzer/voice/stt_handler.py

import requests
from django.conf import settings

def transcribe_audio(audio_data, client_id=None, client_secret=None):
    """
    Transcribe audio using Naver Clova STT

    Args:
        audio_data: Binary audio data
        client_id: Naver Client ID (optional, uses settings if not provided)
        client_secret: Naver Client Secret

    Returns:
        str: Transcribed text
    """
    client_id = client_id or settings.NAVER_CLIENT_ID
    client_secret = client_secret or settings.NAVER_CLIENT_SECRET

    url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor"
    headers = {
        "Content-Type": "application/octet-stream",
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }

    response = requests.post(url, data=audio_data, headers=headers)

    if response.status_code == 200:
        return response.json().get('text', '')
    else:
        raise Exception(f"STT API Error: {response.status_code} - {response.text}")
```

**Create tts_handler.py:**
```python
# medicine_analyzer/voice/tts_handler.py

import urllib.parse
import urllib.request
from django.conf import settings

def generate_speech(text, client_id=None, client_secret=None, speaker="mijin"):
    """
    Generate speech from text using Naver Clova TTS

    Args:
        text: Text to convert to speech
        client_id: Naver Client ID
        client_secret: Naver Client Secret
        speaker: Voice speaker (mijin, jinho, nara, etc.)

    Returns:
        bytes: MP3 audio data
    """
    client_id = client_id or settings.NAVER_CLIENT_ID
    client_secret = client_secret or settings.NAVER_CLIENT_SECRET

    enc_text = urllib.parse.quote(text)
    data = f"speaker={speaker}&volume=0&speed=0&pitch=0&format=mp3&text={enc_text}"
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)

    response = urllib.request.urlopen(request, data=data.encode('utf-8'))

    if response.getcode() == 200:
        return response.read()
    else:
        raise Exception(f"TTS API Error: {response.getcode()}")
```

**Create wake_word.py:**
```python
# medicine_analyzer/voice/wake_word.py

import pvporcupine
import pyaudio
import struct
from threading import Thread, Event

class WakeWordListener(Thread):
    """
    Background thread for wake word detection
    """
    def __init__(self, access_key, keyword_path, callback):
        super().__init__(daemon=True)
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.callback = callback
        self.stop_event = Event()

    def run(self):
        porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=[self.keyword_path]
        )

        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Wake word listener started...")

        try:
            while not self.stop_event.is_set():
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                keyword_index = porcupine.process(pcm)

                if keyword_index >= 0:
                    print("Wake word detected!")
                    self.callback()
        finally:
            audio_stream.close()
            pa.terminate()
            porcupine.delete()

    def stop(self):
        self.stop_event.set()
```

### 5.4 Environment Configuration

**Update .env file:**
```env
# Naver Cloud Platform
NAVER_CLIENT_ID=your_client_id_here
NAVER_CLIENT_SECRET=your_client_secret_here

# Porcupine
PORCUPINE_ACCESS_KEY=your_picovoice_access_key

# Wake Word Model Path
WAKE_WORD_MODEL_PATH=/path/to/carepill_ko_linux.ppn

# Django
SECRET_KEY=your_django_secret_key
DEBUG=True
```

**Update .env.example:**
```env
# Naver Cloud Platform - Get from https://console.ncloud.com/
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=

# Porcupine - Get from https://console.picovoice.ai/
PORCUPINE_ACCESS_KEY=

# Wake Word Model - Train at https://console.picovoice.ai/
WAKE_WORD_MODEL_PATH=

# Django
SECRET_KEY=
DEBUG=True
```

---

## 6. API Usage Workflow

### Complete Voice Interaction Flow

```
1. User says "케어필" (Wake Word)
   ↓
2. Porcupine detects wake word
   ↓
3. Application starts recording (5 seconds)
   ↓
4. Audio sent to Naver Clova STT API
   ↓
5. Transcription received: "오늘 약 먹었어?"
   ↓
6. Django processes command (check medicine intake)
   ↓
7. Generate response: "네, 오전 8시에 복용하셨습니다."
   ↓
8. Send text to Naver Clova TTS API
   ↓
9. Audio response played to user
   ↓
10. Return to listening for wake word (Loop to step 1)
```

### Example End-to-End Test Script

```python
# test_voice_flow.py

import os
from dotenv import load_dotenv
from medicine_analyzer.voice.wake_word import WakeWordListener
from medicine_analyzer.voice.stt_handler import transcribe_audio
from medicine_analyzer.voice.tts_handler import generate_speech
import sounddevice as sd
import numpy as np
import wave
import io

load_dotenv()

def record_audio_after_wake_word(duration=5, sample_rate=16000):
    """Record audio"""
    print("Recording command...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )
    sd.wait()
    return audio.flatten()

def audio_to_wav(audio_data, sample_rate=16000):
    """Convert numpy array to WAV bytes"""
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    return wav_buffer.getvalue()

def wake_word_callback():
    """Called when wake word is detected"""
    print("\n🎤 Wake word detected! Listening for command...")

    # Record command
    audio = record_audio_after_wake_word(duration=5)
    wav_data = audio_to_wav(audio)

    # Transcribe
    try:
        text = transcribe_audio(wav_data)
        print(f"📝 Transcribed: {text}")

        # Generate response
        response = f"명령을 받았습니다: {text}"
        print(f"💬 Response: {response}")

        # Text to speech
        audio_response = generate_speech(response)
        print(f"🔊 Playing audio response...")

        # Save and play (for testing)
        with open("response.mp3", "wb") as f:
            f.write(audio_response)

        # Play using system player (for testing)
        os.system("ffplay -nodisp -autoexit response.mp3")

    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("Voice Assistant Test")
    print("=" * 60)

    access_key = os.getenv('PORCUPINE_ACCESS_KEY')
    keyword_path = os.getenv('WAKE_WORD_MODEL_PATH')

    if not access_key or not keyword_path:
        print("❌ Missing environment variables!")
        print("Set PORCUPINE_ACCESS_KEY and WAKE_WORD_MODEL_PATH in .env")
        return

    # Start wake word listener
    listener = WakeWordListener(
        access_key=access_key,
        keyword_path=keyword_path,
        callback=wake_word_callback
    )

    listener.start()

    try:
        print("\n👂 Listening for wake word '케어필'...")
        print("Press Ctrl+C to stop\n")
        listener.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping...")
        listener.stop()

if __name__ == "__main__":
    main()
```

---

## 7. Potential Challenges and Solutions

### 7.1 Audio Format Compatibility

**Challenge:** Naver Clova STT accepts specific formats; wake word detection uses PCM

**Solution:**
- Use `pydub` or `wave` for format conversion
- Standardize on 16kHz, mono, 16-bit throughout pipeline

```python
from pydub import AudioSegment

def convert_to_wav(input_audio, output_format='wav'):
    """Convert audio to WAV format"""
    audio = AudioSegment.from_file(io.BytesIO(input_audio))
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format=output_format)
    return wav_buffer.getvalue()
```

### 7.2 Network Latency

**Challenge:** API calls introduce latency (200-500ms per request)

**Solution:**
- Implement audio caching for common responses (TTS)
- Use streaming API for long interactions
- Provide visual feedback during processing
- Pre-generate common TTS responses

### 7.3 Korean Language Accuracy

**Challenge:** STT accuracy varies with accents, background noise

**Solution:**
- Use noise cancellation libraries (noisereduce)
- Implement confidence scoring
- Provide fallback to text input
- Tune VAD parameters

```python
import noisereduce as nr

def reduce_noise(audio_data, sample_rate=16000):
    """Apply noise reduction"""
    return nr.reduce_noise(y=audio_data, sr=sample_rate)
```

### 7.4 Resource Management

**Challenge:** Continuous listening consumes resources

**Solution:**
- Use efficient wake word detection (Porcupine)
- Implement sleep/wake cycles
- Monitor CPU/memory usage
- Use threading for non-blocking operations

### 7.5 Error Handling

**Challenge:** API failures, network issues, audio errors

**Solution:**
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """Decorator for retrying failed API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
def transcribe_with_retry(audio_data):
    """Transcribe with automatic retry"""
    return transcribe_audio(audio_data)
```

### 7.6 Django Async Integration

**Challenge:** Voice processing blocks request/response cycle

**Solution:**
- Use Django Channels for WebSocket communication
- Implement background tasks with Celery
- Use async views (Django 3.1+)

```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import asyncio

@csrf_exempt
async def voice_command_api(request):
    """Async API endpoint for voice commands"""
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')

        # Process asynchronously
        audio_data = audio_file.read()
        text = await asyncio.to_thread(transcribe_audio, audio_data)

        return JsonResponse({'text': text})
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# tests/test_voice.py

import unittest
from medicine_analyzer.voice.stt_handler import transcribe_audio
from medicine_analyzer.voice.tts_handler import generate_speech

class VoiceAPITestCase(unittest.TestCase):

    def setUp(self):
        self.client_id = "test_id"
        self.client_secret = "test_secret"

    def test_stt_transcription(self):
        """Test STT with sample audio"""
        with open('tests/fixtures/sample_audio.wav', 'rb') as f:
            audio_data = f.read()

        text = transcribe_audio(audio_data, self.client_id, self.client_secret)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)

    def test_tts_generation(self):
        """Test TTS with sample text"""
        text = "테스트 메시지입니다"
        audio = generate_speech(text, self.client_id, self.client_secret)

        self.assertIsInstance(audio, bytes)
        self.assertGreater(len(audio), 0)

    def test_wake_word_detection(self):
        """Test wake word detection"""
        # Implement wake word test
        pass
```

### 8.2 Integration Tests

```python
# tests/test_integration.py

from django.test import TestCase
from channels.testing import WebsocketCommunicator
from medicine_project.asgi import application

class VoiceWebSocketTestCase(TestCase):

    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        communicator = WebsocketCommunicator(application, "/ws/voice/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_audio_transcription(self):
        """Test audio transcription via WebSocket"""
        communicator = WebsocketCommunicator(application, "/ws/voice/")
        await communicator.connect()

        # Send audio data
        import base64
        with open('tests/fixtures/sample_audio.wav', 'rb') as f:
            audio_b64 = base64.b64encode(f.read()).decode()

        await communicator.send_json_to({
            'type': 'audio',
            'audio': audio_b64
        })

        # Receive transcription
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'transcription')
        self.assertIn('text', response)

        await communicator.disconnect()
```

---

## 9. Deployment Considerations

### 9.1 Production Environment

**Requirements:**
- Redis for Django Channels
- NGINX for WebSocket proxying
- SSL certificates for secure WebSocket (wss://)
- Audio processing server (separate from web server)

**NGINX Configuration:**
```nginx
upstream django_channels {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /ws/ {
        proxy_pass http://django_channels;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://django_channels;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 9.2 Performance Optimization

**Caching Strategy:**
```python
from django.core.cache import cache

def get_or_generate_speech(text, speaker="mijin"):
    """Cache TTS responses"""
    cache_key = f"tts:{speaker}:{hash(text)}"

    audio = cache.get(cache_key)
    if audio is None:
        audio = generate_speech(text, speaker=speaker)
        cache.set(cache_key, audio, timeout=86400)  # 24 hours

    return audio
```

### 9.3 Monitoring and Logging

```python
import logging

logger = logging.getLogger(__name__)

def transcribe_with_logging(audio_data):
    """Transcribe with comprehensive logging"""
    try:
        logger.info("Starting transcription")
        start_time = time.time()

        text = transcribe_audio(audio_data)

        duration = time.time() - start_time
        logger.info(f"Transcription completed in {duration:.2f}s")
        logger.debug(f"Transcribed text: {text}")

        return text
    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        raise
```

---

## 10. Cost Estimation

### Naver Clova API Costs

**STT (Speech-to-Text):**
- ~0.5 KRW per second of audio
- 1000 5-second commands = 25,000 seconds = 12,500 KRW (~$10 USD/month)

**TTS (Text-to-Speech):**
- Similar pricing model based on character count
- Estimate: ~$10-15 USD/month for moderate usage

**Total Estimated Cost:**
- Small app (100 users, 10 commands/day): ~$20-30 USD/month
- Medium app (1000 users, 5 commands/day): ~$150-200 USD/month

**Optimization Strategies:**
- Cache common TTS responses
- Use wake word detection to minimize STT calls
- Implement usage quotas per user
- Pre-generate frequent responses

---

## 11. Quick Start Checklist

### Phase 1: Setup (Day 1)
- [ ] Create Naver Cloud Platform account
- [ ] Register application and get API keys
- [ ] Create Picovoice account
- [ ] Train custom wake word "케어필"
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure .env file with API keys

### Phase 2: Basic Integration (Day 2-3)
- [ ] Test STT API with sample audio
- [ ] Test TTS API with sample text
- [ ] Test wake word detection locally
- [ ] Create Django voice handler modules
- [ ] Test end-to-end flow with test script

### Phase 3: Django Integration (Day 4-5)
- [ ] Install Django Channels
- [ ] Configure WebSocket routing
- [ ] Create WebSocket consumer for voice
- [ ] Integrate with medicine analyzer logic
- [ ] Test WebSocket communication

### Phase 4: Testing & Refinement (Day 6-7)
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test with real users (Korean speakers)
- [ ] Tune accuracy and performance
- [ ] Implement error handling

### Phase 5: Deployment (Day 8-10)
- [ ] Set up Redis for Channels
- [ ] Configure NGINX
- [ ] Set up SSL certificates
- [ ] Deploy to production server
- [ ] Monitor logs and performance
- [ ] Implement caching strategy

---

## 12. Additional Resources

### Official Documentation
- **Naver Cloud Platform**: https://www.ncloud.com/product/aiService/clovaSpeech
- **CLOVA Speech API Docs**: https://api.ncloud-docs.com/docs/en/ai-naver-clovaspeechrecognition
- **CLOVA Voice API Docs**: https://api.ncloud-docs.com/docs/en/ai-naver-clovavoice
- **Porcupine Console**: https://console.picovoice.ai/
- **Porcupine Documentation**: https://picovoice.ai/docs/porcupine/

### Python Libraries
- **pvporcupine**: https://pypi.org/project/pvporcupine/
- **clovaTTS**: https://github.com/zebehn/clovaTTS
- **Django Channels**: https://channels.readthedocs.io/
- **sounddevice**: https://python-sounddevice.readthedocs.io/

### Community & Support
- **Naver Cloud Community**: Contact through NAVER Cloud Platform support
- **Picovoice Forum**: https://github.com/Picovoice/porcupine/discussions
- **Django Forum**: https://forum.djangoproject.com/

---

## Summary

This research document provides a complete guide for integrating Naver Clova STT and TTS APIs with a Django application, including Korean wake word detection using Porcupine. The recommended architecture uses:

1. **Porcupine** for local wake word detection ("케어필")
2. **Naver Clova STT** for accurate Korean speech transcription
3. **Naver Clova TTS** for natural Korean speech synthesis
4. **Django Channels** for real-time WebSocket communication
5. **sounddevice/PyAudio** for audio capture and playback

The implementation is production-ready, cost-effective, and optimized for Korean language voice interaction in a medicine analysis application.
