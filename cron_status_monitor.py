#!/usr/bin/env python3
"""
Cron Status Monitor
Monitors the health and status of all cronjobs
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pymongo import MongoClient
from pathlib import Path
import requests
import psutil

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CronStatusMonitor:
    def __init__(self):
        """Initialize Cron Status Monitor"""
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/buzz2remote')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.buzz2remote
        self.cron_status_collection = self.db.cron_status
        self.notification_url = os.getenv('TELEGRAM_WEBHOOK_URL')  # For notifications
        
        self.expected_cronjobs = [
            {
                'name': 'Database Cleanup',
                'script': 'cron_database_cleanup.py',
                'frequency': 'daily',
                'max_runtime': 1800,  # 30 minutes
                'critical': True
            },
            {
                'name': 'External API Crawler',
                'script': 'cron_external_apis.py',
                'frequency': 'daily',
                'max_runtime': 3600,  # 1 hour
                'critical': True
            },
            {
                'name': 'Job Statistics',
                'script': 'cron_job_statistics.py',
                'frequency': 'daily',
                'max_runtime': 900,   # 15 minutes
                'critical': False
            },
            {
                'name': 'Distill Crawler',
                'script': 'cron_distill_crawler.py',
                'frequency': 'daily',
                'max_runtime': 1800,  # 30 minutes
                'critical': False
            },
            {
                'name': 'Keep Render Alive',
                'script': 'render_ping',
                'frequency': 'every_14_minutes',
                'max_runtime': 30,    # 30 seconds
                'critical': True
            },
            {
                'name': 'Health Check',
                'script': 'health_check.sh',
                'frequency': 'hourly',
                'max_runtime': 300,   # 5 minutes
                'critical': True
            },
            {
                'name': 'Test Timeout Monitor',
                'script': 'cron_test_timeout.py',
                'frequency': 'hourly',
                'max_runtime': 600,   # 10 minutes
                'critical': False
            }
        ]
    
    def get_active_cronjobs(self):
        """Get list of active cronjobs from crontab"""
        try:
            result = subprocess.run(['crontab', '-l'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                cron_lines = result.stdout.strip().split('\n')
                active_jobs = []
                
                for line in cron_lines:
                    if line.strip() and not line.startswith('#'):
                        active_jobs.append(line.strip())
                
                logger.info(f"📋 Found {len(active_jobs)} active cronjobs")
                return active_jobs
            else:
                logger.error(f"❌ Error getting crontab: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting active cronjobs: {e}")
            return []
    
    def check_log_file_status(self, log_file, max_age_hours=25):
        """Check if log file exists and has recent entries"""
        try:
            log_path = Path(log_file)
            
            if not log_path.exists():
                return {
                    'status': 'missing',
                    'message': f"Log file {log_file} does not exist",
                    'last_modified': None,
                    'size': 0
                }
            
            stat_info = log_path.stat()
            last_modified = datetime.fromtimestamp(stat_info.st_mtime)
            file_size = stat_info.st_size
            
            # Check if file has been modified recently
            age_hours = (datetime.now() - last_modified).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                status = 'stale'
                message = f"Log file is {age_hours:.1f} hours old"
            else:
                status = 'active'
                message = f"Log file updated {age_hours:.1f} hours ago"
            
            return {
                'status': status,
                'message': message,
                'last_modified': last_modified,
                'size': file_size,
                'age_hours': age_hours
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error checking log file: {e}",
                'last_modified': None,
                'size': 0
            }
    
    def check_process_running(self, script_name):
        """Check if a script process is currently running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if script_name in cmdline and 'python' in cmdline.lower():
                        return {
                            'running': True,
                            'pid': proc.info['pid'],
                            'cmdline': cmdline
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {'running': False, 'pid': None, 'cmdline': None}
            
        except Exception as e:
            logger.error(f"❌ Error checking process: {e}")
            return {'running': False, 'pid': None, 'cmdline': None}
    
    def check_database_health(self):
        """Check database connectivity and basic health"""
        try:
            # Test database connection
            self.client.admin.command('ping')
            
            # Get basic stats
            stats = self.db.command('dbstats')
            collections = self.db.list_collection_names()
            
            # Check critical collections
            critical_collections = ['jobs', 'companies', 'users']
            missing_collections = [col for col in critical_collections 
                                 if col not in collections]
            
            return {
                'status': 'healthy' if not missing_collections else 'warning',
                'message': 'Database connection OK' if not missing_collections 
                          else f"Missing collections: {missing_collections}",
                'collections_count': len(collections),
                'db_size_mb': round(stats.get('dataSize', 0) / 1024 / 1024, 2),
                'missing_collections': missing_collections
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Database connection failed: {e}",
                'collections_count': 0,
                'db_size_mb': 0,
                'missing_collections': []
            }
    
    def check_render_service(self):
        """Check Render service health"""
        try:
            render_url = 'https://buzz2remote-api.onrender.com/api/v1/health'
            response = requests.get(render_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'healthy',
                    'message': 'Render service is responsive',
                    'response_time': response.elapsed.total_seconds(),
                    'data': data
                }
            else:
                return {
                    'status': 'error',
                    'message': f"Render service returned {response.status_code}",
                    'response_time': response.elapsed.total_seconds(),
                    'data': None
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Failed to reach Render service: {e}",
                'response_time': None,
                'data': None
            }
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            usage = psutil.disk_usage('/')
            
            # Calculate percentages
            used_percent = (usage.used / usage.total) * 100
            free_gb = usage.free / (1024**3)
            
            if used_percent > 90:
                status = 'critical'
                message = f"Disk space critically low: {used_percent:.1f}% used"
            elif used_percent > 80:
                status = 'warning'
                message = f"Disk space running low: {used_percent:.1f}% used"
            else:
                status = 'healthy'
                message = f"Disk space OK: {used_percent:.1f}% used"
            
            return {
                'status': status,
                'message': message,
                'used_percent': round(used_percent, 1),
                'free_gb': round(free_gb, 2),
                'total_gb': round(usage.total / (1024**3), 2)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error checking disk space: {e}",
                'used_percent': 0,
                'free_gb': 0,
                'total_gb': 0
            }
    
    def analyze_cronjob_status(self, job_config):
        """Analyze status of a specific cronjob"""
        job_name = job_config['name']
        script_name = job_config['script']
        
        logger.info(f"🔍 Analyzing {job_name}")
        
        status_info = {
            'name': job_name,
            'script': script_name,
            'frequency': job_config['frequency'],
            'critical': job_config['critical'],
            'checks': {}
        }
        
        # Check if process is running
        process_status = self.check_process_running(script_name)
        status_info['checks']['process'] = process_status
        
        # Check log files
        possible_log_files = [
            f"{script_name.replace('.py', '')}.log",
            f"{script_name.replace('.py', '')}_cron.log",
            f"external_api_cron.log" if 'external' in script_name else None,
            f"render_ping.log" if 'render' in script_name else None
        ]
        
        log_status = None
        for log_file in possible_log_files:
            if log_file and Path(log_file).exists():
                log_status = self.check_log_file_status(log_file)
                status_info['checks']['log_file'] = {
                    'file': log_file,
                    **log_status
                }
                break
        
        if not log_status:
            status_info['checks']['log_file'] = {
                'file': None,
                'status': 'missing',
                'message': 'No log file found'
            }
        
        # Determine overall status
        if process_status['running']:
            overall_status = 'running'
        elif log_status and log_status['status'] == 'active':
            overall_status = 'healthy'
        elif log_status and log_status['status'] == 'stale':
            overall_status = 'stale'
        else:
            overall_status = 'inactive'
        
        status_info['overall_status'] = overall_status
        
        return status_info
    
    def generate_status_report(self):
        """Generate comprehensive status report"""
        logger.info("🚀 Generating cron status report")
        
        report = {
            'timestamp': datetime.now(),
            'summary': {
                'total_jobs': len(self.expected_cronjobs),
                'healthy_jobs': 0,
                'critical_issues': 0,
                'warnings': 0
            },
            'system_health': {},
            'cronjob_status': [],
            'active_crontab': [],
            'recommendations': []
        }
        
        # Check system health
        report['system_health']['database'] = self.check_database_health()
        report['system_health']['render_service'] = self.check_render_service()
        report['system_health']['disk_space'] = self.check_disk_space()
        
        # Get active crontab entries
        report['active_crontab'] = self.get_active_cronjobs()
        
        # Analyze each expected cronjob
        for job_config in self.expected_cronjobs:
            job_status = self.analyze_cronjob_status(job_config)
            report['cronjob_status'].append(job_status)
            
            # Update summary counts
            if job_status['overall_status'] == 'healthy':
                report['summary']['healthy_jobs'] += 1
            elif job_status['overall_status'] in ['inactive', 'error'] and job_config['critical']:
                report['summary']['critical_issues'] += 1
            elif job_status['overall_status'] == 'stale':
                report['summary']['warnings'] += 1
        
        # Generate recommendations
        recommendations = []
        
        # Check for critical issues
        critical_jobs = [job for job in report['cronjob_status'] 
                        if job['critical'] and job['overall_status'] in ['inactive', 'error']]
        
        if critical_jobs:
            for job in critical_jobs:
                recommendations.append({
                    'priority': 'critical',
                    'message': f"Critical job '{job['name']}' is {job['overall_status']}",
                    'action': f"Check and restart {job['script']}"
                })
        
        # Check system health issues
        if report['system_health']['database']['status'] != 'healthy':
            recommendations.append({
                'priority': 'critical',
                'message': "Database health issue detected",
                'action': "Check MongoDB connection and status"
            })
        
        if report['system_health']['disk_space']['status'] in ['warning', 'critical']:
            recommendations.append({
                'priority': 'high',
                'message': f"Disk space {report['system_health']['disk_space']['message']}",
                'action': "Clean up old logs and temporary files"
            })
        
        if len(report['active_crontab']) < 3:
            recommendations.append({
                'priority': 'high',
                'message': f"Only {len(report['active_crontab'])} cronjobs active, expected 7",
                'action': "Run setup_cronjobs.sh to restore missing cronjobs"
            })
        
        report['recommendations'] = recommendations
        
        # Save to database
        self.save_status_report(report)
        
        logger.info(f"✅ Status report generated: {report['summary']['healthy_jobs']}/{report['summary']['total_jobs']} jobs healthy")
        
        return report
    
    def save_status_report(self, report):
        """Save status report to database"""
        try:
            # Convert datetime objects to strings for JSON serialization
            report_copy = json.loads(json.dumps(report, default=str))
            
            self.cron_status_collection.insert_one(report_copy)
            
            # Keep only last 30 reports
            old_reports = list(self.cron_status_collection.find().sort('timestamp', -1).skip(30))
            for old_report in old_reports:
                self.cron_status_collection.delete_one({'_id': old_report['_id']})
            
            logger.info("💾 Status report saved to database")
            
        except Exception as e:
            logger.error(f"❌ Error saving status report: {e}")
    
    def send_alert_notification(self, report):
        """Send alert notifications for critical issues"""
        try:
            critical_issues = report['summary']['critical_issues']
            
            if critical_issues > 0 and self.notification_url:
                message = f"🚨 CRONJOB ALERT\n\n"
                message += f"Critical issues detected: {critical_issues}\n"
                message += f"Healthy jobs: {report['summary']['healthy_jobs']}/{report['summary']['total_jobs']}\n\n"
                
                for rec in report['recommendations']:
                    if rec['priority'] == 'critical':
                        message += f"❌ {rec['message']}\n"
                        message += f"   Action: {rec['action']}\n\n"
                
                # Send notification (implementation depends on notification service)
                logger.info(f"🔔 Sending alert notification for {critical_issues} critical issues")
                
        except Exception as e:
            logger.error(f"❌ Error sending alert notification: {e}")

def main():
    """Main function for cronjob execution"""
    try:
        monitor = CronStatusMonitor()
        
        # Generate status report
        report = monitor.generate_status_report()
        
        # Send alerts if needed
        monitor.send_alert_notification(report)
        
        # Print summary
        print(f"✅ Cron status check completed")
        print(f"📊 Healthy jobs: {report['summary']['healthy_jobs']}/{report['summary']['total_jobs']}")
        print(f"🚨 Critical issues: {report['summary']['critical_issues']}")
        print(f"⚠️ Warnings: {report['summary']['warnings']}")
        
        if report['recommendations']:
            print(f"\n📋 Recommendations:")
            for rec in report['recommendations'][:3]:  # Show top 3
                print(f"  {rec['priority'].upper()}: {rec['message']}")
        
        return 0 if report['summary']['critical_issues'] == 0 else 1
        
    except Exception as e:
        logger.error(f"❌ Cron status monitor failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 