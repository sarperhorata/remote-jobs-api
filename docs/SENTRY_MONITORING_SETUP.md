# Sentry Monitoring & Alerting Setup

## 🎯 Overview

Sentry monitoring sistemi Buzz2Remote projesine başarıyla entegre edildi. Free tier kotasını aşmayacak şekilde optimize edilmiş konfigürasyon ile error tracking, performance monitoring ve alerting özellikleri aktif.

## ✅ Tamamlanan Özellikler

### Frontend (React)
- ✅ **Error Boundary:** Tüm uygulamayı sarıyor
- ✅ **Error Tracking:** JavaScript hatalarını yakalıyor
- ✅ **User Context:** Kullanıcı bilgilerini error'lara ekliyor
- ✅ **Performance Monitoring:** Transaction sampling (%10)
- ✅ **Error Filtering:** Gereksiz hataları filtreliyor
- ✅ **Free Tier Optimization:** Kotayı aşmayacak şekilde ayarlandı

### Backend (FastAPI)
- ✅ **Exception Tracking:** Python exception'larını yakalıyor
- ✅ **Performance Monitoring:** API endpoint performansı
- ✅ **Database Monitoring:** MongoDB query performansı
- ✅ **Webhook Integration:** Real-time alerting
- ✅ **Telegram Integration:** Kritik hatalar için bildirim
- ✅ **Free Tier Optimization:** Sample rate %10

## 🚀 Kurulum

### 1. Sentry Projesi Oluştur
1. [Sentry.io](https://sentry.io) hesabı oluştur
2. Yeni proje oluştur (React + FastAPI)
3. DSN'yi kopyala

### 2. Environment Variables
```bash
# Frontend (.env.local)
REACT_APP_SENTRY_DSN=your_sentry_dsn_here
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0
REACT_APP_ENABLE_SENTRY=true

# Backend (.env)
SENTRY_DSN=your_sentry_dsn_here
ENVIRONMENT=production
APP_VERSION=1.0.0
SENTRY_DEBUG=false
SENTRY_WEBHOOK_SECRET=your_webhook_secret_here
```

### 3. Otomatik Kurulum
```bash
# Setup script'ini çalıştır
npm run sentry:setup
# veya
node scripts/setup-sentry.js
```

## 📊 Free Tier Optimizations

### Frontend
- **Traces Sample Rate:** %10 (sadece kritik transaction'lar)
- **Max Breadcrumbs:** 10 (veri kullanımını azaltır)
- **Error Filtering:** Browser hatalarını filtreler
- **Performance Events:** Gereksiz route'ları filtreler

### Backend
- **Traces Sample Rate:** %10 (sadece kritik transaction'lar)
- **Profiles Sample Rate:** %10 (sadece kritik profiller)
- **Error Filtering:** Health check'leri filtreler
- **Rate Limiting:** Dakikada max 10 event

## 🔧 Kullanım

### Frontend Error Tracking
```javascript
import { captureException, captureMessage } from './config/sentry';

// Error yakalama
try {
  // riskli işlem
} catch (error) {
  captureException(error, { 
    tags: { component: 'JobSearch' } 
  });
}

// Mesaj gönderme
captureMessage('Kullanıcı onboarding tamamladı', 'info');
```

### Backend Error Tracking
```python
from backend.config.sentry import capture_exception, capture_message

# Exception yakalama
try:
    # riskli işlem
except Exception as e:
    capture_exception(e, {"context": "job_processing"})

# Mesaj gönderme
capture_message("Database backup tamamlandı", "info")
```

### User Context
```javascript
// Login'de user context set et
setUserContext({
  id: user.id,
  email: user.email,
  username: user.name
});

// Logout'ta temizle
clearUserContext();
```

## 🚨 Alerting

### Webhook Configuration
1. Sentry proje ayarlarına git
2. "Alerts" → "Rules" bölümüne git
3. Kritik hatalar için rule oluştur
4. Webhook URL ekle: `https://your-domain.com/webhook/sentry/alert`
5. Webhook secret ayarla

### Telegram Notifications
- Kritik hatalar otomatik olarak Telegram'a gönderilir
- `TELEGRAM_BOT_TOKEN` ve `TELEGRAM_CHAT_ID` gerekli
- Sadece `fatal` ve `error` seviyesindeki hatalar bildirilir

## 📈 Monitoring Dashboard

### Sentry Dashboard
1. **Issues:** Hataları görüntüle ve analiz et
2. **Performance:** Yavaş transaction'ları tespit et
3. **Releases:** Deployment'ları takip et
4. **Users:** Kullanıcı deneyimini izle

### Key Metrics
- **Error Rate:** %1'in altında tutulmalı
- **Response Time:** 95th percentile < 2s
- **Throughput:** Request per second
- **User Experience:** Core Web Vitals

## 🛠️ Troubleshooting

### Common Issues
- **High Event Volume:** Sample rate'leri düşür
- **Missing Context:** User context'i kontrol et
- **Webhook Failures:** Secret ve URL'yi kontrol et

### Debug Mode
```bash
# Development'ta debug mode aktif
SENTRY_DEBUG=true
```

### Performance Monitoring
```javascript
// Transaction başlat
const transaction = startTransaction('job-search', 'search');
// ... işlem ...
transaction.finish();
```

## 📋 Best Practices

### Error Handling
1. **Don't log everything:** Sadece anlamlı hataları yakala
2. **Use tags:** Hatalara context ekle
3. **Monitor usage:** Sentry dashboard'da quota kullanımını kontrol et
4. **Filter noise:** Spam'i önlemek için filtreleme yapılandır

### Performance
1. **Sample rates:** Free tier için %10 kullan
2. **Breadcrumbs:** Max 10 ile sınırla
3. **Transactions:** Sadece kritik işlemleri izle
4. **Profiles:** Sadece production'da aktif et

## 🔒 Security

### Environment Variables
- DSN'yi public repository'de paylaşma
- Webhook secret'ı güvenli tut
- Production'da debug mode'u kapat

### Data Privacy
- PII (Personal Identifiable Information) gönderme
- User context'te sadece gerekli bilgileri kullan
- GDPR compliance için data retention ayarla

## 📞 Support

### Documentation
- [Sentry React Docs](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Sentry Python Docs](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Free Tier Limits](https://sentry.io/pricing/)

### Monitoring
- Sentry dashboard'da quota kullanımını takip et
- Monthly event count'u kontrol et
- Performance impact'i izle

## 🎉 Sonuç

Sentry monitoring sistemi başarıyla kuruldu ve free tier optimizasyonları ile çalışıyor. Artık:

- ✅ Real-time error tracking
- ✅ Performance monitoring
- ✅ User context tracking
- ✅ Automated alerting
- ✅ Free tier compliance

**Proje artık production-ready monitoring ile çalışıyor!** 🚀 