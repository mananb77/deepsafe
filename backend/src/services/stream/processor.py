"""
Stream Processor

Core component for real-time meeting stream processing.
Coordinates audio/video buffering, analysis dispatch, and alert generation.

Target: <5 second end-to-end latency from frame capture to alert.
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from src.integrations.common.types import (
    AudioFrame,
    VideoFrame,
    AlertConfig,
    AlertSeverity,
    MeetingPlatform,
)
from src.services.stream.buffers.audio_buffer import (
    AudioBuffer,
    AudioBufferConfig,
    AudioChunk,
)
from src.services.stream.buffers.video_queue import (
    VideoFrameQueue,
    VideoFrameConfig,
)
from src.services.stream.pipeline.orchestrator import (
    AnalysisPipeline,
    AnalysisResult,
    PipelineConfig,
)
from src.services.stream.alert_generator import (
    AlertGenerator,
    AlertThresholds,
)


logger = logging.getLogger(__name__)


class ProcessorState(str, Enum):
    """Stream processor states."""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class StreamProcessorConfig:
    """Configuration for stream processor."""

    # Audio settings
    audio_chunk_duration_ms: int = 3000  # 3 seconds
    audio_sample_rate: int = 16000
    audio_overlap_ms: int = 500  # Overlap between chunks

    # Video settings
    video_sample_fps: int = 2  # Sample 2 frames per second
    video_max_queue_size: int = 30  # Max frames in queue
    video_analysis_interval_ms: int = 1000  # Analyze every second

    # Processing settings
    max_concurrent_analysis: int = 4
    analysis_timeout_seconds: float = 4.0  # Must complete within latency budget

    # Analysis toggles
    enable_audio_analysis: bool = True
    enable_video_analysis: bool = True
    use_mock_analysis: bool = field(default_factory=lambda: os.getenv("USE_MOCK_ANALYSIS", "true").lower() == "true")

    # Alert settings
    alert_cooldown_seconds: float = 30.0  # Min time between similar alerts

    # Latency budget (5 seconds total)
    target_latency_ms: int = 5000

    # Risk thresholds
    deepfake_alert_threshold: float = 0.7
    social_engineering_alert_threshold: float = 0.6
    combined_risk_alert_threshold: float = 0.65


@dataclass
class ProcessingStats:
    """Statistics for stream processing."""
    # Counts
    audio_frames_processed: int = 0
    video_frames_processed: int = 0
    audio_chunks_analyzed: int = 0
    video_frames_analyzed: int = 0
    analyses_completed: int = 0
    alerts_generated: int = 0

    # Latency tracking (in ms)
    average_latency_ms: float = 0.0
    avg_audio_latency_ms: float = 0.0
    avg_video_latency_ms: float = 0.0
    avg_analysis_latency_ms: float = 0.0
    max_end_to_end_latency_ms: float = 0.0

    # Error counts
    analysis_errors: int = 0
    timeout_errors: int = 0
    buffer_overflows: int = 0

    # Risk scores
    current_risk_score: float = 0.0
    peak_risk_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "audio_frames_processed": self.audio_frames_processed,
            "video_frames_processed": self.video_frames_processed,
            "audio_chunks_analyzed": self.audio_chunks_analyzed,
            "video_frames_analyzed": self.video_frames_analyzed,
            "analyses_completed": self.analyses_completed,
            "alerts_generated": self.alerts_generated,
            "average_latency_ms": round(self.average_latency_ms, 2),
            "avg_audio_latency_ms": round(self.avg_audio_latency_ms, 2),
            "avg_video_latency_ms": round(self.avg_video_latency_ms, 2),
            "avg_analysis_latency_ms": round(self.avg_analysis_latency_ms, 2),
            "max_end_to_end_latency_ms": round(self.max_end_to_end_latency_ms, 2),
            "analysis_errors": self.analysis_errors,
            "timeout_errors": self.timeout_errors,
            "buffer_overflows": self.buffer_overflows,
            "current_risk_score": round(self.current_risk_score, 4),
            "peak_risk_score": round(self.peak_risk_score, 4),
        }


# Type for callbacks
AlertCallback = Callable[[AlertConfig], None]
ResultCallback = Callable[[AnalysisResult], Any]


class StreamProcessor:
    """
    Real-time stream processor for meeting analysis.

    Processes audio and video streams from meeting bots,
    dispatches analysis tasks, aggregates results, and
    generates alerts when risk thresholds are exceeded.

    Usage:
        processor = StreamProcessor(meeting_id, config)

        # Register callbacks
        processor.set_result_callback(handle_result)
        processor.set_alert_callback(handle_alert)

        # Start processing
        await processor.start()

        # Feed frames from meeting bot
        await processor.process_audio_frame(frame)
        await processor.process_video_frame(frame)

        # Stop when meeting ends
        await processor.stop()
    """

    def __init__(
        self,
        meeting_id: str,
        config: Optional[StreamProcessorConfig] = None,
        pipeline_config: Optional[PipelineConfig] = None,
        alert_thresholds: Optional[AlertThresholds] = None,
    ):
        self.meeting_id = meeting_id
        self.config = config or StreamProcessorConfig()

        # State
        self._state = ProcessorState.IDLE
        self._stats = ProcessingStats()

        # Participant tracking: id -> metadata
        self._participants: Dict[str, Optional[dict]] = {}

        # Buffers
        self._audio_buffers: Dict[str, AudioBuffer] = {}
        self._video_queue = VideoFrameQueue(
            config=VideoFrameConfig(
                max_queue_size=self.config.video_max_queue_size,
                sample_fps=self.config.video_sample_fps,
            )
        )

        # Analysis pipeline
        p_config = pipeline_config or PipelineConfig(
            max_concurrent_analysis=self.config.max_concurrent_analysis,
            timeout_seconds=self.config.analysis_timeout_seconds,
            use_mock_analysis=self.config.use_mock_analysis,
            enable_audio_analysis=self.config.enable_audio_analysis,
            enable_video_analysis=self.config.enable_video_analysis,
        )
        self._pipeline = AnalysisPipeline(
            meeting_id=meeting_id,
            config=p_config,
        )

        # Alert generator
        self._alert_generator = AlertGenerator(
            meeting_id=meeting_id,
            thresholds=alert_thresholds or AlertThresholds(
                audio_deepfake_threshold=self.config.deepfake_alert_threshold,
                social_engineering_threshold=self.config.social_engineering_alert_threshold,
                warning_threshold=self.config.combined_risk_alert_threshold,
                info_cooldown=int(self.config.alert_cooldown_seconds),
                warning_cooldown=int(self.config.alert_cooldown_seconds),
            ),
        )

        # Callbacks
        self._alert_callbacks: List[AlertCallback] = []
        self._result_callback: Optional[ResultCallback] = None
        self._alert_callback: Optional[Callable] = None

        # Background tasks
        self._processing_task: Optional[asyncio.Task] = None
        self._video_analysis_task: Optional[asyncio.Task] = None

        # Latency tracking
        self._latency_samples: List[float] = []

        # Participant risk tracking
        self._participant_risks: Dict[str, float] = {}

    # ==================== Properties ====================

    @property
    def state(self) -> ProcessorState:
        """Get current processor state."""
        return self._state

    @property
    def stats(self) -> ProcessingStats:
        """Get processing statistics."""
        return self._stats

    @property
    def is_running(self) -> bool:
        """Check if processor is running."""
        return self._state == ProcessorState.RUNNING

    @property
    def is_paused(self) -> bool:
        """Check if processor is paused."""
        return self._state == ProcessorState.PAUSED

    @property
    def participants(self) -> Dict[str, Optional[dict]]:
        """Get tracked participants."""
        return dict(self._participants)

    # ==================== Lifecycle ====================

    async def start(self) -> bool:
        """Start stream processing."""
        if self._state == ProcessorState.RUNNING:
            logger.warning(f"Processor already running for meeting {self.meeting_id}")
            return True

        self._state = ProcessorState.STARTING
        logger.info(f"Starting stream processor for meeting {self.meeting_id}")

        try:
            # Start background processing tasks
            self._processing_task = asyncio.create_task(
                self._audio_processing_loop()
            )
            self._video_analysis_task = asyncio.create_task(
                self._video_analysis_loop()
            )

            self._state = ProcessorState.RUNNING
            logger.info(f"Stream processor started for meeting {self.meeting_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start stream processor: {e}")
            self._state = ProcessorState.ERROR
            return False

    async def stop(self) -> None:
        """Stop stream processing."""
        if self._state in (ProcessorState.STOPPED, ProcessorState.IDLE):
            return

        self._state = ProcessorState.STOPPING
        logger.info(f"Stopping stream processor for meeting {self.meeting_id}")

        # Cancel background tasks
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

        if self._video_analysis_task:
            self._video_analysis_task.cancel()
            try:
                await self._video_analysis_task
            except asyncio.CancelledError:
                pass

        # Clear buffers
        self._audio_buffers.clear()
        self._video_queue.clear()

        self._state = ProcessorState.STOPPED
        logger.info(f"Stream processor stopped for meeting {self.meeting_id}")

    def pause(self) -> None:
        """Pause stream processing (sync)."""
        if self._state == ProcessorState.RUNNING:
            self._state = ProcessorState.PAUSED
            logger.info(f"Stream processor paused for meeting {self.meeting_id}")

    def resume(self) -> None:
        """Resume stream processing (sync)."""
        if self._state == ProcessorState.PAUSED:
            self._state = ProcessorState.RUNNING
            logger.info(f"Stream processor resumed for meeting {self.meeting_id}")

    # ==================== Context Manager ====================

    async def __aenter__(self):
        """Async context manager entry — starts the processor."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit — stops the processor."""
        await self.stop()
        return False

    # ==================== Frame Processing ====================

    async def process_audio_frame(self, frame: AudioFrame) -> None:
        """Process incoming audio frame (async)."""
        if self._state not in (ProcessorState.RUNNING,):
            return

        self._stats.audio_frames_processed += 1
        participant_id = frame.participant_id

        # Track participant
        if participant_id not in self._participants:
            self._participants[participant_id] = None

        # Get or create buffer for participant
        if participant_id not in self._audio_buffers:
            self._audio_buffers[participant_id] = AudioBuffer(
                participant_id=participant_id,
                meeting_id=self.meeting_id,
                config=AudioBufferConfig(
                    chunk_duration_ms=self.config.audio_chunk_duration_ms,
                    sample_rate=self.config.audio_sample_rate,
                    overlap_ms=self.config.audio_overlap_ms,
                ),
            )

        # Add frame to buffer
        buffer = self._audio_buffers[participant_id]
        buffer.add_frame(frame)

    async def process_video_frame(self, frame: VideoFrame) -> None:
        """Process incoming video frame (async)."""
        if self._state not in (ProcessorState.RUNNING,):
            return

        self._stats.video_frames_processed += 1

        # Track participant
        if frame.participant_id not in self._participants:
            self._participants[frame.participant_id] = None

        # Add to queue (queue handles sampling)
        added = self._video_queue.add_frame(frame)
        if not added:
            self._stats.buffer_overflows += 1

    # ==================== Background Processing ====================

    async def _audio_processing_loop(self) -> None:
        """Background loop for processing audio chunks."""
        while self._state in (ProcessorState.RUNNING, ProcessorState.PAUSED):
            if self._state == ProcessorState.PAUSED:
                await asyncio.sleep(0.1)
                continue

            try:
                for participant_id, buffer in list(self._audio_buffers.items()):
                    chunks = buffer.get_ready_chunks()

                    for chunk in chunks:
                        self._stats.audio_chunks_analyzed += 1
                        asyncio.create_task(
                            self._analyze_audio_chunk(chunk)
                        )

                await asyncio.sleep(0.05)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                self._stats.analysis_errors += 1
                await asyncio.sleep(0.1)

    async def _video_analysis_loop(self) -> None:
        """Background loop for video frame analysis."""
        interval_seconds = self.config.video_analysis_interval_ms / 1000.0

        while self._state in (ProcessorState.RUNNING, ProcessorState.PAUSED):
            if self._state == ProcessorState.PAUSED:
                await asyncio.sleep(0.1)
                continue

            try:
                frames = self._video_queue.get_frames_for_analysis()

                for frame in frames:
                    self._stats.video_frames_analyzed += 1
                    asyncio.create_task(
                        self._analyze_video_frame(frame)
                    )

                await asyncio.sleep(interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in video analysis loop: {e}")
                self._stats.analysis_errors += 1
                await asyncio.sleep(0.1)

    # ==================== Analysis Dispatch ====================

    async def _analyze_audio_chunk(self, chunk: AudioChunk) -> None:
        """Dispatch audio chunk for analysis."""
        start_time = time.time()

        try:
            result = await asyncio.wait_for(
                self._pipeline.analyze_audio(chunk),
                timeout=self.config.analysis_timeout_seconds,
            )

            latency_ms = (time.time() - start_time) * 1000
            self._update_latency_stats(latency_ms, "audio")

            await self._process_analysis_result(result, chunk.participant_id)
            self._stats.analyses_completed += 1

        except asyncio.TimeoutError:
            logger.warning(
                f"Audio analysis timeout for participant {chunk.participant_id}"
            )
            self._stats.timeout_errors += 1
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            self._stats.analysis_errors += 1

    async def _analyze_video_frame(self, frame: VideoFrame) -> None:
        """Dispatch video frame for analysis."""
        start_time = time.time()

        try:
            result = await asyncio.wait_for(
                self._pipeline.analyze_video(frame),
                timeout=self.config.analysis_timeout_seconds,
            )

            latency_ms = (time.time() - start_time) * 1000
            self._update_latency_stats(latency_ms, "video")

            await self._process_analysis_result(result, frame.participant_id)
            self._stats.analyses_completed += 1

        except asyncio.TimeoutError:
            logger.warning(
                f"Video analysis timeout for participant {frame.participant_id}"
            )
            self._stats.timeout_errors += 1
        except Exception as e:
            logger.error(f"Video analysis error: {e}")
            self._stats.analysis_errors += 1

    # ==================== Result Processing ====================

    async def _process_analysis_result(
        self,
        result: AnalysisResult,
        participant_id: str,
    ) -> None:
        """Process analysis result and potentially generate alerts."""
        # Update risk score
        self._stats.current_risk_score = result.combined_risk_score
        if result.combined_risk_score > self._stats.peak_risk_score:
            self._stats.peak_risk_score = result.combined_risk_score

        # Track per-participant risk
        self._participant_risks[participant_id] = result.combined_risk_score

        # Invoke result callback
        if self._result_callback:
            try:
                cb_result = self._result_callback(result)
                if asyncio.iscoroutine(cb_result):
                    await cb_result
            except Exception as e:
                logger.error(f"Result callback error: {e}")

        # Check for alerts via alert generator
        alerts = await self._alert_generator.process_result(
            result, participant_id=participant_id
        )

        for alert in alerts:
            self._stats.alerts_generated += 1
            # Invoke alert callback
            if self._alert_callback:
                try:
                    cb_result = self._alert_callback(alert)
                    if asyncio.iscoroutine(cb_result):
                        await cb_result
                except Exception as e:
                    logger.error(f"Alert callback error: {e}")

            # Legacy on_alert callbacks
            for callback in self._alert_callbacks:
                try:
                    cb_result = callback(alert)
                    if asyncio.iscoroutine(cb_result):
                        await cb_result
                except Exception as e:
                    logger.error(f"Alert callback error: {e}")

    # ==================== Latency Tracking ====================

    def _update_latency_stats(self, latency_ms: float, analysis_type: str) -> None:
        """Update latency statistics."""
        self._latency_samples.append(latency_ms)

        if len(self._latency_samples) > 100:
            self._latency_samples = self._latency_samples[-100:]

        avg_latency = sum(self._latency_samples) / len(self._latency_samples)
        self._stats.avg_analysis_latency_ms = avg_latency
        self._stats.average_latency_ms = avg_latency

        if analysis_type == "audio":
            self._stats.avg_audio_latency_ms = latency_ms
        else:
            self._stats.avg_video_latency_ms = latency_ms

        end_to_end = self.config.audio_chunk_duration_ms + latency_ms
        if end_to_end > self._stats.max_end_to_end_latency_ms:
            self._stats.max_end_to_end_latency_ms = end_to_end

    # ==================== Callbacks ====================

    def set_result_callback(self, callback: ResultCallback) -> None:
        """Set callback for analysis results."""
        self._result_callback = callback

    def set_alert_callback(self, callback: Callable) -> None:
        """Set callback for alerts."""
        self._alert_callback = callback

    def on_alert(self, callback: AlertCallback) -> None:
        """Register alert callback (legacy)."""
        self._alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: AlertCallback) -> bool:
        """Remove alert callback."""
        if callback in self._alert_callbacks:
            self._alert_callbacks.remove(callback)
            return True
        return False

    # ==================== Participant Management ====================

    def add_participant(self, participant_id: str, metadata: Optional[dict] = None) -> None:
        """Register a participant for tracking."""
        self._participants[participant_id] = metadata

    def remove_participant(self, participant_id: str) -> None:
        """Remove a participant and clean up their buffers."""
        self._participants.pop(participant_id, None)
        if participant_id in self._audio_buffers:
            del self._audio_buffers[participant_id]
        self._participant_risks.pop(participant_id, None)

    def get_participants(self) -> List[str]:
        """Get list of tracked participant IDs."""
        return list(self._participants.keys())

    # ==================== Risk Queries ====================

    def get_current_risk_score(self) -> float:
        """Get current aggregated risk score."""
        return self._stats.current_risk_score

    def get_meeting_risk(self) -> float:
        """Get overall meeting risk score."""
        if not self._participant_risks:
            return self._stats.current_risk_score
        return max(self._participant_risks.values()) if self._participant_risks else 0.0

    def get_participant_risk(self, participant_id: str) -> Optional[float]:
        """Get risk score for a specific participant."""
        return self._participant_risks.get(participant_id)

    def is_latency_within_target(self) -> bool:
        """Check if processing latency is within target."""
        return self._stats.max_end_to_end_latency_ms <= self.config.target_latency_ms

    # ==================== Stats Management ====================

    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self._stats = ProcessingStats()
        self._latency_samples.clear()
