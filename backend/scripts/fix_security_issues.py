#!/usr/bin/env python3
"""
Security Issues Fix Script
Fixes hardcoded credentials and security vulnerabilities
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_for_hardcoded_credentials():
    """Check for hardcoded credentials in the codebase."""
    logger.info("🔍 Checking for hardcoded credentials...")
    
    # Patterns to check for
    patterns = [
        r'mongodb\+srv://[^@]+@[^/]+/[^"\s]+',  # MongoDB Atlas URLs
        r'password["\s]*[:=]["\s]*[^"\s]+',     # Password assignments
        r'token["\s]*[:=]["\s]*[^"\s]+',        # Token assignments
        r'secret["\s]*[:=]["\s]*[^"\s]+',       # Secret assignments
        r'api_key["\s]*[:=]["\s]*[^"\s]+',      # API key assignments
    ]
    
    backend_dir = Path(__file__).parent.parent
    issues_found = []
    
    for file_path in backend_dir.rglob("*.py"):
        if "venv" in str(file_path) or "__pycache__" in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues_found.append({
                        'file': str(file_path.relative_to(backend_dir)),
                        'line': line_num,
                        'pattern': pattern,
                        'match': match.group()[:50] + "..." if len(match.group()) > 50 else match.group()
                    })
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
    
    if issues_found:
        logger.warning("⚠️ Potential security issues found:")
        for issue in issues_found:
            logger.warning(f"  {issue['file']}:{issue['line']} - {issue['match']}")
    else:
        logger.info("✅ No hardcoded credentials found!")
    
    return issues_found

def check_environment_variables():
    """Check if required environment variables are set."""
    logger.info("🔍 Checking environment variables...")
    
    required_vars = [
        'MONGODB_URL',
        'JWT_SECRET',
        'ADMIN_PASSWORD',
        'EMAIL_PASSWORD',
        'TELEGRAM_BOT_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning("⚠️ Missing environment variables:")
        for var in missing_vars:
            logger.warning(f"  {var}")
    else:
        logger.info("✅ All required environment variables are set!")
    
    return missing_vars

def create_env_template():
    """Create a template .env file."""
    logger.info("📝 Creating .env template...")
    
    template = """# Database Configuration
MONGODB_URL=mongodb://localhost:27017/buzz2remote
DATABASE_URL=mongodb://localhost:27017/buzz2remote

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password

# Security
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
CORS_ALLOW_CREDENTIALS=true

# Environment
ENVIRONMENT=development
IS_PRODUCTION=false

# Rate Limiting
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_MAX_REQUESTS=1000

# Cache
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Session
SESSION_SECRET_KEY=your-session-secret-key-change-this

# Sentry (Optional)
SENTRY_DSN=your-sentry-dsn
SENTRY_TRACES_SAMPLE_RATE=0.2
SENTRY_PROFILES_SAMPLE_RATE=0.2

# Cron Jobs
CRON_SECRET_TOKEN=your-cron-secret-token

# Logging
LOG_LEVEL=INFO
"""
    
    env_template_path = Path(__file__).parent.parent.parent / ".env.template"
    with open(env_template_path, 'w') as f:
        f.write(template)
    
    logger.info(f"✅ Created .env template at {env_template_path}")

def main():
    """Main function to run security checks."""
    logger.info("🔒 Security Issues Fix Script")
    logger.info("=" * 40)
    
    # Check for hardcoded credentials
    credential_issues = check_for_hardcoded_credentials()
    
    # Check environment variables
    missing_vars = check_environment_variables()
    
    # Create .env template
    create_env_template()
    
    # Summary
    logger.info("\n📊 Security Summary:")
    logger.info(f"  Hardcoded credentials found: {len(credential_issues)}")
    logger.info(f"  Missing environment variables: {len(missing_vars)}")
    
    if credential_issues or missing_vars:
        logger.warning("⚠️ Security issues detected! Please fix them before deployment.")
        return False
    else:
        logger.info("✅ No security issues found!")
        return True

if __name__ == "__main__":
    main() 