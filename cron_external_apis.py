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
        Rate limit strategy:
        - Fantastic Jobs: 15 requests/month = her 2 günde 1 (1,3,5,7,9,11,13,15,17,19,21,23,25,27,29)
        - Job Posting Feed: 5 requests/month = haftada 1 (1,8,15,22,29)
        - RemoteOK: 24 requests/day = her gün
        - Arbeitnow Free: 500,000 requests/month = her gün (çok cömert!)
        """
        today = datetime.now()
        
        # Fantastic Jobs için eski strateji
        fantastic_days = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
        
        # Job Posting Feed için ultra konservatif (ayda 5 kez)
        job_posting_days = [1, 8, 15, 22, 29]
        
        # RemoteOK için günlük (24/day rate limit)
        remoteok_daily = True  # Her gün çalışabilir
        
        # Arbeitnow Free için günlük (500,000/month rate limit - super cömert!)
        arbeitnow_daily = True  # Her gün çalışabilir
        
        # Herhangi bir API için çalıştırma günü ise true döndür
        return (today.day in fantastic_days or 
                today.day in job_posting_days or 
                remoteok_daily or 
                arbeitnow_daily)
    
    def get_next_run_date(self) -> datetime:
        """Bir sonraki çalıştırma tarihini hesapla"""
        today = datetime.now()
        all_target_days = [1, 3, 5, 7, 8, 9, 11, 13, 15, 17, 19, 21, 22, 23, 25, 27, 29]
        
        # Bugünden sonraki ilk target day'i bul
        for day in sorted(all_target_days):
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
        
        today = datetime.now()
        fantastic_days = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
        job_posting_days = [1, 8, 15, 22, 29]
        
        run_fantastic = today.day in fantastic_days
        run_job_posting = today.day in job_posting_days
        run_remoteok = True  # Her gün çalış
        
        # En az bir API çalışacaksa devam et
        if not (run_fantastic or run_job_posting or run_remoteok):
            next_run = self.get_next_run_date()
            
            self.notifier._send_message(f"""⏳ <b>EXTERNAL APIS - SCHEDULED SKIP</b>

🚫 <b>Bugün çalıştırma günü değil</b>
📅 <b>Bugün:</b> {datetime.now().strftime('%Y-%m-%d')}
⏭️ <b>Sonraki çalıştırma:</b> {next_run.strftime('%Y-%m-%d %H:%M')}

💡 <b>Rate limit stratejisi:</b>
• Fantastic Jobs: 15/month (günler: 1,3,5,7,9,11,13,15,17,19,21,23,25,27,29)
• Job Posting Feed: 5/month (günler: 1,8,15,22,29)
• RemoteOK: 24/day (her gün)""")
            
            return {"status": "skipped", "reason": "not_scheduled_day"}
        
        # Hangi API'lerin çalışacağını belirle
        apis_to_run = []
        if run_fantastic:
            apis_to_run.append("Fantastic Jobs")
        if run_job_posting:
            apis_to_run.append("Job Posting Feed")
        if run_remoteok:
            apis_to_run.append("RemoteOK")
        
        self.notifier._send_message(f"""🚀 <b>EXTERNAL APIS - STARTING CRAWL</b>

✅ <b>Bugün çalıştırma günü</b>
📅 <b>Tarih:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
🎯 <b>APIs to run:</b> {', '.join(apis_to_run)}

🔄 <b>External API crawling başlıyor...</b>""")
        
        try:
            # Manuel API control ile çalıştır
            manager = self.manager
            
            # Sadece scheduled API'leri çalıştır
            if not run_fantastic and 'fantastic_jobs' in manager.apis:
                del manager.apis['fantastic_jobs']
            
            if not run_job_posting and 'job_posting_feed' in manager.apis:
                del manager.apis['job_posting_feed']
            
            if not run_remoteok and 'remoteok' in manager.apis:
                del manager.apis['remoteok']
            
            # Ana crawl fonksiyonunu çalıştır
            results = manager.fetch_all_jobs(max_jobs_per_api=100)
            save_results = manager.save_jobs_to_database(results)
            
            # Başarı bildirimi
            total_jobs = sum(save_results.values())
            
            results_text = []
            for api_name, count in save_results.items():
                if api_name == 'fantastic_jobs':
                    results_text.append(f"• Fantastic Jobs: {count} jobs")
                elif api_name == 'job_posting_feed':
                    results_text.append(f"• Job Posting Feed: {count} jobs")
                elif api_name == 'remoteok':
                    results_text.append(f"• RemoteOK: {count} jobs")
            
            self.notifier._send_message(f"""✅ <b>EXTERNAL APIS - CRAWL COMPLETE</b>

🎉 <b>Crawl başarıyla tamamlandı</b>
📊 <b>Toplam job:</b> {total_jobs}

🔧 <b>API Sonuçları:</b>
{chr(10).join(results_text)}

⏭️ <b>Sonraki çalıştırma:</b> {self.get_next_run_date().strftime('%Y-%m-%d %H:%M')}
🕐 <b>Bitiş zamanı:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
            
            return {"status": "success", "results": save_results, "total_jobs": total_jobs}
            
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