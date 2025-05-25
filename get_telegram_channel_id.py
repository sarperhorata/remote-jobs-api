#!/usr/bin/env python3
"""
Utility script to get Telegram Channel ID for @buzz2remote

Bu script, @buzz2remote kanalının doğru chat ID'sini almanıza yardımcı olur.
"""

import requests
import json
import os
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not available, using system env vars")

# Bot token from environment
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
    print("Please set TELEGRAM_BOT_TOKEN in your .env file or environment")
    exit(1)

def get_bot_updates():
    """Telegram botundan güncellemeleri al"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('ok'):
            updates = data.get('result', [])
            print(f"✅ {len(updates)} güncelleme bulundu")
            
            # Channel mesajlarını filtrele
            channel_chats = []
            
            for update in updates:
                if 'message' in update:
                    message = update['message']
                    chat = message.get('chat', {})
                    
                    # Kanal mesajlarını bul
                    if chat.get('type') in ['channel', 'supergroup']:
                        chat_info = {
                            'id': chat.get('id'),
                            'title': chat.get('title'),
                            'username': chat.get('username'),
                            'type': chat.get('type')
                        }
                        
                        if chat_info not in channel_chats:
                            channel_chats.append(chat_info)
            
            if channel_chats:
                print("\n📢 Bulunan kanallar:")
                for i, chat in enumerate(channel_chats, 1):
                    print(f"{i}. {chat['title']} (@{chat.get('username', 'N/A')})")
                    print(f"   ID: {chat['id']}")
                    print(f"   Tip: {chat['type']}")
                    
                    if chat.get('username') == 'buzz2remote':
                        print(f"   🎯 DOĞRU KANAL BULUNDU! Chat ID: {chat['id']}")
                        return chat['id']
                    print()
            else:
                print("\n⚠️ Hiç kanal mesajı bulunamadı.")
                print("Bot'u @buzz2remote kanalına admin olarak ekleyin ve bir mesaj gönderin.")
                
        else:
            print(f"❌ API hatası: {data.get('description', 'Bilinmeyen hata')}")
            
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
    
    return None

def test_send_message(chat_id):
    """Test mesajı gönder"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    message = f"🤖 Test mesajı - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nBu mesaj Buzz2Remote bot tarafından gönderildi."
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('ok'):
            print(f"✅ Test mesajı başarıyla gönderildi!")
            return True
        else:
            print(f"❌ Mesaj gönderilemedi: {data.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Mesaj gönderme hatası: {str(e)}")
        return False

def main():
    print("🚀 Buzz2Remote Telegram Kanal ID Bulucu")
    print("=" * 50)
    
    print(f"📝 Bot Token: {BOT_TOKEN[:20]}..." if BOT_TOKEN else "❌ Bot Token not found")
    
    # Güncellemeleri al
    channel_id = get_bot_updates()
    
    if channel_id:
        print(f"\n🎯 @buzz2remote kanal ID'si: {channel_id}")
        
        # Test mesajı göndermeyi dene
        print("\n🧪 Test mesajı gönderiliyor...")
        if test_send_message(channel_id):
            print(f"\n✅ Başarılı! .env dosyasında TELEGRAM_CHAT_ID'yi şu değerle güncelleyin:")
            print(f"TELEGRAM_CHAT_ID={channel_id}")
        
    else:
        print("\n📋 Adımlar:")
        print("1. @BotFather'dan aldığınız bot'u @buzz2remote kanalına admin olarak ekleyin")
        print("2. Kanala herhangi bir mesaj gönderin")
        print("3. Bu scripti tekrar çalıştırın")
        
        # Manuel kontrol linki
        print(f"\n🔗 Manuel kontrol için:")
        print(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")

if __name__ == "__main__":
    main() 