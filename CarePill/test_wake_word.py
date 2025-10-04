"""
Wake Word Detection Test Script
Test "carepill" wake word using Porcupine
"""

import os
import sys
import pvporcupine
import pyaudio
import struct
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_wake_word():
    """Test carepill wake word detection"""

    # 1. Check environment variables
    access_key = os.getenv('PORCUPINE_ACCESS_KEY')
    porcupine_model_path = os.getenv('PORCUPINE_MODEL_PATH')
    keyword_model_path = os.getenv('WAKE_WORD_MODEL_PATH')

    print("="*60)
    print("[INFO] Porcupine Wake Word Test - Korean")
    print("="*60)
    print()

    if not access_key:
        print("[ERROR] PORCUPINE_ACCESS_KEY not found in .env!")
        print("[TIP] Add your Picovoice access key to .env file")
        return False

    if not porcupine_model_path or not os.path.exists(porcupine_model_path):
        print(f"[ERROR] Korean language model file not found: {porcupine_model_path}")
        print("[TIP] Check PORCUPINE_MODEL_PATH in .env file")
        return False

    if not keyword_model_path or not os.path.exists(keyword_model_path):
        print(f"[ERROR] Wake word keyword file not found: {keyword_model_path}")
        print("[TIP] Check WAKE_WORD_MODEL_PATH in .env file")
        return False

    print(f"[OK] Access Key: {access_key[:20]}...")
    print(f"[OK] Korean Language Model: {porcupine_model_path}")
    print(f"[OK] Keyword Model: {keyword_model_path}")
    print()

    # 2. Initialize Porcupine with Korean model
    try:
        # Sensitivity: 0.0 (least sensitive) to 1.0 (most sensitive)
        # Default is 0.5, we'll use 0.7 for better detection
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[keyword_model_path],
            model_path=porcupine_model_path,
            sensitivities=[0.7]  # Increased from default 0.5
        )
        print(f"[OK] Porcupine initialized successfully!")
        print(f"[INFO] Sample Rate: {porcupine.sample_rate} Hz")
        print(f"[INFO] Frame Length: {porcupine.frame_length}")
        print(f"[INFO] Sensitivity: 0.7 (increased for better detection)")
        print()
    except Exception as e:
        print(f"[ERROR] Porcupine initialization failed: {e}")
        print()
        print("[TROUBLESHOOTING]")
        print("  1. Check if access key is valid")
        print("  2. Verify model file path")
        print("  3. Ensure model matches your platform (Windows)")
        return False

    # 3. Initialize audio stream
    pa = pyaudio.PyAudio()

    try:
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        print("[OK] Microphone stream initialized!")
        print()
    except Exception as e:
        print(f"[ERROR] Microphone initialization failed: {e}")
        print()
        print("[TROUBLESHOOTING]")
        print("  1. Check if microphone is connected")
        print("  2. Allow microphone access in Windows settings")
        print("  3. Try restarting the script")
        porcupine.delete()
        pa.terminate()
        return False

    # 4. Start wake word detection
    print("="*60)
    print('[LISTENING] Say "carepill" (케어필) in Korean to test!')
    print("[INFO] Press Ctrl+C to stop")
    print("="*60)
    print()

    detection_count = 0
    frame_count = 0

    try:
        while True:
            # Read audio frame
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            # Show audio level every 30 frames (~1 second at 16kHz/512 frame)
            frame_count += 1
            if frame_count % 30 == 0:
                import numpy as np
                volume = int(np.abs(np.array(pcm)).mean())
                print(f"[DEBUG] Audio level: {volume:5d} (speak if this is near 0)", end="\r", flush=True)

            # Detect wake word
            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                detection_count += 1
                print(f"\n[DETECTED #{detection_count}] Wake word 'carepill' detected!")
                print("[SUCCESS] Voice recognition is working!\n")

    except KeyboardInterrupt:
        print("\n")
        print("="*60)
        print("[STOPPED] Test stopped by user")
        print("="*60)

    finally:
        # 5. Cleanup
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

        print()
        print("[SUMMARY]")
        print(f"  Total detections: {detection_count}")

        if detection_count > 0:
            print("  Status: SUCCESS - Wake word is working!")
            print()
            print("[NEXT STEPS]")
            print("  1. Integrate with Naver STT API")
            print("  2. Build complete voice assistant pipeline")
            print("  3. Start Django integration")
        else:
            print("  Status: No detections")
            print()
            print("[TIPS]")
            print("  1. Speak clearly: 'care-pill' or '케-어-필'")
            print("  2. Adjust microphone volume")
            print("  3. Reduce background noise")

        print()
        print("[OK] Cleanup complete")

        return detection_count > 0

if __name__ == "__main__":
    success = test_wake_word()
    sys.exit(0 if success else 1)
