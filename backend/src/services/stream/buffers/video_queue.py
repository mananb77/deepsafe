"""
Video Frame Queue

Manages video frame queuing and sampling for analysis.
Implements intelligent frame sampling to reduce processing load
while maintaining analysis quality.

Key features:
- Frame rate downsampling (e.g., 30fps -> 2fps for analysis)
- Per-participant frame tracking
- Screen share prioritization
- Keyframe detection hints
"""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, Dict, List, Optional, Set

from src.integrations.common.types import VideoFrame


logger = logging.getLogger(__name__)


@dataclass
class VideoFrameConfig:
    """Configuration for video frame queue."""

    # Sampling settings
    sample_fps: int = 2  # Target frames per second for analysis
    max_queue_size: int = 30  # Max frames in queue per participant
    max_total_queue_size: int = 100  # Max total frames across all participants

    # Analysis settings
    analysis_interval_ms: int = 1000  # Minimum time between analyses
    prioritize_screen_share: bool = True  # Prioritize screen share frames

    # Frame selection
    prefer_keyframes: bool = True  # Prefer keyframes when available
    min_frame_interval_ms: int = 400  # Min 400ms between sampled frames

    # Resolution limits
    max_width: int = 1920
    max_height: int = 1080

    @property
    def sample_interval_ms(self) -> float:
        """Interval between samples in milliseconds."""
        return 1000.0 / self.sample_fps


@dataclass
class QueuedFrame:
    """A video frame in the queue with metadata."""
    frame: VideoFrame
    queued_at: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0  # Higher = more important
    is_analyzed: bool = False

    @property
    def age_ms(self) -> float:
        """Age of frame in milliseconds."""
        return (datetime.utcnow() - self.queued_at).total_seconds() * 1000


class VideoFrameQueue:
    """
    Video frame queue with intelligent sampling.

    Manages video frames for analysis, implementing:
    - Frame rate downsampling
    - Per-participant queuing
    - Priority-based frame selection
    - Screen share prioritization

    Usage:
        queue = VideoFrameQueue(config)

        # Add frames as they arrive
        queue.add_frame(frame)

        # Get frames ready for analysis
        frames = queue.get_frames_for_analysis()
        for frame in frames:
            analyze(frame)
    """

    def __init__(self, config: Optional[VideoFrameConfig] = None):
        """
        Initialize video frame queue.

        Args:
            config: Queue configuration.
        """
        self.config = config or VideoFrameConfig()

        # Per-participant queues
        self._queues: Dict[str, Deque[QueuedFrame]] = {}

        # Sampling state
        self._last_sample_time: Dict[str, float] = {}  # participant_id -> timestamp
        self._last_analysis_time: float = 0

        # Screen share tracking
        self._screen_share_participants: Set[str] = set()

        # Thread safety (RLock to allow reentrant access from total_queued)
        self._lock = threading.RLock()

        # Statistics
        self._frames_received = 0
        self._frames_sampled = 0
        self._frames_dropped = 0
        self._frames_analyzed = 0

    @property
    def total_queued(self) -> int:
        """Total frames currently queued."""
        with self._lock:
            return sum(len(q) for q in self._queues.values())

    @property
    def stats(self) -> dict:
        """Get queue statistics."""
        with self._lock:
            return {
                "frames_received": self._frames_received,
                "frames_sampled": self._frames_sampled,
                "frames_dropped": self._frames_dropped,
                "frames_analyzed": self._frames_analyzed,
                "total_queued": self.total_queued,
                "participant_count": len(self._queues),
                "screen_share_active": len(self._screen_share_participants) > 0,
            }

    def add_frame(self, frame: VideoFrame) -> bool:
        """
        Add a video frame to the queue.

        Implements frame sampling to reduce processing load.

        Args:
            frame: Video frame to add.

        Returns:
            True if frame was added, False if dropped.
        """
        with self._lock:
            self._frames_received += 1
            participant_id = frame.participant_id

            # Track screen share
            if frame.is_screen_share:
                self._screen_share_participants.add(participant_id)
            else:
                self._screen_share_participants.discard(participant_id)

            # Check if we should sample this frame
            if not self._should_sample_frame(frame):
                self._frames_dropped += 1
                return False

            # Get or create queue for participant
            if participant_id not in self._queues:
                self._queues[participant_id] = deque()
                self._last_sample_time[participant_id] = 0

            queue = self._queues[participant_id]

            # Check queue size limit
            if len(queue) >= self.config.max_queue_size:
                # Remove oldest frame
                queue.popleft()
                self._frames_dropped += 1

            # Check total queue size
            if self.total_queued >= self.config.max_total_queue_size:
                # Find and remove lowest priority frame
                self._remove_lowest_priority_frame()

            # Calculate priority
            priority = self._calculate_priority(frame)

            # Add to queue
            queued = QueuedFrame(
                frame=frame,
                priority=priority,
            )
            queue.append(queued)

            # Update sampling timestamp
            self._last_sample_time[participant_id] = time.time()
            self._frames_sampled += 1

            return True

    def _should_sample_frame(self, frame: VideoFrame) -> bool:
        """
        Determine if a frame should be sampled.

        Args:
            frame: Frame to evaluate.

        Returns:
            True if frame should be sampled.
        """
        participant_id = frame.participant_id
        current_time = time.time()

        # Always sample first frame from a participant
        if participant_id not in self._last_sample_time:
            return True

        # Check time since last sample
        time_since_last = (current_time - self._last_sample_time[participant_id]) * 1000

        # Prioritize screen share frames
        if frame.is_screen_share and self.config.prioritize_screen_share:
            return time_since_last >= self.config.min_frame_interval_ms

        # Normal sampling interval
        return time_since_last >= self.config.sample_interval_ms

    def _calculate_priority(self, frame: VideoFrame) -> int:
        """
        Calculate frame priority for queue management.

        Higher priority frames are kept when queue is full.

        Args:
            frame: Frame to prioritize.

        Returns:
            Priority value (higher = more important).
        """
        priority = 0

        # Screen share frames are high priority
        if frame.is_screen_share:
            priority += 100

        # Frames with detected faces are higher priority
        if frame.has_face_detected:
            priority += 50

        # Recent frames are higher priority
        age_ms = (datetime.utcnow() - frame.timestamp).total_seconds() * 1000
        if age_ms < 500:
            priority += 20
        elif age_ms < 1000:
            priority += 10

        return priority

    def _remove_lowest_priority_frame(self) -> None:
        """Remove the lowest priority frame from any queue."""
        lowest_priority = float('inf')
        lowest_participant = None
        lowest_idx = 0

        for participant_id, queue in self._queues.items():
            for idx, queued_frame in enumerate(queue):
                if queued_frame.priority < lowest_priority:
                    lowest_priority = queued_frame.priority
                    lowest_participant = participant_id
                    lowest_idx = idx

        if lowest_participant and lowest_participant in self._queues:
            queue = self._queues[lowest_participant]
            if lowest_idx < len(queue):
                del queue[lowest_idx]
                self._frames_dropped += 1

    def get_frames_for_analysis(self) -> List[VideoFrame]:
        """
        Get frames ready for analysis.

        Returns one frame per participant that hasn't been analyzed recently.

        Returns:
            List of frames ready for analysis.
        """
        frames = []
        current_time = time.time()

        # Check analysis interval
        time_since_analysis = (current_time - self._last_analysis_time) * 1000
        if time_since_analysis < self.config.analysis_interval_ms:
            return frames

        with self._lock:
            for participant_id, queue in list(self._queues.items()):
                if not queue:
                    continue

                # Get best frame for this participant
                frame = self._select_best_frame(queue)
                if frame:
                    frames.append(frame)
                    self._frames_analyzed += 1

            self._last_analysis_time = current_time

        return frames

    def _select_best_frame(self, queue: Deque[QueuedFrame]) -> Optional[VideoFrame]:
        """
        Select the best frame from a participant's queue.

        Prefers:
        1. Unanalyzed frames
        2. Higher priority frames
        3. More recent frames

        Args:
            queue: Participant's frame queue.

        Returns:
            Best frame or None.
        """
        if not queue:
            return None

        # Find unanalyzed frames
        unanalyzed = [qf for qf in queue if not qf.is_analyzed]

        if unanalyzed:
            # Sort by priority (descending), then by age (ascending)
            unanalyzed.sort(key=lambda qf: (-qf.priority, qf.age_ms))
            best = unanalyzed[0]
            best.is_analyzed = True
            return best.frame

        # All frames analyzed, return most recent
        if queue:
            return queue[-1].frame

        return None

    def get_participant_frames(
        self,
        participant_id: str,
        limit: int = 5,
    ) -> List[VideoFrame]:
        """
        Get recent frames for a specific participant.

        Args:
            participant_id: Participant to get frames for.
            limit: Maximum frames to return.

        Returns:
            List of recent frames.
        """
        with self._lock:
            if participant_id not in self._queues:
                return []

            queue = self._queues[participant_id]
            frames = [qf.frame for qf in list(queue)[-limit:]]
            return frames

    def has_screen_share(self) -> bool:
        """Check if any participant is sharing screen."""
        with self._lock:
            return len(self._screen_share_participants) > 0

    def get_screen_share_participants(self) -> List[str]:
        """Get list of participants sharing screen."""
        with self._lock:
            return list(self._screen_share_participants)

    def remove_participant(self, participant_id: str) -> None:
        """
        Remove a participant's queue.

        Args:
            participant_id: Participant to remove.
        """
        with self._lock:
            if participant_id in self._queues:
                del self._queues[participant_id]
            if participant_id in self._last_sample_time:
                del self._last_sample_time[participant_id]
            self._screen_share_participants.discard(participant_id)

    def clear(self) -> None:
        """Clear all queues."""
        with self._lock:
            self._queues.clear()
            self._last_sample_time.clear()
            self._screen_share_participants.clear()

    def reset_stats(self) -> None:
        """Reset statistics."""
        self._frames_received = 0
        self._frames_sampled = 0
        self._frames_dropped = 0
        self._frames_analyzed = 0
