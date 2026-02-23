"""Unit tests for audio buffer manager."""

import pytest
import threading
from datetime import datetime
from unittest.mock import MagicMock

from src.services.stream.buffers.audio_buffer import (
    AudioBuffer,
    AudioBufferConfig,
    AudioBufferManager,
    AudioChunk,
)
from src.integrations.common.types import AudioFrame


class TestAudioBufferConfig:
    """Tests for AudioBufferConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AudioBufferConfig()

        assert config.chunk_duration_ms == 3000
        assert config.overlap_ms == 500
        assert config.sample_rate == 16000
        assert config.channels == 1
        assert config.bits_per_sample == 16
        assert config.max_buffer_duration_ms == 30000

    def test_bytes_per_sample(self):
        """Test bytes_per_sample calculation."""
        config = AudioBufferConfig(
            bits_per_sample=16,
            channels=1,
        )
        # 16 bits / 8 = 2 bytes per sample
        assert config.bytes_per_sample == 2

    def test_bytes_per_sample_stereo(self):
        """Test bytes_per_sample for stereo."""
        config = AudioBufferConfig(
            bits_per_sample=16,
            channels=2,
        )
        # 16 bits / 8 * 2 channels = 4 bytes
        assert config.bytes_per_sample == 4

    def test_bytes_per_ms(self):
        """Test bytes_per_ms calculation."""
        config = AudioBufferConfig(
            sample_rate=16000,
            bits_per_sample=16,
            channels=1,
        )
        # 16000 samples/sec * 2 bytes/sample / 1000 ms/sec = 32 bytes/ms
        assert config.bytes_per_ms == 32.0

    def test_chunk_size_bytes(self):
        """Test chunk_size_bytes calculation."""
        config = AudioBufferConfig(
            chunk_duration_ms=3000,
            sample_rate=16000,
            bits_per_sample=16,
            channels=1,
        )
        # 3000 ms * 32 bytes/ms = 96000 bytes
        assert config.chunk_size_bytes == 96000

    def test_overlap_size_bytes(self):
        """Test overlap_size_bytes calculation."""
        config = AudioBufferConfig(
            overlap_ms=500,
            sample_rate=16000,
            bits_per_sample=16,
            channels=1,
        )
        # 500 ms * 32 bytes/ms = 16000 bytes
        assert config.overlap_size_bytes == 16000

    def test_max_buffer_size_bytes(self):
        """Test max_buffer_size_bytes calculation."""
        config = AudioBufferConfig(
            max_buffer_duration_ms=30000,
            sample_rate=16000,
            bits_per_sample=16,
            channels=1,
        )
        # 30000 ms * 32 bytes/ms = 960000 bytes
        assert config.max_buffer_size_bytes == 960000


class TestAudioChunk:
    """Tests for AudioChunk dataclass."""

    def test_chunk_creation(self):
        """Test creating an audio chunk."""
        now = datetime.utcnow()
        chunk = AudioChunk(
            chunk_id="chunk-1",
            participant_id="p1",
            meeting_id="m1",
            data=b"audio_data",
            sample_rate=16000,
            channels=1,
            bits_per_sample=16,
            start_time=now,
            end_time=now,
            duration_ms=3000,
            sequence_number=1,
        )

        assert chunk.chunk_id == "chunk-1"
        assert chunk.participant_id == "p1"
        assert chunk.meeting_id == "m1"
        assert chunk.data == b"audio_data"
        assert chunk.sample_rate == 16000
        assert chunk.duration_ms == 3000
        assert chunk.sequence_number == 1

    def test_chunk_duration_seconds(self):
        """Test duration_seconds property."""
        now = datetime.utcnow()
        chunk = AudioChunk(
            chunk_id="chunk-1",
            participant_id="p1",
            meeting_id="m1",
            data=b"audio",
            sample_rate=16000,
            channels=1,
            bits_per_sample=16,
            start_time=now,
            end_time=now,
            duration_ms=3000,
            sequence_number=1,
        )

        assert chunk.duration_seconds == 3.0

    def test_chunk_format(self):
        """Test format property."""
        now = datetime.utcnow()
        chunk = AudioChunk(
            chunk_id="chunk-1",
            participant_id="p1",
            meeting_id="m1",
            data=b"audio",
            sample_rate=16000,
            channels=1,
            bits_per_sample=16,
            start_time=now,
            end_time=now,
            duration_ms=3000,
            sequence_number=1,
        )

        assert chunk.format == "16000Hz/16bit/1ch"


class TestAudioBuffer:
    """Tests for AudioBuffer."""

    def test_buffer_creation(self):
        """Test creating a buffer."""
        config = AudioBufferConfig()
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        assert buffer.participant_id == "p1"
        assert buffer.meeting_id == "m1"
        assert buffer.buffer_duration_ms == 0

    def test_add_frame(self):
        """Test adding a frame to buffer."""
        config = AudioBufferConfig()
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )

        result = buffer.add_frame(frame)

        assert result is True
        assert buffer.buffer_duration_ms > 0

    def test_is_chunk_ready(self):
        """Test is_chunk_ready property."""
        config = AudioBufferConfig(chunk_duration_ms=100)
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        assert buffer.is_chunk_ready is False

        # Add enough data for a chunk
        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * config.chunk_size_bytes),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        buffer.add_frame(frame)

        assert buffer.is_chunk_ready is True

    def test_get_ready_chunks(self):
        """Test getting ready chunks."""
        config = AudioBufferConfig(
            chunk_duration_ms=100,
            overlap_ms=0,
        )
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        # Add enough data for multiple chunks
        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * (config.chunk_size_bytes * 2)),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        buffer.add_frame(frame)

        chunks = buffer.get_ready_chunks()

        assert len(chunks) >= 1
        assert chunks[0].participant_id == "p1"
        assert chunks[0].meeting_id == "m1"

    def test_chunk_sequence_numbers(self):
        """Test that chunk sequence numbers increment."""
        config = AudioBufferConfig(
            chunk_duration_ms=100,
            overlap_ms=0,
        )
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        # Add enough data for multiple chunks
        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * (config.chunk_size_bytes * 3)),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        buffer.add_frame(frame)

        chunks = buffer.get_ready_chunks()

        if len(chunks) >= 2:
            assert chunks[1].sequence_number > chunks[0].sequence_number

    def test_buffer_overflow(self):
        """Test buffer overflow handling."""
        config = AudioBufferConfig(
            max_buffer_duration_ms=100,  # Small buffer
        )
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        # Add more than buffer can hold
        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * (config.max_buffer_size_bytes * 2)),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        buffer.add_frame(frame)

        # Buffer should be limited
        stats = buffer.stats
        assert stats["overflows"] > 0

    def test_clear_buffer(self):
        """Test clearing the buffer."""
        config = AudioBufferConfig()
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        buffer.add_frame(frame)
        assert buffer.buffer_duration_ms > 0

        buffer.clear()
        assert buffer.buffer_duration_ms == 0

    def test_flush(self):
        """Test flushing buffer."""
        config = AudioBufferConfig(
            min_chunk_duration_ms=50,
        )
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        # Add data less than chunk size but more than min
        min_bytes = int(config.min_chunk_duration_ms * config.bytes_per_ms) + 100
        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * min_bytes),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        buffer.add_frame(frame)

        chunk = buffer.flush()

        assert chunk is not None
        assert chunk.participant_id == "p1"

    def test_stats(self):
        """Test buffer statistics."""
        config = AudioBufferConfig()
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        buffer.add_frame(frame)

        stats = buffer.stats

        assert "participant_id" in stats
        assert "frames_received" in stats
        assert "chunks_produced" in stats
        assert "bytes_received" in stats
        assert "buffer_size_bytes" in stats
        assert stats["frames_received"] == 1
        assert stats["bytes_received"] == 1000

    def test_reset_stats(self):
        """Test resetting statistics."""
        config = AudioBufferConfig()
        buffer = AudioBuffer(
            participant_id="p1",
            meeting_id="m1",
            config=config,
        )

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        buffer.add_frame(frame)

        buffer.reset_stats()

        stats = buffer.stats
        assert stats["frames_received"] == 0
        assert stats["bytes_received"] == 0


class TestAudioBufferManager:
    """Tests for AudioBufferManager."""

    def test_manager_creation(self):
        """Test creating a buffer manager."""
        config = AudioBufferConfig()
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        assert manager.meeting_id == "m1"

    def test_get_buffer(self):
        """Test getting/creating participant buffer."""
        config = AudioBufferConfig()
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        buffer = manager.get_buffer("p1")

        assert buffer is not None
        assert buffer.participant_id == "p1"
        assert buffer.meeting_id == "m1"

    def test_get_buffer_cached(self):
        """Test that buffer is cached for same participant."""
        config = AudioBufferConfig()
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        buffer1 = manager.get_buffer("p1")
        buffer2 = manager.get_buffer("p1")

        assert buffer1 is buffer2

    def test_add_frame(self):
        """Test adding frame through manager."""
        config = AudioBufferConfig()
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )

        result = manager.add_frame(frame)

        assert result is True

        stats = manager.get_stats()
        assert stats["participant_count"] == 1

    def test_add_frames_multiple_participants(self):
        """Test adding frames for multiple participants."""
        config = AudioBufferConfig()
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        for pid in ["p1", "p2", "p3"]:
            frame = AudioFrame(
                participant_id=pid,
                meeting_id="m1",
                data=bytes([0] * 1000),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            manager.add_frame(frame)

        stats = manager.get_stats()
        assert stats["participant_count"] == 3

    def test_get_all_ready_chunks(self):
        """Test getting all ready chunks from manager."""
        config = AudioBufferConfig(
            chunk_duration_ms=100,
            overlap_ms=0,
        )
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        # Add enough data for chunks
        for pid in ["p1", "p2"]:
            frame = AudioFrame(
                participant_id=pid,
                meeting_id="m1",
                data=bytes([0] * config.chunk_size_bytes),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            manager.add_frame(frame)

        chunks = manager.get_all_ready_chunks()

        assert len(chunks) >= 2

    def test_remove_participant(self):
        """Test removing a participant."""
        config = AudioBufferConfig()
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        for pid in ["p1", "p2"]:
            frame = AudioFrame(
                participant_id=pid,
                meeting_id="m1",
                data=bytes([0] * 1000),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            manager.add_frame(frame)

        stats_before = manager.get_stats()
        assert stats_before["participant_count"] == 2

        manager.remove_participant("p1")

        stats_after = manager.get_stats()
        assert stats_after["participant_count"] == 1

    def test_clear_all(self):
        """Test clearing all buffers."""
        config = AudioBufferConfig()
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        for pid in ["p1", "p2"]:
            frame = AudioFrame(
                participant_id=pid,
                meeting_id="m1",
                data=bytes([0] * 1000),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            manager.add_frame(frame)

        manager.clear_all()

        stats = manager.get_stats()
        assert stats["participant_count"] == 0

    def test_thread_safety(self):
        """Test that buffer manager is thread-safe."""
        config = AudioBufferConfig()
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        errors = []

        def add_frames(participant_id: str, count: int):
            try:
                for _ in range(count):
                    frame = AudioFrame(
                        participant_id=participant_id,
                        meeting_id="m1",
                        data=bytes([0] * 100),
                        sample_rate=16000,
                        channels=1,
                        timestamp=datetime.utcnow(),
                    )
                    manager.add_frame(frame)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=add_frames, args=(f"p{i}", 50))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have no errors
        assert len(errors) == 0

        stats = manager.get_stats()
        assert stats["participant_count"] == 5

    def test_get_stats(self):
        """Test manager statistics."""
        config = AudioBufferConfig()
        manager = AudioBufferManager(
            meeting_id="m1",
            config=config,
        )

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        manager.add_frame(frame)

        stats = manager.get_stats()

        assert "meeting_id" in stats
        assert "participant_count" in stats
        assert "buffers" in stats
        assert stats["meeting_id"] == "m1"
        assert stats["participant_count"] == 1
