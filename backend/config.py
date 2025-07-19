from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional, List, Union
from functools import lru_cache
import os

class Settings(BaseSettings):
    model_config = ConfigDict(extra='ignore', env_file=".env", case_sensitive=True)
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "mongodb://localhost:27017"
    
    # JWT
    JWT_SECRET: str = "your-secret-key"
    
    # Email
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_USERNAME: str = "test@example.com"
    EMAIL_PASSWORD: str = "test_password"
    EMAIL_FROM: str = "test@example.com"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = "test_google_client_id"
    GOOGLE_CLIENT_SECRET: str = "test_google_client_secret"
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_REDIRECT_URI: Optional[str] = None
    
    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_fake"
    STRIPE_WEBHOOK_SECRET: str = "whsec_test_secret"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = "test_telegram_token"
    TELEGRAM_CHAT_ID: str = "123456789"
    
    # Google Sheets
    GOOGLE_SHEETS_SPREADSHEET_ID: Optional[str] = None
    GOOGLE_SHEETS_TOKEN: Optional[str] = None
    GOOGLE_SHEETS_REFRESH_TOKEN: Optional[str] = None
    GOOGLE_SHEETS_CLIENT_ID: Optional[str] = None
    GOOGLE_SHEETS_CLIENT_SECRET: Optional[str] = None
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = "test_openai_key"
    
    # Job APIs
    REMOTEOK_API_URL: Optional[str] = None
    WEWORKREMOTELY_API_URL: Optional[str] = None
    GITHUB_JOBS_API_URL: Optional[str] = None
    
    # Job Analysis
    JOB_ANALYSIS_BATCH_SIZE: int = 10
    JOB_ANALYSIS_MODEL: str = "gpt-3.5-turbo"
    JOB_ANALYSIS_MAX_TOKENS: int = 1000
    JOB_ANALYSIS_TEMPERATURE: float = 0.7
    
    # Frontend
    FRONTEND_URL: str = "https://buzz2remote.com"
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "https://buzz2remote.com"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # API
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 5000
    API_DEBUG: bool = False
    API_RELOAD: bool = True
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "buzz2remote"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Buzz2Remote"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000"
    
    @field_validator('BACKEND_CORS_ORIGINS')
    @classmethod
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 