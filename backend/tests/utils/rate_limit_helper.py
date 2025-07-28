"""
Rate Limiting Test Helper
Provides rate limiting testing utilities
"""

import asyncio
import time
import logging
from typing import List, Dict, Any
from datetime import datetime, UTC
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.middleware.rate_limiter import RateLimiter, TokenBucketRateLimiter

logger = logging.getLogger(__name__)


class RateLimitTestHelper:
    """Helper class for rate limiting tests"""
    
    def __init__(self, client: TestClient):
        self.client = client
        self.requests_made = 0
        self.start_time = time.time()
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make a request and track it"""
        self.requests_made += 1
        
        if method.upper() == "GET":
            response = self.client.get(url, **kwargs)
        elif method.upper() == "POST":
            response = self.client.post(url, **kwargs)
        elif method.upper() == "PUT":
            response = self.client.put(url, **kwargs)
        elif method.upper() == "DELETE":
            response = self.client.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "json": response.json() if response.content else None,
            "text": response.text
        }
    
    def make_multiple_requests(self, method: str, url: str, count: int, **kwargs) -> List[Dict[str, Any]]:
        """Make multiple requests"""
        responses = []
        for i in range(count):
            response = self.make_request(method, url, **kwargs)
            responses.append(response)
            logger.info(f"Request {i+1}/{count}: {response['status_code']}")
        return responses
    
    def make_requests_with_delay(self, method: str, url: str, count: int, delay: float = 0.1, **kwargs) -> List[Dict[str, Any]]:
        """Make multiple requests with delay between them"""
        responses = []
        for i in range(count):
            response = self.make_request(method, url, **kwargs)
            responses.append(response)
            logger.info(f"Request {i+1}/{count}: {response['status_code']}")
            
            if i < count - 1:  # Don't delay after the last request
                time.sleep(delay)
        
        return responses
    
    def get_rate_limit_headers(self, response: Dict[str, Any]) -> Dict[str, str]:
        """Extract rate limit headers from response"""
        headers = response.get("headers", {})
        return {
            "limit": headers.get("X-RateLimit-Limit", ""),
            "remaining": headers.get("X-RateLimit-Remaining", ""),
            "reset": headers.get("X-RateLimit-Reset", ""),
            "retry_after": headers.get("Retry-After", ""),
            "hourly_limit": headers.get("X-RateLimit-Hourly-Limit", ""),
            "hourly_remaining": headers.get("X-RateLimit-Hourly-Remaining", "")
        }
    
    def assert_rate_limit_exceeded(self, response: Dict[str, Any]):
        """Assert that rate limit was exceeded"""
        assert response["status_code"] == 429, f"Expected 429, got {response['status_code']}"
        
        if response.get("json"):
            json_data = response["json"]
            assert "error" in json_data, "Missing error field in response"
            assert json_data["error"] == "Rate limit exceeded", f"Unexpected error: {json_data['error']}"
            assert "retry_after" in json_data, "Missing retry_after field"
            assert "timestamp" in json_data, "Missing timestamp field"
    
    def assert_rate_limit_headers(self, response: Dict[str, Any], expected_remaining: int = None):
        """Assert rate limit headers are present"""
        headers = self.get_rate_limit_headers(response)
        
        assert headers["limit"], "Missing X-RateLimit-Limit header"
        assert headers["remaining"] != "", "Missing X-RateLimit-Remaining header"
        assert headers["reset"], "Missing X-RateLimit-Reset header"
        
        if expected_remaining is not None:
            actual_remaining = int(headers["remaining"])
            assert actual_remaining == expected_remaining, f"Expected {expected_remaining} remaining, got {actual_remaining}"
    
    def assert_successful_request(self, response: Dict[str, Any]):
        """Assert request was successful"""
        assert response["status_code"] < 400, f"Expected success, got {response['status_code']}"
    
    def wait_for_rate_limit_reset(self, seconds: int):
        """Wait for rate limit to reset"""
        logger.info(f"Waiting {seconds} seconds for rate limit reset...")
        time.sleep(seconds)
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get test statistics"""
        elapsed_time = time.time() - self.start_time
        return {
            "requests_made": self.requests_made,
            "elapsed_time": elapsed_time,
            "requests_per_second": self.requests_made / elapsed_time if elapsed_time > 0 else 0,
            "start_time": datetime.fromtimestamp(self.start_time, UTC).isoformat(),
            "end_time": datetime.now(UTC).isoformat()
        }


class RateLimiterTestHelper:
    """Helper for testing rate limiter classes directly"""
    
    @staticmethod
    def create_test_rate_limiter(requests_per_minute: int = 5, requests_per_hour: int = 10) -> RateLimiter:
        """Create a test rate limiter with low limits"""
        return RateLimiter(requests_per_minute=requests_per_minute, requests_per_hour=requests_per_hour)
    
    @staticmethod
    def create_test_token_bucket_limiter(capacity: int = 5, refill_rate: float = 0.5) -> TokenBucketRateLimiter:
        """Create a test token bucket limiter with low capacity"""
        return TokenBucketRateLimiter(capacity=capacity, refill_rate=refill_rate)
    
    @staticmethod
    def simulate_requests(rate_limiter: RateLimiter, client_ip: str, count: int) -> List[bool]:
        """Simulate multiple requests for a client"""
        results = []
        for i in range(count):
            is_allowed, _ = rate_limiter._check_rate_limit(client_ip)
            results.append(is_allowed)
        return results
    
    @staticmethod
    def simulate_token_bucket_requests(limiter: TokenBucketRateLimiter, client_ip: str, count: int) -> List[bool]:
        """Simulate multiple requests for token bucket limiter"""
        results = []
        for i in range(count):
            success = limiter._consume_token(client_ip)
            results.append(success)
        return results
    
    @staticmethod
    def get_client_ip_from_request(request_data: Dict[str, Any]) -> str:
        """Extract client IP from request data"""
        headers = request_data.get("headers", {})
        
        forwarded_for = headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request_data.get("client_ip", "127.0.0.1")


def create_test_app_with_rate_limiting(rate_limiter: RateLimiter = None) -> FastAPI:
    """Create a test FastAPI app with rate limiting"""
    from fastapi import FastAPI
    
    app = FastAPI()
    
    if rate_limiter is None:
        rate_limiter = RateLimiterTestHelper.create_test_rate_limiter()
    
    app.add_middleware(rate_limiter.__class__, 
                      requests_per_minute=rate_limiter.requests_per_minute,
                      requests_per_hour=rate_limiter.requests_per_hour)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test", "timestamp": datetime.now(UTC).isoformat()}
    
    @app.post("/test")
    async def test_post_endpoint():
        return {"message": "test post", "timestamp": datetime.now(UTC).isoformat()}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app


def assert_rate_limit_behavior(responses: List[Dict[str, Any]], expected_success_count: int):
    """Assert rate limiting behavior"""
    success_count = sum(1 for r in responses if r["status_code"] < 400)
    rate_limited_count = sum(1 for r in responses if r["status_code"] == 429)
    
    assert success_count == expected_success_count, f"Expected {expected_success_count} successful requests, got {success_count}"
    assert rate_limited_count > 0, "Expected some requests to be rate limited"
    
    # Check that successful requests come first
    for i, response in enumerate(responses):
        if i < expected_success_count:
            assert response["status_code"] < 400, f"Request {i} should be successful"
        else:
            assert response["status_code"] == 429, f"Request {i} should be rate limited"


def test_rate_limit_headers_consistency(responses: List[Dict[str, Any]]):
    """Test that rate limit headers are consistent"""
    for i, response in enumerate(responses):
        if response["status_code"] < 400:  # Successful requests
            headers = response.get("headers", {})
            
            # Check required headers
            assert "X-RateLimit-Limit" in headers, f"Missing X-RateLimit-Limit in response {i}"
            assert "X-RateLimit-Remaining" in headers, f"Missing X-RateLimit-Remaining in response {i}"
            assert "X-RateLimit-Reset" in headers, f"Missing X-RateLimit-Reset in response {i}"
            
            # Check header values
            limit = int(headers["X-RateLimit-Limit"])
            remaining = int(headers["X-RateLimit-Remaining"])
            
            assert limit > 0, f"Invalid limit value: {limit}"
            assert 0 <= remaining <= limit, f"Invalid remaining value: {remaining}"


def generate_test_requests(count: int, base_url: str = "/test") -> List[Dict[str, Any]]:
    """Generate test request data"""
    requests = []
    for i in range(count):
        requests.append({
            "method": "GET",
            "url": base_url,
            "headers": {
                "User-Agent": f"TestClient/{i}",
                "X-Forwarded-For": f"192.168.1.{i}"
            },
            "client_ip": f"192.168.1.{i}"
        })
    return requests 