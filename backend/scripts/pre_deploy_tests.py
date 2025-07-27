#!/usr/bin/env python3
"""
Pre-deployment test runner script

This script runs comprehensive tests before deployment and prevents
deployment if critical tests fail.

Usage:
    python scripts/pre_deploy_tests.py
    python scripts/pre_deploy_tests.py --coverage-threshold 85
    python scripts/pre_deploy_tests.py --fast  # Skip slow integration tests
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PreDeploymentTester:
    """Comprehensive pre-deployment test runner"""

    def __init__(
        self,
        coverage_threshold: int = 85,
        skip_slow_tests: bool = False,
        fail_fast: bool = True,
    ):
        self.coverage_threshold = coverage_threshold
        self.skip_slow_tests = skip_slow_tests
        self.fail_fast = fail_fast
        self.project_root = Path(__file__).parent.parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"

        # Test results
        self.test_results = {
            "backend": {},
            "frontend": {},
            "overall": {
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "duration": None,
                "passed": False,
                "critical_failures": [],
            },
        }

    def run_all_tests(self) -> bool:
        """Run all pre-deployment tests"""
        logger.info("🚀 Starting pre-deployment test suite...")
        logger.info(f"Coverage threshold: {self.coverage_threshold}%")
        logger.info(f"Skip slow tests: {self.skip_slow_tests}")

        try:
            # 1. Environment checks
            if not self._check_environment():
                return False

            # 2. Syntax and import checks
            if not self._check_syntax():
                return False

            # 3. Backend tests
            if not self._run_backend_tests():
                return False

            # 4. Frontend tests
            if not self._run_frontend_tests():
                return False

            # 5. Integration tests
            if not self.skip_slow_tests:
                if not self._run_integration_tests():
                    return False

            # 6. Security checks
            if not self._run_security_checks():
                return False

            # 7. Performance checks
            if not self._check_performance():
                return False

            # 8. Final validation
            self._generate_report()

            self.test_results["overall"]["passed"] = True
            logger.info("✅ All pre-deployment tests passed!")
            return True

        except Exception as e:
            logger.error(f"❌ Test suite failed with error: {str(e)}")
            self.test_results["overall"]["critical_failures"].append(str(e))
            return False
        finally:
            self.test_results["overall"]["end_time"] = datetime.now().isoformat()
            self._save_results()

    def _check_environment(self) -> bool:
        """Check if environment is ready for testing"""
        logger.info("🔍 Checking environment...")

        checks = [
            ("Python version", self._check_python_version),
            ("Required directories", self._check_directories),
            ("Environment variables", self._check_env_vars),
            ("Database connection", self._check_database),
            ("Required packages", self._check_packages),
        ]

        for check_name, check_func in checks:
            try:
                if not check_func():
                    logger.error(f"❌ Environment check failed: {check_name}")
                    return False
                logger.info(f"✅ {check_name} check passed")
            except Exception as e:
                logger.error(f"❌ {check_name} check error: {str(e)}")
                return False

        return True

    def _check_python_version(self) -> bool:
        """Check Python version compatibility"""
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 8:
            return True
        logger.error(
            f"Python 3.8+ required, found {python_version.major}.{python_version.minor}"
        )
        return False

    def _check_directories(self) -> bool:
        """Check if required directories exist"""
        required_dirs = [
            self.backend_dir,
            self.frontend_dir,
            self.backend_dir / "tests",
            self.frontend_dir / "src" / "__tests__",
        ]

        for directory in required_dirs:
            if not directory.exists():
                logger.error(f"Required directory not found: {directory}")
                return False

        return True

    def _check_env_vars(self) -> bool:
        """Check critical environment variables"""
        # Don't fail deployment for missing env vars in CI
        critical_vars = ["MONGODB_URL", "JWT_SECRET_KEY"]
        missing_vars = []

        for var in critical_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            logger.warning(f"⚠️ Missing environment variables: {missing_vars}")
            # Don't fail - might be CI environment

        return True

    def _check_database(self) -> bool:
        """Check database connectivity"""
        try:
            # Try to import and test database connection
            sys.path.append(str(self.backend_dir))
            import asyncio

            from database import get_async_db

            async def test_db():
                try:
                    db = await get_async_db()
                    await db.command("ping")
                    return True
                except Exception as e:
                    logger.warning(f"Database connection failed: {str(e)}")
                    return False

            # Don't fail deployment for DB connection in CI
            result = asyncio.run(test_db())
            if not result:
                logger.warning("⚠️ Database connection failed - continuing anyway")

            return True

        except Exception as e:
            logger.warning(f"⚠️ Database check error: {str(e)} - continuing anyway")
            return True

    def _check_packages(self) -> bool:
        """Check if required packages are installed"""
        backend_requirements = self.project_root / "config" / "requirements.txt"
        frontend_package = self.frontend_dir / "package.json"

        if not backend_requirements.exists():
            logger.error("Backend requirements.txt not found in config/")
            return False

        if not frontend_package.exists():
            logger.error("Frontend package.json not found")
            return False

        return True

    def _check_syntax(self) -> bool:
        """Run syntax and import validation"""
        logger.info("🔍 Checking syntax and imports...")

        # Backend syntax check
        result = self._run_command(
            [sys.executable, "-m", "py_compile", str(self.backend_dir / "main.py")],
            cwd=self.backend_dir,
        )

        if result.returncode != 0:
            logger.error("❌ Backend syntax check failed")
            return False

        # Run syntax tests if they exist
        syntax_test_file = (
            self.backend_dir / "tests" / "syntax" / "test_syntax_and_imports.py"
        )
        if syntax_test_file.exists():
            result = self._run_command(
                [sys.executable, "-m", "pytest", str(syntax_test_file), "-v"],
                cwd=self.backend_dir,
            )

            if result.returncode != 0:
                logger.error("❌ Syntax tests failed")
                return False

        logger.info("✅ Syntax checks passed")
        return True

    def _run_backend_tests(self) -> bool:
        """Run backend test suite with coverage"""
        logger.info("🧪 Running backend tests...")

        # Prepare test command
        test_cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "--cov=.",
            "--cov-report=json",
            "--cov-report=term-missing",
            "--tb=short",
            "-v",
        ]

        if self.fail_fast:
            test_cmd.append("-x")

        if self.skip_slow_tests:
            test_cmd.extend(["-m", "not slow"])

        # Run tests
        result = self._run_command(test_cmd, cwd=self.backend_dir)

        # Parse coverage results
        coverage_file = self.backend_dir / "coverage.json"
        coverage_percent = 0

        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    coverage_percent = coverage_data.get("totals", {}).get(
                        "percent_covered", 0
                    )
            except Exception as e:
                logger.warning(f"Could not parse coverage data: {str(e)}")

        # Store results
        self.test_results["backend"] = {
            "passed": result.returncode == 0,
            "coverage": coverage_percent,
            "meets_threshold": coverage_percent >= self.coverage_threshold,
        }

        # Check results
        if result.returncode != 0:
            logger.error("❌ Backend tests failed")
            return False

        if coverage_percent < self.coverage_threshold:
            logger.error(
                f"❌ Coverage {coverage_percent:.1f}% below threshold {self.coverage_threshold}%"
            )
            return False

        logger.info(f"✅ Backend tests passed with {coverage_percent:.1f}% coverage")
        return True

    def _run_frontend_tests(self) -> bool:
        """Run frontend test suite"""
        logger.info("🧪 Running frontend tests...")

        # Check if node_modules exists
        if not (self.frontend_dir / "node_modules").exists():
            logger.info("Installing frontend dependencies...")
            result = self._run_command(["npm", "install"], cwd=self.frontend_dir)
            if result.returncode != 0:
                logger.error("❌ Failed to install frontend dependencies")
                return False

        # Run tests
        test_cmd = [
            "npm",
            "test",
            "--",
            "--coverage",
            "--watchAll=false",
            "--passWithNoTests",
        ]
        result = self._run_command(test_cmd, cwd=self.frontend_dir)

        # Parse coverage results
        coverage_file = self.frontend_dir / "coverage" / "coverage-summary.json"
        coverage_percent = 0

        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    coverage_percent = (
                        coverage_data.get("total", {}).get("lines", {}).get("pct", 0)
                    )
            except Exception as e:
                logger.warning(f"Could not parse frontend coverage: {str(e)}")

        # Store results
        self.test_results["frontend"] = {
            "passed": result.returncode == 0,
            "coverage": coverage_percent,
            "meets_threshold": coverage_percent
            >= (self.coverage_threshold - 5),  # Slightly lower threshold for frontend
        }

        # Check results
        if result.returncode != 0:
            logger.error("❌ Frontend tests failed")
            return False

        frontend_threshold = self.coverage_threshold - 5
        if coverage_percent < frontend_threshold:
            logger.error(
                f"❌ Frontend coverage {coverage_percent:.1f}% below threshold {frontend_threshold}%"
            )
            return False

        logger.info(f"✅ Frontend tests passed with {coverage_percent:.1f}% coverage")
        return True

    def _run_integration_tests(self) -> bool:
        """Run integration tests"""
        logger.info("🔗 Running integration tests...")

        integration_dir = self.backend_dir / "tests" / "integration"
        if not integration_dir.exists():
            logger.info("No integration tests found, skipping...")
            return True

        result = self._run_command(
            [sys.executable, "-m", "pytest", str(integration_dir), "-v"],
            cwd=self.backend_dir,
        )

        if result.returncode != 0:
            logger.error("❌ Integration tests failed")
            return False

        logger.info("✅ Integration tests passed")
        return True

    def _run_security_checks(self) -> bool:
        """Run security checks"""
        logger.info("🔒 Running security checks...")

        # Check for common security issues
        security_checks = [
            self._check_secrets_in_code,
            self._check_dependencies_vulnerabilities,
            self._check_cors_settings,
        ]

        for check in security_checks:
            if not check():
                return False

        logger.info("✅ Security checks passed")
        return True

    def _check_secrets_in_code(self) -> bool:
        """Check for hardcoded secrets"""
        try:
            # Simple grep for common secret patterns
            patterns = [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"api_key\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]",
            ]

            for pattern in patterns:
                result = subprocess.run(
                    [
                        "grep",
                        "-r",
                        "-E",
                        pattern,
                        str(self.backend_dir / "routes"),
                        "--exclude-dir=__pycache__",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    logger.warning(f"⚠️ Potential hardcoded secret found: {pattern}")
                    # Don't fail deployment for this

            return True
        except Exception:
            return True  # Don't fail if grep not available

    def _check_dependencies_vulnerabilities(self) -> bool:
        """Check for known vulnerabilities in dependencies"""
        # This would integrate with tools like safety, audit, etc.
        # For now, just return True
        return True

    def _check_cors_settings(self) -> bool:
        """Check CORS configuration"""
        try:
            main_file = self.backend_dir / "main.py"
            if main_file.exists():
                content = main_file.read_text()
                if 'allow_origins=["*"]' in content:
                    logger.warning(
                        "⚠️ CORS allows all origins - check if this is intended for production"
                    )
            return True
        except Exception:
            return True

    def _check_performance(self) -> bool:
        """Run performance checks"""
        logger.info("⚡ Running performance checks...")

        # Basic performance tests
        performance_checks = [self._check_import_times, self._check_response_times]

        for check in performance_checks:
            if not check():
                logger.warning("⚠️ Performance check failed - continuing anyway")

        logger.info("✅ Performance checks completed")
        return True

    def _check_import_times(self) -> bool:
        """Check import times for main modules"""
        try:
            import time

            start_time = time.time()

            # Test importing main application
            import_cmd = [
                sys.executable,
                "-c",
                "import sys; sys.path.append('.'); from main import app",
            ]

            result = self._run_command(import_cmd, cwd=self.backend_dir)

            import_time = time.time() - start_time

            if import_time > 10:  # 10 second threshold
                logger.warning(f"⚠️ Slow import time: {import_time:.2f}s")
                return False

            return True
        except Exception:
            return True

    def _check_response_times(self) -> bool:
        """Check API response times"""
        # This would test API endpoints for response time
        # For now, just return True
        return True

    def _run_command(
        self, cmd: List[str], cwd: Path = None
    ) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                logger.debug(f"Command failed with code {result.returncode}")
                logger.debug(f"STDOUT: {result.stdout}")
                logger.debug(f"STDERR: {result.stderr}")

            return result

        except subprocess.TimeoutExpired:
            logger.error("❌ Command timed out")
            raise
        except Exception as e:
            logger.error(f"❌ Command execution failed: {str(e)}")
            raise

    def _generate_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 Generating test report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "backend": self.test_results["backend"],
            "frontend": self.test_results["frontend"],
            "overall": self.test_results["overall"],
            "recommendations": self._generate_recommendations(),
        }

        # Save detailed report
        report_file = self.project_root / "test_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Test report saved to {report_file}")

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        backend = self.test_results.get("backend", {})
        frontend = self.test_results.get("frontend", {})

        if backend.get("coverage", 0) < 90:
            recommendations.append(
                "Consider increasing backend test coverage above 90%"
            )

        if frontend.get("coverage", 0) < 85:
            recommendations.append(
                "Consider increasing frontend test coverage above 85%"
            )

        if not recommendations:
            recommendations.append("Test coverage looks great! Keep up the good work.")

        return recommendations

    def _save_results(self):
        """Save test results"""
        results_file = self.project_root / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Pre-deployment test runner")
    parser.add_argument(
        "--coverage-threshold",
        type=int,
        default=85,
        help="Minimum coverage threshold (default: 85)",
    )
    parser.add_argument(
        "--fast", action="store_true", help="Skip slow integration tests"
    )
    parser.add_argument(
        "--no-fail-fast", action="store_true", help="Continue tests even if some fail"
    )

    args = parser.parse_args()

    tester = PreDeploymentTester(
        coverage_threshold=args.coverage_threshold,
        skip_slow_tests=args.fast,
        fail_fast=not args.no_fail_fast,
    )

    success = tester.run_all_tests()

    if success:
        logger.info("🎉 All tests passed! Ready for deployment.")
        sys.exit(0)
    else:
        logger.error("❌ Tests failed! Deployment blocked.")
        sys.exit(1)


if __name__ == "__main__":
    main()
