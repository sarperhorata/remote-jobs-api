#!/usr/bin/env python3
"""
Test script for Render deployment
"""
import os
import sys

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing imports...")
        
        # Test core imports
        import fastapi
        print("✅ FastAPI imported")
        
        import uvicorn
        print("✅ Uvicorn imported")
        
        import motor
        print("✅ Motor imported")
        
        import sentry_sdk
        print("✅ Sentry SDK imported")
        
        import user_agent
        print("✅ User Agent imported")
        
        # Test app import
        from main import app
        print("✅ App imported successfully")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

if __name__ == "__main__":
    print("🚀 Render Deployment Test")
    print("=" * 40)
    
    test_environment()
    success = test_imports()
    
    if success:
        print("✅ Deployment test PASSED")
        sys.exit(0)
    else:
        print("❌ Deployment test FAILED")
        sys.exit(1) 