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
check_endpoint "http://localhost:5001"
check_endpoint "http://localhost:5001/health"
check_endpoint "http://localhost:3000"
check_endpoint "http://localhost:3000/health"

# Check remote endpoints
echo "$TIMESTAMP - Checking remote endpoints..." >> $LOG_FILE
check_endpoint "https://remote-jobs-api-k9v1.onrender.com"
check_endpoint "https://remote-jobs-api-k9v1.onrender.com/health"
check_endpoint "https://buzz2remote.netlify.app"
check_endpoint "https://buzz2remote.netlify.app/health"

# Log completion
echo "$TIMESTAMP - Health check completed" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE 