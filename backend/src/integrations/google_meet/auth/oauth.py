"""
Google OAuth 2.0 Authentication

Handles OAuth 2.0 flow for Google APIs:
- Authorization URL generation with PKCE
- Token exchange
- Token refresh
- User info retrieval
- Service account authentication

Required for:
- Google Meet API
- Google Calendar API
- Google People API

Google OAuth Documentation:
https://developers.google.com/identity/protocols/oauth2
"""

import base64
import hashlib
import json
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx

from src.shared.config import get_settings


logger = logging.getLogger(__name__)


@dataclass
class GoogleTokens:
    """
    Google OAuth tokens.

    Stores access and refresh tokens with expiration tracking.
    """
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600  # seconds
    refresh_token: Optional[str] = None
    scope: str = ""
    id_token: Optional[str] = None  # OpenID Connect

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
            "id_token": self.id_token,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoogleTokens":
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
            id_token=data.get("id_token"),
            created_at=created_at,
        )


@dataclass
class GoogleUserInfo:
    """
    Google user information.

    Retrieved from OpenID Connect userinfo endpoint.
    """
    id: str  # Google user ID (sub claim)
    email: str
    email_verified: bool = False
    name: str = ""
    given_name: str = ""
    family_name: str = ""
    picture: str = ""
    locale: str = ""
    hd: str = ""  # Hosted domain (for Workspace accounts)

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.name:
            return self.name
        return f"{self.given_name} {self.family_name}".strip()

    @property
    def is_workspace_user(self) -> bool:
        """Check if user is a Google Workspace user."""
        return bool(self.hd)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "GoogleUserInfo":
        """Create from Google API response."""
        return cls(
            id=data.get("sub", data.get("id", "")),
            email=data.get("email", ""),
            email_verified=data.get("email_verified", False),
            name=data.get("name", ""),
            given_name=data.get("given_name", ""),
            family_name=data.get("family_name", ""),
            picture=data.get("picture", ""),
            locale=data.get("locale", ""),
            hd=data.get("hd", ""),
        )


class GoogleOAuth:
    """
    Google OAuth 2.0 client.

    Handles OAuth flow for user authorization and service account authentication.

    Usage:
        # User OAuth
        oauth = GoogleOAuth()
        auth_url = oauth.get_authorization_url(redirect_uri, state)
        tokens = await oauth.exchange_code(code, redirect_uri, code_verifier)

        # Service Account
        oauth = GoogleOAuth()
        tokens = await oauth.get_service_account_token(
            service_account_file="path/to/credentials.json"
        )
    """

    # Google OAuth endpoints
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    REVOKE_URL = "https://oauth2.googleapis.com/revoke"
    USER_INFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
    CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

    # Scopes for DeepSafe
    # Calendar scopes - for meeting sync
    CALENDAR_READONLY = "https://www.googleapis.com/auth/calendar.readonly"
    CALENDAR_EVENTS = "https://www.googleapis.com/auth/calendar.events"

    # Meet scopes - for Meet API (when available)
    MEET_READONLY = "https://www.googleapis.com/auth/meetings.space.readonly"

    # User info scopes
    OPENID = "openid"
    EMAIL = "email"
    PROFILE = "profile"

    # Default scopes for DeepSafe
    DEFAULT_SCOPES = [
        OPENID,
        EMAIL,
        PROFILE,
        CALENDAR_READONLY,
        CALENDAR_EVENTS,
    ]

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        service_account_file: Optional[str] = None,
    ):
        """
        Initialize Google OAuth client.

        Args:
            client_id: Google OAuth client ID (from settings if not provided).
            client_secret: Google OAuth client secret.
            service_account_file: Path to service account JSON file.
        """
        settings = get_settings()
        self.client_id = client_id or settings.google.client_id
        self.client_secret = client_secret or settings.google.client_secret
        self.service_account_file = service_account_file

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
        """Generate PKCE code challenge from verifier (S256 method)."""
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        code_challenge: Optional[str] = None,
        login_hint: Optional[str] = None,
        hd: Optional[str] = None,
        prompt: Optional[str] = None,
        access_type: str = "offline",
    ) -> str:
        """
        Generate OAuth authorization URL.

        Args:
            redirect_uri: URL to redirect after authorization.
            state: CSRF protection state (generated if not provided).
            scopes: Requested scopes (defaults to DEFAULT_SCOPES).
            code_challenge: PKCE code challenge (recommended).
            login_hint: Pre-fill email for user.
            hd: Restrict to Google Workspace domain.
            prompt: Consent prompt behavior ("none", "consent", "select_account").
            access_type: "offline" for refresh token, "online" for access only.

        Returns:
            Authorization URL to redirect user to.
        """
        if not self.client_id:
            raise ValueError("Google client_id not configured")

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state or self.generate_state(),
            "scope": " ".join(scopes or self.DEFAULT_SCOPES),
            "access_type": access_type,
        }

        # Add PKCE code challenge (recommended by Google)
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        # Add optional parameters
        if login_hint:
            params["login_hint"] = login_hint
        if hd:
            params["hd"] = hd
        if prompt:
            params["prompt"] = prompt
        elif access_type == "offline":
            # Request consent to get refresh token
            params["prompt"] = "consent"

        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> GoogleTokens:
        """
        Exchange authorization code for tokens.

        Args:
            code: Authorization code from redirect.
            redirect_uri: Same redirect URI used in authorization.
            code_verifier: PKCE code verifier (if code challenge was used).

        Returns:
            GoogleTokens with access and refresh tokens.

        Raises:
            httpx.HTTPStatusError: If token exchange fails.
        """
        client = await self._get_client()

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        if code_verifier:
            data["code_verifier"] = code_verifier

        response = await client.post(
            self.TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()

        token_data = response.json()
        return GoogleTokens(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope", ""),
            id_token=token_data.get("id_token"),
        )

    async def refresh_tokens(self, refresh_token: str) -> GoogleTokens:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token.

        Returns:
            New GoogleTokens with refreshed access token.

        Raises:
            httpx.HTTPStatusError: If refresh fails.
        """
        client = await self._get_client()

        response = await client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()

        token_data = response.json()
        return GoogleTokens(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            # Refresh token might not be returned, keep original
            refresh_token=token_data.get("refresh_token", refresh_token),
            scope=token_data.get("scope", ""),
            id_token=token_data.get("id_token"),
        )

    async def get_service_account_token(
        self,
        service_account_file: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        subject: Optional[str] = None,
    ) -> GoogleTokens:
        """
        Get access token using service account credentials.

        For server-to-server authentication without user interaction.

        Args:
            service_account_file: Path to service account JSON file.
            scopes: Requested scopes.
            subject: Email of user to impersonate (for domain-wide delegation).

        Returns:
            GoogleTokens with access token.

        Raises:
            ValueError: If service account file not configured.
            httpx.HTTPStatusError: If token request fails.
        """
        sa_file = service_account_file or self.service_account_file
        if not sa_file:
            raise ValueError("Service account file not configured")

        sa_path = Path(sa_file)
        if not sa_path.exists():
            raise ValueError(f"Service account file not found: {sa_file}")

        # Load service account credentials
        with open(sa_path) as f:
            sa_creds = json.load(f)

        # Create JWT for authentication
        jwt_token = self._create_service_account_jwt(
            sa_creds,
            scopes=scopes or self.DEFAULT_SCOPES,
            subject=subject,
        )

        client = await self._get_client()

        response = await client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": jwt_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()

        token_data = response.json()
        return GoogleTokens(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 3600),
            scope=" ".join(scopes or self.DEFAULT_SCOPES),
        )

    def _create_service_account_jwt(
        self,
        sa_creds: Dict[str, Any],
        scopes: List[str],
        subject: Optional[str] = None,
    ) -> str:
        """
        Create signed JWT for service account authentication.

        Args:
            sa_creds: Service account credentials from JSON file.
            scopes: Requested scopes.
            subject: Email of user to impersonate.

        Returns:
            Signed JWT string.
        """
        import time

        # This is a simplified implementation
        # In production, use google-auth library
        now = int(time.time())
        expiry = now + 3600  # 1 hour

        header = {
            "alg": "RS256",
            "typ": "JWT",
        }

        payload = {
            "iss": sa_creds["client_email"],
            "scope": " ".join(scopes),
            "aud": self.TOKEN_URL,
            "iat": now,
            "exp": expiry,
        }

        if subject:
            payload["sub"] = subject

        # Encode header and payload
        def b64_encode(data: dict) -> str:
            json_bytes = json.dumps(data, separators=(",", ":")).encode()
            return base64.urlsafe_b64encode(json_bytes).rstrip(b"=").decode()

        header_b64 = b64_encode(header)
        payload_b64 = b64_encode(payload)
        message = f"{header_b64}.{payload_b64}"

        # Sign with private key
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        private_key = serialization.load_pem_private_key(
            sa_creds["private_key"].encode(),
            password=None,
        )

        signature = private_key.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

        signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
        return f"{message}.{signature_b64}"

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
                params={"token": token},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def get_user_info(self, access_token: str) -> GoogleUserInfo:
        """
        Get information about the authenticated user.

        Args:
            access_token: Valid access token with openid/email/profile scopes.

        Returns:
            GoogleUserInfo with user details.

        Raises:
            httpx.HTTPStatusError: If request fails.
        """
        client = await self._get_client()

        response = await client.get(
            self.USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()

        return GoogleUserInfo.from_api_response(response.json())

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

    async def validate_id_token(
        self,
        id_token: str,
        audience: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate and decode an ID token.

        Args:
            id_token: JWT ID token from Google.
            audience: Expected audience (client_id).

        Returns:
            Decoded token claims.

        Raises:
            ValueError: If token is invalid.
        """
        # Split token
        parts = id_token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid ID token format")

        # Decode payload (middle part)
        payload_b64 = parts[1]
        # Add padding if needed
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding

        payload_json = base64.urlsafe_b64decode(payload_b64)
        claims = json.loads(payload_json)

        # Validate basic claims
        now = datetime.utcnow().timestamp()

        if claims.get("exp", 0) < now:
            raise ValueError("ID token has expired")

        if claims.get("iss") not in [
            "https://accounts.google.com",
            "accounts.google.com",
        ]:
            raise ValueError("Invalid token issuer")

        expected_audience = audience or self.client_id
        if expected_audience and claims.get("aud") != expected_audience:
            raise ValueError("Invalid token audience")

        return claims


class GoogleOAuthToken:
    """
    Token manager for automatic refresh.

    Wraps GoogleTokens and GoogleOAuth for automatic token refresh.
    """

    def __init__(
        self,
        oauth: GoogleOAuth,
        tokens: GoogleTokens,
    ):
        self._oauth = oauth
        self._tokens = tokens

    @property
    def tokens(self) -> GoogleTokens:
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
