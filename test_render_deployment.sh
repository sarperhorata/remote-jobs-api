#!/bin/bash

echo "🧪 Render Deployment Test Script"
echo "================================"

BASE_URL="https://buzz2remote-api.onrender.com"

echo ""
echo "🔍 Testing endpoints..."

# Test 1: Root endpoint
echo "1. Testing root endpoint..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Root endpoint OK"
else
    echo "   ❌ Root endpoint failed: $RESPONSE"
fi

# Test 2: Health endpoint
echo "2. Testing health endpoint..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/health")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Health endpoint OK"
else
    echo "   ❌ Health endpoint failed: $RESPONSE"
fi

# Test 3: Cron health endpoint
echo "3. Testing cron health endpoint..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/api/v1/cron/health")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Cron health endpoint OK"
    echo "   📝 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Cron health endpoint failed: $RESPONSE"
fi

# Test 4: Test endpoints list
echo "4. Testing endpoints list..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/api/v1/cron/test-endpoints")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ Test endpoints OK"
else
    echo "   ❌ Test endpoints failed: $RESPONSE"
fi

# Test 5: API docs
echo "5. Testing API docs..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL/docs")
if [[ $RESPONSE == *"HTTP_CODE:200"* ]]; then
    echo "   ✅ API docs OK"
else
    echo "   ❌ API docs failed: $RESPONSE"
fi

echo ""
echo "🎯 Quick Commands for Manual Testing:"
echo "======================================"
echo "curl \"$BASE_URL/api/v1/cron/health\""
echo "curl \"$BASE_URL/api/v1/cron/test-endpoints\""
echo "curl -X POST \"$BASE_URL/api/v1/cron/database-cleanup?token=buzz2remote_cron_2024\""
echo ""
echo "📊 Environment Variables Needed:"
echo "================================"
echo "TELEGRAM_BOT_TOKEN=8116251711:AAFhGxXtOJu2eCqCORoDr46XWq7ejqMeYnY"
echo "TELEGRAM_CHAT_ID=-1002424698891"
echo "CRON_SECRET_TOKEN=buzz2remote_cron_2024"
echo ""
echo "🔗 Links:"
echo "========="
echo "Render Dashboard: https://dashboard.render.com"
echo "API Documentation: $BASE_URL/docs"
echo "Cron-job.org: https://cron-job.org" 