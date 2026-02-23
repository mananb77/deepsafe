"""
Prosody Analyzer

Analyzes speech prosody (rhythm, stress, intonation) for synthetic patterns.
"""

import struct
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ProsodyAnalysisResult:
    """Result from prosody analysis."""

    is_synthetic: bool
    confidence: float  # 0-100
    pitch_variance: float
    energy_variance: float
    speaking_rate: float  # Estimated words per minute
    pause_pattern_score: float  # 0-1, higher = more natural
    emotion_consistency: float  # 0-1, higher = more consistent
    details: Dict[str, Any]


class ProsodyAnalyzer:
    """
    Analyzes prosodic features of speech for synthetic detection.

    Synthetic speech often exhibits:
    - Lower pitch variance than natural speech
    - More regular energy patterns
    - Unnatural pause patterns
    - Inconsistent emotional expression

    Detection methods:
    1. Pitch contour analysis
    2. Energy envelope analysis
    3. Pause pattern detection
    4. Speaking rate estimation
    """

    # Natural speech pitch variance range (Hz)
    NATURAL_PITCH_VARIANCE_MIN = 20.0
    NATURAL_PITCH_VARIANCE_MAX = 100.0

    # Energy variance thresholds
    NATURAL_ENERGY_VARIANCE_MIN = 0.1
    NATURAL_ENERGY_VARIANCE_MAX = 0.6

    # Speaking rate (words per minute)
    NATURAL_SPEAKING_RATE_MIN = 100
    NATURAL_SPEAKING_RATE_MAX = 180

    def __init__(
        self,
        frame_size: int = 512,
        hop_size: int = 160,
    ):
        self.frame_size = frame_size
        self.hop_size = hop_size

    def analyze(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
    ) -> ProsodyAnalysisResult:
        """
        Perform prosody analysis on audio data.

        Args:
            audio_data: Raw PCM audio bytes.
            sample_rate: Audio sample rate in Hz.

        Returns:
            ProsodyAnalysisResult with detection findings.
        """
        # Convert bytes to samples
        samples = self._bytes_to_samples(audio_data)

        if len(samples) < self.frame_size * 2:
            return ProsodyAnalysisResult(
                is_synthetic=False,
                confidence=0.0,
                pitch_variance=0.0,
                energy_variance=0.0,
                speaking_rate=0.0,
                pause_pattern_score=0.0,
                emotion_consistency=0.0,
                details={"error": "Audio too short for analysis"},
            )

        # Extract prosodic features
        pitch_values = self._extract_pitch(samples, sample_rate)
        energy_values = self._extract_energy(samples)
        pauses = self._detect_pauses(energy_values, sample_rate)

        # Calculate metrics
        pitch_variance = self._calculate_variance(pitch_values)
        energy_variance = self._calculate_variance(energy_values)
        speaking_rate = self._estimate_speaking_rate(samples, sample_rate, pauses)
        pause_score = self._score_pause_pattern(pauses)
        emotion_score = self._analyze_emotion_consistency(pitch_values, energy_values)

        # Calculate detection score
        score = self._calculate_score(
            pitch_variance,
            energy_variance,
            speaking_rate,
            pause_score,
            emotion_score,
        )

        is_synthetic = score > 50.0

        return ProsodyAnalysisResult(
            is_synthetic=is_synthetic,
            confidence=score,
            pitch_variance=pitch_variance,
            energy_variance=energy_variance,
            speaking_rate=speaking_rate,
            pause_pattern_score=pause_score,
            emotion_consistency=emotion_score,
            details={
                "pitch_values_count": len(pitch_values),
                "energy_values_count": len(energy_values),
                "pause_count": len(pauses),
                "sample_rate": sample_rate,
            },
        )

    def _bytes_to_samples(self, audio_data: bytes) -> List[float]:
        """Convert PCM bytes to normalized float samples."""
        num_samples = len(audio_data) // 2
        samples = struct.unpack(f"<{num_samples}h", audio_data[:num_samples * 2])
        return [s / 32768.0 for s in samples]

    def _extract_pitch(
        self,
        samples: List[float],
        sample_rate: int,
    ) -> List[float]:
        """
        Extract pitch values using autocorrelation.

        Returns list of estimated pitch values in Hz.
        """
        pitch_values = []
        min_period = int(sample_rate / 400)  # Max F0 = 400 Hz
        max_period = int(sample_rate / 60)   # Min F0 = 60 Hz

        for i in range(0, len(samples) - self.frame_size, self.hop_size):
            frame = samples[i:i + self.frame_size]

            # Compute autocorrelation
            autocorr = []
            for lag in range(min_period, min(max_period, len(frame) // 2)):
                corr = sum(
                    frame[j] * frame[j + lag]
                    for j in range(len(frame) - lag)
                )
                autocorr.append((lag, corr))

            if autocorr:
                # Find peak
                best_lag, best_corr = max(autocorr, key=lambda x: x[1])
                if best_corr > 0:
                    pitch = sample_rate / best_lag
                    if 60 < pitch < 400:  # Valid human pitch range
                        pitch_values.append(pitch)

        return pitch_values

    def _extract_energy(self, samples: List[float]) -> List[float]:
        """
        Extract frame-by-frame energy (RMS).

        Returns list of energy values.
        """
        energy_values = []

        for i in range(0, len(samples) - self.frame_size, self.hop_size):
            frame = samples[i:i + self.frame_size]
            rms = math.sqrt(sum(s * s for s in frame) / len(frame))
            energy_values.append(rms)

        return energy_values

    def _detect_pauses(
        self,
        energy_values: List[float],
        sample_rate: int,
    ) -> List[Dict[str, Any]]:
        """
        Detect pauses in speech based on energy.

        Returns list of pause dictionaries with start, duration, etc.
        """
        if not energy_values:
            return []

        # Calculate energy threshold (20% of mean energy)
        mean_energy = sum(energy_values) / len(energy_values)
        threshold = mean_energy * 0.2

        pauses = []
        in_pause = False
        pause_start = 0
        frame_duration = self.hop_size / sample_rate

        for i, energy in enumerate(energy_values):
            if energy < threshold:
                if not in_pause:
                    in_pause = True
                    pause_start = i
            else:
                if in_pause:
                    pause_duration = (i - pause_start) * frame_duration
                    if pause_duration > 0.1:  # Only count pauses > 100ms
                        pauses.append({
                            "start_frame": pause_start,
                            "end_frame": i,
                            "duration": pause_duration,
                        })
                    in_pause = False

        return pauses

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        return math.sqrt(variance)

    def _estimate_speaking_rate(
        self,
        samples: List[float],
        sample_rate: int,
        pauses: List[Dict[str, Any]],
    ) -> float:
        """
        Estimate speaking rate in words per minute.

        Uses syllable rate estimation as a proxy.
        """
        duration = len(samples) / sample_rate

        # Subtract pause time
        pause_time = sum(p["duration"] for p in pauses)
        speaking_time = max(duration - pause_time, 0.1)

        # Estimate syllables from energy peaks (simplified)
        # In production, use more sophisticated syllable detection
        energy = self._extract_energy(samples)
        if not energy:
            return 0.0

        mean_energy = sum(energy) / len(energy)
        peaks = sum(1 for e in energy if e > mean_energy * 1.5)

        # Estimate words (average 1.5 syllables per word)
        estimated_syllables = peaks
        estimated_words = estimated_syllables / 1.5

        # Calculate words per minute
        wpm = (estimated_words / speaking_time) * 60

        return min(max(wpm, 0), 300)

    def _score_pause_pattern(self, pauses: List[Dict[str, Any]]) -> float:
        """
        Score pause pattern naturalness.

        Natural speech has varied pause durations.
        Synthetic speech often has very regular pauses.

        Returns 0-1, higher = more natural.
        """
        if len(pauses) < 2:
            return 0.5  # Not enough data

        durations = [p["duration"] for p in pauses]
        variance = self._calculate_variance(durations)

        # Natural speech has varied pause durations (variance > 0.1)
        # Very regular pauses (low variance) are suspicious
        if variance < 0.05:
            return 0.2  # Too regular
        elif variance > 0.3:
            return 0.9  # Natural variation
        else:
            return 0.5 + (variance - 0.05) * 2

    def _analyze_emotion_consistency(
        self,
        pitch_values: List[float],
        energy_values: List[float],
    ) -> float:
        """
        Analyze emotional consistency between pitch and energy.

        Natural speech shows correlation between pitch and energy changes.
        Synthetic speech may have mismatched prosodic cues.

        Returns 0-1, higher = more consistent.
        """
        if len(pitch_values) < 3 or len(energy_values) < 3:
            return 0.5

        # Normalize to same length
        min_len = min(len(pitch_values), len(energy_values))
        pitch_norm = pitch_values[:min_len]
        energy_norm = energy_values[:min_len]

        # Calculate pitch and energy deltas
        pitch_deltas = [
            pitch_norm[i + 1] - pitch_norm[i]
            for i in range(min_len - 1)
        ]
        energy_deltas = [
            energy_norm[i + 1] - energy_norm[i]
            for i in range(min_len - 1)
        ]

        # Check correlation (simplified)
        if not pitch_deltas or not energy_deltas:
            return 0.5

        # Count matching direction changes
        matches = sum(
            1 for pd, ed in zip(pitch_deltas, energy_deltas)
            if (pd > 0 and ed > 0) or (pd < 0 and ed < 0) or (abs(pd) < 1 and abs(ed) < 0.01)
        )

        correlation = matches / len(pitch_deltas)
        return correlation

    def _calculate_score(
        self,
        pitch_variance: float,
        energy_variance: float,
        speaking_rate: float,
        pause_score: float,
        emotion_score: float,
    ) -> float:
        """
        Calculate overall synthetic detection score.

        Weights:
        - Pitch variance: 25%
        - Energy variance: 20%
        - Speaking rate: 15%
        - Pause pattern: 20%
        - Emotion consistency: 20%
        """
        scores = []

        # Pitch variance score (low variance = suspicious)
        if pitch_variance < self.NATURAL_PITCH_VARIANCE_MIN:
            pitch_score = 80 - pitch_variance
        elif pitch_variance > self.NATURAL_PITCH_VARIANCE_MAX:
            pitch_score = 30 + (pitch_variance - 100) * 0.3
        else:
            pitch_score = 20  # Normal range
        scores.append(("pitch", min(max(pitch_score, 0), 100), 0.25))

        # Energy variance score (very regular = suspicious)
        if energy_variance < self.NATURAL_ENERGY_VARIANCE_MIN:
            energy_score = 80
        elif energy_variance > self.NATURAL_ENERGY_VARIANCE_MAX:
            energy_score = 30
        else:
            energy_score = 20
        scores.append(("energy", min(max(energy_score, 0), 100), 0.20))

        # Speaking rate score
        if (speaking_rate < self.NATURAL_SPEAKING_RATE_MIN or
            speaking_rate > self.NATURAL_SPEAKING_RATE_MAX):
            rate_score = 60
        else:
            rate_score = 20
        scores.append(("rate", rate_score, 0.15))

        # Pause pattern score (inverted - low naturalness = suspicious)
        pause_detection_score = (1 - pause_score) * 100
        scores.append(("pause", pause_detection_score, 0.20))

        # Emotion consistency score (inverted)
        emotion_detection_score = (1 - emotion_score) * 100
        scores.append(("emotion", emotion_detection_score, 0.20))

        # Weighted sum
        total = sum(score * weight for _, score, weight in scores)

        return min(max(total, 0.0), 100.0)
