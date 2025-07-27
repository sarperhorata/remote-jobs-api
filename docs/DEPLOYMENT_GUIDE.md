# 🚀 BUZZ2REMOTE DEPLOYMENT GUIDE

## 📋 **DEPLOYMENT OVERVIEW**

### **Current Production Environment**
- **Frontend**: Netlify → `https://buzz2remote.com`
- **Backend**: Render → `https://remote-jobs-api-k9v1.onrender.com`
- **Database**: MongoDB Atlas (Shared Cluster)
- **CDN**: Netlify Edge Network
- **Monitoring**: Sentry + Custom Health Checks

---

## 🖥️ **BACKEND DEPLOYMENT (Render)**

### **Prerequisites**
- MongoDB Atlas connection string
- Environment variables configured
- GitHub repository access
- Render account with deployment permissions

### **Environment Variables**
```bash
# Database
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/buzz2remote

# Authentication
JWT_SECRET=your-super-secret-jwt-key-here
SESSION_SECRET=your-session-secret-here

# External APIs
OPENAI_API_KEY=sk-your-openai-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Email Service
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Payment (Stripe)
STRIPE_PUBLIC_KEY=pk_live_or_test_key
STRIPE_SECRET_KEY=sk_live_or_test_key
STRIPE_WEBHOOK_SECRET=whsec_webhook_secret

# Security
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
API_KEY=your-secure-api-key-for-cronjobs
ENCRYPTION_KEY=your-32-character-encryption-key

# Application
ENVIRONMENT=production
FRONTEND_URL=https://buzz2remote.com
BACKEND_URL=https://remote-jobs-api-k9v1.onrender.com

# Rate Limiting
REDIS_URL=redis://localhost:6379  # Optional for advanced rate limiting

# Backup
BACKUP_DIR=/opt/render/project/src/backups
MAX_LOCAL_BACKUPS=7
COMPRESSION_LEVEL=6
```

### **Deployment Steps**

#### **1. Render Configuration**
```yaml
# render.yaml
services:
  - type: web
    name: buzz2remote-api
    env: python
    plan: starter  # or standard/pro
    buildCommand: |
      cd backend
      pip install -r requirements.txt
    startCommand: |
      cd backend
      uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### **2. Build Commands**
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Database migrations (if needed)
python scripts/migrate_database.py

# Generate static files
python scripts/generate_static_files.py
```

#### **3. Start Command**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 65
```

#### **4. Health Check Configuration**
```python
# Health check endpoint: GET /health
{
  "status": "healthy",
  "timestamp": "2025-01-27T12:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "mongodb": "healthy",
    "external_apis": "healthy"
  }
}
```

### **Production Optimizations**

#### **Performance Settings**
```python
# main.py optimizations
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://buzz2remote.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

#### **Security Headers**
```python
# Implemented via security_headers.py middleware
headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY", 
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}
```

---

## 🌐 **FRONTEND DEPLOYMENT (Netlify)**

### **Prerequisites**
- Node.js 18+ installed
- Netlify account and CLI
- GitHub repository access
- Environment variables configured

### **Environment Variables (.env.production)**
```bash
# API Configuration
REACT_APP_API_URL=https://remote-jobs-api-k9v1.onrender.com
REACT_APP_FRONTEND_URL=https://buzz2remote.com

# Analytics
REACT_APP_GA_TRACKING_ID=G-XXXXXXXXXX
REACT_APP_SENTRY_DSN=https://your-frontend-sentry-dsn@sentry.io/project-id

# External Services
REACT_APP_STRIPE_PUBLIC_KEY=pk_live_or_test_key
REACT_APP_GOOGLE_CLIENT_ID=your-google-oauth-client-id

# Feature Flags
REACT_APP_ENABLE_AI_FEATURES=true
REACT_APP_ENABLE_AUTO_APPLY=true
REACT_APP_ENABLE_ANALYTICS=true

# Performance
REACT_APP_BUNDLE_ANALYZER=false
REACT_APP_CACHE_VERSION=v1.0.0
```

### **Build Configuration**

#### **package.json Scripts**
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "build:production": "NODE_ENV=production react-scripts build",
    "build:analyze": "ANALYZE=true react-scripts build",
    "test": "react-scripts test",
    "test:coverage": "react-scripts test --coverage --silent --watchAll=false",
    "deploy": "netlify deploy --prod --dir=build"
  }
}
```

#### **Netlify Configuration (netlify.toml)**
```toml
[build]
  base = "frontend/"
  publish = "build/"
  command = "npm run build:production"

[build.environment]
  NODE_VERSION = "18"
  NPM_VERSION = "9"

[[redirects]]
  from = "/api/*"
  to = "https://remote-jobs-api-k9v1.onrender.com/api/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Strict-Transport-Security = "max-age=31536000; includeSubDomains"

[[headers]]
  for = "/static/js/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/static/css/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/static/media/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

### **Deployment Steps**

#### **1. Automated Deployment (GitHub Integration)**
```bash
# Push to main branch triggers deployment
git push origin main

# Manual deployment via Netlify CLI
cd frontend
npm run build:production
netlify deploy --prod --dir=build
```

#### **2. Performance Optimizations**

**Webpack Bundle Optimization:**
```javascript
// webpack.config.js (implemented)
const config = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
        },
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: 'react',
          priority: 20,
        }
      }
    }
  }
};
```

**Lazy Loading Implementation:**
```typescript
// Implemented in src/utils/bundleOptimization.ts
const LazyJobDetails = lazy(() => import('./pages/JobDetails'));
const LazyUserProfile = lazy(() => import('./pages/UserProfile'));
```

#### **3. Build Verification**
```bash
# Check build size
npm run build:analyze

# Test production build locally
npx serve -s build -l 3000

# Performance audit
npm run lighthouse
```

---

## 🗄️ **DATABASE DEPLOYMENT (MongoDB Atlas)**

### **Configuration**
```javascript
// Connection settings
{
  "connectionString": "mongodb+srv://username:password@cluster.mongodb.net/buzz2remote",
  "options": {
    "maxPoolSize": 10,
    "serverSelectionTimeoutMS": 5000,
    "socketTimeoutMS": 45000,
    "bufferMaxEntries": 0,
    "retryWrites": true,
    "w": "majority"
  }
}
```

### **Indexes for Performance**
```javascript
// jobs collection indexes
db.jobs.createIndex({ "title": "text", "description": "text", "company": "text" })
db.jobs.createIndex({ "location": 1, "remote": 1 })
db.jobs.createIndex({ "created_at": -1 })
db.jobs.createIndex({ "salary_min": 1, "salary_max": 1 })
db.jobs.createIndex({ "job_type": 1, "seniority_level": 1 })

// users collection indexes
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "created_at": -1 })
db.users.createIndex({ "last_login": -1 })

// applications collection indexes
db.applications.createIndex({ "user_id": 1, "job_id": 1 }, { unique: true })
db.applications.createIndex({ "user_id": 1, "created_at": -1 })
db.applications.createIndex({ "status": 1 })
```

### **Backup Strategy**
```bash
# Automated daily backups via cron-job.org
# Full backup: Every Sunday at 2 AM UTC
# Incremental backup: Every day at 2 AM UTC (except Sunday)

# Manual backup via API
curl -X POST "https://remote-jobs-api-k9v1.onrender.com/api/v1/backup/create/full" \
  -H "X-API-Key: your-api-key"

# Backup status check
curl "https://remote-jobs-api-k9v1.onrender.com/api/v1/backup/status" \
  -H "X-API-Key: your-api-key"
```

---

## 🤖 **CRON JOBS DEPLOYMENT (cron-job.org)**

### **Configured Cron Jobs**
```bash
# 1. Database Cleanup - Daily at 1:00 AM UTC
URL: https://remote-jobs-api-k9v1.onrender.com/api/v1/cronjobs/database-cleanup?api_key=your-api-key
Schedule: 0 1 * * *

# 2. External API Crawler - Every 6 hours
URL: https://remote-jobs-api-k9v1.onrender.com/api/v1/cronjobs/external-api-crawler?api_key=your-api-key
Schedule: 0 */6 * * *

# 3. Job Statistics - Daily at 3:00 AM UTC
URL: https://remote-jobs-api-k9v1.onrender.com/api/v1/cronjobs/job-statistics?api_key=your-api-key
Schedule: 0 3 * * *

# 4. Database Backup - Daily at 2:00 AM UTC
URL: https://remote-jobs-api-k9v1.onrender.com/api/v1/backup/create/incremental?api_key=your-api-key
Schedule: 0 2 * * *

# 5. Keep Render Alive - Every 10 minutes
URL: https://remote-jobs-api-k9v1.onrender.com/health
Schedule: */10 * * * *

# 6. Cron Status Monitor - Every hour
URL: https://remote-jobs-api-k9v1.onrender.com/api/v1/cronjobs/status?api_key=your-api-key
Schedule: 0 * * * *

# 7. Test Timeout Prevention - Every 30 minutes
URL: https://remote-jobs-api-k9v1.onrender.com/api/v1/cronjobs/test-timeout?api_key=your-api-key
Schedule: */30 * * * *
```

---

## 📊 **MONITORING & LOGGING**

### **Health Monitoring**
```bash
# System health endpoint
curl https://remote-jobs-api-k9v1.onrender.com/health

# Application metrics
curl https://remote-jobs-api-k9v1.onrender.com/api/v1/monitoring/metrics

# Error tracking via Sentry
# Frontend: https://sentry.io/organizations/buzz2remote/projects/frontend/
# Backend: https://sentry.io/organizations/buzz2remote/projects/backend/
```

### **Performance Metrics**
- **API Response Time**: 60-77ms average
- **Database Query Time**: 10-25ms average
- **Frontend Load Time**: 1.2s average
- **Bundle Size**: 86KB gzipped main bundle

### **Alerting**
```python
# Telegram notifications for critical events
# Configured via TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
# Alerts for:
# - System downtime
# - Database backup failures
# - High error rates
# - Performance degradation
```

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues**

#### **Backend Issues**
```bash
# Error: "Could not import module 'main'"
# Solution: Ensure working directory is /backend
cd backend && uvicorn main:app --host 0.0.0.0 --port 8001

# Error: "ModuleNotFoundError"
# Solution: Install dependencies
pip install -r requirements.txt

# Error: "Database connection failed"
# Solution: Check MONGODB_URL environment variable
python -c "import os; print(os.getenv('MONGODB_URL'))"
```

#### **Frontend Issues**
```bash
# Error: Build fails with memory issues
# Solution: Increase Node.js memory
NODE_OPTIONS="--max-old-space-size=4096" npm run build

# Error: API calls fail in production
# Solution: Check REACT_APP_API_URL environment variable
echo $REACT_APP_API_URL

# Error: Bundle size too large
# Solution: Analyze and optimize
npm run build:analyze
```

#### **Deployment Issues**
```bash
# Render deployment timeout
# Solution: Optimize build process and reduce dependencies

# Netlify build fails
# Solution: Check Node.js version and clear cache
netlify env:list
netlify build --context production
```

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment**
- [ ] Run all tests locally
- [ ] Check environment variables
- [ ] Verify database connections
- [ ] Test API endpoints
- [ ] Build frontend successfully
- [ ] Check bundle size
- [ ] Verify security headers
- [ ] Test backup system

### **Post-Deployment**
- [ ] Verify health endpoints
- [ ] Test critical user flows
- [ ] Check monitoring dashboards
- [ ] Verify cron jobs are running
- [ ] Test backup/restore functionality
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify SSL certificates

### **Rollback Plan**
```bash
# Backend rollback via Render
# 1. Go to Render dashboard
# 2. Select previous deployment
# 3. Redeploy previous version

# Frontend rollback via Netlify
netlify rollback

# Database rollback via backup
curl -X POST "https://remote-jobs-api-k9v1.onrender.com/api/v1/backup/restore/backup_id" \
  -H "X-API-Key: your-api-key"
```

---

## 📞 **SUPPORT & MAINTENANCE**

### **Regular Maintenance Tasks**
- **Weekly**: Review monitoring dashboards
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Performance optimization review
- **Yearly**: Architecture review and scaling planning

### **Contact Information**
- **Technical Issues**: Create GitHub issue
- **Deployment Support**: Check deployment logs
- **Emergency Contact**: Telegram notifications configured

---

## 📝 **VERSION HISTORY**

### **v1.0.0 (2025-01-27) - Current**
- ✅ Production-ready deployment
- ✅ Automated backup system
- ✅ Performance optimizations
- ✅ Security enhancements
- ✅ Comprehensive monitoring
- ✅ CI/CD pipeline with GitHub Actions 