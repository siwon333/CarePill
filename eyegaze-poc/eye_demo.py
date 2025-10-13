#!/usr/bin/env python3
"""
실시간 Eye Tracking 데모 (개선 버전)
- 가까운 거리에서도 안정적인 추적
- 낮은 임계값 + 이전 프레임 활용
"""
import cv2
import mediapipe as mp
import numpy as np
import argparse
import time
from pathlib import Path
from utils.landmarks import compute_ear, compute_gaze, get_eye_landmarks
from utils.filters import EMAFilter
from utils.io import load_calibration, save_log

mp_face_mesh = mp.solutions.face_mesh

class RobustEyeTracker:
    """안정적인 눈 추적기"""
    def __init__(self, min_confidence=0.3):
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_confidence,
            min_tracking_confidence=min_confidence,
        )
        self.last_valid_landmarks = None
        self.lost_frames = 0
        self.max_lost_frames = 30  # 1초 정도 버팀
        
    def process(self, frame):
        """프레임 처리 with fallback"""
        results = self.face_mesh.process(frame)
        
        if results.multi_face_landmarks:
            self.last_valid_landmarks = results.multi_face_landmarks[0].landmark
            self.lost_frames = 0
            return results.multi_face_landmarks[0].landmark
        else:
            self.lost_frames += 1
            # 최근에 본 적 있으면 이전 값 활용
            if self.last_valid_landmarks and self.lost_frames < self.max_lost_frames:
                return self.last_valid_landmarks
            return None
    
    def get_tracking_quality(self):
        """추적 품질 반환 (0.0~1.0)"""
        if self.lost_frames == 0:
            return 1.0
        return max(0.0, 1.0 - self.lost_frames / self.max_lost_frames)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--flip-x', action='store_true', help='X축 반전(셀피 카메라)')
    parser.add_argument('--flip-y', action='store_true', help='Y축 반전')
    parser.add_argument('--two-cross', action='store_true', help='양쪽 눈 인디케이터')
    parser.add_argument('--save', action='store_true', help='CSV 로그 저장')
    parser.add_argument('--show-points', action='store_true', help='랜드마크 표시')
    parser.add_argument('--width', type=int, default=1280, help='카메라 해상도 너비')
    parser.add_argument('--height', type=int, default=720, help='카메라 해상도 높이')
    parser.add_argument('--pos-smooth', type=float, default=0.7, help='위치 스무딩')
    parser.add_argument('--vel-smooth', type=float, default=0.3, help='속도 스무딩')
    parser.add_argument('--deadzone', type=float, default=0.05, help='데드존')
    parser.add_argument('--dot-gain', type=float, default=0.8, help='점 이동 배율')
    parser.add_argument('--min-confidence', type=float, default=0.3, help='최소 감지 신뢰도')
    args = parser.parse_args()

    # 캘리브레이션 로드
    calib = load_calibration('default')
    
    # 카메라 설정
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # 실제 해상도 확인
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"카메라 해상도: {actual_w}x{actual_h}")
    
    # 트래커 및 필터 초기화
    tracker = RobustEyeTracker(min_confidence=args.min_confidence)
    filter_left = EMAFilter(alpha_pos=args.pos_smooth, alpha_vel=args.vel_smooth, deadzone=args.deadzone)
    filter_right = EMAFilter(alpha_pos=args.pos_smooth, alpha_vel=args.vel_smooth, deadzone=args.deadzone)
    
    # 로그 저장
    log_data = [] if args.save else None
    
    # 상단 인디케이터 설정
    indicator_h = 60
    dot_l_x, dot_l_y = actual_w // 4, indicator_h // 2
    dot_r_x, dot_r_y = 3 * actual_w // 4, indicator_h // 2
    
    blink_count = 0
    last_blink_time = 0
    
    print("\n=== Eye Tracking 시작 ===")
    print(f"- 해상도: {actual_w}x{actual_h}")
    print(f"- 최소 신뢰도: {args.min_confidence}")
    print(f"- 스무딩: pos={args.pos_smooth}, vel={args.vel_smooth}")
    print("- ESC 키로 종료\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # RGB 변환
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 얼굴 감지
        landmarks = tracker.process(rgb)
        quality = tracker.get_tracking_quality()
        
        # 상단 인디케이터 영역 생성
        indicator = np.ones((indicator_h, actual_w, 3), dtype=np.uint8) * 40
        
        if landmarks is not None:
            h, w = frame.shape[:2]
            
            # 왼쪽 눈
            left_pts = get_eye_landmarks(landmarks, 'left', w, h)
            ear_left = compute_ear(left_pts)
            gaze_left = compute_gaze(landmarks, 'left', w, h, calib)
            nx_l, ny_l = gaze_left
            
            # 오른쪽 눈
            right_pts = get_eye_landmarks(landmarks, 'right', w, h)
            ear_right = compute_ear(right_pts)
            gaze_right = compute_gaze(landmarks, 'right', w, h, calib)
            nx_r, ny_r = gaze_right
            
            # X/Y 축 반전
            if args.flip_x:
                nx_l, nx_r = -nx_l, -nx_r
            if args.flip_y:
                ny_l, ny_r = -ny_l, -ny_r
            
            # 필터 적용
            fx_l, fy_l = filter_left.update(nx_l, ny_l)
            fx_r, fy_r = filter_right.update(nx_r, ny_r)
            
            # 인디케이터 점 위치
            dot_l_x = int(actual_w // 4 + fx_l * args.dot_gain * 200)
            dot_l_y = int(indicator_h // 2 - fy_l * args.dot_gain * 20)
            dot_l_x = np.clip(dot_l_x, 10, actual_w // 2 - 10)
            dot_l_y = np.clip(dot_l_y, 10, indicator_h - 10)
            
            dot_r_x = int(3 * actual_w // 4 + fx_r * args.dot_gain * 200)
            dot_r_y = int(indicator_h // 2 - fy_r * args.dot_gain * 20)
            dot_r_x = np.clip(dot_r_x, actual_w // 2 + 10, actual_w - 10)
            dot_r_y = np.clip(dot_r_y, 10, indicator_h - 10)
            
            # 깜빡임 감지
            avg_ear = (ear_left + ear_right) / 2
            if avg_ear < 0.2:
                current_time = time.time()
                if current_time - last_blink_time > 0.3:
                    blink_count += 1
                    last_blink_time = current_time
            
            # 인디케이터 그리기
            cv2.circle(indicator, (dot_l_x, dot_l_y), 8, (0, 255, 0), -1)
            cv2.circle(indicator, (dot_r_x, dot_r_y), 8, (0, 255, 255), -1)
            
            if args.two_cross:
                cv2.line(indicator, (dot_l_x - 15, dot_l_y), (dot_l_x + 15, dot_l_y), (255, 255, 255), 1)
                cv2.line(indicator, (dot_l_x, dot_l_y - 15), (dot_l_x, dot_l_y + 15), (255, 255, 255), 1)
                cv2.line(indicator, (dot_r_x - 15, dot_r_y), (dot_r_x + 15, dot_r_y), (255, 255, 255), 1)
                cv2.line(indicator, (dot_r_x, dot_r_y - 15), (dot_r_x, dot_r_y + 15), (255, 255, 255), 1)
            
            # 랜드마크 표시
            if args.show_points:
                for pt in left_pts + right_pts:
                    cv2.circle(frame, pt, 2, (0, 255, 255), -1)
            
            # 정보 표시
            info_y = 30
            cv2.putText(frame, f"EAR: L={ear_left:.2f} R={ear_right:.2f}", 
                       (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Gaze: L=({fx_l:.2f},{fy_l:.2f}) R=({fx_r:.2f},{fy_r:.2f})", 
                       (10, info_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Blink: {blink_count}", 
                       (10, info_y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # 추적 품질 표시
            quality_color = (0, 255, 0) if quality > 0.8 else (0, 255, 255) if quality > 0.5 else (0, 0, 255)
            cv2.putText(frame, f"Quality: {quality:.0%}", 
                       (10, info_y + 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, quality_color, 2)
            
            # 로그 저장
            if log_data is not None:
                log_data.append({
                    'timestamp': time.time(),
                    'ear_left': ear_left,
                    'ear_right': ear_right,
                    'gaze_left_x': fx_l,
                    'gaze_left_y': fy_l,
                    'gaze_right_x': fx_r,
                    'gaze_right_y': fy_r,
                    'quality': quality
                })
        else:
            # 감지 실패
            cv2.putText(frame, "Face not detected - Move closer or adjust lighting", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(indicator, "NO FACE DETECTED", 
                       (actual_w // 2 - 150, indicator_h // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # 화면 결합
        combined = np.vstack([indicator, frame])
        cv2.imshow('Eye Tracking (Improved)', combined)
        
        # 종료
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
    
    # 정리
    cap.release()
    cv2.destroyAllWindows()
    
    if log_data:
        save_log(log_data, 'eye_tracking')
        print(f"\n로그 저장 완료: {len(log_data)}개 프레임")

if __name__ == '__main__':
    main()