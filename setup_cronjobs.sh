#!/bin/bash

echo "🚀 Buzz2Remote Cronjobs Setup"
echo "============================="

# Get current directory
CURRENT_DIR=$(pwd)
PYTHON_PATH="$CURRENT_DIR/.venv/bin/python3"

echo "📁 Current directory: $CURRENT_DIR"
echo "🐍 Python path: $PYTHON_PATH"

# Create logs directory
mkdir -p logs

# 1. Render ping cronjob (every 14 minutes)
RENDER_PING_CRON="*/14 * * * * curl -s https://buzz2remote-api.onrender.com/api/v1/health >> $CURRENT_DIR/render_ping.log 2>&1"

# 2. Health check cronjob (every hour)
HEALTH_CHECK_CRON="0 * * * * cd $CURRENT_DIR && ./health_check.sh"

# 3. External API cronjob (daily at 9 AM)
EXTERNAL_API_CRON="0 9 * * * cd $CURRENT_DIR && TELEGRAM_BOT_TOKEN=\$TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID=\$TELEGRAM_CHAT_ID $PYTHON_PATH $CURRENT_DIR/cron_external_apis.py >> $CURRENT_DIR/external_api_cron.log 2>&1"

# Add all cronjobs
(crontab -l 2>/dev/null; echo "$RENDER_PING_CRON"; echo "$HEALTH_CHECK_CRON"; echo "$EXTERNAL_API_CRON") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ All cronjobs added successfully!"
    
    echo ""
    echo "📋 Current crontab:"
    crontab -l
    
    echo ""
    echo "🎯 CRONJOB SCHEDULES:"
    echo "• Render Ping: Every 14 minutes (keeps Render awake)"
    echo "• Health Check: Every hour (monitors services)"
    echo "• External API: Daily at 9:00 AM (fetches new jobs)"
    
    echo ""
    echo "📊 LOG FILES:"
    echo "• Render ping: $CURRENT_DIR/render_ping.log"
    echo "• Health check: $CURRENT_DIR/health_check.log"
    echo "• External API: $CURRENT_DIR/external_api_cron.log"
    
    echo ""
    echo "🔍 MONITORING:"
    echo "• Check all logs: tail -f *.log"
    echo "• Test external API: $PYTHON_PATH $CURRENT_DIR/cron_external_apis.py"
    echo "• Test health check: ./health_check.sh"
    
    echo ""
    echo "⚙️ ENVIRONMENT VARIABLES NEEDED:"
    echo "export TELEGRAM_BOT_TOKEN='your_bot_token'"
    echo "export TELEGRAM_CHAT_ID='your_chat_id'"
    
else
    echo "❌ Error adding cronjobs!"
    exit 1
fi

echo ""
echo "🎉 Cronjobs setup completed!" 