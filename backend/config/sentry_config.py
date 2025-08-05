import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration

def init_sentry():
    """Sentry konfigürasyonunu başlat"""
    
    # Sadece production'da çalıştır
    if os.getenv('ENVIRONMENT') != 'production':
        return
    
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        print("Warning: SENTRY_DSN not set, Sentry monitoring disabled")
        return
    
    sentry_sdk.init(
        dsn=dsn,
        
        # Integrations
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
            HttpxIntegration(),
        ],
        
        # Performance monitoring
        traces_sample_rate=0.1,  # %10 of transactions
        profiles_sample_rate=0.1,  # %10 of profiles
        
        # Error sampling
        sample_rate=0.1,  # %10 of errors
        
        # Environment
        environment=os.getenv('ENVIRONMENT', 'development'),
        
        # Release tracking
        release=os.getenv('APP_VERSION', '1.0.0'),
        
        # Before send hook - aylık limitleri kontrol et
        before_send=lambda event, hint: before_send_filter(event, hint),
        
        # Ignore patterns
        ignore_errors=[
            # Database connection errors
            "ConnectionError",
            "TimeoutError",
            
            # Rate limiting
            "TooManyRequests",
            
            # Validation errors (non-critical)
            "ValidationError",
            
            # Authentication errors (non-critical)
            "AuthenticationError",
        ],
        
        # Debug mode
        debug=os.getenv('SENTRY_DEBUG', 'false').lower() == 'true',
    )

def before_send_filter(event, hint):
    """Sentry event'lerini filtrele ve limitleri kontrol et"""
    
    # Kritik hataları her zaman gönder
    if event.get('level') in ['fatal', 'error']:
        return event
    
    # Warning'leri %50 oranında gönder (limit tasarrufu için)
    if event.get('level') == 'warning' and os.urandom(1)[0] > 127:
        return None
    
    # Info level event'leri %20 oranında gönder
    if event.get('level') == 'info' and os.urandom(1)[0] > 51:  # %20
        return None
    
    # Performance event'lerini sınırla
    if event.get('type') == 'transaction':
        # Sadece kritik endpoint'leri izle
        critical_endpoints = [
            '/api/jobs/search',
            '/api/jobs/apply',
            '/api/user/profile',
            '/api/admin/',
        ]
        
        transaction_name = event.get('transaction', '')
        if not any(endpoint in transaction_name for endpoint in critical_endpoints):
            return None
    
    return event

def capture_exception(error, context=None):
    """Exception'ları Sentry'ye gönder"""
    if os.getenv('ENVIRONMENT') == 'production':
        sentry_sdk.capture_exception(error, extra=context or {})
    else:
        print(f"Error (development): {error}")
        if context:
            print(f"Context: {context}")

def capture_message(message, level='info', context=None):
    """Mesajları Sentry'ye gönder"""
    if os.getenv('ENVIRONMENT') == 'production':
        sentry_sdk.capture_message(message, level=level, extra=context or {})
    else:
        print(f"Message ({level}): {message}")
        if context:
            print(f"Context: {context}")

def set_user_context(user_id, email=None, username=None):
    """Kullanıcı context'ini ayarla"""
    if os.getenv('ENVIRONMENT') == 'production':
        sentry_sdk.set_user({
            'id': str(user_id),
            'email': email,
            'username': username,
        })

def clear_user_context():
    """Kullanıcı context'ini temizle"""
    if os.getenv('ENVIRONMENT') == 'production':
        sentry_sdk.set_user(None)

def start_transaction(name, operation='http.server'):
    """Performance transaction başlat"""
    if os.getenv('ENVIRONMENT') == 'production':
        return sentry_sdk.start_transaction(
            name=name,
            op=operation,
        )
    return None

def set_tag(key, value):
    """Tag ayarla"""
    if os.getenv('ENVIRONMENT') == 'production':
        sentry_sdk.set_tag(key, value)

def set_context(name, data):
    """Context ayarla"""
    if os.getenv('ENVIRONMENT') == 'production':
        sentry_sdk.set_context(name, data) 