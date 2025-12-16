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

    # Manually set variables
    app_name: str = "Picko"
    default_worker_concurrency: int = 4
    schedule_buffer_seconds: int = 5


settings = Settings()


class CurrencySelection(StrEnum):
    EUR = "EUR"
    PLN = "PLN"
    USD = "USD"


class LanguageSelection(StrEnum):
    EN = "en"
    PL = "pl"
