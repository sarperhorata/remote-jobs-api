#!/usr/bin/env python3
"""
Script to wake up Render service by making multiple requests
"""

import requests
import time
import sys
from datetime import datetime

def wake_render_service():
    """Wake up Render service by making multiple requests"""
    
    base_url = "https://buzz2remote-api.onrender.com"
    endpoints = [
        "/health",
        "/api/health", 
        "/api/v1/health",
        "/api/v1/cron/health-check",
        "/api/v1/cron/test-timeout"
    ]
    
    headers = {
        "X-API-Key": "buzz2remote-cron-2024",
        "User-Agent": "cron-job.org/1.0"
    }
    
    print(f"🔄 Waking up Render service at {datetime.now()}")
    print(f"📍 Base URL: {base_url}")
    print("=" * 50)
    
    for i, endpoint in enumerate(endpoints, 1):
        url = base_url + endpoint
        method = "POST" if "cron" in endpoint else "GET"
        
        print(f"{i}. Testing {method} {endpoint}")
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, timeout=30)
            else:
                response = requests.get(url, timeout=30)
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
            
            if response.status_code == 200:
                print(f"   ✅ Success!")
                return True
            elif response.status_code == 401:
                print(f"   🔐 Authentication required (expected for cron endpoints)")
            elif response.status_code == 404:
                print(f"   ❌ Not found (service might be sleeping)")
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout (service might be waking up)")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection error (service sleeping)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
        time.sleep(2)  # Wait between requests
    
    return False

def main():
    """Main function"""
    print("🚀 Render Service Wake-up Script")
    print("=" * 40)
    
    # Try multiple times
    for attempt in range(3):
        print(f"\n🔄 Attempt {attempt + 1}/3")
        
        if wake_render_service():
            print("\n✅ Service is awake and responding!")
            break
        else:
            print(f"\n⏳ Waiting 30 seconds before next attempt...")
            time.sleep(30)
    else:
        print("\n❌ Failed to wake up service after 3 attempts")
        print("💡 Try manually deploying from Render dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main() 