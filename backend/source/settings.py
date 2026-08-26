from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment variables
    database_url: str
    redis_url: str
    cors_origins: str

    # Email service
    email_from: str
    resend_api_key: str
    resend_max_retries: int = 6
    resend_backoff_base_seconds: float = 0.5
    resend_max_retry_sleep_seconds: float = 20.0
    resend_min_interval_seconds: float = 0.0

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS is a comma-separated string; split it into the list CORSMiddleware expects."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # Manually set variables
    app_name: str = "Picko"
    default_worker_concurrency: int = 4
    schedule_buffer_seconds: int = 5
    celery_visibility_timeout_seconds: int = 60 * 60 * 24 * 14  # 14 days


settings = Settings()


class CurrencySelection(StrEnum):
    EUR = "EUR"
    PLN = "PLN"
    USD = "USD"


class LanguageSelection(StrEnum):
    EN = "en"
    PL = "pl"
