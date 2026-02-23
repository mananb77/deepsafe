"""
Audio Buffer Manager

Manages audio frame buffering and chunking for analysis.
Collects audio frames into fixed-duration chunks with configurable overlap.

The buffer uses a sliding window approach:
- Frames are accumulated until chunk duration is reached
- Chunks are extracted with optional overlap for continuity
- Supports multiple participants with separate buffers
"""

import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List, Optional

from src.integrations.common.types import AudioFrame


logger = logging.getLogger(__name__)


@dataclass
class AudioBufferConfig:
    """Configuration for audio buffer."""

    # Chunk settings
    chunk_duration_ms: int = 3000  # 3 seconds per chunk
    overlap_ms: int = 500  # 500ms overlap between chunks

    # Audio format
    sample_rate: int = 16000  # 16kHz
    channels: int = 1  # Mono
    bits_per_sample: int = 16

    # Buffer limits
    max_buffer_duration_ms: int = 30000  # Max 30 seconds buffered
    min_chunk_duration_ms: int = 1000  # Min 1 second for analysis

    @property
    def bytes_per_sample(self) -> int:
        """Bytes per audio sample."""
        return (self.bits_per_sample // 8) * self.channels

    @property
    def bytes_per_ms(self) -> float:
        """Bytes per millisecond of audio."""
        return (self.sample_rate * self.bytes_per_sample) / 1000

    @property
    def chunk_size_bytes(self) -> int:
        """Target chunk size in bytes."""
        return int(self.chunk_duration_ms * self.bytes_per_ms)

    @property
    def overlap_size_bytes(self) -> int:
        """Overlap size in bytes."""
        return int(self.overlap_ms * self.bytes_per_ms)

    @property
    def max_buffer_size_bytes(self) -> int:
        """Maximum buffer size in bytes."""
        return int(self.max_buffer_duration_ms * self.bytes_per_ms)


@dataclass
class AudioChunk:
    """
    A chunk of audio data ready for analysis.

    Represents a fixed-duration segment of audio from a participant.
    """
    chunk_id: str
    participant_id: str
    meeting_id: str

    # Audio data
    data: bytes
    sample_rate: int
    channels: int
    bits_per_sample: int

    # Timing
    start_time: datetime
    end_time: datetime
    duration_ms: int

    # Sequence
    sequence_number: int

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    has_speech: bool = True  # Assume speech unless VAD says otherwise

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        return self.duration_ms / 1000.0

    @property
    def format(self) -> str:
        """Audio format string."""
        return f"{self.sample_rate}Hz/{self.bits_per_sample}bit/{self.channels}ch"


class AudioBuffer:
    """
    Audio buffer for a single participant.

    Collects audio frames and produces fixed-duration chunks
    suitable for analysis by the detection pipeline.

    Usage:
        buffer = AudioBuffer(participant_id, meeting_id, config)

        # Add frames as they arrive
        buffer.add_frame(frame)

        # Get chunks ready for analysis
        chunks = buffer.get_ready_chunks()
        for chunk in chunks:
            analyze(chunk)
    """

    def __init__(
        self,
        participant_id: str,
        meeting_id: str,
        config: Optional[AudioBufferConfig] = None,
    ):
        """
        Initialize audio buffer.

        Args:
            participant_id: ID of the participant.
            meeting_id: ID of the meeting.
            config: Buffer configuration.
        """
        self.participant_id = participant_id
        self.meeting_id = meeting_id
        self.config = config or AudioBufferConfig()

        # Buffer storage
        self._buffer: bytearray = bytearray()
        self._frame_times: Deque[datetime] = deque()

        # Chunk tracking
        self._chunk_sequence = 0
        self._last_chunk_end: Optional[datetime] = None

        # Thread safety
        self._lock = threading.Lock()

        # Statistics
        self._frames_received = 0
        self._chunks_produced = 0
        self._bytes_received = 0
        self._overflows = 0

    @property
    def buffer_duration_ms(self) -> float:
        """Current buffer duration in milliseconds."""
        return len(self._buffer) / self.config.bytes_per_ms

    @property
    def is_chunk_ready(self) -> bool:
        """Check if a full chunk is available."""
        return len(self._buffer) >= self.config.chunk_size_bytes

    @property
    def stats(self) -> dict:
        """Get buffer statistics."""
        return {
            "participant_id": self.participant_id,
            "frames_received": self._frames_received,
            "chunks_produced": self._chunks_produced,
            "bytes_received": self._bytes_received,
            "buffer_size_bytes": len(self._buffer),
            "buffer_duration_ms": self.buffer_duration_ms,
            "overflows": self._overflows,
        }

    def add_frame(self, frame: AudioFrame) -> bool:
        """
        Add an audio frame to the buffer.

        Args:
            frame: Audio frame to add.

        Returns:
            True if frame was added, False if buffer overflow.
        """
        with self._lock:
            self._frames_received += 1
            self._bytes_received += len(frame.data)

            # Check for buffer overflow
            if len(self._buffer) + len(frame.data) > self.config.max_buffer_size_bytes:
                self._overflows += 1
                # Drop oldest data to make room
                excess = (len(self._buffer) + len(frame.data)) - self.config.max_buffer_size_bytes
                self._buffer = self._buffer[excess:]
                # Also trim frame times
                while self._frame_times and len(self._frame_times) > 0:
                    self._frame_times.popleft()
                    if len(self._buffer) <= self.config.max_buffer_size_bytes:
                        break

            # Add frame data
            self._buffer.extend(frame.data)
            self._frame_times.append(frame.timestamp)

            return True

    def get_ready_chunks(self) -> List[AudioChunk]:
        """
        Get all chunks that are ready for analysis.

        Extracts complete chunks from the buffer, maintaining overlap.

        Returns:
            List of AudioChunk objects ready for analysis.
        """
        chunks = []

        with self._lock:
            while self.is_chunk_ready:
                chunk = self._extract_chunk()
                if chunk:
                    chunks.append(chunk)
                else:
                    break

        return chunks

    def _extract_chunk(self) -> Optional[AudioChunk]:
        """
        Extract a single chunk from the buffer.

        Returns:
            AudioChunk or None if not enough data.
        """
        if len(self._buffer) < self.config.chunk_size_bytes:
            return None

        # Calculate extraction size (chunk minus overlap to keep)
        extraction_size = self.config.chunk_size_bytes - self.config.overlap_size_bytes
        if extraction_size <= 0:
            # Overlap exceeds chunk size — extract full chunk without overlap
            extraction_size = self.config.chunk_size_bytes

        # Extract chunk data
        chunk_data = bytes(self._buffer[:self.config.chunk_size_bytes])

        # Remove extracted portion (keeping overlap)
        self._buffer = self._buffer[extraction_size:]

        # Calculate timing
        start_time = self._frame_times[0] if self._frame_times else datetime.utcnow()

        # Remove old frame times
        frames_to_remove = int(extraction_size / (self.config.bytes_per_ms * 100))  # Approximate
        for _ in range(min(frames_to_remove, len(self._frame_times))):
            if self._frame_times:
                self._frame_times.popleft()

        end_time = datetime.utcnow()

        # Create chunk
        self._chunk_sequence += 1
        self._chunks_produced += 1

        chunk = AudioChunk(
            chunk_id=f"{self.meeting_id}_{self.participant_id}_{self._chunk_sequence}",
            participant_id=self.participant_id,
            meeting_id=self.meeting_id,
            data=chunk_data,
            sample_rate=self.config.sample_rate,
            channels=self.config.channels,
            bits_per_sample=self.config.bits_per_sample,
            start_time=start_time,
            end_time=end_time,
            duration_ms=self.config.chunk_duration_ms,
            sequence_number=self._chunk_sequence,
        )

        self._last_chunk_end = end_time
        return chunk

    def flush(self) -> Optional[AudioChunk]:
        """
        Flush remaining buffer data as a chunk.

        Used when processing ends to capture any remaining audio.

        Returns:
            AudioChunk with remaining data, or None if too short.
        """
        with self._lock:
            # Check if we have enough data for a minimum chunk
            min_bytes = int(self.config.min_chunk_duration_ms * self.config.bytes_per_ms)
            if len(self._buffer) < min_bytes:
                return None

            # Create chunk from remaining data
            chunk_data = bytes(self._buffer)
            duration_ms = int(len(self._buffer) / self.config.bytes_per_ms)

            start_time = self._frame_times[0] if self._frame_times else datetime.utcnow()
            end_time = datetime.utcnow()

            self._chunk_sequence += 1
            self._chunks_produced += 1

            chunk = AudioChunk(
                chunk_id=f"{self.meeting_id}_{self.participant_id}_{self._chunk_sequence}",
                participant_id=self.participant_id,
                meeting_id=self.meeting_id,
                data=chunk_data,
                sample_rate=self.config.sample_rate,
                channels=self.config.channels,
                bits_per_sample=self.config.bits_per_sample,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                sequence_number=self._chunk_sequence,
            )

            # Clear buffer
            self._buffer.clear()
            self._frame_times.clear()

            return chunk

    def clear(self) -> None:
        """Clear the buffer."""
        with self._lock:
            self._buffer.clear()
            self._frame_times.clear()

    def reset_stats(self) -> None:
        """Reset buffer statistics."""
        self._frames_received = 0
        self._chunks_produced = 0
        self._bytes_received = 0
        self._overflows = 0


class AudioBufferManager:
    """
    Manages multiple audio buffers for a meeting.

    Provides a centralized interface for managing per-participant
    audio buffers.
    """

    def __init__(
        self,
        meeting_id: str,
        config: Optional[AudioBufferConfig] = None,
    ):
        """
        Initialize buffer manager.

        Args:
            meeting_id: ID of the meeting.
            config: Default buffer configuration.
        """
        self.meeting_id = meeting_id
        self.default_config = config or AudioBufferConfig()

        self._buffers: dict[str, AudioBuffer] = {}
        self._lock = threading.Lock()

    def get_buffer(self, participant_id: str) -> AudioBuffer:
        """
        Get or create buffer for a participant.

        Args:
            participant_id: Participant ID.

        Returns:
            AudioBuffer for the participant.
        """
        with self._lock:
            if participant_id not in self._buffers:
                self._buffers[participant_id] = AudioBuffer(
                    participant_id=participant_id,
                    meeting_id=self.meeting_id,
                    config=self.default_config,
                )
            return self._buffers[participant_id]

    def add_frame(self, frame: AudioFrame) -> bool:
        """
        Add frame to appropriate participant buffer.

        Args:
            frame: Audio frame with participant_id.

        Returns:
            True if added successfully.
        """
        buffer = self.get_buffer(frame.participant_id)
        return buffer.add_frame(frame)

    def get_all_ready_chunks(self) -> List[AudioChunk]:
        """
        Get ready chunks from all participant buffers.

        Returns:
            List of all ready chunks.
        """
        chunks = []
        with self._lock:
            for buffer in self._buffers.values():
                chunks.extend(buffer.get_ready_chunks())
        return chunks

    def remove_participant(self, participant_id: str) -> Optional[AudioChunk]:
        """
        Remove participant and flush their buffer.

        Args:
            participant_id: Participant to remove.

        Returns:
            Final chunk from participant's buffer, if any.
        """
        with self._lock:
            if participant_id in self._buffers:
                buffer = self._buffers.pop(participant_id)
                return buffer.flush()
        return None

    def clear_all(self) -> None:
        """Clear all buffers."""
        with self._lock:
            for buffer in self._buffers.values():
                buffer.clear()
            self._buffers.clear()

    def get_stats(self) -> dict:
        """Get statistics for all buffers."""
        with self._lock:
            return {
                "meeting_id": self.meeting_id,
                "participant_count": len(self._buffers),
                "buffers": {
                    pid: buffer.stats
                    for pid, buffer in self._buffers.items()
                },
            }
