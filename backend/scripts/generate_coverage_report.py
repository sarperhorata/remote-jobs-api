#!/usr/bin/env python3
"""
Test Coverage Report Generator
Generates comprehensive test coverage reports for the backend
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_tests_with_coverage():
    """Run tests with coverage and generate reports."""
    try:
        # Set test environment variables
        env = os.environ.copy()
        env.update({
            'ENVIRONMENT': 'test',
            'TESTING': 'true',
            'PYTEST_CURRENT_TEST': 'true',
            'DISABLE_EXTERNAL_APIS': 'true'
        })
        
        # Run pytest with coverage
        cmd = [
            'python', '-m', 'pytest', 'tests/',
            '--cov=.',
            '--cov-report=xml',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-fail-under=70',
            '--timeout=30',
            '--maxfail=10',
            '-v'
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Tests failed!")
            print(result.stdout)
            print(result.stderr)
            return False
        
        print("✅ Tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def generate_coverage_summary():
    """Generate a summary of test coverage."""
    coverage_file = Path('coverage.xml')
    
    if not coverage_file.exists():
        print("❌ Coverage file not found")
        return None
    
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Extract coverage data
        coverage_data = {}
        for package in root.findall('.//package'):
            package_name = package.get('name', 'unknown')
            line_rate = float(package.get('line-rate', 0))
            branch_rate = float(package.get('branch-rate', 0))
            
            coverage_data[package_name] = {
                'line_rate': line_rate * 100,
                'branch_rate': branch_rate * 100,
                'lines_covered': int(package.get('lines-covered', 0)),
                'lines_valid': int(package.get('lines-valid', 0))
            }
        
        return coverage_data
        
    except Exception as e:
        print(f"❌ Error parsing coverage file: {e}")
        return None

def create_coverage_report(coverage_data):
    """Create a detailed coverage report."""
    if not coverage_data:
        return
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_packages': len(coverage_data),
            'average_line_coverage': sum(data['line_rate'] for data in coverage_data.values()) / len(coverage_data),
            'average_branch_coverage': sum(data['branch_rate'] for data in coverage_data.values()) / len(coverage_data)
        },
        'packages': coverage_data
    }
    
    # Save detailed report
    with open('coverage_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n📊 COVERAGE SUMMARY")
    print("=" * 50)
    print(f"Total Packages: {report['summary']['total_packages']}")
    print(f"Average Line Coverage: {report['summary']['average_line_coverage']:.2f}%")
    print(f"Average Branch Coverage: {report['summary']['average_branch_coverage']:.2f}%")
    
    print("\n📁 PACKAGE DETAILS")
    print("-" * 50)
    for package, data in sorted(coverage_data.items()):
        print(f"{package:30} | {data['line_rate']:6.2f}% | {data['lines_covered']:4d}/{data['lines_valid']:4d}")

def generate_test_statistics():
    """Generate test statistics."""
    try:
        # Count test files and test cases
        test_files = list(Path('tests').rglob('test_*.py'))
        test_cases = 0
        
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                # Count test functions
                test_cases += content.count('def test_')
        
        stats = {
            'test_files': len(test_files),
            'test_cases': test_cases,
            'categories': {
                'api': len(list(Path('tests/api').rglob('test_*.py'))),
                'services': len(list(Path('tests/services').rglob('test_*.py'))),
                'unit': len(list(Path('tests/unit').rglob('test_*.py'))),
                'integration': len([f for f in test_files if 'api' not in str(f) and 'services' not in str(f) and 'unit' not in str(f)])
            }
        }
        
        print("\n🧪 TEST STATISTICS")
        print("=" * 50)
        print(f"Total Test Files: {stats['test_files']}")
        print(f"Total Test Cases: {stats['test_cases']}")
        print(f"API Tests: {stats['categories']['api']} files")
        print(f"Services Tests: {stats['categories']['services']} files")
        print(f"Unit Tests: {stats['categories']['unit']} files")
        print(f"Integration Tests: {stats['categories']['integration']} files")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error generating test statistics: {e}")
        return None

def main():
    """Main function to generate coverage report."""
    print("🚀 Starting Test Coverage Report Generation")
    print("=" * 60)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    # Run tests with coverage
    if not run_tests_with_coverage():
        sys.exit(1)
    
    # Generate coverage summary
    coverage_data = generate_coverage_summary()
    
    # Create detailed report
    create_coverage_report(coverage_data)
    
    # Generate test statistics
    test_stats = generate_test_statistics()
    
    print("\n✅ Coverage report generation completed!")
    print("📁 Generated files:")
    print("  - coverage.xml (XML coverage data)")
    print("  - htmlcov/ (HTML coverage report)")
    print("  - coverage_report.json (Detailed JSON report)")

if __name__ == "__main__":
    main()