"""
Zoom OAuth 2.0 Authentication

Handles OAuth 2.0 flow for Zoom API access:
- Authorization URL generation
- Token exchange
- Token refresh
- User info retrieval
- Server-to-server OAuth for bots

Zoom OAuth Documentation:
https://developers.zoom.us/docs/integrations/oauth/
"""

import base64
import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx

from src.shared.config import get_settings


@dataclass
class ZoomTokens:
    """
    Zoom OAuth tokens.

    Stores access and refresh tokens with expiration tracking.
    """
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600  # seconds
    refresh_token: Optional[str] = None
    scope: str = ""

    # Computed fields
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def expires_at(self) -> datetime:
        """Get token expiration time."""
        return self.created_at + timedelta(seconds=self.expires_in)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired (with 5 minute buffer)."""
        return datetime.utcnow() >= (self.expires_at - timedelta(minutes=5))

    @property
    def scopes(self) -> List[str]:
        """Get list of granted scopes."""
        return self.scope.split() if self.scope else []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoomTokens":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()

        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in", 3600),
            refresh_token=data.get("refresh_token"),
            scope=data.get("scope", ""),
            created_at=created_at,
        )


@dataclass
class ZoomUserInfo:
    """
    Zoom user information.

    Retrieved from /users/me endpoint.
    """
    id: str
    email: str
    first_name: str = ""
    last_name: str = ""
    display_name: str = ""
    type: int = 1  # 1=Basic, 2=Licensed, 3=On-prem
    role_name: str = ""
    pmi: int = 0  # Personal Meeting ID
    timezone: str = ""
    verified: int = 0
    pic_url: str = ""
    account_id: str = ""
    status: str = "active"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.display_name:
            return self.display_name
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_licensed(self) -> bool:
        """Check if user has a Zoom license."""
        return self.type >= 2

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ZoomUserInfo":
        """Create from Zoom API response."""
        return cls(
            id=data.get("id", ""),
            email=data.get("email", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            display_name=data.get("display_name", ""),
            type=data.get("type", 1),
            role_name=data.get("role_name", ""),
            pmi=data.get("pmi", 0),
            timezone=data.get("timezone", ""),
            verified=data.get("verified", 0),
            pic_url=data.get("pic_url", ""),
            account_id=data.get("account_id", ""),
            status=data.get("status", "active"),
        )


class ZoomOAuth:
    """
    Zoom OAuth 2.0 client.

    Handles both user-level OAuth (authorization code flow)
    and server-to-server OAuth (client credentials flow).

    Usage:
        # User OAuth
        oauth = ZoomOAuth()
        auth_url = oauth.get_authorization_url(redirect_uri, state)
        tokens = await oauth.exchange_code(code, redirect_uri)

        # Server-to-Server OAuth
        oauth = ZoomOAuth()
        tokens = await oauth.get_server_to_server_token()
    """

    # Zoom OAuth endpoints
    AUTHORIZATION_URL = "https://zoom.us/oauth/authorize"
    TOKEN_URL = "https://zoom.us/oauth/token"
    REVOKE_URL = "https://zoom.us/oauth/revoke"
    USER_INFO_URL = "https://api.zoom.us/v2/users/me"

    # Default scopes for DeepSafe
    DEFAULT_SCOPES = [
        "meeting:read",
        "meeting:write",
        "user:read",
        "recording:read",
        "webinar:read",
    ]

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        account_id: Optional[str] = None,
    ):
        """
        Initialize Zoom OAuth client.

        Args:
            client_id: Zoom OAuth client ID (from settings if not provided).
            client_secret: Zoom OAuth client secret.
            account_id: Zoom account ID for server-to-server OAuth.
        """
        settings = get_settings()
        self.client_id = client_id or settings.zoom.client_id
        self.client_secret = client_secret or settings.zoom.client_secret
        self.account_id = account_id

        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    def _get_basic_auth_header(self) -> str:
        """Get Basic auth header for token requests."""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    @staticmethod
    def generate_state() -> str:
        """Generate secure random state for CSRF protection."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_code_verifier() -> str:
        """Generate PKCE code verifier."""
        return secrets.token_urlsafe(64)

    @staticmethod
    def generate_code_challenge(verifier: str) -> str:
        """Generate PKCE code challenge from verifier."""
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        code_challenge: Optional[str] = None,
    ) -> str:
        """
        Generate OAuth authorization URL.

        Args:
            redirect_uri: URL to redirect after authorization.
            state: CSRF protection state (generated if not provided).
            scopes: Requested scopes (defaults to DEFAULT_SCOPES).
            code_challenge: PKCE code challenge (optional).

        Returns:
            Authorization URL to redirect user to.
        """
        if not self.client_id:
            raise ValueError("Zoom client_id not configured")

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state or self.generate_state(),
        }

        # Add scopes if specified
        if scopes:
            params["scope"] = " ".join(scopes)

        # Add PKCE code challenge if provided
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> ZoomTokens:
        """
        Exchange authorization code for tokens.

        Args:
            code: Authorization code from redirect.
            redirect_uri: Same redirect URI used in authorization.
            code_verifier: PKCE code verifier (if code challenge was used).

        Returns:
            ZoomTokens with access and refresh tokens.

        Raises:
            httpx.HTTPStatusError: If token exchange fails.
        """
        client = await self._get_client()

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }

        if code_verifier:
            data["code_verifier"] = code_verifier

        response = await client.post(
            self.TOKEN_URL,
            data=data,
            headers={
                "Authorization": self._get_basic_auth_header(),
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        response.raise_for_status()

        token_data = response.json()
        return ZoomTokens(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope", ""),
        )

    async def refresh_tokens(self, refresh_token: str) -> ZoomTokens:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token.

        Returns:
            New ZoomTokens with refreshed access token.

        Raises:
            httpx.HTTPStatusError: If refresh fails.
        """
        client = await self._get_client()

        response = await client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={
                "Authorization": self._get_basic_auth_header(),
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        response.raise_for_status()

        token_data = response.json()
        return ZoomTokens(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            refresh_token=token_data.get("refresh_token", refresh_token),
            scope=token_data.get("scope", ""),
        )

    async def get_server_to_server_token(
        self,
        account_id: Optional[str] = None,
    ) -> ZoomTokens:
        """
        Get server-to-server OAuth token.

        For server-to-server apps that don't require user authorization.

        Args:
            account_id: Zoom account ID (from settings if not provided).

        Returns:
            ZoomTokens with access token (no refresh token).

        Raises:
            ValueError: If account_id not configured.
            httpx.HTTPStatusError: If token request fails.
        """
        account_id = account_id or self.account_id
        if not account_id:
            raise ValueError("Zoom account_id required for server-to-server OAuth")

        client = await self._get_client()

        response = await client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "account_credentials",
                "account_id": account_id,
            },
            headers={
                "Authorization": self._get_basic_auth_header(),
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        response.raise_for_status()

        token_data = response.json()
        return ZoomTokens(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            scope=token_data.get("scope", ""),
        )

    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token.

        Args:
            token: Token to revoke.

        Returns:
            True if revoked successfully.
        """
        client = await self._get_client()

        try:
            response = await client.post(
                self.REVOKE_URL,
                data={"token": token},
                headers={
                    "Authorization": self._get_basic_auth_header(),
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def get_user_info(self, access_token: str) -> ZoomUserInfo:
        """
        Get information about the authenticated user.

        Args:
            access_token: Valid access token.

        Returns:
            ZoomUserInfo with user details.

        Raises:
            httpx.HTTPStatusError: If request fails.
        """
        client = await self._get_client()

        response = await client.get(
            self.USER_INFO_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )
        response.raise_for_status()

        return ZoomUserInfo.from_api_response(response.json())

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate an access token by making a test API call.

        Args:
            access_token: Token to validate.

        Returns:
            True if token is valid, False otherwise.
        """
        try:
            await self.get_user_info(access_token)
            return True
        except httpx.HTTPError:
            return False

    def is_configured(self) -> bool:
        """Check if OAuth credentials are configured."""
        return bool(self.client_id and self.client_secret)


class ZoomOAuthToken:
    """
    Token manager for automatic refresh.

    Wraps ZoomTokens and ZoomOAuth for automatic token refresh.
    """

    def __init__(
        self,
        oauth: ZoomOAuth,
        tokens: ZoomTokens,
    ):
        self._oauth = oauth
        self._tokens = tokens

    @property
    def tokens(self) -> ZoomTokens:
        return self._tokens

    async def get_access_token(self) -> str:
        """
        Get valid access token, refreshing if needed.

        Returns:
            Valid access token.
        """
        if self._tokens.is_expired and self._tokens.refresh_token:
            self._tokens = await self._oauth.refresh_tokens(
                self._tokens.refresh_token
            )
        return self._tokens.access_token

    async def refresh_if_needed(self) -> bool:
        """
        Refresh token if expired.

        Returns:
            True if token was refreshed, False if still valid.
        """
        if self._tokens.is_expired and self._tokens.refresh_token:
            self._tokens = await self._oauth.refresh_tokens(
                self._tokens.refresh_token
            )
            return True
        return False

    def is_valid(self) -> bool:
        """Check if tokens are valid."""
        return not self._tokens.is_expired or bool(self._tokens.refresh_token)
