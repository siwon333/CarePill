# Voice Conversion Options for Raspberry Pi (Korean Language Support)

## 프로젝트 목표
네이버 TTS 대신 사용자 제공 음색으로 음성 합성을 하기 위한 Voice Conversion 솔루션 조사

**요구사항**:
- ✅ 라즈베리파이에서 실행 가능 (경량 모델)
- ✅ 한국어 지원
- ✅ Zero-shot 음성 변환 (사전 학습 없이 새로운 음색 적용)
- ✅ 실시간 처리 가능

---

## 🎯 추천 솔루션

### 1. **sherpa-onnx** ⭐⭐⭐⭐⭐ (최우선 추천)

**GitHub**: https://github.com/k2-fsa/sherpa-onnx

#### 장점
- ✅ **라즈베리파이 공식 지원** (arm32, arm64)
- ✅ **한국어 네이티브 지원** (ASR 및 TTS 모델 제공)
- ✅ **ONNX 기반** - 경량화 및 최적화 가능
- ✅ **오프라인 동작** - 인터넷 연결 불필요
- ✅ **실시간 스트리밍** 지원
- ✅ **초경량 모델** - 14M~20M 파라미터 모델 제공
- ✅ **다양한 플랫폼** - Android, iOS, HarmonyOS, RISC-V 지원

#### 스펙
```yaml
Language Support: Korean (한국어), English, Chinese, Japanese, Cantonese
Platform: Raspberry Pi, embedded systems, mobile
Model Size: 14M - 20M parameters (ultra-lightweight)
Architecture: ONNX Runtime
Real-time: Yes (streaming & non-streaming)
Offline: Yes
```

#### 제공 기능
- Speech-to-Text (ASR)
- Text-to-Speech (TTS)
- Speaker Diarization
- Voice Activity Detection (VAD)
- WebAssembly 지원

#### 예시 모델
- `sherpa-onnx-streaming-zipformer-korean-2024-06-16` (한국어 스트리밍)
- `sherpa-onnx-streaming-zipformer-zh-14M-2023-02-23` (Cortex A7 CPU용)

#### 구현 방법
```bash
# 설치
pip install sherpa-onnx

# 한국어 TTS 모델 다운로드 및 사용
# 네이버 TTS → sherpa-onnx TTS로 변경
# 사용자 음성 샘플 → Voice Conversion 적용
```

#### 한계점
- ⚠️ Voice Conversion 기능은 명시적으로 언급되지 않음
- 📌 TTS와 VC를 분리해서 파이프라인 구성 필요
- 📌 Zero-shot VC는 별도 모델 필요

---

### 2. **NeuTTS Air** ⭐⭐⭐⭐ (유망한 대안)

**출처**: Neuphonic (2025년 10월 출시)

#### 장점
- ✅ **Edge Device 최적화** (Raspberry Pi, 노트북, 스마트폰)
- ✅ **Zero-shot Voice Cloning** (3초 샘플로 음색 복제)
- ✅ **경량 모델** - 748M 파라미터
- ✅ **GGUF 포맷** - Q4/Q8 양자화 지원
- ✅ **CPU 우선 실행 경로**
- ✅ **MIT 라이선스** - 상업적 이용 가능

#### 스펙
```yaml
Model Size: 748M parameters (GGUF Q4/Q8)
Platform: Raspberry Pi, laptops, phones
Voice Cloning: 3+ seconds reference audio
Architecture: CPU-first
Release: October 2025
License: Open-source
```

#### 한계점
- ⚠️ **한국어 지원 명시 없음** (확인 필요)
- ⚠️ 최신 모델로 커뮤니티 성숙도 낮을 수 있음

---

### 3. **Seed-VC** ⭐⭐⭐ (성능 우수, 하드웨어 요구사항 높음)

**GitHub**: https://github.com/Plachtaa/seed-vc

#### 장점
- ✅ **Zero-shot Voice Conversion**
- ✅ **실시간 변환** (~300ms 지연)
- ✅ **초소량 데이터 학습** (1개 발화로 fine-tuning)
- ✅ **다양한 모델 크기** - 25M ~ 200M 파라미터
- ✅ **빠른 학습** (T4 GPU에서 2분)

#### 스펙
```yaml
Model Sizes: 25M, 50M, 100M, 200M parameters
Reference Audio: 1-30 seconds
Real-time Delay: ~300ms algorithm + ~100ms device
Training: Minimum 100 steps (2 min on T4)
Platform: Windows, Mac M Series, Linux
GPU: NVIDIA CUDA 11.8-12.8
```

#### 한계점
- ❌ **라즈베리파이 명시적 지원 없음**
- ❌ **GPU 권장** (실시간 처리 위해)
- ❌ **한국어 지원 명시 없음**
- ⚠️ RTX 3060 Laptop GPU에서 테스트됨 (라즈베리파이보다 고성능)

#### 라즈베리파이 적용 가능성
- 🔧 최소 모델(25M) + 최적화로 가능성 있음
- 🔧 실시간은 어려울 수 있음 (비실시간 처리로 대안)

---

### 4. **OpenVoice V2** ⭐⭐⭐ (한국어 지원 우수)

**GitHub**: https://github.com/myshell-ai/OpenVoice

#### 장점
- ✅ **한국어 네이티브 지원** (English, Spanish, French, Chinese, Japanese, Korean)
- ✅ **Zero-shot Cross-lingual Voice Cloning**
- ✅ **MIT 라이선스** (2024년 4월부터 상업적 이용 가능)

#### 스펙
```yaml
Languages: Korean (한국어) + 5 other languages
Cloning: Zero-shot cross-lingual
License: MIT (free for commercial use)
Release: OpenVoice V2 (April 2024)
```

#### 한계점
- ❌ **높은 하드웨어 요구사항** (~1.5GB VRAM on RTX 3090)
- ❌ **라즈베리파이 직접 실행 어려움**

#### 라즈베리파이 적용 방법
- 🔧 **양자화 필요** (ONNX 변환 + INT8/FP16)
- 🔧 클라우드 처리 후 결과만 수신하는 하이브리드 방식

---

### 5. **Kokoro TTS (ONNX)** ⭐⭐⭐⭐ (경량 TTS 옵션)

**Hugging Face**: https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX

#### 장점
- ✅ **초경량** - 82M 파라미터, 양자화 후 80MB 이하
- ✅ **ONNX 양자화** - fp32, fp16, q8, q4 지원
- ✅ **Edge Device 최적화**
- ✅ **한국어 지원 예정** (현재 개발 중)

#### 스펙
```yaml
Model Size: 82M parameters (~80MB quantized)
Quantization: fp32, fp16, int8, q4
Languages: English (현재), Korean (planned)
Platform: Cross-platform C++ implementation
Deployment: On-device AI assistant
```

#### 한계점
- ⚠️ **한국어 아직 미지원** (계획만 있음)
- ⚠️ Voice Conversion보다는 TTS에 특화

---

### 6. **RVC (Retrieval-based Voice Conversion)** ⭐⭐⭐ (훈련 용이)

**GitHub**: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI

#### 장점
- ✅ **소량 데이터 학습** (≥10분 음성)
- ✅ **한국어 문서 지원**
- ✅ **낮은 사양에서도 학습 가능**
- ✅ **음색 융합 기능**

#### 스펙
```yaml
Training Data: ≥10 minutes (low-noise)
GPU: Works on poor graphics cards
Languages: Documentation in Korean, Chinese, Japanese, etc.
Features: Model fusion, RMVPE algorithm
```

#### 한계점
- ❌ **라즈베리파이 경량 버전 없음**
- ❌ **GPU 선호** (CUDA 가속)
- ⚠️ 주로 PC/워크스테이션 환경에서 사용

---

## 🔧 권장 구현 전략

### ✨ 최적 파이프라인 (하이브리드 방식)

```yaml
Architecture: "Naver TTS + Voice Conversion Post-processing"

Step 1 - Text to Speech:
  tool: Naver TTS API (현재 사용 중)
  output: 표준 음성 파일 (.wav)

Step 2 - Voice Conversion:
  tool: sherpa-onnx (if VC support added) OR Seed-VC (quantized)
  input: Naver TTS output + user voice sample
  output: 사용자 음색으로 변환된 음성

Step 3 - Playback:
  device: Raspberry Pi speaker
```

### 🎯 단계별 실행 계획

#### Phase 1: Proof of Concept (POC)
```yaml
Objective: 라즈베리파이에서 동작 가능한 최소 시스템 검증

Tools to Test:
  1. sherpa-onnx: TTS 기능 테스트 (한국어)
  2. Seed-VC (25M model): 경량 모델 라즈베리파이 실행 테스트
  3. NeuTTS Air: GGUF Q4 모델 CPU 실행 테스트

Success Criteria:
  - 라즈베리파이에서 모델 로딩 성공
  - 5초 이내 응답 시간
  - 메모리 사용 < 1GB
```

#### Phase 2: Integration
```yaml
Objective: 네이버 TTS와 Voice Conversion 파이프라인 통합

Steps:
  1. Naver TTS → .wav 파일 생성
  2. sherpa-onnx/Seed-VC로 음성 변환
  3. 결과 재생 및 품질 검증

Optimization:
  - 모델 양자화 (INT8, FP16)
  - 배치 처리로 지연 최소화
  - 캐싱으로 반복 음성 최적화
```

#### Phase 3: Production
```yaml
Objective: 실시간 성능 최적화 및 배포

Features:
  - 사용자 음성 샘플 업로드 기능
  - 실시간/비실시간 모드 선택
  - 다양한 음색 프리셋 제공

Performance Target:
  - 응답 시간: < 3초 (비실시간 OK)
  - 품질: 자연스러운 음색 변환
  - 안정성: 24/7 운영 가능
```

---

## 📊 비교표

| 솔루션 | 한국어 | 라즈베리파이 | Zero-shot | 모델 크기 | 난이도 | 추천도 |
|--------|-------|-------------|-----------|----------|--------|--------|
| **sherpa-onnx** | ✅ | ✅ | ⚠️ | 14-20M | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **NeuTTS Air** | ❓ | ✅ | ✅ | 748M | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Seed-VC** | ❓ | ⚠️ | ✅ | 25-200M | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **OpenVoice V2** | ✅ | ❌ | ✅ | Large | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Kokoro ONNX** | 🔜 | ✅ | ❌ | 82M | ⭐⭐ | ⭐⭐⭐⭐ |
| **RVC** | ✅ | ❌ | ❌ | Large | ⭐⭐⭐ | ⭐⭐ |

**범례**:
- ✅ 지원 확인 | ❓ 지원 불명확 | ⚠️ 제한적 지원 | ❌ 미지원 | 🔜 개발 예정

---

## 🛠️ 실험 코드 예시

### sherpa-onnx 기본 사용법
```python
import sherpa_onnx

# TTS 초기화
tts_config = sherpa_onnx.OfflineTtsConfig(
    model="path/to/korean/model",
    language="korean"
)
tts = sherpa_onnx.OfflineTts(tts_config)

# 음성 생성
text = "안녕하세요, CarePill입니다."
audio = tts.generate(text)

# 저장
audio.save("output.wav")
```

### Seed-VC 경량 변환
```python
from seed_vc import VoiceConverter

# 모델 로드 (25M 파라미터)
vc = VoiceConverter(model_size="25M", device="cpu")

# 음성 변환
reference_audio = "user_voice_sample.wav"  # 사용자 음색 샘플
source_audio = "naver_tts_output.wav"      # 네이버 TTS 결과

converted = vc.convert(
    source=source_audio,
    reference=reference_audio
)

converted.save("output_with_user_voice.wav")
```

### 하이브리드 파이프라인
```python
import requests
import sherpa_onnx
from seed_vc import VoiceConverter

# Step 1: 네이버 TTS (현재 코드 유지)
def naver_tts(text):
    # 기존 네이버 TTS API 호출
    response = requests.post(
        "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts",
        headers={...},
        data={"text": text}
    )
    with open("naver_output.wav", "wb") as f:
        f.write(response.content)
    return "naver_output.wav"

# Step 2: Voice Conversion
def apply_user_voice(tts_audio, user_sample):
    vc = VoiceConverter(model_size="25M", device="cpu")
    converted = vc.convert(source=tts_audio, reference=user_sample)
    converted.save("final_output.wav")
    return "final_output.wav"

# 전체 파이프라인
text = "복용 시간입니다"
user_voice = "user_voice_sample.wav"

tts_audio = naver_tts(text)
final_audio = apply_user_voice(tts_audio, user_voice)

# 재생
import pygame
pygame.mixer.init()
pygame.mixer.music.load(final_audio)
pygame.mixer.music.play()
```

---

## 🚀 다음 단계

1. **sherpa-onnx 테스트**
   - 라즈베리파이에 설치 및 한국어 TTS 테스트
   - 메모리/CPU 사용량 측정
   - 응답 시간 벤치마크

2. **Seed-VC POC**
   - 25M 모델 다운로드 및 CPU 모드 실행
   - 라즈베리파이에서 변환 속도 측정
   - 품질 평가 (음색 유사도, 자연스러움)

3. **NeuTTS Air 조사**
   - 한국어 지원 여부 확인 (GitHub issue/Discord)
   - GGUF Q4 모델 라즈베리파이 실행 테스트

4. **대안 전략**
   - 클라우드 처리: 음성 변환만 서버에서 수행
   - 사전 처리: 자주 사용하는 문장은 미리 변환하여 캐싱
   - 품질 vs 속도: 실시간 모드와 고품질 모드 분리

---

## 📚 참고 자료

- [sherpa-onnx GitHub](https://github.com/k2-fsa/sherpa-onnx)
- [Seed-VC GitHub](https://github.com/Plachtaa/seed-vc)
- [OpenVoice Research](https://research.myshell.ai/open-voice)
- [NeuTTS Air Article](https://www.marktechpost.com/2025/10/02/neuphonic-open-sources-neutts-air-a-748m-parameter-on-device-speech-language-model-with-instant-voice-cloning/)
- [Kokoro ONNX Hugging Face](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX)
- [RVC-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)

---

**작성일**: 2025-10-10
**작성자**: Claude (SuperClaude Framework)
**프로젝트**: CarePill - Voice Assistant Enhancement
