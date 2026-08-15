"""
Application configuration — loaded from environment variables via Pydantic Settings.
All settings have safe defaults for local development.
"""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_INSECURE_DEFAULT = "change-me-to-a-long-random-string-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────────────────────────────
    APP_ENV: str = "local"
    APP_VERSION: str = "0.1.0"
    APP_NAME: str = "Agent Hub"
    APP_DESCRIPTION: str = "AI Agent Utility Platform — APIs for AI agents and humans."

    # ── Server ─────────────────────────────────────────────────────────────────
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # ── Security ───────────────────────────────────────────────────────────────
    SECRET_KEY: str = _INSECURE_DEFAULT
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "agent-hub"
    JWT_AUDIENCE: str = "agent-hub-api"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_hub"
    )
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # ── Redis ──────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── CORS ───────────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    # ── Validation ─────────────────────────────────────────────────────────────

    @model_validator(mode="after")
    def _validate_production_settings(self):
        """Fail fast if SECRET_KEY is insecure in non-local environments."""
        if self.APP_ENV not in ("local", "test"):
            if self.SECRET_KEY == _INSECURE_DEFAULT:
                raise ValueError(
                    "SECRET_KEY must be set to a strong random value in "
                    f"APP_ENV={self.APP_ENV}. Do not use the default."
                )
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters in production."
                )
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — injected via FastAPI Depends."""
    return Settings()


settings = get_settings()
