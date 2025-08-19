#!/usr/bin/env python3
"""
Security Monitor Script
Production'da dependency güvenlik durumunu kontrol eder ve raporlar
"""

import os
import sys
import json
import logging
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/security-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecurityMonitor:
    def __init__(self):
        """Initialize Security Monitor"""
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO', 'sarperhorata/buzz2remote')
        
        if not self.github_token:
            logger.error("GITHUB_TOKEN environment variable not set")
            sys.exit(1)
            
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Security-Monitor/1.0'
        }
        
        self.base_url = f"https://api.github.com/repos/{self.github_repo}"
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
    def check_frontend_security(self) -> Dict[str, Any]:
        """Check frontend dependencies for security issues"""
        try:
            logger.info("🔍 Checking frontend security...")
            
            # Change to frontend directory
            os.chdir('frontend')
            
            # Run npm audit
            result = subprocess.run(
                ['npm', 'audit', '--audit-level=moderate', '--json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse npm audit output
            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get('vulnerabilities', {})
                
                critical = len([v for v in vulnerabilities.values() if v.get('severity') == 'critical'])
                high = len([v for v in vulnerabilities.values() if v.get('severity') == 'high'])
                moderate = len([v for v in vulnerabilities.values() if v.get('severity') == 'moderate'])
                low = len([v for v in vulnerabilities.values() if v.get('severity') == 'low'])
                
                return {
                    'status': 'success',
                    'critical': critical,
                    'high': high,
                    'moderate': moderate,
                    'low': low,
                    'total': critical + high + moderate + low,
                    'details': vulnerabilities
                }
            else:
                return {
                    'status': 'error',
                    'error': result.stderr,
                    'critical': 0,
                    'high': 0,
                    'moderate': 0,
                    'low': 0,
                    'total': 0
                }
                
        except Exception as e:
            logger.error(f"Error checking frontend security: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'critical': 0,
                'high': 0,
                'moderate': 0,
                'low': 0,
                'total': 0
            }
        finally:
            # Return to root directory
            os.chdir('..')
    
    def check_backend_security(self) -> Dict[str, Any]:
        """Check backend dependencies for security issues"""
        try:
            logger.info("🔍 Checking backend security...")
            
            # Change to backend directory
            os.chdir('backend')
            
            # Install safety if not available
            try:
                subprocess.run(['safety', '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.info("Installing safety...")
                subprocess.run(['pip', 'install', 'safety'], check=True)
            
            # Run safety check
            result = subprocess.run(
                ['safety', 'check', '--output', 'json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                safety_data = json.loads(result.stdout)
                vulnerabilities = safety_data.get('vulnerabilities', [])
                
                critical = len([v for v in vulnerabilities if v.get('severity') == 'critical'])
                high = len([v for v in vulnerabilities if v.get('severity') == 'high'])
                moderate = len([v for v in vulnerabilities if v.get('severity') == 'medium'])
                low = len([v for v in vulnerabilities if v.get('severity') == 'low'])
                
                return {
                    'status': 'success',
                    'critical': critical,
                    'high': high,
                    'moderate': moderate,
                    'low': low,
                    'total': critical + high + moderate + low,
                    'details': vulnerabilities
                }
            else:
                return {
                    'status': 'error',
                    'error': result.stderr,
                    'critical': 0,
                    'high': 0,
                    'moderate': 0,
                    'low': 0,
                    'total': 0
                }
                
        except Exception as e:
            logger.error(f"Error checking backend security: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'critical': 0,
                'high': 0,
                'moderate': 0,
                'low': 0,
                'total': 0
            }
        finally:
            # Return to root directory
            os.chdir('..')
    
    def check_outdated_dependencies(self) -> Dict[str, Any]:
        """Check for outdated dependencies"""
        try:
            logger.info("🔍 Checking outdated dependencies...")
            
            outdated_info = {
                'frontend': {},
                'backend': {}
            }
            
            # Check frontend outdated packages
            try:
                os.chdir('frontend')
                result = subprocess.run(
                    ['npm', 'outdated', '--json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    outdated_info['frontend'] = json.loads(result.stdout)
                else:
                    outdated_info['frontend'] = {}
                    
            except Exception as e:
                logger.error(f"Error checking frontend outdated: {e}")
                outdated_info['frontend'] = {}
            finally:
                os.chdir('..')
            
            # Check backend outdated packages
            try:
                os.chdir('backend')
                result = subprocess.run(
                    ['pip', 'list', '--outdated', '--format=json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    outdated_info['backend'] = json.loads(result.stdout)
                else:
                    outdated_info['backend'] = []
                    
            except Exception as e:
                logger.error(f"Error checking backend outdated: {e}")
                outdated_info['backend'] = []
            finally:
                os.chdir('..')
            
            return outdated_info
            
        except Exception as e:
            logger.error(f"Error checking outdated dependencies: {e}")
            return {'frontend': {}, 'backend': []}
    
    def create_security_issue(self, security_report: Dict[str, Any]) -> bool:
        """Create GitHub issue for security vulnerabilities"""
        try:
            # Check if there are critical or high vulnerabilities
            frontend_critical = security_report['frontend'].get('critical', 0)
            frontend_high = security_report['frontend'].get('high', 0)
            backend_critical = security_report['backend'].get('critical', 0)
            backend_high = security_report['backend'].get('high', 0)
            
            total_critical = frontend_critical + backend_critical
            total_high = frontend_high + backend_high
            
            if total_critical == 0 and total_high == 0:
                logger.info("No critical or high vulnerabilities found, skipping issue creation")
                return False
            
            # Create issue title and body
            title = f"🚨 Security Alert: {total_critical} Critical, {total_high} High Vulnerabilities Detected"
            
            body = f"""## 🚨 Security Vulnerability Alert

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📊 Summary
- **Critical Vulnerabilities:** {total_critical}
- **High Vulnerabilities:** {total_high}
- **Frontend Critical:** {frontend_critical}
- **Frontend High:** {frontend_high}
- **Backend Critical:** {backend_critical}
- **Backend High:** {backend_high}

### 🔍 Details

#### Frontend Vulnerabilities
- Critical: {frontend_critical}
- High: {frontend_high}
- Moderate: {security_report['frontend'].get('moderate', 0)}
- Low: {security_report['frontend'].get('low', 0)}

#### Backend Vulnerabilities
- Critical: {backend_critical}
- High: {backend_high}
- Moderate: {security_report['backend'].get('moderate', 0)}
- Low: {security_report['backend'].get('low', 0)}

### 🛠️ Recommended Actions
1. Review the detailed security report
2. Update vulnerable dependencies
3. Test thoroughly after updates
4. Deploy security patches

### 📋 Checklist
- [ ] Review vulnerability details
- [ ] Update critical dependencies
- [ ] Update high-risk dependencies
- [ ] Test application functionality
- [ ] Deploy security updates
- [ ] Monitor for new vulnerabilities

**This issue was automatically generated by the Security Monitor.**
"""
            
            # Create GitHub issue
            url = f"{self.base_url}/issues"
            data = {
                'title': title,
                'body': body,
                'labels': ['security', 'vulnerability', 'automated', 'urgent']
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                issue_data = response.json()
                logger.info(f"✅ Security issue created: #{issue_data['number']}")
                return True
            else:
                logger.error(f"❌ Failed to create security issue: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating security issue: {e}")
            return False
    
    def generate_report(self, security_report: Dict[str, Any], outdated_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'security': security_report,
            'outdated': outdated_info,
            'summary': {
                'total_critical': security_report['frontend'].get('critical', 0) + security_report['backend'].get('critical', 0),
                'total_high': security_report['frontend'].get('high', 0) + security_report['backend'].get('high', 0),
                'total_moderate': security_report['frontend'].get('moderate', 0) + security_report['backend'].get('moderate', 0),
                'total_low': security_report['frontend'].get('low', 0) + security_report['backend'].get('low', 0),
                'frontend_outdated': len(outdated_info.get('frontend', {})),
                'backend_outdated': len(outdated_info.get('backend', []))
            }
        }
        
        # Save report
        report_file = f"logs/security-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {report_file}")
        return report
    
    def run(self):
        """Main security monitoring process"""
        logger.info("🚀 Starting Security Monitor...")
        
        try:
            # Check frontend security
            frontend_security = self.check_frontend_security()
            
            # Check backend security
            backend_security = self.check_backend_security()
            
            # Check outdated dependencies
            outdated_info = self.check_outdated_dependencies()
            
            # Combine security report
            security_report = {
                'frontend': frontend_security,
                'backend': backend_security
            }
            
            # Generate comprehensive report
            report = self.generate_report(security_report, outdated_info)
            
            # Create GitHub issue if critical/high vulnerabilities found
            issue_created = self.create_security_issue(security_report)
            
            # Log summary
            summary = report['summary']
            logger.info(f"✅ Security Monitor completed!")
            logger.info(f"📊 Summary:")
            logger.info(f"  - Critical: {summary['total_critical']}")
            logger.info(f"  - High: {summary['total_high']}")
            logger.info(f"  - Moderate: {summary['total_moderate']}")
            logger.info(f"  - Low: {summary['total_low']}")
            logger.info(f"  - Frontend Outdated: {summary['frontend_outdated']}")
            logger.info(f"  - Backend Outdated: {summary['backend_outdated']}")
            
            if issue_created:
                logger.info("🚨 Security issue created for critical/high vulnerabilities")
            
        except Exception as e:
            logger.error(f"❌ Security Monitor failed: {e}")
            sys.exit(1)

def main():
    """Main function"""
    monitor = SecurityMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 