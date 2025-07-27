#!/usr/bin/env python3
"""
Güvenlik Açıklarını Düzeltme Scripti
Bu script hardcoded secret'ları tespit eder ve güvenli hale getirir.
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

def backup_env_file(env_path):
    """Env dosyasının yedeğini al"""
    if os.path.exists(env_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{env_path}.backup.{timestamp}"
        shutil.copy2(env_path, backup_path)
        print(f"✅ {env_path} dosyasının yedeği alındı: {backup_path}")
        return backup_path
    return None

def fix_env_file(env_path):
    """Env dosyasındaki hardcoded secret'ları düzelt"""
    if not os.path.exists(env_path):
        print(f"❌ {env_path} dosyası bulunamadı")
        return False
    
    # Yedek al
    backup_path = backup_env_file(env_path)
    
    # Dosyayı oku
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Güvenlik açıklarını tespit et
    security_issues = []
    
    # Hardcoded secret pattern'leri
    patterns = [
        (r'TELEGRAM_BOT_TOKEN=([^\s]+)', 'TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here'),
        (r'STRIPE_SECRET_KEY=([^\s]+)', 'STRIPE_SECRET_KEY=your_stripe_secret_key'),
        (r'GOOGLE_CLIENT_SECRET=([^\s]+)', 'GOOGLE_CLIENT_SECRET=your_google_client_secret'),
        (r'LINKEDIN_CLIENT_SECRET=([^\s]+)', 'LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret'),
        (r'OPENAI_API_KEY=([^\s]+)', 'OPENAI_API_KEY=your_openai_api_key_here'),
        (r'EMAIL_PASSWORD=([^\s]+)', 'EMAIL_PASSWORD=your_gmail_app_password'),
        (r'SECRET_KEY=([^\s]+)', 'SECRET_KEY=your_super_secret_key_for_jwt_minimum_32_characters'),
        (r'JWT_SECRET=([^\s]+)', 'JWT_SECRET=your_jwt_secret_key_minimum_32_characters'),
    ]
    
    # Her pattern için kontrol et
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                if not match.startswith('your_') and len(match) > 10:
                    security_issues.append(f"Hardcoded secret found: {pattern.split('=')[0]}")
                    content = re.sub(pattern, replacement, content)
    
    # Dosyayı güncelle
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if security_issues:
        print(f"🔒 {env_path} dosyasındaki güvenlik açıkları düzeltildi:")
        for issue in security_issues:
            print(f"   - {issue}")
        return True
    else:
        print(f"✅ {env_path} dosyasında güvenlik açığı bulunamadı")
        return False

def check_git_history_for_secrets():
    """Git geçmişinde secret'ları kontrol et"""
    print("\n🔍 Git geçmişinde secret kontrolü yapılıyor...")
    
    # Git log'da secret'ları ara
    secret_patterns = [
        r'WPL_AP1\.wL2fdcuI4DxM8lL8\.R5LwwA==',
        r'sk_live_',
        r'GOCSPX-',
        r'8116251711:AAFhGxXtOJu2eCqCORoDr46XWq7ejqMeYnY'
    ]
    
    for pattern in secret_patterns:
        try:
            result = os.popen(f'git log --all --full-history -- "{pattern}"').read()
            if result.strip():
                print(f"⚠️  Git geçmişinde secret bulundu: {pattern}")
                print("   Bu secret'ları değiştirmeniz gerekiyor!")
        except Exception as e:
            print(f"❌ Git kontrolü sırasında hata: {e}")

def create_security_report():
    """Güvenlik raporu oluştur"""
    report = """
🔒 GÜVENLİK RAPORU
==================

✅ Yapılan Düzeltmeler:
- Hardcoded secret'lar placeholder'larla değiştirildi
- .env dosyalarının yedeği alındı

⚠️  Yapılması Gerekenler:
1. Tüm API key'lerini yeniden oluşturun
2. LinkedIn Client Secret'ı değiştirin
3. Stripe secret key'ini değiştirin
4. Telegram bot token'ını değiştirin
5. Google OAuth secret'ını değiştirin
6. OpenAI API key'ini değiştirin

🔧 Acil Eylemler:
1. LinkedIn Developer Console'dan yeni client secret oluşturun
2. Stripe Dashboard'dan yeni secret key oluşturun
3. Telegram BotFather'dan yeni bot token oluşturun
4. Google Cloud Console'dan yeni OAuth secret oluşturun
5. OpenAI Dashboard'dan yeni API key oluşturun

📝 Not: Bu script sadece local dosyaları düzeltir. 
    Git geçmişindeki secret'ları temizlemek için manuel işlem gerekir.
"""
    
    with open('SECURITY_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("📄 Güvenlik raporu oluşturuldu: SECURITY_REPORT.md")

def main():
    """Ana fonksiyon"""
    print("🔒 Güvenlik Açıklarını Düzeltme Scripti")
    print("=" * 50)
    
    # Env dosyalarını düzelt
    env_files = [
        'config/.env',
        'backend/.env',
        '.env',
        'frontend/.env',
        'frontend/.env.local'
    ]
    
    fixed_count = 0
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"\n📁 {env_file} dosyası kontrol ediliyor...")
            if fix_env_file(env_file):
                fixed_count += 1
    
    # Git geçmişini kontrol et
    check_git_history_for_secrets()
    
    # Güvenlik raporu oluştur
    create_security_report()
    
    print(f"\n✅ İşlem tamamlandı! {fixed_count} dosya düzeltildi.")
    print("📋 SECURITY_REPORT.md dosyasını kontrol edin.")

if __name__ == "__main__":
    main() 