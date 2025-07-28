# Render Environment Variables

## Required Environment Variables for Render Deployment

### Database Configuration
```
MONGODB_URI=mongodb+srv://your-mongodb-connection-string
```

### Telegram Bot Configuration
```
TELEGRAM_BOT_TOKEN=8116251711:AAFhGxXtOJu2eCqCORoDr46XWq7ejqMeYnY
TELEGRAM_CHAT_ID=-1002424698891
```

### Cron Job Security
```
CRON_SECRET_TOKEN=buzz2remote_cron_2024
```

### Application Configuration
```
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Optional (if using)
```
SENTRY_DSN=https://e307d92640eb7e8b60a7ebabf76db882@o4509547047616512.ingest.us.sentry.io/4509547146575872
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
```

## How to Add in Render Dashboard

1. Go to https://dashboard.render.com
2. Select your backend service
3. Go to "Environment" tab
4. Add each variable with its value
5. Redeploy the service

## Test Commands After Deployment

```bash
# Test health endpoint
curl "https://buzz2remote-api.onrender.com/api/v1/cron/health"

# Test cron endpoints (with token)
curl -X POST "https://buzz2remote-api.onrender.com/api/v1/cron/database-cleanup?token=buzz2remote_cron_2024"

# Test all endpoints
curl "https://buzz2remote-api.onrender.com/api/v1/cron/test-endpoints"
``` 