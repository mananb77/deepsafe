"""
Spectral Analyzer

Frequency-domain analysis for detecting synthetic audio markers.
"""

import struct
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import math


@dataclass
class SpectralAnalysisResult:
    """Result from spectral analysis."""

    is_synthetic: bool
    confidence: float  # 0-100
    synthetic_markers_detected: bool
    artifact_frequencies: List[float]
    formant_irregularities: int
    spectral_flatness: float
    details: Dict[str, Any]


class SpectralAnalyzer:
    """
    Analyzes audio spectrum for synthetic speech markers.

    Detection methods:
    1. FFT-based frequency analysis
    2. Formant detection and validation
    3. Spectral flatness (synthetic speech often has unusual flatness)
    4. Artifact detection at specific frequencies
    """

    # Frequencies commonly associated with synthesis artifacts (Hz)
    ARTIFACT_FREQUENCIES = [440, 880, 1320, 1760, 2200, 4000, 8000]

    # Normal formant ranges for human speech (Hz)
    FORMANT_RANGES = {
        "F1": (200, 900),    # First formant
        "F2": (800, 2500),   # Second formant
        "F3": (1800, 3500),  # Third formant
    }

    # Spectral flatness thresholds
    FLATNESS_SYNTHETIC_THRESHOLD = 0.6  # Above this is suspicious

    def __init__(
        self,
        fft_size: int = 2048,
        hop_size: int = 512,
    ):
        self.fft_size = fft_size
        self.hop_size = hop_size

    def analyze(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
    ) -> SpectralAnalysisResult:
        """
        Perform spectral analysis on audio data.

        Args:
            audio_data: Raw PCM audio bytes (16-bit signed).
            sample_rate: Audio sample rate in Hz.

        Returns:
            SpectralAnalysisResult with detection findings.
        """
        # Convert bytes to samples
        samples = self._bytes_to_samples(audio_data)

        if len(samples) < self.fft_size:
            return SpectralAnalysisResult(
                is_synthetic=False,
                confidence=0.0,
                synthetic_markers_detected=False,
                artifact_frequencies=[],
                formant_irregularities=0,
                spectral_flatness=0.0,
                details={"error": "Audio too short for analysis"},
            )

        # Compute FFT magnitude spectrum
        spectrum = self._compute_spectrum(samples)

        # Analyze for synthetic markers
        artifact_freqs = self._detect_artifacts(spectrum, sample_rate)
        formant_issues = self._analyze_formants(spectrum, sample_rate)
        flatness = self._compute_spectral_flatness(spectrum)

        # Calculate detection score
        score = self._calculate_score(artifact_freqs, formant_issues, flatness)

        is_synthetic = score > 50.0
        has_markers = len(artifact_freqs) > 0 or flatness > self.FLATNESS_SYNTHETIC_THRESHOLD

        return SpectralAnalysisResult(
            is_synthetic=is_synthetic,
            confidence=score,
            synthetic_markers_detected=has_markers,
            artifact_frequencies=artifact_freqs,
            formant_irregularities=formant_issues,
            spectral_flatness=flatness,
            details={
                "fft_size": self.fft_size,
                "sample_rate": sample_rate,
                "num_samples": len(samples),
                "artifact_count": len(artifact_freqs),
            },
        )

    def _bytes_to_samples(self, audio_data: bytes) -> List[float]:
        """Convert PCM bytes to normalized float samples."""
        # Assume 16-bit signed PCM
        num_samples = len(audio_data) // 2
        samples = struct.unpack(f"<{num_samples}h", audio_data[:num_samples * 2])
        # Normalize to -1.0 to 1.0
        return [s / 32768.0 for s in samples]

    def _compute_spectrum(self, samples: List[float]) -> List[float]:
        """
        Compute magnitude spectrum using FFT.

        Uses a simple DFT implementation for portability.
        In production, use numpy.fft or scipy.fft.
        """
        n = min(len(samples), self.fft_size)

        # Apply Hann window
        windowed = [
            samples[i] * 0.5 * (1 - math.cos(2 * math.pi * i / (n - 1)))
            for i in range(n)
        ]

        # Pad to FFT size
        while len(windowed) < self.fft_size:
            windowed.append(0.0)

        # Compute DFT (simplified - use numpy in production)
        spectrum = []
        for k in range(self.fft_size // 2):
            real = sum(
                windowed[n_idx] * math.cos(2 * math.pi * k * n_idx / self.fft_size)
                for n_idx in range(self.fft_size)
            )
            imag = sum(
                -windowed[n_idx] * math.sin(2 * math.pi * k * n_idx / self.fft_size)
                for n_idx in range(self.fft_size)
            )
            magnitude = math.sqrt(real * real + imag * imag)
            spectrum.append(magnitude)

        return spectrum

    def _detect_artifacts(
        self,
        spectrum: List[float],
        sample_rate: int,
    ) -> List[float]:
        """
        Detect synthesis artifacts at specific frequencies.

        Returns list of frequencies where artifacts were detected.
        """
        detected = []
        freq_resolution = sample_rate / self.fft_size

        # Calculate average magnitude for comparison
        avg_magnitude = sum(spectrum) / len(spectrum) if spectrum else 0

        for freq in self.ARTIFACT_FREQUENCIES:
            if freq > sample_rate / 2:
                continue

            bin_idx = int(freq / freq_resolution)
            if bin_idx < len(spectrum):
                # Check if this bin has unusually high energy
                if spectrum[bin_idx] > avg_magnitude * 3:
                    detected.append(freq)

        return detected

    def _analyze_formants(
        self,
        spectrum: List[float],
        sample_rate: int,
    ) -> int:
        """
        Analyze formant structure for irregularities.

        Returns count of formant irregularities detected.
        """
        irregularities = 0
        freq_resolution = sample_rate / self.fft_size

        for formant_name, (low, high) in self.FORMANT_RANGES.items():
            if high > sample_rate / 2:
                continue

            low_bin = int(low / freq_resolution)
            high_bin = int(high / freq_resolution)

            if high_bin >= len(spectrum):
                continue

            # Find peak in formant range
            formant_region = spectrum[low_bin:high_bin]
            if not formant_region:
                continue

            max_val = max(formant_region)
            avg_val = sum(formant_region) / len(formant_region)

            # Check for unusual flatness or excessive peaks
            if max_val < avg_val * 1.5:  # Too flat
                irregularities += 1
            elif max_val > avg_val * 10:  # Too peaky
                irregularities += 1

        return irregularities

    def _compute_spectral_flatness(self, spectrum: List[float]) -> float:
        """
        Compute spectral flatness (Wiener entropy).

        Spectral flatness measures how noise-like vs tonal the spectrum is.
        Synthetic speech often has unusual spectral flatness patterns.

        Returns value between 0 (tonal) and 1 (noise-like).
        """
        if not spectrum or len(spectrum) < 2:
            return 0.0

        # Filter out zero/near-zero values
        filtered = [max(s, 1e-10) for s in spectrum]

        # Geometric mean
        log_sum = sum(math.log(s) for s in filtered)
        geometric_mean = math.exp(log_sum / len(filtered))

        # Arithmetic mean
        arithmetic_mean = sum(filtered) / len(filtered)

        if arithmetic_mean == 0:
            return 0.0

        flatness = geometric_mean / arithmetic_mean
        return min(flatness, 1.0)

    def _calculate_score(
        self,
        artifact_freqs: List[float],
        formant_issues: int,
        flatness: float,
    ) -> float:
        """
        Calculate overall synthetic detection score.

        Weights:
        - Artifact detection: 40%
        - Formant irregularities: 30%
        - Spectral flatness: 30%
        """
        # Artifact score (0-100)
        artifact_score = min(len(artifact_freqs) * 20, 100)

        # Formant score (0-100)
        formant_score = min(formant_issues * 33, 100)

        # Flatness score (0-100)
        if flatness > self.FLATNESS_SYNTHETIC_THRESHOLD:
            flatness_score = min((flatness - 0.3) * 200, 100)
        else:
            flatness_score = flatness * 50

        # Weighted combination
        score = (
            artifact_score * 0.40 +
            formant_score * 0.30 +
            flatness_score * 0.30
        )

        return min(max(score, 0.0), 100.0)
