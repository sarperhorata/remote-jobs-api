# Cron-job.org Configuration for Buzz2Remote

## 🔧 **Endpoint URL'leri**

Bu URL'leri cron-job.org'da kullanın:

### **Base URL**
```
https://buzz2remote-api.onrender.com
```

### **Security Token**
```
CRON_SECRET_TOKEN=buzz2remote_cron_2024
```

## 📋 **Cronjob Configuration**

### **1. Database Cleanup**
- **URL**: `https://buzz2remote-api.onrender.com/api/v1/cron/database-cleanup?token=buzz2remote_cron_2024`
- **Method**: POST
- **Schedule**: Daily at 2:00 AM
- **Cron Expression**: `0 2 * * *`

### **2. External API Crawler**
- **URL**: `https://buzz2remote-api.onrender.com/api/v1/cron/external-api-crawler?token=buzz2remote_cron_2024`
- **Method**: POST
- **Schedule**: Daily at 9:00 AM
- **Cron Expression**: `0 9 * * *`

### **3. Job Statistics**
- **URL**: `https://buzz2remote-api.onrender.com/api/v1/cron/job-statistics?token=buzz2remote_cron_2024`
- **Method**: POST
- **Schedule**: Daily at 8:00 AM
- **Cron Expression**: `0 8 * * *`

### **4. Distill Crawler**
- **URL**: `https://buzz2remote-api.onrender.com/api/v1/cron/distill-crawler?token=buzz2remote_cron_2024`
- **Method**: POST
- **Schedule**: Daily at 10:00 AM
- **Cron Expression**: `0 10 * * *`

### **5. Cron Status Monitor**
- **URL**: `https://buzz2remote-api.onrender.com/api/v1/cron/cron-status?token=buzz2remote_cron_2024`
- **Method**: POST
- **Schedule**: Every 2 hours
- **Cron Expression**: `0 */2 * * *`

### **6. Test Timeout Monitor**
- **URL**: `https://buzz2remote-api.onrender.com/api/v1/cron/test-timeout?token=buzz2remote_cron_2024`
- **Method**: POST
- **Schedule**: Every hour at :30
- **Cron Expression**: `30 * * * *`

### **7. Keep Render Alive**
- **URL**: `https://buzz2remote-api.onrender.com/api/v1/health`
- **Method**: GET
- **Schedule**: Every 14 minutes
- **Cron Expression**: `*/14 * * * *`

## 🔍 **Test & Monitoring URLs**

### **Health Check**
```
GET https://buzz2remote-api.onrender.com/api/v1/cron/health
```

### **Get All Endpoints**
```
GET https://buzz2remote-api.onrender.com/api/v1/cron/test-endpoints
```

### **Check Status**
```
GET https://buzz2remote-api.onrender.com/api/v1/cron/status?token=buzz2remote_cron_2024
```

### **Get Logs**
```
GET https://buzz2remote-api.onrender.com/api/v1/cron/logs/{job_name}?token=buzz2remote_cron_2024&lines=50
```

Örnek log URL'leri:
- Database cleanup: `/api/v1/cron/logs/database_cleanup?token=buzz2remote_cron_2024`
- External API: `/api/v1/cron/logs/external_api_cron?token=buzz2remote_cron_2024`
- Job statistics: `/api/v1/cron/logs/job_statistics?token=buzz2remote_cron_2024`

## 🚨 **Emergency: Run All Jobs**
```
POST https://buzz2remote-api.onrender.com/api/v1/cron/run-all?token=buzz2remote_cron_2024
```
⚠️ **Dikkat**: Bu endpoint tüm cronjob'ları aynı anda çalıştırır. Sadece acil durumlarda kullanın!

## 📊 **Telegram Integration**

Telegram bilgileri endpoint'lere gömülü:
- **Bot Token**: `8116251711:AAFhGxXtOJu2eCqCORoDr46XWq7ejqMeYnY`
- **Chat ID**: `-1002424698891`

External API Crawler çalıştığında Telegram'a bildirim gönderecek.

## ✅ **Setup Steps for cron-job.org**

1. **cron-job.org**'da hesabınıza giriş yapın
2. "Create Cronjob" butonuna tıklayın
3. Her cronjob için:
   - **Title**: Yukarıdaki isimlerden birini kullanın (örn: "Database Cleanup")
   - **URL**: Yukarıdaki URL'lerden birini kopyalayın
   - **HTTP Method**: POST (health check hariç)
   - **Schedule**: Yukarıdaki cron expression'ları kullanın
   - **Timeout**: 300 saniye (5 dakika)
   - **Retries**: 2
   - **Enabled**: ✅ Aktif

## 🔧 **Troubleshooting**

### **Hata Codes**
- **401**: Token hatalı veya eksik
- **404**: Endpoint bulunamadı
- **500**: Internal server error

### **Test Commands**
```bash
# Health check
curl "https://buzz2remote-api.onrender.com/api/v1/cron/health"

# Test database cleanup
curl -X POST "https://buzz2remote-api.onrender.com/api/v1/cron/database-cleanup?token=buzz2remote_cron_2024"

# Check endpoints
curl "https://buzz2remote-api.onrender.com/api/v1/cron/test-endpoints"
```

## 📈 **Monitoring**

1. **cron-job.org Dashboard**: Execution history görüntüle
2. **Status Endpoint**: Gerçek zamanlı durum kontrolü
3. **Log Endpoints**: Detaylı log analizi
4. **Telegram**: External API crawler bildirimleri

## 🔄 **Migration dari Local ke Cloud**

Local cronjob'ları iptal edin:
```bash
# Local crontab'i temizle
crontab -r

# Veya sadece buzz2remote cronjob'larını sil
crontab -e
# Manuel olarak satırları silin
```

Artık tüm cronjob'lar cron-job.org üzerinden çalışacak! 🚀 