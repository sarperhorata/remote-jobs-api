#!/usr/bin/env python3
"""
Comprehensive Test Dashboard System for Backend
Provides real-time monitoring, test execution status, and interactive reporting
"""

import asyncio
import base64
import hashlib
import hmac
import io
import json
import logging
import queue
import sqlite3
import threading
import time
import urllib.parse
import webbrowser
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

import jwt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardStatus(Enum):
    """Dashboard status enumeration"""

    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class DashboardMetric:
    """Dashboard metric definition"""

    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str
    trend: str = "stable"  # increasing, decreasing, stable


@dataclass
class TestExecutionStatus:
    """Test execution status definition"""

    test_id: str
    suite_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    progress: float = 0.0
    current_step: str = ""
    logs: List[str] = None


@dataclass
class DashboardAlert:
    """Dashboard alert definition"""

    id: str
    level: str  # info, warning, error, critical
    title: str
    message: str
    timestamp: datetime
    category: str
    acknowledged: bool = False
    action_required: bool = False


class DashboardDatabase:
    """Dashboard database manager"""

    def __init__(self, db_path: str = "dashboard.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize dashboard database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                category TEXT NOT NULL,
                trend TEXT DEFAULT 'stable'
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT NOT NULL,
                suite_id TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                duration REAL,
                progress REAL DEFAULT 0.0,
                current_step TEXT,
                logs TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                level TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                category TEXT NOT NULL,
                acknowledged BOOLEAN DEFAULT FALSE,
                action_required BOOLEAN DEFAULT FALSE
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dashboard_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_metrics_category ON metrics(category)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_test_executions_test_id ON test_executions(test_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_test_executions_suite_id ON test_executions(suite_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_level ON alerts(level)")

        conn.commit()
        conn.close()
        logger.info("Dashboard database initialized")

    def save_metric(self, metric: DashboardMetric):
        """Save metric to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO metrics (name, value, unit, timestamp, category, trend)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                metric.name,
                metric.value,
                metric.unit,
                metric.timestamp,
                metric.category,
                metric.trend,
            ),
        )

        conn.commit()
        conn.close()

    def get_metrics(
        self, category: Optional[str] = None, hours: int = 24
    ) -> List[DashboardMetric]:
        """Get metrics from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = datetime.now() - timedelta(hours=hours)

        if category:
            cursor.execute(
                """
                SELECT name, value, unit, timestamp, category, trend
                FROM metrics
                WHERE category = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """,
                (category, cutoff_time),
            )
        else:
            cursor.execute(
                """
                SELECT name, value, unit, timestamp, category, trend
                FROM metrics
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            """,
                (cutoff_time,),
            )

        metrics = []
        for row in cursor.fetchall():
            metrics.append(
                DashboardMetric(
                    name=row[0],
                    value=row[1],
                    unit=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    category=row[4],
                    trend=row[5],
                )
            )

        conn.close()
        return metrics

    def save_test_execution(self, execution: TestExecutionStatus):
        """Save test execution to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        logs_json = json.dumps(execution.logs) if execution.logs else None

        cursor.execute(
            """
            INSERT INTO test_executions 
            (test_id, suite_id, status, start_time, end_time, duration, progress, current_step, logs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                execution.test_id,
                execution.suite_id,
                execution.status,
                execution.start_time,
                execution.end_time,
                execution.duration,
                execution.progress,
                execution.current_step,
                logs_json,
            ),
        )

        conn.commit()
        conn.close()

    def get_test_executions(
        self, suite_id: Optional[str] = None, hours: int = 24
    ) -> List[TestExecutionStatus]:
        """Get test executions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = datetime.now() - timedelta(hours=hours)

        if suite_id:
            cursor.execute(
                """
                SELECT test_id, suite_id, status, start_time, end_time, duration, progress, current_step, logs
                FROM test_executions
                WHERE suite_id = ? AND start_time > ?
                ORDER BY start_time DESC
            """,
                (suite_id, cutoff_time),
            )
        else:
            cursor.execute(
                """
                SELECT test_id, suite_id, status, start_time, end_time, duration, progress, current_step, logs
                FROM test_executions
                WHERE start_time > ?
                ORDER BY start_time DESC
            """,
                (cutoff_time,),
            )

        executions = []
        for row in cursor.fetchall():
            logs = json.loads(row[8]) if row[8] else []
            executions.append(
                TestExecutionStatus(
                    test_id=row[0],
                    suite_id=row[1],
                    status=row[2],
                    start_time=datetime.fromisoformat(row[3]),
                    end_time=datetime.fromisoformat(row[4]) if row[4] else None,
                    duration=row[5],
                    progress=row[6],
                    current_step=row[7],
                    logs=logs,
                )
            )

        conn.close()
        return executions

    def save_alert(self, alert: DashboardAlert):
        """Save alert to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO alerts 
            (alert_id, level, title, message, timestamp, category, acknowledged, action_required)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                alert.id,
                alert.level,
                alert.title,
                alert.message,
                alert.timestamp,
                alert.category,
                alert.acknowledged,
                alert.action_required,
            ),
        )

        conn.commit()
        conn.close()

    def get_alerts(
        self, level: Optional[str] = None, acknowledged: Optional[bool] = None
    ) -> List[DashboardAlert]:
        """Get alerts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT alert_id, level, title, message, timestamp, category, acknowledged, action_required FROM alerts"
        params = []

        conditions = []
        if level:
            conditions.append("level = ?")
            params.append(level)
        if acknowledged is not None:
            conditions.append("acknowledged = ?")
            params.append(acknowledged)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)

        alerts = []
        for row in cursor.fetchall():
            alerts.append(
                DashboardAlert(
                    id=row[0],
                    level=row[1],
                    title=row[2],
                    message=row[3],
                    timestamp=datetime.fromisoformat(row[4]),
                    category=row[5],
                    acknowledged=bool(row[6]),
                    action_required=bool(row[7]),
                )
            )

        conn.close()
        return alerts

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE alerts SET acknowledged = TRUE WHERE alert_id = ?", (alert_id,)
        )

        conn.commit()
        conn.close()


class DashboardChartGenerator:
    """Chart generator for dashboard"""

    def __init__(self):
        plt.style.use("seaborn-v0_8")

    def generate_metric_chart(self, metrics: List[DashboardMetric], title: str) -> str:
        """Generate chart for metrics and return as base64 encoded image"""
        if not metrics:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        # Group metrics by name
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.name].append(metric)

        # Plot each metric
        for metric_name, metric_list in metric_groups.items():
            timestamps = [m.timestamp for m in metric_list]
            values = [m.value for m in metric_list]

            ax.plot(timestamps, values, label=metric_name, marker="o", markersize=4)

        ax.set_title(title)
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        # Save to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return image_base64

    def generate_test_status_chart(self, executions: List[TestExecutionStatus]) -> str:
        """Generate chart for test execution status"""
        if not executions:
            return ""

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Status distribution pie chart
        status_counts = defaultdict(int)
        for execution in executions:
            status_counts[execution.status] += 1

        if status_counts:
            labels = list(status_counts.keys())
            sizes = list(status_counts.values())
            colors = ["#28a745", "#dc3545", "#ffc107", "#17a2b8", "#6c757d"]

            ax1.pie(
                sizes,
                labels=labels,
                colors=colors[: len(labels)],
                autopct="%1.1f%%",
                startangle=90,
            )
            ax1.set_title("Test Execution Status Distribution")

        # Duration histogram
        durations = [e.duration for e in executions if e.duration is not None]
        if durations:
            ax2.hist(durations, bins=20, alpha=0.7, color="skyblue", edgecolor="black")
            ax2.set_title("Test Execution Duration Distribution")
            ax2.set_xlabel("Duration (seconds)")
            ax2.set_ylabel("Frequency")

        plt.tight_layout()

        # Save to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)

        return image_base64


class DashboardHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboard"""

    def __init__(self, *args, dashboard=None, **kwargs):
        self.dashboard = dashboard
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            if path == "/":
                self.send_dashboard_page()
            elif path == "/api/metrics":
                self.send_metrics_api()
            elif path == "/api/test-executions":
                self.send_test_executions_api()
            elif path == "/api/alerts":
                self.send_alerts_api()
            elif path == "/api/charts/metrics":
                self.send_metrics_chart()
            elif path == "/api/charts/test-status":
                self.send_test_status_chart()
            elif path == "/api/status":
                self.send_status_api()
            else:
                self.send_error(404, "Not Found")

        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, "Internal Server Error")

    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            if path == "/api/alerts/acknowledge":
                self.handle_alert_acknowledge()
            else:
                self.send_error(404, "Not Found")

        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error(500, "Internal Server Error")

    def send_dashboard_page(self):
        """Send main dashboard HTML page"""
        html_content = self.generate_dashboard_html()

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(html_content)))
        self.end_headers()
        self.wfile.write(html_content.encode())

    def generate_dashboard_html(self) -> str:
        """Generate dashboard HTML content"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backend Test Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-running {{ background-color: #28a745; }}
        .status-idle {{ background-color: #6c757d; }}
        .status-error {{ background-color: #dc3545; }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }}
        
        .card h3 {{
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .metric-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .metric-item:last-child {{
            border-bottom: none;
        }}
        
        .metric-name {{
            font-weight: 500;
            color: #555;
        }}
        
        .metric-value {{
            font-weight: bold;
            color: #333;
        }}
        
        .alert-item {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        
        .alert-info {{
            background-color: #d1ecf1;
            border-left-color: #17a2b8;
        }}
        
        .alert-warning {{
            background-color: #fff3cd;
            border-left-color: #ffc107;
        }}
        
        .alert-error {{
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }}
        
        .alert-critical {{
            background-color: #f5c6cb;
            border-left-color: #721c24;
        }}
        
        .chart-container {{
            text-align: center;
            margin: 20px 0;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }}
        
        .refresh-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: transform 0.2s;
        }}
        
        .refresh-btn:hover {{
            transform: translateY(-2px);
        }}
        
        .test-execution {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .test-status {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .status-passed {{ background-color: #d4edda; color: #155724; }}
        .status-failed {{ background-color: #f8d7da; color: #721c24; }}
        .status-running {{ background-color: #d1ecf1; color: #0c5460; }}
        .status-error {{ background-color: #f5c6cb; color: #721c24; }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background-color: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <span class="status-indicator status-{self.dashboard.status.value}"></span>
                Backend Test Dashboard
            </h1>
            <p>Real-time monitoring and test execution status</p>
            <button class="refresh-btn" onclick="refreshDashboard()">Refresh Dashboard</button>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>System Metrics</h3>
                <div id="system-metrics">
                    <div class="metric-item">
                        <span class="metric-name">Loading...</span>
                        <span class="metric-value">-</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Test Execution Status</h3>
                <div id="test-executions">
                    <div class="metric-item">
                        <span class="metric-name">Loading...</span>
                        <span class="metric-value">-</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Active Alerts</h3>
                <div id="alerts">
                    <div class="metric-item">
                        <span class="metric-name">Loading...</span>
                        <span class="metric-value">-</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Performance Charts</h3>
                <div class="chart-container">
                    <img id="metrics-chart" src="/api/charts/metrics" alt="Metrics Chart" />
                </div>
            </div>
            
            <div class="card">
                <h3>Test Status Distribution</h3>
                <div class="chart-container">
                    <img id="test-status-chart" src="/api/charts/test-status" alt="Test Status Chart" />
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function refreshDashboard() {{
            location.reload();
        }}
        
        // Auto-refresh every 30 seconds
        setInterval(refreshDashboard, 30000);
        
        // Load data on page load
        document.addEventListener('DOMContentLoaded', function() {{
            loadMetrics();
            loadTestExecutions();
            loadAlerts();
        }});
        
        function loadMetrics() {{
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {{
                    const container = document.getElementById('system-metrics');
                    container.innerHTML = '';
                    
                    data.forEach(metric => {{
                        const item = document.createElement('div');
                        item.className = 'metric-item';
                        item.innerHTML = `
                            <span class="metric-name">${{metric.name}}</span>
                            <span class="metric-value">${{metric.value}} ${{metric.unit}}</span>
                        `;
                        container.appendChild(item);
                    }});
                }})
                .catch(error => console.error('Error loading metrics:', error));
        }}
        
        function loadTestExecutions() {{
            fetch('/api/test-executions')
                .then(response => response.json())
                .then(data => {{
                    const container = document.getElementById('test-executions');
                    container.innerHTML = '';
                    
                    data.forEach(execution => {{
                        const item = document.createElement('div');
                        item.className = 'test-execution';
                        item.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong>${{execution.test_id}}</strong>
                                <span class="test-status status-${{execution.status}}">${{execution.status}}</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${{execution.progress}}%"></div>
                            </div>
                            <small>${{execution.current_step}}</small>
                        `;
                        container.appendChild(item);
                    }});
                }})
                .catch(error => console.error('Error loading test executions:', error));
        }}
        
        function loadAlerts() {{
            fetch('/api/alerts')
                .then(response => response.json())
                .then(data => {{
                    const container = document.getElementById('alerts');
                    container.innerHTML = '';
                    
                    data.forEach(alert => {{
                        const item = document.createElement('div');
                        item.className = `alert-item alert-${{alert.level}}`;
                        item.innerHTML = `
                            <strong>${{alert.title}}</strong><br>
                            <small>${{alert.message}}</small>
                        `;
                        container.appendChild(item);
                    }});
                }})
                .catch(error => console.error('Error loading alerts:', error));
        }}
    </script>
</body>
</html>
        """

    def send_metrics_api(self):
        """Send metrics API response"""
        metrics = self.dashboard.get_current_metrics()

        self.send_json_response(metrics)

    def send_test_executions_api(self):
        """Send test executions API response"""
        executions = self.dashboard.get_current_test_executions()

        self.send_json_response(executions)

    def send_alerts_api(self):
        """Send alerts API response"""
        alerts = self.dashboard.get_current_alerts()

        self.send_json_response(alerts)

    def send_metrics_chart(self):
        """Send metrics chart"""
        chart_data = self.dashboard.generate_metrics_chart()

        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.end_headers()

        if chart_data:
            self.wfile.write(base64.b64decode(chart_data))

    def send_test_status_chart(self):
        """Send test status chart"""
        chart_data = self.dashboard.generate_test_status_chart()

        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.end_headers()

        if chart_data:
            self.wfile.write(base64.b64decode(chart_data))

    def send_status_api(self):
        """Send dashboard status API response"""
        status = {
            "status": self.dashboard.status.value,
            "uptime": self.dashboard.get_uptime(),
            "total_metrics": len(self.dashboard.get_current_metrics()),
            "total_executions": len(self.dashboard.get_current_test_executions()),
            "total_alerts": len(self.dashboard.get_current_alerts()),
        }

        self.send_json_response(status)

    def handle_alert_acknowledge(self):
        """Handle alert acknowledgment"""
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode("utf-8"))

        alert_id = data.get("alert_id")
        if alert_id:
            self.dashboard.acknowledge_alert(alert_id)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode())

    def send_json_response(self, data):
        """Send JSON response"""
        json_data = json.dumps(data, default=str)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(json_data)))
        self.end_headers()
        self.wfile.write(json_data.encode())

    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        pass


class TestDashboard:
    """Main dashboard class"""

    def __init__(self, port: int = 8080):
        self.port = port
        self.status = DashboardStatus.IDLE
        self.start_time = datetime.now()
        self.db = DashboardDatabase()
        self.chart_generator = DashboardChartGenerator()
        self.server = None
        self.server_thread = None
        self.running = False

        # Data caches
        self.metrics_cache = deque(maxlen=1000)
        self.executions_cache = deque(maxlen=1000)
        self.alerts_cache = deque(maxlen=100)

        # Initialize with sample data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize dashboard with sample data"""
        # Add sample metrics
        sample_metrics = [
            DashboardMetric("CPU Usage", 45.2, "%", datetime.now(), "system", "stable"),
            DashboardMetric(
                "Memory Usage", 67.8, "%", datetime.now(), "system", "increasing"
            ),
            DashboardMetric(
                "Disk Usage", 23.4, "%", datetime.now(), "system", "stable"
            ),
            DashboardMetric(
                "Active Connections",
                12,
                "connections",
                datetime.now(),
                "application",
                "stable",
            ),
            DashboardMetric(
                "Response Time", 245, "ms", datetime.now(), "application", "decreasing"
            ),
            DashboardMetric(
                "Error Rate", 0.5, "%", datetime.now(), "application", "stable"
            ),
        ]

        for metric in sample_metrics:
            self.add_metric(metric)

        # Add sample test executions
        sample_executions = [
            TestExecutionStatus(
                test_id="test_user_auth",
                suite_id="integration",
                status="running",
                start_time=datetime.now() - timedelta(minutes=5),
                end_time=None,
                duration=None,
                progress=65.0,
                current_step="Validating user credentials",
                logs=[
                    "Test started",
                    "Database connection established",
                    "User lookup completed",
                ],
            ),
            TestExecutionStatus(
                test_id="test_api_performance",
                suite_id="performance",
                status="passed",
                start_time=datetime.now() - timedelta(minutes=15),
                end_time=datetime.now() - timedelta(minutes=10),
                duration=300.0,
                progress=100.0,
                current_step="Completed",
                logs=["Performance test completed successfully"],
            ),
        ]

        for execution in sample_executions:
            self.add_test_execution(execution)

        # Add sample alerts
        sample_alerts = [
            DashboardAlert(
                id="alert_001",
                level="warning",
                title="High Memory Usage",
                message="Memory usage is above 80% threshold",
                timestamp=datetime.now() - timedelta(minutes=30),
                category="system",
                action_required=True,
            ),
            DashboardAlert(
                id="alert_002",
                level="info",
                title="Test Suite Completed",
                message="Integration test suite completed successfully",
                timestamp=datetime.now() - timedelta(minutes=5),
                category="testing",
                action_required=False,
            ),
        ]

        for alert in sample_alerts:
            self.add_alert(alert)

    def add_metric(self, metric: DashboardMetric):
        """Add metric to dashboard"""
        self.metrics_cache.append(metric)
        self.db.save_metric(metric)
        logger.info(f"Added metric: {metric.name} = {metric.value} {metric.unit}")

    def add_test_execution(self, execution: TestExecutionStatus):
        """Add test execution to dashboard"""
        self.executions_cache.append(execution)
        self.db.save_test_execution(execution)
        logger.info(f"Added test execution: {execution.test_id} - {execution.status}")

    def add_alert(self, alert: DashboardAlert):
        """Add alert to dashboard"""
        self.alerts_cache.append(alert)
        self.db.save_alert(alert)
        logger.info(f"Added alert: {alert.title} ({alert.level})")

    def get_current_metrics(self) -> List[Dict[str, Any]]:
        """Get current metrics for API"""
        return [asdict(metric) for metric in list(self.metrics_cache)[-10:]]

    def get_current_test_executions(self) -> List[Dict[str, Any]]:
        """Get current test executions for API"""
        return [asdict(execution) for execution in list(self.executions_cache)[-10:]]

    def get_current_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts for API"""
        return [asdict(alert) for alert in list(self.alerts_cache)[-10:]]

    def generate_metrics_chart(self) -> str:
        """Generate metrics chart"""
        metrics = self.db.get_metrics(hours=6)
        return self.chart_generator.generate_metric_chart(
            metrics, "System Metrics (Last 6 Hours)"
        )

    def generate_test_status_chart(self) -> str:
        """Generate test status chart"""
        executions = self.db.get_test_executions(hours=24)
        return self.chart_generator.generate_test_status_chart(executions)

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        self.db.acknowledge_alert(alert_id)
        logger.info(f"Acknowledged alert: {alert_id}")

    def get_uptime(self) -> str:
        """Get dashboard uptime"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"

    def start(self):
        """Start dashboard server"""
        if self.running:
            logger.warning("Dashboard is already running")
            return

        self.running = True
        self.status = DashboardStatus.RUNNING

        # Create custom handler class with dashboard reference
        class DashboardHandler(DashboardHTTPHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, dashboard=self, **kwargs)

        # Start server in separate thread
        def run_server():
            try:
                self.server = HTTPServer(("localhost", self.port), DashboardHandler)
                logger.info(f"Dashboard server started on http://localhost:{self.port}")
                self.server.serve_forever()
            except Exception as e:
                logger.error(f"Dashboard server error: {e}")
                self.status = DashboardStatus.ERROR

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        # Open browser
        try:
            webbrowser.open(f"http://localhost:{self.port}")
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")

    def stop(self):
        """Stop dashboard server"""
        if not self.running:
            return

        self.running = False
        self.status = DashboardStatus.IDLE

        if self.server:
            self.server.shutdown()
            self.server.server_close()

        logger.info("Dashboard server stopped")

    def update_metric(self, name: str, value: float, unit: str, category: str):
        """Update metric value"""
        # Determine trend based on previous value
        trend = "stable"
        if self.metrics_cache:
            last_metric = self.metrics_cache[-1]
            if last_metric.name == name:
                if value > last_metric.value:
                    trend = "increasing"
                elif value < last_metric.value:
                    trend = "decreasing"

        metric = DashboardMetric(name, value, unit, datetime.now(), category, trend)
        self.add_metric(metric)

    def update_test_execution(
        self,
        test_id: str,
        suite_id: str,
        status: str,
        progress: float = 0.0,
        current_step: str = "",
    ):
        """Update test execution status"""
        # Find existing execution or create new one
        execution = None
        for exec_item in self.executions_cache:
            if exec_item.test_id == test_id and exec_item.suite_id == suite_id:
                execution = exec_item
                break

        if execution is None:
            execution = TestExecutionStatus(
                test_id=test_id,
                suite_id=suite_id,
                status=status,
                start_time=datetime.now(),
                end_time=None,
                duration=None,
                progress=progress,
                current_step=current_step,
                logs=[],
            )
        else:
            execution.status = status
            execution.progress = progress
            execution.current_step = current_step

            if status in ["passed", "failed", "error"]:
                execution.end_time = datetime.now()
                if execution.start_time:
                    execution.duration = (
                        execution.end_time - execution.start_time
                    ).total_seconds()

        self.add_test_execution(execution)


def main():
    """Main function for testing the dashboard"""
    dashboard = TestDashboard(port=8080)

    print("Starting Test Dashboard...")
    dashboard.start()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)

            # Simulate metric updates
            import random

            dashboard.update_metric("CPU Usage", random.uniform(30, 80), "%", "system")
            dashboard.update_metric(
                "Memory Usage", random.uniform(50, 90), "%", "system"
            )
            dashboard.update_metric(
                "Response Time", random.uniform(100, 500), "ms", "application"
            )

    except KeyboardInterrupt:
        print("\nStopping Dashboard...")
        dashboard.stop()
        print("Dashboard stopped")


if __name__ == "__main__":
    main()
