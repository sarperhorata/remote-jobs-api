#!/bin/bash

echo "🔍 Render Deployment Status Check"
echo "=================================="

RENDER_URL="https://buzz2remote-api.onrender.com"

echo ""
echo "1. Testing basic connectivity..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$RENDER_URL" 2>/dev/null)
HTTP_CODE=$(echo $RESPONSE | sed 's/.*HTTP_CODE://')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Service is responding!"
    echo "   📄 Response: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "   ❌ Still 404 - FastAPI app not starting"
elif [ "$HTTP_CODE" = "502" ]; then
    echo "   ⚠️  Bad Gateway - Service starting up or crashed"
elif [ "$HTTP_CODE" = "503" ]; then
    echo "   ⚠️  Service Unavailable - Still deploying"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "   ❌ No response - Service down"
else
    echo "   ⚠️  HTTP $HTTP_CODE: $(echo $RESPONSE | sed 's/HTTP_CODE:.*//')"
fi

echo ""
echo "2. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$RENDER_URL/health" 2>/dev/null)
HEALTH_CODE=$(echo $HEALTH_RESPONSE | sed 's/.*HTTP_CODE://')

if [ "$HEALTH_CODE" = "200" ]; then
    echo "   ✅ Health check OK"
    echo "   📄 Health: $(echo $HEALTH_RESPONSE | sed 's/HTTP_CODE:.*//')"
else
    echo "   ❌ Health check failed: $HEALTH_CODE"
fi

echo ""
echo "3. Testing API docs..."
DOCS_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$RENDER_URL/docs" 2>/dev/null)
DOCS_CODE=$(echo $DOCS_RESPONSE | sed 's/.*HTTP_CODE://')

if [ "$DOCS_CODE" = "200" ]; then
    echo "   ✅ API docs accessible"
else
    echo "   ❌ API docs failed: $DOCS_CODE"
fi

echo ""
echo "4. Testing sample API endpoint..."
API_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" "$RENDER_URL/api/v1/jobs/?limit=1" 2>/dev/null)
API_CODE=$(echo $API_RESPONSE | sed 's/.*HTTP_CODE://')

if [ "$API_CODE" = "200" ]; then
    echo "   ✅ Jobs API working"
elif [ "$API_CODE" = "500" ]; then
    echo "   ❌ Internal Server Error - Check logs for DB connection"
else
    echo "   ❌ Jobs API failed: $API_CODE"
fi

echo ""
echo "📋 SUMMARY:"
echo "==========="

if [ "$HTTP_CODE" = "200" ]; then
    echo "🎉 SUCCESS! Render deployment is working!"
    echo ""
    echo "✅ Available endpoints:"
    echo "   • API: $RENDER_URL"
    echo "   • Health: $RENDER_URL/health" 
    echo "   • Docs: $RENDER_URL/docs"
    echo "   • Jobs: $RENDER_URL/api/v1/jobs/"
    echo ""
    echo "🔗 Cronjob endpoints now working:"
    echo "   • Database Cleanup: $RENDER_URL/api/v1/cron/database-cleanup"
    echo "   • External API: $RENDER_URL/api/v1/cron/external-api-crawler"
    echo "   • Job Stats: $RENDER_URL/api/v1/cron/job-statistics"
    echo "   • Health Check: $RENDER_URL/api/v1/cron/health-check"
    echo "   • Status: $RENDER_URL/api/v1/cron/status"
    
elif [ "$HTTP_CODE" = "503" ] || [ "$HTTP_CODE" = "502" ]; then
    echo "⏳ Deployment still in progress or starting up..."
    echo "   Wait 2-3 minutes and run this script again"
    
elif [ "$HTTP_CODE" = "404" ]; then
    echo "❌ FastAPI app not starting - Possible issues:"
    echo "   1. Import errors in backend/main.py"
    echo "   2. Missing dependencies in requirements.txt"
    echo "   3. Environment variables not loaded"
    echo "   4. Database connection failing"
    echo ""
    echo "🔍 Check Render logs for error details:"
    echo "   • Go to Render Dashboard → Your Service → Logs tab"
    echo "   • Look for Python import errors"
    echo "   • Check for missing package errors"
    echo "   • Verify MongoDB connection"
    
else
    echo "❓ Unexpected response: HTTP $HTTP_CODE"
    echo "   Check Render service status and logs"
fi

echo ""
echo "🔧 Next steps based on result:"
echo "=============================="
echo "• If 200: ✅ All working - test cronjobs"  
echo "• If 503/502: ⏳ Wait and retry"
echo "• If 404: 🔍 Check Render deployment logs"
echo "• If 500: 🔍 Check MongoDB connection in logs" 