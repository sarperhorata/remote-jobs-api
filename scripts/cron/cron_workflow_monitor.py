#!/usr/bin/env python3
"""
Workflow Monitor Cron Job for Render
Bu script Render'da çalışarak GitHub workflow'larını izler ve problemleri raporlar
"""

import os
import sys
import json
import logging
import requests
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Logging konfigürasyonu
log_file = '/opt/render/project/src/logs/workflow-monitor.log' if os.path.exists('/opt/render/project/src') else 'logs/workflow-monitor.log'
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class WorkflowMonitorCronJob:
    def __init__(self):
        """Initialize Workflow Monitor Cron Job"""
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'sarperhorata')
        self.repo_name = os.getenv('GITHUB_REPOSITORY_NAME', 'buzz2remote')
        self.enabled = os.getenv('WORKFLOW_MONITOR_ENABLED', 'true').lower() == 'true'
        
        # GitHub API
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Email configuration
        self.email_config = {
            'from': os.getenv('EMAIL_FROM'),
            'to': os.getenv('EMAIL_TO'),
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD')
        }
        
        # Paths
        if os.path.exists('/opt/render/project/src'):
            self.project_root = Path('/opt/render/project/src')
        else:
            self.project_root = Path.cwd()
        
        self.logs_path = self.project_root / 'logs'
        
        # Ensure logs directory exists
        self.logs_path.mkdir(exist_ok=True)
        
    def check_environment(self):
        """Check if environment is properly configured"""
        if not self.enabled:
            logger.info("Workflow monitoring is disabled")
            return False
            
        if not self.github_token:
            logger.error("GITHUB_TOKEN not set")
            return False
            
        if not self.project_root.exists():
            logger.error(f"Project root not found: {self.project_root}")
            return False
            
        logger.info("Environment check passed")
        return True
    
    def get_workflow_runs(self, workflow_id: Optional[str] = None, days: int = 7) -> List[Dict]:
        """Get workflow runs from the last N days"""
        since_date = datetime.now() - timedelta(days=days)
        since_str = since_date.isoformat()
        
        url = f"{self.base_url}/actions/runs"
        params = {
            "created": f">={since_str}",
            "per_page": 100
        }
        
        if workflow_id:
            url = f"{self.base_url}/actions/workflows/{workflow_id}/runs"
            
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get("workflow_runs", [])
        except requests.RequestException as e:
            logger.error(f"Error fetching workflow runs: {e}")
            return []
    
    def get_workflow_run_details(self, run_id: int) -> Optional[Dict]:
        """Get details of a specific workflow run"""
        url = f"{self.base_url}/actions/runs/{run_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching workflow run {run_id}: {e}")
            return None
    
    def get_job_logs(self, run_id: int, job_id: int) -> Optional[str]:
        """Get logs for a specific job"""
        url = f"{self.base_url}/actions/runs/{run_id}/jobs/{job_id}/logs"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching job logs for {job_id}: {e}")
            return None
    
    def analyze_workflow_problems(self, runs: List[Dict]) -> Dict:
        """Analyze workflow problems"""
        problems = {
            "failed_runs": [],
            "slow_runs": [],
            "recurring_issues": {},
            "coverage_drops": [],
            "security_issues": [],
            "dependency_issues": []
        }
        
        for run in runs:
            run_id = run["id"]
            run_name = run["name"]
            status = run["conclusion"]
            duration = run.get("duration", 0)
            
            # Check for failed runs
            if status == "failure":
                problems["failed_runs"].append({
                    "id": run_id,
                    "name": run_name,
                    "status": status,
                    "duration": duration,
                    "created_at": run.get("created_at")
                })
            
            # Check for slow runs (more than 30 minutes)
            if duration and duration > 1800:  # 30 minutes in seconds
                problems["slow_runs"].append({
                    "id": run_id,
                    "name": run_name,
                    "duration": duration,
                    "created_at": run.get("created_at")
                })
            
            # Check for recurring issues
            if status == "failure":
                if run_name not in problems["recurring_issues"]:
                    problems["recurring_issues"][run_name] = 0
                problems["recurring_issues"][run_name] += 1
        
        return problems
    
    def analyze_logs_for_issues(self, logs: str, problems: Dict):
        """Analyze logs for specific issues"""
        if not logs:
            return
        
        # Check for coverage drops
        if "coverage" in logs.lower() and "decreased" in logs.lower():
            problems["coverage_drops"].append("Coverage decrease detected in logs")
        
        # Check for security issues
        if any(keyword in logs.lower() for keyword in ["vulnerability", "security", "audit"]):
            problems["security_issues"].append("Security issues detected in logs")
        
        # Check for dependency issues
        if any(keyword in logs.lower() for keyword in ["dependency", "package", "npm", "pip"]):
            problems["dependency_issues"].append("Dependency issues detected in logs")
    
    def generate_report(self, problems: Dict) -> str:
        """Generate monitoring report"""
        report = f"""# Workflow Monitoring Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Environment: Render Cron Job

## Summary

### Failed Runs: {len(problems['failed_runs'])}
"""
        
        if problems['failed_runs']:
            report += "\n**Failed Workflows:**\n"
            for run in problems['failed_runs'][:5]:  # Show first 5
                report += f"- {run['name']} (ID: {run['id']}) - {run['created_at']}\n"
        
        report += f"""
### Slow Runs: {len(problems['slow_runs'])}
"""
        
        if problems['slow_runs']:
            report += "\n**Slow Workflows:**\n"
            for run in problems['slow_runs'][:5]:  # Show first 5
                duration_min = run['duration'] // 60
                report += f"- {run['name']} (ID: {run['id']}) - {duration_min} minutes\n"
        
        report += f"""
### Recurring Issues: {len(problems['recurring_issues'])}
"""
        
        if problems['recurring_issues']:
            report += "\n**Recurring Problems:**\n"
            for workflow, count in problems['recurring_issues'].items():
                report += f"- {workflow}: {count} failures\n"
        
        report += f"""
### Security Issues: {len(problems['security_issues'])}
### Dependency Issues: {len(problems['dependency_issues'])}

## Recommendations

1. **Review failed workflows** and fix underlying issues
2. **Optimize slow workflows** by reducing build time
3. **Address recurring issues** to improve reliability
4. **Monitor security vulnerabilities** regularly
5. **Update dependencies** as needed

---
*This report was generated automatically by the Render cron job.*
"""
        return report
    
    def send_email_notification(self, report: str):
        """Send email notification"""
        if not all([self.email_config['from'], self.email_config['to'], 
                   self.email_config['username'], self.email_config['password']]):
            logger.warning("Email configuration incomplete, skipping email notification")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            msg['Subject'] = f"GitHub Workflow Problem Raporu - {datetime.now().strftime('%Y-%m-%d')}"
            
            msg.attach(MIMEText(report, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("Email notification sent successfully")
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def create_github_issue(self, report: str) -> Optional[int]:
        """Create GitHub issue with monitoring report"""
        if not self.github_token:
            logger.warning("GitHub token not available, skipping issue creation")
            return None
            
        issue_data = {
            "title": f"📊 Workflow Monitoring Report - {datetime.now().strftime('%Y-%m-%d')}",
            "body": report,
            "labels": ["monitoring", "workflow", "automation"]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/issues",
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
    
    def run_monitoring(self, days: int = 7, create_issue: bool = True, send_email: bool = False):
        """Run the monitoring process"""
        logger.info(f"Starting workflow monitoring for last {days} days")
        
        # Get workflow runs
        runs = self.get_workflow_runs(days=days)
        logger.info(f"Found {len(runs)} workflow runs")
        
        # Analyze problems
        problems = self.analyze_workflow_problems(runs)
        
        # Generate report
        report = self.generate_report(problems)
        
        # Save report to file
        report_path = self.logs_path / f"workflow-report-{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info("Report generated and saved")
        
        # Create GitHub issue if there are problems
        if create_issue and (problems['failed_runs'] or problems['recurring_issues']):
            issue_number = self.create_github_issue(report)
            if issue_number:
                logger.info(f"GitHub issue #{issue_number} created")
        
        # Send email notification
        if send_email:
            self.send_email_notification(report)
        
        return problems
    
    def run(self):
        """Run the workflow monitor cron job"""
        logger.info("🚀 Starting workflow monitor cron job...")
        
        if not self.check_environment():
            return False
        
        start_time = datetime.now()
        
        try:
            # Run monitoring
            problems = self.run_monitoring(days=7, create_issue=True, send_email=False)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info(f"✅ Workflow monitor cron job completed successfully in {duration}")
            logger.info(f"Found {len(problems['failed_runs'])} failed runs, {len(problems['recurring_issues'])} recurring issues")
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow monitor cron job failed: {e}")
            return False

def main():
    """Main function"""
    cron_job = WorkflowMonitorCronJob()
    success = cron_job.run()
    
    if success:
        print("Workflow monitor cron job completed successfully")
        sys.exit(0)
    else:
        print("Workflow monitor cron job failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 