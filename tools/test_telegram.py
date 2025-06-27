#!/usr/bin/env python3
"""
Test Telegram Notifications for @buzz2remote

Bu script, Telegram bildirimi sisteminin çalışıp çalışmadığını test eder.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add backend to path
sys.path.append('backend')

async def test_telegram_notifications():
    """Test all Telegram notification functions"""
    print("🧪 Testing Telegram Notifications for @buzz2remote")
    print("=" * 60)
    
    try:
        from backend.utils.telegram import TelegramNotifier
        
        notifier = TelegramNotifier()
        
        # Test 1: Basic message
        print("1. Testing basic message...")
        success1 = await notifier.test_connection()
        print(f"   Result: {'✅ Success' if success1 else '❌ Failed'}")
        
        # Test 2: Deployment notification
        print("\n2. Testing deployment notification...")
        success2 = await notifier.send_deployment_status(
            platform="Test Environment",
            status="success",
            details="Test deployment notification from script"
        )
        print(f"   Result: {'✅ Success' if success2 else '❌ Failed'}")
        
        # Test 3: Error notification
        print("\n3. Testing error notification...")
        success3 = await notifier.send_error_notification(
            error_type="Test Error",
            error_message="This is a test error message",
            component="Test Script"
        )
        print(f"   Result: {'✅ Success' if success3 else '❌ Failed'}")
        
        # Test 4: Crawler status
        print("\n4. Testing crawler status notification...")
        success4 = await notifier.send_crawler_status(
            total_jobs=21741,
            new_jobs=100,
            updated_jobs=500,
            errors=0
        )
        print(f"   Result: {'✅ Success' if success4 else '❌ Failed'}")
        
        # Summary
        total_tests = 4
        passed_tests = sum([success1, success2, success3, success4])
        
        print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("✅ All tests passed! Telegram notifications are working.")
            return True
        else:
            print("❌ Some tests failed. Check configuration.")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure you're running this from the project root directory.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

async def check_telegram_config():
    """Check Telegram configuration"""
    print("\n🔧 Checking Telegram Configuration")
    print("-" * 40)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    channel = os.getenv('TELEGRAM_CHANNEL', '@buzz2remote')
    
    print(f"Bot Token: {'✅ Set' if bot_token else '❌ Not set'}")
    if bot_token:
        print(f"  Token starts with: {bot_token[:20]}...")
    
    print(f"Chat ID: {'✅ Set' if chat_id else '❌ Not set'}")
    if chat_id:
        print(f"  Chat ID: {chat_id}")
        if chat_id == "455797523":
            print("  ⚠️ WARNING: This looks like a personal chat ID, not a channel ID")
            print("  📝 Channel IDs usually start with -100")
    
    print(f"Channel: {channel}")
    
    # Check if all required env vars are loaded
    print(f"\nEnvironment check:")
    print(f"- Current working directory: {os.getcwd()}")
    print(f"- .env file exists: {'✅' if os.path.exists('.env') else '❌'}")
    
    return bool(bot_token)

async def main():
    print("🚀 Buzz2Remote Telegram Test Suite")
    print("=" * 50)
    
    # Check configuration first
    config_ok = await check_telegram_config()
    
    if not config_ok:
        print("\n❌ Configuration incomplete. Please check your .env file.")
        print("\nRequired variables:")
        print("- TELEGRAM_BOT_TOKEN")
        print("- TELEGRAM_CHAT_ID (for @buzz2remote channel)")
        return
    
    # Run tests
    await asyncio.sleep(1)  # Small delay
    success = await test_telegram_notifications()
    
    if success:
        print("\n🎉 All Telegram notifications are working!")
        print("You should see test messages in @buzz2remote channel.")
    else:
        print("\n❌ Some issues found. Common solutions:")
        print("1. Make sure bot is added to @buzz2remote as admin")
        print("2. Update TELEGRAM_CHAT_ID with correct channel ID")
        print("3. Send a message to the channel first")
        print("4. Run get_telegram_channel_id.py to find the correct ID")

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not available, using system env vars")
    
    asyncio.run(main()) 