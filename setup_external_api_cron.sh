#!/bin/bash
"""
External API Crontab Setup Script
Fantastic Jobs ve diğer external API'ler için cronjob kurulumu
"""

echo "🚀 Buzz2Remote External API Crontab Setup"
echo "=========================================="

# Get current directory
CURRENT_DIR=$(pwd)
PYTHON_PATH=$(which python3)
CRON_SCRIPT="$CURRENT_DIR/cron_external_apis.py"

echo "📁 Current directory: $CURRENT_DIR"
echo "🐍 Python path: $PYTHON_PATH"
echo "📜 Cron script: $CRON_SCRIPT"

# Check if script exists
if [ ! -f "$CRON_SCRIPT" ]; then
    echo "❌ Error: $CRON_SCRIPT not found!"
    exit 1
fi

# Make script executable
chmod +x "$CRON_SCRIPT"

# Create crontab entry
# Run every day at 9:00 AM (script will handle internal scheduling)
CRON_ENTRY="0 9 * * * cd $CURRENT_DIR && TELEGRAM_BOT_TOKEN=\$TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID=\$TELEGRAM_CHAT_ID $PYTHON_PATH $CRON_SCRIPT >> $CURRENT_DIR/external_api_cron.log 2>&1"

echo ""
echo "📋 Proposed crontab entry:"
echo "$CRON_ENTRY"
echo ""

# Add to crontab
echo "📝 Adding to crontab..."
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Crontab entry added successfully!"
    
    echo ""
    echo "📊 Current crontab:"
    crontab -l | grep -v "^#"
    
    echo ""
    echo "🎯 EXTERNAL API SCHEDULE:"
    echo "• Frequency: Daily at 9:00 AM"
    echo "• Internal Logic: Runs only on target days (1,3,5,7,9,11,13,15,17,19,21,23,25,27,29)"
    echo "• Rate Limit: 15 requests per month"
    echo "• Log File: $CURRENT_DIR/external_api_cron.log"
    
    echo ""
    echo "⚙️ ENVIRONMENT VARIABLES NEEDED:"
    echo "export TELEGRAM_BOT_TOKEN='your_bot_token'"
    echo "export TELEGRAM_CHAT_ID='your_chat_id'"
    
    echo ""
    echo "🔍 MONITORING:"
    echo "• Check logs: tail -f $CURRENT_DIR/external_api_cron.log"
    echo "• Test run: $PYTHON_PATH $CRON_SCRIPT"
    echo "• Rate limit status: cat .api_requests_15_30.json"
    
else
    echo "❌ Error adding crontab entry!"
    exit 1
fi

echo ""
echo "🎉 External API Crontab setup completed!" 