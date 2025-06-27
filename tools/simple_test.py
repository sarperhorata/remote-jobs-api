#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, 'backend')

print("🧪 SIMPLE MAILGUN TEST")
print("=" * 30)

try:
    from backend.services.mailgun_service import mailgun_service
    print("✅ Mailgun service imported")
    
    # Test email to sarperhorata@gmail.com
    print("📧 Sending test email...")
    result = mailgun_service.send_test_email('sarperhorata@gmail.com')
    
    if result.get('success'):
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print(f"Message ID: {result.get('message_id')}")
    else:
        print(f"❌ Email failed: {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🧪 SIMPLE SENTRY TEST")
print("=" * 30)

try:
    import sentry_sdk
    print("✅ Sentry imported")
    
    # Send test error
    sentry_sdk.capture_message('🧪 Test from Buzz2Remote!', level='error')
    print("✅ TEST ERROR SENT TO SENTRY!")
    
except Exception as e:
    print(f"❌ Sentry error: {e}")

print("\n✅ Tests completed!") 