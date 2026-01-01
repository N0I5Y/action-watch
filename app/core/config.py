import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "GitHub Actions Cron Monitor"
    ENV: str = os.getenv("ENV", "local")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/gha_cron_monitor",
    )

    # GitHub App config
    GITHUB_APP_ID: str | None = None
    GITHUB_APP_PRIVATE_KEY: str | None = None  # optional: if you paste key as env
    GITHUB_WEBHOOK_SECRET: str | None = None
    GITHUB_APP_PRIVATE_KEY_PATH: str | None = None  # path to .pem file
    GITHUB_PERSONAL_ACCESS_TOKEN: str | None = None
    SLACK_WEBHOOK_URL: str | None = None

    # OAuth config (for user login)
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/auth/callback"
    FRONTEND_URL: str = "http://localhost:5173"

    # Stripe config
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unexpected env vars instead of failing
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

# Create a global settings instance for convenience
settings = get_settings()
