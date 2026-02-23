"""
Stream Processing Service

Real-time audio/video stream processing for DeepSafe:
- Audio buffering and chunking (3-second windows)
- Video frame queuing and sampling
- Parallel analysis execution
- Risk score aggregation
- Alert generation (<5 second latency target)

Architecture:
    Meeting Bot -> Stream Processor -> Analysis Pipeline -> Alert Generator
                        |                    |
                   Audio Buffer         Detection Tasks
                   Video Queue          (Celery workers)
"""

from src.services.stream.processor import (
    StreamProcessor,
    StreamProcessorConfig,
    ProcessingStats,
)
from src.services.stream.buffers.audio_buffer import (
    AudioBuffer,
    AudioChunk,
    AudioBufferConfig,
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
    AlertDispatcher,
    Alert,
    AlertLevel,
    AlertType,
    DispatchChannel,
)

__all__ = [
    # Core processor
    "StreamProcessor",
    "StreamProcessorConfig",
    "ProcessingStats",
    # Buffers
    "AudioBuffer",
    "AudioChunk",
    "AudioBufferConfig",
    "VideoFrameQueue",
    "VideoFrameConfig",
    # Pipeline
    "AnalysisPipeline",
    "AnalysisResult",
    "PipelineConfig",
    # Alerts
    "AlertGenerator",
    "AlertThresholds",
    "AlertDispatcher",
    "Alert",
    "AlertLevel",
    "AlertType",
    "DispatchChannel",
]
