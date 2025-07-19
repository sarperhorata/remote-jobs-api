import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables
load_dotenv()

# Set logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    # API settings
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    API_RELOAD: bool = True

    # CORS settings
    CORS_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True

    # JWT settings
    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # Email settings
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    # Database settings
    DATABASE_URL: Optional[str] = None
    IS_PRODUCTION: bool = False

    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = "YOUR_BOT_TOKEN_HERE"
    TELEGRAM_CHAT_ID: str = "YOUR_CHAT_ID_HERE"

    # Crawler settings
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    REQUEST_TIMEOUT: int = 30
    REQUEST_DELAY: float = 1.5

    # Monitor settings
    DEFAULT_CHECK_INTERVAL: int = 60
    MAX_CHECK_INTERVAL: int = 1440
    MIN_CHECK_INTERVAL: int = 5

    # Cache settings
    CACHE_TTL: int = 3600
    CACHE_MAX_SIZE: int = 1000

    # Rate limiting
    RATE_LIMIT_WINDOW: int = 3600
    RATE_LIMIT_MAX_REQUESTS: int = 1000

    # File upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS: str = ".pdf,.doc,.docx,.txt"
    UPLOAD_DIR: str = "uploads"

    # Premium features
    PREMIUM_PRICE: float = 8.99
    FREE_TRIAL_DAYS: int = 7
    MAX_FREE_JOB_VIEWS: int = 10
    MAX_REFERRAL_DAYS: int = 30

    # Notification settings
    EMAIL_NOTIFICATION_INTERVAL: int = 24
    TELEGRAM_NOTIFICATION_INTERVAL: int = 1

    # Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # Admin Panel
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "buzz2remote2024"
    ADMIN_PANEL_ENABLED: bool = True

    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.2
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.2
    ENVIRONMENT: str = "development"
    
    # MongoDB URL for explicit use if DATABASE_URL is not set directly
    MONGODB_URL: Optional[str] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Dynamic adjustments after loading from env
        if not self.DATABASE_URL:
            if self.IS_PRODUCTION:
                raise ValueError("DATABASE_URL environment variable is required in production")
            else:
                self.DATABASE_URL = self.MONGODB_URL if self.MONGODB_URL else "mongodb://localhost:27017/buzz2remote"
                logger.info(f"Using development database: {self.DATABASE_URL}")
        else:
            logger.info(f"Database URL configured: {self.DATABASE_URL[:20]}...")
        
        if not self.IS_PRODUCTION and self.TELEGRAM_BOT_TOKEN.startswith("YOUR_"):
            logger.info("Telegram bot disabled - using placeholder token")
            self.TELEGRAM_BOT_TOKEN = ""
            self.TELEGRAM_CHAT_ID = ""

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Test compatibility functions
def get_db_url() -> str:
    """Get database URL for testing compatibility"""
    settings = get_settings()
    return settings.DATABASE_URL or "mongodb://localhost:27017/buzz2remote"

def get_database_url() -> str:
    """Get database URL for testing compatibility"""
    return get_db_url()

def get_all_config() -> Dict[str, Any]:
    """Get all configuration as dictionary for testing compatibility"""
    settings = get_settings()
    return {
        "api": {
            "host": settings.API_HOST,
            "port": settings.API_PORT,
            "debug": settings.API_DEBUG,
            "reload": settings.API_RELOAD,
        },
        "database": {
            "url": settings.DATABASE_URL,
            "is_production": settings.IS_PRODUCTION,
        },
        "email": {
            "host": settings.EMAIL_HOST,
            "port": settings.EMAIL_PORT,
            "user": settings.EMAIL_USERNAME,
            "from": settings.EMAIL_FROM,
            "enabled": bool(settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD),
        },
        "telegram": {
            "bot_token": settings.TELEGRAM_BOT_TOKEN,
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "enabled": bool(settings.TELEGRAM_BOT_TOKEN and not settings.TELEGRAM_BOT_TOKEN.startswith("YOUR_")),
        },
        "monitor": {
            "default_check_interval": settings.DEFAULT_CHECK_INTERVAL,
            "max_check_interval": settings.MAX_CHECK_INTERVAL,
            "min_check_interval": settings.MIN_CHECK_INTERVAL,
        },
        "crawler": {
            "user_agent": settings.USER_AGENT,
            "timeout": settings.REQUEST_TIMEOUT,
            "delay": settings.REQUEST_DELAY,
        },
        "cors": {
            "origins": settings.CORS_ORIGINS,
            "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
        },
        "jwt": {
            "secret": settings.JWT_SECRET,
            "algorithm": settings.JWT_ALGORITHM,
            "expire_minutes": settings.JWT_EXPIRE_MINUTES,
        },
        "cache": {
            "ttl": settings.CACHE_TTL,
            "max_size": settings.CACHE_MAX_SIZE,
        },
        "rate_limit": {
            "window": settings.RATE_LIMIT_WINDOW,
            "max_requests": settings.RATE_LIMIT_MAX_REQUESTS,
        },
        "file_upload": {
            "max_size": settings.MAX_UPLOAD_SIZE,
            "allowed_extensions": settings.ALLOWED_EXTENSIONS,
            "upload_dir": settings.UPLOAD_DIR,
        },
        "premium": {
            "price": settings.PREMIUM_PRICE,
            "free_trial_days": settings.FREE_TRIAL_DAYS,
            "max_free_job_views": settings.MAX_FREE_JOB_VIEWS,
            "max_referral_days": settings.MAX_REFERRAL_DAYS,
        },
        "notification": {
            "email_interval": settings.EMAIL_NOTIFICATION_INTERVAL,
            "telegram_interval": settings.TELEGRAM_NOTIFICATION_INTERVAL,
        },
        "security": {
            "password_min_length": settings.PASSWORD_MIN_LENGTH,
            "require_uppercase": settings.PASSWORD_REQUIRE_UPPERCASE,
            "require_lowercase": settings.PASSWORD_REQUIRE_LOWERCASE,
            "require_numbers": settings.PASSWORD_REQUIRE_NUMBERS,
            "require_special": settings.PASSWORD_REQUIRE_SPECIAL,
        },
        "admin_username": settings.ADMIN_USERNAME,
        "admin_password": settings.ADMIN_PASSWORD,
        "admin_panel_enabled": settings.ADMIN_PANEL_ENABLED,
        "environment": settings.ENVIRONMENT,
        "sentry_dsn": settings.SENTRY_DSN,
    }

def get_crawler_headers() -> Dict[str, str]:
    """Get crawler headers for testing compatibility"""
    settings = get_settings()
    return {
        "User-Agent": settings.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

# Test compatibility constants
settings = get_settings()
DATABASE_URL = settings.DATABASE_URL
USER_AGENT = settings.USER_AGENT
API_HOST = settings.API_HOST
API_PORT = settings.API_PORT 