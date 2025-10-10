"""
GPT-SoVITS TTS Service
Zero-shot Text-to-Speech with voice cloning
"""
import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class GPTSoVITSService:
    """GPT-SoVITS TTS 서비스 클래스 (싱글톤)"""

    _instance = None
    _model_loaded = False

    def __new__(cls):
        """싱글톤 패턴 - 서버당 모델 1개만 로드"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._model_loaded:
            self.model_path = os.getenv('GPTSOVITS_MODEL_PATH', './models/gpt-sovits-v2')
            self.device = os.getenv('GPTSOVITS_DEVICE', 'cpu')  # 'cuda' or 'cpu'
            self._load_model()

    def _load_model(self):
        """모델 로드 (서버 시작 시 1회)"""
        try:
            logger.info(f"Loading GPT-SoVITS model from {self.model_path}")

            # TODO: 실제 GPT-SoVITS 모델 로드
            # GPT-SoVITS 라이브러리 설치 후 아래 코드 활성화
            #
            # from GPTSoVITS.TTS_infer_pack.TTS import TTS
            # self.tts = TTS()
            # self.tts.load_model(self.model_path, device=self.device)

            # 현재는 Mock으로 대체 (개발/테스트용)
            self.tts = None
            logger.warning("GPT-SoVITS Mock mode - using dummy TTS")

            self._model_loaded = True
            logger.info("GPT-SoVITS service initialized")

        except Exception as e:
            logger.error(f"Failed to load GPT-SoVITS model: {e}")
            raise

    def generate_speech(
        self,
        text: str,
        reference_audio_path: str,
        output_path: str,
        language: str = "ko"
    ) -> dict:
        """
        Zero-shot TTS 생성

        Args:
            text: 생성할 텍스트 (예: "약 드실 시간입니다")
            reference_audio_path: 참조 음성 파일 경로 (사용자 음성 샘플)
            output_path: 출력 파일 경로
            language: 언어 코드 (ko, en, ja, zh, yue)

        Returns:
            dict: {
                'success': bool,
                'output_path': str,
                'processing_time_ms': float,
                'error': str (optional)
            }
        """
        start_time = time.time()

        try:
            logger.info(f"Generating TTS for text: '{text[:50]}...'")
            logger.info(f"Reference audio: {reference_audio_path}")

            # TODO: 실제 GPT-SoVITS TTS 생성
            # GPT-SoVITS 라이브러리 설치 후 아래 코드 활성화
            #
            # self.tts.generate(
            #     text=text,
            #     ref_audio_path=reference_audio_path,
            #     language=language,
            #     output_path=output_path
            # )

            # Mock 구현 (개발/테스트용)
            # 실제로는 참조 음성을 복사 (나중에 실제 TTS로 교체)
            import shutil
            if os.path.exists(reference_audio_path):
                shutil.copy(reference_audio_path, output_path)
                logger.info(f"Mock TTS: copied reference audio to {output_path}")
            else:
                raise FileNotFoundError(f"Reference audio not found: {reference_audio_path}")

            processing_time = (time.time() - start_time) * 1000

            logger.info(f"TTS generated in {processing_time:.2f}ms")

            return {
                'success': True,
                'output_path': output_path,
                'processing_time_ms': processing_time
            }

        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def is_ready(self) -> bool:
        """모델 로드 완료 여부"""
        return self._model_loaded

    def check_health(self) -> dict:
        """
        서비스 헬스 체크

        Returns:
            dict: {
                'is_available': bool,
                'model_loaded': bool,
                'device': str,
                'mock_mode': bool
            }
        """
        return {
            'is_available': self.is_ready(),
            'model_loaded': self._model_loaded,
            'device': self.device,
            'mock_mode': self.tts is None  # True if using mock mode
        }
