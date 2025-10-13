"""
신호 스무딩 필터
"""
import numpy as np


class EMAFilter:
    """
    Exponential Moving Average 필터
    위치 + 속도 기반 스무딩
    """
    def __init__(self, alpha_pos=0.7, alpha_vel=0.3, deadzone=0.05):
        """
        Args:
            alpha_pos: 위치 스무딩 강도 (0~1, 높을수록 부드러움)
            alpha_vel: 속도 스무딩 강도 (0~1)
            deadzone: 데드존 임계값 (작은 움직임 무시)
        """
        self.alpha_pos = alpha_pos
        self.alpha_vel = alpha_vel
        self.deadzone = deadzone
        
        self.prev_x = None
        self.prev_y = None
        self.vel_x = 0.0
        self.vel_y = 0.0
    
    def update(self, x, y):
        """
        새 좌표 입력 → 필터링된 좌표 반환
        
        Args:
            x, y: 원본 좌표
        
        Returns:
            (filtered_x, filtered_y)
        """
        # 첫 입력
        if self.prev_x is None:
            self.prev_x = x
            self.prev_y = y
            return (x, y)
        
        # 데드존 적용
        dx = x - self.prev_x
        dy = y - self.prev_y
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance < self.deadzone:
            return (self.prev_x, self.prev_y)
        
        # 속도 계산 및 스무딩
        self.vel_x = self.alpha_vel * self.vel_x + (1 - self.alpha_vel) * dx
        self.vel_y = self.alpha_vel * self.vel_y + (1 - self.alpha_vel) * dy
        
        # 위치 업데이트 (EMA)
        filtered_x = self.alpha_pos * self.prev_x + (1 - self.alpha_pos) * (x + self.vel_x * 0.5)
        filtered_y = self.alpha_pos * self.prev_y + (1 - self.alpha_pos) * (y + self.vel_y * 0.5)
        
        self.prev_x = filtered_x
        self.prev_y = filtered_y
        
        return (filtered_x, filtered_y)
    
    def reset(self):
        """필터 상태 초기화"""
        self.prev_x = None
        self.prev_y = None
        self.vel_x = 0.0
        self.vel_y = 0.0


class KalmanFilter:
    """
    간단한 1D Kalman Filter (선택적)
    """
    def __init__(self, process_variance=1e-3, measurement_variance=1e-1):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimate = 0.0
        self.estimate_error = 1.0
    
    def update(self, measurement):
        """측정값 입력 → 필터링된 값 반환"""
        # Prediction
        prediction = self.estimate
        prediction_error = self.estimate_error + self.process_variance
        
        # Update
        kalman_gain = prediction_error / (prediction_error + self.measurement_variance)
        self.estimate = prediction + kalman_gain * (measurement - prediction)
        self.estimate_error = (1 - kalman_gain) * prediction_error
        
        return self.estimate
    
    def reset(self):
        """필터 상태 초기화"""
        self.estimate = 0.0
        self.estimate_error = 1.0


class MovingAverageFilter:
    """
    Moving Average 필터 (단순 평균)
    """
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.buffer_x = []
        self.buffer_y = []
    
    def update(self, x, y):
        """새 좌표 입력 → 평균값 반환"""
        self.buffer_x.append(x)
        self.buffer_y.append(y)
        
        if len(self.buffer_x) > self.window_size:
            self.buffer_x.pop(0)
            self.buffer_y.pop(0)
        
        avg_x = np.mean(self.buffer_x)
        avg_y = np.mean(self.buffer_y)
        
        return (avg_x, avg_y)
    
    def reset(self):
        """버퍼 초기화"""
        self.buffer_x = []
        self.buffer_y = []