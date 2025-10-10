# Voice Assistant Code Analysis

**Branch**: `feature/voice-conversion`
**Date**: 2025-10-10
**Purpose**: Analyze current voice assistant for Voice Conversion integration

---

## 📋 Current Architecture

### Complete Pipeline Flow

```
Wake Word → STT → Intent Classification → Response → TTS
(Porcupine)  (Naver)  (OpenAI GPT-4)     (OpenAI)  (Naver)
```

### File Structure

```
voice_assistant_prototype.py  # Main pipeline implementation
test_wake_word.py             # Wake word detection test
requirements.txt              # Dependencies
```

---

## 🔍 Code Analysis

### 1. **Wake Word Detection** (voice_assistant_prototype.py:44-80)
- **Library**: `pvporcupine` (Picovoice Porcupine)
- **Wake Word**: "carepill" (케어필)
- **Sensitivity**: 0.7
- **Sample Rate**: 16kHz
- **Status**: ✅ Working

### 2. **Speech-to-Text** (voice_assistant_prototype.py:85-143)
- **Provider**: Naver Clova STT
- **Language**: Korean (Kor)
- **Recording**: 3 seconds after wake word
- **Output Format**: WAV (16kHz, mono)
- **Status**: ✅ Working

### 3. **Intent Classification** (voice_assistant_prototype.py:148-202)
- **Model**: OpenAI GPT-4o-mini
- **Intents**:
  - `get_medicine`: 약 가져오기/복용 요청
  - `list_medicine`: 약 목록 조회
  - `ask_time`: 복용 시간 질문
  - `ask_dosage`: 복용량 질문
  - `unknown`: 알 수 없는 명령
- **Output**: JSON format with intent, time_slot, medicine_name, confidence
- **Status**: ✅ Working

### 4. **Response Generation** (voice_assistant_prototype.py:237-270)
- **Model**: OpenAI GPT-4o-mini
- **Style**: 친절한 약 복용 도우미, 1-2 문장, 존댓말
- **Input**: Intent + Mock Database
- **Status**: ✅ Working

### 5. **Text-to-Speech** ⭐ **TARGET FOR VOICE CONVERSION** (voice_assistant_prototype.py:275-311)
- **Provider**: Naver Clova TTS Premium
- **Voice**: `nara` (나라) - 네이버 기본 목소리
- **Output**: MP3 format
- **Playback**: Windows `start` command
- **Status**: ✅ Working, but **목소리 변환 필요**

---

## 🎯 Voice Conversion Integration Point

### Current TTS Flow (voice_assistant_prototype.py:275-311)

```python
def text_to_speech(text):
    """Convert text to speech using Naver Clova TTS"""
    # 1. Call Naver TTS API
    response = requests.post(url, headers=headers, data=data)

    # 2. Save as MP3
    with open("response_audio.mp3", "wb") as f:
        f.write(response.content)

    # 3. Play audio
    subprocess.run(["start", "response_audio.mp3"], shell=True)
```

### 🔧 Proposed New Flow with Voice Conversion

```python
def text_to_speech_with_voice_conversion(text, user_voice_sample):
    """Convert text to speech with user voice cloning"""

    # STEP 1: Generate standard TTS (기존 네이버 TTS)
    naver_audio = call_naver_tts(text)  # "response_audio.mp3"

    # STEP 2: Apply Voice Conversion (NEW!)
    converted_audio = apply_voice_conversion(
        source_audio=naver_audio,
        target_voice=user_voice_sample  # 사용자 음성 샘플
    )

    # STEP 3: Play converted audio
    play_audio(converted_audio)
```

---

## 📦 Current Dependencies

### Voice-Related Packages
```
pvporcupine>=3.0.0    # Wake word detection
PyAudio>=0.2.14       # Audio I/O
python-dotenv>=1.0.0  # Environment variables
```

### API Services
- **Naver Clova**: STT + TTS
- **OpenAI**: Intent classification + Response generation

### Missing for Voice Conversion
- ❌ `sherpa-onnx` or `seed-vc`
- ❌ Audio processing libraries (soundfile, librosa, scipy)

---

## 🚀 Integration Strategy

### Phase 1: Install Voice Conversion Library

**Option A: sherpa-onnx** (추천)
```bash
pip install sherpa-onnx
```

**Option B: Seed-VC**
```bash
pip install torch  # PyTorch dependency
git clone https://github.com/Plachtaa/seed-vc
pip install -r seed-vc/requirements.txt
```

### Phase 2: Create Voice Conversion Module

**New File**: `voice_conversion.py`

```python
"""
Voice Conversion Module for CarePill
Converts Naver TTS output to user's voice
"""

import sherpa_onnx  # or seed_vc
import soundfile as sf

class VoiceConverter:
    def __init__(self, model_path, user_voice_sample):
        self.model = self.load_model(model_path)
        self.user_voice = user_voice_sample

    def convert(self, source_audio_path):
        """Convert source audio to target voice"""
        # Load source audio (Naver TTS output)
        # Apply voice conversion
        # Save converted audio
        pass
```

### Phase 3: Modify text_to_speech Function

**Update**: `voice_assistant_prototype.py:275-311`

```python
def text_to_speech(text, use_voice_conversion=True):
    """Convert text to speech using Naver Clova TTS + Voice Conversion"""

    # STEP 1: Generate base TTS
    base_audio = generate_naver_tts(text)

    if use_voice_conversion and Config.USER_VOICE_SAMPLE:
        # STEP 2: Apply Voice Conversion
        from voice_conversion import VoiceConverter

        vc = VoiceConverter(
            model_path=Config.VC_MODEL_PATH,
            user_voice_sample=Config.USER_VOICE_SAMPLE
        )

        final_audio = vc.convert(base_audio)
    else:
        final_audio = base_audio

    # STEP 3: Play audio
    play_audio(final_audio)
```

### Phase 4: Configuration Updates

**Add to Config class**:
```python
class Config:
    # ... existing config ...

    # Voice Conversion (NEW)
    USER_VOICE_SAMPLE = os.getenv('USER_VOICE_SAMPLE')  # Path to user's voice
    VC_MODEL_PATH = os.getenv('VC_MODEL_PATH')          # sherpa-onnx or seed-vc model
    ENABLE_VOICE_CONVERSION = os.getenv('ENABLE_VOICE_CONVERSION', 'false').lower() == 'true'
```

**Add to .env**:
```env
# Voice Conversion
USER_VOICE_SAMPLE=./user_voices/user_voice_sample.wav
VC_MODEL_PATH=./models/sherpa-onnx-korean-vc
ENABLE_VOICE_CONVERSION=true
```

---

## 🧪 Testing Plan

### Test 1: sherpa-onnx Installation
```bash
pip install sherpa-onnx
python -c "import sherpa_onnx; print(sherpa_onnx.__version__)"
```

### Test 2: Load Korean TTS Model
```python
import sherpa_onnx

config = sherpa_onnx.OfflineTtsConfig(
    model="path/to/korean/model"
)
tts = sherpa_onnx.OfflineTts(config)
```

### Test 3: Voice Conversion POC
```python
# Convert Naver TTS output with user voice
user_sample = "user_voice.wav"
naver_output = "naver_tts.mp3"

# Apply VC
converted = voice_converter.convert(naver_output, user_sample)
play(converted)
```

### Test 4: Full Pipeline Integration
```python
# Run full flow: Wake Word → STT → Intent → Response → TTS + VC
# Verify:
# - Original Naver TTS quality preserved
# - User voice characteristics applied
# - Latency acceptable (< 3 seconds total)
```

---

## ⚠️ Technical Challenges

### Challenge 1: Format Compatibility
- **Naver TTS Output**: MP3
- **Voice Conversion Input**: Usually WAV
- **Solution**: Convert MP3 → WAV before VC, then back to MP3 for playback

### Challenge 2: Latency
- **Naver TTS**: ~500ms
- **Voice Conversion**: ~1-2 seconds (depending on model)
- **Total**: ~2.5 seconds (acceptable for voice assistant)

### Challenge 3: Quality Preservation
- Ensure voice conversion doesn't degrade Korean pronunciation
- Test with various Korean phonemes and sentence structures

### Challenge 4: Model Size
- sherpa-onnx models: 14-20M parameters ✅ Lightweight
- Seed-VC models: 25-200M parameters ⚠️ May need optimization

---

## 📊 Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Wake Word Latency | < 300ms | ~300ms | ✅ |
| STT Latency | < 1s | ~500ms | ✅ |
| Intent Classification | < 2s | ~1s | ✅ |
| Response Generation | < 2s | ~1s | ✅ |
| TTS Latency | < 1s | ~500ms | ✅ |
| **Voice Conversion** | **< 2s** | **TBD** | ⏳ |
| **Total Pipeline** | **< 8s** | **~3.3s** | ✅ |

---

## 🎯 Next Steps

1. ✅ Branch created: `feature/voice-conversion`
2. ✅ Code analysis complete
3. ⏳ Install sherpa-onnx
4. ⏳ Test Korean TTS model
5. ⏳ Implement voice_conversion.py
6. ⏳ Integrate with text_to_speech()
7. ⏳ Test full pipeline
8. ⏳ Quality validation
9. ⏳ Performance optimization
10. ⏳ Merge to develop-vision

---

**Status**: Ready to proceed with sherpa-onnx installation and testing
**Estimated Time**: 2-3 hours for full integration
**Risk Level**: Low (independent module, easy rollback)
