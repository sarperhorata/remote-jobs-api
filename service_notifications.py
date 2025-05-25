#!/usr/bin/env python3
"""
Service Notifications for Buzz2Remote
Ayrı ayrı 3rd party service durumları için Telegram bildirimleri
"""

import os
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any

class ServiceNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
    
    def _send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Base method to send Telegram message"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, json=payload)
            return response.json().get('ok', False)
        except Exception as e:
            print(f"❌ Telegram notification error: {e}")
            return False
    
    def notify_crawler_status(self, success: bool, new_jobs: int = 0, updated_jobs: int = 0, 
                            total_jobs: int = 0, duration: str = "", errors: int = 0) -> bool:
        """Daily crawler status notification"""
        
        if success:
            icon = "✅"
            status = "BAŞARILI"
            color = "🟢"
        else:
            icon = "❌"
            status = "BAŞARISIZ"
            color = "🔴"
        
        message = f"""🕷️ <b>DAILY CRAWLER RAPORU</b>

{icon} <b>Durum:</b> {status} {color}
📊 <b>İstatistikler:</b>
• Yeni jobs: {new_jobs:,}
• Güncellenmiş: {updated_jobs:,}
• Toplam işlenen: {total_jobs:,}
• Hata sayısı: {errors}

⏱️ <b>Süre:</b> {duration}
🕐 <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 <b>Sistem:</b> buzz2remote.com"""
        
        return self._send_message(message)
    
    def notify_github_deploy(self, success: bool, commit_hash: str = "", 
                           commit_message: str = "", error_details: str = "") -> bool:
        """GitHub deployment notification"""
        
        if success:
            icon = "✅"
            status = "BAŞARILI"
            color = "🟢"
        else:
            icon = "❌"
            status = "BAŞARISIZ"
            color = "🔴"
        
        message = f"""🐙 <b>GITHUB DEPLOYMENT</b>

{icon} <b>Durum:</b> {status} {color}
📦 <b>Commit:</b> {commit_hash[:8] if commit_hash else 'N/A'}
📝 <b>Mesaj:</b> {commit_message[:100]}...

🔗 <b>Repository:</b> sarperhorata/remote-jobs-api
🕐 <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        if not success and error_details:
            message += f"\n\n❌ <b>Hata:</b>\n{error_details[:200]}..."
        
        return self._send_message(message)
    
    def notify_render_deploy(self, success: bool, url: str = "https://buzz2remote-api.onrender.com", 
                           build_time: str = "", error_details: str = "") -> bool:
        """Render deployment notification"""
        
        if success:
            icon = "✅"
            status = "BAŞARILI"
            color = "🟢"
        else:
            icon = "❌"
            status = "BAŞARISIZ"
            color = "🔴"
        
        message = f"""🚀 <b>RENDER DEPLOYMENT</b>

{icon} <b>Durum:</b> {status} {color}
🌐 <b>URL:</b> {url}
⏱️ <b>Build süresi:</b> {build_time}
🕐 <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 <b>Service:</b> buzz2remote-api"""

        if not success and error_details:
            message += f"\n\n❌ <b>Hata:</b>\n{error_details[:200]}..."
        
        return self._send_message(message)
    
    def notify_netlify_deploy(self, success: bool, url: str = "https://buzz2remote.netlify.app", 
                            deploy_id: str = "", error_details: str = "") -> bool:
        """Netlify deployment notification"""
        
        if success:
            icon = "✅"
            status = "BAŞARILI"
            color = "🟢"
        else:
            icon = "❌"
            status = "BAŞARISIZ"
            color = "🔴"
        
        message = f"""🌐 <b>NETLIFY DEPLOYMENT</b>

{icon} <b>Durum:</b> {status} {color}
🏠 <b>URL:</b> {url}
📍 <b>Deploy ID:</b> {deploy_id[:12] if deploy_id else 'N/A'}
🕐 <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎨 <b>Site:</b> buzz2remote.com"""

        if not success and error_details:
            message += f"\n\n❌ <b>Hata:</b>\n{error_details[:200]}..."
        
        return self._send_message(message)
    
    def notify_mongodb_status(self, success: bool, connection_type: str = "Atlas", 
                            db_name: str = "buzz2remote", error_details: str = "") -> bool:
        """MongoDB connection status notification"""
        
        if success:
            icon = "✅"
            status = "BAĞLANTI BAŞARILI"
            color = "🟢"
        else:
            icon = "❌"
            status = "BAĞLANTI HATASI"
            color = "🔴"
        
        message = f"""🗄️ <b>MONGODB DURUMU</b>

{icon} <b>Durum:</b> {status} {color}
🔗 <b>Bağlantı:</b> {connection_type}
📊 <b>Database:</b> {db_name}
🕐 <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💾 <b>Veri kaynağı:</b> buzz2remote.com"""

        if not success and error_details:
            message += f"\n\n❌ <b>Hata detayı:</b>\n{error_details[:200]}..."
        
        return self._send_message(message)
    
    def notify_api_status(self, success: bool, endpoint: str = "/", 
                         response_time: float = 0, status_code: int = 200) -> bool:
        """API health check notification"""
        
        if success:
            icon = "✅"
            status = "ÇALIŞIYOR"
            color = "🟢"
        else:
            icon = "❌"
            status = "ÇALIŞMIYOR"
            color = "🔴"
        
        message = f"""🔌 <b>API DURUM RAPORU</b>

{icon} <b>Durum:</b> {status} {color}
🌐 <b>Endpoint:</b> {endpoint}
⚡ <b>Response time:</b> {response_time:.2f}ms
📡 <b>Status code:</b> {status_code}
🕐 <b>Zaman:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 <b>API:</b> buzz2remote-api.onrender.com"""
        
        return self._send_message(message)

# Convenience functions for easy usage
def send_crawler_notification(success: bool, **kwargs):
    """Quick crawler notification"""
    notifier = ServiceNotifier()
    return notifier.notify_crawler_status(success, **kwargs)

def send_github_notification(success: bool, **kwargs):
    """Quick GitHub notification"""
    notifier = ServiceNotifier()
    return notifier.notify_github_deploy(success, **kwargs)

def send_render_notification(success: bool, **kwargs):
    """Quick Render notification"""
    notifier = ServiceNotifier()
    return notifier.notify_render_deploy(success, **kwargs)

def send_netlify_notification(success: bool, **kwargs):
    """Quick Netlify notification"""
    notifier = ServiceNotifier()
    return notifier.notify_netlify_deploy(success, **kwargs)

def send_mongodb_notification(success: bool, **kwargs):
    """Quick MongoDB notification"""
    notifier = ServiceNotifier()
    return notifier.notify_mongodb_status(success, **kwargs)

def send_api_notification(success: bool, **kwargs):
    """Quick API notification"""
    notifier = ServiceNotifier()
    return notifier.notify_api_status(success, **kwargs)

if __name__ == "__main__":
    print("🧪 Testing Service Notifications...")
    
    # Test all notification types
    notifier = ServiceNotifier()
    
    print("Testing crawler notification...")
    notifier.notify_crawler_status(True, new_jobs=679, updated_jobs=21062, total_jobs=21741, duration="6m 51s")
    
    print("Testing GitHub notification...")
    notifier.notify_github_deploy(True, commit_hash="e24dcc0", commit_message="Fix backend server startup")
    
    print("Testing Render notification...")
    notifier.notify_render_deploy(False, error_details="Service deployment pending")
    
    print("Testing MongoDB notification...")
    notifier.notify_mongodb_status(False, connection_type="Atlas", error_details="Authentication failed")
    
    print("✅ All notifications sent!") 