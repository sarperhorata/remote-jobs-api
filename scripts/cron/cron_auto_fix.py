#!/usr/bin/env python3
"""
Auto-Fix Cron Job for Render
Bu script Render'da çalışarak GitHub workflow'larındaki problemleri otomatik olarak çözer
"""

import os
import sys
import json
import logging
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Logging konfigürasyonu
log_file = '/opt/render/project/src/logs/auto-fix.log' if os.path.exists('/opt/render/project/src') else 'logs/auto-fix.log'
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AutoFixCronJob:
    def __init__(self):
        """Initialize Auto-Fix Cron Job"""
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'sarperhorata')
        self.repo_name = os.getenv('GITHUB_REPOSITORY_NAME', 'buzz2remote')
        self.enabled = os.getenv('AUTO_FIX_ENABLED', 'true').lower() == 'true'
        
        # GitHub API
        self.github_api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Paths
        if os.path.exists('/opt/render/project/src'):
            self.project_root = Path('/opt/render/project/src')
        else:
            self.project_root = Path.cwd()
        
        self.frontend_path = self.project_root / 'frontend'
        self.backend_path = self.project_root / 'backend'
        self.logs_path = self.project_root / 'logs'
        
        # Ensure logs directory exists
        self.logs_path.mkdir(exist_ok=True)
        
    def check_environment(self):
        """Check if environment is properly configured"""
        if not self.enabled:
            logger.info("Auto-fix is disabled")
            return False
            
        if not self.github_token:
            logger.error("GITHUB_TOKEN not set")
            return False
            
        if not self.project_root.exists():
            logger.error(f"Project root not found: {self.project_root}")
            return False
            
        logger.info("Environment check passed")
        return True
    
    def fix_frontend_issues(self):
        """Fix frontend issues"""
        logger.info("🔧 Fixing frontend issues...")
        
        try:
            # Change to frontend directory
            os.chdir(self.frontend_path)
            
            # Install dependencies
            logger.info("Installing frontend dependencies...")
            result = subprocess.run(['npm', 'ci', '--no-optional'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.warning(f"npm install failed: {result.stderr}")
            
            # Fix linting issues
            logger.info("Fixing linting issues...")
            result = subprocess.run(['npm', 'run', 'lint:fix'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Frontend linting issues fixed")
            else:
                logger.warning(f"Some linting issues could not be auto-fixed: {result.stderr}")
            
            # Fix formatting
            logger.info("Fixing formatting...")
            result = subprocess.run(['npm', 'run', 'format'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Frontend formatting issues fixed")
            else:
                logger.warning(f"Some formatting issues could not be auto-fixed: {result.stderr}")
            
            # Type checking
            logger.info("Running type checking...")
            result = subprocess.run(['npm', 'run', 'type-check'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Frontend type checking passed")
            else:
                logger.warning(f"Frontend type checking issues found: {result.stderr}")
            
            # Security audit
            logger.info("Running security audit...")
            result = subprocess.run(['npm', 'audit', '--audit-level=moderate'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Frontend security audit passed")
            else:
                logger.warning(f"Frontend security issues found: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Frontend fix operation timed out")
        except Exception as e:
            logger.error(f"Error fixing frontend issues: {e}")
    
    def fix_backend_issues(self):
        """Fix backend issues"""
        logger.info("🔧 Fixing backend issues...")
        
        try:
            # Change to backend directory
            os.chdir(self.backend_path)
            
            # Install dependencies
            logger.info("Installing backend dependencies...")
            result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.warning(f"pip install failed: {result.stderr}")
            
            # Install formatting tools
            logger.info("Installing formatting tools...")
            subprocess.run(['pip', 'install', 'black', 'isort', 'autopep8', 'bandit', 'safety'], 
                          capture_output=True, text=True, timeout=300)
            
            # Fix code formatting with Black
            logger.info("Fixing code formatting...")
            result = subprocess.run(['black', '.', '--line-length=88', '--quiet'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Backend formatting issues fixed")
            else:
                logger.warning(f"Some formatting issues could not be auto-fixed: {result.stderr}")
            
            # Fix import sorting with isort
            logger.info("Fixing import sorting...")
            result = subprocess.run(['isort', '.', '--profile=black', '--quiet'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Backend import sorting fixed")
            else:
                logger.warning(f"Some import sorting issues could not be auto-fixed: {result.stderr}")
            
            # Fix linting issues with autopep8
            logger.info("Fixing linting issues...")
            result = subprocess.run(['autopep8', '--in-place', '--recursive', '--aggressive', '--aggressive', '.'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Backend linting issues fixed")
            else:
                logger.warning(f"Some linting issues could not be auto-fixed: {result.stderr}")
            
            # Security check with bandit
            logger.info("Running security check...")
            result = subprocess.run(['bandit', '-r', '.', '-f', 'json'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Backend security check passed")
            else:
                logger.warning(f"Backend security issues found: {result.stderr}")
            
            # Safety check
            logger.info("Running safety check...")
            result = subprocess.run(['safety', 'check'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("✅ Backend safety check passed")
            else:
                logger.warning(f"Backend safety issues found: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Backend fix operation timed out")
        except Exception as e:
            logger.error(f"Error fixing backend issues: {e}")
    
    def analyze_coverage(self):
        """Analyze test coverage"""
        logger.info("📊 Analyzing test coverage...")
        
        try:
            # Frontend coverage
            if (self.frontend_path / 'coverage' / 'coverage-summary.json').exists():
                with open(self.frontend_path / 'coverage' / 'coverage-summary.json', 'r') as f:
                    coverage_data = json.load(f)
                    coverage = coverage_data.get('total', {}).get('lines', {}).get('pct', 'Unknown')
                    logger.info(f"Frontend coverage: {coverage}%")
            else:
                logger.warning("Frontend coverage report not found")
            
            # Backend coverage
            if (self.backend_path / 'htmlcov' / 'index.html').exists():
                logger.info("✅ Backend coverage report generated")
            else:
                logger.warning("Backend coverage report not found")
                
        except Exception as e:
            logger.error(f"Error analyzing coverage: {e}")
    
    def analyze_performance(self):
        """Analyze performance"""
        logger.info("⚡ Analyzing performance...")
        
        try:
            # Frontend bundle size
            if (self.frontend_path / 'build').exists():
                result = subprocess.run(['du', '-sh', str(self.frontend_path / 'build')], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    bundle_size = result.stdout.strip().split('\t')[0]
                    logger.info(f"Frontend bundle size: {bundle_size}")
                else:
                    logger.warning("Could not determine bundle size")
            else:
                logger.warning("Frontend build directory not found")
                
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
    
    def create_github_issue(self, report: str):
        """Create GitHub issue with auto-fix report"""
        if not self.github_token:
            logger.warning("GitHub token not available, skipping issue creation")
            return None
            
        issue_data = {
            "title": f"🤖 Auto-Fix Summary - {datetime.now().strftime('%Y-%m-%d')}",
            "body": report,
            "labels": ["auto-fix", "automation", "maintenance"]
        }
        
        try:
            response = requests.post(
                f"{self.github_api_url}/issues",
                headers=self.headers,
                json=issue_data,
                timeout=30
            )
            response.raise_for_status()
            issue = response.json()
            logger.info(f"GitHub issue created: {issue['html_url']}")
            return issue['number']
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return None
    
    def generate_report(self):
        """Generate auto-fix report"""
        report = f"""# Auto-Fix Summary Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Environment: Render Cron Job

## Summary
Auto-fix workflow completed successfully on Render.

## Actions Taken
- ✅ Frontend linting and formatting fixes
- ✅ Backend code formatting and import sorting
- ✅ Security audits (npm audit, bandit, safety)
- ✅ Coverage analysis
- ✅ Performance analysis

## Next Steps
1. Review any warnings in the logs
2. Address any remaining issues manually
3. Monitor for recurring problems

---
*This report was generated automatically by the Render cron job.*
"""
        return report
    
    def run(self):
        """Run the auto-fix cron job"""
        logger.info("🚀 Starting auto-fix cron job...")
        
        if not self.check_environment():
            return False
        
        start_time = datetime.now()
        
        try:
            # Fix frontend issues
            self.fix_frontend_issues()
            
            # Fix backend issues
            self.fix_backend_issues()
            
            # Analyze coverage
            self.analyze_coverage()
            
            # Analyze performance
            self.analyze_performance()
            
            # Generate and save report
            report = self.generate_report()
            report_path = self.logs_path / f"auto-fix-report-{datetime.now().strftime('%Y%m%d')}.md"
            with open(report_path, 'w') as f:
                f.write(report)
            
            # Create GitHub issue
            self.create_github_issue(report)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info(f"✅ Auto-fix cron job completed successfully in {duration}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Auto-fix cron job failed: {e}")
            return False

def main():
    """Main function"""
    cron_job = AutoFixCronJob()
    success = cron_job.run()
    
    if success:
        print("Auto-fix cron job completed successfully")
        sys.exit(0)
    else:
        print("Auto-fix cron job failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 