"""Tests for Zoom OAuth authentication."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.integrations.zoom.auth.oauth import (
    ZoomOAuth,
    ZoomTokens,
    ZoomUserInfo,
    ZoomOAuthToken,
)


class TestZoomTokens:
    """Tests for ZoomTokens dataclass."""

    def test_creation(self):
        """Test creating tokens."""
        tokens = ZoomTokens(access_token="access_123")
        assert tokens.access_token == "access_123"
        assert tokens.token_type == "Bearer"
        assert tokens.expires_in == 3600

    def test_expires_at(self):
        """Test expires_at calculation."""
        tokens = ZoomTokens(
            access_token="access_123",
            expires_in=3600,
        )
        assert tokens.expires_at > datetime.utcnow()
        assert tokens.expires_at <= datetime.utcnow() + timedelta(seconds=3601)

    def test_is_expired_false(self):
        """Test is_expired when token is valid."""
        tokens = ZoomTokens(
            access_token="access_123",
            expires_in=3600,  # 1 hour
        )
        assert tokens.is_expired is False

    def test_is_expired_true(self):
        """Test is_expired when token is expired."""
        tokens = ZoomTokens(
            access_token="access_123",
            expires_in=0,  # Already expired
            created_at=datetime.utcnow() - timedelta(hours=1),
        )
        assert tokens.is_expired is True

    def test_is_expired_buffer(self):
        """Test is_expired with 5 minute buffer."""
        tokens = ZoomTokens(
            access_token="access_123",
            expires_in=240,  # 4 minutes - less than 5 minute buffer
        )
        assert tokens.is_expired is True  # Should be expired due to buffer

    def test_scopes(self):
        """Test scopes parsing."""
        tokens = ZoomTokens(
            access_token="access_123",
            scope="meeting:read meeting:write user:read",
        )
        assert tokens.scopes == ["meeting:read", "meeting:write", "user:read"]

    def test_scopes_empty(self):
        """Test scopes when empty."""
        tokens = ZoomTokens(access_token="access_123", scope="")
        assert tokens.scopes == []

    def test_to_dict(self):
        """Test serialization to dict."""
        tokens = ZoomTokens(
            access_token="access_123",
            refresh_token="refresh_456",
            scope="meeting:read",
        )
        data = tokens.to_dict()
        assert data["access_token"] == "access_123"
        assert data["refresh_token"] == "refresh_456"
        assert data["scope"] == "meeting:read"
        assert "created_at" in data

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "access_token": "access_123",
            "refresh_token": "refresh_456",
            "scope": "meeting:read",
            "expires_in": 3600,
            "created_at": datetime.utcnow().isoformat(),
        }
        tokens = ZoomTokens.from_dict(data)
        assert tokens.access_token == "access_123"
        assert tokens.refresh_token == "refresh_456"


class TestZoomUserInfo:
    """Tests for ZoomUserInfo dataclass."""

    def test_creation(self):
        """Test creating user info."""
        user = ZoomUserInfo(
            id="user_123",
            email="test@example.com",
        )
        assert user.id == "user_123"
        assert user.email == "test@example.com"

    def test_full_name_display_name(self):
        """Test full_name uses display_name."""
        user = ZoomUserInfo(
            id="user_123",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            display_name="Johnny D",
        )
        assert user.full_name == "Johnny D"

    def test_full_name_first_last(self):
        """Test full_name from first and last name."""
        user = ZoomUserInfo(
            id="user_123",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        assert user.full_name == "John Doe"

    def test_is_licensed_basic(self):
        """Test is_licensed for basic user."""
        user = ZoomUserInfo(
            id="user_123",
            email="test@example.com",
            type=1,  # Basic
        )
        assert user.is_licensed is False

    def test_is_licensed_licensed(self):
        """Test is_licensed for licensed user."""
        user = ZoomUserInfo(
            id="user_123",
            email="test@example.com",
            type=2,  # Licensed
        )
        assert user.is_licensed is True

    def test_from_api_response(self):
        """Test creating from API response."""
        data = {
            "id": "user_123",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "display_name": "Johnny",
            "type": 2,
            "role_name": "Member",
            "pmi": 1234567890,
            "timezone": "America/New_York",
            "verified": 1,
            "pic_url": "https://example.com/pic.jpg",
            "account_id": "account_123",
            "status": "active",
        }
        user = ZoomUserInfo.from_api_response(data)
        assert user.id == "user_123"
        assert user.email == "test@example.com"
        assert user.type == 2
        assert user.pmi == 1234567890


class TestZoomOAuth:
    """Tests for ZoomOAuth client."""

    @pytest.fixture
    def oauth(self):
        """Create OAuth client for testing."""
        with patch("src.integrations.zoom.auth.oauth.get_settings") as mock_settings:
            mock_settings.return_value.zoom.client_id = "test_client_id"
            mock_settings.return_value.zoom.client_secret = "test_client_secret"
            return ZoomOAuth()

    def test_initialization(self, oauth):
        """Test OAuth client initialization."""
        assert oauth.client_id == "test_client_id"
        assert oauth.client_secret == "test_client_secret"

    def test_initialization_with_params(self):
        """Test initialization with explicit params."""
        oauth = ZoomOAuth(
            client_id="explicit_id",
            client_secret="explicit_secret",
        )
        assert oauth.client_id == "explicit_id"
        assert oauth.client_secret == "explicit_secret"

    def test_generate_state(self):
        """Test state generation."""
        state1 = ZoomOAuth.generate_state()
        state2 = ZoomOAuth.generate_state()
        assert state1 != state2
        assert len(state1) > 20  # Should be reasonably long

    def test_generate_code_verifier(self):
        """Test PKCE code verifier generation."""
        verifier = ZoomOAuth.generate_code_verifier()
        assert len(verifier) > 40

    def test_generate_code_challenge(self):
        """Test PKCE code challenge generation."""
        verifier = "test_verifier_12345678901234567890"
        challenge = ZoomOAuth.generate_code_challenge(verifier)
        assert challenge != verifier
        assert len(challenge) > 20

    def test_get_authorization_url(self, oauth):
        """Test authorization URL generation."""
        url = oauth.get_authorization_url(
            redirect_uri="https://example.com/callback",
            state="test_state",
        )
        assert "https://zoom.us/oauth/authorize" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=" in url
        assert "state=test_state" in url
        assert "response_type=code" in url

    def test_get_authorization_url_with_scopes(self, oauth):
        """Test authorization URL with custom scopes."""
        url = oauth.get_authorization_url(
            redirect_uri="https://example.com/callback",
            scopes=["meeting:read", "user:read"],
        )
        assert "scope=meeting%3Aread+user%3Aread" in url or "scope=meeting:read" in url

    def test_get_authorization_url_with_pkce(self, oauth):
        """Test authorization URL with PKCE."""
        url = oauth.get_authorization_url(
            redirect_uri="https://example.com/callback",
            code_challenge="test_challenge",
        )
        assert "code_challenge=test_challenge" in url
        assert "code_challenge_method=S256" in url

    def test_get_basic_auth_header(self, oauth):
        """Test Basic auth header generation."""
        header = oauth._get_basic_auth_header()
        assert header.startswith("Basic ")

    def test_is_configured_true(self, oauth):
        """Test is_configured when credentials are set."""
        assert oauth.is_configured() is True

    def test_is_configured_false(self):
        """Test is_configured when credentials are missing."""
        oauth = ZoomOAuth(client_id="", client_secret="")
        assert oauth.is_configured() is False

    @pytest.mark.asyncio
    async def test_exchange_code(self, oauth):
        """Test token exchange."""
        with patch.object(oauth, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "access_token": "new_access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "new_refresh_token",
                "scope": "meeting:read",
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client

            tokens = await oauth.exchange_code(
                code="auth_code",
                redirect_uri="https://example.com/callback",
            )

            assert tokens.access_token == "new_access_token"
            assert tokens.refresh_token == "new_refresh_token"

    @pytest.mark.asyncio
    async def test_refresh_tokens(self, oauth):
        """Test token refresh."""
        with patch.object(oauth, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "access_token": "refreshed_access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "new_refresh_token",
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client

            tokens = await oauth.refresh_tokens("old_refresh_token")

            assert tokens.access_token == "refreshed_access_token"

    @pytest.mark.asyncio
    async def test_get_server_to_server_token(self, oauth):
        """Test server-to-server token."""
        oauth.account_id = "test_account_id"

        with patch.object(oauth, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "access_token": "s2s_access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client

            tokens = await oauth.get_server_to_server_token()

            assert tokens.access_token == "s2s_access_token"
            assert tokens.refresh_token is None

    @pytest.mark.asyncio
    async def test_get_server_to_server_token_no_account_id(self, oauth):
        """Test server-to-server token without account_id raises error."""
        with pytest.raises(ValueError, match="account_id required"):
            await oauth.get_server_to_server_token()

    @pytest.mark.asyncio
    async def test_get_user_info(self, oauth):
        """Test getting user info."""
        with patch.object(oauth, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": "user_123",
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value = mock_client

            user = await oauth.get_user_info("test_access_token")

            assert user.id == "user_123"
            assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_validate_token_valid(self, oauth):
        """Test validating a valid token."""
        with patch.object(oauth, "get_user_info") as mock_get_user:
            mock_get_user.return_value = ZoomUserInfo(
                id="user_123",
                email="test@example.com",
            )

            is_valid = await oauth.validate_token("valid_token")
            assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_token_invalid(self, oauth):
        """Test validating an invalid token."""
        import httpx

        with patch.object(oauth, "get_user_info") as mock_get_user:
            mock_get_user.side_effect = httpx.HTTPError("Unauthorized")

            is_valid = await oauth.validate_token("invalid_token")
            assert is_valid is False

    @pytest.mark.asyncio
    async def test_revoke_token(self, oauth):
        """Test revoking a token."""
        with patch.object(oauth, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.status_code = 200

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = await oauth.revoke_token("test_token")
            assert result is True


class TestZoomOAuthToken:
    """Tests for ZoomOAuthToken manager."""

    @pytest.fixture
    def token_manager(self):
        """Create token manager for testing."""
        with patch("src.integrations.zoom.auth.oauth.get_settings") as mock_settings:
            mock_settings.return_value.zoom.client_id = "test_id"
            mock_settings.return_value.zoom.client_secret = "test_secret"

            oauth = ZoomOAuth()
            tokens = ZoomTokens(
                access_token="access_123",
                refresh_token="refresh_456",
                expires_in=3600,
            )
            return ZoomOAuthToken(oauth, tokens)

    def test_tokens_property(self, token_manager):
        """Test tokens property."""
        tokens = token_manager.tokens
        assert tokens.access_token == "access_123"

    def test_is_valid_true(self, token_manager):
        """Test is_valid when tokens are valid."""
        assert token_manager.is_valid() is True

    @pytest.mark.asyncio
    async def test_get_access_token_not_expired(self, token_manager):
        """Test getting access token when not expired."""
        token = await token_manager.get_access_token()
        assert token == "access_123"

    @pytest.mark.asyncio
    async def test_get_access_token_expired_refreshes(self, token_manager):
        """Test getting access token refreshes when expired."""
        # Make token expired by creating new expired tokens
        token_manager._tokens = ZoomTokens(
            access_token="old_access",
            refresh_token="refresh_456",
            expires_in=3600,
            created_at=datetime.utcnow() - timedelta(hours=2),
        )

        with patch.object(
            token_manager._oauth, "refresh_tokens"
        ) as mock_refresh:
            mock_refresh.return_value = ZoomTokens(
                access_token="refreshed_access",
                refresh_token="new_refresh",
            )

            token = await token_manager.get_access_token()
            assert token == "refreshed_access"

    @pytest.mark.asyncio
    async def test_refresh_if_needed_not_needed(self, token_manager):
        """Test refresh_if_needed when not needed."""
        result = await token_manager.refresh_if_needed()
        assert result is False

    @pytest.mark.asyncio
    async def test_refresh_if_needed_needed(self, token_manager):
        """Test refresh_if_needed when refresh is needed."""
        # Make token expired by creating new expired tokens
        token_manager._tokens = ZoomTokens(
            access_token="old_access",
            refresh_token="refresh_456",
            expires_in=3600,
            created_at=datetime.utcnow() - timedelta(hours=2),
        )

        with patch.object(
            token_manager._oauth, "refresh_tokens"
        ) as mock_refresh:
            mock_refresh.return_value = ZoomTokens(
                access_token="refreshed_access",
                refresh_token="new_refresh",
            )

            result = await token_manager.refresh_if_needed()
            assert result is True
