# Cron-job.org Setup Guide

Bu dokümanda Buzz2Remote projesi için cron-job.org'da cron job'ların nasıl kurulacağı açıklanmaktadır.

## 🚀 Cron Job Endpoints

Aşağıdaki endpoint'ler cron-job.org tarafından çağrılabilir:

### 🔑 Authentication
Tüm cron job endpoint'leri API key gerektirir:
- **Header:** `X-API-Key: buzz2remote-cron-2024`
- **Query Param:** `?api_key=buzz2remote-cron-2024`

### 1. Health Check (Render'ı Uyanık Tutmak İçin)
- **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/health-check`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her 10 dakikada bir (cron-job.org max 30s timeout)
- **Amaç:** Render servisini uyku modundan çıkarmak

### 2. External API Crawler
- **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/external-api-crawler`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her gün saat 09:00 UTC
- **Amaç:** Dış API'lerden iş ilanlarını çekmek

### 3. Distill Crawler
- **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/distill-crawler`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her gün saat 10:00 UTC
- **Amaç:** Buzz2Remote-Companies Distill crawler'ını çalıştırmak

### 4. Database Cleanup
- **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/database-cleanup`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her Pazar günü saat 02:00 UTC
- **Amaç:** Eski verileri temizlemek

### 5. Job Statistics
- **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/job-statistics`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her gün saat 08:00 UTC
- **Amaç:** Günlük iş istatistiklerini güncellemek

### 6. Cron Status (Monitoring)
- **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/status`
- **Method:** GET
- **Schedule:** Her saat başı (monitoring için)
- **Amaç:** Cron job'ların durumunu kontrol etmek

### 7. Test Timeout (Quick Response)
- **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/test-timeout`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her 5 dakikada bir (test için)
- **Amaç:** Hızlı response test etmek

### 🆕 8. Deployment Monitor (YENİ!)
- **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/monitor/check`
- **Method:** POST
- **Headers:** 
  - `Content-Type: application/json`
  - `Authorization: Bearer YOUR_MONITOR_TOKEN`
- **Body:** 
  ```json
  {
    "action": "check",
    "timestamp": "{{timestamp}}",
    "source": "cron-job.org"
  }
  ```
- **Schedule:** Her 15 dakikada bir
- **Amaç:** Render, GitHub Actions, Netlify deployment'larını izlemek ve otomatik düzeltmek

## 📋 Cron-job.org Kurulum Adımları

### 1. Hesap Oluşturma
1. [cron-job.org](https://cron-job.org) adresine gidin
2. Ücretsiz hesap oluşturun
3. Email doğrulamasını tamamlayın

### 2. Yeni Cron Job Ekleme

#### Health Check Job
1. Dashboard'da "CREATE CRONJOB" butonuna tıklayın
2. **Title:** `Buzz2Remote Health Check`
3. **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/health-check`
4. **Schedule:** `*/10 * * * *` (Her 10 dakikada bir)
5. **Method:** POST
6. **Headers:** `X-API-Key: buzz2remote-cron-2024`
7. **Save** butonuna tıklayın

#### External API Crawler
1. **Title:** `Buzz2Remote External API Crawler`
2. **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/external-api-crawler`
3. **Schedule:** `0 9 * * *` (Her gün 09:00 UTC)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

#### Distill Crawler
1. **Title:** `Buzz2Remote Distill Crawler`
2. **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/distill-crawler`
3. **Schedule:** `0 10 * * *` (Her gün 10:00 UTC)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

#### Database Cleanup
1. **Title:** `Buzz2Remote Database Cleanup`
2. **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/database-cleanup`
3. **Schedule:** `0 2 * * 0` (Her Pazar 02:00 UTC)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

#### Job Statistics
1. **Title:** `Buzz2Remote Job Statistics`
2. **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/job-statistics`
3. **Schedule:** `0 8 * * *` (Her gün 08:00 UTC)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

#### Cron Status
1. **Title:** `Buzz2Remote Cron Status`
2. **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/status`
3. **Schedule:** `0 * * * *` (Her saat başı)
4. **Method:** GET
5. **Save**

#### Test Timeout
1. **Title:** `Buzz2Remote Test Timeout`
2. **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/test-timeout`
3. **Schedule:** `*/5 * * * *` (Her 5 dakikada bir)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

#### 🆕 Deployment Monitor (YENİ!)
1. **Title:** `Buzz2Remote Deployment Monitor`
2. **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/monitor/check`
3. **Schedule:** `*/15 * * * *` (Her 15 dakikada bir)
4. **Method:** POST
5. **Headers:** 
   - `Content-Type: application/json`
   - `Authorization: Bearer YOUR_MONITOR_TOKEN`
6. **Body (JSON):**
   ```json
   {
     "action": "check",
     "timestamp": "{{timestamp}}",
     "source": "cron-job.org"
   }
   ```
7. **Save**

## 🔧 Environment Variables

Render'da aşağıdaki environment variables'ları ayarlayın:

```bash
# Mevcut cron job'lar için
CRON_API_KEY=buzz2remote-cron-2024

# Yeni monitoring sistemi için
RENDER_API_KEY=your_render_api_key
GITHUB_TOKEN=your_github_token
NETLIFY_ACCESS_TOKEN=your_netlify_token
NETLIFY_SITE_ID=your_netlify_site_id
MONITOR_TOKEN=your_secure_monitor_token
WEBHOOK_URL=your_webhook_url
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

## 📊 Monitoring Dashboard

Yeni monitoring sistemi için dashboard:
- **URL:** `https://remote-jobs-api-k9v1.onrender.com/api/monitor/dashboard`
- **Status:** `https://remote-jobs-api-k9v1.onrender.com/api/monitor/status`
- **Logs:** `https://remote-jobs-api-k9v1.onrender.com/api/monitor/logs`

## 🔒 Güvenlik

### API Token Oluşturma
```bash
# Güçlü monitor token oluştur
openssl rand -hex 32
# Çıktıyı MONITOR_TOKEN olarak ayarlayın
```

### IP Whitelisting
Cron-job.org IP'leri otomatik olarak allow edilir:
- `165.227.83.0/24`
- `159.89.49.0/24`

## 🐛 Troubleshooting

### Yaygın Sorunlar

#### 1. Timeout Errors
```
Error: Request timeout after 30 seconds
Solution: cron-job.org maximum timeout'u 30 saniye
```

#### 2. Authentication Errors
```
Error: 401 Unauthorized
Solution: API key'leri kontrol edin
```

#### 3. Monitoring Token Errors
```
Error: Invalid monitor token
Solution: MONITOR_TOKEN environment variable'ını kontrol edin
```

#### 4. Rate Limiting (429 Too Many Requests)
```
Error: 429 Too Many Requests
Solution: Cron job'lar için özel rate limiting ayarlandı
```

### Debug Komutları
```bash
# Health check test
curl -X POST https://remote-jobs-api-k9v1.onrender.com/api/v1/cron/health-check \
  -H "X-API-Key: buzz2remote-cron-2024"

# Monitoring test
curl -X POST https://remote-jobs-api-k9v1.onrender.com/api/monitor/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MONITOR_TOKEN" \
  -d '{"action":"check","timestamp":"2025-07-31T08:48:00.484Z","source":"test"}'

# Status check
curl https://remote-jobs-api-k9v1.onrender.com/api/monitor/status
```

## 📈 Monitoring Features

### Yeni Monitoring Sistemi Özellikleri:
- ✅ **Render Deployment Monitoring**
- ✅ **GitHub Actions Workflow Monitoring**
- ✅ **Netlify Deployment Monitoring**
- ✅ **External Health Checks**
- ✅ **Auto-Fix Mechanisms**
- ✅ **Real-Time Notifications**
- ✅ **Web Dashboard**
- ✅ **JSON Reports**

### Mevcut Cron Job'lar:
- ✅ **Health Check** (Render wake-up)
- ✅ **External API Crawler**
- ✅ **Distill Crawler**
- ✅ **Database Cleanup**
- ✅ **Job Statistics**
- ✅ **Cron Status**
- ✅ **Test Timeout**

Bu güncelleme ile hem mevcut cron job'larınız çalışmaya devam edecek hem de yeni monitoring sistemi eklenmiş olacak! 🚀 