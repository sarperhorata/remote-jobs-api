#!/usr/bin/env node

/**
 * Sentry Setup Script for Buzz2Remote
 * 
 * This script helps configure Sentry for both frontend and backend
 * with free tier optimizations to stay within limits.
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const question = (query) => new Promise((resolve) => rl.question(query, resolve));

async function setupSentry() {
  console.log('🚀 Sentry Setup for Buzz2Remote\n');
  
  try {
    // Get Sentry DSN
    const dsn = await question('Enter your Sentry DSN: ');
    if (!dsn) {
      console.log('❌ DSN is required');
      process.exit(1);
    }
    
    // Get environment
    const environment = await question('Enter environment (development/production): ') || 'development';
    
    // Get app version
    const version = await question('Enter app version (default: 1.0.0): ') || '1.0.0';
    
    // Get webhook secret
    const webhookSecret = await question('Enter Sentry webhook secret (optional): ') || '';
    
    console.log('\n📝 Creating configuration files...\n');
    
    // Create frontend .env.local
    const frontendEnvPath = path.join(__dirname, '../frontend/.env.local');
    const frontendEnvContent = `# Sentry Configuration (Free Tier Optimized)
REACT_APP_SENTRY_DSN=${dsn}
REACT_APP_ENVIRONMENT=${environment}
REACT_APP_VERSION=${version}
REACT_APP_ENABLE_SENTRY=true
`;
    
    fs.writeFileSync(frontendEnvPath, frontendEnvContent);
    console.log('✅ Frontend .env.local created');
    
    // Create backend .env
    const backendEnvPath = path.join(__dirname, '../backend/.env');
    const backendEnvContent = `# Sentry Configuration (Free Tier Optimized)
SENTRY_DSN=${dsn}
ENVIRONMENT=${environment}
APP_VERSION=${version}
SENTRY_DEBUG=false
${webhookSecret ? `SENTRY_WEBHOOK_SECRET=${webhookSecret}` : ''}
`;
    
    fs.writeFileSync(backendEnvPath, backendEnvContent);
    console.log('✅ Backend .env created');
    
    // Create Sentry configuration guide
    const guidePath = path.join(__dirname, '../docs/SENTRY_SETUP_GUIDE.md');
    const guideContent = `# Sentry Setup Guide

## Overview
Sentry is configured for Buzz2Remote with free tier optimizations to stay within limits.

## Configuration

### Frontend (.env.local)
\`\`\`env
REACT_APP_SENTRY_DSN=${dsn}
REACT_APP_ENVIRONMENT=${environment}
REACT_APP_VERSION=${version}
REACT_APP_ENABLE_SENTRY=true
\`\`\`

### Backend (.env)
\`\`\`env
SENTRY_DSN=${dsn}
ENVIRONMENT=${environment}
APP_VERSION=${version}
SENTRY_DEBUG=false
${webhookSecret ? `SENTRY_WEBHOOK_SECRET=${webhookSecret}` : ''}
\`\`\`

## Free Tier Optimizations

### Frontend
- **Traces Sample Rate:** 10% (only critical transactions)
- **Max Breadcrumbs:** 10 (reduced data usage)
- **Error Filtering:** Common browser errors ignored
- **Performance Events:** Non-critical routes filtered

### Backend
- **Traces Sample Rate:** 10% (only critical transactions)
- **Profiles Sample Rate:** 10% (only critical profiles)
- **Error Filtering:** Health checks and common errors ignored
- **Rate Limiting:** Max 10 events per minute

## Features

### Error Tracking
- JavaScript errors in frontend
- Python exceptions in backend
- User context tracking
- Performance monitoring

### Alerting
- Critical error notifications via Telegram
- Webhook integration for real-time alerts
- Admin notification system

### Performance Monitoring
- Transaction tracing
- Database query monitoring
- API endpoint performance
- User experience metrics

## Usage

### Frontend
\`\`\`javascript
import { captureException, captureMessage } from './config/sentry';

// Capture errors
try {
  // risky operation
} catch (error) {
  captureException(error, { tags: { component: 'JobSearch' } });
}

// Capture messages
captureMessage('User completed onboarding', 'info');
\`\`\`

### Backend
\`\`\`python
from backend.config.sentry import capture_exception, capture_message

# Capture exceptions
try:
    # risky operation
except Exception as e:
    capture_exception(e, {"context": "job_processing"})

# Capture messages
capture_message("Database backup completed", "info")
\`\`\`

## Monitoring Dashboard

1. Go to your Sentry dashboard
2. Check the "Issues" tab for errors
3. Check the "Performance" tab for slow transactions
4. Set up alerts for critical errors

## Webhook Configuration

1. In your Sentry project settings
2. Go to "Alerts" → "Rules"
3. Create a rule for critical errors
4. Add webhook URL: \`https://your-domain.com/webhook/sentry/alert\`
5. Set webhook secret if configured

## Best Practices

1. **Don't log everything:** Only capture meaningful errors
2. **Use tags:** Add context to errors for better debugging
3. **Monitor usage:** Check Sentry dashboard for quota usage
4. **Filter noise:** Configure error filtering to avoid spam
5. **Set up alerts:** Configure notifications for critical issues

## Troubleshooting

### Common Issues
- **High event volume:** Reduce sample rates or add more filters
- **Missing context:** Ensure user context is set properly
- **Webhook failures:** Check webhook secret and URL configuration

### Support
- Check Sentry documentation: https://docs.sentry.io/
- Review free tier limits: https://sentry.io/pricing/
- Contact Sentry support for account issues
`;
    
    fs.writeFileSync(guidePath, guideContent);
    console.log('✅ Sentry setup guide created');
    
    console.log('\n🎉 Sentry setup completed successfully!');
    console.log('\n📋 Next steps:');
    console.log('1. Restart your frontend and backend servers');
    console.log('2. Check the Sentry dashboard for events');
    console.log('3. Configure alerts in your Sentry project');
    console.log('4. Review the setup guide: docs/SENTRY_SETUP_GUIDE.md');
    
  } catch (error) {
    console.error('❌ Setup failed:', error.message);
    process.exit(1);
  } finally {
    rl.close();
  }
}

// Run setup
setupSentry(); 