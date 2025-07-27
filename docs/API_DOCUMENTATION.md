# 📚 BUZZ2REMOTE API DOCUMENTATION

## 🌐 **Base URLs**
- **Production**: `https://remote-jobs-api-k9v1.onrender.com`
- **Frontend**: `https://buzz2remote.com`

## 🔐 **Authentication**

### API Key Authentication
Most endpoints require API key authentication:
```
X-API-Key: your_api_key_here
```

### Rate Limiting
- **Public endpoints**: 100 requests/hour per IP
- **Authenticated endpoints**: 1000 requests/hour per API key
- **Premium users**: 5000 requests/hour per API key

---

## 📋 **CORE ENDPOINTS**

### **Health Check**
```http
GET /health
```
**Response:**
```json
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

---

## 🔍 **JOB ENDPOINTS**

### **Get Jobs**
```http
GET /api/v1/jobs/?page={page}&limit={limit}&location={location}&remote={remote}
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Jobs per page (max: 100, default: 20)
- `location` (string): Filter by location
- `remote` (boolean): Filter remote jobs
- `salary_min` (int): Minimum salary filter
- `salary_max` (int): Maximum salary filter
- `job_type` (string): full-time, part-time, contract, freelance
- `sort_by` (string): newest, oldest, relevance

**Response:**
```json
{
  "jobs": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Senior Frontend Developer",
      "company": "TechCorp",
      "location": "Remote",
      "salary_min": 80000,
      "salary_max": 120000,
      "posted_date": "2025-01-27",
      "remote": true,
      "job_type": "full-time",
      "required_skills": ["React", "TypeScript", "Node.js"],
      "apply_url": "https://example.com/apply"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1234,
    "total_pages": 62,
    "has_next": true,
    "has_prev": false
  }
}
```

### **Search Jobs**
```http
GET /api/v1/jobs/search?q={query}&location={location}&remote={remote}
```

**Advanced Search Parameters:**
- `q` (string): Search query (title, company, description)
- `skills` (array): Required skills filter
- `experience_level` (string): junior, mid, senior, lead
- `company_size` (string): startup, small, medium, large
- `industry` (string): tech, finance, healthcare, etc.

### **Get Job by ID**
```http
GET /api/v1/jobs/{job_id}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Senior Frontend Developer",
  "company": "TechCorp",
  "description": "Full job description...",
  "requirements": ["3+ years React", "TypeScript experience"],
  "benefits": ["Health insurance", "Remote work"],
  "location": "Remote",
  "salary_range": "$80,000 - $120,000",
  "posted_date": "2025-01-27",
  "application_deadline": "2025-02-27",
  "remote": true,
  "job_type": "full-time",
  "seniority_level": "senior",
  "apply_url": "https://example.com/apply",
  "company_info": {
    "name": "TechCorp",
    "size": "201-500",
    "industry": "Technology",
    "website": "https://techcorp.com"
  }
}
```

---

## 🏢 **COMPANY ENDPOINTS**

### **Get Companies**
```http
GET /api/v1/companies/?page={page}&limit={limit}
```

### **Get Company Details**
```http
GET /api/v1/companies/{company_id}
```

### **Get Jobs by Company**
```http
GET /api/v1/companies/{company_id}/jobs
```

---

## 👤 **USER & AUTH ENDPOINTS**

### **Register User**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe",
  "agreed_to_terms": true
}
```

### **Login**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe",
    "profile_completed": false
  }
}
```

### **Get User Profile**
```http
GET /api/v1/profile/
Authorization: Bearer {access_token}
```

### **Update Profile**
```http
PUT /api/v1/profile/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "John Doe",
  "location": "San Francisco, CA",
  "skills": ["React", "Node.js", "Python"],
  "experience_years": 5,
  "bio": "Senior software engineer...",
  "linkedin_url": "https://linkedin.com/in/johndoe"
}
```

---

## 🤖 **AI SERVICES**

### **AI CV Analysis**
```http
POST /api/v1/ai-cv-analysis/analyze
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: [CV_FILE.pdf]
```

**Response:**
```json
{
  "analysis": {
    "skills": ["React", "Node.js", "Python"],
    "experience_years": 5,
    "education": [
      {
        "degree": "Bachelor of Computer Science",
        "institution": "University Name",
        "year": 2018
      }
    ],
    "strengths": ["Strong technical skills", "Leadership experience"],
    "suggestions": ["Add more quantified achievements"],
    "score": 85
  }
}
```

### **AI Job Recommendations**
```http
GET /api/v1/ai/recommendations
Authorization: Bearer {access_token}
```

### **Skills Extraction**
```http
POST /api/v1/skills-extraction/extract
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "text": "I have 5 years of experience with React, Node.js, and MongoDB..."
}
```

---

## 📄 **APPLICATION MANAGEMENT**

### **Apply to Job**
```http
POST /api/v1/applications/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "job_id": "507f1f77bcf86cd799439011",
  "cover_letter": "I am excited to apply...",
  "additional_info": "Available for immediate start"
}
```

### **Get My Applications**
```http
GET /api/v1/applications/
Authorization: Bearer {access_token}
```

### **Auto Apply Settings**
```http
POST /api/v1/auto-apply/settings
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "enabled": true,
  "criteria": {
    "keywords": ["React", "Frontend"],
    "locations": ["Remote", "San Francisco"],
    "salary_min": 80000,
    "job_types": ["full-time"]
  },
  "daily_limit": 5
}
```

---

## 🗄️ **DATABASE BACKUP ENDPOINTS**

### **Create Full Backup**
```http
POST /api/v1/backup/create/full
X-API-Key: {api_key}
```

**Response:**
```json
{
  "status": "success",
  "message": "Full backup completed successfully",
  "backup_id": "20250127_143022",
  "backup_info": {
    "total_documents": 45678,
    "total_size_mb": 234.5,
    "collections": {
      "jobs": {"document_count": 38345, "file_size_mb": 156.7},
      "users": {"document_count": 7333, "file_size_mb": 77.8}
    }
  }
}
```

### **Create Incremental Backup**
```http
POST /api/v1/backup/create/incremental?since_days=1
X-API-Key: {api_key}
```

### **List Backups**
```http
GET /api/v1/backup/list
X-API-Key: {api_key}
```

### **Restore Backup**
```http
POST /api/v1/backup/restore/{backup_id}
X-API-Key: {api_key}
Content-Type: application/json

{
  "collections": ["jobs", "users"]  // Optional: specific collections
}
```

### **Backup Status**
```http
GET /api/v1/backup/status
X-API-Key: {api_key}
```

**Response:**
```json
{
  "status": "success",
  "backup_system": {
    "health_status": "HEALTHY",
    "last_backup_age_hours": 2.5,
    "total_backups": 7,
    "total_backup_size_mb": 1640.5,
    "retention_policy": "7 backups"
  },
  "recent_backups": [...]
}
```

---

## 🔔 **NOTIFICATIONS**

### **Get Notifications**
```http
GET /api/v1/notifications/
Authorization: Bearer {access_token}
```

### **Mark as Read**
```http
PUT /api/v1/notifications/{notification_id}/read
Authorization: Bearer {access_token}
```

### **Notification Settings**
```http
PUT /api/v1/notifications/settings
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email_notifications": true,
  "job_alerts": true,
  "application_updates": true,
  "weekly_digest": false
}
```

---

## 💳 **PAYMENT & SUBSCRIPTIONS**

### **Get Subscription Plans**
```http
GET /api/v1/payment/plans
```

### **Create Subscription**
```http
POST /api/v1/payment/subscribe
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "plan_id": "premium_monthly",
  "payment_method": "pm_1234567890"
}
```

### **Get Subscription Status**
```http
GET /api/v1/payment/subscription
Authorization: Bearer {access_token}
```

---

## 📊 **ADMIN ENDPOINTS**

### **Admin Dashboard Stats**
```http
GET /admin/api/stats
X-API-Key: {admin_api_key}
```

### **User Management**
```http
GET /admin/api/users?page={page}&limit={limit}
X-API-Key: {admin_api_key}
```

### **Job Management**
```http
GET /admin/api/jobs/pending
X-API-Key: {admin_api_key}
```

```http
POST /admin/api/jobs/{job_id}/approve
X-API-Key: {admin_api_key}
```

---

## 🤖 **CRON JOB ENDPOINTS**

### **Database Cleanup**
```http
POST /api/v1/cronjobs/database-cleanup?api_key={api_key}
```

### **External API Crawler**
```http
POST /api/v1/cronjobs/external-api-crawler?api_key={api_key}
```

### **Job Statistics**
```http
POST /api/v1/cronjobs/job-statistics?api_key={api_key}
```

### **Cron Status Monitor**
```http
GET /api/v1/cronjobs/status?api_key={api_key}
```

---

## 📈 **MONITORING & ANALYTICS**

### **System Health**
```http
GET /api/v1/monitoring/health
```

### **Performance Metrics**
```http
GET /api/v1/monitoring/metrics?timeframe=24h
```

### **Error Logs**
```http
GET /api/v1/monitoring/errors?severity=high&limit=50
```

---

## ⚠️ **ERROR HANDLING**

### **Standard Error Response**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    },
    "error_id": "err_1234567890",
    "timestamp": "2025-01-27T12:00:00Z"
  }
}
```

### **Common HTTP Status Codes**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden  
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

---

## 🚀 **API PERFORMANCE**

### **Response Times**
- **Database queries**: 60-77ms average
- **Search endpoints**: 80-120ms average
- **AI services**: 1-3s average
- **File uploads**: Variable based on size

### **Rate Limits**
- **Burst protection**: 100 requests/minute
- **Daily limits**: Based on subscription tier
- **IP-based limits**: Anti-abuse protection

---

## 🔒 **SECURITY**

### **Headers**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: strict policy`

### **Input Validation**
- XSS protection
- SQL injection prevention
- CSRF token validation
- File upload restrictions

### **Data Protection**
- Encryption at rest
- TLS 1.3 in transit
- Personal data anonymization
- GDPR compliance

---

## 📝 **CHANGELOG**

### **v1.0.0 (2025-01-27)**
- ✅ Complete API redesign with MongoDB aggregation
- ✅ Advanced search and filtering
- ✅ AI-powered features
- ✅ Automated backup system
- ✅ Enhanced security headers
- ✅ Rate limiting implementation
- ✅ Comprehensive error handling
- ✅ Performance optimizations

---

## 🔗 **USEFUL LINKS**

- **API Base URL**: https://remote-jobs-api-k9v1.onrender.com
- **Frontend**: https://buzz2remote.com  
- **Status Page**: https://remote-jobs-api-k9v1.onrender.com/health
- **Admin Panel**: https://remote-jobs-api-k9v1.onrender.com/admin
- **GitHub**: https://github.com/sarperhorata/remote-jobs-api

---

## 📞 **SUPPORT**

For API support, please contact:
- **Email**: support@buzz2remote.com
- **GitHub Issues**: https://github.com/sarperhorata/remote-jobs-api/issues 