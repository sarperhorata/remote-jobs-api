#!/bin/bash

echo "🚀 Render Deployment Diagnosis & Fix Script"
echo "==========================================="

# Configuration
RENDER_URL="https://buzz2remote-api.onrender.com"
LOCAL_URL="http://localhost:8001"
CRON_TOKEN="buzz2remote_cron_2024"

echo ""
echo "📋 RENDER DEPLOYMENT DIAGNOSTICS"
echo "================================="

# Test 1: Basic connectivity
echo ""
echo "1. Testing basic connectivity..."
BASIC_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$RENDER_URL" 2>/dev/null)
HTTP_CODE=$(echo $BASIC_RESPONSE | sed 's/.*HTTP_CODE://')

if [ "$HTTP_CODE" = "404" ]; then
    echo "   ❌ 404 Error - API not accessible"
    echo "   🔍 Response: $(echo $BASIC_RESPONSE | sed 's/HTTP_CODE:.*//')"
elif [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Basic connectivity OK"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "   ❌ No response - service may be down"
else
    echo "   ⚠️  Unexpected response: $HTTP_CODE"
fi

# Test 2: Health endpoint
echo ""
echo "2. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$RENDER_URL/health" 2>/dev/null)
HTTP_CODE=$(echo $HEALTH_RESPONSE | sed 's/.*HTTP_CODE://')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Health endpoint OK"
    echo "   📄 Response: $(echo $HEALTH_RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Health endpoint failed: $HTTP_CODE"
fi

# Test 3: API v1 endpoints
echo ""
echo "3. Testing API v1 endpoints..."
API_ENDPOINTS=(
    "/api/v1/jobs/"
    "/api/v1/companies/"
    "/api/v1/cron/health"
    "/api/v1/cron/status"
)

for endpoint in "${API_ENDPOINTS[@]}"; do
    echo "   Testing $endpoint..."
    RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$RENDER_URL$endpoint" 2>/dev/null)
    HTTP_CODE=$(echo $RESPONSE | sed 's/.*HTTP_CODE://')
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "     ✅ OK ($HTTP_CODE)"
    elif [ "$HTTP_CODE" = "404" ]; then
        echo "     ❌ Not Found ($HTTP_CODE)"
    else
        echo "     ⚠️  Response: $HTTP_CODE"
    fi
done

# Test 4: Environment variable check via cronjob endpoints
echo ""
echo "4. Testing environment variables via cronjob..."
CRON_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST "$RENDER_URL/api/v1/cron/database-cleanup?token=$CRON_TOKEN" 2>/dev/null)
HTTP_CODE=$(echo $CRON_RESPONSE | sed 's/.*HTTP_CODE://')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Cronjob endpoint accessible - env vars likely OK"
    echo "   📄 Response: $(echo $CRON_RESPONSE | sed 's/HTTP_CODE:.*//')"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "   ❌ Cronjob endpoint not found - routing issue"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "   ❌ Internal server error - likely env var or config issue"
else
    echo "   ⚠️  Unexpected response: $HTTP_CODE"
fi

echo ""
echo "📊 DEPLOYMENT STATUS ANALYSIS"
echo "============================="

# Check deployment status
echo ""
echo "🔍 Render Service Status Check:"
echo "• Go to: https://dashboard.render.com"
echo "• Check your buzz2remote-api service"
echo "• Look for:"
echo "  - Deploy status (Live/Failed/Building)"
echo "  - Latest deployment logs"
echo "  - Environment variables"

echo ""
echo "🔧 REQUIRED ENVIRONMENT VARIABLES"
echo "================================="

echo "Add these in Render Dashboard → Environment tab:"
echo ""
echo "TELEGRAM_BOT_TOKEN=8116251711:AAFhGxXtOJu2eCqCORoDr46XWq7ejqMeYnY"
echo "TELEGRAM_CHAT_ID=-1002424698891"
echo "CRON_SECRET_TOKEN=buzz2remote_cron_2024"
echo "ENVIRONMENT=production"
echo "LOG_LEVEL=INFO"
echo "MONGODB_URI=your-mongodb-connection-string"

echo ""
echo "⚠️  IMPORTANT STEPS:"
echo "1. Add environment variables in Render Dashboard"
echo "2. Redeploy the service"
echo "3. Check deployment logs for errors"
echo "4. Run this script again to verify fix"

echo ""
echo "🛠️  TROUBLESHOOTING GUIDE"
echo "========================"

if [ "$HTTP_CODE" = "404" ]; then
    echo ""
    echo "🚨 404 ERRORS DETECTED"
    echo "Possible causes:"
    echo "1. Service not properly deployed"
    echo "2. Wrong service URL"
    echo "3. FastAPI app not starting correctly"
    echo "4. Missing main.py or incorrect start command"
    echo ""
    echo "✅ Solutions:"
    echo "1. Check Render service logs for startup errors"
    echo "2. Verify start command: 'uvicorn main:app --host 0.0.0.0 --port \$PORT'"
    echo "3. Ensure main.py exists in root directory"
    echo "4. Check build logs for Python dependency issues"
elif [ "$HTTP_CODE" = "500" ]; then
    echo ""
    echo "🚨 500 INTERNAL SERVER ERROR"
    echo "Possible causes:"
    echo "1. Missing environment variables"
    echo "2. Database connection issues"
    echo "3. Python dependency conflicts"
    echo "4. Code errors in startup"
    echo ""
    echo "✅ Solutions:"
    echo "1. Add all required environment variables"
    echo "2. Check MongoDB connection string"
    echo "3. Review Render deployment logs"
    echo "4. Test locally first"
elif [ "$HTTP_CODE" = "000" ]; then
    echo ""
    echo "🚨 NO RESPONSE"
    echo "Service is likely down or not accessible"
    echo ""
    echo "✅ Solutions:"
    echo "1. Check Render dashboard for service status"
    echo "2. Look for recent failed deployments"
    echo "3. Check for billing/account issues"
    echo "4. Verify service is not suspended"
fi

echo ""
echo "📋 NEXT STEPS:"
echo "=============="
echo "1. Go to Render Dashboard: https://dashboard.render.com"
echo "2. Select your buzz2remote-api service"
echo "3. Check 'Events' tab for deployment history"
echo "4. Check 'Logs' tab for runtime errors"
echo "5. Add missing environment variables in 'Environment' tab"
echo "6. Trigger manual redeploy if needed"
echo "7. Run this script again to verify fixes"

echo ""
echo "🔗 USEFUL LINKS:"
echo "=================="
echo "• Render Dashboard: https://dashboard.render.com"
echo "• Service URL: $RENDER_URL"
echo "• Health Check: $RENDER_URL/health"
echo "• API Docs: $RENDER_URL/docs"
echo "• Cronjob Test: $RENDER_URL/api/v1/cron/test-endpoints"

echo ""
echo "📞 If you need help:"
echo "===================="
echo "1. Share Render deployment logs"
echo "2. Confirm environment variables are added"
echo "3. Check if service shows 'Live' status in dashboard"
echo "4. Verify MongoDB connection string is correct"

echo ""
echo "🎯 Deployment diagnosis completed!"
echo "Run script again after making changes in Render Dashboard." 