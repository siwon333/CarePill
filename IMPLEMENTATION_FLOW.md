# CarePill 약봉투 스캔 플로우 구현 문서

## 📋 개요
음성 명령으로 약봉투 스캔부터 약 저장까지 자동으로 진행되는 전체 플로우 구현

## 🎯 구현 완료 날짜
2025-01-XX (구현 완료)

---

## 🔊 음성 명령어

### voice_navigation.js
**파일 경로**: `carepill/static/carepill/js/voice_navigation.js`

**추가된 명령어** (35번째 줄):
```javascript
'봉투스캔': '/scan/',
```

**동작**:
- "봉투스캔" 또는 "약봉투스캔" 음성 명령 시 `/scan/` 페이지로 이동

---

## 📱 페이지별 구현 상세

### 1️⃣ 약봉투 스캔 페이지 (`/scan/`)

**파일**: `carepill/templates/carepill/scan.html`

**주요 변경사항**:
1. **촬영 버튼 제거** (108-120번째 줄)
   - 수동 촬영 버튼 삭제
   - 자동 진행 방식으로 변경

2. **자동 스캔 프로세스** (288-309번째 줄)
```javascript
setTimeout(async () => {
  console.log('[SCAN] Starting automatic scan process');

  // 1. 로딩창 표시
  const overlay = showOverlay('약봉투를 스캔하는 중...');

  // 2. 로딩창 표시 후 5초 대기
  await new Promise(resolve => setTimeout(resolve, 5000));

  // 3. 음성 재생
  await playVoiceGuide('킴스약국에서 2025년 9월 30일에 조제한 기침가래약입니다.mp3');

  // 4. 음성 재생 완료 후 로딩창 제거 및 페이지 이동
  overlay.remove();
  document.body.style.overflow = document.body.dataset.prevOverflow || '';

  window.location.href = "/how2prescription/";
}, 500);
```

**타이밍**:
- 페이지 로드 → 0.5초 대기
- 로딩창 표시 → 5초 대기
- 음성 재생 (약 5초)
- 다음 페이지로 자동 이동

**사용 음성 파일**:
- `carepill/static/carepill/audio/킴스약국에서 2025년 9월 30일에 조제한 기침가래약입니다.mp3`

---

### 2️⃣ 처방약 투입 페이지 (`/how2prescription/`)

**파일**: `carepill/templates/carepill/how2prescription.html`

**구현 내용** (184-204번째 줄):
```javascript
document.addEventListener('DOMContentLoaded', async () => {
  ensureOverlayStyles();

  // 음성 가이드 재생
  await playVoiceGuide('기기 상단 오른쪽 몸쪽에 위치한 빨간색 투입구에 처방약을 넣어주세요.mp3');

  // 오버레이 표시
  const overlay = showOverlay();

  // 17초 후 페이지 이동
  setTimeout(() => {
    document.body.style.overflow = document.body.dataset.prevOverflow || '';
    window.location.href = "/meds_hos/";
  }, 17000);
});
```

**타이밍**:
- 음성 재생 (약 5초)
- 로딩창 "처방약을 투입해주세요..." 표시
- 17초 대기
- 다음 페이지로 자동 이동

**사용 음성 파일**:
- `carepill/static/carepill/audio/기기 상단 오른쪽 몸쪽에 위치한 빨간색 투입구에 처방약을 넣어주세요.mp3`

---

### 3️⃣ 약 목록 페이지 (`/meds_hos/`)

**파일**: `carepill/templates/carepill/meds_hos.html`

**구현 내용** (164-171번째 줄):
```javascript
document.addEventListener('DOMContentLoaded', async function() {
  console.log('[MEDS_HOS] Page loaded, playing audio');
  setTimeout(async () => {
    await playVoiceGuide('처방약이 저장되었습니다.mp3');
    console.log('[MEDS_HOS] Audio playback completed');
  }, 500);
});
```

**타이밍**:
- 페이지 로드 → 0.5초 대기
- 음성 재생 (약 2초)
- 약 목록 표시

**사용 음성 파일**:
- `carepill/static/carepill/audio/처방약이 저장되었습니다.mp3`

---

## 📊 전체 플로우 타임라인

```
사용자: "봉투스캔" 음성 명령
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 페이지 1: /scan/ (약봉투 스캔 페이지)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓ (0.5초 대기)

🔄 로딩창: "약봉투를 스캔하는 중..."
    ↓ (5초 대기)

🔊 음성 재생: "킴스약국에서 2025년 9월 30일에 조제한 기침가래약입니다"
    ↓ (약 5초)

로딩창 제거 → 자동 페이지 이동
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 페이지 2: /how2prescription/ (처방약 투입 페이지)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓

🔊 음성 재생: "기기 상단 오른쪽 몸쪽에 위치한 빨간색 투입구에 처방약을 넣어주세요"
    ↓ (약 5초)

🔄 로딩창: "처방약을 투입해주세요..."
    ↓ (17초 대기)

자동 페이지 이동
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 페이지 3: /meds_hos/ (약 목록 페이지)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓ (0.5초 대기)

🔊 음성 재생: "처방약이 저장되었습니다"
    ↓ (약 2초)

✅ 완료: 약 목록 표시
```

**총 소요 시간**: 약 35-40초

---

## 🎵 사용된 음성 파일 목록

모든 파일 위치: `carepill/static/carepill/audio/`

1. **킴스약국에서 2025년 9월 30일에 조제한 기침가래약입니다.mp3**
   - 사용 위치: `/scan/` 페이지
   - 재생 타이밍: 로딩창 표시 5초 후

2. **기기 상단 오른쪽 몸쪽에 위치한 빨간색 투입구에 처방약을 넣어주세요.mp3**
   - 사용 위치: `/how2prescription/` 페이지
   - 재생 타이밍: 페이지 로드 즉시

3. **처방약이 저장되었습니다.mp3**
   - 사용 위치: `/meds_hos/` 페이지
   - 재생 타이밍: 페이지 로드 0.5초 후

---

## 🔧 핵심 기술 구현

### 1. 음성 파일 재생 함수
```javascript
function playVoiceGuide(audioFile) {
  return new Promise((resolve) => {
    const audio = new Audio("/static/carepill/audio/" + audioFile);
    audio.onended = resolve;
    audio.play().catch(err => {
      console.error('Audio play error:', err);
      resolve();
    });
  });
}
```

**특징**:
- Promise 기반으로 음성 재생 완료 대기 가능
- 오류 발생 시에도 다음 단계 진행

### 2. 로딩 오버레이 표시 함수
```javascript
function showOverlay(text) {
  const flash = document.createElement('div');
  flash.className = 'capture-flash';
  document.body.appendChild(flash);
  setTimeout(() => flash.remove(), 300);

  const overlay = document.createElement('div');
  overlay.className = 'loading-overlay';
  overlay.innerHTML = `
    <div class="loading-spinner" aria-hidden="true"></div>
    <p class="loading-text" aria-live="polite">${text || '처리 중...'}</p>
  `;
  document.body.appendChild(overlay);

  document.body.dataset.prevOverflow = document.body.style.overflow;
  document.body.style.overflow = 'hidden';

  return overlay;
}
```

**특징**:
- 플래시 효과와 함께 로딩창 표시
- 스크롤 잠금 처리
- 커스텀 메시지 지원

### 3. 비동기 타이밍 제어
```javascript
// 5초 대기
await new Promise(resolve => setTimeout(resolve, 5000));

// 음성 재생 완료 대기
await playVoiceGuide('파일명.mp3');
```

**특징**:
- async/await를 사용한 순차적 실행
- Promise 기반 타이밍 제어

---

## 🐛 디버깅 및 로그

각 페이지에서 콘솔 로그로 실행 흐름 확인 가능:

```javascript
// scan.html
[SCAN] Starting automatic scan process
[SCAN] 5 seconds passed, playing audio
[SCAN] Redirecting to /how2prescription/

// how2prescription.html
[how2prescription] DOMContentLoaded fired
[how2prescription] show overlay
[how2prescription] redirect

// meds_hos.html
[MEDS_HOS] Page loaded, playing audio
[MEDS_HOS] Audio playback completed
```

**디버깅 방법**:
1. 브라우저에서 `F12` 키를 눌러 개발자 도구 열기
2. Console 탭 선택
3. 위의 로그 메시지로 실행 흐름 추적

---

## 🧪 테스트 방법

### 1. 서버 시작
```bash
cd C:\Users\woo\Desktop\Jeonggyun6
python manage.py runserver
```

### 2. 브라우저 캐시 삭제
- `Ctrl + Shift + Delete` → 캐시 및 쿠키 삭제
- 또는 `Ctrl + Shift + R` (하드 리프레시)

### 3. 테스트 시나리오

**방법 1: 음성 명령 테스트**
1. 홈 페이지 접속
2. "봉투스캔" 음성 명령
3. 자동 플로우 확인

**방법 2: 직접 접속 테스트**
1. `http://127.0.0.1:8000/scan/` 직접 접속
2. 자동 플로우 확인

### 4. 확인 사항
- ✅ 로딩창이 정상적으로 표시되는가?
- ✅ 음성이 올바른 타이밍에 재생되는가?
- ✅ 페이지 자동 이동이 작동하는가?
- ✅ 각 단계가 순차적으로 진행되는가?

---

## 📝 주요 변경 파일 목록

1. **voice_navigation.js**
   - 경로: `carepill/static/carepill/js/voice_navigation.js`
   - 변경: '봉투스캔' 명령어 추가

2. **scan.html**
   - 경로: `carepill/templates/carepill/scan.html`
   - 변경: 촬영 버튼 제거, 자동 스캔 프로세스 구현

3. **how2prescription.html**
   - 경로: `carepill/templates/carepill/how2prescription.html`
   - 변경: 17초 로딩 후 자동 이동 구현

4. **meds_hos.html**
   - 경로: `carepill/templates/carepill/meds_hos.html`
   - 변경: 페이지 로드 시 음성 재생 추가

---

## ⚠️ 주의사항

1. **음성 파일 경로**
   - 모든 음성 파일은 `/static/carepill/audio/` 디렉토리에 위치
   - 파일명 띄어쓰기 포함된 경우 정확한 이름 사용 필요

2. **브라우저 캐시**
   - JavaScript 변경 시 반드시 캐시 삭제 필요
   - 개발 중에는 시크릿 모드 사용 권장

3. **자동 재생 정책**
   - 일부 브라우저에서 자동 음성 재생이 차단될 수 있음
   - 사용자 상호작용 후 재생 권장

4. **타이밍 조정**
   - 네트워크 속도에 따라 페이지 로드 시간 차이 발생 가능
   - 필요 시 setTimeout 시간 조정

---

## 🔮 향후 개선 사항

1. **에러 처리**
   - 음성 파일 로드 실패 시 대체 동작 추가
   - 네트워크 오류 시 재시도 로직

2. **사용자 피드백**
   - 각 단계별 진행 상황 표시
   - 취소 버튼 추가 고려

3. **성능 최적화**
   - 음성 파일 사전 로딩
   - 페이지 전환 애니메이션 최적화

4. **접근성 개선**
   - 스크린 리더 지원 강화
   - 키보드 네비게이션 추가

---

## 📞 문의 및 지원

구현 관련 문의사항이나 버그 발견 시:
- 프로젝트 저장소 Issues 페이지 활용
- 콘솔 로그 캡처 후 공유

---

**문서 작성일**: 2025-01-XX
**마지막 업데이트**: 2025-01-XX
**작성자**: Claude Code Assistant
