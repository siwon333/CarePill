# eyegaze-poc

MediaPipe Face Mesh + Iris 기반으로
- EAR(눈 뜸/감김)
- 깜빡임 이벤트(ms)
- 정규화 시선 좌표(nx, ny)
- 상단 인디케이터(왼/오른 눈의 이동 점 2개, 옵션으로 + 두 개)

을 실시간으로 표시하는 PoC.

## 1) 설치

### (권장) 가상환경
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

패키지 설치
python -m pip install --upgrade pip
pip install -r requirements.txt
```
## 2) 캘리브레이션(선택)
```
python calib_tool.py
```

정면/좌/우/상/하를 1초씩 바라보며 캘리브레이션합니다.

결과는 out/calib/default.json 에 저장됩니다.

## 3) 데모 실행
```
# 셀피 웹캠이면 보통 X축 반전 필요
python eye_demo.py --flip-x --show-points
```
## 자주 쓰는 옵션
```
--flip-x : 셀피(거울) 카메라인 경우 +X를 오른쪽으로 맞춤

--flip-y : +Y를 위로 바꾸고 싶을 때

--two-cross : 상단 + 인디케이터를 양쪽 눈으로 2개 표시

--save : CSV 로그 저장 (out/logs/*.csv)

--show-points : 눈/홍채 주요 랜드마크 노란 점

# 점 움직임을 둔하게(부드럽게)
python eye_demo.py --flip-x --show-points \
  --pos-smooth 0.9 --vel-smooth 0.2 --deadzone 0.06 --dot-gain 0.6
```
## 4) 종료

ESC 키, 또는 터미널에서 Ctrl+C.

## 5) 트러블슈팅

ModuleNotFoundError: cv2 → pip install -r requirements.txt

Mediapipe 경고는 무시 가능.
성능 이슈 시 해상도를 낮추세요: --width 640 --height 360.


# 📦 requirements.txt

```
opencv-python>=4.8
mediapipe>=0.10.9
numpy>=1.24
```

Windows/Apple Silicon에서 OpenCV 설치가 꼬이면:

Windows: pip install opencv-python==4.8.1.78

macOS ARM: pip install opencv-python-headless 로 우회 가능