#!/usr/bin/env python3
"""
Webhook Test Script for Deployment Notifications
"""

import requests
import json
from datetime import datetime

def test_deployment_webhook():
    """Test the deployment webhook endpoint"""
    
    # Test data
    deployment_data = {
        'environment': 'production',
        'status': 'success',
        'commit': 'abc12345',
        'message': 'Test deployment notification from webhook',
        'timestamp': datetime.now().isoformat()
    }
    
    # Local test
    local_url = "http://localhost:5001/webhook/deployment"
    
    # Production test
    prod_url = "https://buzz2remote-api.onrender.com/webhook/deployment"
    
    print("🧪 Testing deployment webhook...")
    
    # Test local first
    try:
        print("Testing local webhook...")
        response = requests.post(local_url, json=deployment_data, timeout=10)
        print(f"Local response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Local test failed: {e}")
    
    # Test production
    try:
        print("Testing production webhook...")
        response = requests.post(prod_url, json=deployment_data, timeout=10)
        print(f"Production response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Production test failed: {e}")

if __name__ == "__main__":
    test_deployment_webhook() 