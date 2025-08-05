# Cron-job.org Kurulum Rehberi (Güncellenmiş)

## 🚨 Önemli Not: 30 Dakika Kısıtlaması

Cron-job.org'da **ücretsiz plan** için minimum 30 dakika aralık zorunludur. 30 dakikadan sık çalışan job'lar HTTP 429 hatası verir.

## ✅ Çözüm: Yeni External Endpoint'ler

Artık bu URL'leri kullanın (rate limiting olmadan):

### 🔗 Endpoint URL'leri

| Job | URL | Method | Schedule |
|-----|-----|--------|----------|
| Health Check | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/health-check?api_key=buzz2remote-cron-2024` | POST | 30 dakika |
| External APIs | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/external-apis?api_key=buzz2remote-cron-2024` | POST | 30 dakika |
| Database Cleanup | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/database-cleanup?api_key=buzz2remote-cron-2024` | POST | 30 dakika |
| Job Statistics | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/job-statistics?api_key=buzz2remote-cron-2024` | POST | 30 dakika |
| Distill Crawler | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/distill-crawler?api_key=buzz2remote-cron-2024` | POST | 30 dakika |
| Status Monitor | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/status-monitor?api_key=buzz2remote-cron-2024` | POST | 30 dakika |
| Test Timeout | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/test-timeout?api_key=buzz2remote-cron-2024` | POST | 30 dakika |

## 📋 Kurulum Adımları

### 1. Cron-job.org'da Hesap Oluştur
- https://cron-job.org adresine git
- Ücretsiz hesap oluştur

### 2. Yeni Job Ekle
- "CREATE CRONJOB" butonuna tıkla
- **Name**: `Buzz2Remote Health Check`
- **URL**: `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/health-check?api_key=buzz2remote-cron-2024`
- **Method**: `POST`
- **Schedule**: `Every 30 minutes`
- **Save** butonuna tıkla

### 3. Diğer Job'ları Ekle
Yukarıdaki tablodaki her endpoint için aynı adımları tekrarla.

## 🔧 Özellikler

### ✅ Rate Limiting Yok
- External endpoint'ler ana rate limiter'ı bypass eder
- Cron-job.org kısıtlamalarına takılmaz

### ✅ API Key Güvenliği
- `api_key=buzz2remote-cron-2024` query parameter ile
- Veya `Authorization: Bearer buzz2remote-cron-2024` header ile

### ✅ Telegram Bildirimleri
- Başarılı/başarısız durumlar için otomatik bildirim
- Gerçek zamanlı monitoring

### ✅ Background Tasks
- Uzun süren işlemler arka planda çalışır
- Hızlı response time

## 🧪 Test Etme

### Manuel Test
```bash
curl -X POST "https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/health-check?api_key=buzz2remote-cron-2024"
```

### Beklenen Response
```json
{
  "status": "success",
  "message": "Health check started",
  "job_id": "external_health_check"
}
```

## ⚠️ Önemli Notlar

1. **30 Dakika Kısıtlaması**: Ücretsiz plan için minimum aralık
2. **API Key**: URL'de `api_key=buzz2remote-cron-2024` parametresi zorunlu
3. **POST Method**: Tüm endpoint'ler POST method kullanır
4. **Telegram**: Bildirimler otomatik olarak gönderilir

## 🔄 Eski Job'ları Sil

HTTP 429 hatası veren eski job'ları silin:
- `/api/v1/cron/health-check` (eski)
- `/api/v1/cron/external-api-crawler` (eski)
- Diğer eski endpoint'ler

## 📞 Destek

Sorun yaşarsanız:
1. Telegram bildirimlerini kontrol edin
2. Render log'larını kontrol edin
3. API key'in doğru olduğundan emin olun

---

**Son Güncelleme**: 3 Ağustos 2025
**Versiyon**: 2.0 (External Endpoint'ler) 