#!/usr/bin/env python3
"""
Debug script for admin panel login
"""

import os
import requests
from urllib.parse import urljoin

def test_admin_login():
    """Test admin login functionality"""
    
    # Base URL
    base_url = "http://localhost:8001"
    login_url = urljoin(base_url, "/admin/login")
    
    print("🔍 Testing Admin Panel Login...")
    print(f"Login URL: {login_url}")
    
    # Check environment variables
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    
    print(f"\n📋 Environment Variables:")
    print(f"ADMIN_USERNAME: {admin_username}")
    print(f"ADMIN_PASSWORD: {admin_password}")
    
    # Test credentials
    test_credentials = [
        ("admin", "buzz2remote2024"),
        ("admin", "wrong_password"),
        ("wrong_username", "buzz2remote2024"),
        ("admin", ""),
        ("", "buzz2remote2024"),
    ]
    
    print(f"\n🧪 Testing Login Credentials:")
    
    for username, password in test_credentials:
        print(f"\n--- Testing: username='{username}', password='{password}' ---")
        
        try:
            # First get the login page
            session = requests.Session()
            response = session.get(login_url)
            
            if response.status_code == 200:
                print(f"✅ Login page accessible")
                
                # Try to login
                login_data = {
                    "username": username,
                    "password": password
                }
                
                login_response = session.post(login_url, data=login_data, allow_redirects=False)
                
                print(f"Login response status: {login_response.status_code}")
                print(f"Login response headers: {dict(login_response.headers)}")
                
                if login_response.status_code == 302:
                    location = login_response.headers.get('Location', '')
                    print(f"Redirect location: {location}")
                    
                    if location == "/admin/":
                        print("✅ Login successful - redirected to admin dashboard")
                    else:
                        print(f"❌ Unexpected redirect: {location}")
                else:
                    print(f"❌ Login failed - no redirect")
                    print(f"Response content length: {len(login_response.content)}")
                    
            else:
                print(f"❌ Cannot access login page: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Is the backend running?")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def test_admin_dashboard_access():
    """Test direct access to admin dashboard"""
    
    base_url = "http://localhost:8001"
    dashboard_url = urljoin(base_url, "/admin/")
    
    print(f"\n🔍 Testing Direct Dashboard Access...")
    print(f"Dashboard URL: {dashboard_url}")
    
    try:
        response = requests.get(dashboard_url, allow_redirects=False)
        print(f"Dashboard response status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"Redirect location: {location}")
            
            if location == "/admin/login":
                print("✅ Correctly redirected to login page")
            else:
                print(f"❌ Unexpected redirect: {location}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is the backend running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Admin Panel Login Debug Script")
    print("=" * 50)
    
    test_admin_login()
    test_admin_dashboard_access()
    
    print("\n" + "=" * 50)
    print("✅ Debug complete!") 