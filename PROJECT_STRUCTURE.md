# 📁 Proje Klasör Yapısı

## 🏗️ Ana Klasörler

### `/backend/` - Backend Uygulaması
- **FastAPI** tabanlı REST API
- **MongoDB** veritabanı
- **Pytest** test framework
- **CI/CD** pipeline entegrasyonu

### `/frontend/` - Frontend Uygulaması
- **React** tabanlı web uygulaması
- **TypeScript** desteği
- **Jest** test framework
- **Cypress** E2E testleri

### `/docs/` - Dokümantasyon
- API dokümantasyonu
- Kurulum rehberleri
- Teknik dokümanlar

## 📊 Raporlar ve Analizler

### `/reports/` - Proje Raporları
- **CI_CD_STATUS.md** - CI/CD pipeline durumu
- **FINAL_TODO_STATUS.md** - Tamamlanan görevler
- **BACKEND_OPTIMIZATIONS_FINAL.md** - Backend optimizasyonları
- **SECURITY_REPORT.md** - Güvenlik raporu
- **PROJECT_IMPROVEMENT_PLAN.md** - Proje geliştirme planı

## 🔧 Scriptler ve Otomasyonlar

### `/scripts/` - Otomasyon Scriptleri

#### `/scripts/cron/` - Cron Job Scriptleri
- **cron_database_backup.py** - Veritabanı yedekleme
- **cron_status_monitor.py** - Sistem durumu izleme
- **cron_job_statistics.py** - İş istatistikleri
- **cron_external_apis.py** - Dış API entegrasyonları

#### `/scripts/deployment/` - Deployment Scriptleri
- **check_render_logs.sh** - Render log kontrolü
- **debug_render_startup.py** - Render startup debug
- **test_render_deployment.sh** - Deployment testleri
- **setup_all_cronjobs.sh** - Cron job kurulumu

#### `/scripts/testing/` - Test Scriptleri
- **test_api_performance.sh** - API performans testleri
- **test_security_headers.sh** - Güvenlik header testleri
- **test_rate_limiting.sh** - Rate limiting testleri
- **test_cronjobs.sh** - Cron job testleri

#### `/scripts/backup/` - Yedekleme Scriptleri
- **backup.log** - Yedekleme logları
- **cron-job-org-config.md** - Cron job konfigürasyonu

### Diğer Scriptler
- **service_notifications.py** - Servis bildirimleri
- **performance_optimizer.py** - Performans optimizasyonu
- **setup-automation.sh** - Otomasyon kurulumu
- **start_services.sh** - Servis başlatma

## 📁 Veri ve Loglar

### `/data/` - Veri Dosyaları
- Crawler verileri
- İstatistik dosyaları
- Cache verileri

### `/logs/` - Log Dosyaları
- **/logs/old/** - Eski log dosyaları
- Sistem logları
- Hata logları

### `/temp/` - Geçici Dosyalar
- **/temp/old/** - Eski geçici dosyalar
- API request cache'leri
- Test dosyaları

## ⚙️ Konfigürasyon

### `/config/` - Konfigürasyon Dosyaları
- **RENDER_ENVIRONMENT_VARIABLES.md** - Render environment variables
- Veritabanı konfigürasyonu
- API konfigürasyonu

### `/.github/` - GitHub Konfigürasyonu
- **/workflows/** - CI/CD workflows
- **dependabot.yml** - Dependency updates
- GitHub Actions konfigürasyonu

## 🛠️ Geliştirme Araçları

### `/.vscode/` - VS Code Konfigürasyonu
- Debug konfigürasyonu
- Extension ayarları
- Workspace ayarları

### `/tools/` - Geliştirme Araçları
- Utility scriptleri
- Development tools
- Helper functions

## 📦 Deployment ve Backup

### `/backups/` - Yedekler
- Veritabanı yedekleri
- Sistem yedekleri
- Konfigürasyon yedekleri

### `/deploy-logs/` - Deployment Logları
- Render deployment logları
- CI/CD logları
- Error logları

## 🚀 Kullanım

### Geliştirme
```bash
# Backend geliştirme
cd backend && python -m pytest tests/

# Frontend geliştirme
cd frontend && npm run dev

# Test çalıştırma
./scripts/testing/test_api_performance.sh
```

### Deployment
```bash
# Deployment test
./scripts/deployment/test_render_deployment.sh

# Cron job kurulumu
./scripts/deployment/setup_all_cronjobs.sh
```

### Monitoring
```bash
# Log kontrolü
./scripts/deployment/check_render_logs.sh

# Performans testi
./scripts/testing/test_api_performance.sh
```

## 📋 Dosya Temizleme

### Gereksiz Dosyalar (Silindi)
- `__pycache__/` - Python cache
- `.DS_Store` - macOS system files
- `cookies.txt` - Geçici cookie dosyaları
- `.api_requests_*.json` - Eski API request cache'leri
- `conftest.py` - Root test config (backend'e taşındı)

### Organize Edilen Dosyalar
- **Raporlar** → `/reports/`
- **Scriptler** → `/scripts/` (kategorilere ayrıldı)
- **Loglar** → `/logs/old/`
- **Geçici dosyalar** → `/temp/old/`

---

**Son Güncelleme:** 27 Temmuz 2025  
**Durum:** ✅ Düzenli ve Organize 