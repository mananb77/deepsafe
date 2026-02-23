"""Tests for Google OAuth authentication."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.integrations.google_meet.auth.oauth import (
    GoogleOAuth,
    GoogleTokens,
    GoogleUserInfo,
    GoogleOAuthToken,
)


class TestGoogleTokens:
    """Tests for GoogleTokens dataclass."""

    def test_creation(self):
        """Test creating tokens."""
        tokens = GoogleTokens(access_token="access_123")
        assert tokens.access_token == "access_123"
        assert tokens.token_type == "Bearer"
        assert tokens.expires_in == 3600

    def test_with_id_token(self):
        """Test creating tokens with ID token."""
        tokens = GoogleTokens(
            access_token="access_123",
            id_token="id_token_jwt",
        )
        assert tokens.id_token == "id_token_jwt"

    def test_expires_at(self):
        """Test expires_at calculation."""
        tokens = GoogleTokens(
            access_token="access_123",
            expires_in=3600,
        )
        assert tokens.expires_at > datetime.utcnow()
        assert tokens.expires_at <= datetime.utcnow() + timedelta(seconds=3601)

    def test_is_expired_false(self):
        """Test is_expired when token is valid."""
        tokens = GoogleTokens(
            access_token="access_123",
            expires_in=3600,
        )
        assert tokens.is_expired is False

    def test_is_expired_true(self):
        """Test is_expired when token is expired."""
        tokens = GoogleTokens(
            access_token="access_123",
            expires_in=0,
            created_at=datetime.utcnow() - timedelta(hours=1),
        )
        assert tokens.is_expired is True

    def test_scopes(self):
        """Test scopes parsing."""
        tokens = GoogleTokens(
            access_token="access_123",
            scope="openid email profile",
        )
        assert tokens.scopes == ["openid", "email", "profile"]

    def test_to_dict(self):
        """Test serialization to dict."""
        tokens = GoogleTokens(
            access_token="access_123",
            refresh_token="refresh_456",
            id_token="id_token_jwt",
            scope="openid email",
        )
        data = tokens.to_dict()
        assert data["access_token"] == "access_123"
        assert data["refresh_token"] == "refresh_456"
        assert data["id_token"] == "id_token_jwt"
        assert data["scope"] == "openid email"

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "access_token": "access_123",
            "refresh_token": "refresh_456",
            "scope": "openid email",
            "expires_in": 3600,
            "created_at": datetime.utcnow().isoformat(),
        }
        tokens = GoogleTokens.from_dict(data)
        assert tokens.access_token == "access_123"
        assert tokens.refresh_token == "refresh_456"


class TestGoogleUserInfo:
    """Tests for GoogleUserInfo dataclass."""

    def test_creation(self):
        """Test creating user info."""
        user = GoogleUserInfo(
            id="user_123",
            email="test@example.com",
        )
        assert user.id == "user_123"
        assert user.email == "test@example.com"

    def test_full_name_uses_name(self):
        """Test full_name uses name field."""
        user = GoogleUserInfo(
            id="user_123",
            email="test@example.com",
            name="Full Name",
            given_name="First",
            family_name="Last",
        )
        assert user.full_name == "Full Name"

    def test_full_name_from_parts(self):
        """Test full_name from given and family name."""
        user = GoogleUserInfo(
            id="user_123",
            email="test@example.com",
            given_name="John",
            family_name="Doe",
        )
        assert user.full_name == "John Doe"

    def test_is_workspace_user_true(self):
        """Test is_workspace_user for Workspace user."""
        user = GoogleUserInfo(
            id="user_123",
            email="test@company.com",
            hd="company.com",
        )
        assert user.is_workspace_user is True

    def test_is_workspace_user_false(self):
        """Test is_workspace_user for consumer user."""
        user = GoogleUserInfo(
            id="user_123",
            email="test@gmail.com",
        )
        assert user.is_workspace_user is False

    def test_from_api_response(self):
        """Test creating from API response."""
        data = {
            "sub": "user_123",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/pic.jpg",
            "locale": "en",
            "hd": "example.com",
        }
        user = GoogleUserInfo.from_api_response(data)
        assert user.id == "user_123"
        assert user.email == "test@example.com"
        assert user.email_verified is True
        assert user.name == "Test User"
        assert user.hd == "example.com"


class TestGoogleOAuth:
    """Tests for GoogleOAuth client."""

    @pytest.fixture
    def oauth(self):
        """Create OAuth client for testing."""
        with patch("src.integrations.google_meet.auth.oauth.get_settings") as mock:
            mock.return_value.google.client_id = "test_client_id"
            mock.return_value.google.client_secret = "test_client_secret"
            return GoogleOAuth()

    def test_initialization(self, oauth):
        """Test OAuth client initialization."""
        assert oauth.client_id == "test_client_id"
        assert oauth.client_secret == "test_client_secret"

    def test_initialization_with_params(self):
        """Test initialization with explicit params."""
        oauth = GoogleOAuth(
            client_id="explicit_id",
            client_secret="explicit_secret",
        )
        assert oauth.client_id == "explicit_id"
        assert oauth.client_secret == "explicit_secret"

    def test_generate_state(self):
        """Test state generation."""
        state1 = GoogleOAuth.generate_state()
        state2 = GoogleOAuth.generate_state()
        assert state1 != state2
        assert len(state1) > 20

    def test_generate_code_verifier(self):
        """Test PKCE code verifier generation."""
        verifier = GoogleOAuth.generate_code_verifier()
        assert len(verifier) > 40

    def test_generate_code_challenge(self):
        """Test PKCE code challenge generation."""
        verifier = "test_verifier_12345678901234567890"
        challenge = GoogleOAuth.generate_code_challenge(verifier)
        assert challenge != verifier
        assert len(challenge) > 20

    def test_get_authorization_url(self, oauth):
        """Test authorization URL generation."""
        url = oauth.get_authorization_url(
            redirect_uri="https://example.com/callback",
            state="test_state",
        )
        assert "https://accounts.google.com/o/oauth2/v2/auth" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=" in url
        assert "state=test_state" in url
        assert "response_type=code" in url

    def test_get_authorization_url_with_scopes(self, oauth):
        """Test authorization URL with custom scopes."""
        url = oauth.get_authorization_url(
            redirect_uri="https://example.com/callback",
            scopes=["openid", "email"],
        )
        assert "scope=" in url

    def test_get_authorization_url_with_pkce(self, oauth):
        """Test authorization URL with PKCE."""
        url = oauth.get_authorization_url(
            redirect_uri="https://example.com/callback",
            code_challenge="test_challenge",
        )
        assert "code_challenge=test_challenge" in url
        assert "code_challenge_method=S256" in url

    def test_get_authorization_url_with_login_hint(self, oauth):
        """Test authorization URL with login hint."""
        url = oauth.get_authorization_url(
            redirect_uri="https://example.com/callback",
            login_hint="user@example.com",
        )
        assert "login_hint=user%40example.com" in url or "login_hint=user@example.com" in url

    def test_get_authorization_url_with_hd(self, oauth):
        """Test authorization URL with hosted domain."""
        url = oauth.get_authorization_url(
            redirect_uri="https://example.com/callback",
            hd="company.com",
        )
        assert "hd=company.com" in url

    def test_is_configured_true(self, oauth):
        """Test is_configured when credentials are set."""
        assert oauth.is_configured() is True

    def test_is_configured_false(self):
        """Test is_configured when credentials are missing."""
        with patch("src.integrations.google_meet.auth.oauth.get_settings") as mock:
            mock.return_value.google.client_id = ""
            mock.return_value.google.client_secret = ""
            oauth = GoogleOAuth(client_id="", client_secret="")
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
                "scope": "openid email",
                "id_token": "id_jwt",
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
            assert tokens.id_token == "id_jwt"

    @pytest.mark.asyncio
    async def test_refresh_tokens(self, oauth):
        """Test token refresh."""
        with patch.object(oauth, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "access_token": "refreshed_access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client

            tokens = await oauth.refresh_tokens("old_refresh_token")

            assert tokens.access_token == "refreshed_access_token"
            # Original refresh token should be preserved
            assert tokens.refresh_token == "old_refresh_token"

    @pytest.mark.asyncio
    async def test_get_user_info(self, oauth):
        """Test getting user info."""
        with patch.object(oauth, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "sub": "user_123",
                "email": "test@example.com",
                "name": "Test User",
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
            mock_get_user.return_value = GoogleUserInfo(
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

    def test_default_scopes(self):
        """Test default scopes include required permissions."""
        assert GoogleOAuth.OPENID in GoogleOAuth.DEFAULT_SCOPES
        assert GoogleOAuth.EMAIL in GoogleOAuth.DEFAULT_SCOPES
        assert GoogleOAuth.PROFILE in GoogleOAuth.DEFAULT_SCOPES
        assert GoogleOAuth.CALENDAR_READONLY in GoogleOAuth.DEFAULT_SCOPES


class TestGoogleOAuthToken:
    """Tests for GoogleOAuthToken manager."""

    @pytest.fixture
    def token_manager(self):
        """Create token manager for testing."""
        with patch("src.integrations.google_meet.auth.oauth.get_settings") as mock:
            mock.return_value.google.client_id = "test_id"
            mock.return_value.google.client_secret = "test_secret"

            oauth = GoogleOAuth()
            tokens = GoogleTokens(
                access_token="access_123",
                refresh_token="refresh_456",
                expires_in=3600,
            )
            return GoogleOAuthToken(oauth, tokens)

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
        token_manager._tokens = GoogleTokens(
            access_token="old_access",
            refresh_token="refresh_456",
            expires_in=3600,
            created_at=datetime.utcnow() - timedelta(hours=2),
        )

        with patch.object(
            token_manager._oauth, "refresh_tokens"
        ) as mock_refresh:
            mock_refresh.return_value = GoogleTokens(
                access_token="refreshed_access",
                refresh_token="new_refresh",
            )

            token = await token_manager.get_access_token()
            assert token == "refreshed_access"
