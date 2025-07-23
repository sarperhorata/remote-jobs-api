# Cron-job.org Setup Guide

Bu dokümanda Buzz2Remote projesi için cron-job.org'da cron job'ların nasıl kurulacağı açıklanmaktadır.

## 🚀 Cron Job Endpoints

Aşağıdaki endpoint'ler cron-job.org tarafından çağrılabilir:

### 🔑 Authentication
Tüm cron job endpoint'leri API key gerektirir:
- **Header:** `X-API-Key: buzz2remote-cron-2024`
- **Query Param:** `?api_key=buzz2remote-cron-2024`

### 1. Health Check (Render'ı Uyanık Tutmak İçin)
- **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/health-check`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her 10 dakikada bir (cron-job.org max 30s timeout)
- **Amaç:** Render servisini uyku modundan çıkarmak

### 2. External API Crawler
- **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/external-api-crawler`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her gün saat 09:00 UTC
- **Amaç:** Dış API'lerden iş ilanlarını çekmek

### 3. Distill Crawler
- **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/distill-crawler`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her gün saat 10:00 UTC
- **Amaç:** Buzz2Remote-Companies Distill crawler'ını çalıştırmak

### 4. Database Cleanup
- **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/database-cleanup`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her Pazar günü saat 02:00 UTC
- **Amaç:** Eski verileri temizlemek

### 5. Job Statistics
- **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/job-statistics`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her gün saat 08:00 UTC
- **Amaç:** Günlük iş istatistiklerini güncellemek

### 6. Cron Status (Monitoring)
- **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/status`
- **Method:** GET
- **Schedule:** Her saat başı (monitoring için)
- **Amaç:** Cron job'ların durumunu kontrol etmek

### 7. Test Timeout (Quick Response)
- **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/test-timeout`
- **Method:** POST
- **Headers:** `X-API-Key: buzz2remote-cron-2024`
- **Schedule:** Her 5 dakikada bir (test için)
- **Amaç:** Hızlı response test etmek

## 📋 Cron-job.org Kurulum Adımları

### 1. Hesap Oluşturma
1. [cron-job.org](https://cron-job.org) adresine gidin
2. Ücretsiz hesap oluşturun
3. Email doğrulamasını tamamlayın

### 2. Yeni Cron Job Ekleme

#### Health Check Job
1. Dashboard'da "CREATE CRONJOB" butonuna tıklayın
2. **Title:** `Buzz2Remote Health Check`
3. **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/health-check`
4. **Schedule:** `*/10 * * * *` (Her 10 dakikada bir)
5. **Method:** POST
6. **Headers:** `X-API-Key: buzz2remote-cron-2024`
7. **Save** butonuna tıklayın

#### External API Crawler
1. **Title:** `Buzz2Remote External API Crawler`
2. **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/external-api-crawler`
3. **Schedule:** `0 9 * * *` (Her gün 09:00 UTC)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

#### Distill Crawler
1. **Title:** `Buzz2Remote Distill Crawler`
2. **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/distill-crawler`
3. **Schedule:** `0 10 * * *` (Her gün 10:00 UTC)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

#### Database Cleanup
1. **Title:** `Buzz2Remote Database Cleanup`
2. **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/database-cleanup`
3. **Schedule:** `0 2 * * 0` (Her Pazar 02:00 UTC)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

#### Job Statistics
1. **Title:** `Buzz2Remote Job Statistics`
2. **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/job-statistics`
3. **Schedule:** `0 8 * * *` (Her gün 08:00 UTC)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

#### Monitoring
1. **Title:** `Buzz2Remote Status Monitor`
2. **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/status`
3. **Schedule:** `0 * * * *` (Her saat başı)
4. **Method:** GET
5. **Save**

#### Test Timeout
1. **Title:** `Buzz2Remote Test Timeout`
2. **URL:** `https://buzz2remote-api.onrender.com/api/v1/cron/test-timeout`
3. **Schedule:** `*/5 * * * *` (Her 5 dakikada bir)
4. **Method:** POST
5. **Headers:** `X-API-Key: buzz2remote-cron-2024`
6. **Save**

## ⚙️ Cron Expression Açıklamaları

- `*/10 * * * *` - Her 10 dakikada bir (cron-job.org max 30s timeout)
- `*/5 * * * *` - Her 5 dakikada bir (test için)
- `0 9 * * *` - Her gün saat 09:00
- `0 10 * * *` - Her gün saat 10:00
- `0 2 * * 0` - Her Pazar saat 02:00
- `0 8 * * *` - Her gün saat 08:00
- `0 * * * *` - Her saat başı

## 🔧 Ek Ayarlar

### Notification Settings
Her cron job için:
1. **Notifications** sekmesine gidin
2. **Email notifications** aktif edin
3. **Failure notifications** aktif edin
4. **Success notifications** isteğe bağlı

### Retry Settings
1. **Retry on failure** aktif edin
2. **Max retries:** 3
3. **Retry delay:** 5 minutes

### Timeout Settings
1. **Request timeout:** 30 seconds (cron-job.org maximum)
2. **Grace time:** 10 seconds

## 📊 Monitoring

### Dashboard
- Cron-job.org dashboard'ında tüm job'ların durumunu görebilirsiniz
- Başarı/başarısızlık oranlarını takip edebilirsiniz
- Son çalışma zamanlarını kontrol edebilirsiniz

### Logs
Her job için detaylı loglar:
- HTTP response codes
- Response times
- Error messages
- Success confirmations

## 🚨 Troubleshooting

### Common Issues

#### 1. 404 Error
- URL'lerin doğru olduğundan emin olun
- Backend servisinin çalıştığını kontrol edin

#### 2. Timeout Errors
- Request timeout'u artırın
- Backend servisinin yavaş olduğunu kontrol edin

#### 3. Authentication Errors
- Endpoint'ler public olduğu için auth gerekmez
- CORS ayarlarını kontrol edin

### Debug Steps
1. **Manual Test:** URL'leri tarayıcıda test edin
2. **Logs Check:** Backend loglarını kontrol edin
3. **Status Endpoint:** `/api/v1/cron/status` endpoint'ini kontrol edin

## 📈 Performance Monitoring

### Metrics to Track
- **Success Rate:** %95+ olmalı
- **Response Time:** < 30 saniye
- **Uptime:** %99+ olmalı

### Alerts
- Failure rate > %5
- Response time > 60 saniye
- Consecutive failures > 3

## 🔄 Backup Plan

Eğer cron-job.org kullanılamazsa:
1. Render'ın built-in cron job'larını kullanın
2. GitHub Actions scheduled workflows kullanın
3. Local scheduler service'i aktif edin

## 📝 Notes

- Tüm endpoint'ler POST method kullanır (status hariç)
- Health check her 14 dakikada bir çalışır (Render'ı uyanık tutmak için)
- UTC timezone kullanılır
- Response format: JSON
- Error handling built-in

## 🎯 Success Criteria

✅ Tüm cron job'lar başarıyla kuruldu
✅ Health check Render'ı uyanık tutuyor
✅ Job'lar zamanında çalışıyor
✅ Monitoring aktif
✅ Notifications çalışıyor
✅ Error handling çalışıyor 