from __future__ import annotations

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="SpartaHacks-11 API", alias="APP_NAME")
    env: str = Field(default="local", alias="ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    api_v1_str: str = Field(default="/api/v1", alias="API_V1_STR")

    # Comma-separated in env; pydantic handles parsing to list for us.
    allowed_origins: List[str] = Field(default_factory=list, alias="ALLOWED_ORIGINS")


settings = Settings()
