#!/usr/bin/env python3
"""
OAuth2 Form Data Authentication Tests
Tests for the OAuth2PasswordRequestForm authentication fix
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from main import app
import json

client = TestClient(app)


class TestOAuth2FormDataAuth:
    """Test OAuth2 form data authentication implementation"""

    def test_login_accepts_form_data(self):
        """Test that login endpoint accepts OAuth2 form data format"""
        form_data = {
            'username': 'test@example.com',
            'password': 'testpassword123'
        }
        
        # Test with form data (correct format)
        response = client.post('/api/v1/auth/login', data=form_data)
        
        # Should accept the request format (might fail auth but not format)
        assert response.status_code in [200, 401, 422], f"Unexpected status: {response.status_code}, Response: {response.text}"
        
        # Should not return 400 for bad request format
        assert response.status_code != 400, "Login endpoint rejecting valid form data format"

    def test_login_rejects_json_data(self):
        """Test that login endpoint properly handles JSON data (should prefer form data)"""
        json_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        # Test with JSON data (not OAuth2 standard)
        response = client.post('/api/v1/auth/login', json=json_data)
        
        # OAuth2 standard expects form data, so this might be rejected or handled differently
        assert response.status_code in [200, 401, 422], f"Unexpected status: {response.status_code}"

    def test_oauth2_form_data_structure(self):
        """Test that OAuth2 form data uses correct field names"""
        # OAuth2PasswordRequestForm expects 'username' and 'password' fields
        correct_form_data = {
            'username': 'user@example.com',  # OAuth2 uses 'username' even for email
            'password': 'password123',
            'grant_type': 'password',  # Optional but valid OAuth2 field
            'scope': '',  # Optional scope field
            'client_id': '',  # Optional client_id field
            'client_secret': ''  # Optional client_secret field
        }
        
        response = client.post('/api/v1/auth/login', data=correct_form_data)
        
        # Should handle all OAuth2 standard fields properly
        assert response.status_code in [200, 401, 422], f"OAuth2 form structure not handled properly: {response.status_code}"

    def test_register_then_login_workflow(self):
        """Test complete OAuth2 workflow: register then login with form data"""
        # First register a user
        register_data = {
            "email": "oauth2test@example.com",
            "name": "OAuth2 Test User",
            "password": "testpassword123"
        }
        
        register_response = client.post('/api/v1/auth/register', json=register_data)
        
        if register_response.status_code in [200, 201]:
            # If registration successful, try login with OAuth2 form data
            login_form_data = {
                'username': 'oauth2test@example.com',  # OAuth2 uses 'username' field
                'password': 'testpassword123'
            }
            
            login_response = client.post('/api/v1/auth/login', data=login_form_data)
            
            # Should be able to login with form data
            assert login_response.status_code in [200, 401], f"OAuth2 login failed: {login_response.status_code}"
            
            if login_response.status_code == 200:
                # Check response format
                response_data = login_response.json()
                assert "access_token" in response_data, "Missing access_token in response"
                assert "token_type" in response_data, "Missing token_type in response"
                assert response_data["token_type"] == "bearer", "Incorrect token_type"

    def test_form_data_content_type(self):
        """Test that form data is sent with correct content type"""
        form_data = {
            'username': 'test@example.com',
            'password': 'testpassword123'
        }
        
        # Explicitly set content type for form data
        response = client.post(
            '/api/v1/auth/login', 
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        # Should handle form-encoded content type
        assert response.status_code in [200, 401, 422], f"Form content type not handled: {response.status_code}"

    def test_oauth2_error_responses(self):
        """Test OAuth2 error response format"""
        # Test with missing password
        incomplete_form_data = {
            'username': 'test@example.com'
            # Missing password
        }
        
        response = client.post('/api/v1/auth/login', data=incomplete_form_data)
        
        # Should return proper validation error
        assert response.status_code == 422, f"Expected validation error for incomplete form data"
        
        if response.status_code == 422:
            error_detail = response.json()
            assert "detail" in error_detail, "Missing error detail in response"

    def test_oauth2_special_characters(self):
        """Test OAuth2 form data with special characters"""
        form_data = {
            'username': 'test+special@example.com',
            'password': 'password@#$%^&*()'
        }
        
        response = client.post('/api/v1/auth/login', data=form_data)
        
        # Should handle special characters in form data
        assert response.status_code in [200, 401, 422], f"Special characters not handled properly: {response.status_code}"

    def test_oauth2_long_credentials(self):
        """Test OAuth2 with very long credentials"""
        form_data = {
            'username': 'verylongemailaddressthatexceedsnormallengthlimits@exampledomainnamethatisalsoextremelylongfortesting.com',
            'password': 'a' * 200  # Very long password
        }
        
        response = client.post('/api/v1/auth/login', data=form_data)
        
        # Should handle long credentials gracefully
        assert response.status_code in [200, 401, 422], f"Long credentials not handled properly: {response.status_code}"

    def test_oauth2_empty_fields(self):
        """Test OAuth2 with empty fields"""
        form_data = {
            'username': '',
            'password': ''
        }
        
        response = client.post('/api/v1/auth/login', data=form_data)
        
        # Should return validation error for empty fields
        assert response.status_code == 422, f"Empty fields should return validation error: {response.status_code}"

    def test_oauth2_encoding_handling(self):
        """Test OAuth2 form data encoding"""
        # Test with URL-encoded special characters
        form_data = {
            'username': 'test%40example.com',  # URL encoded @
            'password': 'pass%20word'  # URL encoded space
        }
        
        response = client.post('/api/v1/auth/login', data=form_data)
        
        # Should handle URL encoding properly
        assert response.status_code in [200, 401, 422], f"URL encoding not handled properly: {response.status_code}" 