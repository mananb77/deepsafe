#!/usr/bin/env python3
"""
Local Detection Test Script

Quick standalone CLI to verify local ML detectors work end-to-end.
No meeting bot, API server, or full pipeline needed.

Usage:
    # Self-test with synthetic data (no files needed)
    poetry run python scripts/test_local_detection.py

    # Test with audio file
    poetry run python scripts/test_local_detection.py --audio path/to/audio.wav

    # Test with video file
    poetry run python scripts/test_local_detection.py --video path/to/video.mp4

    # Test with image
    poetry run python scripts/test_local_detection.py --image path/to/photo.jpg

    # Test with webcam (press q to quit)
    poetry run python scripts/test_local_detection.py --webcam

    # Test social engineering detection (requires: ollama serve)
    poetry run python scripts/test_local_detection.py --transcript "Send the wire transfer now"
    poetry run python scripts/test_local_detection.py --transcript-file path/to/transcript.txt
"""

import argparse
import asyncio
import struct
import sys
import time
import wave
from pathlib import Path

# Ensure project root is on sys.path so `src` is importable
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# ANSI color codes
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def color_for_score(score: float) -> str:
    """Return ANSI color based on risk score (0-100)."""
    if score <= 30:
        return GREEN
    elif score <= 60:
        return YELLOW
    else:
        return RED


def print_header(title: str) -> None:
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}\n")


def print_result(label: str, value, indent: int = 2) -> None:
    prefix = " " * indent
    if isinstance(value, float):
        color = color_for_score(value)
        print(f"{prefix}{DIM}{label}:{RESET} {color}{value:.1f}{RESET}")
    elif isinstance(value, bool):
        color = RED if value else GREEN
        print(f"{prefix}{DIM}{label}:{RESET} {color}{value}{RESET}")
    else:
        print(f"{prefix}{DIM}{label}:{RESET} {value}")


def print_score_bar(score: float, width: int = 30) -> None:
    """Print a visual score bar."""
    filled = int(score / 100 * width)
    color = color_for_score(score)
    bar = f"{color}{'#' * filled}{DIM}{'.' * (width - filled)}{RESET}"
    print(f"  [{bar}] {color}{score:.1f}%{RESET}")


# ---------------------------------------------------------------------------
# Mode 1: Audio file
# ---------------------------------------------------------------------------

async def test_audio(file_path: str) -> None:
    """Test audio deepfake detection on a WAV/MP3 file."""
    from src.services.detection.audio.wav2vec_detector import Wav2VecDetector
    from src.services.detection.audio.detector import AudioDeepfakeDetector
    from src.services.detection.base import AudioChunk

    path = Path(file_path)
    if not path.exists():
        print(f"{RED}File not found: {file_path}{RESET}")
        sys.exit(1)

    print_header(f"Audio Detection: {path.name}")

    # Load audio
    print(f"  Loading {path.suffix} file...")
    if path.suffix.lower() == ".wav":
        with wave.open(str(path), "rb") as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            n_frames = wf.getnframes()
            raw_data = wf.readframes(n_frames)

        duration_s = n_frames / sample_rate
        print_result("Sample rate", f"{sample_rate} Hz")
        print_result("Channels", n_channels)
        print_result("Duration", f"{duration_s:.1f}s")
        print_result("Sample width", f"{sample_width} bytes")

        # Convert to mono PCM16 if needed
        if n_channels == 2:
            # Mix stereo to mono
            samples = struct.unpack(f"<{n_frames * 2}h", raw_data)
            mono = [(samples[i] + samples[i + 1]) // 2 for i in range(0, len(samples), 2)]
            audio_bytes = struct.pack(f"<{len(mono)}h", *mono)
        elif sample_width == 2:
            audio_bytes = raw_data
        else:
            print(f"{YELLOW}  Unsupported sample width {sample_width}, attempting raw pass-through{RESET}")
            audio_bytes = raw_data
    else:
        print(f"{RED}  Unsupported format: {path.suffix}. Use .wav files.{RESET}")
        sys.exit(1)

    # --- Raw Wav2Vec detector ---
    print(f"\n{BOLD}  [1/2] Wav2Vec Detector (raw){RESET}")
    wav2vec = Wav2VecDetector(device="cpu")
    t0 = time.perf_counter()
    raw_result = await wav2vec.analyze(audio_bytes, sample_rate=sample_rate)
    latency = (time.perf_counter() - t0) * 1000

    print_result("Synthetic", raw_result.get("is_synthetic", False))
    print_result("Confidence", raw_result.get("confidence", 0.0))
    print_result("Method", raw_result.get("method", "unknown"))
    print_result("Latency", f"{latency:.0f}ms")
    if raw_result.get("error"):
        print_result("Error", raw_result["error"])
    print()
    print_score_bar(raw_result.get("confidence", 0.0))

    # --- Full AudioDeepfakeDetector ---
    print(f"\n{BOLD}  [2/2] Full Audio Detector (spectral + prosody + wav2vec){RESET}")
    full_detector = AudioDeepfakeDetector(
        enable_api=False,
        enable_local=True,
        local_audio_detector=wav2vec,
    )
    chunk = AudioChunk(
        data=audio_bytes,
        sample_rate=sample_rate,
        duration_ms=int(len(audio_bytes) / (sample_rate * 2) * 1000),
    )
    t0 = time.perf_counter()
    full_result = await full_detector.analyze(chunk)
    latency = (time.perf_counter() - t0) * 1000

    print_result("Detected", full_result.is_detected)
    print_result("Confidence", full_result.confidence)
    print_result("Risk level", full_result.risk_level.value)
    print_result("Latency", f"{latency:.0f}ms")
    if full_result.details.get("method_scores"):
        print(f"  {DIM}Method scores:{RESET}")
        for method, score in full_result.details["method_scores"].items():
            print_result(method, score, indent=4)
    if full_result.error:
        print_result("Errors", full_result.error)
    print()
    print_score_bar(full_result.confidence)


# ---------------------------------------------------------------------------
# Mode 2: Image / Video file
# ---------------------------------------------------------------------------

async def test_image(file_path: str) -> None:
    """Test video deepfake detection on a single image."""
    import cv2
    from src.services.detection.video.efficientnet_detector import EfficientNetDetector
    from src.services.detection.video.detector import VideoDeepfakeDetector
    from src.services.detection.base import VideoFrame

    path = Path(file_path)
    if not path.exists():
        print(f"{RED}File not found: {file_path}{RESET}")
        sys.exit(1)

    print_header(f"Image Detection: {path.name}")

    img = cv2.imread(str(path))
    if img is None:
        print(f"{RED}  Failed to load image{RESET}")
        sys.exit(1)

    h, w = img.shape[:2]
    print_result("Dimensions", f"{w}x{h}")

    _, jpeg_bytes = cv2.imencode(".jpg", img)
    image_bytes = jpeg_bytes.tobytes()

    # --- Raw EfficientNet detector ---
    print(f"\n{BOLD}  [1/2] EfficientNet Detector (raw){RESET}")
    efficientnet = EfficientNetDetector(device="cpu")
    t0 = time.perf_counter()
    raw_result = await efficientnet.analyze(image_bytes)
    latency = (time.perf_counter() - t0) * 1000

    print_result("Deepfake", raw_result.get("is_deepfake", False))
    print_result("Confidence", raw_result.get("confidence", 0.0))
    print_result("Method", raw_result.get("method", "unknown"))
    print_result("Latency", f"{latency:.0f}ms")
    if raw_result.get("error"):
        print_result("Error", raw_result["error"])
    print()
    print_score_bar(raw_result.get("confidence", 0.0))

    # --- Full VideoDeepfakeDetector ---
    print(f"\n{BOLD}  [2/2] Full Video Detector (efficientnet + virtual camera){RESET}")
    full_detector = VideoDeepfakeDetector(
        enable_api=False,
        enable_local=True,
        local_video_detector=efficientnet,
    )
    frame = VideoFrame(data=image_bytes, width=w, height=h, format="jpeg")
    t0 = time.perf_counter()
    full_result = await full_detector.analyze([frame])
    latency = (time.perf_counter() - t0) * 1000

    print_result("Detected", full_result.is_detected)
    print_result("Confidence", full_result.confidence)
    print_result("Risk level", full_result.risk_level.value)
    print_result("Latency", f"{latency:.0f}ms")
    if full_result.details.get("method_scores"):
        print(f"  {DIM}Method scores:{RESET}")
        for method, score in full_result.details["method_scores"].items():
            print_result(method, score, indent=4)
    print()
    print_score_bar(full_result.confidence)


async def test_video(file_path: str) -> None:
    """Test video deepfake detection on a video file."""
    import cv2
    from src.services.detection.video.efficientnet_detector import EfficientNetDetector
    from src.services.detection.video.detector import VideoDeepfakeDetector
    from src.services.detection.base import VideoFrame

    path = Path(file_path)
    if not path.exists():
        print(f"{RED}File not found: {file_path}{RESET}")
        sys.exit(1)

    print_header(f"Video Detection: {path.name}")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        print(f"{RED}  Failed to open video{RESET}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_s = total_frames / fps if fps > 0 else 0

    print_result("Resolution", f"{w}x{h}")
    print_result("FPS", f"{fps:.1f}")
    print_result("Duration", f"{duration_s:.1f}s")
    print_result("Total frames", total_frames)

    # Extract frames at ~2 FPS
    sample_interval = max(1, int(fps / 2))
    frames_jpeg: list[bytes] = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % sample_interval == 0:
            _, jpeg = cv2.imencode(".jpg", frame)
            frames_jpeg.append(jpeg.tobytes())
        frame_idx += 1

    cap.release()
    print_result("Sampled frames", len(frames_jpeg))

    if not frames_jpeg:
        print(f"{RED}  No frames extracted{RESET}")
        return

    # --- Raw EfficientNet per-frame ---
    print(f"\n{BOLD}  [1/2] EfficientNet Detector (per-frame){RESET}")
    efficientnet = EfficientNetDetector(device="cpu")
    t0 = time.perf_counter()
    video_result = await efficientnet.analyze_video(frames_jpeg, sample_rate=1)
    latency = (time.perf_counter() - t0) * 1000

    print_result("Deepfake", video_result.get("is_deepfake", False))
    print_result("Confidence", video_result.get("confidence", 0.0))
    print_result("Frames analyzed", video_result.get("frames_analyzed", 0))
    print_result("Frames with deepfake", video_result.get("frames_with_deepfake", 0))
    print_result("Latency", f"{latency:.0f}ms")
    print()
    print_score_bar(video_result.get("confidence", 0.0))

    # --- Full VideoDeepfakeDetector ---
    print(f"\n{BOLD}  [2/2] Full Video Detector (efficientnet + virtual camera){RESET}")
    full_detector = VideoDeepfakeDetector(
        enable_api=False,
        enable_local=True,
        local_video_detector=efficientnet,
    )
    video_frames = [
        VideoFrame(data=fb, width=w, height=h, format="jpeg")
        for fb in frames_jpeg
    ]
    t0 = time.perf_counter()
    full_result = await full_detector.analyze(video_frames)
    latency = (time.perf_counter() - t0) * 1000

    print_result("Detected", full_result.is_detected)
    print_result("Confidence", full_result.confidence)
    print_result("Risk level", full_result.risk_level.value)
    print_result("Latency", f"{latency:.0f}ms")
    if full_result.details.get("method_scores"):
        print(f"  {DIM}Method scores:{RESET}")
        for method, score in full_result.details["method_scores"].items():
            print_result(method, score, indent=4)
    print()
    print_score_bar(full_result.confidence)


# ---------------------------------------------------------------------------
# Mode 3: Webcam
# ---------------------------------------------------------------------------

async def test_webcam() -> None:
    """Live webcam deepfake detection."""
    import cv2
    from src.services.detection.video.efficientnet_detector import EfficientNetDetector

    print_header("Webcam Detection (press 'q' to quit)")

    efficientnet = EfficientNetDetector(device="cpu")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(f"{RED}  Failed to open webcam{RESET}")
        sys.exit(1)

    print("  Warming up detector on first frame...\n")
    frame_count = 0
    interval = 0.5  # ~2 FPS analysis rate

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"{RED}  Failed to read frame{RESET}")
                break

            _, jpeg = cv2.imencode(".jpg", frame)
            image_bytes = jpeg.tobytes()

            t0 = time.perf_counter()
            result = await efficientnet.analyze(image_bytes)
            latency = (time.perf_counter() - t0) * 1000

            score = result.get("confidence", 0.0)
            is_df = result.get("is_deepfake", False)
            color = color_for_score(score)
            method = result.get("method", "?")

            frame_count += 1
            bar_width = 20
            filled = int(score / 100 * bar_width)
            bar = f"{color}{'#' * filled}{'.' * (bar_width - filled)}{RESET}"

            print(
                f"\r  Frame {frame_count:4d} | "
                f"[{bar}] {color}{score:5.1f}%{RESET} | "
                f"deepfake={color}{is_df}{RESET} | "
                f"{method} | {latency:.0f}ms",
                end="",
                flush=True,
            )

            # Check for 'q' key via OpenCV window (if display available)
            cv2.imshow("DeepSafe Webcam Test", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            await asyncio.sleep(interval)

    except KeyboardInterrupt:
        pass
    finally:
        print(f"\n\n  Processed {frame_count} frames.")
        cap.release()
        cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# Mode 4: Transcript
# ---------------------------------------------------------------------------

async def test_transcript(text: str) -> None:
    """Test social engineering detection on a transcript."""
    from src.services.detection.social_engineering.ollama_analyzer import OllamaAnalyzer

    print_header("Social Engineering Detection (Ollama)")

    analyzer = OllamaAnalyzer()

    # Health check
    print("  Checking Ollama connection...")
    healthy = await analyzer.health_check()
    if not healthy:
        print(f"{RED}  Ollama is not running. Start it with: ollama serve{RESET}")
        print(f"{DIM}  Then pull a model: ollama pull phi3:mini{RESET}")
        sys.exit(1)
    print(f"  {GREEN}Ollama connected{RESET} (model: {analyzer.model})\n")

    print(f"  {DIM}Transcript:{RESET}")
    # Print truncated transcript
    display = text[:200] + "..." if len(text) > 200 else text
    for line in display.split("\n"):
        print(f"    {line}")
    print()

    t0 = time.perf_counter()
    result = await analyzer.analyze(text)
    latency = (time.perf_counter() - t0) * 1000

    score = result.confidence
    color = color_for_score(score)

    print_result("Suspicious", result.is_suspicious)
    print_result("Confidence", result.confidence)
    print_result("Intent", result.intent_classification)
    print_result("Risk", result.risk_assessment)
    print_result("Latency", f"{latency:.0f}ms")

    if result.manipulation_tactics:
        print(f"  {DIM}Tactics:{RESET}")
        for tactic in result.manipulation_tactics:
            print(f"    {RED}- {tactic}{RESET}")

    if result.reasoning:
        print(f"\n  {DIM}Reasoning:{RESET}")
        for line in result.reasoning.split("\n"):
            print(f"    {line}")

    if result.recommendations:
        print(f"\n  {DIM}Recommendations:{RESET}")
        for rec in result.recommendations:
            print(f"    {YELLOW}- {rec}{RESET}")

    print()
    print_score_bar(score)

    if result.details.get("error"):
        print(f"\n  {RED}Error: {result.details['error']}{RESET}")


# ---------------------------------------------------------------------------
# Default: Self-test with synthetic data
# ---------------------------------------------------------------------------

async def test_all() -> None:
    """Run self-test with synthetic data to verify all detectors load."""
    print_header("Self-Test: All Local Detectors")

    passed = 0
    failed = 0

    # --- Audio ---
    print(f"{BOLD}  [1/3] Audio Deepfake Detector{RESET}")
    try:
        from src.services.detection.audio.wav2vec_detector import Wav2VecDetector
        from src.services.detection.base import AudioChunk

        wav2vec = Wav2VecDetector(device="cpu")

        # Generate 2 seconds of silence at 16kHz (PCM16)
        sample_rate = 16000
        duration_s = 2
        n_samples = sample_rate * duration_s
        silence = b"\x00\x00" * n_samples

        t0 = time.perf_counter()
        result = await wav2vec.analyze(silence, sample_rate=sample_rate)
        latency = (time.perf_counter() - t0) * 1000

        print_result("Status", f"{GREEN}OK{RESET}")
        print_result("Confidence", result.get("confidence", 0.0))
        print_result("Method", result.get("method", "unknown"))
        print_result("Latency", f"{latency:.0f}ms")
        if result.get("error"):
            print_result("Note", result["error"])
        passed += 1
    except Exception as e:
        print_result("Status", f"{RED}FAILED{RESET}")
        print_result("Error", str(e))
        failed += 1

    # --- Video ---
    print(f"\n{BOLD}  [2/3] Video Deepfake Detector{RESET}")
    try:
        from src.services.detection.video.efficientnet_detector import EfficientNetDetector

        efficientnet = EfficientNetDetector(device="cpu")

        # Generate a test JPEG image — try cv2 first, then PIL, then raw minimal JPEG
        image_bytes: bytes
        try:
            import cv2
            import numpy as np
            img = np.full((224, 224, 3), (255, 0, 0), dtype=np.uint8)
            _, jpeg = cv2.imencode(".jpg", img)
            image_bytes = jpeg.tobytes()
        except ImportError:
            try:
                from PIL import Image
                import io
                img = Image.new("RGB", (224, 224), (0, 0, 255))
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                image_bytes = buf.getvalue()
            except ImportError:
                # Minimal 1x1 red JPEG (valid JFIF)
                image_bytes = (
                    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01"
                    b"\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06"
                    b"\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b"
                    b"\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c"
                    b"\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0"
                    b"\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4"
                    b"\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00"
                    b"\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06"
                    b"\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03"
                    b"\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02"
                    b"\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81"
                    b"\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16"
                    b"\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghij"
                    b"stuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94"
                    b"\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8"
                    b"\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3"
                    b"\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7"
                    b"\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea"
                    b"\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00"
                    b"\x08\x01\x01\x00\x00?\x00T\xdb\xa8\xa0\x03\xa5\x14\x00"
                    b"\x1f\xff\xd9"
                )
                print_result("Note", "cv2/PIL unavailable, using minimal JPEG")

        t0 = time.perf_counter()
        result = await efficientnet.analyze(image_bytes)
        latency = (time.perf_counter() - t0) * 1000

        print_result("Status", f"{GREEN}OK{RESET}")
        print_result("Confidence", result.get("confidence", 0.0))
        print_result("Method", result.get("method", "unknown"))
        print_result("Latency", f"{latency:.0f}ms")
        if result.get("error"):
            print_result("Note", result["error"])
        passed += 1
    except Exception as e:
        print_result("Status", f"{RED}FAILED{RESET}")
        print_result("Error", str(e))
        failed += 1

    # --- Social Engineering ---
    print(f"\n{BOLD}  [3/3] Social Engineering Detector (Ollama){RESET}")
    try:
        from src.services.detection.social_engineering.ollama_analyzer import OllamaAnalyzer

        analyzer = OllamaAnalyzer()
        healthy = await analyzer.health_check()

        if not healthy:
            print_result("Status", f"{YELLOW}SKIPPED{RESET}")
            print_result("Reason", "Ollama not running (ollama serve)")
        else:
            transcript = (
                "This is the CEO speaking. I need you to wire $50,000 to this account "
                "immediately. Don't tell anyone about this, it's confidential. "
                "The account number is 1234567890. Do it now before the market closes."
            )

            t0 = time.perf_counter()
            result = await analyzer.analyze(transcript)
            latency = (time.perf_counter() - t0) * 1000

            print_result("Status", f"{GREEN}OK{RESET}")
            print_result("Suspicious", result.is_suspicious)
            print_result("Confidence", result.confidence)
            print_result("Intent", result.intent_classification)
            print_result("Latency", f"{latency:.0f}ms")
            if result.details.get("error"):
                print_result("Note", result.details["error"])
            passed += 1
    except Exception as e:
        print_result("Status", f"{RED}FAILED{RESET}")
        print_result("Error", str(e))
        failed += 1

    # --- Summary ---
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    total = passed + failed
    if failed == 0:
        print(f"  {GREEN}All {passed}/{total} detectors passed{RESET}")
    else:
        print(f"  {YELLOW}{passed}/{total} passed, {RED}{failed} failed{RESET}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Test local deepfake detection models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                     # Self-test all detectors
  %(prog)s --audio recording.wav               # Test audio file
  %(prog)s --image photo.jpg                   # Test single image
  %(prog)s --video clip.mp4                    # Test video file
  %(prog)s --webcam                            # Live webcam detection
  %(prog)s --transcript "Wire the money now"   # Test social engineering
  %(prog)s --transcript-file transcript.txt    # Test from file
        """,
    )
    parser.add_argument("--audio", metavar="FILE", help="WAV audio file to test")
    parser.add_argument("--video", metavar="FILE", help="MP4/AVI video file to test")
    parser.add_argument("--image", metavar="FILE", help="JPG/PNG image file to test")
    parser.add_argument("--webcam", action="store_true", help="Live webcam detection")
    parser.add_argument("--transcript", metavar="TEXT", help="Transcript text to analyze")
    parser.add_argument("--transcript-file", metavar="FILE", help="Transcript file to analyze")

    args = parser.parse_args()

    # Determine which mode to run
    if args.audio:
        asyncio.run(test_audio(args.audio))
    elif args.image:
        asyncio.run(test_image(args.image))
    elif args.video:
        asyncio.run(test_video(args.video))
    elif args.webcam:
        asyncio.run(test_webcam())
    elif args.transcript:
        asyncio.run(test_transcript(args.transcript))
    elif args.transcript_file:
        path = Path(args.transcript_file)
        if not path.exists():
            print(f"{RED}File not found: {args.transcript_file}{RESET}")
            sys.exit(1)
        text = path.read_text()
        asyncio.run(test_transcript(text))
    else:
        # Default: run all self-tests
        asyncio.run(test_all())


if __name__ == "__main__":
    main()
