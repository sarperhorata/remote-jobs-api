#!/bin/bash

# Load environment variables
set -a
source ../.env
set +a

# Function to send notification to Telegram
send_telegram_notification() {
    platform=$1
    status=$2
    details=$3
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT_ID" \
        -d "parse_mode=HTML" \
        -d "text=🚀 <b>Deployment Update</b>%0A%0APlatform: $platform%0AStatus: $status%0ADetails: $details"
}

echo "Starting deployment process..."

# GitHub Deployment
echo "Deploying to GitHub..."
cd ..
git add .
git commit -m "Auto-deploy: $(date +'%Y-%m-%d %H:%M:%S')"
if git push origin main; then
    send_telegram_notification "GitHub" "✅ Success" "Code pushed successfully"
else
    send_telegram_notification "GitHub" "❌ Failed" "Failed to push code"
    exit 1
fi

# Netlify Deployment
echo "Deploying to Netlify..."
cd frontend
if npm run build && netlify deploy --prod; then
    send_telegram_notification "Netlify" "✅ Success" "Frontend deployed successfully"
else
    send_telegram_notification "Netlify" "❌ Failed" "Frontend deployment failed"
    exit 1
fi

# Render Deployment
echo "Deploying to Render..."
if curl -X POST "$RENDER_DEPLOY_HOOK"; then
    send_telegram_notification "Render" "✅ Success" "Backend deployment triggered"
else
    send_telegram_notification "Render" "❌ Failed" "Failed to trigger backend deployment"
    exit 1
fi

echo "Deployment process completed!"
send_telegram_notification "Overall" "✅ Complete" "All deployments finished successfully" 