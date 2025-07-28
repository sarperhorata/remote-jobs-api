import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration

def init_sentry():
    """Initialize Sentry with free tier optimizations"""
    
    # Only initialize in production
    if os.getenv('ENVIRONMENT') != 'production':
        return
    
    dsn = os.getenv('SENTRY_DSN')
    if not dsn:
        return
    
    # Free tier optimizations
    traces_sample_rate = 0.1  # Only sample 10% of transactions
    profiles_sample_rate = 0.1  # Only sample 10% of profiles
    
    sentry_sdk.init(
        dsn=dsn,
        
        # Performance monitoring
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        
        # Integrations
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
            HttpxIntegration(),
        ],
        
        # Environment
        environment=os.getenv('ENVIRONMENT', 'development'),
        release=os.getenv('APP_VERSION', '1.0.0'),
        
        # Error filtering to avoid spam
        before_send=lambda event, hint: filter_sentry_events(event, hint),
        
        # Rate limiting
        max_breadcrumbs=10,  # Limit breadcrumbs
        
        # Debug mode
        debug=os.getenv('SENTRY_DEBUG', 'false').lower() == 'true',
        
        # Ignore specific errors
        ignore_errors=[
            KeyboardInterrupt,
            ConnectionError,
            TimeoutError,
        ],
    )

def filter_sentry_events(event, hint):
    """Filter out common non-critical errors to stay within free tier limits"""
    
    # Filter out health check errors
    if event.get('request', {}).get('url', '').endswith('/health'):
        return None
    
    # Filter out common browser errors
    if event.get('exception'):
        for exception in event['exception'].get('values', []):
            value = exception.get('value', '')
            
            # Ignore common non-critical errors
            if any(phrase in value.lower() for phrase in [
                'connection refused',
                'timeout',
                'network error',
                'script error',
                'resizeobserver loop limit exceeded',
                'unhandled promise rejection',
            ]):
                return None
    
    # Filter out performance events for non-critical endpoints
    if event.get('transaction'):
        non_critical_endpoints = [
            '/static/',
            '/favicon.ico',
            '/robots.txt',
            '/health',
            '/metrics',
        ]
        
        if any(endpoint in event['transaction'] for endpoint in non_critical_endpoints):
            return None
    
    return event

def capture_exception(error, context=None):
    """Capture exception with context"""
    if context:
        sentry_sdk.set_context("error_context", context)
    sentry_sdk.capture_exception(error)

def capture_message(message, level="info", context=None):
    """Capture message with context"""
    if context:
        sentry_sdk.set_context("message_context", context)
    sentry_sdk.capture_message(message, level)

def set_user_context(user_id, email=None, username=None):
    """Set user context for error tracking"""
    sentry_sdk.set_user({
        "id": str(user_id),
        "email": email,
        "username": username,
    })

def clear_user_context():
    """Clear user context"""
    sentry_sdk.set_user(None)

def start_transaction(name, operation):
    """Start a performance transaction"""
    return sentry_sdk.start_transaction(
        name=name,
        op=operation,
    ) 