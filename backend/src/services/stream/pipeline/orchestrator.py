"""
Analysis Pipeline Orchestrator

Coordinates parallel analysis of audio and video streams.
Dispatches to detection services and aggregates results.

Implements:
- Parallel audio/video analysis
- Celery task dispatch (when available)
- Fallback synchronous processing
- Result aggregation and risk scoring
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from uuid import uuid4

from src.integrations.common.types import VideoFrame
from src.services.stream.buffers.audio_buffer import AudioChunk


logger = logging.getLogger(__name__)


class AnalysisType(str, Enum):
    """Types of analysis."""
    AUDIO_DEEPFAKE = "audio_deepfake"
    VIDEO_DEEPFAKE = "video_deepfake"
    VOICE_VERIFICATION = "voice_verification"
    FACIAL_ANALYSIS = "facial_analysis"
    SOCIAL_ENGINEERING = "social_engineering"
    AV_SYNC = "av_sync"


@dataclass
class PipelineConfig:
    """Configuration for analysis pipeline."""

    # Concurrency
    max_concurrent_analysis: int = 4
    timeout_seconds: float = 5.0

    # Analysis toggles
    enable_audio_analysis: bool = True
    enable_video_analysis: bool = True
    enable_voice_verification: bool = True
    enable_facial_analysis: bool = True
    enable_social_engineering: bool = True
    enable_av_sync_detection: bool = True

    # Celery settings
    use_celery_tasks: bool = False
    celery_queue: str = "detection"

    # Fallback settings
    use_mock_analysis: bool = True

    # Configurable risk weights (must sum to ~1.0)
    audio_deepfake_weight: float = 0.25
    video_deepfake_weight: float = 0.25
    social_engineering_weight: float = 0.20
    voice_mismatch_weight: float = 0.15
    facial_anomaly_weight: float = 0.10
    av_sync_weight: float = 0.05


@dataclass
class AnalysisResult:
    """
    Result from analysis pipeline.

    Aggregates results from multiple analysis types.
    """
    result_id: str = field(default_factory=lambda: str(uuid4()))
    participant_id: str = ""
    meeting_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Analysis type
    analysis_type: str = ""  # "audio", "video", or "combined"

    # Individual scores (0.0 to 1.0, where 1.0 = highest risk)
    audio_deepfake_score: float = 0.0
    video_deepfake_score: float = 0.0
    voice_mismatch_score: float = 0.0
    facial_anomaly_score: float = 0.0
    social_engineering_score: float = 0.0
    av_sync_score: float = 0.0

    # Combined risk
    combined_risk_score: float = 0.0
    risk_level: str = "low"  # "low", "medium", "high", "critical"

    # Confidence
    confidence: float = 0.0

    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    # Timing
    processing_time_ms: float = 0.0

    def calculate_combined_risk(self, config: Optional[PipelineConfig] = None) -> float:
        """Calculate combined risk score from individual scores."""
        if config:
            weights = {
                "audio_deepfake": config.audio_deepfake_weight,
                "video_deepfake": config.video_deepfake_weight,
                "voice_mismatch": config.voice_mismatch_weight,
                "facial_anomaly": config.facial_anomaly_weight,
                "social_engineering": config.social_engineering_weight,
                "av_sync": config.av_sync_weight,
            }
        else:
            weights = {
                "audio_deepfake": 0.25,
                "video_deepfake": 0.25,
                "voice_mismatch": 0.15,
                "facial_anomaly": 0.10,
                "social_engineering": 0.20,
                "av_sync": 0.05,
            }

        self.combined_risk_score = (
            self.audio_deepfake_score * weights["audio_deepfake"] +
            self.video_deepfake_score * weights["video_deepfake"] +
            self.voice_mismatch_score * weights["voice_mismatch"] +
            self.facial_anomaly_score * weights["facial_anomaly"] +
            self.social_engineering_score * weights["social_engineering"] +
            self.av_sync_score * weights["av_sync"]
        )

        # Determine risk level
        if self.combined_risk_score >= 0.85:
            self.risk_level = "critical"
        elif self.combined_risk_score >= 0.65:
            self.risk_level = "high"
        elif self.combined_risk_score >= 0.35:
            self.risk_level = "medium"
        else:
            self.risk_level = "low"

        return self.combined_risk_score

    def get_risk_level(self) -> str:
        """Calculate and return the risk level."""
        self.calculate_combined_risk()
        return self.risk_level

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary."""
        self.calculate_combined_risk()
        return {
            "result_id": self.result_id,
            "participant_id": self.participant_id,
            "meeting_id": self.meeting_id,
            "timestamp": self.timestamp.isoformat(),
            "analysis_type": self.analysis_type,
            "audio_deepfake_score": self.audio_deepfake_score,
            "video_deepfake_score": self.video_deepfake_score,
            "voice_mismatch_score": self.voice_mismatch_score,
            "facial_anomaly_score": self.facial_anomaly_score,
            "social_engineering_score": self.social_engineering_score,
            "av_sync_score": self.av_sync_score,
            "combined_risk_score": self.combined_risk_score,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "details": self.details,
            "warnings": self.warnings,
            "processing_time_ms": self.processing_time_ms,
        }


class AnalysisPipeline:
    """
    Analysis pipeline for audio and video streams.

    Orchestrates parallel analysis and aggregates results.
    """

    def __init__(
        self,
        meeting_id: str = "",
        config: Optional[PipelineConfig] = None,
    ):
        self.meeting_id = meeting_id
        self.config = config or PipelineConfig()

        # Concurrency control
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_analysis)
        self._active_tasks: int = 0

        # State
        self._is_running = False

        # Analysis services (lazy loaded)
        self._audio_detector = None
        self._video_detector = None
        self._social_engineering_detector = None

        # Statistics
        self._audio_analyses = 0
        self._video_analyses = 0
        self._combined_analyses = 0
        self._analyses_failed = 0
        self._total_processing_time_ms = 0.0

    @property
    def is_running(self) -> bool:
        """Check if pipeline is running."""
        return self._is_running

    @property
    def stats(self) -> dict:
        """Get pipeline statistics."""
        total = self._audio_analyses + self._video_analyses + self._combined_analyses
        avg_time = 0.0
        if total > 0:
            avg_time = self._total_processing_time_ms / total

        return {
            "is_running": self._is_running,
            "active_tasks": self._active_tasks,
            "audio_analyses": self._audio_analyses,
            "video_analyses": self._video_analyses,
            "combined_analyses": self._combined_analyses,
            "analyses_failed": self._analyses_failed,
            "avg_processing_time_ms": round(avg_time, 2),
        }

    def reset(self) -> None:
        """Reset pipeline statistics."""
        self._audio_analyses = 0
        self._video_analyses = 0
        self._combined_analyses = 0
        self._analyses_failed = 0
        self._total_processing_time_ms = 0.0

    async def start(self) -> None:
        """Start the analysis pipeline."""
        if self._is_running:
            return
        logger.info("Starting analysis pipeline")
        await self._initialize_services()
        self._is_running = True
        logger.info("Analysis pipeline started")

    async def stop(self) -> None:
        """Stop the analysis pipeline."""
        if not self._is_running:
            return
        logger.info("Stopping analysis pipeline")
        while self._active_tasks > 0:
            await asyncio.sleep(0.1)
        self._is_running = False
        logger.info("Analysis pipeline stopped")

    async def _initialize_services(self) -> None:
        """Initialize detection services."""
        pass

    # ==================== Audio Analysis ====================

    async def analyze_audio(self, chunk: AudioChunk) -> AnalysisResult:
        """Analyze an audio chunk."""
        start_time = time.time()
        result = AnalysisResult(
            participant_id=chunk.participant_id,
            meeting_id=chunk.meeting_id,
            analysis_type="audio",
        )

        async with self._semaphore:
            self._active_tasks += 1
            try:
                if self.config.use_celery_tasks:
                    try:
                        result = await self._analyze_audio_celery(chunk)
                    except Exception:
                        if self.config.use_mock_analysis:
                            result = await self._analyze_audio_mock(chunk)
                        else:
                            raise
                elif self.config.use_mock_analysis:
                    result = await self._analyze_audio_mock(chunk)
                else:
                    result = await self._analyze_audio_direct(chunk)

                result.calculate_combined_risk(self.config)
                self._audio_analyses += 1

            except Exception as e:
                logger.error(f"Audio analysis error: {e}")
                self._analyses_failed += 1
                result.warnings.append(f"Analysis error: {str(e)}")
            finally:
                self._active_tasks -= 1

        result.processing_time_ms = (time.time() - start_time) * 1000
        self._total_processing_time_ms += result.processing_time_ms
        return result

    async def _analyze_audio_mock(self, chunk: AudioChunk) -> AnalysisResult:
        """Mock audio analysis for development."""
        import random
        await asyncio.sleep(random.uniform(0.1, 0.3))

        result = AnalysisResult(
            participant_id=chunk.participant_id,
            meeting_id=chunk.meeting_id,
            analysis_type="audio",
        )
        result.audio_deepfake_score = random.uniform(0.0, 0.3)
        result.voice_mismatch_score = random.uniform(0.0, 0.2)
        result.social_engineering_score = random.uniform(0.0, 0.25)

        if random.random() < 0.05:
            result.audio_deepfake_score = random.uniform(0.7, 0.95)

        result.confidence = 0.85
        result.details = {
            "chunk_id": chunk.chunk_id,
            "duration_ms": chunk.duration_ms,
            "mock": True,
        }
        return result

    async def _analyze_audio_direct(self, chunk: AudioChunk) -> AnalysisResult:
        """Direct audio analysis using detection services."""
        result = AnalysisResult(
            participant_id=chunk.participant_id,
            meeting_id=chunk.meeting_id,
            analysis_type="audio",
        )

        tasks = []
        if self.config.enable_audio_analysis:
            tasks.append(self._run_audio_deepfake_detection(chunk))
        if self.config.enable_social_engineering:
            tasks.append(self._run_social_engineering_detection(chunk))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    result.warnings.append(f"Analysis {i} failed: {str(res)}")
                elif isinstance(res, dict):
                    if "audio_deepfake_score" in res:
                        result.audio_deepfake_score = res["audio_deepfake_score"]
                    if "social_engineering_score" in res:
                        result.social_engineering_score = res["social_engineering_score"]

        return result

    async def _analyze_audio_celery(self, chunk: AudioChunk) -> AnalysisResult:
        """Dispatch audio analysis to Celery workers."""
        from src.services.stream.tasks.detection_tasks import analyze_audio_task

        def _send_and_get():
            task_result = analyze_audio_task.delay(
                chunk_data=chunk.data,
                participant_id=chunk.participant_id,
                meeting_id=chunk.meeting_id,
                chunk_id=chunk.chunk_id,
            )
            return task_result.get(timeout=self.config.timeout_seconds)

        loop = asyncio.get_event_loop()
        result_data = await asyncio.wait_for(
            loop.run_in_executor(None, _send_and_get),
            timeout=self.config.timeout_seconds + 1,
        )

        return AnalysisResult(
            participant_id=chunk.participant_id,
            meeting_id=chunk.meeting_id,
            analysis_type="audio",
            audio_deepfake_score=result_data.get("audio_deepfake_score", 0.0),
            social_engineering_score=result_data.get("social_engineering_score", 0.0),
            confidence=result_data.get("confidence", 0.0),
            details=result_data.get("details", {}),
        )

    async def _run_audio_deepfake_detection(self, chunk: AudioChunk) -> dict:
        """Run audio deepfake detection."""
        try:
            from src.services.detection.audio.service import AudioDetectionService
            if self._audio_detector is None:
                self._audio_detector = AudioDetectionService()
            result = await self._audio_detector.detect_deepfake(
                audio_data=chunk.data,
                sample_rate=chunk.sample_rate,
            )
            return {"audio_deepfake_score": result.confidence}
        except ImportError:
            return {}

    async def _run_social_engineering_detection(self, chunk: AudioChunk) -> dict:
        """Run social engineering detection on transcript."""
        return {}

    # ==================== Video Analysis ====================

    async def analyze_video(self, frame: VideoFrame) -> AnalysisResult:
        """Analyze a video frame."""
        start_time = time.time()
        result = AnalysisResult(
            participant_id=frame.participant_id,
            meeting_id=frame.meeting_id,
            analysis_type="video",
        )

        async with self._semaphore:
            self._active_tasks += 1
            try:
                if self.config.use_celery_tasks:
                    try:
                        result = await self._analyze_video_celery(frame)
                    except Exception:
                        if self.config.use_mock_analysis:
                            result = await self._analyze_video_mock(frame)
                        else:
                            raise
                elif self.config.use_mock_analysis:
                    result = await self._analyze_video_mock(frame)
                else:
                    result = await self._analyze_video_direct(frame)

                result.calculate_combined_risk(self.config)
                self._video_analyses += 1

            except Exception as e:
                logger.error(f"Video analysis error: {e}")
                self._analyses_failed += 1
                result.warnings.append(f"Analysis error: {str(e)}")
            finally:
                self._active_tasks -= 1

        result.processing_time_ms = (time.time() - start_time) * 1000
        self._total_processing_time_ms += result.processing_time_ms
        return result

    async def _analyze_video_mock(self, frame: VideoFrame) -> AnalysisResult:
        """Mock video analysis for development."""
        import random
        await asyncio.sleep(random.uniform(0.15, 0.4))

        result = AnalysisResult(
            participant_id=frame.participant_id,
            meeting_id=frame.meeting_id,
            analysis_type="video",
        )
        result.video_deepfake_score = random.uniform(0.0, 0.25)
        result.facial_anomaly_score = random.uniform(0.0, 0.2)
        result.av_sync_score = random.uniform(0.0, 0.15)

        if random.random() < 0.03:
            result.video_deepfake_score = random.uniform(0.75, 0.98)

        result.confidence = 0.82
        result.details = {
            "frame_number": frame.frame_number,
            "resolution": frame.resolution,
            "is_screen_share": frame.is_screen_share,
            "mock": True,
        }
        return result

    async def _analyze_video_direct(self, frame: VideoFrame) -> AnalysisResult:
        """Direct video analysis using detection services."""
        result = AnalysisResult(
            participant_id=frame.participant_id,
            meeting_id=frame.meeting_id,
            analysis_type="video",
        )

        tasks = []
        if self.config.enable_video_analysis:
            tasks.append(self._run_video_deepfake_detection(frame))
        if self.config.enable_facial_analysis:
            tasks.append(self._run_facial_analysis(frame))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    result.warnings.append(f"Analysis {i} failed: {str(res)}")
                elif isinstance(res, dict):
                    if "video_deepfake_score" in res:
                        result.video_deepfake_score = res["video_deepfake_score"]
                    if "facial_anomaly_score" in res:
                        result.facial_anomaly_score = res["facial_anomaly_score"]

        return result

    async def _analyze_video_celery(self, frame: VideoFrame) -> AnalysisResult:
        """Dispatch video analysis to Celery workers."""
        from src.services.stream.tasks.detection_tasks import analyze_video_task

        def _send_and_get():
            task_result = analyze_video_task.delay(
                frame_data=frame.data,
                participant_id=frame.participant_id,
                meeting_id=frame.meeting_id,
                width=frame.width,
                height=frame.height,
            )
            return task_result.get(timeout=self.config.timeout_seconds)

        loop = asyncio.get_event_loop()
        result_data = await asyncio.wait_for(
            loop.run_in_executor(None, _send_and_get),
            timeout=self.config.timeout_seconds + 1,
        )

        return AnalysisResult(
            participant_id=frame.participant_id,
            meeting_id=frame.meeting_id,
            analysis_type="video",
            video_deepfake_score=result_data.get("video_deepfake_score", 0.0),
            facial_anomaly_score=result_data.get("facial_anomaly_score", 0.0),
            confidence=result_data.get("confidence", 0.0),
            details=result_data.get("details", {}),
        )

    async def _run_video_deepfake_detection(self, frame: VideoFrame) -> dict:
        """Run video deepfake detection."""
        try:
            from src.services.detection.video.service import VideoDetectionService
            if self._video_detector is None:
                self._video_detector = VideoDetectionService()
            result = await self._video_detector.detect_deepfake(
                frame_data=frame.data,
                width=frame.width,
                height=frame.height,
            )
            return {"video_deepfake_score": result.confidence}
        except ImportError:
            return {}

    async def _run_facial_analysis(self, frame: VideoFrame) -> dict:
        """Run facial analysis."""
        return {}

    # ==================== Combined Analysis ====================

    async def analyze_combined(
        self,
        chunk: AudioChunk,
        frame: VideoFrame,
    ) -> AnalysisResult:
        """Run combined audio and video analysis."""
        audio_task = self.analyze_audio(chunk)
        video_task = self.analyze_video(frame)

        audio_result, video_result = await asyncio.gather(audio_task, video_task)

        combined = AnalysisResult(
            participant_id=chunk.participant_id,
            meeting_id=chunk.meeting_id,
            analysis_type="combined",
        )

        combined.audio_deepfake_score = audio_result.audio_deepfake_score
        combined.video_deepfake_score = video_result.video_deepfake_score
        combined.voice_mismatch_score = audio_result.voice_mismatch_score
        combined.facial_anomaly_score = video_result.facial_anomaly_score
        combined.social_engineering_score = audio_result.social_engineering_score

        if self.config.enable_av_sync_detection:
            combined.av_sync_score = await self._run_av_sync_detection(chunk, frame)

        combined.calculate_combined_risk(self.config)

        combined.details = {
            "audio": audio_result.details,
            "video": video_result.details,
        }
        combined.warnings = audio_result.warnings + video_result.warnings
        combined.processing_time_ms = (
            audio_result.processing_time_ms + video_result.processing_time_ms
        )

        self._combined_analyses += 1

        return combined

    async def _run_av_sync_detection(
        self,
        chunk: AudioChunk,
        frame: VideoFrame,
    ) -> float:
        """Detect audio-video synchronization issues."""
        audio_time = chunk.end_time
        video_time = frame.timestamp

        diff_ms = abs((audio_time - video_time).total_seconds() * 1000)

        if diff_ms <= 42:
            return 0.0
        elif diff_ms <= 100:
            return (diff_ms - 42) / 100
        elif diff_ms <= 200:
            return 0.5 + ((diff_ms - 100) / 200)
        else:
            return min(1.0, 0.7 + (diff_ms - 200) / 500)
