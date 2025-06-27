import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import stripe

# Add backend to path to ensure correct imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.main import app

client = TestClient(app)

class TestWebhooksAPI:
    """Test suite for all webhook endpoints."""

    def test_stripe_webhook_valid_signature(self):
        """Test Stripe webhook with a valid signature."""
        with patch('stripe.Webhook.construct_event') as mock_construct_event:
            mock_construct_event.return_value = {"type": "checkout.session.completed", "data": {}}
            
            response = client.post(
                "/api/v1/webhooks/stripe",
                content="test payload",
                headers={"Stripe-Signature": "t=123,v1=test_signature"}
            )
            
            assert response.status_code == 200
            assert response.json() == {"status": "success"}

    def test_stripe_webhook_invalid_signature(self):
        """Test Stripe webhook with an invalid signature."""
        with patch('stripe.Webhook.construct_event', side_effect=stripe.error.SignatureVerificationError("Invalid signature", "sig_header")):
            response = client.post(
                "/api/v1/webhooks/stripe",
                content="test payload",
                headers={"Stripe-Signature": "t=123,v1=invalid_signature"}
            )
            assert response.status_code == 400
            assert "Invalid signature" in response.json()["detail"]

    def test_stripe_webhook_missing_header(self):
        """Test Stripe webhook with a missing signature header."""
        app.dependency_overrides[webhook_secret] = None # Simulate missing secret
        response = client.post("/api/v1/webhooks/stripe", content="test payload")
        assert response.status_code == 400
        assert "Webhook secret or signature not configured" in response.json()["detail"]
        app.dependency_overrides[webhook_secret] = "whsec_test_123" # Restore for other tests
        
    def test_deprecated_stripe_webhook(self):
        """Test the old, deprecated Stripe webhook endpoint."""
        response = client.post("/webhook/stripe", content="test payload")
        assert response.status_code == 410
        assert "deprecated" in response.json()["detail"]

    def test_sentry_webhook(self):
        """Test the Sentry webhook for issue creation."""
        payload = { "action": "created", "issue": { "id": "12345", "title": "Test Sentry Issue" }, "data": { "event": {"level": "info"}, "issue": {"title": "Test Sentry Issue", "permalink": "http://sentry.io/test"} } }
        response = client.post("/api/webhooks/sentry", json=payload)
        
        assert response.status_code == 200
        assert "Webhook processed" in response.json()["message"]
        assert response.json()["success"] is True

# Cleanup dependency override after tests run
def fin():
    app.dependency_overrides = {}
    
app.add_event_handler("shutdown", fin) 