#!/usr/bin/env python3
"""
Priority Test Runner for Buzz2Remote Backend
Runs critical tests in order of priority
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class PriorityTestRunner:
    """Priority-based test runner for critical functionality"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.log_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Test categories in priority order
        self.test_categories = {
            "sanity": {
                "description": "Basic sanity checks",
                "files": ["tests/test_sanity.py"],
                "priority": 1,
                "critical": True
            },
            "performance": {
                "description": "Performance and load tests",
                "files": ["tests/performance/test_load_performance.py"],
                "priority": 2,
                "critical": True
            },
            "database": {
                "description": "Database migration and schema tests",
                "files": ["tests/database/test_migrations.py"],
                "priority": 3,
                "critical": True
            },
            "e2e": {
                "description": "End-to-end user journey tests",
                "files": ["tests/e2e/test_complete_user_journey.py"],
                "priority": 4,
                "critical": True
            },
            "api_critical": {
                "description": "Critical API functionality",
                "files": [
                    "tests/api/test_jobs_coverage.py",
                    "tests/api/test_auth_comprehensive.py",
                    "tests/api/test_applications_comprehensive.py"
                ],
                "priority": 5,
                "critical": True
            },
            "security": {
                "description": "Security and authentication tests",
                "files": [
                    "tests/api/test_security_comprehensive.py",
                    "tests/test_api_security.py"
                ],
                "priority": 6,
                "critical": True
            },
            "services": {
                "description": "Core service functionality",
                "files": [
                    "tests/services/test_ai_services_coverage.py",
                    "tests/services/test_performance_analytics_service.py"
                ],
                "priority": 7,
                "critical": False
            },
            "unit": {
                "description": "Unit tests for core components",
                "files": [
                    "tests/unit/test_utils_comprehensive.py",
                    "tests/unit/test_database.py"
                ],
                "priority": 8,
                "critical": False
            }
        }
    
    def run_test_file(self, test_file):
        """Run a single test file"""
        try:
            print(f"Running {test_file}...")
            
            # Check if file exists
            if not os.path.exists(test_file):
                print(f"⚠️  Test file not found: {test_file}")
                return {
                    "status": "skipped",
                    "reason": "File not found",
                    "duration": 0,
                    "tests_run": 0,
                    "tests_passed": 0,
                    "tests_failed": 0
                }
            
            # Run pytest on the file
            start_time = time.time()
            result = subprocess.run(
                ["python", "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            end_time = time.time()
            
            duration = end_time - start_time
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            tests_run = 0
            tests_passed = 0
            tests_failed = 0
            
            for line in output_lines:
                if "passed" in line and "failed" in line:
                    # Extract test counts
                    parts = line.split()
                    for part in parts:
                        if part.endswith("passed"):
                            tests_passed = int(part.split()[0])
                        elif part.endswith("failed"):
                            tests_failed = int(part.split()[0])
                    tests_run = tests_passed + tests_failed
                    break
            
            if result.returncode == 0:
                status = "passed"
            elif result.returncode == 1:
                status = "failed"
            else:
                status = "error"
            
            return {
                "status": status,
                "duration": duration,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout running {test_file}")
            return {
                "status": "timeout",
                "duration": 300,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "stdout": "",
                "stderr": "Test timeout after 5 minutes"
            }
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            return {
                "status": "error",
                "duration": 0,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "stdout": "",
                "stderr": str(e)
            }
    
    def run_category(self, category_name, category_info):
        """Run all tests in a category"""
        print(f"\n{'='*60}")
        print(f"🏃 Running {category_name.upper()} tests")
        print(f"📝 {category_info['description']}")
        print(f"🎯 Priority: {category_info['priority']}")
        print(f"🚨 Critical: {category_info['critical']}")
        print(f"{'='*60}")
        
        category_results = {
            "description": category_info["description"],
            "priority": category_info["priority"],
            "critical": category_info["critical"],
            "files": {},
            "summary": {
                "total_files": len(category_info["files"]),
                "files_passed": 0,
                "files_failed": 0,
                "files_skipped": 0,
                "total_tests": 0,
                "total_passed": 0,
                "total_failed": 0,
                "total_duration": 0
            }
        }
        
        for test_file in category_info["files"]:
            result = self.run_test_file(test_file)
            category_results["files"][test_file] = result
            
            # Update summary
            category_results["summary"]["total_duration"] += result["duration"]
            category_results["summary"]["total_tests"] += result["tests_run"]
            category_results["summary"]["total_passed"] += result["tests_passed"]
            category_results["summary"]["total_failed"] += result["tests_failed"]
            
            if result["status"] == "passed":
                category_results["summary"]["files_passed"] += 1
                print(f"✅ {test_file} - PASSED ({result['tests_passed']} tests, {result['duration']:.2f}s)")
            elif result["status"] == "failed":
                category_results["summary"]["files_failed"] += 1
                print(f"❌ {test_file} - FAILED ({result['tests_failed']} failed, {result['duration']:.2f}s)")
            elif result["status"] == "skipped":
                category_results["summary"]["files_skipped"] += 1
                print(f"⏭️  {test_file} - SKIPPED")
            else:
                category_results["summary"]["files_failed"] += 1
                print(f"💥 {test_file} - ERROR ({result['status']})")
        
        # Print category summary
        summary = category_results["summary"]
        print(f"\n📊 {category_name.upper()} Summary:")
        print(f"   Files: {summary['files_passed']} passed, {summary['files_failed']} failed, {summary['files_skipped']} skipped")
        print(f"   Tests: {summary['total_passed']} passed, {summary['total_failed']} failed")
        print(f"   Duration: {summary['total_duration']:.2f}s")
        
        return category_results
    
    def run_all_tests(self):
        """Run all test categories in priority order"""
        print("🚀 Starting Priority Test Runner for Buzz2Remote Backend")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Sort categories by priority
        sorted_categories = sorted(
            self.test_categories.items(),
            key=lambda x: x[1]["priority"]
        )
        
        total_start_time = time.time()
        
        for category_name, category_info in sorted_categories:
            try:
                category_results = self.run_category(category_name, category_info)
                self.test_results[category_name] = category_results
                
                # Check if critical tests failed
                if category_info["critical"] and category_results["summary"]["files_failed"] > 0:
                    print(f"\n⚠️  CRITICAL TESTS FAILED in {category_name.upper()}")
                    print("   Consider fixing these before proceeding...")
                    
                    # Ask user if they want to continue
                    response = input("\nContinue with remaining tests? (y/N): ")
                    if response.lower() != 'y':
                        print("🛑 Test execution stopped by user")
                        break
                
            except KeyboardInterrupt:
                print(f"\n🛑 Test execution interrupted during {category_name}")
                break
            except Exception as e:
                print(f"\n💥 Error running {category_name}: {e}")
                self.test_results[category_name] = {
                    "error": str(e),
                    "status": "error"
                }
        
        total_duration = time.time() - total_start_time
        
        # Generate final report
        self.generate_report(total_duration)
    
    def generate_report(self, total_duration):
        """Generate comprehensive test report"""
        print(f"\n{'='*60}")
        print("📋 FINAL TEST REPORT")
        print(f"{'='*60}")
        
        # Calculate overall statistics
        total_files = 0
        total_files_passed = 0
        total_files_failed = 0
        total_files_skipped = 0
        total_tests = 0
        total_tests_passed = 0
        total_tests_failed = 0
        
        critical_failures = []
        
        for category_name, category_results in self.test_results.items():
            if "summary" in category_results:
                summary = category_results["summary"]
                total_files += summary["total_files"]
                total_files_passed += summary["files_passed"]
                total_files_failed += summary["files_failed"]
                total_files_skipped += summary["files_skipped"]
                total_tests += summary["total_tests"]
                total_tests_passed += summary["total_passed"]
                total_tests_failed += summary["total_failed"]
                
                # Check for critical failures
                category_info = self.test_categories[category_name]
                if category_info["critical"] and summary["files_failed"] > 0:
                    critical_failures.append(category_name)
        
        # Print overall statistics
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        print(f"📁 Files: {total_files_passed} passed, {total_files_failed} failed, {total_files_skipped} skipped")
        print(f"🧪 Tests: {total_tests_passed} passed, {total_tests_failed} failed")
        
        if total_tests > 0:
            success_rate = (total_tests_passed / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Print category breakdown
        print(f"\n📊 Category Breakdown:")
        for category_name, category_results in self.test_results.items():
            if "summary" in category_results:
                summary = category_results["summary"]
                status_icon = "✅" if summary["files_failed"] == 0 else "❌"
                print(f"   {status_icon} {category_name}: {summary['files_passed']}/{summary['total_files']} files passed")
        
        # Print critical failures
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"   ❌ {failure}")
        
        # Overall status
        if total_files_failed == 0:
            print(f"\n🎉 ALL TESTS PASSED!")
            overall_status = "SUCCESS"
        elif not critical_failures:
            print(f"\n⚠️  Some non-critical tests failed")
            overall_status = "PARTIAL_SUCCESS"
        else:
            print(f"\n💥 Critical tests failed!")
            overall_status = "FAILURE"
        
        # Save detailed results
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "overall_status": overall_status,
            "statistics": {
                "total_files": total_files,
                "files_passed": total_files_passed,
                "files_failed": total_files_failed,
                "files_skipped": total_files_skipped,
                "total_tests": total_tests,
                "tests_passed": total_tests_passed,
                "tests_failed": total_tests_failed,
                "success_rate": (total_tests_passed / total_tests * 100) if total_tests > 0 else 0
            },
            "critical_failures": critical_failures,
            "categories": self.test_results
        }
        
        with open(self.log_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {self.log_file}")
        print(f"🏁 Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return overall_status

def main():
    """Main entry point"""
    runner = PriorityTestRunner()
    
    try:
        status = runner.run_all_tests()
        sys.exit(0 if status == "SUCCESS" else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()