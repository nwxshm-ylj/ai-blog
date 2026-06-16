from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="李宝帅 | 工业AI与制造数字化作品集", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_blog",
        alias="DATABASE_URL",
    )

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    secret_key: str = Field(default="", alias="SECRET_KEY")
    session_cookie_name: str = Field(default="ai_blog_session", alias="SESSION_COOKIE_NAME")
    session_max_age_seconds: int = Field(default=60 * 60 * 24 * 14, alias="SESSION_MAX_AGE_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def validate_production_settings() -> None:
    if settings.app_env in {"local", "development", "test"}:
        return

    if not settings.secret_key or settings.secret_key == "change-me-for-local-development-only":
        raise RuntimeError("SECRET_KEY must be set to a strong unique value in production.")
    if "localhost" in settings.database_url or "postgres:postgres" in settings.database_url:
        raise RuntimeError("DATABASE_URL must not use local default credentials in production.")
