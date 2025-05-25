#!/usr/bin/env python3
"""
Cronjob Script for External API Job Crawling
Fantastic Jobs ve diğer external API'leri scheduled olarak çalıştırır
"""

import os
import sys
import time
from datetime import datetime, timedelta
from external_job_apis import ExternalJobAPIManager, run_external_api_crawler
from service_notifications import ServiceNotifier

class ExternalAPICronJob:
    def __init__(self):
        self.notifier = ServiceNotifier()
        self.manager = ExternalJobAPIManager()
        
    def should_run_today(self) -> bool:
        """
        Rate limit: 15 requests/month = yaklaşık her 2 günde 1
        Aylık 15 isteği optimal dağıtmak için
        """
        today = datetime.now()
        
        # Ayın 1., 3., 5., 7., 9., 11., 13., 15., 17., 19., 21., 23., 25., 27., 29. günlerinde çalış
        target_days = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
        
        return today.day in target_days
    
    def get_next_run_date(self) -> datetime:
        """Bir sonraki çalıştırma tarihini hesapla"""
        today = datetime.now()
        target_days = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
        
        # Bugünden sonraki ilk target day'i bul
        for day in target_days:
            if day > today.day:
                next_run = today.replace(day=day, hour=9, minute=0, second=0)
                return next_run
        
        # Bu ayda kalan target day yok, gelecek aya geç
        next_month = today.replace(month=today.month + 1 if today.month < 12 else 1,
                                  year=today.year + 1 if today.month == 12 else today.year,
                                  day=1, hour=9, minute=0, second=0)
        return next_month
    
    def run_scheduled_crawl(self):
        """Scheduled crawl çalıştır"""
        
        if not self.should_run_today():
            next_run = self.get_next_run_date()
            
            self.notifier._send_message(f"""⏳ <b>EXTERNAL APIS - SCHEDULED SKIP</b>

🚫 <b>Bugün çalıştırma günü değil</b>
📅 <b>Bugün:</b> {datetime.now().strftime('%Y-%m-%d')}
⏭️ <b>Sonraki çalıştırma:</b> {next_run.strftime('%Y-%m-%d %H:%M')}

💡 <b>Rate limit stratejisi:</b> Ayda 15 istek
🎯 <b>Hedef günler:</b> 1,3,5,7,9,11,13,15,17,19,21,23,25,27,29""")
            
            return {"status": "skipped", "reason": "not_scheduled_day"}
        
        # Çalıştırma zamanı gelmiş
        self.notifier._send_message(f"""🚀 <b>EXTERNAL APIS - STARTING CRAWL</b>

✅ <b>Bugün çalıştırma günü</b>
📅 <b>Tarih:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
🎯 <b>Rate limit:</b> 15 requests/month strategy

🔄 <b>External API crawling başlıyor...</b>""")
        
        try:
            # Ana crawl fonksiyonunu çalıştır
            results = run_external_api_crawler()
            
            # Başarı bildirimi
            total_jobs = sum(results.values())
            
            self.notifier._send_message(f"""✅ <b>EXTERNAL APIS - CRAWL COMPLETE</b>

🎉 <b>Crawl başarıyla tamamlandı</b>
📊 <b>Toplam job:</b> {total_jobs}

🔧 <b>API Sonuçları:</b>
• Fantastic Jobs: {results.get('fantastic_jobs', 0)} jobs

⏭️ <b>Sonraki çalıştırma:</b> {self.get_next_run_date().strftime('%Y-%m-%d %H:%M')}
🕐 <b>Bitiş zamanı:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
            
            return {"status": "success", "results": results, "total_jobs": total_jobs}
            
        except Exception as e:
            # Hata bildirimi
            error_msg = str(e)[:300]
            
            self.notifier._send_message(f"""❌ <b>EXTERNAL APIS - CRAWL ERROR</b>

🚫 <b>Crawl sırasında hata oluştu</b>
❌ <b>Hata:</b> {error_msg}

⏭️ <b>Sonraki deneme:</b> {self.get_next_run_date().strftime('%Y-%m-%d %H:%M')}
🕐 <b>Hata zamanı:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
            
            return {"status": "error", "error": error_msg}

def main():
    """Ana cronjob fonksiyonu"""
    
    print(f"🚀 External API Cronjob Started - {datetime.now()}")
    print("=" * 60)
    
    # Environment variables check
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('TELEGRAM_CHAT_ID'):
        print("❌ Telegram environment variables not set!")
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        sys.exit(1)
    
    try:
        cron_job = ExternalAPICronJob()
        result = cron_job.run_scheduled_crawl()
        
        print(f"📊 Cronjob Result: {result['status']}")
        
        if result['status'] == 'success':
            print(f"✅ Successfully crawled {result['total_jobs']} jobs")
        elif result['status'] == 'skipped':
            print(f"⏳ Skipped: {result['reason']}")
        elif result['status'] == 'error':
            print(f"❌ Error: {result['error']}")
        
        print(f"🏁 Cronjob Completed - {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Fatal cronjob error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 