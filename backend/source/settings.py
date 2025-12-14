from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment variables
    database_url: str
    cors_origins: str

    # Email Service
    sender: str
    resend_api_key: str


settings = Settings()
