"""
Rate Limiting Tests
Tests for rate limiting middleware
"""

import pytest
import time
from unittest.mock import Mock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.middleware.rate_limiter import RateLimiter, TokenBucketRateLimiter
from backend.tests.utils.rate_limit_helper import (
    RateLimitTestHelper, 
    RateLimiterTestHelper,
    create_test_app_with_rate_limiting,
    assert_rate_limit_behavior,
    test_rate_limit_headers_consistency
)


@pytest.fixture
def rate_limiter():
    """Create test rate limiter"""
    return RateLimiterTestHelper.create_test_rate_limiter(requests_per_minute=5, requests_per_hour=10)


@pytest.fixture
def token_bucket_limiter():
    """Create test token bucket limiter"""
    return RateLimiterTestHelper.create_test_token_bucket_limiter(capacity=5, refill_rate=0.5)


@pytest.fixture
def test_app():
    """Create test app with rate limiting"""
    return create_test_app_with_rate_limiting()


@pytest.fixture
def client(test_app):
    """Create test client"""
    return TestClient(test_app)


@pytest.fixture
def rate_limit_helper(client):
    """Create rate limit test helper"""
    return RateLimitTestHelper(client)


class TestRateLimiter:
    """Test RateLimiter class"""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
        
        assert limiter.requests_per_minute == 60
        assert limiter.requests_per_hour == 1000
        assert limiter.minute_requests == {}
        assert limiter.hour_requests == {}
    
    def test_get_client_ip_direct(self):
        """Test getting client IP from direct connection"""
        limiter = RateLimiter()
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.100"
        
        ip = limiter._get_client_ip(mock_request)
        assert ip == "192.168.1.100"
    
    def test_get_client_ip_forwarded(self):
        """Test getting client IP from forwarded header"""
        limiter = RateLimiter()
        mock_request = Mock()
        mock_request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}
        mock_request.client.host = "192.168.1.100"
        
        ip = limiter._get_client_ip(mock_request)
        assert ip == "10.0.0.1"
    
    def test_get_client_ip_real_ip(self):
        """Test getting client IP from real IP header"""
        limiter = RateLimiter()
        mock_request = Mock()
        mock_request.headers = {"X-Real-IP": "172.16.0.1"}
        mock_request.client.host = "192.168.1.100"
        
        ip = limiter._get_client_ip(mock_request)
        assert ip == "172.16.0.1"
    
    def test_cleanup_old_requests(self):
        """Test cleanup of old requests"""
        limiter = RateLimiter()
        current_time = time.time()
        
        # Add old and new requests
        requests_list = [
            current_time - 70,  # Old request (70 seconds ago)
            current_time - 30,  # Recent request (30 seconds ago)
            current_time - 10   # Very recent request (10 seconds ago)
        ]
        
        limiter._cleanup_old_requests(requests_list, 60)
        
        # Should only keep requests from last 60 seconds
        assert len(requests_list) == 2
        assert requests_list[0] == current_time - 30
        assert requests_list[1] == current_time - 10
    
    def test_check_rate_limit_within_limits(self, rate_limiter):
        """Test rate limit check within limits"""
        client_ip = "192.168.1.100"
        
        # Make requests within limit
        for i in range(5):
            is_allowed, message = rate_limiter._check_rate_limit(client_ip)
            assert is_allowed, f"Request {i+1} should be allowed"
            assert message is None
    
    def test_check_rate_limit_exceeded(self, rate_limiter):
        """Test rate limit check when exceeded"""
        client_ip = "192.168.1.100"
        
        # Make requests up to limit
        for i in range(5):
            is_allowed, _ = rate_limiter._check_rate_limit(client_ip)
            assert is_allowed, f"Request {i+1} should be allowed"
        
        # Next request should be blocked
        is_allowed, message = rate_limiter._check_rate_limit(client_ip)
        assert not is_allowed, "Request should be blocked"
        assert "Rate limit exceeded" in message
    
    def test_should_skip_rate_limit(self, rate_limiter):
        """Test rate limit skip logic"""
        # Should skip health endpoint
        assert rate_limiter._should_skip_rate_limit("/health")
        
        # Should skip docs endpoint
        assert rate_limiter._should_skip_rate_limit("/docs")
        
        # Should not skip regular endpoint
        assert not rate_limiter._should_skip_rate_limit("/api/jobs")
    
    def test_get_retry_after(self, rate_limiter):
        """Test retry after calculation"""
        client_ip = "192.168.1.100"
        
        # Make some requests
        for i in range(3):
            rate_limiter._check_rate_limit(client_ip)
        
        retry_after = rate_limiter._get_retry_after(client_ip)
        assert retry_after > 0
        assert retry_after <= 60


class TestTokenBucketRateLimiter:
    """Test TokenBucketRateLimiter class"""
    
    def test_token_bucket_initialization(self):
        """Test token bucket initialization"""
        limiter = TokenBucketRateLimiter(capacity=100, refill_rate=1.0)
        
        assert limiter.capacity == 100
        assert limiter.refill_rate == 1.0
        assert limiter.tokens == {}
        assert limiter.last_refill == {}
    
    def test_refill_tokens_new_client(self, token_bucket_limiter):
        """Test token refill for new client"""
        client_ip = "192.168.1.100"
        
        token_bucket_limiter._refill_tokens(client_ip)
        
        assert client_ip in token_bucket_limiter.tokens
        assert client_ip in token_bucket_limiter.last_refill
        assert token_bucket_limiter.tokens[client_ip] == token_bucket_limiter.capacity
    
    def test_refill_tokens_existing_client(self, token_bucket_limiter):
        """Test token refill for existing client"""
        client_ip = "192.168.1.100"
        
        # Initialize client
        token_bucket_limiter._refill_tokens(client_ip)
        initial_tokens = token_bucket_limiter.tokens[client_ip]
        
        # Consume some tokens
        token_bucket_limiter.tokens[client_ip] = 2
        
        # Wait and refill
        time.sleep(0.1)
        token_bucket_limiter._refill_tokens(client_ip)
        
        # Should have more tokens than before
        assert token_bucket_limiter.tokens[client_ip] > 2
    
    def test_consume_token_success(self, token_bucket_limiter):
        """Test successful token consumption"""
        client_ip = "192.168.1.100"
        
        # Initialize with tokens
        token_bucket_limiter._refill_tokens(client_ip)
        initial_tokens = token_bucket_limiter.tokens[client_ip]
        
        # Consume token
        success = token_bucket_limiter._consume_token(client_ip)
        
        assert success, "Token consumption should succeed"
        assert token_bucket_limiter.tokens[client_ip] == initial_tokens - 1
    
    def test_consume_token_failure(self, token_bucket_limiter):
        """Test failed token consumption"""
        client_ip = "192.168.1.100"
        
        # Initialize with tokens
        token_bucket_limiter._refill_tokens(client_ip)
        
        # Consume all tokens
        for i in range(int(token_bucket_limiter.capacity)):
            token_bucket_limiter._consume_token(client_ip)
        
        # Next consumption should fail
        success = token_bucket_limiter._consume_token(client_ip)
        assert not success, "Token consumption should fail"


class TestRateLimitingIntegration:
    """Test rate limiting integration with FastAPI"""
    
    def test_successful_requests_within_limit(self, rate_limit_helper):
        """Test successful requests within rate limit"""
        responses = rate_limit_helper.make_multiple_requests("GET", "/test", 3)
        
        # All requests should be successful
        for response in responses:
            rate_limit_helper.assert_successful_request(response)
            rate_limit_helper.assert_rate_limit_headers(response)
    
    def test_rate_limit_exceeded(self, rate_limit_helper):
        """Test rate limit exceeded behavior"""
        # Make more requests than allowed
        responses = rate_limit_helper.make_multiple_requests("GET", "/test", 10)
        
        # Should have some successful and some rate limited
        success_count = sum(1 for r in responses if r["status_code"] < 400)
        rate_limited_count = sum(1 for r in responses if r["status_code"] == 429)
        
        assert success_count > 0, "Should have some successful requests"
        assert rate_limited_count > 0, "Should have some rate limited requests"
        
        # Check rate limited responses
        for response in responses:
            if response["status_code"] == 429:
                rate_limit_helper.assert_rate_limit_exceeded(response)
    
    def test_rate_limit_headers_consistency(self, rate_limit_helper):
        """Test rate limit headers consistency"""
        responses = rate_limit_helper.make_multiple_requests("GET", "/test", 3)
        test_rate_limit_headers_consistency(responses)
    
    def test_different_endpoints_same_limit(self, rate_limit_helper):
        """Test that different endpoints share the same rate limit"""
        # Make requests to different endpoints
        responses = []
        responses.extend(rate_limit_helper.make_multiple_requests("GET", "/test", 3))
        responses.extend(rate_limit_helper.make_multiple_requests("POST", "/test", 3))
        
        # Should have some rate limited requests
        rate_limited_count = sum(1 for r in responses if r["status_code"] == 429)
        assert rate_limited_count > 0, "Should have rate limited requests"
    
    def test_health_endpoint_not_rate_limited(self, rate_limit_helper):
        """Test that health endpoint is not rate limited"""
        responses = rate_limit_helper.make_multiple_requests("GET", "/health", 10)
        
        # All health requests should be successful
        for response in responses:
            rate_limit_helper.assert_successful_request(response)
    
    def test_rate_limit_reset_after_wait(self, rate_limit_helper):
        """Test rate limit reset after waiting"""
        # Make requests to hit limit
        responses = rate_limit_helper.make_multiple_requests("GET", "/test", 10)
        
        # Wait for rate limit to reset
        rate_limit_helper.wait_for_rate_limit_reset(2)
        
        # Make more requests
        new_responses = rate_limit_helper.make_multiple_requests("GET", "/test", 3)
        
        # Should have some successful requests
        success_count = sum(1 for r in new_responses if r["status_code"] < 400)
        assert success_count > 0, "Should have successful requests after reset"


class TestRateLimitingEdgeCases:
    """Test rate limiting edge cases"""
    
    def test_empty_client_ip(self, rate_limiter):
        """Test handling of empty client IP"""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.client = None
        
        ip = rate_limiter._get_client_ip(mock_request)
        assert ip == "unknown"
    
    def test_multiple_forwarded_ips(self, rate_limiter):
        """Test handling of multiple forwarded IPs"""
        mock_request = Mock()
        mock_request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1, 172.16.0.1"}
        
        ip = rate_limiter._get_client_ip(mock_request)
        assert ip == "10.0.0.1"
    
    def test_rate_limiter_error_handling(self, rate_limiter):
        """Test rate limiter error handling"""
        # Mock request that will cause an error
        mock_request = Mock()
        mock_request.url.path = "/test"
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.100"
        
        # Mock call_next to raise an exception
        async def mock_call_next(request):
            raise Exception("Test error")
        
        # Should handle error gracefully
        with pytest.raises(Exception):
            asyncio.run(rate_limiter(mock_request, mock_call_next))


class TestRateLimitingPerformance:
    """Test rate limiting performance"""
    
    def test_rate_limiter_performance(self, rate_limiter):
        """Test rate limiter performance"""
        client_ip = "192.168.1.100"
        start_time = time.time()
        
        # Make many requests
        for i in range(100):
            rate_limiter._check_rate_limit(client_ip)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        assert duration < 1.0, f"Rate limiting took too long: {duration}s"
    
    def test_token_bucket_performance(self, token_bucket_limiter):
        """Test token bucket performance"""
        client_ip = "192.168.1.100"
        start_time = time.time()
        
        # Make many token consumptions
        for i in range(100):
            token_bucket_limiter._consume_token(client_ip)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        assert duration < 1.0, f"Token bucket took too long: {duration}s" 