from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Personal Job Portal"
    database_url: str = "postgresql+psycopg://portal:portal@localhost:5432/portal"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    timezone: str = "America/New_York"
    document_storage_dir: str = "./storage/documents"
    app_password: str = "change-me"
    cors_origins: str = "http://localhost:3000"
    adzuna_app_id: str | None = None
    adzuna_app_key: str | None = None
    rapidapi_key: str | None = None
    usajobs_api_key: str | None = None
    usajobs_user_agent: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    default_user_email: str = Field(default="me@local.jobportal")

    @property
    def parsed_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
