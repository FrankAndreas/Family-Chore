from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TESTING: str = "False"
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    CORS_ORIGINS: str = ""

    # SMTP Settings
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    DEFAULT_FROM_EMAIL: str = "chorespec@example.com"

    # VAPID Settings
    VAPID_CLAIMS_EMAIL: str = "mailto:admin@example.com"
    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
