#!/bin/bash

# Deployment Monitor Setup Script
# Sets up cron job for automatic deployment monitoring

set -e

echo "🚀 Setting up Deployment Monitoring System..."

# Check if running as root (needed for cron)
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script needs to be run with sudo for cron setup"
    echo "   Run: sudo $0"
    exit 1
fi

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONITOR_SCRIPT="$PROJECT_DIR/scripts/deployment-monitor-cron.js"

# Check if monitor script exists
if [ ! -f "$MONITOR_SCRIPT" ]; then
    echo "❌ Monitor script not found: $MONITOR_SCRIPT"
    exit 1
fi

# Make monitor script executable
chmod +x "$MONITOR_SCRIPT"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Install Node.js dependencies if needed
if [ ! -f "$PROJECT_DIR/package.json" ]; then
    echo "📦 Creating package.json for monitoring dependencies..."
    cat > "$PROJECT_DIR/package.json" << EOF
{
  "name": "buzz2remote-deployment-monitor",
  "version": "1.0.0",
  "description": "Deployment monitoring and auto-fix system",
  "main": "scripts/deployment-monitor-cron.js",
  "scripts": {
    "monitor": "node scripts/deployment-monitor-cron.js",
    "monitor:once": "node scripts/deployment-monitor-cron.js --once",
    "monitor:report": "node scripts/deployment-monitor-cron.js --report"
  },
  "dependencies": {
    "axios": "^1.6.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF
fi

# Install dependencies
echo "📦 Installing Node.js dependencies..."
cd "$PROJECT_DIR"
npm install

# Create environment file template
ENV_FILE="$PROJECT_DIR/.env.monitor"
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating environment file template..."
    cat > "$ENV_FILE" << EOF
# Deployment Monitor Configuration
# Copy this to .env and fill in your actual values

# Render Configuration
RENDER_SERVICE_ID=buzz2remote-backend
RENDER_API_KEY=your_render_api_key_here

# Netlify Configuration
NETLIFY_SITE_ID=your_netlify_site_id_here
NETLIFY_ACCESS_TOKEN=your_netlify_access_token_here

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=sarperhorata/remote-jobs-api

# Monitoring Configuration
CHECK_INTERVAL=900000  # 15 minutes in milliseconds
MAX_RETRIES=3
EOF
    echo "✅ Created $ENV_FILE - Please update with your actual API keys"
fi

# Set up cron job
echo "⏰ Setting up cron job for deployment monitoring..."

# Create cron job entry
CRON_JOB="*/15 * * * * cd $PROJECT_DIR && source .env.monitor 2>/dev/null; node scripts/deployment-monitor-cron.js --once >> logs/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "deployment-monitor-cron.js"; then
    echo "⚠️  Cron job already exists, updating..."
    # Remove existing cron job
    crontab -l 2>/dev/null | grep -v "deployment-monitor-cron.js" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added successfully!"

# Create systemd service for persistent monitoring (optional)
echo "🔧 Creating systemd service for persistent monitoring..."

SERVICE_FILE="/etc/systemd/system/buzz2remote-monitor.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Buzz2Remote Deployment Monitor
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$PROJECT_DIR
Environment=NODE_ENV=production
ExecStart=/usr/bin/node scripts/deployment-monitor-cron.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable buzz2remote-monitor.service
systemctl start buzz2remote-monitor.service

echo "✅ Systemd service created and started!"

# Create monitoring dashboard script
DASHBOARD_SCRIPT="$PROJECT_DIR/scripts/monitor-dashboard.sh"
cat > "$DASHBOARD_SCRIPT" << 'EOF'
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
if systemctl is-active --quiet buzz2remote-monitor.service; then
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
    cat "$REPORT_FILE" | jq '.' 2>/dev/null || cat "$REPORT_FILE"
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

echo ""
echo "🔧 Quick Actions:"
echo "  - Start monitor: sudo systemctl start buzz2remote-monitor"
echo "  - Stop monitor: sudo systemctl stop buzz2remote-monitor"
echo "  - Check once: npm run monitor:once"
echo "  - View report: npm run monitor:report"
EOF

chmod +x "$DASHBOARD_SCRIPT"

# Create npm scripts
echo "📝 Adding npm scripts to package.json..."

# Check if scripts section exists
if ! grep -q '"scripts"' "$PROJECT_DIR/package.json"; then
    # Add scripts section
    sed -i 's/}/  "scripts": {\n    "monitor": "node scripts\/deployment-monitor-cron.js",\n    "monitor:once": "node scripts\/deployment-monitor-cron.js --once",\n    "monitor:report": "node scripts\/deployment-monitor-cron.js --report",\n    "monitor:dashboard": "bash scripts\/monitor-dashboard.sh"\n  }\n}/' "$PROJECT_DIR/package.json"
else
    # Add to existing scripts section
    sed -i '/"scripts": {/a\    "monitor": "node scripts\/deployment-monitor-cron.js",\n    "monitor:once": "node scripts\/deployment-monitor-cron.js --once",\n    "monitor:report": "node scripts\/deployment-monitor-cron.js --report",\n    "monitor:dashboard": "bash scripts\/monitor-dashboard.sh",' "$PROJECT_DIR/package.json"
fi

echo ""
echo "🎉 Deployment Monitoring System Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Update $ENV_FILE with your actual API keys"
echo "2. Test the monitor: npm run monitor:once"
echo "3. View dashboard: npm run monitor:dashboard"
echo "4. Monitor will run automatically every 15 minutes"
echo ""
echo "🔧 Useful Commands:"
echo "  - Start monitoring: sudo systemctl start buzz2remote-monitor"
echo "  - Stop monitoring: sudo systemctl stop buzz2remote-monitor"
echo "  - View logs: tail -f logs/deployment-monitor.log"
echo "  - Check status: npm run monitor:dashboard"
echo ""
echo "📊 Monitor will check:"
echo "  ✅ Render deployments"
echo "  ✅ GitHub Actions workflows"
echo "  ✅ Netlify deployments"
echo "  ✅ Local service health"
echo "  🔧 Auto-fix common issues" 