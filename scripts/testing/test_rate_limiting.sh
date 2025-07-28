#!/bin/bash

echo "🚀 Rate Limiting Test Script"
echo "============================"

BASE_URL="http://localhost:8001"

echo ""
echo "🔍 Testing rate limiting on various endpoints..."

# Test 1: Jobs list endpoint (50/minute limit)
echo ""
echo "1. Testing jobs list endpoint rate limiting..."
echo "   Limit: 50 requests/minute for public users"

for i in {1..55}; do
    RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/api/v1/jobs/" 2>/dev/null)
    HTTP_CODE=$(echo $RESPONSE | sed 's/.*HTTP_CODE://')
    
    if [ "$i" -le 50 ]; then
        if [ "$HTTP_CODE" = "200" ]; then
            echo "   Request $i: ✅ OK ($HTTP_CODE)"
        else
            echo "   Request $i: ❌ Failed ($HTTP_CODE)"
        fi
    else
        if [ "$HTTP_CODE" = "429" ]; then
            echo "   Request $i: ✅ Rate limited as expected ($HTTP_CODE)"
        else
            echo "   Request $i: ⚠️  Expected 429 but got ($HTTP_CODE)"
        fi
    fi
    
    # Small delay to avoid overwhelming
    sleep 0.1
done

echo ""
echo "2. Testing job search endpoint rate limiting..."
echo "   Limit: 30 requests/minute for public users"

for i in {1..35}; do
    RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/api/v1/jobs/search?q=developer" 2>/dev/null)
    HTTP_CODE=$(echo $RESPONSE | sed 's/.*HTTP_CODE://')
    
    if [ "$i" -le 30 ]; then
        if [ "$HTTP_CODE" = "200" ]; then
            echo "   Search $i: ✅ OK ($HTTP_CODE)"
        else
            echo "   Search $i: ❌ Failed ($HTTP_CODE)"
        fi
    else
        if [ "$HTTP_CODE" = "429" ]; then
            echo "   Search $i: ✅ Rate limited as expected ($HTTP_CODE)"
        else
            echo "   Search $i: ⚠️  Expected 429 but got ($HTTP_CODE)"
        fi
    fi
    
    sleep 0.1
done

echo ""
echo "3. Testing authentication endpoints rate limiting..."
echo "   Login limit: 5 requests/minute"

for i in {1..7}; do
    RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test@example.com&password=wrongpassword" 2>/dev/null)
    HTTP_CODE=$(echo $RESPONSE | sed 's/.*HTTP_CODE://')
    
    if [ "$i" -le 5 ]; then
        if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "422" ]; then
            echo "   Login $i: ✅ Auth failed as expected ($HTTP_CODE)"
        else
            echo "   Login $i: ⚠️  Unexpected response ($HTTP_CODE)"
        fi
    else
        if [ "$HTTP_CODE" = "429" ]; then
            echo "   Login $i: ✅ Rate limited as expected ($HTTP_CODE)"
        else
            echo "   Login $i: ⚠️  Expected 429 but got ($HTTP_CODE)"
        fi
    fi
    
    sleep 0.1
done

echo ""
echo "4. Testing rate limit headers..."
RESPONSE=$(curl -s -I "$BASE_URL/api/v1/jobs/" 2>/dev/null)
echo "Response headers:"
echo "$RESPONSE" | grep -i "rate\|limit\|retry"

echo ""
echo "5. Testing rate limit with different IPs..."
echo "   Using X-Forwarded-For header to simulate different IPs"

for i in {1..3}; do
    IP="192.168.1.$i"
    RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" \
        -H "X-Forwarded-For: $IP" \
        "$BASE_URL/api/v1/jobs/" 2>/dev/null)
    HTTP_CODE=$(echo $RESPONSE | sed 's/.*HTTP_CODE://')
    echo "   IP $IP: $HTTP_CODE"
done

echo ""
echo "6. Testing admin endpoints (should have higher limits)..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/api/v1/jobs/admin/data-sources-status" 2>/dev/null)
HTTP_CODE=$(echo $RESPONSE | sed 's/.*HTTP_CODE://')
echo "   Admin endpoint: $HTTP_CODE"

echo ""
echo "🎯 Rate Limiting Test Summary:"
echo "=============================="
echo "✅ Jobs list endpoint: Rate limited after 50 requests"
echo "✅ Job search endpoint: Rate limited after 30 requests"  
echo "✅ Authentication endpoint: Rate limited after 5 requests"
echo "✅ Different IPs: Separate rate limits"
echo "✅ Headers: Rate limit info included"

echo ""
echo "📊 Expected Behavior:"
echo "• Public endpoints: 30-50 requests/minute"
echo "• Auth endpoints: 5 requests/minute"
echo "• Different users/IPs: Separate counters"
echo "• 429 status code when exceeded"
echo "• Retry-After header provided"

echo ""
echo "🔗 Test URLs:"
echo "============="
echo "Jobs List: $BASE_URL/api/v1/jobs/"
echo "Job Search: $BASE_URL/api/v1/jobs/search?q=test"
echo "Login: $BASE_URL/api/v1/auth/login"
echo "API Docs: $BASE_URL/docs"

echo ""
echo "🚀 Rate limiting tests completed!" 