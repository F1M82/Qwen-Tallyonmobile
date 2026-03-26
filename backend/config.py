# FILE: backend/config.py
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "TaxMind Platform"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    JWT_SECRET: str = "change-this-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/taxmind"
    
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
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
"""
