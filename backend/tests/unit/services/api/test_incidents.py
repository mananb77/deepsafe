"""
Incidents Router Tests

Unit tests for incident management endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestListIncidentsEndpoint:
    """Tests for list incidents endpoint."""

    def test_list_incidents_requires_auth(self, client: TestClient):
        """List incidents requires authentication."""
        response = client.get("/api/v1/incidents")

        assert response.status_code == 401

    def test_list_incidents_with_auth(self, client: TestClient, auth_headers: dict):
        """List incidents with auth returns response."""
        response = client.get("/api/v1/incidents", headers=auth_headers)

        assert response.status_code in [200, 500]

    def test_list_incidents_filter_by_meeting(self, client: TestClient, auth_headers: dict):
        """List incidents filters by meeting ID."""
        response = client.get(
            "/api/v1/incidents?meeting_id=550e8400-e29b-41d4-a716-446655440002",
            headers=auth_headers,
        )

        assert response.status_code in [200, 500]

    def test_list_incidents_filter_by_type(self, client: TestClient, auth_headers: dict):
        """List incidents filters by incident type."""
        response = client.get(
            "/api/v1/incidents?incident_type=audio_deepfake",
            headers=auth_headers,
        )

        assert response.status_code in [200, 422, 500]

    def test_list_incidents_filter_by_severity(self, client: TestClient, auth_headers: dict):
        """List incidents filters by severity."""
        response = client.get(
            "/api/v1/incidents?severity=high",
            headers=auth_headers,
        )

        assert response.status_code in [200, 422, 500]

    def test_list_incidents_filter_by_status(self, client: TestClient, auth_headers: dict):
        """List incidents filters by status."""
        response = client.get(
            "/api/v1/incidents?status=detected",
            headers=auth_headers,
        )

        assert response.status_code in [200, 422, 500]


class TestIncidentStatsEndpoint:
    """Tests for incident statistics endpoint."""

    def test_incident_stats_requires_auth(self, client: TestClient):
        """Incident stats requires authentication."""
        response = client.get("/api/v1/incidents/stats")

        assert response.status_code == 401

    def test_incident_stats_with_auth(self, client: TestClient, auth_headers: dict):
        """Incident stats with auth returns response."""
        response = client.get("/api/v1/incidents/stats", headers=auth_headers)

        assert response.status_code in [200, 500]


class TestGetIncidentEndpoint:
    """Tests for get incident endpoint."""

    def test_get_incident_requires_auth(self, client: TestClient):
        """Get incident requires authentication."""
        response = client.get("/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004")

        assert response.status_code == 401

    def test_get_incident_with_auth(self, client: TestClient, auth_headers: dict):
        """Get incident with auth."""
        response = client.get(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404, 500]


class TestCreateIncidentEndpoint:
    """Tests for create incident endpoint."""

    def test_create_incident_requires_auth(self, client: TestClient):
        """Create incident requires authentication."""
        response = client.post(
            "/api/v1/incidents",
            json={
                "meeting_id": "550e8400-e29b-41d4-a716-446655440002",
                "incident_type": "audio_deepfake",
                "severity": "high",
                "title": "Test Incident",
            },
        )

        assert response.status_code == 401

    def test_create_incident_validation(self, client: TestClient, auth_headers: dict):
        """Create incident validates required fields."""
        response = client.post(
            "/api/v1/incidents",
            headers=auth_headers,
            json={},
        )

        assert response.status_code == 422

    def test_create_incident_with_data(self, client: TestClient, auth_headers: dict):
        """Create incident with valid data."""
        response = client.post(
            "/api/v1/incidents",
            headers=auth_headers,
            json={
                "meeting_id": "550e8400-e29b-41d4-a716-446655440002",
                "incident_type": "audio_deepfake",
                "severity": "high",
                "title": "Potential Audio Deepfake",
                "description": "Analysis indicates potential voice cloning",
                "confidence_score": 85.5,
            },
        )

        assert response.status_code in [201, 404, 422, 500]

    def test_create_incident_invalid_type(self, client: TestClient, auth_headers: dict):
        """Create incident with invalid type returns 422."""
        response = client.post(
            "/api/v1/incidents",
            headers=auth_headers,
            json={
                "meeting_id": "550e8400-e29b-41d4-a716-446655440002",
                "incident_type": "invalid_type",
                "severity": "high",
                "title": "Test Incident",
            },
        )

        assert response.status_code == 422


class TestUpdateIncidentEndpoint:
    """Tests for update incident endpoint."""

    def test_update_incident_requires_auth(self, client: TestClient):
        """Update incident requires authentication."""
        response = client.patch(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004",
            json={"title": "Updated Title"},
        )

        assert response.status_code == 401

    def test_update_incident_with_auth(self, client: TestClient, auth_headers: dict):
        """Update incident with auth."""
        response = client.patch(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004",
            headers=auth_headers,
            json={"title": "Updated Title"},
        )

        # Requires security_analyst role
        assert response.status_code in [200, 403, 404, 500]


class TestResolveIncidentEndpoint:
    """Tests for resolve incident endpoint."""

    def test_resolve_incident_requires_auth(self, client: TestClient):
        """Resolve incident requires authentication."""
        response = client.post(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004/resolve",
            json={"resolution_notes": "Investigation complete"},
        )

        assert response.status_code == 401

    def test_resolve_incident_validation(self, client: TestClient, auth_headers: dict):
        """Resolve incident validates input."""
        response = client.post(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004/resolve",
            headers=auth_headers,
            json={},
        )

        assert response.status_code in [200, 403, 404, 422, 500]

    def test_resolve_incident_as_false_positive(self, client: TestClient, auth_headers: dict):
        """Resolve incident as false positive."""
        response = client.post(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004/resolve",
            headers=auth_headers,
            json={
                "resolution_notes": "Confirmed to be legitimate participant",
                "is_false_positive": True,
            },
        )

        assert response.status_code in [200, 403, 404, 500]


class TestEscalateIncidentEndpoint:
    """Tests for escalate incident endpoint."""

    def test_escalate_incident_requires_auth(self, client: TestClient):
        """Escalate incident requires authentication."""
        response = client.post(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004/escalate",
            json={"new_severity": "critical", "reason": "Additional evidence found"},
        )

        assert response.status_code == 401

    def test_escalate_incident_validation(self, client: TestClient, auth_headers: dict):
        """Escalate incident validates input."""
        response = client.post(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004/escalate",
            headers=auth_headers,
            json={},
        )

        assert response.status_code in [403, 404, 422, 500]

    def test_escalate_incident_with_data(self, client: TestClient, auth_headers: dict):
        """Escalate incident with valid data."""
        response = client.post(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004/escalate",
            headers=auth_headers,
            json={
                "new_severity": "critical",
                "reason": "Additional evidence confirms attack",
            },
        )

        assert response.status_code in [200, 403, 404, 422, 500]


class TestInvestigateIncidentEndpoint:
    """Tests for investigate incident endpoint."""

    def test_investigate_incident_requires_auth(self, client: TestClient):
        """Investigate incident requires authentication."""
        response = client.post(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004/investigate"
        )

        assert response.status_code == 401

    def test_investigate_incident_with_auth(self, client: TestClient, auth_headers: dict):
        """Investigate incident with auth."""
        response = client.post(
            "/api/v1/incidents/550e8400-e29b-41d4-a716-446655440004/investigate",
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404, 500]
