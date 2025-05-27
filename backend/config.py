from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    
    # JWT settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email settings
    EMAIL_HOST: str
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    
    # Google Sheets settings
    GOOGLE_SHEETS_SPREADSHEET_ID: str
    GOOGLE_SHEETS_TOKEN: str
    GOOGLE_SHEETS_REFRESH_TOKEN: str
    GOOGLE_SHEETS_CLIENT_ID: str
    GOOGLE_SHEETS_CLIENT_SECRET: str
    
    # Service URLs
    RENDER_URL: str
    FRONTEND_URL: str = "http://localhost:3000"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str

    # External API Configuration
    REMOTEOK_API_URL: str
    WEWORKREMOTELY_API_URL: str
    GITHUB_JOBS_API_URL: str

    # Job Analysis Configuration
    JOB_ANALYSIS_BATCH_SIZE: int
    JOB_ANALYSIS_MODEL: str
    JOB_ANALYSIS_MAX_TOKENS: int
    JOB_ANALYSIS_TEMPERATURE: float
    
    class Config:
        env_file = ".env"

settings = Settings() 