"""Unit tests for detection Celery tasks."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from src.services.stream.tasks.detection_tasks import (
    analyze_audio_task,
    analyze_video_task,
    analyze_combined_task,
    transcribe_audio_task,
    analyze_social_engineering_task,
    aggregate_risk_task,
)


class TestAnalyzeAudioTask:
    """Tests for analyze_audio_task."""

    def test_task_attributes(self):
        """Test task configuration attributes."""
        assert analyze_audio_task.name == "detection.analyze_audio"

    def test_analyze_audio_success(self):
        """Test successful audio analysis."""
        mock_service = MagicMock()
        mock_result = MagicMock()
        mock_result.confidence = 0.85
        mock_result.details = {"test": "data"}
        mock_service.detect_deepfake_sync.return_value = mock_result

        mock_service_class = MagicMock(return_value=mock_service)
        mock_module = MagicMock(AudioDetectionService=mock_service_class)

        import sys
        sys.modules["src.services.detection.audio.service"] = mock_module
        try:
            result = analyze_audio_task(
                chunk_data=b"audio_data",
                participant_id="p1",
                meeting_id="m1",
                chunk_id="chunk-1",
                sample_rate=16000,
            )

            assert result["chunk_id"] == "chunk-1"
            assert result["participant_id"] == "p1"
            assert result["meeting_id"] == "m1"
            assert "audio_deepfake_score" in result
            assert result["audio_deepfake_score"] == 0.85
        finally:
            sys.modules.pop("src.services.detection.audio.service", None)

    def test_analyze_audio_result_structure(self):
        """Test result structure matches expected format (services unavailable)."""
        result = analyze_audio_task(
            chunk_data=b"audio_data",
            participant_id="p1",
            meeting_id="m1",
            chunk_id="chunk-1",
        )

        # Check all expected fields
        assert "chunk_id" in result
        assert "participant_id" in result
        assert "meeting_id" in result
        assert "audio_deepfake_score" in result
        assert "voice_mismatch_score" in result
        assert "social_engineering_score" in result
        assert "confidence" in result
        assert "details" in result

    def test_analyze_audio_zero_scores_when_unavailable(self):
        """Test zero scores when detection services unavailable."""
        result = analyze_audio_task(
            chunk_data=b"audio_data",
            participant_id="p1",
            meeting_id="m1",
            chunk_id="chunk-1",
        )

        # Should return result with zero scores when service unavailable
        assert result["audio_deepfake_score"] == 0.0


class TestAnalyzeVideoTask:
    """Tests for analyze_video_task."""

    def test_task_attributes(self):
        """Test task configuration attributes."""
        assert analyze_video_task.name == "detection.analyze_video"

    def test_analyze_video_success(self):
        """Test successful video analysis."""
        mock_service = MagicMock()
        mock_result = MagicMock()
        mock_result.confidence = 0.75
        mock_result.details = {"facial": "data"}
        mock_service.detect_deepfake_sync.return_value = mock_result

        mock_service_class = MagicMock(return_value=mock_service)
        mock_module = MagicMock(VideoDetectionService=mock_service_class)

        import sys
        sys.modules["src.services.detection.video.service"] = mock_module
        try:
            result = analyze_video_task(
                frame_data=b"frame_data",
                participant_id="p1",
                meeting_id="m1",
                width=640,
                height=480,
                frame_number=1,
            )

            assert result["participant_id"] == "p1"
            assert result["meeting_id"] == "m1"
            assert result["frame_number"] == 1
            assert "video_deepfake_score" in result
            assert result["video_deepfake_score"] == 0.75
        finally:
            sys.modules.pop("src.services.detection.video.service", None)

    def test_analyze_video_result_structure(self):
        """Test result structure matches expected format."""
        result = analyze_video_task(
            frame_data=b"frame_data",
            participant_id="p1",
            meeting_id="m1",
            width=640,
            height=480,
        )

        assert "participant_id" in result
        assert "meeting_id" in result
        assert "frame_number" in result
        assert "video_deepfake_score" in result
        assert "facial_anomaly_score" in result
        assert "av_sync_score" in result
        assert "confidence" in result
        assert "details" in result

    def test_analyze_video_zero_scores_when_unavailable(self):
        """Test zero scores when detection services unavailable."""
        result = analyze_video_task(
            frame_data=b"frame_data",
            participant_id="p1",
            meeting_id="m1",
            width=640,
            height=480,
        )

        assert result["video_deepfake_score"] == 0.0


class TestAnalyzeCombinedTask:
    """Tests for analyze_combined_task."""

    def test_task_attributes(self):
        """Test task configuration attributes."""
        assert analyze_combined_task.name == "detection.analyze_combined"

    def test_analyze_combined_result_structure(self):
        """Test combined analysis result structure."""
        result = analyze_combined_task(
            audio_data=b"audio",
            video_data=b"video",
            participant_id="p1",
            meeting_id="m1",
            audio_sample_rate=16000,
            video_width=640,
            video_height=480,
        )

        # Check combined result fields
        assert "participant_id" in result
        assert "meeting_id" in result
        assert "audio_deepfake_score" in result
        assert "video_deepfake_score" in result
        assert "combined_risk_score" in result
        assert "risk_level" in result

    def test_combined_risk_score_calculation(self):
        """Test that combined risk score is calculated."""
        result = analyze_combined_task(
            audio_data=b"audio",
            video_data=b"video",
            participant_id="p1",
            meeting_id="m1",
        )

        # Combined score should be between 0 and 1
        assert 0.0 <= result["combined_risk_score"] <= 1.0

    def test_risk_level_classification(self):
        """Test risk level is assigned."""
        result = analyze_combined_task(
            audio_data=b"audio",
            video_data=b"video",
            participant_id="p1",
            meeting_id="m1",
        )

        assert result["risk_level"] in ["low", "medium", "high", "critical"]


class TestTranscribeAudioTask:
    """Tests for transcribe_audio_task."""

    def test_task_attributes(self):
        """Test task configuration attributes."""
        assert transcribe_audio_task.name == "detection.transcribe_audio"

    def test_transcribe_success(self):
        """Test successful transcription."""
        mock_service = MagicMock()
        mock_result = MagicMock()
        mock_result.text = "Hello world"
        mock_result.confidence = 0.95
        mock_result.words = [{"word": "Hello"}, {"word": "world"}]
        mock_service.transcribe_sync.return_value = mock_result

        mock_service_class = MagicMock(return_value=mock_service)
        mock_module = MagicMock(TranscriptionService=mock_service_class)

        import sys
        sys.modules["src.shared.external.transcription"] = mock_module
        try:
            result = transcribe_audio_task(
                chunk_data=b"audio_data",
                participant_id="p1",
                meeting_id="m1",
                chunk_id="chunk-1",
            )

            assert result["transcript"] == "Hello world"
            assert result["confidence"] == 0.95
        finally:
            sys.modules.pop("src.shared.external.transcription", None)

    def test_transcribe_result_structure(self):
        """Test transcription result structure."""
        result = transcribe_audio_task(
            chunk_data=b"audio_data",
            participant_id="p1",
            meeting_id="m1",
            chunk_id="chunk-1",
        )

        assert "chunk_id" in result
        assert "participant_id" in result
        assert "meeting_id" in result
        assert "transcript" in result
        assert "confidence" in result
        assert "words" in result
        assert "language" in result


class TestAnalyzeSocialEngineeringTask:
    """Tests for analyze_social_engineering_task."""

    def test_task_attributes(self):
        """Test task configuration attributes."""
        assert analyze_social_engineering_task.name == "analysis.social_engineering"

    def test_analyze_success(self):
        """Test successful social engineering analysis."""
        mock_detector = MagicMock()
        mock_result = MagicMock()
        mock_result.risk_score = 0.65
        mock_result.scenario_scores = {"bec": 0.7}
        mock_result.keyword_matches = ["urgent", "wire transfer"]
        mock_result.tactics_detected = ["authority", "urgency"]
        mock_result.confidence = 0.8
        mock_result.details = {}
        mock_detector.analyze_sync.return_value = mock_result

        mock_detector_class = MagicMock(return_value=mock_detector)
        mock_module = MagicMock(SocialEngineeringDetector=mock_detector_class)

        import sys
        sys.modules["src.services.detection.social_engineering.service"] = mock_module
        try:
            result = analyze_social_engineering_task(
                transcript="Please wire transfer $50000 urgently",
                participant_id="p1",
                meeting_id="m1",
            )

            assert result["risk_score"] == 0.65
            assert result["tactics_detected"] == ["authority", "urgency"]
        finally:
            sys.modules.pop("src.services.detection.social_engineering.service", None)

    def test_analyze_result_structure(self):
        """Test result structure."""
        result = analyze_social_engineering_task(
            transcript="Normal conversation",
            participant_id="p1",
            meeting_id="m1",
        )

        assert "participant_id" in result
        assert "meeting_id" in result
        assert "risk_score" in result
        assert "scenario_scores" in result
        assert "keyword_matches" in result
        assert "tactics_detected" in result
        assert "confidence" in result


class TestAggregateRiskTask:
    """Tests for aggregate_risk_task."""

    def test_task_attributes(self):
        """Test task configuration attributes."""
        assert aggregate_risk_task.name == "analysis.aggregate_risk"

    def test_aggregate_empty_results(self):
        """Test aggregation with no results."""
        result = aggregate_risk_task(
            meeting_id="m1",
            participant_results={},
        )

        assert result["meeting_id"] == "m1"
        assert result["overall_risk_score"] == 0.0
        assert result["risk_level"] == "low"
        assert result["high_risk_participants"] == []

    def test_aggregate_single_participant(self):
        """Test aggregation with single participant."""
        result = aggregate_risk_task(
            meeting_id="m1",
            participant_results={
                "p1": {
                    "combined_risk_score": 0.75,
                    "risk_level": "high",
                },
            },
        )

        assert result["overall_risk_score"] == 0.75
        assert result["risk_level"] == "high"
        assert "p1" in result["high_risk_participants"]

    def test_aggregate_multiple_participants(self):
        """Test aggregation with multiple participants."""
        result = aggregate_risk_task(
            meeting_id="m1",
            participant_results={
                "p1": {"combined_risk_score": 0.3, "risk_level": "low"},
                "p2": {"combined_risk_score": 0.7, "risk_level": "high"},
                "p3": {"combined_risk_score": 0.9, "risk_level": "critical"},
            },
        )

        # Overall should be max of participants
        assert result["overall_risk_score"] == 0.9
        assert result["risk_level"] == "critical"
        assert "p2" in result["high_risk_participants"]
        assert "p3" in result["high_risk_participants"]
        assert "p1" not in result["high_risk_participants"]

    def test_aggregate_result_structure(self):
        """Test aggregation result structure."""
        result = aggregate_risk_task(
            meeting_id="m1",
            participant_results={
                "p1": {"combined_risk_score": 0.5, "risk_level": "medium"},
            },
        )

        assert "meeting_id" in result
        assert "overall_risk_score" in result
        assert "risk_level" in result
        assert "participant_risks" in result
        assert "high_risk_participants" in result
        assert "alerts" in result


class TestTaskRetryBehavior:
    """Tests for task retry behavior."""

    def test_audio_task_retry_config(self):
        """Test audio task retry configuration."""
        assert analyze_audio_task.max_retries == 2

    def test_video_task_retry_config(self):
        """Test video task retry configuration."""
        assert analyze_video_task.max_retries == 2

    def test_combined_task_retry_config(self):
        """Test combined task retry configuration."""
        assert analyze_combined_task.max_retries == 1


class TestTaskTimeLimits:
    """Tests for task time limits."""

    def test_audio_task_time_limits(self):
        """Test audio task time limits."""
        assert analyze_audio_task.soft_time_limit == 10
        assert analyze_audio_task.time_limit == 15

    def test_video_task_time_limits(self):
        """Test video task time limits."""
        assert analyze_video_task.soft_time_limit == 15
        assert analyze_video_task.time_limit == 20

    def test_combined_task_time_limits(self):
        """Test combined task time limits."""
        assert analyze_combined_task.soft_time_limit == 20
        assert analyze_combined_task.time_limit == 30

    def test_transcribe_task_time_limits(self):
        """Test transcription task time limits."""
        assert transcribe_audio_task.soft_time_limit == 30
        assert transcribe_audio_task.time_limit == 45
