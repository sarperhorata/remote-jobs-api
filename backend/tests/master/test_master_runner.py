#!/usr/bin/env python3
"""
Master Test Runner for Backend
Orchestrates all testing components including monitoring, security audit, automation framework, and dashboard
"""

import argparse
import asyncio
import json
import logging
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil
import requests
import yaml

# Import our testing components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from automation.test_automation_framework import (TestAutomationFramework,
                                                      TestCase, TestPriority)
    from coverage.test_coverage_analysis import CoverageAnalyzer
    from dashboard.test_dashboard import TestDashboard
    from data.test_data_manager import TestDataManager
    from e2e.test_complete_user_journey import E2ETestRunner
    from load.load_testing_framework import LoadTestFramework
    from monitoring.test_monitoring_system import MonitoringSystem
    from performance.test_load_performance import LoadTestingFramework
    from security.test_security_audit import SecurityAuditor

    from database.test_migrations import DatabaseMigrationTester
except ImportError as e:
    print(f"Warning: Could not import some testing components: {e}")
    print("Some features may not be available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("master_runner.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class TestPhase(Enum):
    """Test phase enumeration"""

    SETUP = "setup"
    UNIT_TESTS = "unit_tests"
    INTEGRATION_TESTS = "integration_tests"
    PERFORMANCE_TESTS = "performance_tests"
    SECURITY_TESTS = "security_tests"
    E2E_TESTS = "e2e_tests"
    COVERAGE_ANALYSIS = "coverage_analysis"
    LOAD_TESTS = "load_tests"
    CLEANUP = "cleanup"


class RunnerStatus(Enum):
    """Runner status enumeration"""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TestResult:
    """Test result definition"""

    phase: TestPhase
    status: str  # passed, failed, skipped, error
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    details: Dict[str, Any]
    error_message: Optional[str]
    logs: List[str]


@dataclass
class MasterTestConfig:
    """Master test configuration"""

    # General settings
    parallel_execution: bool = True
    max_workers: int = 4
    timeout_per_phase: int = 1800  # 30 minutes
    continue_on_failure: bool = False

    # Component settings
    enable_monitoring: bool = True
    enable_security_audit: bool = True
    enable_automation: bool = True
    enable_dashboard: bool = True
    enable_performance_tests: bool = True
    enable_load_tests: bool = True
    enable_e2e_tests: bool = True
    enable_coverage_analysis: bool = True

    # Dashboard settings
    dashboard_port: int = 8080
    dashboard_auto_open: bool = True

    # Reporting settings
    generate_reports: bool = True
    report_format: str = "json"  # json, html, xml
    save_logs: bool = True

    # Notification settings
    send_notifications: bool = False
    notification_email: Optional[str] = None
    notification_webhook: Optional[str] = None


class MasterTestRunner:
    """Master test runner that orchestrates all testing components"""

    def __init__(self, config: MasterTestConfig):
        self.config = config
        self.status = RunnerStatus.IDLE
        self.start_time = None
        self.end_time = None
        self.results = {}
        self.current_phase = None
        self.cancelled = False

        # Initialize components
        self.monitoring_system = None
        self.security_auditor = None
        self.automation_framework = None
        self.dashboard = None
        self.load_testing = None
        self.e2e_runner = None
        self.coverage_analyzer = None
        self.data_manager = None

        # Initialize components based on config
        self._initialize_components()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        logger.info(f"Received signal {signum}, cancelling test run...")
        self.cancel()

    def _initialize_components(self):
        """Initialize testing components based on configuration"""
        try:
            if self.config.enable_monitoring:
                monitoring_config = {
                    "mongodb_uri": "mongodb://localhost:27017",
                    "redis_host": "localhost",
                    "redis_port": 6379,
                }
                self.monitoring_system = MonitoringSystem(monitoring_config)
                logger.info("Monitoring system initialized")
        except Exception as e:
            logger.warning(f"Could not initialize monitoring system: {e}")

        try:
            if self.config.enable_security_audit:
                security_config = {
                    "test_credentials": {
                        "admin": {"email": "admin@example.com", "password": "admin123"},
                        "user": {"email": "user@example.com", "password": "user123"},
                    }
                }
                self.security_auditor = SecurityAuditor(
                    "http://localhost:8000", security_config
                )
                logger.info("Security auditor initialized")
        except Exception as e:
            logger.warning(f"Could not initialize security auditor: {e}")

        try:
            if self.config.enable_automation:
                self.automation_framework = TestAutomationFramework("test_config.yaml")
                logger.info("Automation framework initialized")
        except Exception as e:
            logger.warning(f"Could not initialize automation framework: {e}")

        try:
            if self.config.enable_dashboard:
                self.dashboard = TestDashboard(port=self.config.dashboard_port)
                logger.info("Dashboard initialized")
        except Exception as e:
            logger.warning(f"Could not initialize dashboard: {e}")

        try:
            if self.config.enable_performance_tests:
                self.load_testing = LoadTestingFramework()
                logger.info("Load testing framework initialized")
        except Exception as e:
            logger.warning(f"Could not initialize load testing: {e}")

        try:
            if self.config.enable_e2e_tests:
                self.e2e_runner = E2ETestRunner()
                logger.info("E2E test runner initialized")
        except Exception as e:
            logger.warning(f"Could not initialize E2E runner: {e}")

        try:
            if self.config.enable_coverage_analysis:
                self.coverage_analyzer = CoverageAnalyzer()
                logger.info("Coverage analyzer initialized")
        except Exception as e:
            logger.warning(f"Could not initialize coverage analyzer: {e}")

        try:
            self.data_manager = TestDataManager()
            logger.info("Test data manager initialized")
        except Exception as e:
            logger.warning(f"Could not initialize data manager: {e}")

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        if self.status == RunnerStatus.RUNNING:
            logger.warning("Test runner is already running")
            return self._get_current_results()

        logger.info("Starting comprehensive test suite...")
        self.status = RunnerStatus.RUNNING
        self.start_time = datetime.now()
        self.cancelled = False

        try:
            # Phase 1: Setup
            if not self.cancelled:
                self._run_phase(TestPhase.SETUP, self._setup_environment)

            # Phase 2: Unit Tests
            if not self.cancelled:
                self._run_phase(TestPhase.UNIT_TESTS, self._run_unit_tests)

            # Phase 3: Integration Tests
            if not self.cancelled:
                self._run_phase(
                    TestPhase.INTEGRATION_TESTS, self._run_integration_tests
                )

            # Phase 4: Performance Tests
            if not self.cancelled and self.config.enable_performance_tests:
                self._run_phase(
                    TestPhase.PERFORMANCE_TESTS, self._run_performance_tests
                )

            # Phase 5: Security Tests
            if not self.cancelled and self.config.enable_security_audit:
                self._run_phase(TestPhase.SECURITY_TESTS, self._run_security_tests)

            # Phase 6: E2E Tests
            if not self.cancelled and self.config.enable_e2e_tests:
                self._run_phase(TestPhase.E2E_TESTS, self._run_e2e_tests)

            # Phase 7: Coverage Analysis
            if not self.cancelled and self.config.enable_coverage_analysis:
                self._run_phase(
                    TestPhase.COVERAGE_ANALYSIS, self._run_coverage_analysis
                )

            # Phase 8: Load Tests
            if not self.cancelled and self.config.enable_load_tests:
                self._run_phase(TestPhase.LOAD_TESTS, self._run_load_tests)

            # Phase 9: Cleanup
            if not self.cancelled:
                self._run_phase(TestPhase.CLEANUP, self._cleanup_environment)

            # Finalize results
            self.end_time = datetime.now()

            if self.cancelled:
                self.status = RunnerStatus.CANCELLED
                logger.info("Test run was cancelled")
            else:
                self.status = RunnerStatus.COMPLETED
                logger.info("Comprehensive test suite completed")

            # Generate final report
            final_report = self._generate_final_report()

            # Send notifications if configured
            if self.config.send_notifications:
                self._send_notifications(final_report)

            return final_report

        except Exception as e:
            self.status = RunnerStatus.FAILED
            self.end_time = datetime.now()
            logger.error(f"Test run failed: {e}")
            return self._generate_final_report()

    def _run_phase(self, phase: TestPhase, phase_function: Callable) -> TestResult:
        """Run a specific test phase"""
        logger.info(f"Starting phase: {phase.value}")
        self.current_phase = phase

        start_time = datetime.now()
        status = "passed"
        error_message = None
        details = {}
        logs = []

        try:
            # Run the phase function
            result = phase_function()
            if isinstance(result, dict):
                details = result
            else:
                details = {"result": str(result)}

            logs.append(f"Phase {phase.value} completed successfully")

        except Exception as e:
            status = "failed"
            error_message = str(e)
            logs.append(f"Phase {phase.value} failed: {e}")
            logger.error(f"Phase {phase.value} failed: {e}")

            if not self.config.continue_on_failure:
                raise e

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        test_result = TestResult(
            phase=phase,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            details=details,
            error_message=error_message,
            logs=logs,
        )

        self.results[phase] = test_result

        # Update dashboard if available
        if self.dashboard:
            self.dashboard.update_test_execution(
                test_id=phase.value,
                suite_id="master_runner",
                status=status,
                progress=100.0,
                current_step=f"Completed {phase.value}",
            )

        logger.info(f"Phase {phase.value} completed in {duration:.2f} seconds")
        return test_result

    def _setup_environment(self) -> Dict[str, Any]:
        """Setup test environment"""
        logger.info("Setting up test environment...")

        setup_details = {
            "database_initialized": False,
            "test_data_created": False,
            "services_started": False,
        }

        # Initialize database
        try:
            if self.data_manager:
                self.data_manager.setup_test_database()
                setup_details["database_initialized"] = True
                logger.info("Database initialized")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")

        # Create test data
        try:
            if self.data_manager:
                self.data_manager.create_test_data()
                setup_details["test_data_created"] = True
                logger.info("Test data created")
        except Exception as e:
            logger.warning(f"Test data creation failed: {e}")

        # Start monitoring if enabled
        try:
            if self.monitoring_system:
                self.monitoring_system.start_monitoring(interval=30)
                setup_details["services_started"] = True
                logger.info("Monitoring started")
        except Exception as e:
            logger.warning(f"Monitoring start failed: {e}")

        # Start dashboard if enabled
        try:
            if self.dashboard and self.config.enable_dashboard:
                self.dashboard.start()
                if self.config.dashboard_auto_open:
                    logger.info("Dashboard started and opened in browser")
                else:
                    logger.info("Dashboard started")
        except Exception as e:
            logger.warning(f"Dashboard start failed: {e}")

        return setup_details

    def _run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        logger.info("Running unit tests...")

        if not self.automation_framework:
            return {"status": "skipped", "reason": "Automation framework not available"}

        # Add unit test cases
        unit_tests = [
            TestCase(
                id="test_user_model",
                name="User Model Test",
                description="Test user model functionality",
                category="unit",
                priority=TestPriority.HIGH,
                timeout=60,
            ),
            TestCase(
                id="test_auth_service",
                name="Authentication Service Test",
                description="Test authentication service",
                category="unit",
                priority=TestPriority.CRITICAL,
                timeout=120,
            ),
            TestCase(
                id="test_job_service",
                name="Job Service Test",
                description="Test job service functionality",
                category="unit",
                priority=TestPriority.HIGH,
                timeout=90,
            ),
        ]

        for test in unit_tests:
            self.automation_framework.add_test_case("unit", test)

        # Run unit test suite
        results = self.automation_framework.run_test_suite("unit")

        return {
            "total_tests": results.get("total_tests", 0),
            "passed": results.get("passed", 0),
            "failed": results.get("failed", 0),
            "duration": results.get("duration", 0),
        }

    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        logger.info("Running integration tests...")

        if not self.automation_framework:
            return {"status": "skipped", "reason": "Automation framework not available"}

        # Add integration test cases
        integration_tests = [
            TestCase(
                id="test_auth_flow",
                name="Authentication Flow Test",
                description="Test complete authentication flow",
                category="integration",
                priority=TestPriority.CRITICAL,
                timeout=180,
            ),
            TestCase(
                id="test_job_creation_flow",
                name="Job Creation Flow Test",
                description="Test job creation and management flow",
                category="integration",
                priority=TestPriority.HIGH,
                timeout=150,
            ),
            TestCase(
                id="test_user_job_interaction",
                name="User-Job Interaction Test",
                description="Test user interactions with jobs",
                category="integration",
                priority=TestPriority.HIGH,
                timeout=120,
            ),
        ]

        for test in integration_tests:
            self.automation_framework.add_test_case("integration", test)

        # Run integration test suite
        results = self.automation_framework.run_test_suite("integration")

        return {
            "total_tests": results.get("total_tests", 0),
            "passed": results.get("passed", 0),
            "failed": results.get("failed", 0),
            "duration": results.get("duration", 0),
        }

    def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        logger.info("Running performance tests...")

        if not self.load_testing:
            return {
                "status": "skipped",
                "reason": "Load testing framework not available",
            }

        # Run performance tests
        performance_results = self.load_testing.run_performance_tests()

        return {
            "load_test_results": performance_results.get("load_test_results", {}),
            "stress_test_results": performance_results.get("stress_test_results", {}),
            "memory_test_results": performance_results.get("memory_test_results", {}),
            "database_test_results": performance_results.get(
                "database_test_results", {}
            ),
        }

    def _run_security_tests(self) -> Dict[str, Any]:
        """Run security tests"""
        logger.info("Running security tests...")

        if not self.security_auditor:
            return {"status": "skipped", "reason": "Security auditor not available"}

        # Run security audit
        audit_results = self.security_auditor.run_full_audit()

        return {
            "total_vulnerabilities": audit_results.get("total_vulnerabilities", 0),
            "vulnerabilities_by_level": audit_results.get(
                "vulnerabilities_by_level", {}
            ),
            "security_score": audit_results.get("security_score", 0),
            "recommendations": audit_results.get("recommendations", []),
        }

    def _run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests"""
        logger.info("Running E2E tests...")

        if not self.e2e_runner:
            return {"status": "skipped", "reason": "E2E runner not available"}

        # Run E2E tests
        e2e_results = self.e2e_runner.run_all_scenarios()

        return {
            "total_scenarios": e2e_results.get("total_scenarios", 0),
            "passed_scenarios": e2e_results.get("passed_scenarios", 0),
            "failed_scenarios": e2e_results.get("failed_scenarios", 0),
            "duration": e2e_results.get("duration", 0),
        }

    def _run_coverage_analysis(self) -> Dict[str, Any]:
        """Run coverage analysis"""
        logger.info("Running coverage analysis...")

        if not self.coverage_analyzer:
            return {"status": "skipped", "reason": "Coverage analyzer not available"}

        # Run coverage analysis
        coverage_results = self.coverage_analyzer.run_coverage_analysis()

        return {
            "overall_coverage": coverage_results.get("overall_coverage", 0),
            "module_coverage": coverage_results.get("module_coverage", {}),
            "uncovered_lines": coverage_results.get("uncovered_lines", []),
            "recommendations": coverage_results.get("recommendations", []),
        }

    def _run_load_tests(self) -> Dict[str, Any]:
        """Run load tests"""
        logger.info("Running load tests...")

        if not self.load_testing:
            return {
                "status": "skipped",
                "reason": "Load testing framework not available",
            }

        # Run load tests
        load_results = self.load_testing.run_load_tests()

        return {
            "concurrent_users": load_results.get("concurrent_users", 0),
            "response_times": load_results.get("response_times", {}),
            "throughput": load_results.get("throughput", 0),
            "error_rate": load_results.get("error_rate", 0),
        }

    def _cleanup_environment(self) -> Dict[str, Any]:
        """Cleanup test environment"""
        logger.info("Cleaning up test environment...")

        cleanup_details = {
            "monitoring_stopped": False,
            "dashboard_stopped": False,
            "test_data_cleaned": False,
            "database_cleaned": False,
        }

        # Stop monitoring
        try:
            if self.monitoring_system:
                self.monitoring_system.stop_monitoring()
                cleanup_details["monitoring_stopped"] = True
                logger.info("Monitoring stopped")
        except Exception as e:
            logger.warning(f"Monitoring stop failed: {e}")

        # Stop dashboard
        try:
            if self.dashboard:
                self.dashboard.stop()
                cleanup_details["dashboard_stopped"] = True
                logger.info("Dashboard stopped")
        except Exception as e:
            logger.warning(f"Dashboard stop failed: {e}")

        # Clean test data
        try:
            if self.data_manager:
                self.data_manager.cleanup_test_data()
                cleanup_details["test_data_cleaned"] = True
                logger.info("Test data cleaned")
        except Exception as e:
            logger.warning(f"Test data cleanup failed: {e}")

        # Clean database
        try:
            if self.data_manager:
                self.data_manager.cleanup_database()
                cleanup_details["database_cleaned"] = True
                logger.info("Database cleaned")
        except Exception as e:
            logger.warning(f"Database cleanup failed: {e}")

        return cleanup_details

    def cancel(self):
        """Cancel the current test run"""
        self.cancelled = True
        logger.info("Test run cancellation requested")

    def _get_current_results(self) -> Dict[str, Any]:
        """Get current test results"""
        return {
            "status": self.status.value,
            "start_time": self.start_time,
            "current_phase": self.current_phase.value if self.current_phase else None,
            "results": {
                phase.value: asdict(result) for phase, result in self.results.items()
            },
        }

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final test report"""
        total_duration = (
            (self.end_time - self.start_time).total_seconds()
            if self.end_time and self.start_time
            else 0
        )

        # Calculate summary statistics
        total_phases = len(self.results)
        passed_phases = len([r for r in self.results.values() if r.status == "passed"])
        failed_phases = len([r for r in self.results.values() if r.status == "failed"])
        skipped_phases = len(
            [r for r in self.results.values() if r.status == "skipped"]
        )

        report = {
            "test_run_id": f"run_{int(time.time())}",
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration": total_duration,
            "summary": {
                "total_phases": total_phases,
                "passed_phases": passed_phases,
                "failed_phases": failed_phases,
                "skipped_phases": skipped_phases,
                "success_rate": (
                    (passed_phases / total_phases * 100) if total_phases > 0 else 0
                ),
            },
            "phase_results": {
                phase.value: {
                    "status": result.status,
                    "duration": result.duration,
                    "details": result.details,
                    "error_message": result.error_message,
                    "logs": result.logs,
                }
                for phase, result in self.results.items()
            },
            "configuration": asdict(self.config),
        }

        # Save report if configured
        if self.config.generate_reports:
            self._save_report(report)

        return report

    def _save_report(self, report: Dict[str, Any]):
        """Save test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.config.report_format == "json":
            report_file = f"test_report_{timestamp}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Report saved to {report_file}")

        elif self.config.report_format == "html":
            report_file = f"test_report_{timestamp}.html"
            html_content = self._generate_html_report(report)
            with open(report_file, "w") as f:
                f.write(html_content)
            logger.info(f"Report saved to {report_file}")

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {report['test_run_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .phase-result {{ margin: 10px 0; padding: 10px; border-radius: 3px; }}
        .passed {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
        .failed {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        .skipped {{ background-color: #e2e3e5; border: 1px solid #d6d8db; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Report</h1>
        <p>Run ID: {report['test_run_id']}</p>
        <p>Status: {report['status']}</p>
        <p>Duration: {report['total_duration']:.2f} seconds</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Phases: {report['summary']['total_phases']}</p>
        <p>Passed: {report['summary']['passed_phases']}</p>
        <p>Failed: {report['summary']['failed_phases']}</p>
        <p>Skipped: {report['summary']['skipped_phases']}</p>
        <p>Success Rate: {report['summary']['success_rate']:.2f}%</p>
    </div>
    
    <div class="results">
        <h2>Phase Results</h2>
        {self._generate_phase_results_html(report['phase_results'])}
    </div>
</body>
</html>
        """

    def _generate_phase_results_html(self, phase_results: Dict[str, Any]) -> str:
        """Generate HTML for phase results"""
        html = ""
        for phase, result in phase_results.items():
            html += f"""
        <div class="phase-result {result['status']}">
            <h3>{phase.replace('_', ' ').title()}</h3>
            <p>Status: {result['status']}</p>
            <p>Duration: {result['duration']:.2f} seconds</p>
            {f"<p>Error: {result['error_message']}</p>" if result['error_message'] else ""}
        </div>
            """
        return html

    def _send_notifications(self, report: Dict[str, Any]):
        """Send notifications about test results"""
        if not self.config.send_notifications:
            return

        # Email notification
        if self.config.notification_email:
            self._send_email_notification(report)

        # Webhook notification
        if self.config.notification_webhook:
            self._send_webhook_notification(report)

    def _send_email_notification(self, report: Dict[str, Any]):
        """Send email notification"""
        # Implementation would depend on email service
        logger.info(
            f"Email notification would be sent to {self.config.notification_email}"
        )

    def _send_webhook_notification(self, report: Dict[str, Any]):
        """Send webhook notification"""
        try:
            payload = {
                "test_run_id": report["test_run_id"],
                "status": report["status"],
                "success_rate": report["summary"]["success_rate"],
                "duration": report["total_duration"],
            }

            response = requests.post(self.config.notification_webhook, json=payload)
            response.raise_for_status()
            logger.info("Webhook notification sent successfully")

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")


def load_config_from_file(config_path: str) -> MasterTestConfig:
    """Load configuration from YAML file"""
    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        return MasterTestConfig(**config_data)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return MasterTestConfig()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return MasterTestConfig()


def main():
    """Main function for the master test runner"""
    parser = argparse.ArgumentParser(description="Master Test Runner for Backend")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument(
        "--parallel", "-p", action="store_true", help="Enable parallel execution"
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=4, help="Number of workers"
    )
    parser.add_argument(
        "--timeout", "-t", type=int, default=1800, help="Timeout per phase in seconds"
    )
    parser.add_argument(
        "--continue-on-failure", action="store_true", help="Continue on phase failure"
    )
    parser.add_argument(
        "--dashboard-port", type=int, default=8080, help="Dashboard port"
    )
    parser.add_argument("--no-dashboard", action="store_true", help="Disable dashboard")
    parser.add_argument(
        "--no-monitoring", action="store_true", help="Disable monitoring"
    )
    parser.add_argument(
        "--no-security", action="store_true", help="Disable security tests"
    )
    parser.add_argument(
        "--no-performance", action="store_true", help="Disable performance tests"
    )
    parser.add_argument("--no-e2e", action="store_true", help="Disable E2E tests")
    parser.add_argument(
        "--no-coverage", action="store_true", help="Disable coverage analysis"
    )
    parser.add_argument("--no-load", action="store_true", help="Disable load tests")
    parser.add_argument(
        "--report-format",
        choices=["json", "html"],
        default="json",
        help="Report format",
    )
    parser.add_argument("--notify-email", help="Email for notifications")
    parser.add_argument("--notify-webhook", help="Webhook URL for notifications")

    args = parser.parse_args()

    # Load configuration
    if args.config:
        config = load_config_from_file(args.config)
    else:
        config = MasterTestConfig()

    # Override with command line arguments
    if args.parallel:
        config.parallel_execution = True
    if args.workers:
        config.max_workers = args.workers
    if args.timeout:
        config.timeout_per_phase = args.timeout
    if args.continue_on_failure:
        config.continue_on_failure = True
    if args.dashboard_port:
        config.dashboard_port = args.dashboard_port
    if args.no_dashboard:
        config.enable_dashboard = False
    if args.no_monitoring:
        config.enable_monitoring = False
    if args.no_security:
        config.enable_security_audit = False
    if args.no_performance:
        config.enable_performance_tests = False
    if args.no_e2e:
        config.enable_e2e_tests = False
    if args.no_coverage:
        config.enable_coverage_analysis = False
    if args.no_load:
        config.enable_load_tests = False
    if args.report_format:
        config.report_format = args.report_format
    if args.notify_email:
        config.send_notifications = True
        config.notification_email = args.notify_email
    if args.notify_webhook:
        config.send_notifications = True
        config.notification_webhook = args.notify_webhook

    # Create and run master test runner
    runner = MasterTestRunner(config)

    print("Starting Master Test Runner...")
    print(f"Configuration: {asdict(config)}")

    try:
        results = runner.run_comprehensive_tests()

        print("\n" + "=" * 50)
        print("TEST RUN COMPLETED")
        print("=" * 50)
        print(f"Status: {results['status']}")
        print(f"Duration: {results['total_duration']:.2f} seconds")
        print(f"Success Rate: {results['summary']['success_rate']:.2f}%")
        print(f"Passed Phases: {results['summary']['passed_phases']}")
        print(f"Failed Phases: {results['summary']['failed_phases']}")
        print(f"Skipped Phases: {results['summary']['skipped_phases']}")

        if results["status"] == "completed":
            print("\n✅ All tests completed successfully!")
        elif results["status"] == "failed":
            print("\n❌ Some tests failed!")
        elif results["status"] == "cancelled":
            print("\n⚠️ Test run was cancelled!")

    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        runner.cancel()
    except Exception as e:
        print(f"\nTest run failed with error: {e}")
        logger.error(f"Test run failed: {e}")


if __name__ == "__main__":
    main()
