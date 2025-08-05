# Cronjob Kurulum Rehberi (FastCron ve Cron-job.org)

## 🎯 Genel Bakış
Bu rehber, Buzz2Remote projesinin cronjob'larını **FastCron (setcronjob.com)** ve **Cron-job.org** platformlarında nasıl kuracağınızı açıklar.

## ⚠️ Önemli Not: Ücretsiz Plan Kısıtlamaları
- **Cron-job.org**: Ücretsiz planında cronjob çalıştırma aralığı **minimum 30 dakikadır**. Daha sık aralıklar için ücretli plana geçmeniz gerekir.
- **FastCron (setcronjob.com)**: Ücretsiz planında **5 adet cronjob** için **minimum 5 dakikalık** çalıştırma aralığı sunar.

Bu nedenle, 5 dakikalık aralıklarla çalışan kritik cronjob'lar için **FastCron** tercih edilmelidir. Diğer, daha az kritik veya daha uzun aralıklı cronjob'lar için **Cron-job.org** kullanılabilir.

## 📋 Gereksinimler
- FastCron (setcronjob.com) hesabı
- Cron-job.org hesabı (isteğe bağlı, daha uzun aralıklar için)
- Telegram Bot Token (aktifse)
- Telegram Chat ID (aktifse)
- MongoDB URI
- `CRON_EXTERNAL_API_KEY` environment değişkeni

## 🔧 Kurulum Adımları

### 1. FastCron veya Cron-job.org'da Hesap Oluşturun
1.  **FastCron**: https://www.setcronjob.com adresine gidin ve "Sign up free" ile hesap oluşturun.
2.  **Cron-job.org**: https://cron-job.org adresine gidin ve "Sign up" ile hesap oluşturun (isteğe bağlı).
3.  Email doğrulamalarını tamamlayın.

### 2. Backend API Endpoint'lerini Hazırlayın

#### Render'da Deploy Edin
```bash
# Render'da backend servisini deploy edin ve URL'yi alın
# Örnek: https://remote-jobs-api-k9v1.onrender.com
```

#### Cronjob Endpoint'leri
Cronjob'lar için özel olarak tasarlanmış external endpoint'leri kullanacağız. Bu endpoint'ler, standart rate limiting'e takılmadan ve özel bir API key ile çağrılabilir.

**API Key**: `buzz2remote-cron-2024` (Bu değeri FastCron/cron-job.org kurulumunda "Custom HTTP Headers" veya "POST/GET parameters" kısmında `api_key=buzz2remote-cron-2024` olarak eklemelisiniz.)

### 3. FastCron'da Job'ları Oluşturun (5 Dakika Aralıklarla Çalışanlar İçin)

FastCron'un ücretsiz planında 5 adet cronjob ayarlayabilirsiniz. En kritik 5 tanesini aşağıda bulabilirsiniz:

| Job Adı                     | URL                                                                   | Sıklık (FastCron) | Method | Parametreler (API Key dahil)                       |
| :-------------------------- | :-------------------------------------------------------------------- | :---------------- | :----- | :------------------------------------------------- |
| **Health Check**            | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/health-check`           | Her 5 dakikada bir  | POST   | `api_key=buzz2remote-cron-2024`                    |
| **External API Crawler**    | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/external-apis`          | Her 5 dakikada bir  | POST   | `api_key=buzz2remote-cron-2024`                    |
| **Database Cleanup**        | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/database-cleanup`       | Her 5 dakikada bir  | POST   | `api_key=buzz2remote-cron-2024`                    |
| **Job Statistics**          | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/job-statistics`         | Her 5 dakikada bir  | POST   | `api_key=buzz2remote-cron-2024`                    |
| **Status Monitor**          | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/status-monitor`         | Her 5 dakikada bir  | POST   | `api_key=buzz2remote-cron-2024`                    |

**FastCron Kurulum İpuçları:**
- "Create Cron Job" veya benzeri bir buton arayın.
- "URL to call" kısmına yukarıdaki URL'yi yapıştırın.
- "Schedule" kısmında "5 minutes" veya "*/5 * * * *" seçeneğini ayarlayın.
- "HTTP Method" olarak "POST" seçin.
- "POST/GET parameters" veya "Custom HTTP Headers" kısmına `api_key=buzz2remote-cron-2024` ekleyin. Parametre olarak eklemek daha kolay olabilir.

### 4. Cron-job.org'da Job'ları Oluşturun (30 Dakika ve Üzeri Aralıklar İçin - İsteğe Bağlı)

Eğer yukarıdaki 5 cronjob dışında daha fazla veya daha seyrek çalışan cronjob'lara ihtiyacınız varsa, Cron-job.org'un 30 dakikalık limitine uygun olanları burada ayarlayabilirsiniz. Örnek olarak:

| Job Adı               | URL                                                              | Sıklık (cron-job.org) | Method | Parametreler (API Key dahil)                      |
| :-------------------- | :--------------------------------------------------------------- | :-------------------- | :----- | :------------------------------------------------ |
| **Render Keep-Alive** | `https://remote-jobs-api-k9v1.onrender.com/api/v1/health`        | Her 30 dakikada bir   | GET    | `api_key=buzz2remote-cron-2024`                   |
| **Distill Crawler**   | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/distill-crawler` | Günde bir (örn. 0 10 * * *)  | POST   | `api_key=buzz2remote-cron-2024`                   |
| **Test Timeout Monitor** | `https://remote-jobs-api-k9v1.onrender.com/api/v1/cron-external/test-timeout` | Her 30 dakikada bir (örn. 30 * * * *) | POST   | `api_key=buzz2remote-cron-2024`                   |

### 5. Environment Variables Ayarlayın

Render'da (veya kullandığınız herhangi bir ortamda) aşağıdaki environment variables'ları ayarlayın:

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/buzz2remote
TELEGRAM_BOT_TOKEN=your_telegram_bot_token # Telegram bildirimlerini kullanacaksanız
TELEGRAM_CHAT_ID=your_telegram_chat_id # Telegram bildirimlerini kullanacaksanız
API_KEY=your_secure_api_key_for_internal_cronjobs # Internal cronjob'lar için
CRON_EXTERNAL_API_KEY=buzz2remote-cron-2024 # FastCron gibi dış servisler için
```

### 6. Test Edin

1.  FastCron ve/veya Cron-job.org panellerinden her job'ı manuel olarak tetikleyin.
2.  Render loglarını kontrol edin (deploy'unuz başarılıysa).
3.  Eğer Telegram bildirimleri aktifse, bildirimleri kontrol edin.

## 🔍 Monitoring

### FastCron / Cron-job.org Dashboard
- Job durumlarını kontrol edin
- Başarı/başarısız oranlarını izleyin
- Response time'ları takip edin

### Telegram Bildirimleri (aktifse)
- Başarılı/başarısız job'lar için bildirim alın
- Hata durumlarında anında uyarı alın

### Log Monitoring
- Render loglarını kontrol edin
- Backend'in kendi loglarını izleyin

## 🚨 Troubleshooting

### Yaygın Sorunlar

1.  **401 Unauthorized**
    -   API key'in doğru olduğundan emin olun (`CRON_EXTERNAL_API_KEY` veya `API_KEY`).
    -   Header veya query parameter'ı doğru formatta gönderdiğinizden emin olun.
2.  **404 Not Found**
    -   URL'nin doğru olduğundan ve backend'in deploy edildiğinden emin olun.
    -   Render deploy loglarını kontrol edin.
3.  **500 Internal Server Error**
    -   Backend loglarını kontrol edin (Render dashboardunda).
    -   Environment variables'ların doğru ayarlandığından emin olun.
4.  **Timeout Errors**
    -   Job süresini artırın (FastCron/cron-job.org ayarlarından).
    -   Backend performansını kontrol edin. İşlemin çok uzun sürmediğinden emin olun.

## 📊 Cron Expression Açıklamaları

-   `*/5 * * * *` - Her 5 dakikada bir
-   `*/30 * * * *` - Her 30 dakikada bir
-   `0 * * * *` - Her saat başı
-   `0 9 * * *` - Her gün saat 9:00
-   `0 2 * * *` - Her gün saat 2:00
-   `0 6 * * *` - Her gün saat 6:00
-   `0 10 * * *` - Her gün saat 10:00
-   `0 */2 * * *` - Her 2 saatte
-   `30 * * * *` - Her saat başı :30'da

## 🔐 Güvenlik

1.  **API Key Kullanın**: Tüm cronjob endpoint'lerinde API key doğrulaması yapın.
2.  **HTTPS Kullanın**: Sadece HTTPS endpoint'lerini kullanın.
3.  **Rate Limiting**: Backend'de ve cron servislerinde rate limiting uygulayın.
4.  **Log Monitoring**: Şüpheli aktiviteleri izleyin.

## 📈 Performans Optimizasyonu

1.  **Job Süreleri**: Job'ların mümkün olduğunca kısa sürmesini sağlayın.
2.  **Retry Logic**: Başarısız job'lar için retry mekanizması ekleyin.
3.  **Monitoring**: Job performansını sürekli izleyin.
4.  **Scaling**: Gerekirse job sıklığını azaltın veya daha güçlü bir cron servisine geçiş yapın. 