"""
얼굴 랜드마크 기반 EAR 및 시선 계산
"""
import numpy as np

# MediaPipe Face Mesh 인덱스
LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

LEFT_IRIS_INDICES = [468, 469, 470, 471, 472]
RIGHT_IRIS_INDICES = [473, 474, 475, 476, 477]


def get_eye_landmarks(landmarks, eye='left', w=1, h=1):
    """
    눈 랜드마크 좌표 추출
    
    Args:
        landmarks: MediaPipe landmarks
        eye: 'left' or 'right'
        w, h: 프레임 크기
    
    Returns:
        List of (x, y) tuples
    """
    indices = LEFT_EYE_INDICES if eye == 'left' else RIGHT_EYE_INDICES
    points = []
    
    for idx in indices:
        lm = landmarks[idx]
        x = int(lm.x * w)
        y = int(lm.y * h)
        points.append((x, y))
    
    return points


def compute_ear(eye_points):
    """
    Eye Aspect Ratio 계산
    
    Args:
        eye_points: 6개의 눈 좌표 [(x,y), ...]
    
    Returns:
        EAR 값 (0.0 ~ 1.0, 낮을수록 눈 감김)
    """
    if len(eye_points) < 6:
        return 0.0
    
    # 수직 거리
    v1 = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
    v2 = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
    
    # 수평 거리
    h = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
    
    if h == 0:
        return 0.0
    
    ear = (v1 + v2) / (2.0 * h)
    return ear


def compute_gaze(landmarks, eye='left', w=1, h=1, calibration=None):
    """
    정규화된 시선 좌표 계산
    
    Args:
        landmarks: MediaPipe landmarks
        eye: 'left' or 'right'
        w, h: 프레임 크기
        calibration: 캘리브레이션 데이터 (선택)
    
    Returns:
        (nx, ny) 정규화 시선 좌표
    """
    # 눈 외곽 및 홍채 중심
    eye_indices = LEFT_EYE_INDICES if eye == 'left' else RIGHT_EYE_INDICES
    iris_indices = LEFT_IRIS_INDICES if eye == 'left' else RIGHT_IRIS_INDICES
    
    # 눈 중심
    eye_center = np.mean([(landmarks[i].x, landmarks[i].y) for i in eye_indices], axis=0)
    
    # 홍채 중심
    iris_center = np.mean([(landmarks[i].x, landmarks[i].y) for i in iris_indices], axis=0)
    
    # 상대 이동 (정규화)
    dx = iris_center[0] - eye_center[0]
    dy = iris_center[1] - eye_center[1]
    
    # 스케일 조정 (경험적 값)
    nx = dx * 20  # X축 이동 증폭
    ny = dy * 15  # Y축 이동 증폭
    
    # 캘리브레이션 보정
    if calibration:
        center_x, center_y = calibration.get('center', (0, 0))
        nx -= center_x
        ny -= center_y
    
    return (float(nx), float(ny))


def get_iris_landmarks(landmarks, eye='left', w=1, h=1):
    """
    홍채 랜드마크 좌표 추출
    
    Args:
        landmarks: MediaPipe landmarks
        eye: 'left' or 'right'
        w, h: 프레임 크기
    
    Returns:
        List of (x, y) tuples
    """
    indices = LEFT_IRIS_INDICES if eye == 'left' else RIGHT_IRIS_INDICES
    points = []
    
    for idx in indices:
        lm = landmarks[idx]
        x = int(lm.x * w)
        y = int(lm.y * h)
        points.append((x, y))
    
    return points