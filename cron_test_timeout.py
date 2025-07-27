#!/usr/bin/env python3
"""
Test Timeout Monitor Cronjob
Monitors for hanging tests and long-running processes
"""

import os
import sys
import json
import logging
import psutil
import signal
from datetime import datetime, timedelta
from pymongo import MongoClient
import subprocess

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTimeoutMonitor:
    def __init__(self):
        """Initialize Test Timeout Monitor"""
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/buzz2remote')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.buzz2remote
        self.timeout_logs_collection = self.db.timeout_logs
        
        # Timeout thresholds (in seconds)
        self.process_timeouts = {
            'pytest': 3600,        # 1 hour for tests
            'python': 7200,        # 2 hours for Python scripts
            'npm': 1800,           # 30 minutes for npm processes
            'node': 1800,          # 30 minutes for Node processes
            'crawl': 3600,         # 1 hour for crawlers
            'backup': 1800,        # 30 minutes for backups
        }
        
        # Critical processes that should never be killed
        self.protected_processes = [
            'mongod', 'postgres', 'redis-server', 'nginx', 'apache',
            'systemd', 'kernel', 'init', 'ssh', 'cron'
        ]
    
    def get_long_running_processes(self):
        """Get list of long-running processes that might be hanging"""
        try:
            long_running = []
            current_time = datetime.now()
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    proc_info = proc.info
                    if not proc_info['cmdline']:
                        continue
                    
                    cmdline = ' '.join(proc_info['cmdline'])
                    proc_name = proc_info['name'].lower()
                    
                    # Skip protected processes
                    if any(protected in proc_name for protected in self.protected_processes):
                        continue
                    
                    # Calculate process age
                    create_time = datetime.fromtimestamp(proc_info['create_time'])
                    age_seconds = (current_time - create_time).total_seconds()
                    
                    # Check if process matches our monitored types
                    timeout_threshold = None
                    process_type = None
                    
                    for proc_type, timeout in self.process_timeouts.items():
                        if proc_type in cmdline.lower() or proc_type in proc_name:
                            timeout_threshold = timeout
                            process_type = proc_type
                            break
                    
                    # If process is older than threshold, add to list
                    if timeout_threshold and age_seconds > timeout_threshold:
                        try:
                            memory_info = proc.memory_info()
                            cpu_percent = proc.cpu_percent()
                            
                            long_running.append({
                                'pid': proc_info['pid'],
                                'name': proc_name,
                                'cmdline': cmdline,
                                'process_type': process_type,
                                'age_seconds': int(age_seconds),
                                'age_hours': round(age_seconds / 3600, 2),
                                'memory_mb': round(memory_info.rss / 1024 / 1024, 2),
                                'cpu_percent': cpu_percent,
                                'create_time': create_time,
                                'timeout_threshold': timeout_threshold,
                                'should_terminate': age_seconds > (timeout_threshold * 1.5)  # 150% of threshold
                            })
                            
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by age (oldest first)
            long_running.sort(key=lambda x: x['age_seconds'], reverse=True)
            
            logger.info(f"🔍 Found {len(long_running)} long-running processes")
            return long_running
            
        except Exception as e:
            logger.error(f"❌ Error getting long-running processes: {e}")
            return []
    
    def check_test_processes(self):
        """Specifically check for hanging test processes"""
        try:
            test_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    proc_info = proc.info
                    if not proc_info['cmdline']:
                        continue
                    
                    cmdline = ' '.join(proc_info['cmdline'])
                    
                    # Look for test-related processes
                    test_indicators = ['pytest', 'test_', 'npm test', 'jest', 'mocha', 'unittest']
                    
                    if any(indicator in cmdline.lower() for indicator in test_indicators):
                        create_time = datetime.fromtimestamp(proc_info['create_time'])
                        age_seconds = (datetime.now() - create_time).total_seconds()
                        
                        try:
                            memory_info = proc.memory_info()
                            cpu_percent = proc.cpu_percent(interval=1)
                            
                            test_processes.append({
                                'pid': proc_info['pid'],
                                'name': proc_info['name'],
                                'cmdline': cmdline,
                                'age_seconds': int(age_seconds),
                                'age_minutes': round(age_seconds / 60, 1),
                                'memory_mb': round(memory_info.rss / 1024 / 1024, 2),
                                'cpu_percent': cpu_percent,
                                'create_time': create_time,
                                'likely_hanging': age_seconds > 1800 and cpu_percent < 5  # 30 min + low CPU
                            })
                            
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            logger.info(f"🧪 Found {len(test_processes)} active test processes")
            return test_processes
            
        except Exception as e:
            logger.error(f"❌ Error checking test processes: {e}")
            return []
    
    def check_system_resources(self):
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Load average (Unix-like systems)
            try:
                load_avg = os.getloadavg()
            except (OSError, AttributeError):
                load_avg = (0, 0, 0)  # Windows doesn't have load average
            
            return {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total_gb': round(memory.total / 1024**3, 2),
                    'used_gb': round(memory.used / 1024**3, 2),
                    'available_gb': round(memory.available / 1024**3, 2),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / 1024**3, 2),
                    'used_gb': round(disk.used / 1024**3, 2),
                    'free_gb': round(disk.free / 1024**3, 2),
                    'percent': round((disk.used / disk.total) * 100, 1)
                },
                'load_average': {
                    '1min': round(load_avg[0], 2),
                    '5min': round(load_avg[1], 2),
                    '15min': round(load_avg[2], 2)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking system resources: {e}")
            return {}
    
    def terminate_hanging_processes(self, processes, dry_run=True):
        """Terminate hanging processes (with dry run option)"""
        terminated = []
        failed = []
        
        for proc_info in processes:
            if not proc_info.get('should_terminate', False):
                continue
            
            pid = proc_info['pid']
            
            try:
                if dry_run:
                    logger.info(f"🔍 DRY RUN: Would terminate PID {pid} ({proc_info['name']})")
                    terminated.append({
                        'pid': pid,
                        'name': proc_info['name'],
                        'action': 'dry_run',
                        'reason': f"Running for {proc_info['age_hours']} hours"
                    })
                else:
                    proc = psutil.Process(pid)
                    
                    # First try graceful termination
                    proc.terminate()
                    
                    # Wait up to 10 seconds for graceful termination
                    try:
                        proc.wait(timeout=10)
                        action = 'terminated'
                    except psutil.TimeoutExpired:
                        # Force kill if graceful termination failed
                        proc.kill()
                        action = 'killed'
                    
                    logger.info(f"🔪 {action.upper()} PID {pid} ({proc_info['name']})")
                    
                    terminated.append({
                        'pid': pid,
                        'name': proc_info['name'],
                        'action': action,
                        'reason': f"Running for {proc_info['age_hours']} hours"
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.warning(f"⚠️ Failed to terminate PID {pid}: {e}")
                failed.append({
                    'pid': pid,
                    'name': proc_info['name'],
                    'error': str(e)
                })
        
        return {
            'terminated': terminated,
            'failed': failed,
            'dry_run': dry_run
        }
    
    def check_zombie_processes(self):
        """Check for zombie processes"""
        try:
            zombies = []
            
            for proc in psutil.process_iter(['pid', 'name', 'status', 'ppid']):
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        zombies.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'ppid': proc.info['ppid'],
                            'status': proc.info['status']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if zombies:
                logger.warning(f"🧟 Found {len(zombies)} zombie processes")
            
            return zombies
            
        except Exception as e:
            logger.error(f"❌ Error checking zombie processes: {e}")
            return []
    
    def analyze_timeouts(self):
        """Perform comprehensive timeout analysis"""
        logger.info("🚀 Starting timeout analysis")
        
        analysis = {
            'timestamp': datetime.now(),
            'long_running_processes': self.get_long_running_processes(),
            'test_processes': self.check_test_processes(),
            'zombie_processes': self.check_zombie_processes(),
            'system_resources': self.check_system_resources(),
            'summary': {
                'total_long_running': 0,
                'should_terminate': 0,
                'hanging_tests': 0,
                'zombie_count': 0,
                'high_cpu_usage': False,
                'high_memory_usage': False
            },
            'recommendations': []
        }
        
        # Calculate summary
        analysis['summary']['total_long_running'] = len(analysis['long_running_processes'])
        analysis['summary']['should_terminate'] = len([p for p in analysis['long_running_processes'] 
                                                     if p.get('should_terminate', False)])
        analysis['summary']['hanging_tests'] = len([p for p in analysis['test_processes'] 
                                                  if p.get('likely_hanging', False)])
        analysis['summary']['zombie_count'] = len(analysis['zombie_processes'])
        
        # Check system resource thresholds
        if analysis['system_resources'].get('cpu_percent', 0) > 80:
            analysis['summary']['high_cpu_usage'] = True
        
        if analysis['system_resources'].get('memory', {}).get('percent', 0) > 85:
            analysis['summary']['high_memory_usage'] = True
        
        # Generate recommendations
        recommendations = []
        
        if analysis['summary']['should_terminate'] > 0:
            recommendations.append({
                'priority': 'high',
                'message': f"{analysis['summary']['should_terminate']} processes should be terminated",
                'action': "Review long-running processes and terminate if hanging"
            })
        
        if analysis['summary']['hanging_tests'] > 0:
            recommendations.append({
                'priority': 'medium',
                'message': f"{analysis['summary']['hanging_tests']} test processes appear to be hanging",
                'action': "Investigate hanging test processes and restart if needed"
            })
        
        if analysis['summary']['zombie_count'] > 0:
            recommendations.append({
                'priority': 'low',
                'message': f"{analysis['summary']['zombie_count']} zombie processes detected",
                'action': "Restart parent processes to clean up zombies"
            })
        
        if analysis['summary']['high_memory_usage']:
            recommendations.append({
                'priority': 'high',
                'message': "High memory usage detected",
                'action': "Review memory-intensive processes and optimize"
            })
        
        analysis['recommendations'] = recommendations
        
        # Save analysis to database
        self.save_timeout_analysis(analysis)
        
        logger.info(f"✅ Timeout analysis completed: {analysis['summary']['total_long_running']} long-running processes")
        
        return analysis
    
    def save_timeout_analysis(self, analysis):
        """Save timeout analysis to database"""
        try:
            # Convert datetime objects for JSON serialization
            analysis_copy = json.loads(json.dumps(analysis, default=str))
            
            self.timeout_logs_collection.insert_one(analysis_copy)
            
            # Keep only last 24 hours of data
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.timeout_logs_collection.delete_many({
                'timestamp': {'$lt': cutoff_time}
            })
            
            logger.info("💾 Timeout analysis saved to database")
            
        except Exception as e:
            logger.error(f"❌ Error saving timeout analysis: {e}")

def main():
    """Main function for cronjob execution"""
    try:
        monitor = TestTimeoutMonitor()
        
        # Perform timeout analysis
        analysis = monitor.analyze_timeouts()
        
        # Print summary
        print(f"✅ Test timeout monitor completed")
        print(f"📊 Long-running processes: {analysis['summary']['total_long_running']}")
        print(f"🔪 Should terminate: {analysis['summary']['should_terminate']}")
        print(f"🧪 Hanging tests: {analysis['summary']['hanging_tests']}")
        print(f"🧟 Zombie processes: {analysis['summary']['zombie_count']}")
        
        if analysis['recommendations']:
            print(f"\n📋 Recommendations:")
            for rec in analysis['recommendations'][:3]:
                print(f"  {rec['priority'].upper()}: {rec['message']}")
        
        # Terminate hanging processes if requested via environment variable
        if os.getenv('TERMINATE_HANGING_PROCESSES') == 'true':
            logger.info("🔪 Terminating hanging processes (TERMINATE_HANGING_PROCESSES=true)")
            result = monitor.terminate_hanging_processes(
                analysis['long_running_processes'], 
                dry_run=False
            )
            print(f"🔪 Terminated {len(result['terminated'])} processes")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Test timeout monitor failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 