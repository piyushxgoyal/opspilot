"""Runtime configuration for the AcmeCloud checkout service.

Configuration is supplied through environment variables so the service
can run unchanged in local development, Docker Compose, and later
deployment environments.

The service intentionally does not contain environment-specific
database credentials in application code.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration values required by the checkout service."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
    )

    database_url: str


@lru_cache
def get_settings() -> Settings:
    """Return the cached application configuration.

    Configuration is loaded once per process. Caching prevents repeated
    environment parsing while keeping configuration construction
    centralized and testable.
    """
    return Settings()
