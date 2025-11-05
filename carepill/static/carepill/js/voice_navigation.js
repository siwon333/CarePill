/**
 * Voice Command Navigation System
 * 음성 명령으로 페이지 이동 기능
 * localStorage로 상태 유지
 */

/***************************************************************
 *  AudioContext unlock – 사용자 인터랙션 후에만 실행
 ***************************************************************/
window.unlockAudioContext = function () {
    try {
        if (!window.audioCtx) return; // AudioContext 가 없다면 실행 X

        if (window.audioCtx.state === "suspended") {
            console.log("[AudioContext] 🎵 Unlocking...");
            window.audioCtx.resume().then(() => {
                console.log("[AudioContext] ✅ Unlocked");
            });
        }
    } catch (err) {
        console.error("[AudioContext] ❌ Unlock Failed:", err);
    }
};

// ✅ 클릭 or 터치 이벤트가 발생했을 때 AudioContext unlock (단 1회만)
document.addEventListener(
    "click",
    () => {
        console.log("[AudioContext] User interaction detected → Attempt unlock");
        window.unlockAudioContext();
    },
    { once: true }
);

console.log("[HOME INLINE] Audio unlock listener registered");


class VoiceNavigator {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.statusCallback = null;
        this.commandCallback = null;
        this.storageKey = 'voice_navigation_enabled';

        // 음성 명령 매핑
        this.commandMap = {
            '홈': '/',
            '홈으로': '/',
            '홈화면': '/',
            '메인': '/',
            '처음으로': '/',
            '메인화면': '/',

            '처방약': '/how2green/',
            '처방': '/how2green/',
            '병원약': '/how2green/',

            '상비약': '/how2green/',
            'OTC': '/how2green/',
            '약국약': '/how2green/',
            '머리': '/how2green/',


            '약봉지스캔': '/scan/',
            '약 봉지 스캔': '/scan/',
            '봉지스캔': '/scan/',
            '봉투스캔': '/scan/',
            '약봉투스캔': '/scan/',

            '음성등록': '/voice_setup/',
            '음성 등록': '/voice_setup/',
            '등록': '/voice_setup/',

            '약투입': '/scan/',
            '약 투입': '/scan/',
            '약봉투': '/scan/',

            '현재있는약': '/meds/',
            '현재 있는 약': '/meds/',
            '약목록': '/meds/',
            '내약': '/meds/',

            '말하기': '/voice/',
            '음성': '/voice/',
            '대화': '/voice/',

            '약분출': '/how2green/',
            '약 분출': '/how2green/',
            '분출': '/how2green/'
        };

        this.initRecognition();
    }

    /**
     * Web Speech API 초기화
     */
    initRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('이 브라우저는 음성 인식을 지원하지 않습니다.');
            return false;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        // 한국어 설정
        this.recognition.lang = 'ko-KR';
        this.recognition.continuous = true;  // 연속 인식
        this.recognition.interimResults = false;  // 최종 결과만
        this.recognition.maxAlternatives = 3;  // 대안 결과 3개

        // 이벤트 리스너 설정
        this.recognition.onstart = () => this.handleStart();
        this.recognition.onresult = (event) => this.handleResult(event);
        this.recognition.onerror = (event) => this.handleError(event);
        this.recognition.onend = () => this.handleEnd();

        return true;
    }

    /**
     * 음성 인식 활성화 상태 확인
     */
    isEnabled() {
        return localStorage.getItem(this.storageKey) === 'true';
    }

    /**
     * 음성 인식 활성화 상태 저장
     */
    setEnabled(enabled) {
        if (enabled) {
            localStorage.setItem(this.storageKey, 'true');
        } else {
            localStorage.removeItem(this.storageKey);
        }
    }

    /**
     * 음성 인식 토글 (켜기/끄기)
     */
    toggle(statusCallback, commandCallback) {
        if (this.isEnabled()) {
            // 비활성화
            this.stop();
            this.setEnabled(false);
            console.log('음성 인식 비활성화');
            return false;
        } else {
            // 활성화
            this.start(statusCallback, commandCallback);
            this.setEnabled(true);
            console.log('음성 인식 활성화');
            return true;
        }
    }

    /**
     * 음성 인식 시작
     */
    start(statusCallback, commandCallback) {
        if (!this.recognition) {
            console.error('음성 인식을 사용할 수 없습니다.');
            return false;
        }

        if (this.isListening) {
            console.log('이미 음성 인식 중입니다');
            return true;
        }

        this.statusCallback = statusCallback;
        this.commandCallback = commandCallback;

        try {
            this.recognition.start();
            return true;
        } catch (error) {
            console.error('음성 인식 시작 실패:', error);
            return false;
        }
    }

    /**
     * 음성 인식 중지
     */
    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    /**
     * 페이지 로드 시 자동 시작
     */
    autoStart(statusCallback, commandCallback) {
        if (this.isEnabled()) {
            console.log('자동으로 음성 인식 시작');
            this.start(statusCallback, commandCallback);
        }
    }

    /**
     * 음성 인식 시작 이벤트
     */
    handleStart() {
        this.isListening = true;
        console.log('음성 인식 시작됨');

        if (this.statusCallback) {
            this.statusCallback('listening', '듣고 있습니다...');
        }
    }

    /**
     * 음성 인식 결과 처리
     */
    handleResult(event) {
        const last = event.results.length - 1;
        const result = event.results[last];

        // 최종 결과만 처리
        if (!result.isFinal) return;

        // 모든 대안 결과 확인
        for (let i = 0; i < result.length; i++) {
            const transcript = result[i].transcript.trim();
            console.log(`인식된 음성 (${i}): ${transcript}`);

            // 약 배출 명령어 우선 체크
            const medicineCommand = this.checkMedicineDispense(transcript);
            if (medicineCommand) {
                console.log(`약 배출 명령 인식: ${medicineCommand}`);

                if (this.statusCallback) {
                    this.statusCallback('recognized', `"${medicineCommand}" 배출 명령 인식됨`);
                }

                // 약 배출 실행
                console.log('[약 배출] window.MedicineDispenser 체크:', window.MedicineDispenser);
                console.log('[약 배출] typeof window.MedicineDispenser:', typeof window.MedicineDispenser);

                if (window.MedicineDispenser) {
                    console.log('[약 배출] MedicineDispenser 발견, dispenseMedicine 호출');
                    window.MedicineDispenser.dispenseMedicine(medicineCommand);
                } else {
                    console.error('[약 배출] MedicineDispenser를 찾을 수 없습니다');
                    console.error('[약 배출] window 객체의 키들:', Object.keys(window).filter(k => k.includes('Medicine')));

                    // 대기 후 재시도
                    console.log('[약 배출] 1초 후 재시도...');
                    setTimeout(() => {
                        if (window.MedicineDispenser) {
                            console.log('[약 배출] 재시도 성공!');
                            window.MedicineDispenser.dispenseMedicine(medicineCommand);
                        } else {
                            console.error('[약 배출] 재시도 실패');
                        }
                    }, 1000);
                }

                return;
            }

            // 페이지 네비게이션 명령어 매칭
            const command = this.matchCommand(transcript);
            if (command) {
                console.log(`명령어 매칭: ${command.text} → ${command.url}`);

                if (this.commandCallback) {
                    this.commandCallback(command.text, command.url);
                }

                if (this.statusCallback) {
                    this.statusCallback('recognized', `"${command.text}" 명령 인식됨`);
                }

                // 페이지 이동 (1초 후)
                setTimeout(() => {
                    window.location.href = command.url;
                }, 1000);

                return;
            }
        }

        // 매칭되지 않은 명령
        if (this.statusCallback) {
            this.statusCallback('unknown', `인식되지 않은 명령: ${result[0].transcript}`);
        }
    }

    /**
     * 약 배출 명령어 체크 (페이지 네비게이션보다 우선)
     */
    checkMedicineDispense(text) {
        const normalized = text.replace(/\s+/g, '').toLowerCase();
        console.log('[약 배출 체크] 정규화된 텍스트:', normalized);

        // "확펜 좀 줘", "확펜 줘", "머리아픈데" 등
        if (normalized.includes('확펜') || normalized.includes('확팬')) {
            if (normalized.includes('줘') || normalized.includes('주세요') || normalized.includes('주십시오')) {
                return '확펜';
            }
        }

        // 머리 아픈 증상 -> 확펜
        if (normalized.includes('머리') && (normalized.includes('아프') || normalized.includes('아픈') || normalized.includes('아파'))) {
            console.log('[약 배출 체크] 머리아픔 증상 감지 -> 확펜');
            return '확펜';
        }

        // "킴스약국에서 받은 약 줘", "처방약 줘", "병원약 줘" 등
        // 발음 변형 처리: 킴스, 김치, 김씨
        const hasPrescriptionKeyword = normalized.includes('킴스약국') || normalized.includes('킴스') ||
            normalized.includes('김치약국') || normalized.includes('김치') ||
            normalized.includes('김씨약국') || normalized.includes('김씨') ||
            normalized.includes('처방약') || normalized.includes('병원약');

        if (hasPrescriptionKeyword) {
            if (normalized.includes('줘') || normalized.includes('주세요') ||
                normalized.includes('주십시오') || normalized.includes('받은') || normalized.includes('약초')) {
                console.log('[약 배출 체크] 처방약 키워드 매칭됨!');
                return '처방약';
            }
        }

        return null;
    }

    /**
     * 명령어 매칭
     */
    matchCommand(text) {
        const normalized = text.replace(/\s+/g, '').toLowerCase();

        // 정확한 매칭 시도
        for (const [key, url] of Object.entries(this.commandMap)) {
            const normalizedKey = key.replace(/\s+/g, '').toLowerCase();
            if (normalized.includes(normalizedKey)) {
                return { text: key, url: url };
            }
        }

        // 부분 매칭 시도
        if (normalized.includes('홈') || normalized.includes('메인') || normalized.includes('처음')) {
            return { text: '홈', url: '/' };
        }
        if (normalized.includes('봉지') && normalized.includes('스캔')) {
            return { text: '약봉지 스캔', url: '/scan/' };
        }
        if (normalized.includes('음성') && normalized.includes('등록')) {
            return { text: '음성 등록', url: '/voice_setup/' };
        }
        if (normalized.includes('투입') || (normalized.includes('스캔') && !normalized.includes('봉지') && !normalized.includes('봉투'))) {
            return { text: '약투입', url: '/scan/' };
        }
        if (normalized.includes('목록') || normalized.includes('현재')) {
            return { text: '현재있는 약', url: '/meds/' };
        }
        if (normalized.includes('말하기') || normalized.includes('대화')) {
            return { text: '말하기', url: '/voice/' };
        }
        if (normalized.includes('분출')) {
            return { text: '약분출', url: '/how2green/' };
        }
        if (normalized.includes('등록') && !normalized.includes('음성')) {
            return { text: '음성 등록', url: '/voice_setup/' };
        
        }
        return null;    
    

    /**
     * 에러 처리
     */
    handleError(event) 
        console.error('음성 인식 오류:', event.error);

        let errorMessage = '';
        switch (event.error) {
            case 'no-speech':
                errorMessage = '음성이 감지되지 않았습니다';
                break;
            case 'audio-capture':
                errorMessage = '마이크를 찾을 수 없습니다';
                break;
            case 'not-allowed':
                errorMessage = '마이크 권한이 거부되었습니다';
                break;
            case 'network':
                errorMessage = '네트워크 오류가 발생했습니다';
                break;
            default:
                errorMessage = `오류: ${event.error}`;
        }

        if (this.statusCallback) {
            this.statusCallback('error', errorMessage);
        }
    }

    /**
     * 음성 인식 종료 이벤트
     */
    handleEnd() {
        this.isListening = false;
        console.log('음성 인식 종료됨');

        if (this.statusCallback) {
            this.statusCallback('stopped', '음성 인식이 중지되었습니다');
        }

        // 활성화 상태면 자동으로 재시작
        if (this.isEnabled()) {
            console.log('음성 인식 자동 재시작');
            setTimeout(() => {
                this.start(this.statusCallback, this.commandCallback);
            }, 1000);
        }
    }

    /**
     * 지원 여부 확인
     */
    static isSupported() {
        return ('webkitSpeechRecognition' in window) || ('SpeechRecognition' in window);
    }
}

// 전역 인스턴스
window.voiceNavigator = new VoiceNavigator();
