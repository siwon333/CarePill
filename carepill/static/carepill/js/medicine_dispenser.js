/**
 * 약 배출 알림 기능
 * 사용자가 약을 요청하면 작은 알림창을 표시하고 안내 음성 재생
 */

class MedicineDispenser {
  constructor() {
    this.overlay = null;
    this.currentAudio = null;

    // ✅ 오디오 컨텍스트 생성 (전역으로 공유)
    if (!window.audioCtx) {
      window.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      console.log("[MedicineDispenser] AudioContext 생성됨");
    }
  }

  /**
   * 약 배출 알림 표시
   * @param {string} medicineName - 약 이름 (예: "확펜", "처방약")
   * @param {string} message - 표시할 메시지
   * @param {string} audioFileName - 재생할 음성 파일명
   */
  showDispenseNotification(medicineName, message, audioFileName) {
    console.log('[MedicineDispenser] 알림 표시 시작:', { medicineName, message, audioFileName });

    // 기존 알림이 있으면 제거
    this.hideNotification();

    this.overlay = document.createElement('div');
    this.overlay.className = 'dispense-notification';
    this.overlay.innerHTML = `
      <div class="dispense-card">
        <div class="dispense-icon">💊</div>
        <div class="dispense-message">${message}</div>
      </div>
    `;

    this.addStyles();
    document.body.appendChild(this.overlay);

    setTimeout(() => {
      this.overlay.classList.add('show');
    }, 10);

    this.playAudio(audioFileName);

    setTimeout(() => {
      this.hideNotification();
    }, 3000);
  }

  /**
   * 음성 파일 재생
   * @param {string} fileName - 음성 파일명
   */
  playAudio(fileName) {
    console.log('[MedicineDispenser] 오디오 재생 시작:', fileName);

    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }

    try {
      const audioPath = `/static/carepill/audio/${fileName}`;
      console.log('[MedicineDispenser] 오디오 경로:', audioPath);

      this.currentAudio = new Audio(audioPath);

      this.currentAudio.onended = () => {
        this.currentAudio = null;
      };

      this.currentAudio.onerror = (error) => {
        console.error('음성 재생 오류:', error);
        this.currentAudio = null;
      };

      // ✅ play()는 AudioContext unlock 이후에만 정상 실행됨
      this.currentAudio.play().catch(err => {
        console.warn("[MedicineDispenser] play() 실패 (unlock 전일 수 있음):", err);
      });

    } catch (err) {
      console.error('음성 파일 로드 오류:', err);
    }
  }

  hideNotification() {
    if (this.overlay) {
      this.overlay.classList.remove('show');
      setTimeout(() => {
        if (this.overlay && this.overlay.parentNode) {
          this.overlay.parentNode.removeChild(this.overlay);
        }
        this.overlay = null;
      }, 300);
    }

    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
  }

  addStyles() {
    if (document.getElementById('dispense-notification-styles')) return;

    const style = document.createElement('style');
    style.id = 'dispense-notification-styles';
    style.textContent = `
      .dispense-notification {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
      }
      .dispense-notification.show { opacity: 1; }
      .dispense-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px 40px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        text-align: center;
        min-width: 300px;
        animation: slideUp 0.3s ease;
      }
      @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
      .dispense-icon {
        font-size: 48px;
        margin-bottom: 15px;
        animation: pulse 1.5s infinite;
      }
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }
      .dispense-message {
        font-size: 20px;
        font-weight: 600;
        line-height: 1.4;
      }
    `;
    document.head.appendChild(style);
  }

  dispenseMedicine(medicineName) {
    console.log('[MedicineDispenser] dispenseMedicine 호출됨, 약 이름:', medicineName);

    const medicineMap = {
      '확펜': { message: '확펜이 배출되고 있습니다', audio: '확펜이 배출되고있습니다.mp3' },
      '처방약': { message: '처방약이 배출되고 있습니다', audio: '처방약이 배출되고있습니다.mp3' },
      '킴스약국': { message: '처방약이 배출되고 있습니다', audio: '처방약이 배출되고있습니다.mp3' }
    };

    const medicine = medicineMap[medicineName];
    if (medicine) {
      this.showDispenseNotification(medicineName, medicine.message, medicine.audio);
    } else {
      console.warn('[MedicineDispenser] 알 수 없는 약 이름:', medicineName);
    }
  }
}

// 전역 인스턴스 생성
console.log('[MedicineDispenser] 인스턴스 생성 시작');
window.MedicineDispenser = new MedicineDispenser();
console.log('[MedicineDispenser] 인스턴스 생성 완료');
window.dispenseMedicine = (medicineName) => window.MedicineDispenser.dispenseMedicine(medicineName);
window.dispatchEvent(new CustomEvent('MedicineDispenserReady'));
console.log('[MedicineDispenser] Ready 이벤트 발생');
