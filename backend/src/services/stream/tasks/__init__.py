"""Celery tasks for stream processing."""

from src.services.stream.tasks.detection_tasks import (
    analyze_audio_task,
    analyze_video_task,
    analyze_combined_task,
)

__all__ = [
    "analyze_audio_task",
    "analyze_video_task",
    "analyze_combined_task",
]
