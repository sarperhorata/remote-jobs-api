#!/bin/bash

# Setup Health Check Cronjob for Buzz2Remote
# This script configures an hourly health check for the application

echo "🕰️ Setting up health check cronjob..."

# Get current directory
CURRENT_DIR=$(pwd)

# Create logs directory if it doesn't exist
mkdir -p logs

# Create the cronjob entry
CRONJOB_ENTRY="0 * * * * cd $CURRENT_DIR && ./health_check.sh"

echo "📋 Cronjob entry to be added:"
echo "$CRONJOB_ENTRY"
echo ""

# Check if cronjob already exists
EXISTING_CRON=$(crontab -l 2>/dev/null | grep "health_check.sh" || true)

if [ -n "$EXISTING_CRON" ]; then
    echo "⚠️ Health check cronjob already exists:"
    echo "$EXISTING_CRON"
    echo ""
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing cronjob
        crontab -l 2>/dev/null | grep -v "health_check.sh" | crontab -
        echo "🗑️ Removed existing health check cronjob"
    else
        echo "⏹️ Keeping existing cronjob, exiting..."
        exit 0
    fi
fi

# Add new cronjob
(crontab -l 2>/dev/null; echo "$CRONJOB_ENTRY") | crontab -

echo "✅ Health check cronjob added successfully!"
echo ""
echo "📊 Cronjob details:"
echo "   - Runs every hour"
echo "   - Checks both Render and Netlify endpoints"
echo "   - Logs saved to: health_check.log"
echo ""

# Show current crontab
echo "📋 Current crontab:"
crontab -l | grep -E "(health_check|#)"

echo ""
echo "🔧 Manual commands:"
echo "   Test run:     ./health_check.sh"
echo "   View logs:    tail -f health_check.log"
echo "   Remove cron:  crontab -e (then delete the line)"
echo ""
echo "🎉 Setup complete! Health checks will start on the next hour." 