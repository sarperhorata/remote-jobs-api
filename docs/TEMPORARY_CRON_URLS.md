# 🔄 Geçici Cron Job URL'leri

Render servisi uyku modunda olduğu için geçici olarak local backend'i kullanabilirsiniz.

## 🚨 **ÖNEMLİ NOT:**
Bu URL'ler geçicidir ve sadece local backend çalıştığında erişilebilir. Render servisi uyandığında production URL'lere geçiş yapın.

## 🔗 **Geçici URL'ler:**

### 1. Health Check (Her 10 dakikada bir)
```
Title: Buzz2Remote Health Check (Temporary)
URL: https://buzz2remote-cron.loca.lt/api/v1/cron/health-check
Method: POST
Headers: X-API-Key: buzz2remote-cron-2024
Schedule: */10 * * * *
```

### 2. Test Timeout (Her 5 dakikada bir)
```
Title: Buzz2Remote Test Timeout (Temporary)
URL: https://buzz2remote-cron.loca.lt/api/v1/cron/test-timeout
Method: POST
Headers: X-API-Key: buzz2remote-cron-2024
Schedule: */5 * * * *
```

### 3. Job Statistics (Her gün 08:00 UTC)
```
Title: Buzz2Remote Job Statistics (Temporary)
URL: https://buzz2remote-cron.loca.lt/api/v1/cron/job-statistics
Method: POST
Headers: X-API-Key: buzz2remote-cron-2024
Schedule: 0 8 * * *
```

### 4. External API Crawler (Her gün 09:00 UTC)
```
Title: Buzz2Remote External API Crawler (Temporary)
URL: https://buzz2remote-cron.loca.lt/api/v1/cron/external-api-crawler
Method: POST
Headers: X-API-Key: buzz2remote-cron-2024
Schedule: 0 9 * * *
```

### 5. Distill Crawler (Her gün 10:00 UTC)
```
Title: Buzz2Remote Distill Crawler (Temporary)
URL: https://buzz2remote-cron.loca.lt/api/v1/cron/distill-crawler
Method: POST
Headers: X-API-Key: buzz2remote-cron-2024
Schedule: 0 10 * * *
```

### 6. Database Cleanup (Her Pazar 02:00 UTC)
```
Title: Buzz2Remote Database Cleanup (Temporary)
URL: https://buzz2remote-cron.loca.lt/api/v1/cron/database-cleanup
Method: POST
Headers: X-API-Key: buzz2remote-cron-2024
Schedule: 0 2 * * 0
```

### 7. Status Monitor (Her saat başı)
```
Title: Buzz2Remote Status Monitor (Temporary)
URL: https://buzz2remote-cron.loca.lt/api/v1/cron/status
Method: GET
Schedule: 0 * * * *
```

## ⚠️ **Kısıtlamalar:**

1. **Local Backend Gerekli:** Bu URL'ler sadece local backend çalıştığında erişilebilir
2. **Geçici Çözüm:** Render servisi uyandığında production URL'lere geçiş yapın
3. **Güvenlik:** Local backend production veritabanına bağlı olduğu için dikkatli olun

## 🔄 **Production'a Geçiş:**

Render servisi uyandığında şu URL'lere geçiş yapın:

```
Production Base URL: https://buzz2remote-api.onrender.com
```

Örnek:
- Geçici: `https://buzz2remote-cron.loca.lt/api/v1/cron/health-check`
- Production: `https://buzz2remote-api.onrender.com/api/v1/cron/health-check`

## 🛠️ **Local Backend Başlatma:**

```bash
cd backend
python -m uvicorn main:app --reload --port 8001
```

## 📊 **Test Komutları:**

```bash
# Test timeout
curl -X POST https://buzz2remote-cron.loca.lt/api/v1/cron/test-timeout \
  -H "X-API-Key: buzz2remote-cron-2024"

# Health check
curl -X POST https://buzz2remote-cron.loca.lt/api/v1/cron/health-check \
  -H "X-API-Key: buzz2remote-cron-2024"

# Status
curl https://buzz2remote-cron.loca.lt/api/v1/cron/status
```

## 🎯 **Sonraki Adımlar:**

1. ✅ Cron-job.org'da geçici URL'leri kullanın
2. ⏳ Render servisinin uyanmasını bekleyin
3. 🔄 Production URL'lere geçiş yapın
4. 🗑️ Geçici job'ları silin 