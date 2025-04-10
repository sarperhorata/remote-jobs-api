from pydantic_settings import BaseSettings
from typing import Optional

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
    
    class Config:
        env_file = ".env"

settings = Settings() 