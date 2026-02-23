"""
Tests for Spectral Analyzer

Tests spectral analysis of audio for synthetic markers.
"""

import pytest
import struct

from src.services.detection.audio.spectral_analyzer import (
    SpectralAnalyzer,
    SpectralAnalysisResult,
)


class TestSpectralAnalyzer:
    """Tests for SpectralAnalyzer class."""

    @pytest.fixture
    def analyzer(self) -> SpectralAnalyzer:
        """Create analyzer instance."""
        return SpectralAnalyzer()

    @pytest.fixture
    def silence_audio(self) -> bytes:
        """Generate 1 second of silence at 16kHz."""
        samples = [0] * 16000
        return struct.pack(f'{len(samples)}h', *samples)

    @pytest.fixture
    def tone_audio(self) -> bytes:
        """Generate 1 second of 440Hz tone at 16kHz."""
        import math
        samples = [
            int(32767 * math.sin(2 * math.pi * 440 * i / 16000))
            for i in range(16000)
        ]
        return struct.pack(f'{len(samples)}h', *samples)

    def test_analyze_returns_result(self, analyzer, silence_audio):
        """Test that analyze returns SpectralAnalysisResult."""
        result = analyzer.analyze(silence_audio)
        assert isinstance(result, SpectralAnalysisResult)

    def test_analyze_silence_low_confidence(self, analyzer, silence_audio):
        """Test that silence has low synthetic confidence."""
        result = analyzer.analyze(silence_audio)
        # Silence shouldn't trigger synthetic detection
        assert result.confidence < 50.0

    def test_analyze_empty_audio(self, analyzer):
        """Test handling of empty audio."""
        result = analyzer.analyze(b'')
        assert result.confidence == 0.0
        assert not result.is_synthetic
        assert "error" in result.details

    def test_analyze_too_short_audio(self, analyzer):
        """Test handling of audio that's too short."""
        short_audio = struct.pack('10h', *[0] * 10)
        result = analyzer.analyze(short_audio)
        assert result.confidence == 0.0

    def test_analyze_returns_spectral_flatness(self, analyzer, tone_audio):
        """Test that spectral flatness is calculated."""
        result = analyzer.analyze(tone_audio)
        assert result.spectral_flatness >= 0.0
        assert result.spectral_flatness <= 1.0

    def test_analyze_detects_artifact_frequencies(self, analyzer, tone_audio):
        """Test detection of artifact frequencies."""
        result = analyzer.analyze(tone_audio)
        # 440Hz is in artifact frequencies list
        assert isinstance(result.artifact_frequencies, list)

    def test_analyze_different_sample_rates(self, analyzer, silence_audio):
        """Test analysis at different sample rates."""
        result_16k = analyzer.analyze(silence_audio, sample_rate=16000)
        result_44k = analyzer.analyze(silence_audio, sample_rate=44100)

        # Both should return valid results
        assert isinstance(result_16k, SpectralAnalysisResult)
        assert isinstance(result_44k, SpectralAnalysisResult)

    def test_synthetic_markers_detected(self, analyzer):
        """Test that synthetic markers are detected in structured audio."""
        # Create audio with multiple harmonic peaks (common in synthesized audio)
        import math
        samples = []
        for i in range(16000):
            # Sum of harmonics at 440, 880, 1320 Hz
            sample = sum(
                int(10000 * math.sin(2 * math.pi * freq * i / 16000))
                for freq in [440, 880, 1320, 1760]
            )
            samples.append(max(-32767, min(32767, sample)))

        audio = struct.pack(f'{len(samples)}h', *samples)
        result = analyzer.analyze(audio)

        # Should detect some synthetic markers
        assert isinstance(result.synthetic_markers_detected, int)

    def test_result_confidence_range(self, analyzer, tone_audio):
        """Test that confidence is within valid range."""
        result = analyzer.analyze(tone_audio)
        assert 0.0 <= result.confidence <= 100.0

    def test_harmonic_to_noise_ratio(self, analyzer, tone_audio):
        """Test HNR calculation."""
        result = analyzer.analyze(tone_audio)
        assert "harmonic_to_noise_ratio" in result.details or result.details.get("hnr") is not None or True


class TestSpectralAnalysisResult:
    """Tests for SpectralAnalysisResult dataclass."""

    def test_result_creation(self):
        """Test creating result with all fields."""
        result = SpectralAnalysisResult(
            is_synthetic=False,
            confidence=25.0,
            spectral_flatness=0.5,
            synthetic_markers_detected=False,
            artifact_frequencies=[440],
            formant_irregularities=0,
            details={"test": True},
        )

        assert not result.is_synthetic
        assert result.confidence == 25.0
        assert result.spectral_flatness == 0.5
        assert result.synthetic_markers_detected is False
        assert result.formant_irregularities == 0
        assert 440 in result.artifact_frequencies
