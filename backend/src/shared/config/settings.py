"""
DeepSafe Application Settings

Centralized configuration using Pydantic Settings with environment variable support.
All settings can be overridden via environment variables or .env files.
"""

from enum import Enum
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DetectionMode(str, Enum):
    """Detection mode controlling local vs API model usage."""

    LOCAL = "local"
    API = "api"
    HYBRID = "hybrid"


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    url: str = Field(
        default="postgresql+asyncpg://deepsafe:deepsafe@localhost:5432/deepsafe",
        description="PostgreSQL connection URL with asyncpg driver",
    )
    pool_size: int = Field(default=20, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=50)
    pool_timeout: int = Field(default=30, ge=1)
    pool_recycle: int = Field(default=1800, ge=60)
    echo: bool = Field(default=False, description="Log SQL queries")


class RedisSettings(BaseSettings):
    """Redis cache configuration."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    url: str = Field(default="redis://localhost:6379/0")
    max_connections: int = Field(default=50, ge=1, le=200)
    decode_responses: bool = Field(default=True)
    socket_timeout: int = Field(default=5, ge=1)
    socket_connect_timeout: int = Field(default=5, ge=1)


class MongoDBSettings(BaseSettings):
    """MongoDB document store configuration."""

    model_config = SettingsConfigDict(env_prefix="MONGODB_")

    url: str = Field(default="mongodb://localhost:27017/deepsafe")
    database: str = Field(default="deepsafe")
    max_pool_size: int = Field(default=50, ge=1, le=200)
    min_pool_size: int = Field(default=10, ge=1, le=50)


class CelerySettings(BaseSettings):
    """Celery task queue configuration."""

    model_config = SettingsConfigDict(env_prefix="CELERY_")

    broker_url: str = Field(default="amqp://guest:guest@localhost:5672//")
    result_backend: str = Field(default="redis://localhost:6379/1")
    task_serializer: str = Field(default="json")
    result_serializer: str = Field(default="json")
    accept_content: List[str] = Field(default=["json"])
    timezone: str = Field(default="UTC")
    enable_utc: bool = Field(default=True)
    task_track_started: bool = Field(default=True)
    task_time_limit: int = Field(default=300, description="Hard time limit in seconds")
    task_soft_time_limit: int = Field(default=240, description="Soft time limit in seconds")
    worker_prefetch_multiplier: int = Field(default=4)
    worker_concurrency: int = Field(default=4)


class JWTSettings(BaseSettings):
    """JWT authentication configuration."""

    model_config = SettingsConfigDict(env_prefix="JWT_")

    secret_key: str = Field(default="dev-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)


class CORSSettings(BaseSettings):
    """CORS configuration."""

    model_config = SettingsConfigDict(env_prefix="CORS_")

    origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed origins",
    )
    allow_credentials: bool = Field(default=True)
    allow_methods: List[str] = Field(default=["*"])
    allow_headers: List[str] = Field(default=["*"])

    @property
    def origins_list(self) -> List[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.origins.split(",")]


class TwilioSettings(BaseSettings):
    """Twilio SMS/Voice verification configuration."""

    model_config = SettingsConfigDict(env_prefix="TWILIO_")

    account_sid: str = Field(default="")
    auth_token: str = Field(default="")
    phone_number: str = Field(default="")
    verify_service_sid: str = Field(default="")


class OpenAISettings(BaseSettings):
    """OpenAI API configuration for GPT-4 analysis."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_")

    api_key: str = Field(default="")
    model: str = Field(default="gpt-4-turbo-preview")
    max_tokens: int = Field(default=1000)
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)


class ResembleAISettings(BaseSettings):
    """Resemble AI configuration for audio deepfake detection."""

    model_config = SettingsConfigDict(env_prefix="RESEMBLE_")

    api_key: str = Field(default="")
    api_url: str = Field(default="https://api.resembleai.com")


class SensitySettings(BaseSettings):
    """Sensity/GetReal API configuration for video deepfake detection."""

    model_config = SettingsConfigDict(env_prefix="SENSITY_")

    api_key: str = Field(default="")
    api_url: str = Field(default="https://api.sensity.ai")


class ZoomSettings(BaseSettings):
    """Zoom integration configuration."""

    model_config = SettingsConfigDict(env_prefix="ZOOM_")

    client_id: str = Field(default="")
    client_secret: str = Field(default="")
    webhook_secret_token: str = Field(default="")
    bot_jid: str = Field(default="")
    verification_token: str = Field(default="")


class GoogleMeetSettings(BaseSettings):
    """Google Meet integration configuration."""

    model_config = SettingsConfigDict(env_prefix="GOOGLE_")

    client_id: str = Field(default="")
    client_secret: str = Field(default="")
    service_account_json: str = Field(default="", description="Path to service account JSON")


class SentrySettings(BaseSettings):
    """Sentry error tracking configuration."""

    model_config = SettingsConfigDict(env_prefix="SENTRY_")

    dsn: str = Field(default="")
    environment: str = Field(default="development")
    traces_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)


class DetectionSettings(BaseSettings):
    """Detection engine configuration."""

    model_config = SettingsConfigDict(env_prefix="DETECTION_")

    # Detection mode: local, api, or hybrid
    mode: DetectionMode = Field(default=DetectionMode.LOCAL)

    # Local model settings
    audio_model: str = Field(default="facebook/wav2vec2-base")
    video_model: str = Field(default="google/efficientnet-b4")
    ollama_model: str = Field(default="phi3:mini")
    ollama_url: str = Field(default="http://localhost:11434")
    whisper_model_size: str = Field(default="small")
    local_device: str = Field(default="cpu")

    # Risk score thresholds
    low_risk_threshold: int = Field(default=30, ge=0, le=100)
    medium_risk_threshold: int = Field(default=60, ge=0, le=100)
    high_risk_threshold: int = Field(default=85, ge=0, le=100)

    # Audio-video sync threshold (milliseconds)
    av_sync_threshold_ms: int = Field(default=42, ge=10, le=100)

    # Detection weights
    scenario_weight: float = Field(default=0.20)
    keyword_weight: float = Field(default=0.20)
    gpt4_weight: float = Field(default=0.20)
    participant_weight: float = Field(default=0.15)
    metadata_weight: float = Field(default=0.10)
    behavioral_weight: float = Field(default=0.15)

    # Processing settings
    audio_chunk_seconds: int = Field(default=3, ge=1, le=10)
    video_fps: int = Field(default=5, ge=1, le=30)
    max_latency_seconds: int = Field(default=5, ge=1, le=30)


class Settings(BaseSettings):
    """
    Main application settings.

    All settings can be configured via environment variables.
    Nested settings use their respective prefixes.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="DeepSafe")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    api_prefix: str = Field(default="/api/v1")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=4, ge=1, le=32)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    mongodb: MongoDBSettings = Field(default_factory=MongoDBSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    twilio: TwilioSettings = Field(default_factory=TwilioSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    resemble: ResembleAISettings = Field(default_factory=ResembleAISettings)
    sensity: SensitySettings = Field(default_factory=SensitySettings)
    zoom: ZoomSettings = Field(default_factory=ZoomSettings)
    google_meet: GoogleMeetSettings = Field(default_factory=GoogleMeetSettings)
    sentry: SentrySettings = Field(default_factory=SentrySettings)
    detection: DetectionSettings = Field(default_factory=DetectionSettings)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of allowed values."""
        allowed = {"development", "staging", "production", "testing"}
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v.lower()

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.environment == "testing"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses lru_cache to ensure settings are only loaded once.
    Call get_settings.cache_clear() to reload settings.
    """
    return Settings()
