#!/bin/bash

# Configuration
LOG_FILE="health_check.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Function to check endpoint
check_endpoint() {
    local url=$1
    local response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$response" = "200" ]; then
        echo "$TIMESTAMP - SUCCESS: $url is up (Status: $response)" >> $LOG_FILE
    else
        echo "$TIMESTAMP - ERROR: $url is down (Status: $response)" >> $LOG_FILE
    fi
}

# Check local endpoints first
echo "$TIMESTAMP - Checking local endpoints..." >> $LOG_FILE
check_endpoint "http://localhost:8001"
check_endpoint "http://localhost:8001/api/v1/health"
check_endpoint "http://localhost:3000"
check_endpoint "http://localhost:3002"

# Check remote endpoints
echo "$TIMESTAMP - Checking remote endpoints..." >> $LOG_FILE
check_endpoint "https://buzz2remote-api.onrender.com"
check_endpoint "https://buzz2remote-api.onrender.com/api/v1/health"
check_endpoint "https://buzz2remote.netlify.app"
check_endpoint "https://buzz2remote-frontend.onrender.com"

# Log completion
echo "$TIMESTAMP - Health check completed" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE 