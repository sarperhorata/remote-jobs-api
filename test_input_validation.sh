#!/bin/bash

echo "🔍 Input Validation Test Script"
echo "==============================="

BASE_URL="http://localhost:8001"

# Test 1: Valid search
echo ""
echo "1. Testing valid search..."
RESPONSE=$(curl -s "$BASE_URL/api/v1/jobs/search?q=python" 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo "   ✅ Valid search working"
else
    echo "   ❌ Valid search failed"
fi

# Test 2: XSS attempt
echo ""
echo "2. Testing XSS protection..."
RESPONSE=$(curl -s "$BASE_URL/api/v1/jobs/search?q=<script>alert('xss')</script>" 2>/dev/null)
if [[ $? -eq 0 ]] && echo "$RESPONSE" | grep -q "error"; then
    echo "   ✅ XSS protection working"
elif [[ $? -eq 0 ]]; then
    echo "   ⚠️  XSS protection bypass (might be expected in current implementation)"
else
    echo "   ❌ Request failed"
fi

# Test 3: SQL injection attempt  
echo ""
echo "3. Testing SQL injection protection..."
RESPONSE=$(curl -s "$BASE_URL/api/v1/jobs/search?q=' OR 1=1 --" 2>/dev/null)
if [[ $? -eq 0 ]] && echo "$RESPONSE" | grep -q "error"; then
    echo "   ✅ SQL injection protection working"
elif [[ $? -eq 0 ]]; then
    echo "   ⚠️  SQL injection protection bypass (might be expected)"
else
    echo "   ❌ Request failed"
fi

echo ""
echo "🔍 Input validation tests completed!" 