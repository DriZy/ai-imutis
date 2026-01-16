"""Application configuration and defaults for the AI-IMUTIS backend."""
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Environment-driven application settings."""

    app_name: str = "AI-IMUTIS API"
    description: str = (
        "Inter-Urban Mobility and Tourism Information System backend built with FastAPI."
    )
    version: str = "1.0.0"
    api_prefix: str = "/api"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    # Runtime environment
    environment: str = "development"

    allowed_origins: str = "http://localhost:3000,http://localhost:19006"

    # Core services (fail fast if empty)
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ai_imutis"
    redis_url: str = "redis://localhost:6379/0"

    firebase_project_id: Optional[str] = None
    firebase_service_account_json: Optional[str] = None
    
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins or return as is."""
        if isinstance(v, str):
            return v
        return v

    @validator("database_url", "redis_url", pre=True)
    def ensure_required(cls, v, field):
        """Ensure required service URLs are provided."""

        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError(f"{field.name.upper()} is required")
        return v

    # Rate limiting tiers (requests per window)
    rate_limit_window_seconds: int = 60
    rate_limit_anonymous: int = 10
    rate_limit_authenticated: int = 100
    rate_limit_premium: int = 500
    rate_limit_ai: int = 20
    rate_limit_booking: int = 5

    request_timeout_seconds: int = 30

    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
