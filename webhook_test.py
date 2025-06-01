#!/usr/bin/env python3
"""
Webhook Test Script for Deployment and Stripe Notifications
"""

import requests
import json
from datetime import datetime
import stripe
import os

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

def test_stripe_webhook():
    """Test the Stripe webhook endpoint"""
    
    # Initialize Stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Test data
    test_event = {
        "id": "evt_test123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test123",
                "customer": "cus_test123",
                "subscription": "sub_test123",
                "status": "complete"
            }
        }
    }
    
    # Create test signature
    timestamp = int(datetime.now().timestamp())
    payload = json.dumps(test_event).encode()
    signature = stripe.Webhook.construct_event(
        payload, 
        stripe.Webhook.signature_header(timestamp, payload, webhook_secret),
        webhook_secret
    )
    
    # Local test
    local_url = "http://localhost:5001/webhook/stripe"
    
    # Production test
    prod_url = "https://buzz2remote-api.onrender.com/webhook/stripe"
    
    print("🧪 Testing Stripe webhook...")
    
    # Test local first
    try:
        print("Testing local webhook...")
        headers = {
            "stripe-signature": signature,
            "Content-Type": "application/json"
        }
        response = requests.post(local_url, json=test_event, headers=headers, timeout=10)
        print(f"Local response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Local test failed: {e}")
    
    # Test production
    try:
        print("Testing production webhook...")
        response = requests.post(prod_url, json=test_event, headers=headers, timeout=10)
        print(f"Production response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Production test failed: {e}")

if __name__ == "__main__":
    test_deployment_webhook()
    test_stripe_webhook() 