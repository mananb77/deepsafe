"""
Audio-Video Sync Detector

Detects synchronization mismatches between audio and video.
Uses the 42ms threshold for lip sync detection.
"""

import struct
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AVSyncResult:
    """Result from audio-video sync analysis."""

    is_synced: bool
    sync_offset_ms: float  # Positive = audio leads video
    confidence: float  # 0-100
    lip_sync_score: float  # 0-1, higher = better sync
    details: Dict[str, Any]


class AVSyncDetector:
    """
    Detects audio-video synchronization issues.

    Key detection method:
    - 42ms threshold: Human perception of lip sync issues
    - Audio-video correlation analysis
    - Voice activity to mouth movement correlation

    Deepfakes often have sync issues because:
    1. Face swapping processes video and audio separately
    2. Lip synthesis may not perfectly match audio
    3. Different frame rates between source and target
    """

    # Perceptual threshold for sync detection (milliseconds)
    SYNC_THRESHOLD_MS = 42.0

    # Maximum offset to search (milliseconds)
    MAX_OFFSET_MS = 500.0

    def __init__(
        self,
        frame_rate: float = 30.0,
        audio_sample_rate: int = 16000,
    ):
        self.frame_rate = frame_rate
        self.audio_sample_rate = audio_sample_rate

    def analyze(
        self,
        audio_data: bytes,
        video_frames: List[bytes],
        lip_positions: Optional[List[Dict[str, float]]] = None,
    ) -> AVSyncResult:
        """
        Analyze audio-video synchronization.

        Args:
            audio_data: Raw PCM audio bytes.
            video_frames: List of video frame data.
            lip_positions: Optional list of lip landmark positions per frame.
                          Each dict has 'openness' (0-1) and 'width' (0-1).

        Returns:
            AVSyncResult with sync analysis.
        """
        if not audio_data or not video_frames:
            return AVSyncResult(
                is_synced=True,
                sync_offset_ms=0.0,
                confidence=0.0,
                lip_sync_score=0.0,
                details={"error": "Insufficient data for analysis"},
            )

        # Extract audio envelope
        audio_envelope = self._extract_audio_envelope(audio_data)

        # If lip positions provided, use them for correlation
        if lip_positions:
            offset_ms, confidence = self._correlate_with_lips(
                audio_envelope, lip_positions
            )
        else:
            # Estimate lip movement from video frames (simplified)
            estimated_movement = self._estimate_mouth_movement(video_frames)
            offset_ms, confidence = self._correlate_with_movement(
                audio_envelope, estimated_movement
            )

        # Calculate lip sync score
        lip_sync_score = self._calculate_lip_sync_score(abs(offset_ms))

        # Determine if synced (within threshold)
        is_synced = abs(offset_ms) <= self.SYNC_THRESHOLD_MS

        return AVSyncResult(
            is_synced=is_synced,
            sync_offset_ms=offset_ms,
            confidence=confidence,
            lip_sync_score=lip_sync_score,
            details={
                "threshold_ms": self.SYNC_THRESHOLD_MS,
                "audio_frames": len(audio_envelope),
                "video_frames": len(video_frames),
                "lip_positions_provided": lip_positions is not None,
            },
        )

    def analyze_with_landmarks(
        self,
        audio_data: bytes,
        facial_landmarks: List[Dict[str, Any]],
    ) -> AVSyncResult:
        """
        Analyze sync using facial landmarks.

        Args:
            audio_data: Raw PCM audio bytes.
            facial_landmarks: List of facial landmark data per frame.
                             Should include mouth landmarks.

        Returns:
            AVSyncResult with sync analysis.
        """
        if not audio_data or not facial_landmarks:
            return AVSyncResult(
                is_synced=True,
                sync_offset_ms=0.0,
                confidence=0.0,
                lip_sync_score=0.0,
                details={"error": "Insufficient data"},
            )

        # Extract lip positions from landmarks
        lip_positions = []
        for frame_landmarks in facial_landmarks:
            if "mouth" in frame_landmarks:
                mouth = frame_landmarks["mouth"]
                lip_positions.append({
                    "openness": mouth.get("openness", 0.5),
                    "width": mouth.get("width", 0.5),
                })
            else:
                # Estimate from individual landmarks if available
                lip_positions.append({"openness": 0.5, "width": 0.5})

        return self.analyze(audio_data, [], lip_positions)

    def _extract_audio_envelope(self, audio_data: bytes) -> List[float]:
        """
        Extract amplitude envelope from audio.

        Returns energy values at video frame rate.
        """
        # Convert bytes to samples
        num_samples = len(audio_data) // 2
        samples = struct.unpack(f"<{num_samples}h", audio_data[:num_samples * 2])
        normalized = [s / 32768.0 for s in samples]

        # Calculate samples per video frame
        samples_per_frame = int(self.audio_sample_rate / self.frame_rate)

        # Extract envelope at video frame rate
        envelope = []
        for i in range(0, len(normalized) - samples_per_frame, samples_per_frame):
            frame = normalized[i:i + samples_per_frame]
            # RMS energy
            rms = math.sqrt(sum(s * s for s in frame) / len(frame))
            envelope.append(rms)

        return envelope

    def _estimate_mouth_movement(
        self,
        video_frames: List[bytes],
    ) -> List[float]:
        """
        Estimate mouth movement from video frames.

        This is a simplified placeholder. In production, use:
        - Face detection (MTCNN, dlib)
        - Lip segmentation
        - Optical flow analysis

        Returns estimated mouth openness per frame (0-1).
        """
        # Placeholder: return uniform values
        # Real implementation would analyze actual video frames
        return [0.5] * len(video_frames)

    def _correlate_with_lips(
        self,
        audio_envelope: List[float],
        lip_positions: List[Dict[str, float]],
    ) -> Tuple[float, float]:
        """
        Find optimal offset by correlating audio envelope with lip movement.

        Returns (offset_ms, confidence).
        """
        if not audio_envelope or not lip_positions:
            return 0.0, 0.0

        # Extract lip openness values
        lip_values = [lp.get("openness", 0.5) for lp in lip_positions]

        # Normalize lengths
        min_len = min(len(audio_envelope), len(lip_values))
        audio = audio_envelope[:min_len]
        lips = lip_values[:min_len]

        if min_len < 3:
            return 0.0, 0.0

        # Search for best offset
        ms_per_frame = 1000.0 / self.frame_rate
        max_offset_frames = int(self.MAX_OFFSET_MS / ms_per_frame)

        best_offset = 0
        best_correlation = -1.0

        for offset in range(-max_offset_frames, max_offset_frames + 1):
            correlation = self._compute_correlation(audio, lips, offset)
            if correlation > best_correlation:
                best_correlation = correlation
                best_offset = offset

        offset_ms = best_offset * ms_per_frame
        confidence = max(0, best_correlation) * 100

        return offset_ms, confidence

    def _correlate_with_movement(
        self,
        audio_envelope: List[float],
        movement: List[float],
    ) -> Tuple[float, float]:
        """
        Correlate audio envelope with estimated mouth movement.

        Returns (offset_ms, confidence).
        """
        return self._correlate_with_lips(
            audio_envelope,
            [{"openness": m} for m in movement],
        )

    def _compute_correlation(
        self,
        seq1: List[float],
        seq2: List[float],
        offset: int,
    ) -> float:
        """
        Compute normalized cross-correlation with offset.

        Returns correlation coefficient (-1 to 1).
        """
        if offset >= 0:
            s1 = seq1[offset:]
            s2 = seq2[:len(s1)]
        else:
            s2 = seq2[-offset:]
            s1 = seq1[:len(s2)]

        n = min(len(s1), len(s2))
        if n < 2:
            return 0.0

        s1 = s1[:n]
        s2 = s2[:n]

        # Calculate means
        mean1 = sum(s1) / n
        mean2 = sum(s2) / n

        # Calculate correlation
        numerator = sum((s1[i] - mean1) * (s2[i] - mean2) for i in range(n))

        var1 = sum((s1[i] - mean1) ** 2 for i in range(n))
        var2 = sum((s2[i] - mean2) ** 2 for i in range(n))

        denominator = math.sqrt(var1 * var2)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _calculate_lip_sync_score(self, offset_ms: float) -> float:
        """
        Calculate lip sync quality score based on offset.

        Returns 0-1, higher = better sync.
        """
        if offset_ms <= self.SYNC_THRESHOLD_MS:
            # Good sync: linear scale from 1.0 at 0ms to 0.7 at threshold
            return 1.0 - (offset_ms / self.SYNC_THRESHOLD_MS) * 0.3
        elif offset_ms <= self.MAX_OFFSET_MS:
            # Poor sync: decreasing score
            normalized = (offset_ms - self.SYNC_THRESHOLD_MS) / (self.MAX_OFFSET_MS - self.SYNC_THRESHOLD_MS)
            return 0.7 * (1 - normalized)
        else:
            return 0.0
