"""
파일 입출력 유틸리티
"""
import json
import csv
from pathlib import Path
from datetime import datetime


def ensure_dir(path):
    """디렉토리 생성 (없으면)"""
    Path(path).mkdir(parents=True, exist_ok=True)


def save_calibration(calib_data, user='default'):
    """
    캘리브레이션 데이터 저장
    
    Args:
        calib_data: 캘리브레이션 딕셔너리
        user: 사용자 이름
    """
    ensure_dir('out/calib')
    
    filepath = f'out/calib/{user}.json'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(calib_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 캘리브레이션 저장: {filepath}")


def load_calibration(user='default'):
    """
    캘리브레이션 데이터 로드
    
    Args:
        user: 사용자 이름
    
    Returns:
        캘리브레이션 딕셔너리 (없으면 None)
    """
    filepath = f'out/calib/{user}.json'
    
    if not Path(filepath).exists():
        print(f"⚠ 캘리브레이션 파일 없음: {filepath}")
        print("  → calib_tool.py를 먼저 실행하세요")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        calib = json.load(f)
    
    print(f"✓ 캘리브레이션 로드: {filepath}")
    return calib


def save_log(log_data, prefix='eye_tracking'):
    """
    CSV 로그 저장
    
    Args:
        log_data: 로그 리스트 (딕셔너리)
        prefix: 파일명 prefix
    """
    if not log_data:
        return
    
    ensure_dir('out/logs')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = f'out/logs/{prefix}_{timestamp}.csv'
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=log_data[0].keys())
        writer.writeheader()
        writer.writerows(log_data)
    
    print(f"✓ 로그 저장: {filepath}")


def load_log(filepath):
    """
    CSV 로그 로드
    
    Args:
        filepath: CSV 파일 경로
    
    Returns:
        로그 리스트 (딕셔너리)
    """
    log_data = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 숫자 변환
            converted = {}
            for k, v in row.items():
                try:
                    converted[k] = float(v)
                except ValueError:
                    converted[k] = v
            log_data.append(converted)
    
    return log_data


def save_config(config, name='config'):
    """
    설정 파일 저장
    
    Args:
        config: 설정 딕셔너리
        name: 파일명
    """
    ensure_dir('out')
    filepath = f'out/{name}.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 설정 저장: {filepath}")


def load_config(name='config'):
    """
    설정 파일 로드
    
    Args:
        name: 파일명
    
    Returns:
        설정 딕셔너리 (없으면 None)
    """
    filepath = f'out/{name}.json'
    
    if not Path(filepath).exists():
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config