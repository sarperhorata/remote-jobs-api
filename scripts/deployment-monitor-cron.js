#!/usr/bin/env node

/**
 * Deployment Monitor Cron Job
 * Runs every 5 minutes to check deployment status
 */

const cron = require('node-cron');
const { execSync } = require('child_process');
const path = require('path');

// Run deployment monitor every 5 minutes
cron.schedule('*/5 * * * *', async () => {
  console.log('🕐 Running scheduled deployment check...');
  
  try {
    // Run the deployment monitor
    execSync('node scripts/deployment-monitor.js', {
      cwd: path.resolve(__dirname, '..'),
      stdio: 'inherit'
    });
    
    console.log('✅ Scheduled deployment check completed');
  } catch (error) {
    console.error('❌ Scheduled deployment check failed:', error.message);
    
    // Send notification on failure
    try {
      execSync('node scripts/send-notification.js "Deployment monitor failed"', {
        cwd: path.resolve(__dirname, '..'),
        stdio: 'pipe'
      });
    } catch (notifyError) {
      console.error('Failed to send notification:', notifyError.message);
    }
  }
}, {
  scheduled: true,
  timezone: "UTC"
});

console.log('🚀 Deployment monitor cron job started');
console.log('📅 Will run every 5 minutes');

// Keep the process running
process.on('SIGINT', () => {
  console.log('🛑 Stopping deployment monitor cron job...');
  process.exit(0);
}); 