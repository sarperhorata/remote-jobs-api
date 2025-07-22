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
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    
    # Email
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: Optional[str] = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: Optional[str] = os.getenv("LINKEDIN_CLIENT_SECRET")
    LINKEDIN_REDIRECT_URI: Optional[str] = os.getenv("LINKEDIN_REDIRECT_URI")
    
    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Google Sheets
    GOOGLE_SHEETS_SPREADSHEET_ID: Optional[str] = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    GOOGLE_SHEETS_TOKEN: Optional[str] = os.getenv("GOOGLE_SHEETS_TOKEN")
    GOOGLE_SHEETS_REFRESH_TOKEN: Optional[str] = os.getenv("GOOGLE_SHEETS_REFRESH_TOKEN")
    GOOGLE_SHEETS_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_SHEETS_CLIENT_ID")
    GOOGLE_SHEETS_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_SHEETS_CLIENT_SECRET")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Job APIs
    REMOTEOK_API_URL: Optional[str] = os.getenv("REMOTEOK_API_URL")
    WEWORKREMOTELY_API_URL: Optional[str] = os.getenv("WEWORKREMOTELY_API_URL")
    GITHUB_JOBS_API_URL: Optional[str] = os.getenv("GITHUB_JOBS_API_URL")
    
    # Job Analysis
    JOB_ANALYSIS_BATCH_SIZE: int = 10
    JOB_ANALYSIS_MODEL: str = "gpt-3.5-turbo"
    JOB_ANALYSIS_MAX_TOKENS: int = 1000
    JOB_ANALYSIS_TEMPERATURE: float = 0.7
    
    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://buzz2remote.com")
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://buzz2remote.com")
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # API
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "5000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "buzz2remote")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Buzz2Remote"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")
    
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