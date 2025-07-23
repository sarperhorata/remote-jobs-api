#!/usr/bin/env python3
"""
Load Testing Framework for Buzz2Remote Backend
Comprehensive load testing with multiple scenarios and reporting
"""

import asyncio
import time
import json
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import aiohttp
import psutil
import matplotlib.pyplot as plt
import numpy as np
from fastapi.testclient import TestClient
from main import app

@dataclass
class LoadTestResult:
    """Load test result data structure"""
    test_name: str
    duration: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    success_rate: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: str

@dataclass
class LoadTestScenario:
    """Load test scenario configuration"""
    name: str
    description: str
    endpoint: str
    method: str = "GET"
    payload: Optional[Dict] = None
    headers: Optional[Dict] = None
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10
    ramp_down_seconds: int = 10

class LoadTestClient:
    """HTTP client for load testing"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None
        self.results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", 
                          payload: Optional[Dict] = None, 
                          headers: Optional[Dict] = None) -> Dict:
        """Make a single HTTP request"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_time = time.time() - start_time
                    return {
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "success": 200 <= response.status_code < 300,
                        "error": None
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=payload, headers=headers) as response:
                    response_time = time.time() - start_time
                    return {
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "success": 200 <= response.status_code < 300,
                        "error": None
                    }
            else:
                raise ValueError(f"Unsupported method: {method}")
                
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }

class LoadTestRunner:
    """Main load test runner"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.results = []
        self.scenarios = []
        
    def add_scenario(self, scenario: LoadTestScenario):
        """Add a test scenario"""
        self.scenarios.append(scenario)
    
    def add_default_scenarios(self):
        """Add default test scenarios"""
        scenarios = [
            LoadTestScenario(
                name="Health Check",
                description="Basic health check endpoint",
                endpoint="/health",
                concurrent_users=50,
                duration_seconds=30
            ),
            LoadTestScenario(
                name="Job Search",
                description="Job search with basic query",
                endpoint="/api/v1/jobs/search?q=python&limit=10",
                concurrent_users=20,
                duration_seconds=60
            ),
            LoadTestScenario(
                name="Job Statistics",
                description="Job statistics endpoint",
                endpoint="/api/v1/jobs/statistics",
                concurrent_users=15,
                duration_seconds=45
            ),
            LoadTestScenario(
                name="Recent Jobs",
                description="Recent jobs endpoint",
                endpoint="/api/v1/jobs/recent",
                concurrent_users=25,
                duration_seconds=50
            ),
            LoadTestScenario(
                name="Complex Search",
                description="Complex job search with filters",
                endpoint="/api/v1/jobs/search?q=python&work_type=remote&job_type=full-time&experience=senior&salary_range=80000-120000&limit=20",
                concurrent_users=10,
                duration_seconds=40
            ),
            LoadTestScenario(
                name="User Registration",
                description="User registration endpoint",
                endpoint="/api/v1/auth/register",
                method="POST",
                payload={
                    "email": "test@example.com",
                    "password": "TestPass123!",
                    "full_name": "Test User"
                },
                concurrent_users=5,
                duration_seconds=30
            )
        ]
        
        for scenario in scenarios:
            self.add_scenario(scenario)
    
    async def run_scenario(self, scenario: LoadTestScenario) -> LoadTestResult:
        """Run a single load test scenario"""
        print(f"🚀 Running scenario: {scenario.name}")
        print(f"   📝 {scenario.description}")
        print(f"   👥 Concurrent users: {scenario.concurrent_users}")
        print(f"   ⏱️  Duration: {scenario.duration_seconds}s")
        
        # Monitor system resources
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        initial_cpu = process.cpu_percent()
        
        # Start load test
        start_time = time.time()
        all_results = []
        
        async with LoadTestClient(self.base_url) as client:
            # Create tasks for concurrent users
            tasks = []
            for user_id in range(scenario.concurrent_users):
                task = self._user_workload(client, scenario, user_id)
                tasks.append(task)
            
            # Run concurrent workload
            user_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect all results
            for result in user_results:
                if isinstance(result, list):
                    all_results.extend(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate final system metrics
        final_memory = process.memory_info().rss
        final_cpu = process.cpu_percent()
        memory_usage = (final_memory - initial_memory) / 1024 / 1024  # MB
        cpu_usage = (initial_cpu + final_cpu) / 2
        
        # Calculate statistics
        response_times = [r["response_time"] for r in all_results]
        successful_requests = len([r for r in all_results if r["success"]])
        failed_requests = len(all_results) - successful_requests
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = np.percentile(response_times, 95)
            p99_response_time = np.percentile(response_times, 99)
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        success_rate = (successful_requests / len(all_results)) * 100 if all_results else 0
        error_rate = 100 - success_rate
        requests_per_second = len(all_results) / duration if duration > 0 else 0
        
        result = LoadTestResult(
            test_name=scenario.name,
            duration=duration,
            total_requests=len(all_results),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            success_rate=success_rate,
            error_rate=error_rate,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            timestamp=datetime.now().isoformat()
        )
        
        # Print results
        print(f"✅ Scenario completed: {scenario.name}")
        print(f"   📊 Total requests: {result.total_requests}")
        print(f"   ✅ Success rate: {result.success_rate:.1f}%")
        print(f"   ⏱️  Avg response time: {result.avg_response_time:.3f}s")
        print(f"   🚀 Requests/second: {result.requests_per_second:.1f}")
        print(f"   💾 Memory usage: {result.memory_usage_mb:.1f}MB")
        print(f"   🔥 CPU usage: {result.cpu_usage_percent:.1f}%")
        
        return result
    
    async def _user_workload(self, client: LoadTestClient, scenario: LoadTestScenario, user_id: int) -> List[Dict]:
        """Individual user workload"""
        results = []
        start_time = time.time()
        end_time = start_time + scenario.duration_seconds
        
        # Ramp up period
        ramp_up_end = start_time + scenario.ramp_up_seconds
        ramp_down_start = end_time - scenario.ramp_down_seconds
        
        while time.time() < end_time:
            current_time = time.time()
            
            # Calculate request rate based on ramp up/down
            if current_time < ramp_up_end:
                # Ramp up: increase requests gradually
                progress = (current_time - start_time) / scenario.ramp_up_seconds
                requests_per_second = 1 + (4 * progress)  # 1 to 5 requests per second
            elif current_time > ramp_down_start:
                # Ramp down: decrease requests gradually
                progress = (end_time - current_time) / scenario.ramp_down_seconds
                requests_per_second = 1 + (4 * progress)  # 5 to 1 requests per second
            else:
                # Steady state: maximum requests
                requests_per_second = 5
            
            # Make requests
            delay = 1.0 / requests_per_second
            result = await client.make_request(
                scenario.endpoint,
                scenario.method,
                scenario.payload,
                scenario.headers
            )
            results.append(result)
            
            # Wait before next request
            await asyncio.sleep(delay)
        
        return results
    
    async def run_all_scenarios(self) -> List[LoadTestResult]:
        """Run all configured scenarios"""
        print("🚀 Starting load test suite...")
        print(f"📊 Total scenarios: {len(self.scenarios)}")
        
        results = []
        
        for i, scenario in enumerate(self.scenarios, 1):
            print(f"\n{'='*60}")
            print(f"Scenario {i}/{len(self.scenarios)}: {scenario.name}")
            print(f"{'='*60}")
            
            try:
                result = await self.run_scenario(scenario)
                results.append(result)
                
                # Brief pause between scenarios
                if i < len(self.scenarios):
                    print("⏸️  Pausing between scenarios...")
                    await asyncio.sleep(5)
                    
            except Exception as e:
                print(f"❌ Error running scenario {scenario.name}: {e}")
                continue
        
        self.results = results
        return results
    
    def generate_report(self, output_dir: str = "load_test_reports") -> str:
        """Generate comprehensive load test report"""
        if not self.results:
            print("⚠️  No results to report")
            return ""
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_path / f"load_test_report_{timestamp}.json"
        
        # Prepare report data
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_duration": sum(r.duration for r in self.results),
            "total_scenarios": len(self.results),
            "scenarios": [asdict(result) for result in self.results],
            "summary": self._generate_summary()
        }
        
        # Save JSON report
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Generate HTML report
        html_report = self._generate_html_report(report_data)
        html_file = output_path / f"load_test_report_{timestamp}.html"
        with open(html_file, 'w') as f:
            f.write(html_report)
        
        # Generate charts
        self._generate_charts(output_path, timestamp)
        
        print(f"📄 Load test report generated:")
        print(f"   📊 JSON: {report_file}")
        print(f"   🌐 HTML: {html_file}")
        print(f"   📈 Charts: {output_path}")
        
        return str(report_file)
    
    def _generate_summary(self) -> Dict:
        """Generate test summary"""
        if not self.results:
            return {}
        
        total_requests = sum(r.total_requests for r in self.results)
        total_successful = sum(r.successful_requests for r in self.results)
        total_failed = sum(r.failed_requests for r in self.results)
        
        avg_response_times = [r.avg_response_time for r in self.results]
        success_rates = [r.success_rate for r in self.results]
        requests_per_second = [r.requests_per_second for r in self.results]
        
        return {
            "total_requests": total_requests,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "overall_success_rate": (total_successful / total_requests * 100) if total_requests > 0 else 0,
            "avg_response_time": statistics.mean(avg_response_times) if avg_response_times else 0,
            "max_response_time": max(avg_response_times) if avg_response_times else 0,
            "min_response_time": min(avg_response_times) if avg_response_times else 0,
            "avg_success_rate": statistics.mean(success_rates) if success_rates else 0,
            "avg_requests_per_second": statistics.mean(requests_per_second) if requests_per_second else 0,
            "total_duration": sum(r.duration for r in self.results)
        }
    
    def _generate_html_report(self, report_data: Dict) -> str:
        """Generate HTML report"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Load Test Report - Buzz2Remote Backend</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .scenario { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .metric { display: inline-block; margin: 5px 10px; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Load Test Report</h1>
        <p><strong>Project:</strong> Buzz2Remote Backend</p>
        <p><strong>Timestamp:</strong> {timestamp}</p>
        <p><strong>Total Scenarios:</strong> {total_scenarios}</p>
        <p><strong>Total Duration:</strong> {total_duration:.1f} seconds</p>
    </div>
    
    <div class="summary">
        <h2>📊 Test Summary</h2>
        <div class="metric"><strong>Total Requests:</strong> {total_requests}</div>
        <div class="metric"><strong>Success Rate:</strong> <span class="success">{success_rate:.1f}%</span></div>
        <div class="metric"><strong>Avg Response Time:</strong> {avg_response_time:.3f}s</div>
        <div class="metric"><strong>Requests/Second:</strong> {requests_per_second:.1f}</div>
    </div>
    
    <h2>📋 Scenario Results</h2>
    {scenarios_html}
</body>
</html>
        """
        
        summary = report_data["summary"]
        scenarios_html = ""
        
        for scenario in report_data["scenarios"]:
            success_class = "success" if scenario["success_rate"] >= 95 else "warning" if scenario["success_rate"] >= 80 else "error"
            
            scenarios_html += f"""
            <div class="scenario">
                <h3>{scenario['test_name']}</h3>
                <div class="metric"><strong>Duration:</strong> {scenario['duration']:.1f}s</div>
                <div class="metric"><strong>Total Requests:</strong> {scenario['total_requests']}</div>
                <div class="metric"><strong>Success Rate:</strong> <span class="{success_class}">{scenario['success_rate']:.1f}%</span></div>
                <div class="metric"><strong>Avg Response Time:</strong> {scenario['avg_response_time']:.3f}s</div>
                <div class="metric"><strong>Requests/Second:</strong> {scenario['requests_per_second']:.1f}</div>
                <div class="metric"><strong>Memory Usage:</strong> {scenario['memory_usage_mb']:.1f}MB</div>
                <div class="metric"><strong>CPU Usage:</strong> {scenario['cpu_usage_percent']:.1f}%</div>
            </div>
            """
        
        return html_template.format(
            timestamp=report_data["timestamp"],
            total_scenarios=report_data["total_scenarios"],
            total_duration=summary.get("total_duration", 0),
            total_requests=summary.get("total_requests", 0),
            success_rate=summary.get("overall_success_rate", 0),
            avg_response_time=summary.get("avg_response_time", 0),
            requests_per_second=summary.get("avg_requests_per_second", 0),
            scenarios_html=scenarios_html
        )
    
    def _generate_charts(self, output_path: Path, timestamp: str):
        """Generate performance charts"""
        try:
            # Response time chart
            plt.figure(figsize=(12, 8))
            
            scenarios = [r.test_name for r in self.results]
            avg_times = [r.avg_response_time for r in self.results]
            p95_times = [r.p95_response_time for r in self.results]
            p99_times = [r.p99_response_time for r in self.results]
            
            x = range(len(scenarios))
            width = 0.25
            
            plt.bar([i - width for i in x], avg_times, width, label='Average', color='blue', alpha=0.7)
            plt.bar(x, p95_times, width, label='95th Percentile', color='orange', alpha=0.7)
            plt.bar([i + width for i in x], p99_times, width, label='99th Percentile', color='red', alpha=0.7)
            
            plt.xlabel('Scenarios')
            plt.ylabel('Response Time (seconds)')
            plt.title('Response Time by Scenario')
            plt.xticks(x, scenarios, rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            
            chart_file = output_path / f"response_times_{timestamp}.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Success rate chart
            plt.figure(figsize=(10, 6))
            
            success_rates = [r.success_rate for r in self.results]
            colors = ['green' if rate >= 95 else 'orange' if rate >= 80 else 'red' for rate in success_rates]
            
            plt.bar(scenarios, success_rates, color=colors, alpha=0.7)
            plt.axhline(y=95, color='green', linestyle='--', label='95% Target')
            plt.axhline(y=80, color='orange', linestyle='--', label='80% Warning')
            
            plt.xlabel('Scenarios')
            plt.ylabel('Success Rate (%)')
            plt.title('Success Rate by Scenario')
            plt.xticks(rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            
            success_chart_file = output_path / f"success_rates_{timestamp}.png"
            plt.savefig(success_chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📈 Charts generated: {chart_file}, {success_chart_file}")
            
        except ImportError:
            print("⚠️  matplotlib not available, skipping charts")
        except Exception as e:
            print(f"⚠️  Error generating charts: {e}")

def main():
    """Main entry point for load testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load Testing Framework")
    parser.add_argument("--url", default="http://localhost:8001", help="Base URL for testing")
    parser.add_argument("--scenarios", default="default", help="Scenarios to run (default, custom)")
    parser.add_argument("--output", default="load_test_reports", help="Output directory for reports")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    
    args = parser.parse_args()
    
    async def run_load_tests():
        runner = LoadTestRunner(args.url)
        
        if args.scenarios == "default":
            runner.add_default_scenarios()
        else:
            # Add custom scenarios here
            pass
        
        # Run all scenarios
        results = await runner.run_all_scenarios()
        
        # Generate report
        report_file = runner.generate_report(args.output)
        
        print(f"\n🎉 Load testing completed!")
        print(f"📄 Report saved to: {report_file}")
        
        return results
    
    asyncio.run(run_load_tests())

if __name__ == "__main__":
    main()