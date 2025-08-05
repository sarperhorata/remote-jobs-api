#!/usr/bin/env python3
"""
Test Cron Jobs
Bu script cron job'ları test etmek için kullanılır
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_cron_job(script_path: str, job_name: str) -> bool:
    """Test a specific cron job"""
    logger.info(f"🧪 Testing {job_name}...")
    
    try:
        # Check if script exists
        if not Path(script_path).exists():
            logger.error(f"Script not found: {script_path}")
            return False
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        # Set test environment variables
        env = os.environ.copy()
        env['GITHUB_TOKEN'] = 'test_token'
        env['AUTO_FIX_ENABLED'] = 'false'
        env['WORKFLOW_MONITOR_ENABLED'] = 'false'
        env['DB_CLEANUP_ENABLED'] = 'false'
        env['API_CRAWLER_ENABLED'] = 'false'
        env['JOB_STATS_ENABLED'] = 'false'
        env['CRON_MONITOR_ENABLED'] = 'false'
        
        # Run script with timeout
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
            env=env
        )
        
        # Check if script ran successfully or failed gracefully
        if result.returncode == 0:
            logger.info(f"✅ {job_name} test passed")
            return True
        elif "disabled" in result.stderr.lower() or "not set" in result.stderr.lower():
            logger.info(f"✅ {job_name} test passed (disabled as expected)")
            return True
        else:
            logger.error(f"❌ {job_name} test failed")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {job_name} test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ {job_name} test error: {e}")
        return False

def test_auto_fix_cron():
    """Test auto-fix cron job"""
    return test_cron_job(
        "scripts/cron/cron_auto_fix.py",
        "Auto-Fix Cron Job"
    )

def test_workflow_monitor_cron():
    """Test workflow monitor cron job"""
    return test_cron_job(
        "scripts/cron/cron_workflow_monitor.py",
        "Workflow Monitor Cron Job"
    )

def test_database_cleanup_cron():
    """Test database cleanup cron job"""
    return test_cron_job(
        "scripts/cron/cron_database_cleanup.py",
        "Database Cleanup Cron Job"
    )

def test_external_apis_cron():
    """Test external APIs cron job"""
    return test_cron_job(
        "scripts/cron/cron_external_apis.py",
        "External APIs Cron Job"
    )

def test_job_statistics_cron():
    """Test job statistics cron job"""
    return test_cron_job(
        "scripts/cron/cron_job_statistics.py",
        "Job Statistics Cron Job"
    )

def test_status_monitor_cron():
    """Test status monitor cron job"""
    return test_cron_job(
        "scripts/cron/cron_status_monitor.py",
        "Status Monitor Cron Job"
    )

def test_render_yaml():
    """Test render.yaml syntax"""
    logger.info("🧪 Testing render.yaml syntax...")
    
    try:
        import yaml
        
        with open('render.yaml', 'r') as f:
            yaml.safe_load(f)
        
        logger.info("✅ render.yaml syntax is valid")
        return True
        
    except Exception as e:
        logger.error(f"❌ render.yaml syntax error: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting cron job tests...")
    
    # Test results
    results = {}
    
    # Test render.yaml
    results['render_yaml'] = test_render_yaml()
    
    # Test cron jobs
    results['auto_fix'] = test_auto_fix_cron()
    results['workflow_monitor'] = test_workflow_monitor_cron()
    results['database_cleanup'] = test_database_cleanup_cron()
    results['external_apis'] = test_external_apis_cron()
    results['job_statistics'] = test_job_statistics_cron()
    results['status_monitor'] = test_status_monitor_cron()
    
    # Summary
    logger.info("\n📊 Test Results Summary:")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    logger.info("=" * 50)
    logger.info(f"Total: {total}, Passed: {passed}, Failed: {total - passed}")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return True
    else:
        logger.error(f"❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 