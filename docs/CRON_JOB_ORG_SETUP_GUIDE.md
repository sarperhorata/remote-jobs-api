# Cron-job.org Kurulum Rehberi

## 🎯 **Genel Bakış**
Bu rehber, Buzz2Remote backend'inin cronjob'larını cron-job.org üzerinde kurmak için hazırlanmıştır.

## 📋 **Gerekli Cronjob'lar**

### 1. **Database Cleanup** 
- **URL:** `http://localhost:8001/api/v1/cron/database-cleanup?token=buzz2remote_cron_2024`
- **Method:** POST
- **Schedule:** `0 2 * * *` (Her gün saat 02:00)
- **Description:** Eski verileri temizler, database'i optimize eder

### 2. **External API Crawler**
- **URL:** `http://localhost:8001/api/v1/cron/external-api-crawler?token=buzz2remote_cron_2024`
- **Method:** POST
- **Schedule:** `0 */4 * * *` (Her 4 saatte bir)
- **Description:** External job board'lardan yeni iş ilanları çeker

### 3. **Job Statistics**
- **URL:** `http://localhost:8001/api/v1/cron/job-statistics?token=buzz2remote_cron_2024`
- **Method:** POST
- **Schedule:** `0 6 * * *` (Her gün saat 06:00)
- **Description:** Günlük iş istatistikleri oluşturur

### 4. **Distill Crawler**
- **URL:** `http://localhost:8001/api/v1/cron/distill-crawler?token=buzz2remote_cron_2024`
- **Method:** POST
- **Schedule:** `0 */6 * * *` (Her 6 saatte bir)
- **Description:** Company job posting'leri takip eder

### 5. **Cron Status Monitor**
- **URL:** `http://localhost:8001/api/v1/cron/cron-status?token=buzz2remote_cron_2024`
- **Method:** POST
- **Schedule:** `*/30 * * * *` (Her 30 dakikada bir)
- **Description:** Cronjob sisteminin durumunu kontrol eder

### 6. **Test Timeout Monitor**
- **URL:** `http://localhost:8001/api/v1/cron/test-timeout?token=buzz2remote_cron_2024`
- **Method:** POST
- **Schedule:** `0 */2 * * *` (Her 2 saatte bir)
- **Description:** Hanging test'leri ve process'leri kontrol eder

### 7. **Keep Render Alive**
- **URL:** `http://localhost:8001/api/v1/cron/health`
- **Method:** GET
- **Schedule:** `*/15 * * * *` (Her 15 dakikada bir)
- **Description:** Render service'ini aktif tutar

## 🔧 **Kurulum Adımları**

### Adım 1: Cron-job.org'a Git
1. https://cron-job.org adresine git
2. Hesabın yoksa kayıt ol
3. Dashboard'a gir

### Adım 2: Yeni Cronjob Ekle
1. "CREATE CRONJOB" butonuna tıkla
2. Her cronjob için aşağıdaki bilgileri gir:

#### Örnek: Database Cleanup
- **Title:** `Buzz2Remote - Database Cleanup`
- **URL:** `http://localhost:8001/api/v1/cron/database-cleanup?token=buzz2remote_cron_2024`
- **Method:** `POST`
- **Schedule:** `0 2 * * *`
- **Timezone:** `Europe/Istanbul`
- **Retry on failure:** `3`
- **Timeout:** `300` (5 dakika)

### Adım 3: Telegram Notifications
1. Her cronjob için "Notifications" sekmesine git
2. "Telegram" seçeneğini aktif et
3. Bot Token: `8116251711:AAFhGxXtOJu2eCqCORoDr46XWq7ejqMeYnY`
4. Chat ID: `-1002424698891`

### Adım 4: Test Et
1. Her cronjob'ı manuel olarak test et
2. Log'ları kontrol et
3. Telegram bildirimlerini doğrula

## 🧪 **Local Test Komutları**

```bash
# Backend'i başlat
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Health check
curl "http://localhost:8001/api/v1/cron/health"

# Database cleanup test
curl -X POST "http://localhost:8001/api/v1/cron/database-cleanup?token=buzz2remote_cron_2024"

# External API crawler test
curl -X POST "http://localhost:8001/api/v1/cron/external-api-crawler?token=buzz2remote_cron_2024"

# Job statistics test
curl -X POST "http://localhost:8001/api/v1/cron/job-statistics?token=buzz2remote_cron_2024"

# Distill crawler test
curl -X POST "http://localhost:8001/api/v1/cron/distill-crawler?token=buzz2remote_cron_2024"

# Cron status test
curl -X POST "http://localhost:8001/api/v1/cron/cron-status?token=buzz2remote_cron_2024"

# Test timeout test
curl -X POST "http://localhost:8001/api/v1/cron/test-timeout?token=buzz2remote_cron_2024"
```

## 🌐 **Production Deployment**

Render'da environment variables eklendikten sonra URL'leri şu şekilde güncelle:

```
https://buzz2remote-api.onrender.com/api/v1/cron/[endpoint]?token=buzz2remote_cron_2024
```

## 📊 **Monitoring**

### Cron Status Dashboard
- **URL:** `http://localhost:8001/api/v1/cron/status`
- **Description:** Tüm cronjob'ların durumunu gösterir

### Logs
- **URL:** `http://localhost:8001/api/v1/cron/logs/{job_name}`
- **Example:** `http://localhost:8001/api/v1/cron/logs/database_cleanup`

## 🔒 **Güvenlik**

- **Token:** `buzz2remote_cron_2024` (CRON_SECRET_TOKEN)
- **IP Whitelist:** Cron-job.org IP'leri
- **Rate Limiting:** Her endpoint için ayrı limit

## 🚨 **Troubleshooting**

### Cronjob Çalışmıyor
1. Backend'in çalıştığını kontrol et
2. Token'ın doğru olduğunu kontrol et
3. URL'in erişilebilir olduğunu kontrol et
4. Log'ları kontrol et

### Telegram Bildirimleri Gelmiyor
1. Bot token'ın doğru olduğunu kontrol et
2. Chat ID'nin doğru olduğunu kontrol et
3. Bot'un chat'e eklendiğini kontrol et

### Timeout Hatası
1. Cronjob'ın çok uzun sürdüğünü kontrol et
2. Timeout süresini artır
3. Background task'ları kontrol et 