#!/usr/bin/env python3
"""
Automated Service Monitoring for Buzz2Remote
Tüm servisleri kontrol edip otomatik bildirim gönderir
"""

import requests
import subprocess
import time
from datetime import datetime
from service_notifications import ServiceNotifier

class ServiceMonitor:
    def __init__(self):
        self.notifier = ServiceNotifier()
        
    def check_render_api(self) -> bool:
        """Render API durumunu kontrol et"""
        try:
            start_time = time.time()
            response = requests.get("https://buzz2remote-api.onrender.com/", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                self.notifier.notify_api_status(True, 
                    endpoint="buzz2remote-api.onrender.com/", 
                    response_time=response_time, 
                    status_code=200)
                return True
            else:
                self.notifier.notify_render_deploy(False, 
                    error_details=f"API responding with {response.status_code}")
                return False
        except Exception as e:
            self.notifier.notify_render_deploy(False, 
                error_details=f"Connection failed: {str(e)[:100]}")
            return False
    
    def check_netlify_frontend(self) -> bool:
        """Netlify frontend durumunu kontrol et"""
        try:
            response = requests.get("https://buzz2remote.netlify.app/", timeout=10)
            
            if response.status_code == 200 and "buzz2remote" in response.text.lower():
                self.notifier.notify_netlify_deploy(True)
                return True
            else:
                self.notifier.notify_netlify_deploy(False, 
                    error_details=f"Site not accessible or content missing")
                return False
        except Exception as e:
            self.notifier.notify_netlify_deploy(False, 
                error_details=f"Connection failed: {str(e)[:100]}")
            return False
    
    def check_mongodb_connection(self) -> bool:
        """MongoDB bağlantısını test et"""
        try:
            # Test MongoDB connection
            result = subprocess.run([
                'python3', '-c', 
                'from database import get_db; db=get_db(); db.command("ismaster"); print("OK")'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.notifier.notify_mongodb_status(True, connection_type="Local")
                return True
            else:
                self.notifier.notify_mongodb_status(False, 
                    error_details=result.stderr[:150])
                return False
        except Exception as e:
            self.notifier.notify_mongodb_status(False, 
                error_details=str(e)[:150])
            return False
    
    def check_github_status(self) -> bool:
        """GitHub repository durumunu kontrol et"""
        try:
            # Get latest commit info
            result = subprocess.run([
                'git', 'log', '-1', '--format=%H|%s'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                commit_hash, commit_message = result.stdout.strip().split('|', 1)
                self.notifier.notify_github_deploy(True, 
                    commit_hash=commit_hash, 
                    commit_message=commit_message)
                return True
            else:
                self.notifier.notify_github_deploy(False, 
                    error_details="Cannot access git repository")
                return False
        except Exception as e:
            self.notifier.notify_github_deploy(False, 
                error_details=str(e)[:150])
            return False
    
    def run_daily_health_check(self):
        """Günlük sağlık kontrolü"""
        print(f"🔍 Starting daily health check - {datetime.now()}")
        
        results = {
            "render_api": self.check_render_api(),
            "netlify_frontend": self.check_netlify_frontend(), 
            "mongodb": self.check_mongodb_connection(),
            "github": self.check_github_status()
        }
        
        # Summary notification
        success_count = sum(results.values())
        total_count = len(results)
        
        summary_msg = f"""📊 <b>GÜNLÜK SİSTEM RAPORU</b>

✅ <b>Başarılı Servisler:</b> {success_count}/{total_count}

🔧 <b>Servis Durumları:</b>
{'🟢' if results['render_api'] else '🔴'} Render API
{'🟢' if results['netlify_frontend'] else '🔴'} Netlify Frontend  
{'🟢' if results['mongodb'] else '🔴'} MongoDB
{'🟢' if results['github'] else '🔴'} GitHub

🕐 <b>Kontrol zamanı:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 <b>Sistem:</b> buzz2remote.com"""
        
        self.notifier._send_message(summary_msg)
        
        print(f"✅ Health check completed - {success_count}/{total_count} services healthy")
        return results

if __name__ == "__main__":
    print("🚀 Buzz2Remote Service Monitor")
    monitor = ServiceMonitor()
    
    # Run health check
    monitor.run_daily_health_check() 