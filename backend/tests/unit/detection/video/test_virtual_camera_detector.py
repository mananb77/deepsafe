"""
Tests for Virtual Camera Detector

Tests detection of virtual camera software.
"""

import pytest

from src.services.detection.video.virtual_camera_detector import (
    VirtualCameraDetector,
    VirtualCameraResult,
)


class TestVirtualCameraDetector:
    """Tests for VirtualCameraDetector class."""

    @pytest.fixture
    def detector(self) -> VirtualCameraDetector:
        """Create detector instance."""
        return VirtualCameraDetector()

    # --- Device Name Detection Tests ---

    def test_detect_obs_virtual_camera(self, detector):
        """Test detection of OBS Virtual Camera."""
        result = detector.analyze(device_name="OBS Virtual Camera")
        assert result.is_virtual
        assert result.detected_software == "OBS Studio"
        assert result.confidence > 50

    def test_detect_snap_camera(self, detector):
        """Test detection of Snap Camera."""
        result = detector.analyze(device_name="Snap Camera")
        assert result.is_virtual
        assert result.detected_software == "Snap Camera"

    def test_detect_manycam(self, detector):
        """Test detection of ManyCam."""
        result = detector.analyze(device_name="ManyCam Virtual Webcam")
        assert result.is_virtual
        assert result.detected_software == "ManyCam"

    def test_detect_xsplit_vcam(self, detector):
        """Test detection of XSplit VCam."""
        result = detector.analyze(device_name="XSplit VCam")
        assert result.is_virtual
        assert result.detected_software == "XSplit VCam"

    def test_detect_mmhmm(self, detector):
        """Test detection of mmhmm."""
        result = detector.analyze(device_name="mmhmm Camera")
        assert result.is_virtual
        assert result.detected_software == "mmhmm"

    def test_detect_ndi(self, detector):
        """Test detection of NDI Virtual Input."""
        result = detector.analyze(device_name="NDI Video")
        assert result.is_virtual
        assert result.detected_software == "NDI Virtual Input"

    def test_detect_generic_virtual(self, detector):
        """Test detection of generic virtual camera indicators."""
        result = detector.analyze(device_name="Virtual Webcam Device")
        assert result.is_virtual
        assert "virtual" in result.detected_software.lower()

    def test_real_camera_not_detected(self, detector):
        """Test that real cameras are not flagged as virtual."""
        result = detector.analyze(device_name="Logitech HD Webcam C920")
        assert not result.is_virtual
        assert result.detected_software is None

    def test_builtin_camera_not_detected(self, detector):
        """Test that built-in cameras are not flagged."""
        result = detector.analyze(device_name="FaceTime HD Camera")
        assert not result.is_virtual

    def test_case_insensitive_detection(self, detector):
        """Test that detection is case-insensitive."""
        result1 = detector.analyze(device_name="OBS VIRTUAL CAMERA")
        result2 = detector.analyze(device_name="obs virtual camera")
        result3 = detector.analyze(device_name="Obs Virtual Camera")

        assert all(r.is_virtual for r in [result1, result2, result3])

    # --- Frame Timing Detection Tests ---

    def test_detect_suspicious_frame_timing(self, detector):
        """Test detection of suspicious frame timing patterns."""
        # Very consistent timing (like pre-recorded video)
        timestamps = [i * 0.0333 for i in range(100)]  # Exactly 30fps

        result = detector.analyze(frame_timestamps=timestamps)
        # Very consistent timing is suspicious
        assert "timing" in str(result.indicators).lower() or result.confidence > 0

    def test_normal_frame_timing(self, detector):
        """Test that normal frame timing isn't flagged."""
        import random
        # Natural timing with some variance
        timestamps = []
        t = 0
        for _ in range(100):
            timestamps.append(t)
            t += 0.0333 + random.uniform(-0.005, 0.005)  # ~30fps with jitter

        result = detector.analyze(frame_timestamps=timestamps)
        # Natural timing shouldn't have high confidence
        assert result.confidence < 50 or not result.is_virtual

    def test_insufficient_timestamps(self, detector):
        """Test handling of insufficient timestamps."""
        result = detector.analyze(frame_timestamps=[0.0, 0.033])
        # Not enough data for timing analysis
        assert result.confidence < 50

    # --- Metadata Detection Tests ---

    def test_detect_virtual_camera_metadata(self, detector):
        """Test detection via metadata."""
        result = detector.analyze(
            frame_metadata={"virtual_camera": True}
        )
        assert "Metadata indicates virtual camera" in result.indicators

    def test_detect_source_type_virtual(self, detector):
        """Test detection of virtual source type."""
        result = detector.analyze(
            frame_metadata={"source_type": "virtual"}
        )
        assert any("source type" in i.lower() for i in result.indicators)

    def test_detect_screen_capture(self, detector):
        """Test detection of screen capture source."""
        result = detector.analyze(
            frame_metadata={"source_type": "screen"}
        )
        assert any("source type" in i.lower() for i in result.indicators)

    def test_detect_unusual_aspect_ratio(self, detector):
        """Test detection of unusual aspect ratios."""
        # Very narrow aspect ratio (like a vertical phone screen capture)
        result = detector.analyze(
            frame_metadata={"width": 1080, "height": 1920}
        )
        assert any("aspect" in i.lower() for i in result.indicators)

    # --- Combined Detection Tests ---

    def test_combined_detection(self, detector):
        """Test detection using multiple indicators."""
        # Consistent timing + suspicious device name
        timestamps = [i * 0.0333 for i in range(100)]

        result = detector.analyze(
            device_name="OBS Virtual Camera",
            frame_timestamps=timestamps,
        )

        assert result.is_virtual
        assert result.confidence > 70
        assert len(result.indicators) >= 1

    def test_no_data_provided(self, detector):
        """Test handling when no data is provided."""
        result = detector.analyze()
        assert not result.is_virtual
        assert result.confidence == 0.0

    # --- Utility Method Tests ---

    def test_get_known_virtual_cameras(self, detector):
        """Test getting list of known virtual camera software."""
        known = detector.get_known_virtual_cameras()

        assert isinstance(known, set)
        assert "OBS Studio" in known
        assert "Snap Camera" in known
        assert "ManyCam" in known


class TestVirtualCameraResult:
    """Tests for VirtualCameraResult dataclass."""

    def test_result_creation(self):
        """Test creating result with all fields."""
        result = VirtualCameraResult(
            is_virtual=True,
            confidence=85.0,
            detected_software="OBS Studio",
            indicators=["Device name matches: OBS Studio"],
            details={"device_name": "OBS Virtual Camera"},
        )

        assert result.is_virtual
        assert result.confidence == 85.0
        assert result.detected_software == "OBS Studio"
        assert len(result.indicators) == 1

    def test_result_not_virtual(self):
        """Test result for non-virtual camera."""
        result = VirtualCameraResult(
            is_virtual=False,
            confidence=0.0,
            detected_software=None,
            indicators=[],
            details={"device_name": "Logitech C920"},
        )

        assert not result.is_virtual
        assert result.detected_software is None
        assert len(result.indicators) == 0
