#!/usr/bin/env python3
"""
Test script for Mailgun and Sentry integration
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test Mailgun service
        from services.mailgun_service import mailgun_service
        print("✅ Mailgun service imported successfully")
        
        # Test mailgun service stats
        stats = mailgun_service.get_stats()
        print(f"📊 Mailgun stats: {stats}")
        
    except Exception as e:
        print(f"❌ Mailgun import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        # Test Sentry
        import sentry_sdk
        print("✅ Sentry SDK imported successfully")
        
        # Test Sentry client
        hub = sentry_sdk.Hub.current
        client = hub.client
        if client:
            print(f"✅ Sentry client active - DSN configured: {bool(client.dsn)}")
        else:
            print("⚠️ Sentry client not initialized")
            
    except Exception as e:
        print(f"❌ Sentry import error: {e}")
        return False
    
    try:
        # Test FastAPI main app
        from main import app
        print("✅ FastAPI app imported successfully")
        
    except Exception as e:
        print(f"❌ FastAPI app import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_mailgun_config():
    """Test Mailgun configuration"""
    print("\n📧 Testing Mailgun configuration...")
    
    try:
        from services.mailgun_service import mailgun_service
        
        # Check configuration
        print(f"API Key: {'*' * 20}{mailgun_service.api_key[-10:] if mailgun_service.api_key else 'NOT SET'}")
        print(f"Domain: {mailgun_service.domain}")
        print(f"From Email: {mailgun_service.from_email}")
        print(f"Daily Limit: {mailgun_service.daily_limit}")
        print(f"Sent Today: {mailgun_service.sent_today}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mailgun config error: {e}")
        return False

def test_sentry_config():
    """Test Sentry configuration"""
    print("\n🔍 Testing Sentry configuration...")
    
    try:
        import sentry_sdk
        
        hub = sentry_sdk.Hub.current
        client = hub.client
        
        if client:
            print(f"DSN: {'*' * 20}{str(client.dsn)[-20:] if client.dsn else 'NOT SET'}")
            print(f"Environment: {client.options.get('environment', 'NOT SET')}")
            print(f"Release: {client.options.get('release', 'NOT SET')}")
            print(f"Sample Rate: {client.options.get('traces_sample_rate', 'NOT SET')}")
            print(f"Send PII: {client.options.get('send_default_pii', 'NOT SET')}")
        else:
            print("❌ Sentry client not initialized")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Sentry config error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Buzz2Remote - Mailgun & Sentry Integration Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    # Test Mailgun config
    if not test_mailgun_config():
        print("\n❌ Mailgun config tests failed!")
        return False
    
    # Test Sentry config
    if not test_sentry_config():
        print("\n❌ Sentry config tests failed!")
        return False
    
    print("\n🎉 All tests passed successfully!")
    print("\n📋 Next steps:")
    print("1. Start backend: uvicorn main:app --reload --port 8000")
    print("2. Test Mailgun: POST /api/email-test/send-test-email?email=YOUR_EMAIL")
    print("3. Test Sentry: POST /api/sentry-test/test-error")
    print("4. Check email stats: GET /api/email-test/email-stats")
    print("5. Check Sentry config: GET /api/sentry-test/sentry-config")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 