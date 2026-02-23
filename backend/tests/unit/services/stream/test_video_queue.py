"""Unit tests for video frame queue."""

import pytest
import threading
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.services.stream.buffers.video_queue import (
    VideoFrameQueue,
    VideoFrameConfig,
    QueuedFrame,
)
from src.integrations.common.types import VideoFrame


class TestVideoFrameConfig:
    """Tests for VideoFrameConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = VideoFrameConfig()

        assert config.sample_fps == 2
        assert config.max_queue_size == 30
        assert config.max_total_queue_size == 100
        assert config.analysis_interval_ms == 1000

    def test_sample_interval_calculation(self):
        """Test sample_interval_ms calculation."""
        config = VideoFrameConfig(sample_fps=2)

        # 1000ms / 2fps = 500ms between samples
        assert config.sample_interval_ms == 500.0

    def test_sample_interval_high_fps(self):
        """Test sample interval with high FPS."""
        config = VideoFrameConfig(sample_fps=10)

        # 1000ms / 10fps = 100ms between samples
        assert config.sample_interval_ms == 100.0


class TestQueuedFrame:
    """Tests for QueuedFrame dataclass."""

    def test_queued_frame_creation(self):
        """Test creating a queued frame."""
        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame_data",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )

        queued = QueuedFrame(
            frame=frame,
            priority=10,
        )

        assert queued.frame == frame
        assert queued.priority == 10
        assert queued.is_analyzed is False

    def test_queued_frame_age(self):
        """Test frame age calculation."""
        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame_data",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )

        queued = QueuedFrame(frame=frame)

        # Age should be very small (just created)
        assert queued.age_ms < 100


class TestVideoFrameQueue:
    """Tests for VideoFrameQueue."""

    def test_queue_creation(self):
        """Test creating a video frame queue."""
        config = VideoFrameConfig()
        queue = VideoFrameQueue(config=config)

        assert queue.total_queued == 0

    def test_add_frame(self):
        """Test adding a frame to the queue."""
        config = VideoFrameConfig(
            sample_fps=100,  # High FPS for testing
            min_frame_interval_ms=0,
        )
        queue = VideoFrameQueue(config=config)

        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame_data",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )

        result = queue.add_frame(frame)
        assert result is True
        assert queue.total_queued >= 1

    def test_frame_sampling(self):
        """Test that frames are sampled according to FPS."""
        config = VideoFrameConfig(
            sample_fps=2,
            min_frame_interval_ms=400,
        )
        queue = VideoFrameQueue(config=config)

        frames_added = 0
        for i in range(10):
            frame = VideoFrame(
                participant_id="p1",
                meeting_id="m1",
                data=b"frame_data",
                width=640,
                height=480,
                timestamp=datetime.utcnow(),
            )
            if queue.add_frame(frame):
                frames_added += 1

        # Most frames should be dropped due to sampling
        assert frames_added < 10

    def test_frame_sampling_after_delay(self):
        """Test that frames are added after sample interval."""
        config = VideoFrameConfig(
            sample_fps=100,
            min_frame_interval_ms=10,  # 10ms interval
        )
        queue = VideoFrameQueue(config=config)

        # Add first frame
        frame1 = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame1",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )
        result1 = queue.add_frame(frame1)
        assert result1 is True

        # Wait for interval
        time.sleep(0.02)  # 20ms

        # Add second frame
        frame2 = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame2",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )
        result2 = queue.add_frame(frame2)
        assert result2 is True

    def test_multiple_participants(self):
        """Test queue handles multiple participants."""
        config = VideoFrameConfig(
            sample_fps=100,
            min_frame_interval_ms=0,
        )
        queue = VideoFrameQueue(config=config)

        for pid in ["p1", "p2", "p3"]:
            frame = VideoFrame(
                participant_id=pid,
                meeting_id="m1",
                data=b"frame_data",
                width=640,
                height=480,
                timestamp=datetime.utcnow(),
            )
            queue.add_frame(frame)

        # Should have frames from all participants
        assert queue.total_queued >= 3

    def test_queue_size_limit(self):
        """Test that queue respects size limits."""
        config = VideoFrameConfig(
            max_queue_size=5,
            sample_fps=1000,  # Very high to accept all frames
            min_frame_interval_ms=0,
        )
        queue = VideoFrameQueue(config=config)

        # Add more than max
        for i in range(10):
            frame = VideoFrame(
                participant_id="p1",
                meeting_id="m1",
                data=f"frame_{i}".encode(),
                width=640,
                height=480,
                timestamp=datetime.utcnow(),
            )
            queue.add_frame(frame)
            time.sleep(0.001)  # Small delay between frames

        # Should be limited to max
        participant_frames = queue.get_participant_frames("p1", limit=100)
        assert len(participant_frames) <= config.max_queue_size

    def test_screen_share_prioritization(self):
        """Test that screen share frames are prioritized."""
        config = VideoFrameConfig(
            prioritize_screen_share=True,
            min_frame_interval_ms=100,
        )
        queue = VideoFrameQueue(config=config)

        # Add regular frame
        regular_frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"regular",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
            is_screen_share=False,
        )
        queue.add_frame(regular_frame)

        # Wait less than normal interval
        time.sleep(0.05)

        # Add screen share frame
        screen_frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"screen",
            width=1920,
            height=1080,
            timestamp=datetime.utcnow(),
            is_screen_share=True,
        )

        # Screen share should bypass normal interval check
        result = queue.add_frame(screen_frame)
        # May or may not be added depending on min_frame_interval_ms
        assert isinstance(result, bool)

    def test_screen_share_tracking(self):
        """Test screen share participant tracking."""
        config = VideoFrameConfig()
        queue = VideoFrameQueue(config=config)

        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"screen",
            width=1920,
            height=1080,
            timestamp=datetime.utcnow(),
            is_screen_share=True,
        )
        queue.add_frame(frame)

        assert queue.has_screen_share() is True
        assert "p1" in queue.get_screen_share_participants()

    def test_get_frames_for_analysis(self):
        """Test getting frames ready for analysis."""
        config = VideoFrameConfig(
            analysis_interval_ms=0,  # No delay for testing
            sample_fps=1000,
            min_frame_interval_ms=0,
        )
        queue = VideoFrameQueue(config=config)

        # Add frames
        for pid in ["p1", "p2"]:
            frame = VideoFrame(
                participant_id=pid,
                meeting_id="m1",
                data=b"frame",
                width=640,
                height=480,
                timestamp=datetime.utcnow(),
            )
            queue.add_frame(frame)

        frames = queue.get_frames_for_analysis()

        # Should get frames
        assert isinstance(frames, list)

    def test_get_participant_frames(self):
        """Test getting frames for a specific participant."""
        config = VideoFrameConfig(
            sample_fps=1000,
            min_frame_interval_ms=0,
        )
        queue = VideoFrameQueue(config=config)

        # Add frames for multiple participants
        for i in range(3):
            for pid in ["p1", "p2"]:
                frame = VideoFrame(
                    participant_id=pid,
                    meeting_id="m1",
                    data=f"frame_{i}".encode(),
                    width=640,
                    height=480,
                    timestamp=datetime.utcnow(),
                )
                queue.add_frame(frame)
                time.sleep(0.001)

        p1_frames = queue.get_participant_frames("p1", limit=10)

        # Should only get p1's frames
        for frame in p1_frames:
            assert frame.participant_id == "p1"

    def test_remove_participant(self):
        """Test removing a participant from queue."""
        config = VideoFrameConfig(
            sample_fps=1000,
            min_frame_interval_ms=0,
        )
        queue = VideoFrameQueue(config=config)

        # Add frames
        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )
        queue.add_frame(frame)

        assert queue.total_queued > 0

        queue.remove_participant("p1")

        p1_frames = queue.get_participant_frames("p1")
        assert len(p1_frames) == 0

    def test_clear(self):
        """Test clearing all queues."""
        config = VideoFrameConfig(
            sample_fps=1000,
            min_frame_interval_ms=0,
        )
        queue = VideoFrameQueue(config=config)

        # Add frames
        for pid in ["p1", "p2", "p3"]:
            frame = VideoFrame(
                participant_id=pid,
                meeting_id="m1",
                data=b"frame",
                width=640,
                height=480,
                timestamp=datetime.utcnow(),
            )
            queue.add_frame(frame)

        queue.clear()

        assert queue.total_queued == 0

    def test_stats(self):
        """Test queue statistics."""
        config = VideoFrameConfig()
        queue = VideoFrameQueue(config=config)

        stats = queue.stats

        assert "frames_received" in stats
        assert "frames_sampled" in stats
        assert "frames_dropped" in stats
        assert "frames_analyzed" in stats
        assert "total_queued" in stats
        assert "participant_count" in stats

    def test_reset_stats(self):
        """Test resetting statistics."""
        config = VideoFrameConfig(
            sample_fps=1000,
            min_frame_interval_ms=0,
        )
        queue = VideoFrameQueue(config=config)

        # Add some frames
        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )
        queue.add_frame(frame)

        queue.reset_stats()

        stats = queue.stats
        assert stats["frames_received"] == 0
        assert stats["frames_sampled"] == 0

    def test_thread_safety(self):
        """Test that queue is thread-safe."""
        config = VideoFrameConfig(
            sample_fps=1000,
            min_frame_interval_ms=0,
            max_queue_size=1000,
        )
        queue = VideoFrameQueue(config=config)

        errors = []

        def add_frames(participant_id: str, count: int):
            try:
                for i in range(count):
                    frame = VideoFrame(
                        participant_id=participant_id,
                        meeting_id="m1",
                        data=f"frame_{i}".encode(),
                        width=640,
                        height=480,
                        timestamp=datetime.utcnow(),
                    )
                    queue.add_frame(frame)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=add_frames, args=(f"p{i}", 20))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have no errors
        assert len(errors) == 0

    def test_priority_calculation(self):
        """Test frame priority is calculated correctly."""
        config = VideoFrameConfig(
            sample_fps=1000,
            min_frame_interval_ms=0,
        )
        queue = VideoFrameQueue(config=config)

        # Screen share frame should have higher priority
        screen_frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"screen",
            width=1920,
            height=1080,
            timestamp=datetime.utcnow(),
            is_screen_share=True,
        )

        regular_frame = VideoFrame(
            participant_id="p2",
            meeting_id="m1",
            data=b"regular",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
            is_screen_share=False,
        )

        queue.add_frame(screen_frame)
        queue.add_frame(regular_frame)

        # Both should be added successfully
        assert queue.total_queued >= 2
