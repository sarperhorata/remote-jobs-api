# GitHub Workflow Otomasyon Sistemi

Bu dokümantasyon, Buzz2Remote projesinde GitHub workflow'larındaki problemleri otomatik olarak çözen ve izleyen sistemin nasıl çalıştığını açıklar.

## 🎯 Sistem Amacı

GitHub workflow'larında her gün tekrarlanan problemleri otomatik olarak çözmek ve projenin sürekli entegrasyon sürecini iyileştirmek.

## 🔧 Otomatik Düzeltme Sistemi

### 1. Auto Fix Workflow (`.github/workflows/auto-fix.yml`)

**Çalışma Zamanı:**
- Her gün saat 02:00'de otomatik
- Manuel tetikleme mümkün
- Dependency değişikliklerinde tetiklenir

**Yaptığı İşlemler:**

#### Frontend Düzeltmeleri:
- ✅ Linting problemlerini otomatik düzeltir (`npm run lint:fix`)
- ✅ Kod formatını düzeltir (`npm run format`)
- ✅ Type checking yapar
- ✅ Eski dependency'leri kontrol eder

#### Backend Düzeltmeleri:
- ✅ Black ile kod formatını düzeltir
- ✅ isort ile import'ları sıralar
- ✅ autopep8 ile linting problemlerini düzeltir
- ✅ Security kontrolleri yapar (bandit, safety)
- ✅ Eski Python dependency'lerini kontrol eder

#### Test Coverage İyileştirme:
- ✅ Frontend ve backend test coverage'ını analiz eder
- ✅ Coverage raporları oluşturur
- ✅ Düşük coverage alanlarını tespit eder

#### Dependency Yönetimi:
- ✅ Frontend ve backend dependency'lerini kontrol eder
- ✅ Security audit yapar
- ✅ Güncelleme önerileri sunar

#### Performance Monitoring:
- ✅ Frontend bundle boyutunu analiz eder
- ✅ Build sürelerini izler
- ✅ Performance raporları oluşturur

### 2. Workflow Monitor (`.github/workflows/workflow-monitor.yml`)

**Çalışma Zamanı:**
- Her gün saat 06:00'da otomatik
- Diğer workflow'lar tamamlandığında
- Manuel tetikleme mümkün

**İzlediği Metrikler:**
- ❌ Başarısız workflow çalışmaları
- 🐌 Yavaş çalışan workflow'lar (30+ dakika)
- 🔄 Tekrarlayan problemler
- 📊 Coverage düşüşleri
- 🔒 Security problemleri
- 📦 Dependency problemleri

## 📋 Oluşturulan Raporlar

### 1. Auto-Fix Raporları
- `coverage-report.md` - Test coverage analizi
- `dependency-report.md` - Dependency yönetimi
- `performance-report.md` - Performance analizi
- `auto-fix-summary.md` - Genel özet

### 2. Monitoring Raporları
- `workflow-report-YYYYMMDD.md` - Günlük workflow raporu
- `workflow-monitor.log` - Detaylı log dosyası
- GitHub Issues - Otomatik oluşturulan problem raporları

## 🚀 Kullanım

### Manuel Çalıştırma

```bash
# Auto-fix script'ini manuel çalıştır
./scripts/auto-fix-common-issues.sh

# Workflow monitoring'i çalıştır
python scripts/workflow-monitor.py
```

### GitHub Actions'ta Manuel Tetikleme

1. GitHub repository'de "Actions" sekmesine git
2. İlgili workflow'u seç
3. "Run workflow" butonuna tıkla
4. Branch seç ve çalıştır

## 📊 Monitoring Dashboard

### Otomatik Oluşturulan GitHub Issues

Sistem aşağıdaki etiketlerle GitHub issue'ları oluşturur:

- `auto-fix` - Otomatik düzeltme raporları
- `monitoring` - Workflow izleme raporları
- `workflow` - Workflow ile ilgili problemler
- `automation` - Otomasyon sistemi raporları
- `trends` - Trend analizi raporları
- `maintenance` - Bakım raporları

### Issue Örnekleri

```
🤖 Auto-Fix Summary - 2025-08-02
📊 Workflow Monitoring Report - 2025-08-02
📈 Workflow Trend Analysis - 2025-08-02
```

## ⚙️ Konfigürasyon

### Frontend Konfigürasyonu

**Prettier (.prettierrc):**
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```

**Package.json Scripts:**
```json
{
  "lint:fix": "eslint src --ext .ts,.tsx,.js,.jsx --fix",
  "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
  "type-check": "tsc --noEmit"
}
```

### Backend Konfigürasyonu

**Black & isort (pyproject.toml):**
```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 88
```

## 🔍 Problem Tespiti

### Otomatik Tespit Edilen Problemler

1. **Linting Problemleri:**
   - ESLint hataları
   - Prettier format problemleri
   - TypeScript type hataları

2. **Backend Problemleri:**
   - Black format problemleri
   - Import sıralama problemleri
   - autopep8 linting problemleri

3. **Security Problemleri:**
   - npm audit bulguları
   - Python safety bulguları
   - Bandit security taraması

4. **Performance Problemleri:**
   - Yavaş workflow çalışmaları
   - Büyük bundle boyutları
   - Uzun build süreleri

5. **Coverage Problemleri:**
   - Düşük test coverage
   - Coverage düşüşleri
   - Test edilmemiş alanlar

## 🛠️ Sorun Giderme

### Yaygın Problemler ve Çözümleri

1. **Workflow Timeout:**
   - Timeout sürelerini artır
   - Workflow'u optimize et
   - Paralel job'ları kullan

2. **Permission Problemleri:**
   - GitHub token'larını kontrol et
   - Repository permission'larını kontrol et

3. **Dependency Problemleri:**
   - package.json ve requirements.txt'yi güncelle
   - Lock file'ları yeniden oluştur

4. **Test Problemleri:**
   - Test'leri düzelt
   - Mock'ları güncelle
   - Test environment'ını kontrol et

### Detaylı Troubleshooting

#### Workflow Çalışmıyor
```bash
# Workflow loglarını kontrol et
gh run list --limit 10
gh run view <run-id> --log

# Workflow'u manuel tetikle
gh workflow run auto-fix.yml
```

#### Auto-fix Script Çalışmıyor
```bash
# Script'i çalıştırılabilir yap
chmod +x scripts/auto-fix-common-issues.sh

# Dependencies'i kontrol et
npm list --depth=0  # Frontend
pip list  # Backend

# Script'i debug modda çalıştır
bash -x scripts/auto-fix-common-issues.sh
```

#### Monitoring Script Hataları
```bash
# Python dependencies'i kontrol et
pip install -r requirements.txt

# GitHub token'ı kontrol et
echo $GITHUB_TOKEN

# Script'i debug modda çalıştır
python -u scripts/workflow-monitor.py --debug
```

#### Performance Problemleri
```bash
# Bundle boyutunu analiz et
npm run build -- --analyze

# Workflow sürelerini kontrol et
gh run list --json name,conclusion,duration

# Cache'leri temizle
npm run clean
pip cache purge
```

## 📈 Performans Metrikleri

### İzlenen Metrikler

- **Workflow Başarı Oranı:** %95+
- **Ortalama Çalışma Süresi:** <30 dakika
- **Auto-fix Başarı Oranı:** %90+
- **Problem Tespit Oranı:** %85+

### Hedefler

- ✅ Günlük workflow problemlerini %80 azalt
- ✅ Manuel müdahale ihtiyacını %70 azalt
- ✅ Code quality'yi sürekli iyileştir
- ✅ Security problemlerini erken tespit et

## 🔄 Sürekli İyileştirme

### Otomatik Öğrenme

Sistem aşağıdaki yollarla kendini iyileştirir:

1. **Pattern Recognition:**
   - Tekrarlayan problemleri tespit eder
   - Çözüm pattern'lerini öğrenir
   - Otomatik düzeltme oranını artırır

2. **Trend Analysis:**
   - Workflow performans trendlerini analiz eder
   - Problem kaynaklarını tespit eder
   - Önleyici önlemler önerir

3. **Feedback Loop:**
   - Başarılı düzeltmeleri kaydeder
   - Başarısız düzeltmeleri analiz eder
   - Algoritmaları iyileştirir

## ❓ Sık Sorulan Sorular (Q&A)

### Genel Sorular

**Q: Auto-fix workflow'u ne sıklıkla çalışır?**
A: Her gün saat 02:00'de otomatik olarak çalışır. Ayrıca dependency değişikliklerinde ve manuel tetikleme ile de çalıştırılabilir.

**Q: Workflow'lar başarısız olursa ne olur?**
A: Sistem otomatik olarak problemleri tespit eder, düzeltmeye çalışır ve GitHub issue'su oluşturur. Manuel müdahale gerektiren durumlar için bildirim gönderir.

**Q: Auto-fix hangi problemleri çözebilir?**
A: Linting hataları, format problemleri, import sıralama, security vulnerabilities, dependency güncellemeleri ve coverage problemleri.

**Q: Monitoring raporları nerede bulunur?**
A: GitHub Issues'da `monitoring` etiketi ile, workflow artifacts'larında ve `workflow-report-YYYYMMDD.md` dosyalarında.

### Teknik Sorular

**Q: Script'ler çalışmazsa ne yapmalıyım?**
A: Önce `chmod +x scripts/*.sh` komutu ile script'leri çalıştırılabilir yapın. Sonra dependencies'i kontrol edin ve debug modda çalıştırın.

**Q: GitHub token'ı nasıl ayarlarım?**
A: Repository Settings > Secrets and variables > Actions > New repository secret ile `GITHUB_TOKEN` ekleyin.

**Q: Workflow timeout olursa ne yapmalıyım?**
A: Workflow dosyasında `timeout-minutes` değerini artırın veya workflow'u optimize edin.

**Q: Performance problemleri nasıl çözerim?**
A: Bundle boyutunu analiz edin, cache'leri temizleyin, paralel job'ları kullanın ve gereksiz adımları kaldırın.

### Konfigürasyon Soruları

**Q: Cron schedule'ı nasıl değiştiririm?**
A: Workflow dosyalarındaki `cron` değerlerini değiştirin. Format: `'minute hour day month day-of-week'`

**Q: Hangi branch'lerde çalışır?**
A: Varsayılan olarak `main` ve `develop` branch'lerinde çalışır. `on.push.branches` kısmından değiştirebilirsiniz.

**Q: Email bildirimleri nasıl ayarlarım?**
A: `scripts/workflow-monitor.py` dosyasında email konfigürasyonunu yapın ve `send_email=True` parametresi ile çalıştırın.

**Q: Custom script'ler ekleyebilir miyim?**
A: Evet, `scripts/` klasörüne custom script'ler ekleyebilir ve workflow'larda çağırabilirsiniz.

### Monitoring Soruları

**Q: Monitoring raporları ne kadar süre saklanır?**
A: GitHub artifacts 7 gün, log dosyaları 30 gün saklanır. Bu süreleri workflow'larda ayarlayabilirsiniz.

**Q: Trend analizi nasıl çalışır?**
A: Sistem son 30 günün verilerini analiz eder ve pattern'leri tespit eder. Bu bilgiler trend raporlarında sunulur.

**Q: Security taraması hangi araçları kullanır?**
A: Frontend için `npm audit`, backend için `bandit` ve `safety` kullanılır.

**Q: Coverage hedefleri nasıl belirlenir?**
A: Varsayılan hedef %80'tir. Bu değeri `scripts/workflow-monitor.py` dosyasında değiştirebilirsiniz.

## 📞 Destek

### Sorun Bildirimi

1. GitHub Issues'da `automation` etiketi ile sorun bildir
2. Workflow log'larını kontrol et
3. Monitoring raporlarını incele

### Katkıda Bulunma

1. Script'leri iyileştir
2. Yeni problem tespit algoritmaları ekle
3. Dokümantasyonu güncelle

### İletişim

- **GitHub Issues:** `automation` etiketi ile
- **Email:** workflow-monitor@buzz2remote.com
- **Telegram:** @buzz2remote_bot

---

**Son Güncelleme:** 2025-08-02  
**Versiyon:** 1.1.0  
**Durum:** Aktif ✅  
**Sonraki Güncelleme:** Q&A bölümü eklendi, troubleshooting genişletildi 