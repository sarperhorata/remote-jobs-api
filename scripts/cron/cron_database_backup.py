#!/usr/bin/env python3
"""
🗄️ AUTOMATED DATABASE BACKUP CRON JOB
Scheduled backup service for MongoDB with rotation and notifications
"""

import os
import sys
import json
import asyncio
import datetime
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / 'backend'))

from backend.scripts.database_backup import DatabaseBackupManager
import requests

class BackupCronJob:
    """Automated backup cron job with Telegram notifications"""
    
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.backup_manager = DatabaseBackupManager()
        
    async def run_scheduled_backup(self):
        """Run scheduled backup based on current time"""
        now = datetime.datetime.now()
        
        # Full backup: Every Sunday at 2 AM
        is_full_backup_time = now.weekday() == 6 and now.hour == 2
        
        # Incremental backup: Every day at 2 AM (except Sunday)
        is_incremental_backup_time = now.weekday() != 6 and now.hour == 2
        
        if is_full_backup_time:
            print("🔄 Starting scheduled full backup...")
            result = await self.backup_manager.create_full_backup()
            backup_type = "Full"
            
        elif is_incremental_backup_time:
            print("🔄 Starting scheduled incremental backup...")
            since_date = now - datetime.timedelta(days=1)
            result = await self.backup_manager.create_incremental_backup(since_date)
            backup_type = "Incremental"
            
        else:
            # Manual backup (called via API)
            print("🔄 Starting manual full backup...")
            result = await self.backup_manager.create_full_backup()
            backup_type = "Manual Full"
        
        # Cleanup old backups
        await self.backup_manager.cleanup_old_backups()
        
        # Send notification
        await self._send_backup_notification(result, backup_type)
        
        return result
    
    async def _send_backup_notification(self, result: dict, backup_type: str):
        """Send Telegram notification about backup status"""
        if not self.telegram_token or not self.telegram_chat_id:
            print("⚠️ Telegram credentials not configured")
            return
        
        try:
            if result['success']:
                info = result.get('backup_info', {})
                message = f"""
🗄️ **{backup_type} Backup Completed**
✅ Status: SUCCESS
📊 Documents: {info.get('total_documents', 'N/A')}
💾 Size: {info.get('total_size_mb', 'N/A')} MB
📅 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔗 ID: {result.get('backup_id', 'N/A')}
"""
            else:
                message = f"""
🗄️ **{backup_type} Backup Failed**
❌ Status: FAILED
📅 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🐛 Error: {result.get('error', 'Unknown error')}
"""
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print("📱 Telegram notification sent")
            else:
                print(f"⚠️ Telegram notification failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Notification error: {str(e)}")
    
    async def get_backup_status(self):
        """Get backup status for monitoring"""
        status = await self.backup_manager.get_backup_schedule_status()
        backups = await self.backup_manager.list_backups()
        
        # Calculate backup health
        now = datetime.datetime.now()
        last_backup_age = None
        
        if backups:
            last_backup_time = datetime.datetime.fromisoformat(backups[0]['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
            last_backup_age = (now - last_backup_time).total_seconds() / 3600  # hours
        
        health_status = "HEALTHY"
        if last_backup_age and last_backup_age > 25:  # More than 25 hours
            health_status = "WARNING"
        elif last_backup_age and last_backup_age > 49:  # More than 49 hours  
            health_status = "CRITICAL"
        
        return {
            'status': health_status,
            'last_backup_age_hours': last_backup_age,
            'total_backups': len(backups),
            'backup_statistics': status,
            'recent_backups': backups[:3]  # Last 3 backups
        }


async def main():
    """Main cron job execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup Cron Job')
    parser.add_argument('--action', choices=['backup', 'status'], default='backup')
    args = parser.parse_args()
    
    cron_job = BackupCronJob()
    
    try:
        if args.action == 'backup':
            result = await cron_job.run_scheduled_backup()
            print(json.dumps(result, indent=2))
            return 0 if result.get('success') else 1
            
        elif args.action == 'status':
            status = await cron_job.get_backup_status()
            print(json.dumps(status, indent=2))
            return 0
            
    except Exception as e:
        print(f"❌ Cron job failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 