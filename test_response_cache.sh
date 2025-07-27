#!/bin/bash

echo "⚡ Response Caching Test Script"
echo "==============================="

BASE_URL="http://localhost:8001"

echo ""
echo "🔍 Testing response caching implementation..."

# Test 1: Check cache stats before testing
echo ""
echo "1. Checking initial cache stats..."
RESPONSE=$(curl -s "$BASE_URL/api/cache-stats" 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo "   ✅ Cache stats endpoint working"
    echo "   📊 Initial stats: $RESPONSE"
else
    echo "   ❌ Cache stats endpoint failed"
fi

# Test 2: First request (cache miss)
echo ""
echo "2. Testing first request (should be cache miss)..."
START_TIME=$(date +%s%N)
RESPONSE1=$(curl -s -I "$BASE_URL/api/v1/jobs/search?q=python&limit=5" 2>/dev/null)
END_TIME=$(date +%s%N)
DURATION1=$(((END_TIME - START_TIME) / 1000000))

if [[ $? -eq 0 ]]; then
    echo "   ✅ First request successful"
    echo "   ⏱️  Time: ${DURATION1}ms"
    
    if echo "$RESPONSE1" | grep -i "x-cache: miss" > /dev/null; then
        echo "   ✅ Cache MISS detected (expected)"
    else
        echo "   ⚠️  Cache MISS header missing"
    fi
else
    echo "   ❌ First request failed"
fi

# Test 3: Second request (cache hit)
echo ""
echo "3. Testing second request (should be cache hit)..."
sleep 1
START_TIME=$(date +%s%N)
RESPONSE2=$(curl -s -I "$BASE_URL/api/v1/jobs/search?q=python&limit=5" 2>/dev/null)
END_TIME=$(date +%s%N)
DURATION2=$(((END_TIME - START_TIME) / 1000000))

if [[ $? -eq 0 ]]; then
    echo "   ✅ Second request successful"
    echo "   ⏱️  Time: ${DURATION2}ms"
    
    if echo "$RESPONSE2" | grep -i "x-cache: hit" > /dev/null; then
        echo "   ✅ Cache HIT detected!"
        
        # Calculate performance improvement
        if [[ $DURATION1 -gt 0 && $DURATION2 -gt 0 ]]; then
            IMPROVEMENT=$((($DURATION1 - $DURATION2) * 100 / $DURATION1))
            echo "   🚀 Performance improvement: ${IMPROVEMENT}%"
        fi
    else
        echo "   ❌ Cache HIT not detected"
    fi
else
    echo "   ❌ Second request failed"
fi

# Test 4: Different endpoint
echo ""
echo "4. Testing different endpoint caching..."
START_TIME=$(date +%s%N)
RESPONSE3=$(curl -s -I "$BASE_URL/api/companies/statistics" 2>/dev/null)
END_TIME=$(date +%s%N)
DURATION3=$(((END_TIME - START_TIME) / 1000000))

if [[ $? -eq 0 ]]; then
    echo "   ✅ Statistics endpoint successful"
    echo "   ⏱️  Time: ${DURATION3}ms"
    
    if echo "$RESPONSE3" | grep -i "cache-control" > /dev/null; then
        echo "   ✅ Cache-Control header present"
    fi
    
    if echo "$RESPONSE3" | grep -i "x-cache-ttl" > /dev/null; then
        echo "   ✅ Cache TTL header present"
    fi
else
    echo "   ❌ Statistics endpoint failed"
fi

# Test 5: Cache stats after testing
echo ""
echo "5. Checking cache stats after testing..."
FINAL_RESPONSE=$(curl -s "$BASE_URL/api/cache-stats" 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo "   ✅ Final cache stats retrieved"
    echo "   📊 Final stats: $FINAL_RESPONSE"
else
    echo "   ❌ Final cache stats failed"
fi

# Test 6: Cache clear
echo ""
echo "6. Testing cache clear functionality..."
CLEAR_RESPONSE=$(curl -s -X POST "$BASE_URL/api/cache/clear" 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo "   ✅ Cache clear endpoint working"
    echo "   🗑️  Clear response: $CLEAR_RESPONSE"
else
    echo "   ❌ Cache clear failed"
fi

echo ""
echo "⚡ Response caching tests completed!"

# Performance summary
echo ""
echo "📊 Performance Summary:"
echo "   First request (miss): ${DURATION1}ms"
echo "   Second request (hit):  ${DURATION2}ms"
echo "   Statistics request:    ${DURATION3}ms" 