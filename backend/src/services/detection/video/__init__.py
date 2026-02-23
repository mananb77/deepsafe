"""
Video Deepfake Detection Module

Multi-method detection combining:
- Sensity/GetReal API (primary)
- Facial landmark analysis
- Micro-expression analysis
- Lighting/shadow analysis
- Virtual camera detection
- EfficientNet-B4 fallback model
"""

from src.services.detection.video.detector import VideoDeepfakeDetector
from src.services.detection.video.sensity_client import SensityClient
from src.services.detection.video.facial_landmark_detector import (
    FacialLandmarkDetector,
    FacialLandmarks,
    LandmarkAnalysisResult,
)
from src.services.detection.video.micro_expression_analyzer import (
    MicroExpressionAnalyzer,
    MicroExpressionResult,
    FaceRegion,
)
from src.services.detection.video.lighting_analyzer import (
    LightingAnalyzer,
    LightingAnalysisResult,
    FrameLightingData,
)
from src.services.detection.video.virtual_camera_detector import (
    VirtualCameraDetector,
    VirtualCameraResult,
)

__all__ = [
    "VideoDeepfakeDetector",
    "SensityClient",
    "FacialLandmarkDetector",
    "FacialLandmarks",
    "LandmarkAnalysisResult",
    "MicroExpressionAnalyzer",
    "MicroExpressionResult",
    "FaceRegion",
    "LightingAnalyzer",
    "LightingAnalysisResult",
    "FrameLightingData",
    "VirtualCameraDetector",
    "VirtualCameraResult",
]
