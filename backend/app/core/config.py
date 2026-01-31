from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_uri: str = Field(..., alias="MONGODB_URI")
    db_name: str = Field(default="FinFancy", alias="MONGODB_DB_NAME")

    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_exp_minutes: int = Field(default=60 * 24, alias="JWT_EXP_MINUTES")

    app_name: str = Field(default="SpartaHacks-11 API", alias="APP_NAME")
    env: str = Field(default="local", alias="ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    api_v1_str: str = Field(default="/api/v1", alias="API_V1_STR")

    # Comma-separated string (e.g. "http://localhost:3000,http://127.0.0.1:3000")
    # Kept as a string to avoid JSON parsing requirements for lists in .env.
    allowed_origins: str = Field(default="", alias="ALLOWED_ORIGINS")


settings = Settings()
