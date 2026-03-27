from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional, List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "TaxMind Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "change-this-in-production-min-32-chars"
    JWT_SECRET: str = "change-this-jwt-secret-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/taxmind"
    REDIS_URL: str = "redis://localhost:6379"

    # AI APIs
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None

    # Tally
    TALLY_HOST: str = "localhost"
    TALLY_PORT: int = 9000
    CONNECTOR_PORT: int = 7000

    # Email
    GMAIL_APP_PASSWORD: Optional[str] = None
    IMAP_SERVER: str = "imap.gmail.com"

    # Payment Detection
    AUTO_POST_CONFIDENCE_THRESHOLD: float = 0.90
    AUTO_POST_MAX_AMOUNT: float = 100000.00

    # Push Notifications
    FIREBASE_SERVER_KEY: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None

    # Frontend URLs
    WEB_URL: str = "http://localhost:5173"
    MOBILE_URL: str = "taxmind://"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://taxmind.in",
        "taxmind://",
    ]

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        _defaults = {
            "change-this-in-production-min-32-chars",
            "change-this-jwt-secret-min-32-chars",
        }
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY in _defaults:
                raise ValueError("SECRET_KEY must be changed in production")
            if self.JWT_SECRET in _defaults:
                raise ValueError("JWT_SECRET must be changed in production")
        return self


settings = Settings()
