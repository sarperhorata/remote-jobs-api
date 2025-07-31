# 🚀 Deployment Monitoring & Auto-Fix System

Buzz2Remote için kapsamlı deployment monitoring ve otomatik hata düzeltme sistemi.

## 📋 Özellikler

### 🔍 Monitoring
- **Render Deployments**: Backend deployment durumu kontrolü
- **GitHub Actions**: Workflow başarısızlıklarını tespit etme
- **Netlify Deployments**: Frontend deployment durumu kontrolü
- **Local Services**: Backend (8001) ve Frontend (3002) port kontrolü

### 🔧 Auto-Fix
- **Render**: Failed deployment'ları otomatik retry
- **GitHub Actions**: Failed workflow'ları otomatik retry
- **Netlify**: Failed deployment'ları otomatik retry
- **Local Services**: Durdurulan servisleri otomatik başlatma

### 📊 Dashboard
- Real-time monitoring durumu
- Son loglar
- Detaylı raporlar
- Hızlı aksiyon butonları

## 🛠️ Kurulum

### 1. Otomatik Kurulum
```bash
# Root yetkisi ile çalıştırın
sudo npm run setup:monitor
```

### 2. Manuel Kurulum
```bash
# Dependencies yükle
npm install

# Environment dosyasını oluştur
cp .env.monitor .env
# .env dosyasını düzenle ve API key'leri ekle

# Cron job ekle
crontab -e
# Aşağıdaki satırı ekle:
# */15 * * * * cd /path/to/buzz2remote && source .env 2>/dev/null; node scripts/deployment-monitor-cron.js --once >> logs/cron.log 2>&1
```

## 🔧 Konfigürasyon

### Environment Variables (.env)
```bash
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
```

### API Key'leri Nasıl Alınır

#### Render API Key
1. Render Dashboard'a git
2. Account Settings > API Keys
3. "New API Key" oluştur
4. Service ID'yi service sayfasından al

#### Netlify Access Token
1. Netlify Dashboard'a git
2. User Settings > Applications > Personal access tokens
3. "New access token" oluştur
4. Site ID'yi site settings'den al

#### GitHub Token
1. GitHub Settings > Developer settings > Personal access tokens
2. "Generate new token" > "Fine-grained tokens"
3. Repository access: "Only select repositories" > "sarperhorata/remote-jobs-api"
4. Permissions: "Actions" > "Read and write"

## 📊 Kullanım

### Monitoring Komutları
```bash
# Tek seferlik kontrol
npm run monitor:once

# Sürekli monitoring (development)
npm run monitor

# Dashboard görüntüle
npm run monitor:dashboard

# Rapor oluştur
npm run monitor:report
```

### Systemd Service
```bash
# Service başlat
sudo systemctl start buzz2remote-monitor

# Service durdur
sudo systemctl stop buzz2remote-monitor

# Service durumu
sudo systemctl status buzz2remote-monitor

# Service logları
sudo journalctl -u buzz2remote-monitor -f
```

### Cron Job
```bash
# Cron job listesi
crontab -l

# Cron job düzenle
crontab -e

# Cron logları
tail -f logs/cron.log
```

## 📈 Dashboard

Dashboard şu bilgileri gösterir:
- Monitor service durumu
- Son 20 log satırı
- En son rapor
- Cron job durumu
- Local service durumları
- Hızlı aksiyon komutları

## 🔍 Monitoring Detayları

### Render Monitoring
- Service durumu kontrolü (running, failed, suspended)
- Son deployment durumu
- Error mesajları
- Otomatik retry mekanizması

### GitHub Actions Monitoring
- Son 5 workflow run'ı kontrolü
- Failed workflow'ları tespit etme
- Otomatik retry mekanizması
- Branch ve commit bilgileri

### Netlify Monitoring
- Son 5 deployment kontrolü
- Failed deployment'ları tespit etme
- Otomatik retry mekanizması
- Branch bilgileri

### Local Service Monitoring
- Backend port 8001 kontrolü
- Frontend port 3002 kontrolü
- Otomatik service başlatma
- Process durumu kontrolü

## 🔧 Auto-Fix Mekanizmaları

### Render Auto-Fix
```javascript
// Failed deployment retry
await axios.post(`https://api.render.com/v1/services/${serviceId}/deploys`);

// Service unsuspend
await axios.patch(`https://api.render.com/v1/services/${serviceId}`, { suspend: false });
```

### GitHub Actions Auto-Fix
```javascript
// Failed workflow retry
await axios.post(`https://api.github.com/repos/${repo}/actions/runs/${workflowId}/rerun`);
```

### Netlify Auto-Fix
```javascript
// Failed deployment retry
await axios.post(`https://api.netlify.com/api/v1/sites/${siteId}/deploys`);
```

### Local Service Auto-Fix
```bash
# Backend başlat
cd backend && python main.py &

# Frontend başlat
cd frontend && npm start &
```

## 📊 Raporlama

### JSON Report Format
```json
{
  "timestamp": "2025-07-31T08:48:00.484Z",
  "lastCheck": "2025-07-31T08:48:00.484Z",
  "issuesFound": 2,
  "fixesApplied": 1,
  "issues": [
    {
      "platform": "Render",
      "type": "deployment_failed",
      "message": "Render deployment failed: Build timeout",
      "severity": "high"
    }
  ],
  "fixes": [
    "render_deployment_retry"
  ]
}
```

### Log Format
```
[2025-07-31T08:48:00.408Z] [INFO] 🔍 Starting deployment health check...
[2025-07-31T08:48:00.411Z] [WARN] Render API key not configured, skipping Render check
[2025-07-31T08:48:00.484Z] [INFO] ✅ All deployments are healthy!
```

## 🚨 Alert Sistemi

### Severity Levels
- **Critical**: Service suspended, complete failure
- **High**: Deployment failed, workflow failed
- **Medium**: API errors, configuration issues
- **Low**: Warnings, non-critical issues

### Notification Channels
- Log files
- Console output
- JSON reports
- Systemd journal

## 🔒 Güvenlik

### API Key Güvenliği
- Environment variables kullanımı
- .env dosyası .gitignore'da
- Minimum gerekli permissions
- Token rotation önerisi

### Access Control
- Root yetkisi sadece kurulum için
- Service user isolation
- Read-only API access mümkün olduğunca

## 🐛 Troubleshooting

### Yaygın Sorunlar

#### Monitor Service Başlamıyor
```bash
# Service durumu kontrol et
sudo systemctl status buzz2remote-monitor

# Logları kontrol et
sudo journalctl -u buzz2remote-monitor -f

# Environment variables kontrol et
cat .env
```

#### API Key Hataları
```bash
# API key'leri test et
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.render.com/v1/services/YOUR_SERVICE_ID
```

#### Cron Job Çalışmıyor
```bash
# Cron job listesi
crontab -l

# Cron logları
tail -f logs/cron.log

# Manual test
npm run monitor:once
```

### Debug Mode
```bash
# Debug logları ile çalıştır
DEBUG=* npm run monitor:once

# Verbose output
npm run monitor:once -- --verbose
```

## 📝 Maintenance

### Log Rotation
```bash
# Log dosyalarını temizle (30 gün)
find logs/ -name "*.log" -mtime +30 -delete

# Report dosyalarını temizle (7 gün)
find logs/ -name "*.json" -mtime +7 -delete
```

### Performance Monitoring
- Memory usage kontrolü
- CPU usage kontrolü
- Network request sayısı
- Response time monitoring

### Backup
```bash
# Monitoring config backup
cp .env .env.backup
cp logs/deployment-report.json logs/backup/

# Cron job backup
crontab -l > cron.backup
```

## 🔄 Updates

### Otomatik Güncelleme
```bash
# Git pull
git pull origin main

# Dependencies güncelle
npm install

# Service restart
sudo systemctl restart buzz2remote-monitor
```

### Version Control
- Semantic versioning
- Changelog maintenance
- Breaking changes documentation
- Migration guides

## 📞 Support

### Log Dosyaları
- `logs/deployment-monitor.log`: Ana log dosyası
- `logs/cron.log`: Cron job logları
- `logs/deployment-report.json`: Son rapor

### Debug Komutları
```bash
# Service durumu
sudo systemctl status buzz2remote-monitor

# Logları takip et
tail -f logs/deployment-monitor.log

# Dashboard
npm run monitor:dashboard

# Manual test
npm run monitor:once
```

Bu sistem sayesinde deployment'larınız 7/24 izlenir ve yaygın sorunlar otomatik olarak düzeltilir! 🚀 