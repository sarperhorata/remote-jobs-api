#!/usr/bin/env python3
"""
Test Coverage Analysis and Reporting System
Comprehensive coverage analysis for Buzz2Remote Backend
"""

import ast
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class CoverageAnalyzer:
    """Comprehensive test coverage analyzer"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.backend_root = self.project_root / "backend"
        self.coverage_data = {}
        self.file_coverage = {}
        self.module_coverage = {}
        self.function_coverage = {}
        self.class_coverage = {}

        # Coverage thresholds
        self.thresholds = {
            "overall": 80.0,
            "api": 90.0,
            "services": 85.0,
            "models": 95.0,
            "utils": 80.0,
            "database": 90.0,
            "security": 95.0,
        }

    def analyze_code_structure(self):
        """Analyze the codebase structure"""
        print("🔍 Analyzing codebase structure...")

        code_structure = {
            "api": [],
            "services": [],
            "models": [],
            "utils": [],
            "database": [],
            "middleware": [],
            "admin": [],
            "crawler": [],
            "notification": [],
            "telegram_bot": [],
        }

        # Scan backend directory
        for root, dirs, files in os.walk(self.backend_root):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.backend_root)

                    # Categorize files
                    if "api" in str(relative_path):
                        code_structure["api"].append(str(relative_path))
                    elif "services" in str(relative_path):
                        code_structure["services"].append(str(relative_path))
                    elif "models" in str(relative_path):
                        code_structure["models"].append(str(relative_path))
                    elif "utils" in str(relative_path):
                        code_structure["utils"].append(str(relative_path))
                    elif "database" in str(relative_path):
                        code_structure["database"].append(str(relative_path))
                    elif "middleware" in str(relative_path):
                        code_structure["middleware"].append(str(relative_path))
                    elif "admin" in str(relative_path):
                        code_structure["admin"].append(str(relative_path))
                    elif "crawler" in str(relative_path):
                        code_structure["crawler"].append(str(relative_path))
                    elif "notification" in str(relative_path):
                        code_structure["notification"].append(str(relative_path))
                    elif "telegram_bot" in str(relative_path):
                        code_structure["telegram_bot"].append(str(relative_path))

        # Count files in each category
        category_counts = {k: len(v) for k, v in code_structure.items()}

        print(f"📊 Code Structure Analysis:")
        for category, count in category_counts.items():
            print(f"   {category}: {count} files")

        return code_structure, category_counts

    def analyze_test_structure(self):
        """Analyze the test structure"""
        print("🧪 Analyzing test structure...")

        test_structure = {
            "api": [],
            "services": [],
            "unit": [],
            "integration": [],
            "performance": [],
            "database": [],
            "e2e": [],
            "security": [],
        }

        tests_root = self.backend_root / "tests"

        if tests_root.exists():
            for root, dirs, files in os.walk(tests_root):
                for file in files:
                    if file.endswith(".py") and file.startswith("test_"):
                        file_path = Path(root) / file
                        relative_path = file_path.relative_to(tests_root)

                        # Categorize test files
                        if "api" in str(relative_path):
                            test_structure["api"].append(str(relative_path))
                        elif "services" in str(relative_path):
                            test_structure["services"].append(str(relative_path))
                        elif "unit" in str(relative_path):
                            test_structure["unit"].append(str(relative_path))
                        elif "integration" in str(relative_path):
                            test_structure["integration"].append(str(relative_path))
                        elif "performance" in str(relative_path):
                            test_structure["performance"].append(str(relative_path))
                        elif "database" in str(relative_path):
                            test_structure["database"].append(str(relative_path))
                        elif "e2e" in str(relative_path):
                            test_structure["e2e"].append(str(relative_path))
                        elif "security" in file:
                            test_structure["security"].append(str(relative_path))

        # Count test files in each category
        test_counts = {k: len(v) for k, v in test_structure.items()}

        print(f"📊 Test Structure Analysis:")
        for category, count in test_counts.items():
            print(f"   {category}: {count} test files")

        return test_structure, test_counts

    def run_coverage_analysis(self):
        """Run coverage analysis using pytest-cov"""
        print("📈 Running coverage analysis...")

        try:
            # Run pytest with coverage
            cmd = [
                "python",
                "-m",
                "pytest",
                "tests/",
                "--cov=.",
                "--cov-report=json",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-fail-under=80",
            ]

            result = subprocess.run(
                cmd,
                cwd=self.backend_root,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes
            )

            # Parse coverage results
            coverage_file = self.backend_root / "htmlcov" / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, "r") as f:
                    coverage_data = json.load(f)

                self.coverage_data = coverage_data
                self.analyze_coverage_data()

                return True
            else:
                print("⚠️  Coverage file not found")
                return False

        except subprocess.TimeoutExpired:
            print("⏰ Coverage analysis timed out")
            return False
        except Exception as e:
            print(f"❌ Error running coverage analysis: {e}")
            return False

    def analyze_coverage_data(self):
        """Analyze coverage data and generate insights"""
        print("📊 Analyzing coverage data...")

        if not self.coverage_data:
            return

        # Extract file coverage
        files = self.coverage_data.get("files", {})

        for file_path, file_data in files.items():
            # Calculate file coverage
            lines = file_data.get("executed_lines", [])
            missing = file_data.get("missing_lines", [])
            total_lines = len(lines) + len(missing)

            if total_lines > 0:
                coverage_percentage = (len(lines) / total_lines) * 100
            else:
                coverage_percentage = 0

            self.file_coverage[file_path] = {
                "coverage": coverage_percentage,
                "lines_covered": len(lines),
                "lines_missing": len(missing),
                "total_lines": total_lines,
            }

        # Categorize coverage by module
        self.categorize_coverage()

        # Generate coverage insights
        self.generate_coverage_insights()

    def categorize_coverage(self):
        """Categorize coverage by module type"""
        print("🏷️  Categorizing coverage by module...")

        categories = {
            "api": [],
            "services": [],
            "models": [],
            "utils": [],
            "database": [],
            "middleware": [],
            "admin": [],
            "crawler": [],
            "notification": [],
            "telegram_bot": [],
            "other": [],
        }

        for file_path, coverage_data in self.file_coverage.items():
            if "api" in file_path:
                categories["api"].append(coverage_data)
            elif "services" in file_path:
                categories["services"].append(coverage_data)
            elif "models" in file_path:
                categories["models"].append(coverage_data)
            elif "utils" in file_path:
                categories["utils"].append(coverage_data)
            elif "database" in file_path:
                categories["database"].append(coverage_data)
            elif "middleware" in file_path:
                categories["middleware"].append(coverage_data)
            elif "admin" in file_path:
                categories["admin"].append(coverage_data)
            elif "crawler" in file_path:
                categories["crawler"].append(coverage_data)
            elif "notification" in file_path:
                categories["notification"].append(coverage_data)
            elif "telegram_bot" in file_path:
                categories["telegram_bot"].append(coverage_data)
            else:
                categories["other"].append(coverage_data)

        # Calculate category averages
        self.module_coverage = {}
        for category, files in categories.items():
            if files:
                avg_coverage = sum(f["coverage"] for f in files) / len(files)
                total_files = len(files)
                total_lines = sum(f["total_lines"] for f in files)
                covered_lines = sum(f["lines_covered"] for f in files)

                self.module_coverage[category] = {
                    "average_coverage": avg_coverage,
                    "total_files": total_files,
                    "total_lines": total_lines,
                    "covered_lines": covered_lines,
                    "files": files,
                }

    def generate_coverage_insights(self):
        """Generate insights from coverage data"""
        print("💡 Generating coverage insights...")

        insights = {
            "overall_coverage": 0,
            "category_insights": {},
            "low_coverage_files": [],
            "uncovered_files": [],
            "recommendations": [],
        }

        # Calculate overall coverage
        total_lines = sum(f["total_lines"] for f in self.file_coverage.values())
        total_covered = sum(f["lines_covered"] for f in self.file_coverage.values())

        if total_lines > 0:
            insights["overall_coverage"] = (total_covered / total_lines) * 100

        # Analyze each category
        for category, data in self.module_coverage.items():
            threshold = self.thresholds.get(category, 80.0)
            coverage = data["average_coverage"]

            insights["category_insights"][category] = {
                "coverage": coverage,
                "threshold": threshold,
                "status": "PASS" if coverage >= threshold else "FAIL",
                "files_analyzed": data["total_files"],
                "total_lines": data["total_lines"],
                "covered_lines": data["covered_lines"],
            }

        # Find low coverage files
        for file_path, coverage_data in self.file_coverage.items():
            if coverage_data["coverage"] < 50:
                insights["low_coverage_files"].append(
                    {
                        "file": file_path,
                        "coverage": coverage_data["coverage"],
                        "missing_lines": coverage_data["lines_missing"],
                    }
                )

        # Generate recommendations
        insights["recommendations"] = self.generate_recommendations(insights)

        self.coverage_insights = insights

    def generate_recommendations(self, insights):
        """Generate actionable recommendations"""
        recommendations = []

        # Overall coverage recommendations
        overall_coverage = insights["overall_coverage"]
        if overall_coverage < 80:
            recommendations.append(
                {
                    "type": "critical",
                    "message": f"Overall coverage is {overall_coverage:.1f}%, target is 80%",
                    "action": "Add more comprehensive tests",
                }
            )

        # Category-specific recommendations
        for category, data in insights["category_insights"].items():
            if data["status"] == "FAIL":
                recommendations.append(
                    {
                        "type": "important",
                        "message": f'{category.upper()} coverage is {data["coverage"]:.1f}%, target is {data["threshold"]}%',
                        "action": f"Focus on {category} module tests",
                    }
                )

        # Low coverage file recommendations
        if insights["low_coverage_files"]:
            recommendations.append(
                {
                    "type": "important",
                    "message": f'{len(insights["low_coverage_files"])} files have <50% coverage',
                    "action": "Prioritize testing these files",
                }
            )

        return recommendations

    def generate_coverage_report(self):
        """Generate comprehensive coverage report"""
        print("📋 Generating coverage report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "project": "Buzz2Remote Backend",
            "overall_coverage": self.coverage_insights["overall_coverage"],
            "categories": self.module_coverage,
            "insights": self.coverage_insights,
            "file_coverage": self.file_coverage,
            "summary": {
                "total_files": len(self.file_coverage),
                "total_lines": sum(
                    f["total_lines"] for f in self.file_coverage.values()
                ),
                "covered_lines": sum(
                    f["lines_covered"] for f in self.file_coverage.values()
                ),
                "categories_analyzed": len(self.module_coverage),
            },
        }

        # Save detailed report
        report_file = (
            self.backend_root
            / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Generate summary report
        self.print_coverage_summary(report)

        return report, report_file

    def print_coverage_summary(self, report):
        """Print coverage summary to console"""
        print(f"\n{'='*80}")
        print("📊 COVERAGE ANALYSIS SUMMARY")
        print(f"{'='*80}")

        print(f"🎯 Overall Coverage: {report['overall_coverage']:.1f}%")
        print(f"📁 Files Analyzed: {report['summary']['total_files']}")
        print(f"📝 Total Lines: {report['summary']['total_lines']}")
        print(f"✅ Covered Lines: {report['summary']['covered_lines']}")

        print(f"\n📊 Category Breakdown:")
        for category, data in report["categories"].items():
            status_icon = (
                "✅"
                if data["average_coverage"] >= self.thresholds.get(category, 80)
                else "❌"
            )
            print(
                f"   {status_icon} {category.upper()}: {data['average_coverage']:.1f}% ({data['total_files']} files)"
            )

        print(f"\n💡 Key Insights:")
        for insight in report["insights"]["recommendations"][
            :5
        ]:  # Top 5 recommendations
            icon = "🚨" if insight["type"] == "critical" else "⚠️"
            print(f"   {icon} {insight['message']}")

        print(f"\n📄 Detailed report saved to: {report_file}")
        print(f"{'='*80}")

    def run_full_analysis(self):
        """Run complete coverage analysis"""
        print("🚀 Starting comprehensive coverage analysis...")

        # Step 1: Analyze code structure
        code_structure, code_counts = self.analyze_code_structure()

        # Step 2: Analyze test structure
        test_structure, test_counts = self.analyze_test_structure()

        # Step 3: Run coverage analysis
        coverage_success = self.run_coverage_analysis()

        if coverage_success:
            # Step 4: Generate report
            report, report_file = self.generate_coverage_report()

            return {
                "success": True,
                "code_structure": code_structure,
                "test_structure": test_structure,
                "code_counts": code_counts,
                "test_counts": test_counts,
                "coverage_report": report,
                "report_file": str(report_file),
            }
        else:
            return {
                "success": False,
                "code_structure": code_structure,
                "test_structure": test_structure,
                "code_counts": code_counts,
                "test_counts": test_counts,
            }


def main():
    """Main entry point"""
    analyzer = CoverageAnalyzer()

    try:
        results = analyzer.run_full_analysis()

        if results["success"]:
            print(f"\n🎉 Coverage analysis completed successfully!")
            print(f"📄 Report saved to: {results['report_file']}")
        else:
            print(f"\n⚠️  Coverage analysis completed with issues")
            print("   Check the output above for details")

        return results

    except KeyboardInterrupt:
        print("\n🛑 Coverage analysis interrupted by user")
        return {"success": False, "error": "Interrupted"}
    except Exception as e:
        print(f"\n💥 Unexpected error during coverage analysis: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    main()
