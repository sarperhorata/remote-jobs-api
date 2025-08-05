# 🕐 Cronjob Kurulum Rehberi

## 📋 İçindekiler
1. [Render'da Cronjob Kurulumu](#render-da-cronjob-kurulumu)
2. [Cron-job.org'da Kurulum](#cron-joborg-da-kurulum)
3. [Lokal Kurulum](#lokal-kurulum)
4. [Test ve Monitoring](#test-ve-monitoring)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Render'da Cronjob Kurulumu

### Adım 1: render.yaml Dosyasını Hazırlayın
Proje kök dizininde `render.yaml` dosyası zaten hazır. Bu dosya 8 farklı cronjob servisi tanımlar.

### Adım 2: Render'da Deploy Edin
```bash
# 1. Render Dashboard'a gidin: https://dashboard.render.com
# 2. "New +" > "Blueprint" seçin
# 3. GitHub repo'nuzu bağlayın
# 4. render.yaml dosyasını otomatik olarak algılayacak
# 5. "Apply" butonuna tıklayın
```

### Adım 3: Environment Variables Ayarlayın
Render Dashboard'da her servis için aşağıdaki environment variables'ları ayarlayın:

```bash
# Gerekli Environment Variables
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/buzz2remote
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
API_KEY=your_secure_api_key_for_cronjobs

# Opsiyonel Environment Variables
ENVIRONMENT=production
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn
```

### Adım 4: Kurulan Cronjob'lar
Render'da otomatik olarak kurulan cronjob'lar:

| Job Adı | Zamanlama | Açıklama |
|---------|-----------|----------|
| `render-keep-alive` | `*/14 * * * *` | Render servisini canlı tutar |
| `health-check` | `0 * * * *` | Sistem sağlığını kontrol eder |
| `external-api-crawler` | `0 9 * * *` | Yeni iş ilanları çeker |
| `database-cleanup` | `0 2 * * *` | Eski verileri temizler |
| `job-statistics` | `0 6 * * *` | İstatistikler oluşturur |
| `distill-crawler` | `0 10 * * *` | Şirketleri izler |
| `cron-status-monitor` | `0 */2 * * *` | Cronjob sağlığını kontrol eder |
| `test-timeout-monitor` | `30 * * * *` | Asılı işlemleri kontrol eder |

---

## 🌐 Cron-job.org'da Kurulum

### Adım 1: Cron-job.org Hesabı Oluşturun
1. https://cron-job.org adresine gidin
2. "Sign up" ile hesap oluşturun
3. Email doğrulamasını tamamlayın

### Adım 2: API Endpoint'lerini Hazırlayın
Render'da deploy edilen backend URL'sini alın:
```
https://buzz2remote-backend.onrender.com
```

### Adım 3: Job'ları Oluşturun

#### Job 1: Render Keep-Alive
- **Name**: `Render Keep-Alive`
- **URL**: `https://buzz2remote-backend.onrender.com/api/v1/health`
- **Schedule**: `*/14 * * * *`
- **Method**: GET
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_API_KEY
  ```

#### Job 2: Health Check
- **Name**: `Health Check`
- **URL**: `https://buzz2remote-backend.onrender.com/api/v1/health`
- **Schedule**: `0 * * * *`
- **Method**: GET
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_API_KEY
  ```

#### Job 3: External API Crawler
- **Name**: `External API Crawler`
- **URL**: `https://buzz2remote-backend.onrender.com/api/v1/cron/external-apis`
- **Schedule**: `0 9 * * *`
- **Method**: POST
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_API_KEY
  ```

#### Job 4: Database Cleanup
- **Name**: `Database Cleanup`
- **URL**: `https://buzz2remote-backend.onrender.com/api/v1/cron/database-cleanup`
- **Schedule**: `0 2 * * *`
- **Method**: POST
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_API_KEY
  ```

#### Job 5: Job Statistics
- **Name**: `Job Statistics`
- **URL**: `https://buzz2remote-backend.onrender.com/api/v1/cron/job-statistics`
- **Schedule**: `0 6 * * *`
- **Method**: POST
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_API_KEY
  ```

#### Job 6: Distill Crawler
- **Name**: `Distill Crawler`
- **URL**: `https://buzz2remote-backend.onrender.com/api/v1/cron/distill-crawler`
- **Schedule**: `0 10 * * *`
- **Method**: POST
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_API_KEY
  ```

#### Job 7: Cron Status Monitor
- **Name**: `Cron Status Monitor`
- **URL**: `https://buzz2remote-backend.onrender.com/api/v1/cron/status-monitor`
- **Schedule**: `0 */2 * * *`
- **Method**: POST
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_API_KEY
  ```

#### Job 8: Test Timeout Monitor
- **Name**: `Test Timeout Monitor`
- **URL**: `https://buzz2remote-backend.onrender.com/api/v1/cron/test-timeout`
- **Schedule**: `30 * * * *`
- **Method**: POST
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Bearer YOUR_API_KEY
  ```

---

## 💻 Lokal Kurulum

### Adım 1: Kurulum Script'ini Çalıştırın
```bash
cd /Users/sarperhorata/buzz2remote
chmod +x scripts/deployment/setup_all_cronjobs.sh
./scripts/deployment/setup_all_cronjobs.sh
```

### Adım 2: Environment Variables Ayarlayın
```bash
# ~/.zshrc dosyasına ekleyin
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
export TELEGRAM_CHAT_ID='your_chat_id_here'
export MONGODB_URI='mongodb://localhost:27017/buzz2remote'
export API_KEY='your_secure_api_key'

# Değişiklikleri uygulayın
source ~/.zshrc
```

### Adım 3: Cronjob'ları Kontrol Edin
```bash
# Mevcut cronjob'ları görüntüleyin
crontab -l

# Log dizinini kontrol edin
ls -la logs/
```

---

## 🧪 Test ve Monitoring

### 1. Manuel Test
```bash
# Backend'i başlatın
cd backend && python main.py

# Endpoint'leri test edin
curl -X POST https://buzz2remote-backend.onrender.com/api/v1/cron/external-apis \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

### 2. Telegram Bildirimleri
- Başarılı/başarısız job'lar için bildirim alın
- Hata durumlarında anında uyarı alın

### 3. Log Monitoring
```bash
# Render log'larını kontrol edin
# Render Dashboard > Services > Logs

# Lokal log'ları kontrol edin
tail -f logs/cron.log
```

### 4. Cron-job.org Dashboard
- Job durumlarını kontrol edin
- Başarı/başarısız oranlarını izleyin
- Response time'ları takip edin

---

## 🚨 Troubleshooting

### Yaygın Sorunlar

#### 1. 401 Unauthorized
**Sorun**: API key doğrulama hatası
**Çözüm**:
```bash
# Environment variable'ı kontrol edin
echo $API_KEY

# Backend'de API key'i kontrol edin
# backend/routes/cron.py dosyasında
```

#### 2. 404 Not Found
**Sorun**: Endpoint bulunamıyor
**Çözüm**:
```bash
# Backend'in çalıştığından emin olun
curl https://buzz2remote-backend.onrender.com/health

# Route'un doğru tanımlandığını kontrol edin
# backend/main.py dosyasında
```

#### 3. 500 Internal Server Error
**Sorun**: Backend hatası
**Çözüm**:
```bash
# Render log'larını kontrol edin
# Render Dashboard > Services > Logs

# Environment variables'ları kontrol edin
# MONGODB_URI, TELEGRAM_BOT_TOKEN, vb.
```

#### 4. Timeout Errors
**Sorun**: Job çok uzun sürüyor
**Çözüm**:
```bash
# Job süresini artırın (cron-job.org'da)
# Backend performansını kontrol edin
# Database bağlantısını kontrol edin
```

### Debug Komutları

```bash
# Cronjob durumunu kontrol edin
crontab -l

# Log dosyalarını kontrol edin
tail -f logs/*.log

# Backend durumunu kontrol edin
curl https://buzz2remote-backend.onrender.com/health

# Telegram bot'unu test edin
curl -X POST https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage \
  -d "chat_id=YOUR_CHAT_ID&text=Test message"
```

---

## 📊 Cron Expression Açıklamaları

| Expression | Açıklama |
|------------|----------|
| `*/14 * * * *` | Her 14 dakikada |
| `0 * * * *` | Her saat başı |
| `0 9 * * *` | Her gün saat 9:00 |
| `0 2 * * *` | Her gün saat 2:00 |
| `0 6 * * *` | Her gün saat 6:00 |
| `0 10 * * *` | Her gün saat 10:00 |
| `0 */2 * * *` | Her 2 saatte |
| `30 * * * *` | Her saat başı :30'da |

---

## 🔐 Güvenlik

### 1. API Key Kullanımı
- Tüm cronjob endpoint'lerinde API key doğrulaması yapın
- Güçlü, rastgele API key'ler kullanın
- API key'leri environment variable olarak saklayın

### 2. HTTPS Kullanımı
- Sadece HTTPS endpoint'lerini kullanın
- SSL sertifikalarını güncel tutun

### 3. Rate Limiting
- Endpoint'lerde rate limiting uygulayın
- Aşırı istekleri engelleyin

### 4. Log Monitoring
- Şüpheli aktiviteleri izleyin
- Başarısız giriş denemelerini loglayın

---

## 📈 Performans Optimizasyonu

### 1. Job Süreleri
- Job'ların 5 dakikadan az sürmesini sağlayın
- Uzun süren job'ları background task olarak çalıştırın

### 2. Retry Logic
- Başarısız job'lar için retry mekanizması ekleyin
- Exponential backoff kullanın

### 3. Monitoring
- Job performansını sürekli izleyin
- Response time'ları takip edin

### 4. Scaling
- Gerekirse job sıklığını azaltın
- Database bağlantılarını optimize edin

---

## 📞 Destek

Sorun yaşarsanız:
1. Log dosyalarını kontrol edin
2. Environment variables'ları doğrulayın
3. Backend durumunu kontrol edin
4. Telegram bildirimlerini kontrol edin

**Not**: Bu rehber Render ve cron-job.org platformları için hazırlanmıştır. Diğer platformlar için benzer adımları takip edebilirsiniz. 