from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
