#!/usr/bin/env python3
"""
Comprehensive Monitoring System for Backend
Tracks application metrics, database performance, API response times, error rates, and system resources
"""

import time
import psutil
import threading
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import redis
from redis.exceptions import RedisError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    load_average: List[float]

@dataclass
class ApplicationMetrics:
    """Application performance metrics"""
    timestamp: datetime
    active_connections: int
    request_count: int
    error_count: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float

@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    timestamp: datetime
    connection_count: int
    query_count: int
    slow_queries: int
    avg_query_time: float
    index_usage: Dict[str, int]
    collection_sizes: Dict[str, int]

@dataclass
class Alert:
    """Alert definition"""
    timestamp: datetime
    level: str  # 'info', 'warning', 'critical'
    category: str
    message: str
    metric_value: float
    threshold: float
    action_taken: str

class MonitoringSystem:
    """Comprehensive monitoring system for backend"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_history = {
            'system': deque(maxlen=1000),
            'application': deque(maxlen=1000),
            'database': deque(maxlen=1000)
        }
        self.alerts = deque(maxlen=500)
        self.alert_rules = self._load_alert_rules()
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Initialize connections
        self.mongo_client = None
        self.redis_client = None
        self._init_connections()
    
    def _init_connections(self):
        """Initialize database connections"""
        try:
            # MongoDB connection
            mongo_uri = self.config.get('mongodb_uri', 'mongodb://localhost:27017')
            self.mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.mongo_client.admin.command('ping')
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.mongo_client = None
        
        try:
            # Redis connection
            redis_host = self.config.get('redis_host', 'localhost')
            redis_port = self.config.get('redis_port', 6379)
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def _load_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load alert rules from configuration"""
        return {
            'cpu_high': {
                'metric': 'cpu_percent',
                'threshold': 80.0,
                'level': 'warning',
                'message': 'CPU usage is high'
            },
            'cpu_critical': {
                'metric': 'cpu_percent',
                'threshold': 95.0,
                'level': 'critical',
                'message': 'CPU usage is critical'
            },
            'memory_high': {
                'metric': 'memory_percent',
                'threshold': 85.0,
                'level': 'warning',
                'message': 'Memory usage is high'
            },
            'memory_critical': {
                'metric': 'memory_percent',
                'threshold': 95.0,
                'level': 'critical',
                'message': 'Memory usage is critical'
            },
            'disk_high': {
                'metric': 'disk_usage_percent',
                'threshold': 90.0,
                'level': 'warning',
                'message': 'Disk usage is high'
            },
            'response_time_slow': {
                'metric': 'avg_response_time',
                'threshold': 2000.0,  # 2 seconds
                'level': 'warning',
                'message': 'Response time is slow'
            },
            'error_rate_high': {
                'metric': 'error_rate',
                'threshold': 5.0,  # 5%
                'level': 'warning',
                'message': 'Error rate is high'
            },
            'db_connection_high': {
                'metric': 'connection_count',
                'threshold': 100,
                'level': 'warning',
                'message': 'Database connections are high'
            }
        }
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system resource metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_data = {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv
            }
            
            # Load average
            load_avg = list(psutil.getloadavg())
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io=network_data,
                load_average=load_avg
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application performance metrics"""
        try:
            # Get metrics from Redis if available
            if self.redis_client:
                request_count = int(self.redis_client.get('app:request_count') or 0)
                error_count = int(self.redis_client.get('app:error_count') or 0)
                response_times = self.redis_client.lrange('app:response_times', 0, -1)
                
                if response_times:
                    response_times = [float(rt) for rt in response_times]
                    avg_response_time = statistics.mean(response_times)
                    p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
                    p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
                else:
                    avg_response_time = p95_response_time = p99_response_time = 0.0
                
                active_connections = int(self.redis_client.get('app:active_connections') or 0)
            else:
                # Fallback to simulated metrics
                request_count = 0
                error_count = 0
                avg_response_time = p95_response_time = p99_response_time = 0.0
                active_connections = 0
            
            return ApplicationMetrics(
                timestamp=datetime.now(),
                active_connections=active_connections,
                request_count=request_count,
                error_count=error_count,
                avg_response_time=avg_response_time,
                p95_response_time=p95_response_time,
                p99_response_time=p99_response_time
            )
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return None
    
    def collect_database_metrics(self) -> DatabaseMetrics:
        """Collect database performance metrics"""
        try:
            if not self.mongo_client:
                return None
            
            db = self.mongo_client.get_database()
            
            # Connection count
            connection_count = len(self.mongo_client.server_info()['connections']['current'])
            
            # Collection sizes
            collection_sizes = {}
            for collection_name in db.list_collection_names():
                collection_sizes[collection_name] = db[collection_name].count_documents({})
            
            # Index usage (simplified)
            index_usage = {}
            for collection_name in db.list_collection_names():
                indexes = db[collection_name].index_information()
                index_usage[collection_name] = len(indexes)
            
            # Query metrics (simplified)
            query_count = 0
            slow_queries = 0
            avg_query_time = 0.0
            
            return DatabaseMetrics(
                timestamp=datetime.now(),
                connection_count=connection_count,
                query_count=query_count,
                slow_queries=slow_queries,
                avg_query_time=avg_query_time,
                index_usage=index_usage,
                collection_sizes=collection_sizes
            )
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            return None
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check metrics against alert rules"""
        alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            metric_value = None
            
            # Get metric value based on rule
            if rule['metric'] == 'cpu_percent' and metrics.get('system'):
                metric_value = metrics['system'].cpu_percent
            elif rule['metric'] == 'memory_percent' and metrics.get('system'):
                metric_value = metrics['system'].memory_percent
            elif rule['metric'] == 'disk_usage_percent' and metrics.get('system'):
                metric_value = metrics['system'].disk_usage_percent
            elif rule['metric'] == 'avg_response_time' and metrics.get('application'):
                metric_value = metrics['application'].avg_response_time
            elif rule['metric'] == 'error_rate' and metrics.get('application'):
                app_metrics = metrics['application']
                if app_metrics.request_count > 0:
                    metric_value = (app_metrics.error_count / app_metrics.request_count) * 100
            elif rule['metric'] == 'connection_count' and metrics.get('database'):
                metric_value = metrics['database'].connection_count
            
            # Check if alert should be triggered
            if metric_value is not None and metric_value > rule['threshold']:
                alert = Alert(
                    timestamp=datetime.now(),
                    level=rule['level'],
                    category=rule_name,
                    message=rule['message'],
                    metric_value=metric_value,
                    threshold=rule['threshold'],
                    action_taken='monitoring'
                )
                alerts.append(alert)
        
        return alerts
    
    def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info(f"Monitoring started with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoring stopped")
    
    def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                system_metrics = self.collect_system_metrics()
                app_metrics = self.collect_application_metrics()
                db_metrics = self.collect_database_metrics()
                
                # Store metrics
                if system_metrics:
                    self.metrics_history['system'].append(system_metrics)
                if app_metrics:
                    self.metrics_history['application'].append(app_metrics)
                if db_metrics:
                    self.metrics_history['database'].append(db_metrics)
                
                # Check alerts
                current_metrics = {
                    'system': system_metrics,
                    'application': app_metrics,
                    'database': db_metrics
                }
                alerts = self.check_alerts(current_metrics)
                
                # Store alerts
                for alert in alerts:
                    self.alerts.append(alert)
                    logger.warning(f"Alert: {alert.level.upper()} - {alert.message} "
                                 f"(Value: {alert.metric_value:.2f}, Threshold: {alert.threshold:.2f})")
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        summary = {
            'system': {},
            'application': {},
            'database': {},
            'alerts': []
        }
        
        # System metrics summary
        system_metrics = [m for m in self.metrics_history['system'] 
                         if m.timestamp > cutoff_time]
        if system_metrics:
            summary['system'] = {
                'avg_cpu': statistics.mean([m.cpu_percent for m in system_metrics]),
                'max_cpu': max([m.cpu_percent for m in system_metrics]),
                'avg_memory': statistics.mean([m.memory_percent for m in system_metrics]),
                'max_memory': max([m.memory_percent for m in system_metrics]),
                'avg_disk': statistics.mean([m.disk_usage_percent for m in system_metrics]),
                'max_disk': max([m.disk_usage_percent for m in system_metrics])
            }
        
        # Application metrics summary
        app_metrics = [m for m in self.metrics_history['application'] 
                      if m.timestamp > cutoff_time]
        if app_metrics:
            summary['application'] = {
                'total_requests': sum([m.request_count for m in app_metrics]),
                'total_errors': sum([m.error_count for m in app_metrics]),
                'avg_response_time': statistics.mean([m.avg_response_time for m in app_metrics]),
                'max_response_time': max([m.avg_response_time for m in app_metrics]),
                'avg_connections': statistics.mean([m.active_connections for m in app_metrics])
            }
        
        # Database metrics summary
        db_metrics = [m for m in self.metrics_history['database'] 
                     if m.timestamp > cutoff_time]
        if db_metrics:
            summary['database'] = {
                'avg_connections': statistics.mean([m.connection_count for m in db_metrics]),
                'max_connections': max([m.connection_count for m in db_metrics]),
                'total_queries': sum([m.query_count for m in db_metrics]),
                'slow_queries': sum([m.slow_queries for m in db_metrics])
            }
        
        # Alerts summary
        recent_alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
        summary['alerts'] = {
            'total': len(recent_alerts),
            'critical': len([a for a in recent_alerts if a.level == 'critical']),
            'warning': len([a for a in recent_alerts if a.level == 'warning']),
            'info': len([a for a in recent_alerts if a.level == 'info'])
        }
        
        return summary
    
    def export_metrics(self, filepath: str, hours: int = 24):
        """Export metrics to JSON file"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'time_range_hours': hours,
            'system_metrics': [],
            'application_metrics': [],
            'database_metrics': [],
            'alerts': []
        }
        
        # Export system metrics
        for metric in self.metrics_history['system']:
            if metric.timestamp > cutoff_time:
                export_data['system_metrics'].append(asdict(metric))
        
        # Export application metrics
        for metric in self.metrics_history['application']:
            if metric.timestamp > cutoff_time:
                export_data['application_metrics'].append(asdict(metric))
        
        # Export database metrics
        for metric in self.metrics_history['database']:
            if metric.timestamp > cutoff_time:
                export_data['database_metrics'].append(asdict(metric))
        
        # Export alerts
        for alert in self.alerts:
            if alert.timestamp > cutoff_time:
                export_data['alerts'].append(asdict(alert))
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Metrics exported to {filepath}")
    
    def generate_report(self, hours: int = 24) -> str:
        """Generate a human-readable monitoring report"""
        summary = self.get_metrics_summary(hours)
        
        report = f"""
=== MONITORING REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Time Range: Last {hours} hours

SYSTEM METRICS:
"""
        
        if summary['system']:
            report += f"""
  CPU Usage:
    Average: {summary['system']['avg_cpu']:.2f}%
    Maximum: {summary['system']['max_cpu']:.2f}%
  
  Memory Usage:
    Average: {summary['system']['avg_memory']:.2f}%
    Maximum: {summary['system']['max_memory']:.2f}%
  
  Disk Usage:
    Average: {summary['system']['avg_disk']:.2f}%
    Maximum: {summary['system']['max_disk']:.2f}%
"""
        else:
            report += "  No system metrics available\n"
        
        report += f"""
APPLICATION METRICS:
"""
        
        if summary['application']:
            report += f"""
  Requests:
    Total: {summary['application']['total_requests']}
    Errors: {summary['application']['total_errors']}
    Error Rate: {(summary['application']['total_errors'] / max(summary['application']['total_requests'], 1)) * 100:.2f}%
  
  Response Time:
    Average: {summary['application']['avg_response_time']:.2f}ms
    Maximum: {summary['application']['max_response_time']:.2f}ms
  
  Connections:
    Average: {summary['application']['avg_connections']:.2f}
"""
        else:
            report += "  No application metrics available\n"
        
        report += f"""
DATABASE METRICS:
"""
        
        if summary['database']:
            report += f"""
  Connections:
    Average: {summary['database']['avg_connections']:.2f}
    Maximum: {summary['database']['max_connections']}
  
  Queries:
    Total: {summary['database']['total_queries']}
    Slow Queries: {summary['database']['slow_queries']}
"""
        else:
            report += "  No database metrics available\n"
        
        report += f"""
ALERTS:
  Total: {summary['alerts']['total']}
  Critical: {summary['alerts']['critical']}
  Warning: {summary['alerts']['warning']}
  Info: {summary['alerts']['info']}

=== END REPORT ===
"""
        
        return report

def main():
    """Main function for testing the monitoring system"""
    config = {
        'mongodb_uri': 'mongodb://localhost:27017',
        'redis_host': 'localhost',
        'redis_port': 6379
    }
    
    monitor = MonitoringSystem(config)
    
    print("Starting monitoring system...")
    monitor.start_monitoring(interval=10)  # 10 second intervals for testing
    
    try:
        # Run for 2 minutes
        time.sleep(120)
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
    finally:
        monitor.stop_monitoring()
        
        # Generate report
        report = monitor.generate_report(hours=0.1)  # Last 6 minutes
        print(report)
        
        # Export metrics
        monitor.export_metrics('monitoring_export.json', hours=0.1)

if __name__ == "__main__":
    main()