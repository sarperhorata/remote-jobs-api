import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "True").lower() == "true"
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# CORS settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

# Email settings
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("MONGODB_URI") or os.getenv("MONGODB_URL")
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

# Set proper database URL based on environment
if not DATABASE_URL:
    if IS_PRODUCTION:
        # In production, DATABASE_URL MUST be set via environment variables
        raise ValueError("DATABASE_URL environment variable is required in production")
    else:
        # In development, use local MongoDB
        DATABASE_URL = "mongodb://localhost:27017/buzz2remote"
        logger.info(f"Using development database: {DATABASE_URL}")
else:
    logger.info(f"Database URL configured: {DATABASE_URL[:20]}...")

# Telegram settings - use placeholder values that won't be flagged
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN.strip() and not TELEGRAM_BOT_TOKEN.startswith("YOUR_"))

# Development mode için Telegram'ı disable et if using placeholder
if not IS_PRODUCTION and TELEGRAM_BOT_TOKEN.startswith("YOUR_"):
    logger.info("Telegram bot disabled - using placeholder token")
    TELEGRAM_ENABLED = False

# Crawler settings
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.5"))  # seconds between requests

# Monitor settings
DEFAULT_CHECK_INTERVAL = 60  # minutes
MAX_CHECK_INTERVAL = 1440  # minutes (24 hours)
MIN_CHECK_INTERVAL = 5  # minutes

# Cache settings
CACHE_TTL = 3600  # seconds (1 hour)
CACHE_MAX_SIZE = 1000  # items

# Rate limiting
RATE_LIMIT_WINDOW = 3600  # seconds (1 hour)
RATE_LIMIT_MAX_REQUESTS = 1000  # requests per window

# File upload
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt"]
UPLOAD_DIR = "uploads"

# Premium features
PREMIUM_PRICE = 8.99  # USD/month
FREE_TRIAL_DAYS = 7
MAX_FREE_JOB_VIEWS = 10
MAX_REFERRAL_DAYS = 30

# Notification settings
EMAIL_NOTIFICATION_INTERVAL = 24  # hours
TELEGRAM_NOTIFICATION_INTERVAL = 1  # hours

# Security
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL = True

def get_db_url() -> str:
    """
    Returns the database connection URL
    """
    # Use DATABASE_URL directly
    return DATABASE_URL

def get_crawler_headers() -> Dict[str, str]:
    """
    Returns HTTP headers for the crawler
    """
    return {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

def get_all_config() -> Dict[str, Any]:
    """
    Returns all configuration settings as a dictionary
    """
    return {
        "api": {
            "host": API_HOST,
            "port": API_PORT,
            "debug": API_DEBUG,
            "reload": API_RELOAD,
        },
        "database": {
            "url": get_db_url(),
            "is_production": IS_PRODUCTION,
        },
        "email": {
            "host": EMAIL_HOST,
            "port": EMAIL_PORT,
            "user": EMAIL_USERNAME,
            "from": EMAIL_FROM,
            "enabled": bool(EMAIL_USERNAME and EMAIL_PASSWORD),
        },
        "telegram": {
            "enabled": TELEGRAM_ENABLED,
            "bot_token": TELEGRAM_BOT_TOKEN,
            "chat_id": TELEGRAM_CHAT_ID,
        },
        "monitor": {
            "default_interval": DEFAULT_CHECK_INTERVAL,
            "max_interval": MAX_CHECK_INTERVAL,
            "min_interval": MIN_CHECK_INTERVAL,
        },
        "crawler": {
            "timeout": REQUEST_TIMEOUT,
            "delay": REQUEST_DELAY,
            "user_agent": USER_AGENT,
        },
        "cors": {
            "origins": CORS_ORIGINS,
            "allow_credentials": CORS_ALLOW_CREDENTIALS,
        },
        "jwt": {
            "secret": JWT_SECRET,
            "algorithm": JWT_ALGORITHM,
            "expire_minutes": JWT_EXPIRE_MINUTES,
        },
        "cache": {
            "ttl": CACHE_TTL,
            "max_size": CACHE_MAX_SIZE,
        },
        "rate_limit": {
            "window": RATE_LIMIT_WINDOW,
            "max_requests": RATE_LIMIT_MAX_REQUESTS,
        },
        "file_upload": {
            "max_size": MAX_UPLOAD_SIZE,
            "allowed_extensions": ALLOWED_EXTENSIONS,
            "upload_dir": UPLOAD_DIR,
        },
        "premium": {
            "price": PREMIUM_PRICE,
            "free_trial_days": FREE_TRIAL_DAYS,
            "max_free_job_views": MAX_FREE_JOB_VIEWS,
            "max_referral_days": MAX_REFERRAL_DAYS,
        },
        "notification": {
            "email_interval": EMAIL_NOTIFICATION_INTERVAL,
            "telegram_interval": TELEGRAM_NOTIFICATION_INTERVAL,
        },
        "security": {
            "password_min_length": PASSWORD_MIN_LENGTH,
            "require_uppercase": PASSWORD_REQUIRE_UPPERCASE,
            "require_lowercase": PASSWORD_REQUIRE_LOWERCASE,
            "require_numbers": PASSWORD_REQUIRE_NUMBERS,
            "require_special": PASSWORD_REQUIRE_SPECIAL,
        },
    } 