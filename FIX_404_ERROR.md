# 404 에러 해결 방법 (단계별 가이드)

## 즉시 시도: 브라우저 캐시 완전 삭제

### 방법 1: Chrome 시크릿 모드 (가장 빠름!)
```
1. Chrome에서 Ctrl + Shift + N (시크릿 창)
2. http://localhost:8000/ 접속
3. "설정" 클릭해서 작동하는지 확인
```
✅ **시크릿 모드에서 작동하면 → 캐시 문제 확정**

---

### 방법 2: 개발자 도구에서 캐시 비활성화

1. **F12** 키로 개발자 도구 열기
2. **Network** 탭 클릭
3. **"Disable cache"** 체크박스 선택
4. **개발자 도구를 열어둔 채로** 페이지 새로고침 (Ctrl+Shift+R)

![Network Tab](https://i.imgur.com/example.png)

---

### 방법 3: 완전한 캐시 삭제

**Chrome에서:**
```
1. 우측 상단 ⋮ 클릭
2. "도구 더보기" → "인터넷 사용 기록 삭제"
3. 시간 범위: "전체 기간"
4. "캐시된 이미지 및 파일" 체크
5. "데이터 삭제" 클릭
6. Chrome 완전히 종료 (X 버튼)
7. Chrome 재시작
8. http://localhost:8000/ 접속
```

---

### 방법 4: 정확한 404 파일 확인

1. **F12** 키로 개발자 도구 열기
2. **Console** 탭 클릭
3. 빨간색 에러 메시지에서 정확한 파일 이름 확인
4. 아래 스크린샷 예시처럼 보입니다:

```
Failed to load resource: the server responded with a status of 404 (Not Found)
http://localhost:8000/static/carepill/js/voice_navigation.js
```

**정확한 URL을 복사해서 알려주세요!**

---

## 서버 재시작 (추가 조치)

```bash
# 1. 기존 서버 중지
# 터미널에서 Ctrl+C

# 2. 서버 재시작
cd C:\Users\woo\Desktop\Jeonggyun
python manage.py runserver

# 3. 출력 확인
# "Starting development server at http://127.0.0.1:8000/" 메시지 확인
```

---

## 직접 URL 테스트

브라우저 주소창에 다음 URL을 **직접 입력**해서 테스트:

### 1. voice_navigation.js 확인
```
http://localhost:8000/static/carepill/js/voice_navigation.js
```
✅ JavaScript 코드가 보이면 성공
❌ 404 페이지가 보이면 파일 경로 문제

### 2. tts_helper.js 확인
```
http://localhost:8000/static/carepill/js/tts_helper.js
```

### 3. notification.js 확인
```
http://localhost:8000/static/carepill/js/notification.js
```

**모든 파일이 정상적으로 로드되어야 합니다.**

---

## 여전히 안 될 경우

### 정보 수집
다음 정보를 알려주세요:

1. **정확한 404 URL** (F12 → Console 탭에서 복사)
2. **브라우저 종류 및 버전**
   - Chrome: 주소창에 `chrome://version/` 입력
3. **시크릿 모드에서 작동 여부**
4. **직접 URL 접근 결과** (위의 3개 URL 각각)

### 스크린샷 찍기
1. F12 개발자 도구 열기
2. Network 탭 클릭
3. Ctrl+Shift+R로 새로고침
4. 빨간색 404 에러 파일 클릭
5. 스크린샷 찍기

---

## 예상 결과 (정상 작동 시)

### Network 탭에서 확인할 내용
```
Name                        Status    Type          Size
voice_navigation.js         200       javascript    6.7 KB
tts_helper.js              200       javascript    2.3 KB
notification.js            200       javascript    3.9 KB
```

모두 **200 OK** 상태여야 합니다.

---

## 긴급 우회 방법 (임시)

캐시 문제가 계속되면 파일명을 변경해서 강제로 다시 로드:

```bash
# 1. 파일명 변경
cd C:\Users\woo\Desktop\Jeonggyun\carepill\static\carepill\js
mv voice_navigation.js voice_navigation_v2.js

# 2. HTML에서 파일명 수정 (home.html, scan.html, meds.html)
# voice_navigation.js → voice_navigation_v2.js

# 3. 서버 재시작
```

**하지만 이 방법은 추천하지 않습니다. 먼저 위의 캐시 삭제 방법을 시도하세요.**
