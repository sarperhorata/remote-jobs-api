#!/usr/bin/env python3
"""
Test Mailgun email service
"""

import sys
import os
from datetime import datetime

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.dirname(__file__))

def test_mailgun_email():
    """Test Mailgun email service"""
    print("📧 TESTING MAILGUN EMAIL SERVICE")
    print("=" * 40)
    
    try:
        # Import Mailgun service
        from backend.services.mailgun_service import mailgun_service
        print("✅ Mailgun service imported successfully")
        
        # Check service stats
        stats = mailgun_service.get_stats()
        print(f"📊 Mailgun stats: {stats}")
        
        # Send test email to sarperhorata@gmail.com
        print("\n📧 Sending test email to sarperhorata@gmail.com...")
        result = mailgun_service.send_test_email('sarperhorata@gmail.com')
        
        print(f"\n📊 Email Result:")
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            print(f"✅ EMAIL SENT SUCCESSFULLY!")
            print(f"📨 Message ID: {result.get('message_id')}")
            print(f"📬 Check your email inbox at sarperhorata@gmail.com")
        else:
            print(f"❌ Email failed")
            print(f"Error: {result.get('error')}")
            print(f"Details: {result}")
        
        # Test other email types
        print(f"\n📧 Testing verification email...")
        verification_result = mailgun_service.send_verification_email('sarperhorata@gmail.com', 'test_token_123')
        print(f"Verification email result: {verification_result}")
        
        print(f"\n📧 Testing welcome email...")
        welcome_result = mailgun_service.send_welcome_email('sarperhorata@gmail.com', 'Sarper')
        print(f"Welcome email result: {welcome_result}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Mailgun test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sentry():
    """Test Sentry integration"""
    print(f"\n🚨 TESTING SENTRY INTEGRATION")
    print("=" * 40)
    
    try:
        import sentry_sdk
        print("✅ Sentry SDK imported successfully")
        
        # Initialize Sentry with DSN from environment
        sentry_dsn = os.getenv('SENTRY_DSN', 'https://e307d92640eb7e8b60a7ebabf76db882@o4509547047616512.ingest.us.sentry.io/4509547146575872')
        
        if not sentry_sdk.Hub.current.client:
            sentry_sdk.init(dsn=sentry_dsn)
            print("✅ Sentry initialized")
        
        # Send test error message
        print("🚨 Sending test error to Sentry...")
        sentry_sdk.capture_message(
            f'🧪 TEST ERROR from Buzz2Remote - Integration test at {datetime.now()}', 
            level='error'
        )
        
        # Send test exception
        try:
            raise ValueError("🧪 Test exception for Sentry integration - this is expected!")
        except Exception as e:
            sentry_sdk.capture_exception(e)
        
        print("✅ TEST ERRORS SENT TO SENTRY!")
        print("📱 Check your Telegram for Sentry webhook notifications")
        print("🌐 Also check your Sentry dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 BUZZ2REMOTE EMAIL & SENTRY TESTS")
    print("=" * 50)
    
    # Test Mailgun
    email_success = test_mailgun_email()
    
    # Test Sentry
    sentry_success = test_sentry()
    
    # Summary
    print(f"\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"📧 Mailgun: {'✅ PASS' if email_success else '❌ FAIL'}")
    print(f"🚨 Sentry: {'✅ PASS' if sentry_success else '❌ FAIL'}")
    
    if email_success and sentry_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"📬 Check your email: sarperhorata@gmail.com")
        print(f"📱 Check your Telegram for notifications")
    else:
        print(f"\n⚠️ Some tests failed - check output above") 