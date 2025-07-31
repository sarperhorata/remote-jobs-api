# 🔗 Cron-job.org Kurulum Rehberi

Bu rehber, deployment monitoring sistemini cron-job.org üzerinde nasıl kuracağınızı açıklar.

## 📋 Gereksinimler

1. **Cron-job.org hesabı** (ücretsiz)
2. **Render API Key**
3. **GitHub Token**
4. **Netlify Access Token** (opsiyonel)

## 🛠️ Kurulum Adımları

### 1. Cron-job.org'da Hesap Oluşturma

1. [cron-job.org](https://cron-job.org) adresine gidin
2. "Sign up" ile ücretsiz hesap oluşturun
3. Email doğrulamasını tamamlayın

### 2. Yeni Cron Job Oluşturma

1. Dashboard'da "CREATE CRONJOB" butonuna tıklayın
2. Aşağıdaki ayarları yapın:

#### 🔧 Temel Ayarlar
```
Title: Buzz2Remote Deployment Monitor
URL: https://buzz2remote.onrender.com/api/monitor/check
Method: POST
```

#### ⏰ Zamanlama
```
Schedule: Every 15 minutes
Timezone: UTC
```

#### 📝 Headers
```
Content-Type: application/json
Authorization: Bearer YOUR_MONITOR_TOKEN
```

#### 📄 Body (JSON)
```json
{
  "action": "check",
  "timestamp": "{{timestamp}}",
  "source": "cron-job.org"
}
```

### 3. API Endpoint Oluşturma

Backend'e monitoring endpoint'i ekleyelim:

```python
# backend/routes/monitor.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os

router = APIRouter(prefix="/api/monitor", tags=["monitoring"])

class MonitorRequest(BaseModel):
    action: str
    timestamp: str
    source: str

@router.post("/check")
async def check_deployments(request: MonitorRequest):
    """External monitoring endpoint for cron-job.org"""
    
    # Validate request
    if request.action != "check":
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Run monitoring check
    try:
        from scripts.deployment_monitor import DeploymentMonitoringSystem
        system = DeploymentMonitoringSystem()
        await system.performCheck()
        report = await system.generateReport()
        
        return {
            "status": "success",
            "issues_found": report["issuesFound"],
            "fixes_applied": report["fixesApplied"],
            "timestamp": report["timestamp"]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": request.timestamp
        }
```

### 4. Environment Variables Ayarlama

Render'da environment variables'ları ayarlayın:

```bash
# Render Dashboard > Your Service > Environment
RENDER_API_KEY=your_render_api_key
GITHUB_TOKEN=your_github_token
NETLIFY_ACCESS_TOKEN=your_netlify_token
NETLIFY_SITE_ID=your_netlify_site_id
WEBHOOK_URL=your_webhook_url
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
MONITOR_TOKEN=your_secure_monitor_token
```

### 5. Test Etme

1. Cron job'ı manuel olarak çalıştırın
2. Logları kontrol edin: `https://buzz2remote.onrender.com/api/monitor/logs`
3. Dashboard'ı kontrol edin: `https://buzz2remote.onrender.com/api/monitor/dashboard`

## 🔧 Alternatif Cron Servisleri

### 1. EasyCron
```
URL: https://buzz2remote.onrender.com/api/monitor/check
Method: POST
Schedule: Every 15 minutes
```

### 2. SetCronJob
```
URL: https://buzz2remote.onrender.com/api/monitor/check
Method: POST
Schedule: */15 * * * *
```

### 3. GitHub Actions (Alternatif)
```yaml
# .github/workflows/monitor.yml
name: Deployment Monitor
on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm install
      - run: node scripts/deployment-monitor-cron.js --once
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NETLIFY_ACCESS_TOKEN: ${{ secrets.NETLIFY_ACCESS_TOKEN }}
```

## 📊 Monitoring Dashboard

### Webhook Entegrasyonu

Slack, Discord veya Telegram'a bildirim göndermek için:

```javascript
// Webhook URL örnekleri
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
TELEGRAM_BOT=https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage
```

### Notification Format

```json
{
  "text": "🚨 Critical deployment issue detected",
  "severity": "critical",
  "timestamp": "2025-07-31T08:48:00.484Z",
  "environment": "production",
  "issues": [
    {
      "platform": "Render",
      "message": "Service suspended",
      "severity": "critical"
    }
  ]
}
```

## 🔒 Güvenlik

### API Token Güvenliği
```bash
# Güçlü token oluştur
openssl rand -hex 32

# Environment variable olarak ayarla
MONITOR_TOKEN=your_generated_token
```

### Rate Limiting
```python
# Backend'de rate limiting ekle
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/check")
@limiter.limit("10/minute")  # 10 request per minute
async def check_deployments(request: MonitorRequest):
    # ... monitoring logic
```

## 📈 Monitoring Metrics

### Cron-job.org Dashboard'da Görünen Metrikler
- **Success Rate**: Başarılı kontroller
- **Response Time**: Yanıt süreleri
- **Error Rate**: Hata oranları
- **Uptime**: Servis erişilebilirliği

### Custom Metrics
```json
{
  "deployment_health": 95.5,
  "issues_detected": 2,
  "auto_fixes_applied": 1,
  "last_check": "2025-07-31T08:48:00.484Z",
  "uptime": "99.9%"
}
```

## 🐛 Troubleshooting

### Yaygın Sorunlar

#### 1. Timeout Errors
```
Error: Request timeout after 10 seconds
Solution: Increase timeout in cron-job.org settings
```

#### 2. Authentication Errors
```
Error: 401 Unauthorized
Solution: Check MONITOR_TOKEN in environment variables
```

#### 3. Rate Limiting
```
Error: 429 Too Many Requests
Solution: Reduce cron frequency or implement rate limiting
```

### Debug Komutları
```bash
# Manual test
curl -X POST https://buzz2remote.onrender.com/api/monitor/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"action":"check","timestamp":"2025-07-31T08:48:00.484Z","source":"test"}'

# Check logs
curl https://buzz2remote.onrender.com/api/monitor/logs

# Check status
curl https://buzz2remote.onrender.com/api/monitor/status
```

## 📞 Support

### Cron-job.org Support
- [Documentation](https://cron-job.org/en/help/)
- [FAQ](https://cron-job.org/en/faq/)
- [Contact](https://cron-job.org/en/contact/)

### Monitoring System Support
- Logs: `https://buzz2remote.onrender.com/api/monitor/logs`
- Dashboard: `https://buzz2remote.onrender.com/api/monitor/dashboard`
- Health Check: `https://buzz2remote.onrender.com/api/monitor/health`

Bu kurulum sayesinde deployment monitoring sisteminiz hem Render'da hem de external cron servislerinde çalışacak! 🚀 