# 🧪 Test Automation Setup

## 🎯 Amaç
Bu test sistemi, kod değişikliklerinden sonra her şeyin düzgün çalıştığından emin olmak için kurulmuştur. Artık her commit öncesi testler çalışacak ve hata varsa commit engellencek.

## 📁 Test Yapısı

```
backend/
├── tests/
│   ├── unit/           # Birim testleri
│   ├── integration/    # Entegrasyon testleri
│   ├── api/           # API testleri
│   └── conftest.py    # Test konfigürasyonu
├── pytest.ini        # Pytest ayarları
├── test_before_commit.py  # Hızlı test runner
└── .git-hooks/pre-commit  # Git hook
```

## 🚀 Kullanım

### Manuel Test Çalıştırma

```bash
# Tüm testleri çalıştır
pytest

# Sadece unit testler
pytest tests/unit/ -v

# Sadece API testler
pytest tests/api/ -v

# Coverage raporu ile
pytest --cov=. --cov-report=html

# Hızlı pre-commit testleri
python test_before_commit.py
```

### Test Türleri

#### 🔧 Unit Tests
- Database fonksiyonları
- Utility fonksiyonları
- Data validation

#### 🌐 API Tests  
- Health check endpoints
- Basic endpoint responses

#### 🔗 Integration Tests
- Admin panel routes
- Full workflow tests

## 🛡️ Pre-commit Protection

Her commit öncesi otomatik olarak çalışan testler:
- Unit tests
- Basic API tests
- Database tests

Eğer testler başarısız olursa, commit engellenir!

## 📊 Test Coverage

```bash
# HTML coverage raporu oluştur
pytest --cov=. --cov-report=html:htmlcov

# Raporu aç
open htmlcov/index.html
```

## 🔄 Sürekli Entegrasyon

### Test-Driven Development Süreci:

1. **Kod Değişikliği Yap**
2. **Testleri Çalıştır** → `python test_before_commit.py`
3. **Testler Başarılı mı?**
   - ✅ Evet → Commit yapabilirsin
   - ❌ Hayır → Hataları düzelt, tekrar test et

### Git Hook Kurulumu

```bash
# Backend dizininde
chmod +x .git-hooks/pre-commit

# Git'e hook'u kullanmasını söyle (project root'ta)
ln -sf ../../backend/.git-hooks/pre-commit .git/hooks/pre-commit
```

## 🐛 Test Yazma Rehberi

### Yeni Unit Test Ekleme

```python
# tests/unit/test_my_feature.py
import pytest

@pytest.mark.unit
def test_my_function():
    # Test kodun buraya
    assert True
```

### Yeni API Test Ekleme

```python
# tests/api/test_my_api.py
import pytest
from fastapi import status

@pytest.mark.api
def test_my_endpoint(client):
    response = client.get("/my-endpoint")
    assert response.status_code == status.HTTP_200_OK
```

## 🚨 Sorun Giderme

### Test Başarısız Oluyorsa:

1. **Hata mesajını oku**
2. **Loglara bak**
3. **Debugging yap:**
   ```bash
   pytest tests/unit/test_database.py::test_specific_function -v -s
   ```

### Mock Sorunları:
- External serviceler mock'lanmıştır
- Database mongomock kullanır
- Authentication gerekirse token mock'lanır

## 📈 Gelecek İyileştirmeler

- [ ] Daha fazla API test kapsamı
- [ ] Performance testleri
- [ ] End-to-end testler
- [ ] CI/CD pipeline entegrasyonu
- [ ] Test otomasyonu ile frontend testleri

## 💡 İpuçları

- **Hızlı test için:** `python test_before_commit.py`
- **Detaylı analiz için:** `pytest --cov=. -v`
- **Specific test için:** `pytest tests/unit/test_database.py::test_name -v`
- **Test eklemeyi unutma!** Her yeni feature için test yaz

---

> ⚡ **Artık her kod değişikliğinde testler çalışacak ve projen daha stabil olacak!** 