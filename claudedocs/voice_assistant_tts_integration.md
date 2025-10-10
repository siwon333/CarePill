# Voice Assistant TTS Integration Guide

## Overview
This guide explains how to integrate the Django TTS API with the existing voice assistant (`voice_assistant_prototype.py`).

## Current Architecture

### Before (Naver TTS)
```
Voice Assistant → Naver TTS API → Fixed Voice ("nara") → Audio Output
```

### After (Custom Voice TTS)
```
Voice Assistant → Django TTS API → GPT-SoVITS → User's Voice → Audio Output
                                    ↓
                                 Cache Layer (for offline/fast access)
```

## Setup Steps

### 1. Install Dependencies
```bash
pip install djangorestframework==3.14.0
```

### 2. Run Migrations
```bash
python manage.py makemigrations voice_tts
python manage.py migrate
```

### 3. Create API Token
```bash
python manage.py shell
```

In the shell:
```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create or get user
user, created = User.objects.get_or_create(username='voice_user')
if created:
    user.set_password('secure_password')
    user.save()

# Create token
token, created = Token.objects.get_or_create(user=user)
print(f"Your API Token: {token.key}")
```

Save this token - you'll need it for API calls.

### 4. Upload User Voice Sample

You need a short (5-30 seconds) voice sample from the user. This can be:
- A recording saying "안녕하세요, 저는 [이름]입니다"
- Any clear voice recording in the target voice style
- Supported formats: WAV, MP3

**Upload via API:**
```bash
curl -X POST http://localhost:8000/api/tts/upload-voice/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -F "voice_file=@/path/to/voice_sample.wav"
```

**Or via Django Admin:**
1. Visit http://localhost:8000/admin/
2. Login with superuser credentials
3. Go to "Voice Tts" → "User voices"
4. Add new user voice, upload file

## API Endpoints

### Health Check
**GET** `/api/tts/health/`

No authentication required.

**Response:**
```json
{
  "status": "healthy",
  "service": {
    "is_available": true,
    "model_loaded": true,
    "device": "cpu",
    "mock_mode": true
  },
  "timestamp": "2025-10-10T12:34:56.789Z"
}
```

### Generate TTS
**POST** `/api/tts/generate/`

Authentication required.

**Request:**
```json
{
  "text": "약을 드실 시간입니다",
  "use_cache": true,
  "language": "ko"
}
```

**Response (Cache Hit):**
```json
{
  "success": true,
  "cache_hit": true,
  "audio_url": "/media/tts_cache/83e5d0e3d5035810f7e09c04b1c8d7f4.wav",
  "duration_seconds": 2.5,
  "processing_time_ms": 45
}
```

**Response (Cache Miss, Generated):**
```json
{
  "success": true,
  "cache_hit": false,
  "audio_url": "/media/tts_cache/83e5d0e3d5035810f7e09c04b1c8d7f4.wav",
  "duration_seconds": 2.5,
  "processing_time_ms": 2150
}
```

## Integration with Voice Assistant

### Current Voice Assistant Code Location
The voice assistant prototype is likely in one of these locations:
- `voice_assistant_prototype.py` (mentioned in previous analysis)
- `voice_tts/` directory
- Root directory

### Integration Pattern

**Before (Naver TTS):**
```python
from naver_tts import NaverTTS

def speak(text):
    tts = NaverTTS()
    audio_file = tts.generate(text, voice="nara")
    play_audio(audio_file)
```

**After (Django TTS API):**
```python
import requests
import pygame  # or other audio player

class DjangoTTSClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {'Authorization': f'Token {token}'}

    def generate_speech(self, text, use_cache=True, language="ko"):
        """Generate TTS using Django API"""
        url = f"{self.base_url}/api/tts/generate/"
        data = {
            "text": text,
            "use_cache": use_cache,
            "language": language
        }

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def speak(self, text):
        """Generate and play TTS"""
        result = self.generate_speech(text)

        if result['success']:
            # Download audio file
            audio_url = f"{self.base_url}{result['audio_url']}"
            audio_response = requests.get(audio_url)

            # Save temporarily
            temp_path = '/tmp/tts_output.wav'
            with open(temp_path, 'wb') as f:
                f.write(audio_response.content)

            # Play audio
            pygame.mixer.init()
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        else:
            print(f"TTS failed: {result.get('error', 'Unknown error')}")

# Usage
tts_client = DjangoTTSClient(
    base_url="http://localhost:8000",
    token="YOUR_TOKEN_HERE"
)

tts_client.speak("약을 드실 시간입니다")
```

### For Raspberry Pi Integration

**If Django server is on the same Pi:**
```python
tts_client = DjangoTTSClient(
    base_url="http://localhost:8000",
    token="YOUR_TOKEN_HERE"
)
```

**If Django server is on cloud (recommended for performance):**
```python
tts_client = DjangoTTSClient(
    base_url="https://your-server.com",
    token="YOUR_TOKEN_HERE"
)
```

### Error Handling
```python
def speak_with_fallback(text):
    """Speak with fallback to Naver TTS if Django API fails"""
    try:
        # Try Django TTS first
        tts_client.speak(text)
    except Exception as e:
        print(f"Django TTS failed: {e}, falling back to Naver TTS")
        # Fallback to Naver TTS
        naver_tts = NaverTTS()
        audio_file = naver_tts.generate(text, voice="nara")
        play_audio(audio_file)
```

## Cache Management

### Cache Benefits
- **Speed**: Cached responses are 50-100x faster (45ms vs 2-4 seconds)
- **Offline**: Cached phrases work without internet/server
- **Cost**: Reduces API/compute costs for repeated phrases

### Common Phrases to Pre-Cache
```python
common_phrases = [
    "약을 드실 시간입니다",
    "오늘의 약 복용 일정입니다",
    "약 복용을 완료했습니다",
    "다음 약 복용까지 4시간 남았습니다",
    "약을 아직 복용하지 않으셨습니다",
    "약 복용 기록이 저장되었습니다"
]

# Pre-generate cache
for phrase in common_phrases:
    result = tts_client.generate_speech(phrase, use_cache=True)
    print(f"Cached: {phrase} - {result['audio_url']}")
```

### Cache Administration

**Via Django Admin:**
1. Visit http://localhost:8000/admin/
2. Go to "Voice Tts" → "TTS caches"
3. View cached entries, access counts, last used dates
4. Use "Delete 30+ day old cache" action to clean up

**Via Management Command:**
```bash
# Create a custom management command to pre-cache phrases
python manage.py precache_tts --file common_phrases.txt
```

## Performance Considerations

### Current Implementation (Mock Mode)
- **Processing Time**: ~50ms (just copies reference audio)
- **Quality**: Returns reference audio, not actual TTS
- **Purpose**: API testing and integration development

### With Real GPT-SoVITS
- **First Request**: 2-4 seconds (model inference on CPU)
- **Cached Request**: ~50ms (file retrieval)
- **GPU Acceleration**: 0.5-1 second with CUDA
- **Quality**: Natural voice cloning with user's voice characteristics

### Optimization Strategies

**1. Pre-cache common phrases:**
- Generate cache for frequent medicine alerts
- Run during off-peak hours
- Reduces real-time processing needs

**2. Cloud deployment:**
- Deploy Django + GPT-SoVITS on cloud server with GPU
- Raspberry Pi makes API calls
- Much faster inference than Pi CPU

**3. Hybrid approach:**
- Cache on Pi for offline access
- Cloud API for new phrases
- Automatic sync when online

## Testing Checklist

- [ ] Django server running (`python manage.py runserver`)
- [ ] User created and API token generated
- [ ] User voice sample uploaded
- [ ] Health check endpoint returns `is_available: true`
- [ ] TTS generation endpoint returns audio URL
- [ ] Audio file playable and in correct format
- [ ] Cache working (second request faster than first)
- [ ] Error handling tested (invalid text, missing voice sample)

## Next Steps

### Immediate (Development)
1. ✅ Django TTS app created
2. ✅ Migrations applied
3. ✅ Basic testing completed
4. ⏳ Update voice assistant to use Django API
5. ⏳ Upload test voice sample
6. ⏳ Test end-to-end flow

### Later (Production)
1. Install actual GPT-SoVITS model
2. Replace mock implementation with real inference
3. Deploy to cloud server with GPU
4. Configure production database (PostgreSQL)
5. Set up HTTPS/SSL for secure API access
6. Implement rate limiting and usage monitoring

## GPT-SoVITS Installation (Future)

When ready to use real TTS instead of mock:

```bash
# Install dependencies
pip install torch==2.1.2 torchaudio==2.1.2
pip install librosa==0.10.1 soundfile==0.12.1 scipy==1.11.4

# Clone GPT-SoVITS
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS

# Download pretrained models
# Follow official instructions at:
# https://github.com/RVC-Boss/GPT-SoVITS/blob/main/docs/en/README.md

# Update voice_tts/services/gpt_sovits.py
# Uncomment the real GPT-SoVITS code sections
# Comment out the mock implementation
```

Then restart Django server to load the real model.

## Troubleshooting

### "No voice sample found"
- Upload voice sample via API or admin panel
- Check `media/user_voices/` directory has the file
- Verify `is_active=True` for UserVoice object

### "Service not available"
- Check Django server is running
- Verify GPTSoVITSService initialized successfully
- Check logs for model loading errors

### "Audio file not found"
- Check `media/tts_cache/` directory permissions
- Verify MEDIA_ROOT and MEDIA_URL in settings.py
- Check file was actually generated (not just DB entry)

### Slow TTS generation
- Expected in mock mode with CPU
- Solution: Use GPU or cloud deployment
- Workaround: Pre-cache common phrases

## Support

For issues or questions:
1. Check Django logs: `python manage.py runserver` output
2. Check voice_tts logs: Look for GPTSoVITSService messages
3. Test with `/api/tts/health/` endpoint
4. Review this documentation and API responses
