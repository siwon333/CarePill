# 음성 네비게이션 디버깅 가이드

## 문제 증상
- 홈화면에서 "설정"을 누르면 아무 반응이 없음
- 다른 페이지에서 "설정"을 누르면 path 오류 발생

## 해결 방법

### 1단계: 브라우저 캐시 완전 삭제 (필수!)

**방법 A: 하드 새로고침**
```
Windows: Ctrl + Shift + R 또는 Ctrl + F5
Mac: Cmd + Shift + R
```

**방법 B: 수동 캐시 삭제**
1. Chrome 설정(⋮) → 도구 더보기 → 인터넷 사용 기록 삭제
2. "캐시된 이미지 및 파일" 체크
3. "데이터 삭제" 클릭
4. 페이지 새로고침

### 2단계: 브라우저 확인

**지원 브라우저**
- ✅ Google Chrome (권장)
- ✅ Microsoft Edge
- ❌ Firefox (Web Speech API 제한적 지원)
- ❌ Safari (Web Speech API 미지원)

### 3단계: 테스트 페이지로 확인

테스트 파일을 브라우저에서 직접 열기:
```
C:\Users\woo\Desktop\Jeonggyun\test_voice.html
```

**테스트 순서**
1. "1. 브라우저 지원 확인" 버튼 클릭
   - ✅ 지원됨: 다음 단계로
   - ❌ 미지원: Chrome 브라우저로 변경

2. "2. 음성 인식 시작" 버튼 클릭
   - 마이크 권한 요청 시 "허용" 클릭
   - "약투입", "현재있는 약", "말하기", "약분출" 중 하나 말하기
   - 인식되면 메시지 표시됨

3. 테스트가 성공하면 실제 사이트로 이동

### 4단계: 실제 사이트 테스트

**서버 실행 확인**
```bash
cd C:\Users\woo\Desktop\Jeonggyun
python manage.py runserver
```

**브라우저에서 접속**
```
http://localhost:8000/
```

**테스트 절차**
1. 홈페이지 로드
2. Ctrl+Shift+R로 하드 새로고침
3. F12 키를 눌러 개발자 도구 열기
4. Console 탭 확인 (빨간색 에러 있는지 확인)
5. "설정" 미니탭 클릭
6. 보라색 오버레이가 나타나는지 확인
7. "약투입" 말하기
8. 약 투입 화면으로 이동하는지 확인

### 5단계: 개발자 도구로 디버깅

**F12 개발자 도구 열기**

**Console 탭에서 확인할 내용**
```javascript
// 1. voice_navigation.js 로드 확인
window.voiceNavigator

// 2. 지원 여부 확인
'webkitSpeechRecognition' in window

// 3. 수동 테스트
startVoiceRecognition()
```

**예상 에러 및 해결**

| 에러 메시지 | 원인 | 해결 |
|------------|------|------|
| `window.voiceNavigator is undefined` | JavaScript 파일 로드 실패 | 하드 새로고침 (Ctrl+Shift+R) |
| `webkitSpeechRecognition is not defined` | 브라우저 미지원 | Chrome 브라우저 사용 |
| `not-allowed` | 마이크 권한 거부됨 | 브라우저 설정에서 마이크 권한 허용 |
| `audio-capture` | 마이크 없음 | 마이크 연결 확인 |
| `network` | 인터넷 연결 없음 | 인터넷 연결 확인 |

### 6단계: 마이크 권한 확인

**Chrome에서 마이크 권한 설정**
1. 주소창 왼쪽의 자물쇠 아이콘 클릭
2. "사이트 설정" 클릭
3. "마이크" → "허용" 선택
4. 페이지 새로고침

### 7단계: 여전히 작동하지 않을 경우

**로그 수집**
1. F12 개발자 도구 열기
2. Console 탭에서 모든 메시지 복사
3. Network 탭에서 voice_navigation.js 파일 확인
   - 200 OK 응답인지 확인
   - 404 에러인 경우 파일 경로 문제

**서버 로그 확인**
```bash
# 서버 실행 중인 터미널에서 확인
# 404 에러가 있는지 확인
```

## 성공 시나리오

### 정상 작동 시 나타나는 현상
1. "설정" 클릭 → 보라색 오버레이 즉시 표시
2. 오버레이 중앙에 마이크 아이콘과 펄스 애니메이션
3. "음성 인식 중..." 메시지 표시
4. 명령어 말하면 "명령 인식됨!" 표시
5. 1초 후 해당 페이지로 자동 이동

### 음성 명령어
- "약투입" → /scan_choice/ 이동
- "현재있는 약" → /meds/ 이동
- "말하기" → /voice/ 이동
- "약분출" → /how2green/ 이동

## 추가 확인 사항

### 파일 존재 여부 확인
```bash
ls -la C:\Users\woo\Desktop\Jeonggyun\carepill\static\carepill\js\voice_navigation.js
# 파일이 존재해야 함

ls -la C:\Users\woo\Desktop\Jeonggyun\carepill\templates\carepill\home.html
# 파일이 존재해야 함
```

### Django collectstatic 실행 (필요 시)
```bash
cd C:\Users\woo\Desktop\Jeonggyun
python manage.py collectstatic --noinput
```

## 연락처

문제가 계속되면 다음 정보와 함께 문의:
1. 브라우저 종류 및 버전
2. F12 Console의 에러 메시지 스크린샷
3. Network 탭 스크린샷
4. 서버 로그
