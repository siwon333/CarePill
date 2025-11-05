/**
 * 약 복용 알림 기능 (페이지 내 오버레이 방식)
 */

class MedicationNotification {
  constructor() {
    this.scheduledTimes = ['09:00', '12:00', '18:00']; // 아침 9시, 낮 12시, 저녁 6시
    this.snoozeTimeout = null;
  }

  /**
   * 약 복용 알림 표시 (페이지 내 오버레이)
   */
  showNotification(timeLabel = '', message = '타이레놀 500, 가스터 10mg를 복용해주세요.') {
    const overlay = document.getElementById('medicationAlert');
    const title = document.getElementById('alertTitle');
    const messageEl = document.getElementById('alertMessage');

    if (!overlay) {
      console.error('알림 오버레이를 찾을 수 없습니다.');
      return;
    }

    // 제목과 메시지 설정
    if (timeLabel) {
      title.textContent = `${timeLabel} 약 복용 시간입니다`;
    } else {
      title.textContent = '약 복용 시간입니다';
    }
    messageEl.textContent = message;

    // 오버레이 표시
    overlay.style.display = 'flex';

    // 음성 안내 재생
    setTimeout(() => {
      this.playVoiceReminder(title.textContent + '. ' + message);
    }, 500);
  }

  /**
   * 음성 안내 재생
   */
  playVoiceReminder(message) {
    if (window.CarePillTTS) {
      window.CarePillTTS.speak(message);
    }
  }

  /**
   * 알림 닫기
   */
  hideNotification() {
    const overlay = document.getElementById('medicationAlert');
    if (overlay) {
      overlay.style.display = 'none';
    }
  }

  /**
   * 테스트용 알림 (버튼 클릭 시)
   */
  testNotification() {
    const currentTime = new Date().toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit'
    });
    const hour = new Date().getHours();
    let timeLabel = '';

    if (hour >= 6 && hour < 11) {
      timeLabel = '아침';
    } else if (hour >= 11 && hour < 15) {
      timeLabel = '점심';
    } else {
      timeLabel = '저녁';
    }

    this.showNotification(timeLabel, '타이레놀 500, 가스터 10mg를 복용해주세요.');
  }

  /**
   * 정해진 시간에 알림 스케줄링
   */
  scheduleNotifications() {
    // 매 분마다 현재 시간 확인
    setInterval(() => {
      const now = new Date();
      const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

      if (this.scheduledTimes.includes(currentTime)) {
        const timeLabel = currentTime === '09:00' ? '아침' :
                         currentTime === '12:00' ? '점심' : '저녁';
        this.showNotification(timeLabel, '타이레놀 500, 가스터 10mg를 복용해주세요.');
      }
    }, 60000); // 1분마다 체크
  }

  /**
   * 10분 후 다시 알림
   */
  snooze() {
    this.hideNotification();

    // 기존 스누즈 타이머가 있으면 취소
    if (this.snoozeTimeout) {
      clearTimeout(this.snoozeTimeout);
    }

    // 10분 후 다시 알림
    this.snoozeTimeout = setTimeout(() => {
      this.showNotification('', '10분 전에 미루셨던 약 복용 시간입니다. 타이레놀 500, 가스터 10mg를 복용해주세요.');
    }, 10 * 60 * 1000); // 10분 = 600,000ms
  }

  /**
   * 초기화
   */
  init() {
    console.log('약 복용 알림 시스템이 초기화되었습니다.');
    // 스케줄링 시작
    this.scheduleNotifications();
  }
}

// 전역 인스턴스 생성
window.MedicationNotification = new MedicationNotification();

// 전역 함수로 노출 (HTML onclick에서 사용)
function testNotification() {
  window.MedicationNotification.testNotification();
}

function confirmMedication() {
  window.MedicationNotification.hideNotification();
}

function snoozeMedication() {
  window.MedicationNotification.snooze();
}

// 페이지 로드 시 자동 초기화
document.addEventListener('DOMContentLoaded', () => {
  window.MedicationNotification.init();
});
