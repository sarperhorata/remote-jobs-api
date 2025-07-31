#!/bin/bash

# Deployment Monitor Dashboard
# Shows current status and recent logs

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$PROJECT_DIR/logs/deployment-monitor.log"
REPORT_FILE="$PROJECT_DIR/logs/deployment-report.json"

echo "📊 Buzz2Remote Deployment Monitor Dashboard"
echo "=========================================="
echo ""

# Check if monitor is running
if systemctl is-active --quiet buzz2remote-monitor.service 2>/dev/null; then
    echo "🟢 Monitor Service: RUNNING"
else
    echo "🔴 Monitor Service: STOPPED"
fi

# Show recent logs
echo ""
echo "📋 Recent Logs (last 20 lines):"
echo "-------------------------------"
if [ -f "$LOG_FILE" ]; then
    tail -n 20 "$LOG_FILE"
else
    echo "No logs found"
fi

# Show latest report
echo ""
echo "📈 Latest Report:"
echo "----------------"
if [ -f "$REPORT_FILE" ]; then
    if command -v jq &> /dev/null; then
        cat "$REPORT_FILE" | jq '.'
    else
        cat "$REPORT_FILE"
    fi
else
    echo "No report found"
fi

# Show cron status
echo ""
echo "⏰ Cron Job Status:"
echo "------------------"
if crontab -l 2>/dev/null | grep -q "deployment-monitor-cron.js"; then
    echo "✅ Cron job is active"
    crontab -l | grep "deployment-monitor-cron.js"
else
    echo "❌ Cron job not found"
fi

# Show local service status
echo ""
echo "🏠 Local Service Status:"
echo "----------------------"
if lsof -i :8001 >/dev/null 2>&1; then
    echo "🟢 Backend: RUNNING (port 8001)"
else
    echo "🔴 Backend: STOPPED (port 8001)"
fi

if lsof -i :3002 >/dev/null 2>&1; then
    echo "🟢 Frontend: RUNNING (port 3002)"
else
    echo "🔴 Frontend: STOPPED (port 3002)"
fi

echo ""
echo "🔧 Quick Actions:"
echo "  - Start monitor: sudo systemctl start buzz2remote-monitor"
echo "  - Stop monitor: sudo systemctl stop buzz2remote-monitor"
echo "  - Check once: npm run monitor:once"
echo "  - View report: npm run monitor:report"
echo "  - Start backend: npm run dev:backend"
echo "  - Start frontend: npm run dev:frontend" 