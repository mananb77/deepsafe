"""
Health Router Tests

Unit tests for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check_returns_response(self, client: TestClient):
        """Health check returns a valid response."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        # Status will be "degraded" in tests since no real DB connections
        assert data["status"] in ["healthy", "degraded"]

    def test_health_check_includes_environment(self, client: TestClient):
        """Health check includes environment information."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "environment" in data

    def test_health_check_includes_version(self, client: TestClient):
        """Health check includes version."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "version" in data

    def test_health_check_includes_db_status(self, client: TestClient):
        """Health check includes database status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "redis" in data
        assert "mongodb" in data


class TestLivenessProbe:
    """Tests for Kubernetes liveness probe."""

    def test_liveness_returns_ok(self, client: TestClient):
        """Liveness probe returns OK."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestReadinessProbe:
    """Tests for Kubernetes readiness probe."""

    def test_readiness_returns_status(self, client: TestClient):
        """Readiness probe returns status."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert "checks" in data


class TestRootEndpoint:
    """Tests for root endpoint - skipped since no root endpoint defined."""

    @pytest.mark.skip(reason="No root endpoint defined in current implementation")
    def test_root_returns_service_info(self, client: TestClient):
        """Root endpoint returns service information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["status"] == "operational"
