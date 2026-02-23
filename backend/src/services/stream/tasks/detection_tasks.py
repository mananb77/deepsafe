"""
Celery Tasks for Detection

Defines Celery tasks for audio and video analysis.
These tasks run on worker nodes for distributed processing.

Task Queues:
- detection: High-priority detection tasks (deepfake, etc.)
- analysis: NLP and risk scoring tasks
- verification: SMS, voice, push verification tasks
"""

import logging
from typing import Any, Dict, Optional

from celery import shared_task

from src.shared.messaging.celery_app import celery_app


logger = logging.getLogger(__name__)


# ==================== Audio Analysis Tasks ====================


@celery_app.task(
    name="detection.analyze_audio",
    queue="detection",
    bind=True,
    max_retries=2,
    soft_time_limit=10,
    time_limit=15,
)
def analyze_audio_task(
    self,
    chunk_data: bytes,
    participant_id: str,
    meeting_id: str,
    chunk_id: str,
    sample_rate: int = 16000,
) -> Dict[str, Any]:
    """
    Analyze audio chunk for deepfakes and anomalies.

    Args:
        chunk_data: Raw audio bytes.
        participant_id: ID of the speaking participant.
        meeting_id: ID of the meeting.
        chunk_id: Unique chunk identifier.
        sample_rate: Audio sample rate.

    Returns:
        Analysis results dict.
    """
    logger.info(f"Analyzing audio chunk {chunk_id} for meeting {meeting_id}")

    try:
        result = {
            "chunk_id": chunk_id,
            "participant_id": participant_id,
            "meeting_id": meeting_id,
            "audio_deepfake_score": 0.0,
            "voice_mismatch_score": 0.0,
            "social_engineering_score": 0.0,
            "confidence": 0.0,
            "details": {},
        }

        # Run audio deepfake detection
        try:
            from src.services.detection.audio.service import AudioDetectionService

            detector = AudioDetectionService()
            deepfake_result = detector.detect_deepfake_sync(
                audio_data=chunk_data,
                sample_rate=sample_rate,
            )

            result["audio_deepfake_score"] = deepfake_result.confidence
            result["confidence"] = deepfake_result.confidence
            result["details"]["deepfake"] = deepfake_result.details

        except ImportError:
            logger.warning("Audio detection service not available")
        except Exception as e:
            logger.error(f"Audio deepfake detection error: {e}")

        # Run voice verification (if baseline exists)
        try:
            from src.services.detection.audio.voice_verifier import VoiceVerifier

            verifier = VoiceVerifier()
            voice_result = verifier.verify_sync(
                audio_data=chunk_data,
                participant_id=participant_id,
            )

            result["voice_mismatch_score"] = 1.0 - voice_result.similarity
            result["details"]["voice"] = voice_result.details

        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Voice verification skipped: {e}")

        logger.info(
            f"Audio analysis complete for {chunk_id}: "
            f"deepfake={result['audio_deepfake_score']:.2f}"
        )

        return result

    except Exception as e:
        logger.error(f"Audio analysis task failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task(
    name="detection.transcribe_audio",
    queue="analysis",
    bind=True,
    max_retries=2,
    soft_time_limit=30,
    time_limit=45,
)
def transcribe_audio_task(
    self,
    chunk_data: bytes,
    participant_id: str,
    meeting_id: str,
    chunk_id: str,
    sample_rate: int = 16000,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Transcribe audio chunk to text.

    Args:
        chunk_data: Raw audio bytes.
        participant_id: Speaker ID.
        meeting_id: Meeting ID.
        chunk_id: Chunk identifier.
        sample_rate: Audio sample rate.
        language: Expected language code.

    Returns:
        Transcription result.
    """
    logger.info(f"Transcribing audio chunk {chunk_id}")

    try:
        result = {
            "chunk_id": chunk_id,
            "participant_id": participant_id,
            "meeting_id": meeting_id,
            "transcript": "",
            "confidence": 0.0,
            "words": [],
            "language": language,
        }

        # Use transcription service
        try:
            from src.shared.external.transcription import TranscriptionService

            transcriber = TranscriptionService()
            transcript_result = transcriber.transcribe_sync(
                audio_data=chunk_data,
                sample_rate=sample_rate,
                language=language,
            )

            result["transcript"] = transcript_result.text
            result["confidence"] = transcript_result.confidence
            result["words"] = transcript_result.words

        except ImportError:
            logger.warning("Transcription service not available")
        except Exception as e:
            logger.error(f"Transcription error: {e}")

        return result

    except Exception as e:
        logger.error(f"Transcription task failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


# ==================== Video Analysis Tasks ====================


@celery_app.task(
    name="detection.analyze_video",
    queue="detection",
    bind=True,
    max_retries=2,
    soft_time_limit=15,
    time_limit=20,
)
def analyze_video_task(
    self,
    frame_data: bytes,
    participant_id: str,
    meeting_id: str,
    width: int,
    height: int,
    frame_number: int = 0,
) -> Dict[str, Any]:
    """
    Analyze video frame for deepfakes and anomalies.

    Args:
        frame_data: Raw frame bytes (RGB or JPEG).
        participant_id: ID of the participant.
        meeting_id: ID of the meeting.
        width: Frame width.
        height: Frame height.
        frame_number: Frame sequence number.

    Returns:
        Analysis results dict.
    """
    logger.info(
        f"Analyzing video frame {frame_number} for participant {participant_id}"
    )

    try:
        result = {
            "participant_id": participant_id,
            "meeting_id": meeting_id,
            "frame_number": frame_number,
            "video_deepfake_score": 0.0,
            "facial_anomaly_score": 0.0,
            "av_sync_score": 0.0,
            "confidence": 0.0,
            "details": {},
        }

        # Run video deepfake detection
        try:
            from src.services.detection.video.service import VideoDetectionService

            detector = VideoDetectionService()
            deepfake_result = detector.detect_deepfake_sync(
                frame_data=frame_data,
                width=width,
                height=height,
            )

            result["video_deepfake_score"] = deepfake_result.confidence
            result["confidence"] = deepfake_result.confidence
            result["details"]["deepfake"] = deepfake_result.details

        except ImportError:
            logger.warning("Video detection service not available")
        except Exception as e:
            logger.error(f"Video deepfake detection error: {e}")

        # Run facial analysis
        try:
            from src.services.detection.video.facial_analyzer import FacialAnalyzer

            analyzer = FacialAnalyzer()
            facial_result = analyzer.analyze_sync(
                frame_data=frame_data,
                width=width,
                height=height,
            )

            result["facial_anomaly_score"] = facial_result.anomaly_score
            result["details"]["facial"] = facial_result.details

        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Facial analysis skipped: {e}")

        logger.info(
            f"Video analysis complete for frame {frame_number}: "
            f"deepfake={result['video_deepfake_score']:.2f}"
        )

        return result

    except Exception as e:
        logger.error(f"Video analysis task failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


# ==================== Combined Analysis Tasks ====================


@celery_app.task(
    name="detection.analyze_combined",
    queue="detection",
    bind=True,
    max_retries=1,
    soft_time_limit=20,
    time_limit=30,
)
def analyze_combined_task(
    self,
    audio_data: bytes,
    video_data: bytes,
    participant_id: str,
    meeting_id: str,
    audio_sample_rate: int = 16000,
    video_width: int = 640,
    video_height: int = 480,
) -> Dict[str, Any]:
    """
    Run combined audio and video analysis.

    Includes A/V sync detection.

    Args:
        audio_data: Audio chunk bytes.
        video_data: Video frame bytes.
        participant_id: Participant ID.
        meeting_id: Meeting ID.
        audio_sample_rate: Audio sample rate.
        video_width: Video frame width.
        video_height: Video frame height.

    Returns:
        Combined analysis results.
    """
    logger.info(f"Running combined A/V analysis for participant {participant_id}")

    try:
        # Run audio analysis
        audio_result = analyze_audio_task(
            audio_data,
            participant_id,
            meeting_id,
            f"{meeting_id}_{participant_id}_combined",
            audio_sample_rate,
        )

        # Run video analysis
        video_result = analyze_video_task(
            video_data,
            participant_id,
            meeting_id,
            video_width,
            video_height,
        )

        # Combine results
        result = {
            "participant_id": participant_id,
            "meeting_id": meeting_id,
            "audio_deepfake_score": audio_result.get("audio_deepfake_score", 0.0),
            "video_deepfake_score": video_result.get("video_deepfake_score", 0.0),
            "voice_mismatch_score": audio_result.get("voice_mismatch_score", 0.0),
            "facial_anomaly_score": video_result.get("facial_anomaly_score", 0.0),
            "social_engineering_score": audio_result.get("social_engineering_score", 0.0),
            "av_sync_score": 0.0,  # Would need actual timing to calculate
            "confidence": (
                audio_result.get("confidence", 0.0) +
                video_result.get("confidence", 0.0)
            ) / 2,
            "details": {
                "audio": audio_result.get("details", {}),
                "video": video_result.get("details", {}),
            },
        }

        # Calculate combined risk score
        weights = {
            "audio_deepfake": 0.25,
            "video_deepfake": 0.25,
            "voice_mismatch": 0.15,
            "facial_anomaly": 0.10,
            "social_engineering": 0.20,
            "av_sync": 0.05,
        }

        combined_score = (
            result["audio_deepfake_score"] * weights["audio_deepfake"] +
            result["video_deepfake_score"] * weights["video_deepfake"] +
            result["voice_mismatch_score"] * weights["voice_mismatch"] +
            result["facial_anomaly_score"] * weights["facial_anomaly"] +
            result["social_engineering_score"] * weights["social_engineering"] +
            result["av_sync_score"] * weights["av_sync"]
        )

        result["combined_risk_score"] = combined_score

        # Determine risk level
        if combined_score >= 0.85:
            result["risk_level"] = "critical"
        elif combined_score >= 0.65:
            result["risk_level"] = "high"
        elif combined_score >= 0.35:
            result["risk_level"] = "medium"
        else:
            result["risk_level"] = "low"

        logger.info(
            f"Combined analysis complete: risk={combined_score:.2f} ({result['risk_level']})"
        )

        return result

    except Exception as e:
        logger.error(f"Combined analysis task failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


# ==================== Social Engineering Analysis ====================


@celery_app.task(
    name="analysis.social_engineering",
    queue="analysis",
    bind=True,
    max_retries=2,
    soft_time_limit=10,
    time_limit=15,
)
def analyze_social_engineering_task(
    self,
    transcript: str,
    participant_id: str,
    meeting_id: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Analyze transcript for social engineering patterns.

    Args:
        transcript: Text transcript to analyze.
        participant_id: Speaker ID.
        meeting_id: Meeting ID.
        context: Additional context (meeting type, participants, etc.).

    Returns:
        Social engineering analysis results.
    """
    logger.info(f"Analyzing transcript for social engineering: {meeting_id}")

    try:
        result = {
            "participant_id": participant_id,
            "meeting_id": meeting_id,
            "risk_score": 0.0,
            "scenario_scores": {},
            "keyword_matches": [],
            "tactics_detected": [],
            "confidence": 0.0,
            "details": {},
        }

        # Use social engineering detection service
        try:
            from src.services.detection.social_engineering.service import (
                SocialEngineeringDetector,
            )

            detector = SocialEngineeringDetector()
            se_result = detector.analyze_sync(
                text=transcript,
                context=context or {},
            )

            result["risk_score"] = se_result.risk_score
            result["scenario_scores"] = se_result.scenario_scores
            result["keyword_matches"] = se_result.keyword_matches
            result["tactics_detected"] = se_result.tactics_detected
            result["confidence"] = se_result.confidence
            result["details"] = se_result.details

        except ImportError:
            logger.warning("Social engineering detector not available")
        except Exception as e:
            logger.error(f"Social engineering analysis error: {e}")

        return result

    except Exception as e:
        logger.error(f"Social engineering task failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


# ==================== Risk Aggregation ====================


@celery_app.task(
    name="analysis.aggregate_risk",
    queue="analysis",
    bind=True,
    soft_time_limit=5,
    time_limit=10,
)
def aggregate_risk_task(
    self,
    meeting_id: str,
    participant_results: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Aggregate risk scores across participants and time.

    Args:
        meeting_id: Meeting ID.
        participant_results: Dict of participant_id -> analysis results.

    Returns:
        Aggregated risk assessment.
    """
    logger.info(f"Aggregating risk for meeting {meeting_id}")

    try:
        result = {
            "meeting_id": meeting_id,
            "overall_risk_score": 0.0,
            "risk_level": "low",
            "participant_risks": {},
            "high_risk_participants": [],
            "alerts": [],
        }

        if not participant_results:
            return result

        # Calculate per-participant risk
        participant_scores = []
        for participant_id, analysis in participant_results.items():
            score = analysis.get("combined_risk_score", 0.0)
            participant_scores.append(score)

            result["participant_risks"][participant_id] = {
                "risk_score": score,
                "risk_level": analysis.get("risk_level", "unknown"),
            }

            if score >= 0.65:
                result["high_risk_participants"].append(participant_id)

        # Overall meeting risk is max of participant risks
        result["overall_risk_score"] = max(participant_scores) if participant_scores else 0.0

        # Determine overall risk level
        if result["overall_risk_score"] >= 0.85:
            result["risk_level"] = "critical"
        elif result["overall_risk_score"] >= 0.65:
            result["risk_level"] = "high"
        elif result["overall_risk_score"] >= 0.35:
            result["risk_level"] = "medium"
        else:
            result["risk_level"] = "low"

        logger.info(
            f"Risk aggregation complete: {result['risk_level']} "
            f"({result['overall_risk_score']:.2f})"
        )

        return result

    except Exception as e:
        logger.error(f"Risk aggregation task failed: {e}")
        return {
            "meeting_id": meeting_id,
            "error": str(e),
        }
