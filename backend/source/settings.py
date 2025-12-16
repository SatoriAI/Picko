from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment variables
    database_url: str
    cors_origins: str

    # Email Service
    email_from: str
    resend_api_key: str
    app_name: str = "Picko"


settings = Settings()


class CurrencySelection(StrEnum):
    EUR = "EUR"
    PLN = "PLN"
    USD = "USD"


class LanguageSelection(StrEnum):
    EN = "en"
    PL = "pl"
