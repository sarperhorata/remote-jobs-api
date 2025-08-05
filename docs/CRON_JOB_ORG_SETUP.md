# Cron-Job.org Kurulum Kılavuzu

## 🎯 Amaç

Render free tier sınırlamaları nedeniyle cron job'ları cron-job.org üzerinden tetiklemek.

## 🔍 Render Free Tier Sınırlamaları

- **Cron Job'lar**: 10 dakikada bir çalışır
- **Web Servisleri**: 15 dakika inaktif kaldıktan sonra uyku moduna geçer
- **Cron Job'lar**: Sadece web servisleri aktifken çalışır

## 🚀 Çözüm: Cron-Job.org + Ping Service

### 1. Ping Service (Render'da)
- `buzz2remote-ping` servisi sürekli çalışır
- Ana backend servisini 10 dakikada bir ping'ler
- Cron job'ları tetiklemek için endpoint'ler sağlar

### 2. Cron-Job.org (Dışarıda)
- Cron job'ları belirtilen zamanlarda tetikler
- Ping service endpoint'lerini çağırır
- Ücretsiz ve güvenilir

## 📋 Cron-Job.org Kurulum Adımları

### Adım 1: Cron-Job.org'a Kayıt Ol
1. https://cron-job.org adresine git
2. Ücretsiz hesap oluştur
3. Email doğrulamasını tamamla

### Adım 2: Cron Job'ları Ekle

#### 1. Ping Service (Her 10 dakikada)
```
Name: Buzz2Remote Ping
URL: https://buzz2remote-ping.onrender.com/ping
Schedule: */10 * * * * (Her 10 dakikada)
```

#### 2. Auto-Fix (Her gün 02:00)
```
Name: Auto-Fix Workflow
URL: https://buzz2remote-ping.onrender.com/trigger/auto-fix
Schedule: 0 2 * * * (Her gün saat 02:00)
```

#### 3. Workflow Monitor (Her gün 06:00)
```
Name: Workflow Monitor
URL: https://buzz2remote-ping.onrender.com/trigger/workflow-monitor
Schedule: 0 6 * * * (Her gün saat 06:00)
```

#### 4. Database Cleanup (Her gün 03:00)
```
Name: Database Cleanup
URL: https://buzz2remote-ping.onrender.com/trigger/db-cleanup
Schedule: 0 3 * * * (Her gün saat 03:00)
```

#### 5. External API Crawler (Her gün 04:00)
```
Name: External API Crawler
URL: https://buzz2remote-ping.onrender.com/trigger/api-crawler
Schedule: 0 4 * * * (Her gün saat 04:00)
```

#### 6. Job Statistics (Her gün 05:00)
```
Name: Job Statistics
URL: https://buzz2remote-ping.onrender.com/trigger/job-stats
Schedule: 0 5 * * * (Her gün saat 05:00)
```

### Adım 3: Cron Job Ayarları

Her cron job için şu ayarları yap:

#### General Settings
- **Name**: Açıklayıcı isim
- **URL**: Ping service endpoint'i
- **Schedule**: Cron expression
- **Timezone**: UTC

#### Advanced Settings
- **Retry on failure**: 3 attempts
- **Retry delay**: 5 minutes
- **Timeout**: 300 seconds
- **Request method**: GET
- **Headers**: None (gerekirse ekle)

#### Notifications
- **Email notifications**: Enable
- **Webhook notifications**: Optional
- **Failure notifications**: Enable

## 🔧 Ping Service Endpoint'leri

### Ana Endpoint'ler
```
GET /                    - Service status
GET /health             - Health check
GET /ping               - Manual ping
```

### Trigger Endpoint'leri
```
GET /trigger/auto-fix           - Auto-fix workflow
GET /trigger/workflow-monitor   - Workflow monitoring
GET /trigger/db-cleanup         - Database cleanup
GET /trigger/api-crawler        - External API crawler
GET /trigger/job-stats          - Job statistics
```

## 📊 Monitoring

### Cron-Job.org Dashboard
- Cron job'ların çalışma durumunu izle
- Başarısızlık durumlarını kontrol et
- Log'ları incele

### Render Dashboard
- `buzz2remote-ping` servisinin durumunu izle
- Log'ları kontrol et
- Ping başarı oranını takip et

## 🚨 Sorun Giderme

### Ping Service Çalışmıyor
1. Render dashboard'da servis durumunu kontrol et
2. Log'ları incele
3. Environment variables'ları kontrol et

### Cron Job'lar Tetiklenmiyor
1. Cron-job.org'da job durumunu kontrol et
2. URL'lerin doğru olduğunu kontrol et
3. Schedule'ları kontrol et

### Timeout Hataları
1. Script timeout sürelerini artır
2. Cron job timeout ayarlarını kontrol et
3. Script'lerin performansını optimize et

## 💰 Maliyet

### Cron-Job.org Free Tier
- **Cron Job Sayısı**: 5 adet
- **Çalışma Sıklığı**: Her 1 dakikada
- **Maliyet**: Ücretsiz

### Render Free Tier
- **Web Servisleri**: 2 adet
- **Maliyet**: Ücretsiz

## ✅ Avantajlar

1. **Güvenilir**: Cron-job.org 99.9% uptime
2. **Ücretsiz**: Tamamen ücretsiz
3. **Esnek**: İstediğin zaman çalıştır
4. **Monitoring**: Detaylı log'lar ve bildirimler
5. **Basit**: Kolay kurulum ve yönetim

## 🔄 Sonraki Adımlar

1. **Cron-job.org'a kayıt ol**
2. **Ping service'i Render'a deploy et**
3. **Cron job'ları cron-job.org'da ayarla**
4. **Test et ve monitoring yap**
5. **Gerekirse ayarları optimize et**

---

**Son Güncelleme:** 2025-08-02  
**Durum:** Hazır ✅  
**Sonraki Adım:** Cron-job.org kurulumu 