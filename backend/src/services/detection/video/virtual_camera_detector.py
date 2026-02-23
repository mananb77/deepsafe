"""
Virtual Camera Detector

Detects virtual camera software being used instead of real webcam.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


@dataclass
class VirtualCameraResult:
    """Result from virtual camera detection."""

    is_virtual: bool
    confidence: float  # 0-100
    detected_software: Optional[str]
    indicators: List[str]
    details: Dict[str, Any]


class VirtualCameraDetector:
    """
    Detects virtual camera software usage.

    Virtual cameras can be used to inject pre-recorded or AI-generated
    video into a meeting, bypassing real-time face detection.

    Detection methods:
    1. Device name pattern matching
    2. Frame metadata analysis
    3. Timing pattern detection
    4. Encoding artifact detection
    """

    # Known virtual camera device names
    VIRTUAL_CAMERA_PATTERNS = {
        # OBS
        "obs virtual camera": "OBS Studio",
        "obs-camera": "OBS Studio",
        "obs virtualcam": "OBS Studio",

        # Snap Camera
        "snap camera": "Snap Camera",
        "snapcamera": "Snap Camera",

        # ManyCam
        "manycam": "ManyCam",
        "many cam": "ManyCam",

        # XSplit
        "xsplit": "XSplit VCam",
        "xsplit vcam": "XSplit VCam",

        # CamTwist
        "camtwist": "CamTwist",
        "cam twist": "CamTwist",

        # Avatarify
        "avatarify": "Avatarify",

        # NDI
        "ndi": "NDI Virtual Input",
        "newtek ndi": "NDI Virtual Input",

        # SplitCam
        "splitcam": "SplitCam",

        # Chromacam
        "chromacam": "ChromaCam",

        # mmhmm
        "mmhmm": "mmhmm",

        # Loom
        "loom": "Loom Camera",

        # Generic virtual camera indicators
        "virtual": None,
        "vcam": None,
        "v-cam": None,
        "screen capture": None,
        "capture card": None,
    }

    # Frame timing patterns for pre-recorded video
    TIMING_VARIANCE_THRESHOLD = 0.1  # 10% variance is suspicious

    def __init__(self):
        pass

    def analyze(
        self,
        device_name: Optional[str] = None,
        frame_timestamps: Optional[List[float]] = None,
        frame_metadata: Optional[Dict[str, Any]] = None,
    ) -> VirtualCameraResult:
        """
        Analyze for virtual camera indicators.

        Args:
            device_name: Camera device name.
            frame_timestamps: List of frame arrival timestamps.
            frame_metadata: Additional frame/device metadata.

        Returns:
            VirtualCameraResult with detection findings.
        """
        indicators = []
        detected_software = None
        confidence = 0.0

        # Check device name
        if device_name:
            name_result = self._check_device_name(device_name)
            if name_result:
                detected_software = name_result
                indicators.append(f"Device name matches: {name_result}")
                confidence += 80

        # Check frame timing patterns
        if frame_timestamps and len(frame_timestamps) > 2:
            timing_suspicious = self._check_frame_timing(frame_timestamps)
            if timing_suspicious:
                indicators.append("Unusual frame timing pattern")
                confidence += 30

        # Check frame metadata
        if frame_metadata:
            metadata_indicators = self._check_metadata(frame_metadata)
            indicators.extend(metadata_indicators)
            confidence += len(metadata_indicators) * 15

        # Normalize confidence
        confidence = min(confidence, 100)

        is_virtual = confidence > 50 or detected_software is not None

        return VirtualCameraResult(
            is_virtual=is_virtual,
            confidence=confidence,
            detected_software=detected_software,
            indicators=indicators,
            details={
                "device_name": device_name,
                "timestamps_checked": len(frame_timestamps) if frame_timestamps else 0,
                "metadata_checked": bool(frame_metadata),
            },
        )

    def _check_device_name(self, device_name: str) -> Optional[str]:
        """
        Check device name for virtual camera patterns.

        Returns detected software name or None.
        """
        name_lower = device_name.lower()

        for pattern, software in self.VIRTUAL_CAMERA_PATTERNS.items():
            if pattern in name_lower:
                return software or f"Unknown virtual camera ({pattern})"

        return None

    def _check_frame_timing(self, timestamps: List[float]) -> bool:
        """
        Check frame timing for pre-recorded video patterns.

        Pre-recorded video often has very consistent frame intervals.

        Returns True if suspicious.
        """
        if len(timestamps) < 3:
            return False

        # Calculate frame intervals
        intervals = [
            timestamps[i + 1] - timestamps[i]
            for i in range(len(timestamps) - 1)
        ]

        if not intervals:
            return False

        # Calculate mean and variance
        mean_interval = sum(intervals) / len(intervals)
        if mean_interval == 0:
            return False

        variance = sum((i - mean_interval) ** 2 for i in intervals) / len(intervals)
        std_dev = variance ** 0.5

        # Coefficient of variation
        cv = std_dev / mean_interval

        # Very low variance (too consistent) is suspicious
        # Real cameras have natural timing variance from USB/driver
        if cv < self.TIMING_VARIANCE_THRESHOLD:
            return True

        return False

    def _check_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Check metadata for virtual camera indicators.

        Returns list of indicator descriptions.
        """
        indicators = []

        # Check for virtual camera specific metadata
        if metadata.get("virtual_camera"):
            indicators.append("Metadata indicates virtual camera")

        if metadata.get("source_type") in ["virtual", "screen", "window"]:
            indicators.append(f"Source type: {metadata.get('source_type')}")

        # Check for unusual resolution patterns
        width = metadata.get("width", 0)
        height = metadata.get("height", 0)
        if width > 0 and height > 0:
            # Non-standard aspect ratios might indicate screen capture
            aspect = width / height
            if aspect < 1.0 or aspect > 2.5:
                indicators.append(f"Unusual aspect ratio: {aspect:.2f}")

        # Check for codec indicators
        codec = metadata.get("codec", "").lower()
        if codec and any(x in codec for x in ["screen", "capture", "virtual"]):
            indicators.append(f"Suspicious codec: {codec}")

        # Check for software encoding (vs hardware)
        if metadata.get("encoder_type") == "software":
            # Software encoding could indicate virtual camera
            # but is not definitive
            pass

        return indicators

    def get_known_virtual_cameras(self) -> Set[str]:
        """Return set of known virtual camera software names."""
        return {v for v in self.VIRTUAL_CAMERA_PATTERNS.values() if v}
