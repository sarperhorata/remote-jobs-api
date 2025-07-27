#!/bin/bash

echo "🧪 Cronjob Test Script"
echo "======================"

BASE_URL="http://localhost:8001"
TOKEN="buzz2remote_cron_2024"

echo ""
echo "🔍 Testing cronjob endpoints..."

# Test 1: Health endpoint
echo "1. Testing health endpoint..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/api/v1/cron/health")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Health endpoint OK"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Health endpoint failed: $RESPONSE"
fi

echo ""

# Test 2: Database cleanup
echo "2. Testing database cleanup..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/v1/cron/database-cleanup?token=$TOKEN")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Database cleanup OK"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Database cleanup failed: $RESPONSE"
fi

echo ""

# Test 3: External API crawler
echo "3. Testing external API crawler..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/v1/cron/external-api-crawler?token=$TOKEN")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ External API crawler OK"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ External API crawler failed: $RESPONSE"
fi

echo ""

# Test 4: Job statistics
echo "4. Testing job statistics..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/v1/cron/job-statistics?token=$TOKEN")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Job statistics OK"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Job statistics failed: $RESPONSE"
fi

echo ""

# Test 5: Distill crawler
echo "5. Testing distill crawler..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/v1/cron/distill-crawler?token=$TOKEN")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Distill crawler OK"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Distill crawler failed: $RESPONSE"
fi

echo ""

# Test 6: Cron status
echo "6. Testing cron status..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/v1/cron/cron-status?token=$TOKEN")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Cron status OK"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Cron status failed: $RESPONSE"
fi

echo ""

# Test 7: Test timeout
echo "7. Testing test timeout..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/v1/cron/test-timeout?token=$TOKEN")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Test timeout OK"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Test timeout failed: $RESPONSE"
fi

echo ""

# Test 8: Status dashboard
echo "8. Testing status dashboard..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/api/v1/cron/status")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Status dashboard OK"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Status dashboard failed: $RESPONSE"
fi

echo ""

# Test 9: Test endpoints
echo "9. Testing test endpoints..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/api/v1/cron/test-endpoints")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Test endpoints OK"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Test endpoints failed: $RESPONSE"
fi

echo ""
echo "🎯 Quick Commands for Manual Testing:"
echo "======================================"
echo "curl \"$BASE_URL/api/v1/cron/health\""
echo "curl -X POST \"$BASE_URL/api/v1/cron/database-cleanup?token=$TOKEN\""
echo "curl -X POST \"$BASE_URL/api/v1/cron/external-api-crawler?token=$TOKEN\""
echo "curl -X POST \"$BASE_URL/api/v1/cron/job-statistics?token=$TOKEN\""
echo "curl -X POST \"$BASE_URL/api/v1/cron/distill-crawler?token=$TOKEN\""
echo "curl -X POST \"$BASE_URL/api/v1/cron/cron-status?token=$TOKEN\""
echo "curl -X POST \"$BASE_URL/api/v1/cron/test-timeout?token=$TOKEN\""
echo "curl \"$BASE_URL/api/v1/cron/status\""
echo "curl \"$BASE_URL/api/v1/cron/test-endpoints\""

echo ""
echo "📊 Cron-job.org URLs:"
echo "====================="
echo "Database Cleanup: $BASE_URL/api/v1/cron/database-cleanup?token=$TOKEN"
echo "External API Crawler: $BASE_URL/api/v1/cron/external-api-crawler?token=$TOKEN"
echo "Job Statistics: $BASE_URL/api/v1/cron/job-statistics?token=$TOKEN"
echo "Distill Crawler: $BASE_URL/api/v1/cron/distill-crawler?token=$TOKEN"
echo "Cron Status: $BASE_URL/api/v1/cron/cron-status?token=$TOKEN"
echo "Test Timeout: $BASE_URL/api/v1/cron/test-timeout?token=$TOKEN"
echo "Keep Alive: $BASE_URL/api/v1/cron/health"

echo ""
echo "🔗 Links:"
echo "========="
echo "Cron-job.org: https://cron-job.org"
echo "Local Backend: $BASE_URL"
echo "API Documentation: $BASE_URL/docs" 