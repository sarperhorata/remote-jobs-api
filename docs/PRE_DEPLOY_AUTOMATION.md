# 🚀 Pre-Deploy Automation System

Bu doküman Buzz2Remote projesi için geliştirilmiş otomatik test ve düzeltme sistemini açıklar.

## 📋 Özet

Pre-Deploy Automation sistemi, her deployment öncesi otomatik olarak:
- ✅ Testleri çalıştırır
- 🔍 Hataları tespit eder
- 🔧 Hataları otomatik düzeltmeye çalışır
- 🔄 Düzeltme sonrası testleri tekrar çalıştırır
- 📊 Detaylı raporlar oluşturur

## 🎯 Özellikler

### Otomatik Test Çalıştırma
- **Frontend**: React/TypeScript testleri, build testi, lint kontrolü
- **Backend**: Python testleri, API testleri, veritabanı testleri
- **Integration**: API entegrasyonu, veri akışı testleri
- **Security**: Güvenlik açığı taraması, hassas veri kontrolü

### Otomatik Hata Düzeltme
- **Syntax Errors**: ESLint auto-fix, noktalı virgül ekleme
- **Import Errors**: Dependency yeniden kurulumu, cache temizleme
- **Type Errors**: TypeScript tip düzeltmeleri
- **Build Errors**: Dependency ve syntax sorunlarını çözme
- **Test Failures**: Snapshot güncelleme, test cache temizleme

### Akıllı Retry Mekanizması
- Hata tespit edildiğinde otomatik düzeltme
- Düzeltme sonrası testleri tekrar çalıştırma
- 3 deneme hakkı ile başarı oranını artırma

## 🛠️ Kurulum

### 1. Sistem Kurulumu

```bash
# Script'leri çalıştırılabilir yap
chmod +x scripts/pre-deploy-automation.sh
chmod +x scripts/install-git-hooks.sh

# Git hooks'larını kur (otomatik çalışma için)
./scripts/install-git-hooks.sh
```

### 2. Konfigürasyon

`config/pre-deploy-config.json` dosyasını düzenleyerek sistem ayarlarını özelleştirebilirsiniz:

```json
{
  "testing": {
    "maxRetryAttempts": 3,
    "timeoutSeconds": 120
  },
  "autoFix": {
    "enabled": true,
    "maxFixAttempts": 2
  }
}
```

## 🔄 Kullanım

### Manuel Çalıştırma

```bash
# Tam test süiti
./scripts/pre-deploy-automation.sh

# Hızlı mod (daha kısa timeout)
QUICK_MODE=true ./scripts/pre-deploy-automation.sh

# Sadece frontend testleri
cd frontend && npm run test:quick
```

### Otomatik Çalışma

Git hooks kurulduktan sonra sistem otomatik olarak çalışır:

```bash
# Her commit öncesi hızlı testler
git commit -m "feat: yeni özellik eklendi"

# Ana branch'e push öncesi tam testler
git push origin main
```

### GitHub Actions

`.github/workflows/enhanced-ci-cd.yml` dosyası ile CI/CD pipeline entegrasyonu:

- Pull request açıldığında otomatik test
- Main branch'e push'ta deployment
- Hata durumunda otomatik rollback

## 📊 Test Türleri

### Frontend Testleri

1. **Syntax Tests** (Kritik)
   - Build structure validation
   - Import/export kontrolü
   - Component structure

2. **Unit Tests** (Kritik)
   - Component rendering
   - Function logic
   - State management

3. **Integration Tests**
   - API calls
   - User workflows
   - Data validation

4. **Build Test** (Kritik)
   - Production build
   - Asset optimization
   - Bundle analysis

5. **Lint Check**
   - Code style
   - Best practices
   - Potential bugs

### Backend Testleri

1. **Syntax Check** (Kritik)
   - Python syntax validation
   - Import checks

2. **Unit Tests** (Kritik)
   - Function testing
   - Class methods
   - Utility functions

3. **API Tests** (Kritik)
   - Endpoint responses
   - Status codes
   - Data validation

4. **Database Tests** (Kritik)
   - Connection
   - CRUD operations
   - Data integrity

5. **Integration Tests**
   - End-to-end workflows
   - External API calls
   - Service communication

## 🔧 Otomatik Düzeltmeler

### Desteklenen Hata Türleri

| Hata Türü | Otomatik Düzeltme | Açıklama |
|------------|-------------------|----------|
| Syntax Error | ✅ | ESLint auto-fix, noktalı virgül ekleme |
| Import Error | ✅ | Dependency reinstall, cache clear |
| Type Error | ✅ | TypeScript düzeltmeleri |
| Lint Error | ✅ | Otomatik kod formatlaması |
| Build Error | ✅ | Dependency ve syntax fixes |
| Test Failure | ✅ | Snapshot update, cache clear |
| Database Error | ❌ | Manuel müdahale gerekli |
| Memory Error | ❌ | Sistem kaynak sorunu |

### Düzeltme Stratejileri

1. **İlk Deneme**: Temel otomatik düzeltmeler
2. **İkinci Deneme**: Kapsamlı dependency temizliği
3. **Üçüncü Deneme**: Generic fixes ve son şans

## 📈 Raporlama

### Log Dosyaları

Tüm test sonuçları `deploy-logs/` klasöründe saklanır:

```
deploy-logs/
├── frontend_tests_1_20240101_120000.log
├── backend_tests_1_20240101_120000.log
├── deployment_report_20240101_120000.md
└── notifications.log
```

### Rapor İçeriği

- **Test Results**: Her test süitinin sonucu
- **Error Analysis**: Tespit edilen hata türleri
- **Auto-Fixes**: Uygulanan otomatik düzeltmeler
- **Performance Metrics**: Çalışma süreleri
- **Recommendations**: İyileştirme önerileri

## ⚙️ Gelişmiş Konfigürasyon

### Çevre Değişkenleri

```bash
export QUICK_MODE=true           # Hızlı test modu
export MAX_RETRY_ATTEMPTS=3      # Maksimum deneme sayısı
export TEST_TIMEOUT=120          # Test timeout (saniye)
export ENABLE_AUTO_FIX=true      # Otomatik düzeltme aktif
```

### Custom Scripts

Kendi script'lerinizi eklemek için `config/pre-deploy-config.json`:

```json
{
  "advanced": {
    "customScripts": {
      "beforeTests": ["./scripts/setup-test-env.sh"],
      "afterTests": ["./scripts/cleanup.sh"],
      "onSuccess": ["./scripts/notify-success.sh"],
      "onFailure": ["./scripts/alert-team.sh"]
    }
  }
}
```

## 🚨 Sorun Giderme

### Yaygın Sorunlar

1. **Permission Denied**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Module Not Found**
   ```bash
   cd frontend && npm install --legacy-peer-deps
   cd backend && pip install -r requirements.txt
   ```

3. **Git Hooks Çalışmıyor**
   ```bash
   ./scripts/install-git-hooks.sh
   ```

4. **Tests Timeout**
   ```bash
   export TEST_TIMEOUT=300  # 5 dakika timeout
   ```

### Debug Modu

Detaylı log almak için:

```bash
DEBUG=true ./scripts/pre-deploy-automation.sh
```

### Manuel Test Çalıştırma

Sistem sorunlarını kontrol etmek için:

```bash
# Frontend kontrolü
cd frontend
npm run test:quick -- --watchAll=false

# Backend kontrolü  
cd backend
python run_tests.py

# Build kontrolü
cd frontend && npm run build
```

## 🔄 Git Hook Detayları

### Pre-Commit Hook
- Hızlı testler (60 saniye timeout)
- Lint fixes
- Hassas veri kontrolü
- Büyük dosya kontrolü

### Pre-Push Hook
- Tam test süiti (protected branches için)
- Build verification
- Security scans
- Performance checks

### Commit Message Hook
- Conventional commit format kontrolü
- Otomatik changelog generation

## 📞 Destek

Sistem ile ilgili sorunlar için:

1. **Log dosyalarını kontrol edin**: `deploy-logs/`
2. **Debug modunu çalıştırın**: `DEBUG=true`
3. **Manual testleri deneyin**: Her test süitini ayrı ayrı
4. **Konfigürasyonu kontrol edin**: `config/pre-deploy-config.json`

## 🔮 Gelecek Özellikler

- [ ] AI-powered error analysis
- [ ] Performance regression detection
- [ ] Automated dependency updates
- [ ] Visual test reports
- [ ] Slack/Teams notifications
- [ ] Custom notification webhooks
- [ ] Test parallelization optimization
- [ ] Docker integration
- [ ] Kubernetes deployment automation

---

## 📝 Notlar

- Sistem hataları otomatik düzeltmeye çalışır ama her zaman başarılı olmayabilir
- Kritik hataları manuel olarak düzeltmeniz gerekebilir
- Protected branch'lerde daha kapsamlı testler çalışır
- Emergency deployment için `--no-verify` flag'i kullanılabilir (tavsiye edilmez)

**⚠️ Önemli**: Emergency deployment haricinde hook'ları bypass etmeyin!