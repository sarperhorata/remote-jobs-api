#!/usr/bin/env python3
"""
Telegram Channel Setup Helper for @buzz2remote

Bu script, @buzz2remote kanalının kurulumunu adım adım yapar.
"""

import requests
import json
import os
import time
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not available, using system env vars")

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
    exit(1)

def get_bot_info():
    """Bot bilgilerini al"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            return bot_info
        else:
            print(f"❌ Bot bilgisi alınamadı: {data.get('description')}")
            return None
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return None

def check_channel_membership():
    """Kanal üyeliğini kontrol et"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('ok'):
            updates = data.get('result', [])
            
            # buzz2remote kanalını ara
            for update in updates:
                if 'message' in update:
                    chat = update['message'].get('chat', {})
                    if chat.get('username') == 'buzz2remote':
                        return chat
            return None
        else:
            print(f"❌ Güncellemeler alınamadı: {data.get('description')}")
            return None
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return None

def send_test_message(chat_id):
    """Test mesajı gönder"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    message = f"🎉 <b>Buzz2Remote Bot Aktif!</b>\n\n" \
              f"✅ Bot başarıyla @buzz2remote kanalına bağlandı\n" \
              f"🕐 Kurulum zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n" \
              f"Artık tüm bildirimler bu kanala gelecek:\n" \
              f"• 🚀 Deployment bildirimleri\n" \
              f"• ❌ Error bildirimleri\n" \
              f"• 📊 Günlük crawler raporları"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get('ok'):
            return True
        else:
            print(f"❌ Test mesajı gönderilemedi: {data.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Test mesajı hatası: {str(e)}")
        return False

def update_env_file(chat_id):
    """Environment dosyasını güncelle"""
    print(f"\n📝 .env dosyasını güncelleyin:")
    print(f"TELEGRAM_CHAT_ID={chat_id}")
    print("\nOtomatik güncelleme için bu komutu çalıştırın:")
    print(f"sed -i 's/TELEGRAM_CHAT_ID=.*/TELEGRAM_CHAT_ID={chat_id}/' .env")

def main():
    print("🚀 Buzz2Remote Telegram Kanal Kurulumu")
    print("=" * 50)
    
    # Bot bilgilerini al
    bot_info = get_bot_info()
    if not bot_info:
        print("❌ Bot bilgilerine erişilemedi!")
        return
    
    print(f"🤖 Bot: @{bot_info.get('username', 'Bilinmiyor')}")
    print(f"📝 Bot ID: {bot_info.get('id')}")
    print(f"👤 Bot Adı: {bot_info.get('first_name')}")
    
    print(f"\n📋 ADIMLAR:")
    print(f"1. @buzz2remote kanalına gidin")
    print(f"2. Kanal ayarları → Administrators")
    print(f"3. Add Administrator → @{bot_info.get('username')} arayın")
    print(f"4. Bot'u admin yapın (mesaj gönderme yetkisi verin)")
    print(f"5. Kanala herhangi bir mesaj gönderin")
    print(f"6. Bu scripti tekrar çalıştırın")
    
    print(f"\n🔍 Kanal kontrolü yapılıyor...")
    
    # Kanal üyeliğini kontrol et
    channel_info = check_channel_membership()
    
    if channel_info:
        chat_id = channel_info['id']
        print(f"\n🎯 @buzz2remote kanalı bulundu!")
        print(f"📊 Kanal ID: {chat_id}")
        print(f"📢 Kanal Tipi: {channel_info.get('type')}")
        print(f"👥 Kanal Adı: {channel_info.get('title')}")
        
        # Test mesajı gönder
        print(f"\n📤 Test mesajı gönderiliyor...")
        if send_test_message(chat_id):
            print(f"✅ Test mesajı başarıyla gönderildi!")
            
            # .env güncellemesi
            update_env_file(chat_id)
            
            print(f"\n🎉 KURULUM TAMAMLANDI!")
            print(f"✅ Bot @buzz2remote kanalına bağlandı")
            print(f"✅ Test mesajı gönderildi")
            print(f"📝 .env dosyasını güncelleyerek kurulumu tamamlayın")
            
        else:
            print(f"❌ Test mesajı gönderilemedi!")
            print(f"Bot'un kanala mesaj gönderme yetkisi var mı kontrol edin")
            
    else:
        print(f"\n⚠️ @buzz2remote kanalı bulunamadı!")
        print(f"\nOlası sorunlar:")
        print(f"• Bot henüz kanala eklenmemiş")
        print(f"• Bot admin yetkisi almamış")
        print(f"• Kanala henüz mesaj gönderilmemiş")
        
        print(f"\n💡 Çözüm:")
        print(f"1. @{bot_info.get('username')} bot'unu @buzz2remote kanalına admin olarak ekleyin")
        print(f"2. Kanala herhangi bir mesaj gönderin")
        print(f"3. Bu scripti tekrar çalıştırın: python3 setup_telegram_channel.py")

if __name__ == "__main__":
    main() 