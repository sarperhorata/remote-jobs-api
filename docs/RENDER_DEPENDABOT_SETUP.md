# 🚀 Render'da Dependabot Kurulum Rehberi

## 📅 Tarih: 5 Ağustos 2025

## 🎯 Amaç
Dependabot değişikliklerinin production'da (Render) çalışması için gerekli kurulum ve konfigürasyon.

## ✅ Kurulum Adımları

### 1. GitHub Personal Access Token Oluşturma

#### Token Yetkileri:
- `repo` (Full control of private repositories)
- `workflow` (Update GitHub Action workflows)
- `write:packages` (Upload packages to GitHub Package Registry)
- `delete:packages` (Delete packages from GitHub Package Registry)

#### Token Oluşturma:
1. GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" tıklayın
3. Note: "Dependabot Monitor Token"
4. Expiration: "No expiration" (veya 90 days)
5. Select scopes: Yukarıdaki yetkileri seçin
6. "Generate token" tıklayın
7. Token'ı kopyalayın ve güvenli bir yere kaydedin

### 2. Render Dashboard Konfigürasyonu

#### Environment Variables Ekleme:
1. Render Dashboard → buzz2remote-api → Environment
2. "Add Environment Variable" tıklayın
3. Aşağıdaki değişkenleri ekleyin:

```bash
# GitHub Configuration
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_REPO=sarperhorata/buzz2remote

# Dependabot Configuration
DEPENDABOT_ENABLED=true
AUTO_MERGE_ENABLED=true
SECURITY_UPDATES_ONLY=true

# Telegram (DISABLED)
TELEGRAM_ENABLED=false
```

### 3. Render Cron Jobs Kurulumu

#### Dependabot Auto-Merge Service:
1. Render Dashboard → "New" → "Cron Job"
2. **Name:** `dependabot-auto-merge`
3. **Environment:** `Python`
4. **Build Command:**
```bash
pip install -r backend/requirements.txt
npm install --prefix frontend
```
5. **Start Command:**
```bash
python scripts/dependabot-monitor.py
```
6. **Schedule:** `0 */6 * * *` (Her 6 saatte bir)
7. **Branch:** `main`

#### Environment Variables:
```bash
PYTHON_VERSION=3.11.0
NODE_VERSION=18
ENVIRONMENT=production
GITHUB_TOKEN=your-github-token
GITHUB_REPO=sarperhorata/buzz2remote
DEPENDABOT_ENABLED=true
AUTO_MERGE_ENABLED=true
SECURITY_UPDATES_ONLY=true
TELEGRAM_ENABLED=false
```

#### Security Monitor Service:
1. Render Dashboard → "New" → "Cron Job"
2. **Name:** `dependency-security-monitor`
3. **Environment:** `Python`
4. **Build Command:**
```bash
pip install -r backend/requirements.txt
npm install --prefix frontend
```
5. **Start Command:**
```bash
python scripts/security-monitor.py
```
6. **Schedule:** `0 2 * * *` (Her gün saat 02:00)
7. **Branch:** `main`

#### Environment Variables:
```bash
PYTHON_VERSION=3.11.0
NODE_VERSION=18
ENVIRONMENT=production
GITHUB_TOKEN=your-github-token
TELEGRAM_ENABLED=false
```

### 4. External API Crawler (Mevcut)
- **Name:** `external-api-crawler`
- **Schedule:** `0 9 * * *` (Her gün saat 09:00)
- **Start Command:** `python scripts/cron/cron_external_apis.py`

### 5. Database Cleanup (Mevcut)
- **Name:** `database-cleanup`
- **Schedule:** `0 2 * * 0` (Her Pazar saat 02:00)
- **Start Command:** `python scripts/cron/cron_database_cleanup.py`

## 🔧 Konfigürasyon Dosyaları

### 1. render.yaml Güncellemesi
`config/render.yaml` dosyası zaten güncellenmiş durumda. İçerik:

```yaml
services:
  # Backend API Service
  - type: web
    name: buzz2remote-api
    # ... mevcut konfigürasyon ...
    envVars:
      # ... mevcut değişkenler ...
      # Dependabot Configuration
      - key: DEPENDABOT_ENABLED
        value: true
      - key: AUTO_MERGE_ENABLED
        value: true
      - key: SECURITY_UPDATES_ONLY
        value: true

  # Dependabot Auto-Merge Service (Cron Job)
  - type: cron
    name: dependabot-auto-merge
    runtime: python
    rootDir: .
    buildCommand: |
      pip install -r backend/requirements.txt
      npm install --prefix frontend
    startCommand: python scripts/dependabot-monitor.py
    plan: starter
    schedule: "0 */6 * * *"
    # ... environment variables ...

  # Security Monitor Service (Cron Job)
  - type: cron
    name: dependency-security-monitor
    # ... konfigürasyon ...
```

### 2. Script Dosyaları
- `scripts/dependabot-monitor.py` ✅ Oluşturuldu
- `scripts/security-monitor.py` ✅ Oluşturuldu

## 🧪 Test Etme

### 1. Manuel Test:
```bash
# Dependabot Monitor test
python scripts/dependabot-monitor.py

# Security Monitor test
python scripts/security-monitor.py
```

### 2. Render Log Kontrolü:
1. Render Dashboard → Cron Jobs
2. İlgili service'i seçin
3. "Logs" tab'ına gidin
4. Son çalışma loglarını kontrol edin

### 3. GitHub Issues Kontrolü:
1. GitHub → Issues
2. "security" label'ı ile filtreleme
3. Otomatik oluşturulan issue'ları kontrol edin

## 📊 Monitoring ve Raporlama

### 1. Log Dosyaları:
- `logs/dependabot-monitor.log`
- `logs/security-monitor.log`
- `logs/dependabot-report-*.json`
- `logs/security-report-*.json`

### 2. GitHub Issues:
- Security vulnerabilities için otomatik issue oluşturma
- Major updates için review checklist
- Auto-merge başarı bildirimleri

### 3. Render Metrics:
- Cron job başarı oranları
- Execution süreleri
- Error rates

## 🔄 Otomatik İşlemler

### Dependabot Auto-Merge:
1. **Her 6 saatte bir** Dependabot PR'larını kontrol eder
2. **Security/minor/patch** güncellemelerini otomatik merge eder
3. **Major** güncellemeler için manuel review gerektirir
4. **CI status** kontrolü yapar
5. **Labels** ekler
6. **Comments** ekler

### Security Monitor:
1. **Her gün saat 02:00** güvenlik kontrolü yapar
2. **Frontend** npm audit çalıştırır
3. **Backend** safety check çalıştırır
4. **Outdated dependencies** kontrol eder
5. **Critical/High** vulnerabilities için GitHub issue oluşturur
6. **Detaylı rapor** oluşturur

## 🚨 Troubleshooting

### Yaygın Sorunlar:

#### 1. GitHub Token Yetkisi:
```bash
# Token'ın doğru yetkilere sahip olduğunu kontrol edin
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

#### 2. Rate Limiting:
```bash
# GitHub API rate limit kontrolü
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

#### 3. Render Build Failures:
```bash
# Log kontrolü
# Render Dashboard → Service → Logs
```

#### 4. Script Execution Errors:
```bash
# Manuel test
cd /path/to/project
python scripts/dependabot-monitor.py
```

### Debug Komutları:
```bash
# Environment variables kontrolü
echo $GITHUB_TOKEN
echo $GITHUB_REPO

# Script permissions
chmod +x scripts/dependabot-monitor.py
chmod +x scripts/security-monitor.py

# Log directory oluşturma
mkdir -p logs
```

## 📋 Checklist

### Kurulum Öncesi:
- [ ] GitHub Personal Access Token oluşturuldu
- [ ] Token yetkileri doğru ayarlandı
- [ ] Render account aktif
- [ ] Repository Render'a bağlı

### Kurulum Sonrası:
- [ ] Environment variables eklendi
- [ ] Cron jobs oluşturuldu
- [ ] Script dosyaları yüklendi
- [ ] İlk test çalıştırıldı
- [ ] Log dosyaları kontrol edildi
- [ ] GitHub issues kontrol edildi

### Monitoring:
- [ ] Cron job başarı oranları kontrol edildi
- [ ] Log dosyaları düzenli kontrol ediliyor
- [ ] GitHub issues takip ediliyor
- [ ] Security alerts kontrol ediliyor

## 🎯 Sonuç

### Başarı Kriterleri:
- ✅ Dependabot PR'ları otomatik merge ediliyor
- ✅ Security vulnerabilities otomatik tespit ediliyor
- ✅ GitHub issues otomatik oluşturuluyor
- ✅ Log dosyaları düzenli oluşturuluyor
- ✅ Render cron jobs düzenli çalışıyor

### Gelecek İyileştirmeler:
1. **Advanced Notifications:** Slack/Discord entegrasyonu
2. **Performance Monitoring:** Dependency update performans etkisi
3. **Rollback Automation:** Başarısız güncellemeler için otomatik rollback
4. **Custom Rules:** Proje özel kuralları

---

**Son Güncelleme:** 5 Ağustos 2025  
**Durum:** ✅ Render kurulum rehberi tamamlandı 