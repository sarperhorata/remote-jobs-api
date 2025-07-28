#!/bin/bash

echo "🛡️ Security Headers Test Script"
echo "==============================="

BASE_URL="http://localhost:8001"

echo ""
echo "🔍 Testing security headers implementation..."

# Test 1: Basic Security Headers
echo ""
echo "1. Testing basic security headers..."

RESPONSE=$(curl -s -I "$BASE_URL/api/v1/jobs/" 2>/dev/null)

if [[ $? -eq 0 ]]; then
    echo "   ✅ Connection successful"
    
    # Check for security headers
    if echo "$RESPONSE" | grep -i "x-content-type-options" > /dev/null; then
        echo "   ✅ X-Content-Type-Options header present"
    else
        echo "   ❌ X-Content-Type-Options header missing"
    fi
    
    if echo "$RESPONSE" | grep -i "x-frame-options" > /dev/null; then
        echo "   ✅ X-Frame-Options header present"
    else
        echo "   ❌ X-Frame-Options header missing"
    fi
    
    if echo "$RESPONSE" | grep -i "x-xss-protection" > /dev/null; then
        echo "   ✅ X-XSS-Protection header present"
    else
        echo "   ❌ X-XSS-Protection header missing"
    fi
    
    if echo "$RESPONSE" | grep -i "content-security-policy" > /dev/null; then
        echo "   ✅ Content-Security-Policy header present"
    else
        echo "   ❌ Content-Security-Policy header missing"
    fi
    
    if echo "$RESPONSE" | grep -i "strict-transport-security" > /dev/null; then
        echo "   ✅ Strict-Transport-Security header present"
    else
        echo "   ⚠️  HSTS header missing (normal in development)"
    fi
    
    if echo "$RESPONSE" | grep -i "permissions-policy" > /dev/null; then
        echo "   ✅ Permissions-Policy header present"
    else
        echo "   ⚠️  Permissions-Policy header missing"
    fi
    
    echo ""
    echo "📋 Full response headers:"
    echo "$RESPONSE"
    
else
    echo "   ❌ Failed to connect to $BASE_URL"
fi

# Test 2: Security Health Endpoint
echo ""
echo "2. Testing security health endpoint..."

HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/security-health" 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo "   ✅ Security health endpoint accessible"
    echo "   📊 Response: $HEALTH_RESPONSE"
else
    echo "   ❌ Security health endpoint failed"
fi

echo ""
echo "🛡️ Security headers tests completed!" 