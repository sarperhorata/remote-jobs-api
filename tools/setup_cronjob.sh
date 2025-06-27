#!/bin/bash

# Setup Daily Crawler Cronjob for Buzz2Remote
# This script configures a daily job to crawl all companies

echo "🕰️ Setting up daily crawler cronjob..."

# Get current directory
CURRENT_DIR=$(pwd)
PYTHON_PATH=$(which python3)

# Create logs directory
mkdir -p logs

# Create the cronjob entry
CRONJOB_ENTRY="0 2 * * * cd $CURRENT_DIR && $PYTHON_PATH daily_crawler.py >> logs/cron_output.log 2>&1"

echo "📋 Cronjob entry to be added:"
echo "$CRONJOB_ENTRY"
echo ""

# Check if cronjob already exists
EXISTING_CRON=$(crontab -l 2>/dev/null | grep "daily_crawler.py" || true)

if [ -n "$EXISTING_CRON" ]; then
    echo "⚠️ Cronjob already exists:"
    echo "$EXISTING_CRON"
    echo ""
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing cronjob
        crontab -l 2>/dev/null | grep -v "daily_crawler.py" | crontab -
        echo "🗑️ Removed existing cronjob"
    else
        echo "⏹️ Keeping existing cronjob, exiting..."
        exit 0
    fi
fi

# Add new cronjob
(crontab -l 2>/dev/null; echo "$CRONJOB_ENTRY") | crontab -

echo "✅ Cronjob added successfully!"
echo ""
echo "📊 Cronjob details:"
echo "   - Runs daily at 2:00 AM"
echo "   - Crawls all 471 companies"
echo "   - Logs saved to: logs/"
echo "   - Output saved to: logs/cron_output.log"
echo ""

# Show current crontab
echo "📋 Current crontab:"
crontab -l | grep -E "(daily_crawler|#)"

echo ""
echo "🔧 Manual commands:"
echo "   Test run:     python3 daily_crawler.py"
echo "   View logs:    tail -f logs/crawler_$(date +%Y%m%d).log"
echo "   Cron logs:    tail -f logs/cron_output.log"
echo "   Remove cron:  crontab -e (then delete the line)"
echo ""
echo "🎉 Setup complete! Daily crawling will start tonight at 2:00 AM." 