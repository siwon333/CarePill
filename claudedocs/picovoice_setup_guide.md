# Picovoice (Porcupine) 설정 가이드 - "케어필" 웨이크 워드

**목적**: "케어필" 한국어 웨이크 워드 설정 및 테스트
**소요 시간**: 15-20분
**비용**: 무료 (Free Tier)

---

## Picovoice가 뭔가요?

**Picovoice**는 음성 AI 플랫폼입니다. 그 중 **Porcupine**이 웨이크 워드 검출 엔진입니다.

### 웨이크 워드(Wake Word)란?
```
사용자: "케어필 아침약 줘"
         ↑↑↑
      웨이크 워드

→ 시스템이 항상 이 단어만 듣고 있다가
→ "케어필" 감지 → 그때부터 녹음 시작 → STT로 전송
```

### 왜 필요한가?
```
Option 1 (웨이크 워드 없이):
→ 마이크 항상 녹음 → 모든 소리 STT로 전송 → 비용 폭탄 💸

Option 2 (웨이크 워드 사용):
→ 로컬에서 "케어필"만 감지 (무료)
→ "케어필" 들리면 그때만 STT 사용
→ 비용 99% 절감 ✅
```

### Porcupine의 장점
- ✅ **한국어 지원** (중요!)
- ✅ **무료**: 월 3개 커스텀 웨이크 워드
- ✅ **정확도**: 경쟁사 대비 11배 높음
- ✅ **저전력**: 라즈베리파이에서도 작동
- ✅ **오프라인**: 인터넷 연결 불필요

---

## 1단계: Picovoice 계정 생성

### 1.1 웹사이트 접속
🔗 https://console.picovoice.ai/

### 1.2 회원가입
1. **Sign Up** 버튼 클릭
2. 이메일 입력 (Gmail 추천)
3. 비밀번호 설정
4. **Create Account** 클릭

### 1.3 이메일 인증
1. 가입한 이메일 확인
2. "Verify your email" 링크 클릭
3. 자동으로 콘솔로 이동

**소요 시간**: 2-3분

---

## 2단계: Access Key 발급

### 2.1 콘솔 접속
로그인 후 자동으로 Dashboard로 이동

### 2.2 Access Key 복사
```
Dashboard 페이지 상단에 표시됨:
┌─────────────────────────────────────────────┐
│ Access Key                                  │
│ ▶ ••••••••••••••••••••••••••••••••••••      │
│   [Copy]                                    │
└─────────────────────────────────────────────┘
```

1. **Access Key** 섹션 찾기
2. **눈 아이콘** 클릭 → 키 표시
3. **Copy** 버튼 클릭

### 2.3 .env 파일에 저장
```bash
# CarePill/.env 파일에 추가
PORCUPINE_ACCESS_KEY=여기에_복사한_키_붙여넣기
```

**예시**:
```bash
PORCUPINE_ACCESS_KEY=aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890AbCdEfGhIjKlMnOpQrStUvWxYz
```

**주의**: 따옴표 없이 그대로 붙여넣기!

**소요 시간**: 1분

---

## 3단계: "케어필" 웨이크 워드 훈련

### 3.1 Porcupine 페이지 이동
콘솔 왼쪽 메뉴:
```
Products
 └─ Porcupine ← 클릭
```

### 3.2 새 웨이크 워드 생성
1. **"Create Wake Word"** 또는 **"Train New Model"** 버튼 클릭

### 3.3 설정 입력

#### Language (언어)
```
┌────────────────────────────┐
│ Language: [Korean (한국어)] │ ← 선택
└────────────────────────────┘
```
**중요**: 반드시 **Korean** 선택!

#### Wake Phrase (웨이크 워드)
```
┌────────────────────────────┐
│ Wake Phrase: [케어필      ] │ ← 입력
└────────────────────────────┘
```

**입력**: `케어필` (한글로 정확히 입력)

**팁**:
- 2-3음절 권장 (케어필 = 3음절 ✅)
- 발음이 명확한 단어
- 일상 대화에 안 나오는 단어

#### Platform (플랫폼)
```
┌────────────────────────────┐
│ Platform: [Windows       ] │ ← 선택
└────────────────────────────┘
```

**선택 기준**:
- 개발 중인 OS 선택
- Windows 개발 → Windows
- Linux 배포 예정 → Linux도 추가 훈련 (나중에)

**참고**: 나중에 다른 플랫폼도 추가 훈련 가능

### 3.4 훈련 시작
```
┌────────────────────────────┐
│      [Train Model]         │ ← 클릭
└────────────────────────────┘
```

**훈련 시간**: 5-10초 (매우 빠름!)

### 3.5 모델 다운로드
훈련 완료 후:
```
┌─────────────────────────────────────────┐
│ ✓ Training Complete!                    │
│                                         │
│ Model: 케어필_ko_windows_v3_0_0.ppn     │
│                                         │
│       [Download .ppn file]              │
└─────────────────────────────────────────┘
```

1. **Download** 버튼 클릭
2. `.ppn` 파일 저장 (예: `Downloads/케어필_ko_windows_v3_0_0.ppn`)

### 3.6 모델 파일 이동
```bash
# CarePill 프로젝트에 wake_words 폴더 생성
CarePill/
  └─ wake_words/
      └─ carepill_ko_windows.ppn  ← 여기로 이동
```

**PowerShell 명령어**:
```powershell
# CarePill 디렉토리에서 실행
mkdir wake_words
move $env:USERPROFILE\Downloads\케어필_ko_windows_v3_0_0.ppn wake_words\carepill_ko_windows.ppn
```

### 3.7 .env 파일 업데이트
```bash
# .env 파일에 추가
WAKE_WORD_MODEL_PATH=wake_words/carepill_ko_windows.ppn
```

**소요 시간**: 5-7분

---

## 4단계: Python 라이브러리 설치

### 4.1 requirements.txt 업데이트
```bash
# CarePill/requirements.txt에 추가

# Wake Word Detection
pvporcupine>=3.0.0

# Audio Processing
PyAudio>=0.2.14
```

### 4.2 의존성 설치

#### Windows에서 PyAudio 설치 (중요!)
PyAudio는 Windows에서 설치가 까다로움. 두 가지 방법:

**방법 1: pipwin 사용 (권장)**
```bash
pip install pipwin
pipwin install pyaudio
```

**방법 2: Wheel 파일 직접 다운로드**
1. https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio 접속
2. Python 버전에 맞는 파일 다운로드
   - Python 3.11 64bit → `PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl`
3. 설치:
```bash
pip install 다운로드한파일경로\PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl
```

#### Porcupine 설치
```bash
pip install pvporcupine
```

### 4.3 설치 확인
```python
# test_porcupine.py
import pvporcupine
print("Porcupine version:", pvporcupine.__version__)
```

```bash
python test_porcupine.py
# 출력: Porcupine version: 3.0.x
```

**소요 시간**: 5-10분 (PyAudio 설치 시간 포함)

---

## 5단계: 웨이크 워드 테스트

### 5.1 테스트 스크립트 작성
```python
# test_wake_word.py

import os
import pvporcupine
import pyaudio
import struct
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def test_wake_word():
    """케어필 웨이크 워드 테스트"""

    # 1. 환경변수 확인
    access_key = os.getenv('PORCUPINE_ACCESS_KEY')
    model_path = os.getenv('WAKE_WORD_MODEL_PATH')

    if not access_key:
        print("❌ PORCUPINE_ACCESS_KEY가 .env에 설정되지 않았습니다!")
        return

    if not model_path or not os.path.exists(model_path):
        print(f"❌ 웨이크 워드 모델 파일을 찾을 수 없습니다: {model_path}")
        return

    print(f"✅ Access Key: {access_key[:20]}...")
    print(f"✅ Model Path: {model_path}")

    # 2. Porcupine 초기화
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[model_path]
        )
        print(f"✅ Porcupine 초기화 성공!")
        print(f"   Sample Rate: {porcupine.sample_rate} Hz")
        print(f"   Frame Length: {porcupine.frame_length}")
    except Exception as e:
        print(f"❌ Porcupine 초기화 실패: {e}")
        return

    # 3. 오디오 스트림 초기화
    pa = pyaudio.PyAudio()

    try:
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        print("✅ 마이크 스트림 초기화 성공!")
    except Exception as e:
        print(f"❌ 마이크 초기화 실패: {e}")
        print("\n마이크가 연결되어 있는지 확인하세요!")
        porcupine.delete()
        pa.terminate()
        return

    # 4. 웨이크 워드 감지 시작
    print("\n" + "="*50)
    print("🎤 \"케어필\"이라고 말해보세요!")
    print("   (종료하려면 Ctrl+C)")
    print("="*50 + "\n")

    try:
        while True:
            # 오디오 프레임 읽기
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            # 웨이크 워드 감지
            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print("\n🎉 웨이크 워드 감지! \"케어필\"을 들었습니다!\n")
                # 실제 앱에서는 여기서 STT 녹음 시작

    except KeyboardInterrupt:
        print("\n\n종료합니다...")

    finally:
        # 5. 정리
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()
        print("✅ 리소스 정리 완료")

if __name__ == "__main__":
    test_wake_word()
```

### 5.2 테스트 실행
```bash
python test_wake_word.py
```

**예상 출력**:
```
✅ Access Key: aBcDeFgHiJkLmNoPqRsT...
✅ Model Path: wake_words/carepill_ko_windows.ppn
✅ Porcupine 초기화 성공!
   Sample Rate: 16000 Hz
   Frame Length: 512
✅ 마이크 스트림 초기화 성공!

==================================================
🎤 "케어필"이라고 말해보세요!
   (종료하려면 Ctrl+C)
==================================================

🎉 웨이크 워드 감지! "케어필"을 들었습니다!
```

### 5.3 문제 해결

#### 문제 1: 마이크 초기화 실패
```
❌ 마이크 초기화 실패: [Errno -9996] Invalid input device
```

**해결**:
```python
# 사용 가능한 마이크 확인
import pyaudio
pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"Device {i}: {info['name']}")
```

#### 문제 2: 웨이크 워드 감지 안 됨
**원인**:
- 마이크 볼륨 너무 낮음
- 배경 소음 너무 큼
- 발음이 불명확

**해결**:
1. 마이크 볼륨 높이기 (Windows 설정)
2. 조용한 곳에서 테스트
3. "케-어-필" 천천히 명확하게 발음

#### 문제 3: Access Key 오류
```
❌ Porcupine 초기화 실패: Invalid access key
```

**해결**:
1. .env 파일에 `PORCUPINE_ACCESS_KEY` 확인
2. 키 앞뒤 공백 제거
3. Picovoice 콘솔에서 키 재확인

**소요 시간**: 3-5분

---

## 6단계: .gitignore 업데이트

### 6.1 웨이크 워드 모델 파일 제외
```bash
# .gitignore에 추가

# Wake Word Models
wake_words/*.ppn
!wake_words/.gitkeep
```

### 6.2 .gitkeep 생성
```bash
# wake_words 폴더 구조 유지용
touch wake_words/.gitkeep
```

**이유**: `.ppn` 모델 파일은 개인 계정으로 생성하므로 Git에 포함하지 않음

**소요 시간**: 1분

---

## 완료 체크리스트

### ✅ Picovoice 설정 완료 확인
- [ ] Picovoice 계정 생성
- [ ] Access Key 발급 및 .env 저장
- [ ] "케어필" 웨이크 워드 훈련
- [ ] .ppn 모델 파일 다운로드
- [ ] wake_words/ 폴더에 모델 파일 저장
- [ ] .env에 WAKE_WORD_MODEL_PATH 설정
- [ ] pvporcupine 라이브러리 설치
- [ ] PyAudio 설치 (Windows)
- [ ] test_wake_word.py 실행 성공
- [ ] 실제로 "케어필" 감지 확인
- [ ] .gitignore 업데이트

### 🎯 다음 단계
Picovoice 설정이 완료되었으므로 이제:
1. ✅ **환경 설정 완료** (Naver API ✅ + Picovoice ✅)
2. 다음: **Naver API 테스트** (STT + TTS)
3. 다음: **미니 프로토타입** (Wake Word → STT → TTS)

---

## 참고 자료

### Picovoice 공식 문서
- **콘솔**: https://console.picovoice.ai/
- **Porcupine 문서**: https://picovoice.ai/docs/porcupine/
- **Python SDK**: https://github.com/Picovoice/porcupine/tree/master/binding/python
- **FAQ**: https://picovoice.ai/docs/faq/

### 무료 티어 제한
```
Free Plan:
- 월 3개 커스텀 웨이크 워드
- 무제한 사용 (API 호출 제한 없음)
- 상업적 사용 가능 (조건부)
```

**충분함**: "케어필" 1개만 필요하므로 무료 플랜으로 충분

### 유료 플랜 (필요 시)
```
개인용 ($5/월):
- 10개 커스텀 웨이크 워드
- 우선 지원

비즈니스용 ($contact):
- 무제한 웨이크 워드
- 전담 지원
```

**현재 프로젝트**: 무료 플랜 충분 ✅

---

## 요약

**Picovoice = 웨이크 워드 감지 서비스**

```
작동 방식:
1. 항상 마이크 듣기 (로컬, 무료)
2. "케어필" 감지
3. 그때만 STT로 녹음 전송 → 비용 절감

설정 시간: 15-20분
비용: 무료
결과: "케어필" 말하면 감지됨!
```

**현재 상태**:
- ✅ Naver Clova API 키 보유
- ⏳ Picovoice 설정 필요 (이 가이드 따라하면 완료)

**다음**:
- Naver STT/TTS 테스트
- 전체 통합 (Wake Word → STT → TTS)

---

*작성일: 2025-10-01*
*문의: Picovoice 공식 문서 또는 GitHub Issues*
