#!/usr/bin/env python3
"""
Ping Service for Render Free Tier
Bu servis Render free tier'da servislerin uyku moduna geçmesini önler
"""

import os
import time
import requests
import logging
from datetime import datetime
from flask import Flask, jsonify

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

class PingService:
    def __init__(self):
        self.target_service = os.getenv('TARGET_SERVICE', 'buzz2remote-backend')
        self.ping_interval = int(os.getenv('PING_INTERVAL', 600))  # 10 minutes
        self.render_url = f"https://{self.target_service}.onrender.com"
        
    def ping_target_service(self):
        """Hedef servisi ping'le"""
        try:
            response = requests.get(f"{self.render_url}/health", timeout=30)
            if response.status_code == 200:
                logger.info(f"✅ Ping successful to {self.render_url}")
                return True
            else:
                logger.warning(f"⚠️ Ping failed to {self.render_url} - Status: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"❌ Ping error to {self.render_url}: {e}")
            return False
    
    def start_ping_loop(self):
        """Ping döngüsünü başlat"""
        logger.info(f"🚀 Starting ping service for {self.render_url}")
        logger.info(f"⏰ Ping interval: {self.ping_interval} seconds")
        
        while True:
            try:
                self.ping_target_service()
                time.sleep(self.ping_interval)
            except KeyboardInterrupt:
                logger.info("🛑 Ping service stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Ping loop error: {e}")
                time.sleep(60)  # 1 minute delay on error

# Flask routes
@app.route('/')
def home():
    return jsonify({
        "service": "Ping Service",
        "status": "running",
        "target": os.getenv('TARGET_SERVICE', 'buzz2remote-backend'),
        "interval": f"{os.getenv('PING_INTERVAL', 600)} seconds",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "ping-service",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/ping')
def ping():
    """Manual ping endpoint"""
    ping_service = PingService()
    success = ping_service.ping_target_service()
    
    return jsonify({
        "ping": "success" if success else "failed",
        "target": ping_service.render_url,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/trigger/auto-fix')
def trigger_auto_fix():
    """Auto-fix'i tetikle"""
    try:
        # Auto-fix script'ini çalıştır
        import subprocess
        result = subprocess.run(
            ['python', 'scripts/cron/cron_auto_fix.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return jsonify({
            "trigger": "auto-fix",
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "trigger": "auto-fix",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/trigger/workflow-monitor')
def trigger_workflow_monitor():
    """Workflow monitor'ü tetikle"""
    try:
        # Workflow monitor script'ini çalıştır
        import subprocess
        result = subprocess.run(
            ['python', 'scripts/cron/cron_workflow_monitor.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return jsonify({
            "trigger": "workflow-monitor",
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "trigger": "workflow-monitor",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/trigger/db-cleanup')
def trigger_db_cleanup():
    """Database cleanup'ı tetikle"""
    try:
        # Database cleanup script'ini çalıştır
        import subprocess
        result = subprocess.run(
            ['python', 'scripts/cron/cron_database_cleanup.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return jsonify({
            "trigger": "db-cleanup",
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "trigger": "db-cleanup",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/trigger/api-crawler')
def trigger_api_crawler():
    """External API crawler'ı tetikle"""
    try:
        # External API crawler script'ini çalıştır
        import subprocess
        result = subprocess.run(
            ['python', 'scripts/cron/cron_external_apis.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return jsonify({
            "trigger": "api-crawler",
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "trigger": "api-crawler",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/trigger/job-stats')
def trigger_job_stats():
    """Job statistics'i tetikle"""
    try:
        # Job statistics script'ini çalıştır
        import subprocess
        result = subprocess.run(
            ['python', 'scripts/cron/cron_job_statistics.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return jsonify({
            "trigger": "job-stats",
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "trigger": "job-stats",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def main():
    """Ana fonksiyon"""
    import threading
    
    # Ping service'i ayrı thread'de başlat
    ping_service = PingService()
    ping_thread = threading.Thread(target=ping_service.start_ping_loop, daemon=True)
    ping_thread.start()
    
    # Flask app'i başlat
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main() 