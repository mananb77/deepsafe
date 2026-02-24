"""
Tests for Ollama Local LLM Analyzer
"""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import httpx

from src.services.detection.social_engineering.ollama_analyzer import OllamaAnalyzer
from src.services.detection.social_engineering.gpt4_analyzer import GPT4AnalysisResult


class TestOllamaAnalyzer:
    """Tests for OllamaAnalyzer class."""

    @pytest.fixture
    def analyzer(self) -> OllamaAnalyzer:
        """Create analyzer instance."""
        return OllamaAnalyzer(
            model="phi3:mini",
            ollama_url="http://localhost:11434",
            timeout=10.0,
        )

    @pytest.fixture
    def mock_response_data(self) -> dict:
        """Create mock Ollama response."""
        return {
            "message": {
                "content": json.dumps(
                    {
                        "is_suspicious": True,
                        "confidence": 75.0,
                        "intent_classification": "suspicious",
                        "manipulation_tactics": ["urgency", "authority"],
                        "risk_assessment": "high",
                        "reasoning": "The conversation contains pressure tactics",
                        "recommendations": ["Verify identity through secondary channel"],
                    }
                )
            }
        }

    async def test_analyze_returns_gpt4_result(self, analyzer, mock_response_data):
        """Test that analyze returns GPT4AnalysisResult."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await analyzer.analyze("This is a test transcript for analysis.")

        assert isinstance(result, GPT4AnalysisResult)
        assert result.is_suspicious is True
        assert result.confidence == 75.0
        assert result.intent_classification == "suspicious"
        assert "urgency" in result.manipulation_tactics

    async def test_analyze_short_transcript(self, analyzer):
        """Test that short transcripts return early."""
        result = await analyzer.analyze("Hi")
        assert isinstance(result, GPT4AnalysisResult)
        assert result.confidence == 0.0
        assert "Insufficient content" in result.reasoning

    async def test_analyze_empty_transcript(self, analyzer):
        """Test that empty transcripts return early."""
        result = await analyzer.analyze("")
        assert result.confidence == 0.0

    async def test_analyze_connection_error(self, analyzer):
        """Test handling when Ollama is not running."""
        with patch(
            "httpx.AsyncClient.post",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            result = await analyzer.analyze("Test transcript for analysis purposes.")

        assert isinstance(result, GPT4AnalysisResult)
        assert result.confidence == 0.0
        assert "Cannot connect to Ollama" in result.reasoning

    async def test_analyze_timeout(self, analyzer):
        """Test handling of request timeout."""
        with patch(
            "httpx.AsyncClient.post",
            new_callable=AsyncMock,
            side_effect=httpx.TimeoutException("Timeout"),
        ):
            result = await analyzer.analyze("Test transcript for analysis purposes.")

        assert isinstance(result, GPT4AnalysisResult)
        assert "timeout" in result.reasoning.lower()

    async def test_analyze_invalid_json_response(self, analyzer):
        """Test handling of non-JSON response from Ollama."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": {"content": "not valid json"}}

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await analyzer.analyze("Test transcript for analysis purposes.")

        assert isinstance(result, GPT4AnalysisResult)
        assert "JSON parse error" in result.reasoning

    async def test_analyze_api_error_status(self, analyzer):
        """Test handling of non-200 status code."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await analyzer.analyze("Test transcript for analysis purposes.")

        assert isinstance(result, GPT4AnalysisResult)
        assert "500" in result.reasoning

    async def test_health_check_success(self, analyzer):
        """Test health check when Ollama is running."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            result = await analyzer.health_check()

        assert result is True

    async def test_health_check_failure(self, analyzer):
        """Test health check when Ollama is not running."""
        with patch(
            "httpx.AsyncClient.get",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            result = await analyzer.health_check()

        assert result is False

    async def test_analyze_with_context(self, analyzer, mock_response_data):
        """Test analyze with meeting context and participant info."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await analyzer.analyze(
                "Test transcript for analysis purposes.",
                meeting_context={"title": "Board Meeting", "organizer": "CEO"},
                participant_info={"John": "CFO (john@company.com)"},
            )

        assert isinstance(result, GPT4AnalysisResult)
        assert result.details.get("source") == "ollama_local"
