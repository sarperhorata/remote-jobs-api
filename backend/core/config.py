from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "Buzz2Remote"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-jwt-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: Optional[str] = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: Optional[str] = os.getenv("LINKEDIN_CLIENT_SECRET")
    LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:3000/auth/linkedin/callback")
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    model_config = SettingsConfigDict(
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = Settings() 