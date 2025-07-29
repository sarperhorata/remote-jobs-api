# 🚀 BUZZ2REMOTE - AI-Powered Remote Job Platform

[![Production Status](https://img.shields.io/badge/status-production-green)](https://buzz2remote.com)
[![API Status](https://img.shields.io/badge/api-operational-green)](https://remote-jobs-api-k9v1.onrender.com/health)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub Actions](https://github.com/sarperhorata/remote-jobs-api/workflows/Auto%20Deploy%20on%20Success/badge.svg)](https://github.com/sarperhorata/remote-jobs-api/actions)

## 📁 **PROJECT STRUCTURE**

This project has a well-organized folder structure. For detailed information, see the [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) file.

### 🏗️ Main Folders
- **`/backend/`** - FastAPI-based REST API
- **`/frontend/`** - React-based web application
- **`/scripts/`** - Automation scripts (cron, deployment, testing)
- **`/reports/`** - Project reports and analyses
- **`/docs/`** - Technical documentation
- **`/config/`** - Configuration files

### 🚀 Quick Start
```bash
# Backend development
cd backend && python -m pytest tests/

# Frontend development
cd frontend && npm run dev

# Run tests
./scripts/testing/test_api_performance.sh
```

---

## 🌟 **OVERVIEW**

Buzz2Remote is a comprehensive AI-powered platform connecting remote workers with global opportunities. Built with modern technologies and optimized for performance, security, and scalability.

### **🎯 Key Features**
- 🔍 **Advanced Job Search** - MongoDB aggregation-powered search with 60-77ms response times
- 🤖 **AI-Powered Services** - CV analysis, job recommendations, and skills extraction
- 📄 **Smart Applications** - Auto-apply functionality with intelligent matching
- 🔒 **Enterprise Security** - Rate limiting, input validation, and comprehensive audit logging
- 🗄️ **Automated Backups** - Daily incremental and weekly full database backups
- 📊 **Performance Monitoring** - Real-time metrics and health monitoring
- 🌐 **Global CDN** - Optimized content delivery with lazy loading and bundle splitting

---

## 🛠️ **TECH STACK**

### **Frontend**
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with responsive design
- **State Management**: React Query + Context API
- **Build Tool**: Webpack with custom optimizations
- **Performance**: Lazy loading, code splitting (39 chunks), 86KB gzipped bundle
- **Hosting**: Netlify with edge CDN

### **Backend**
- **Framework**: FastAPI with Python 3.11
- **Database**: MongoDB Atlas with optimized aggregation pipelines
- **Authentication**: JWT with refresh tokens
- **Security**: Rate limiting, CORS, security headers, input validation
- **Monitoring**: Sentry error tracking + custom health checks
- **Hosting**: Render with auto-scaling

### **Infrastructure**
- **Database**: MongoDB Atlas (Shared Cluster → Production)
- **Cron Jobs**: cron-job.org (7 automated tasks)
- **Notifications**: Telegram integration
- **CI/CD**: GitHub Actions with automated deployment
- **Monitoring**: Custom dashboards + Sentry integration

---

## 🚀 **LIVE DEPLOYMENT**

### **Production URLs**
- **Frontend**: https://buzz2remote.com
- **Backend API**: https://remote-jobs-api-k9v1.onrender.com
- **API Documentation**: https://remote-jobs-api-k9v1.onrender.com/docs
- **Health Check**: https://remote-jobs-api-k9v1.onrender.com/health

### **Performance Metrics**
```
🚀 Frontend Performance:
├── Bundle Size: 86KB gzipped (main)
├── Total Chunks: 39 (lazy loaded)
├── Load Time: ~1.2s average
└── Core Web Vitals: Optimized

⚡ Backend Performance:
├── API Response: 60-77ms average
├── Database Queries: 10-25ms average
├── Uptime: 99.9% target
└── Rate Limit: 1000 req/hour (authenticated)
```

---

## 📋 **FEATURES OVERVIEW**

### **🔍 Job Search & Discovery**
- **Advanced Filtering**: Location, salary, remote work, job type, experience level
- **AI-Powered Search**: Semantic search with relevance scoring
- **Real-time Results**: MongoDB aggregation with field projection
- **Autocomplete**: Intelligent job title and location suggestions

### **🤖 AI Services**
- **CV Analysis**: Extract skills, experience, and provide optimization suggestions
- **Job Recommendations**: Personalized matching based on profile and preferences
- **Skills Extraction**: Automatically detect skills from text input
- **Salary Estimation**: AI-powered salary range predictions

### **👤 User Management**
- **Profile Management**: Comprehensive user profiles with skills tracking
- **Application Tracking**: Monitor application status and history
- **Auto-Apply**: Intelligent bulk application system with customizable criteria
- **Notifications**: Real-time updates via email and in-app notifications

### **🔒 Security & Reliability**
- **Authentication**: JWT-based with refresh token rotation
- **Rate Limiting**: IP and user-based limits with burst protection
- **Input Validation**: XSS, SQL injection, and CSRF protection
- **Security Headers**: CSP, HSTS, frame protection
- **Audit Logging**: Comprehensive security event tracking

### **🗄️ Data Management**
- **Automated Backups**: Daily incremental + weekly full backups
- **Data Recovery**: Point-in-time restore capabilities
- **Database Optimization**: Indexed collections with aggregation pipelines
- **Data Retention**: Automated cleanup of expired data

---

## ⚙️ **INSTALLATION & SETUP**

### **Prerequisites**
- Node.js 18+
- Python 3.11+
- MongoDB Atlas account
- Git

### **Quick Start**

#### **1. Clone Repository**
```bash
git clone https://github.com/sarperhorata/remote-jobs-api.git
cd remote-jobs-api
```

#### **2. Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with your configuration

# Start backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### **3. Frontend Setup**
```bash
cd frontend
npm install

# Environment setup
cp .env.example .env.local
# Edit .env.local with your configuration

# Start frontend
npm start
```

#### **4. Access Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

---

## 📡 **API DOCUMENTATION**

### **Core Endpoints**
```bash
# Health Check
GET /health

# Job Search
GET /api/v1/jobs/?q=frontend&location=remote&limit=20

# User Authentication
POST /api/v1/auth/login
POST /api/v1/auth/register

# AI Services
POST /api/v1/ai-cv-analysis/analyze
GET /api/v1/ai/recommendations

# Database Backup
POST /api/v1/backup/create/full
GET /api/v1/backup/status
```

### **Authentication**
```bash
# API Key (for internal services)
curl -H "X-API-Key: your-api-key" https://api.example.com/endpoint

# JWT Bearer Token (for user endpoints)
curl -H "Authorization: Bearer your-jwt-token" https://api.example.com/endpoint
```

**Full API Documentation**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## 🚀 **DEPLOYMENT**

### **Production Deployment**
The application is automatically deployed via GitHub Actions:

```bash
# Push to main triggers deployment
git push origin main

# Manual deployment commands
cd frontend && npm run build:production
cd backend && python scripts/deploy.py
```

### **Environment Variables**
```bash
# Backend (.env)
MONGODB_URL=mongodb+srv://...
JWT_SECRET=your-secret-key
OPENAI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=...

# Frontend (.env.local)
REACT_APP_API_URL=https://your-api-url
REACT_APP_STRIPE_PUBLIC_KEY=pk_...
```

**Complete Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

---

## 🔧 **DEVELOPMENT**

### **Development Workflow**
```bash
# Start development servers
npm run dev:backend   # Backend on :8001
npm run dev:frontend  # Frontend on :3000

# Run tests
npm run test:backend  # Python tests
npm run test:frontend # React tests
npm run test:e2e      # Cypress E2E tests

# Code quality
npm run lint          # ESLint + Pylint
npm run format        # Prettier + Black
npm run type-check    # TypeScript + mypy
```

### **Testing Strategy**
```bash
Backend Tests:
├── Unit Tests (pytest): 87% coverage
├── Integration Tests: API endpoints
├── Security Tests: Input validation
└── Performance Tests: Database queries

Frontend Tests:
├── Unit Tests (Jest): 85% coverage
├── Component Tests (React Testing Library)
├── E2E Tests (Cypress): Critical user flows
└── Visual Regression Tests
```

---

## 📊 **MONITORING & ANALYTICS**

### **System Health**
- **Uptime Monitoring**: Automated health checks every 10 minutes
- **Performance Metrics**: Response time, error rates, database performance
- **Error Tracking**: Sentry integration for real-time error monitoring
- **Business Metrics**: User engagement, job application success rates

### **Automated Maintenance**
```bash
Cron Jobs (via cron-job.org):
├── Database Cleanup: Daily at 1:00 AM UTC
├── External API Sync: Every 6 hours
├── Job Statistics: Daily at 3:00 AM UTC
├── Database Backup: Daily at 2:00 AM UTC
├── Keep-Alive Ping: Every 10 minutes
├── Status Monitor: Every hour
└── Test Timeout: Every 30 minutes
```

---

## 🔒 **SECURITY**

### **Security Measures**
- **Input Validation**: XSS, SQL injection, command injection protection
- **Rate Limiting**: IP-based and user-based limits
- **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
- **Authentication**: JWT with refresh token rotation
- **Data Encryption**: At rest and in transit
- **Audit Logging**: Comprehensive security event tracking

### **Compliance**
- **GDPR**: Data protection and user rights
- **OWASP**: Security best practices implementation
- **API Security**: Rate limiting, input validation, output encoding

---

## 📈 **PERFORMANCE OPTIMIZATIONS**

### **Frontend Optimizations**
```bash
✅ Bundle Splitting: 39 chunks with vendor separation
✅ Lazy Loading: Route and component-based
✅ Image Optimization: WebP conversion and compression
✅ Caching Strategy: Service worker implementation
✅ Tree Shaking: Dead code elimination
✅ Compression: Gzip enabled (86KB main bundle)
```

### **Backend Optimizations**
```bash
✅ Database Indexing: Optimized query performance
✅ Aggregation Pipelines: 60-77ms response times
✅ Connection Pooling: Efficient database connections
✅ Response Caching: Popular endpoint caching
✅ Compression: Gzip middleware
✅ Security Middleware: Optimized for performance
```

---

## 🤝 **CONTRIBUTING**

### **Development Setup**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Code Standards**
- **Backend**: Black formatting, type hints, comprehensive tests
- **Frontend**: ESLint + Prettier, TypeScript strict mode
- **Documentation**: Keep README and docs updated
- **Testing**: Maintain test coverage above 80%

---

## 📝 **CHANGELOG**

### **v1.0.0 (2025-01-27) - Current Production**
- ✅ Complete production deployment on Netlify + Render
- ✅ AI-powered job search and recommendations
- ✅ Automated backup system with Telegram notifications
- ✅ Performance optimizations (60-77ms API, 86KB bundle)
- ✅ Security enhancements and audit compliance
- ✅ Comprehensive monitoring and alerting
- ✅ CI/CD pipeline with GitHub Actions

### **Previous Versions**
- **v0.9.0**: Beta testing phase
- **v0.8.0**: Frontend optimization implementation
- **v0.7.0**: AI services integration
- **v0.6.0**: Security audit and hardening

---

## 📞 **SUPPORT & CONTACT**

### **Getting Help**
- **Documentation**: Check [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/sarperhorata/remote-jobs-api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sarperhorata/remote-jobs-api/discussions)

### **Project Links**
- **Live App**: https://buzz2remote.com
- **API**: https://remote-jobs-api-k9v1.onrender.com
- **Status**: https://remote-jobs-api-k9v1.onrender.com/health
- **Repository**: https://github.com/sarperhorata/remote-jobs-api

---

## 📄 **LICENSE**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **ACKNOWLEDGMENTS**

- **MongoDB Atlas** for reliable database hosting
- **Netlify** and **Render** for deployment platforms
- **OpenAI** for AI service integration
- **Sentry** for error monitoring
- **React** and **FastAPI** communities for excellent frameworks

---

*Built with ❤️ for the remote work community*
