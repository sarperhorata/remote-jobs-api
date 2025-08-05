#!/usr/bin/env python3
"""
GitHub Workflow Monitor
Bu script GitHub workflow'larını izler ve problemleri raporlar
"""

import os
import json
import requests
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import logging

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow-monitor.log'),
        logging.StreamHandler()
    ]
)

class WorkflowMonitor:
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    def get_workflow_runs(self, workflow_id: Optional[str] = None, days: int = 7) -> List[Dict]:
        """Son N günün workflow çalışmalarını al"""
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
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get("workflow_runs", [])
        except requests.RequestException as e:
            logging.error(f"Error fetching workflow runs: {e}")
            return []
    
    def get_workflow_run_details(self, run_id: int) -> Optional[Dict]:
        """Workflow çalışmasının detaylarını al"""
        url = f"{self.base_url}/actions/runs/{run_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching workflow run {run_id}: {e}")
            return None
    
    def get_job_logs(self, run_id: int, job_id: int) -> Optional[str]:
        """Job loglarını al"""
        url = f"{self.base_url}/actions/runs/{run_id}/jobs/{job_id}/logs"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching job logs for {job_id}: {e}")
            return None
    
    def analyze_workflow_problems(self, runs: List[Dict]) -> Dict:
        """Workflow problemlerini analiz et"""
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
            
            # Başarısız çalışmalar
            if status == "failure":
                problems["failed_runs"].append({
                    "id": run_id,
                    "name": run_name,
                    "created_at": run["created_at"],
                    "duration": duration
                })
            
            # Yavaş çalışmalar (30 dakikadan fazla)
            if duration and duration > 1800:  # 30 dakika
                problems["slow_runs"].append({
                    "id": run_id,
                    "name": run_name,
                    "duration": duration,
                    "created_at": run["created_at"]
                })
            
            # Detayları al
            details = self.get_workflow_run_details(run_id)
            if details:
                jobs = details.get("jobs", [])
                for job in jobs:
                    job_name = job["name"]
                    job_status = job["conclusion"]
                    
                    if job_status == "failure":
                        # Tekrarlayan problemleri tespit et
                        if job_name not in problems["recurring_issues"]:
                            problems["recurring_issues"][job_name] = 0
                        problems["recurring_issues"][job_name] += 1
                        
                        # Log analizi
                        logs = self.get_job_logs(run_id, job["id"])
                        if logs:
                            self.analyze_logs_for_issues(logs, problems)
        
        return problems
    
    def analyze_logs_for_issues(self, logs: str, problems: Dict):
        """Loglardan problemleri tespit et"""
        log_lines = logs.lower().split('\n')
        
        for line in log_lines:
            # Coverage düşüşleri
            if "coverage" in line and ("decreased" in line or "dropped" in line):
                problems["coverage_drops"].append(line.strip())
            
            # Security problemleri
            if any(keyword in line for keyword in ["vulnerability", "security", "audit failed"]):
                problems["security_issues"].append(line.strip())
            
            # Dependency problemleri
            if any(keyword in line for keyword in ["dependency", "outdated", "npm audit"]):
                problems["dependency_issues"].append(line.strip())
    
    def generate_report(self, problems: Dict) -> str:
        """Problem raporu oluştur"""
        report = f"""
# GitHub Workflow Problem Raporu
Oluşturulma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Özet
- Toplam Başarısız Çalışma: {len(problems['failed_runs'])}
- Yavaş Çalışma: {len(problems['slow_runs'])}
- Tekrarlayan Problemler: {len(problems['recurring_issues'])}
- Coverage Düşüşleri: {len(problems['coverage_drops'])}
- Security Problemleri: {len(problems['security_issues'])}
- Dependency Problemleri: {len(problems['dependency_issues'])}

## Başarısız Çalışmalar
"""
        
        for run in problems["failed_runs"][:5]:  # Son 5'i göster
            report += f"- {run['name']} (ID: {run['id']}) - {run['created_at']}\n"
        
        report += "\n## Tekrarlayan Problemler\n"
        for job_name, count in sorted(problems["recurring_issues"].items(), key=lambda x: x[1], reverse=True):
            report += f"- {job_name}: {count} kez başarısız\n"
        
        if problems["coverage_drops"]:
            report += "\n## Coverage Düşüşleri\n"
            for drop in problems["coverage_drops"][:3]:
                report += f"- {drop}\n"
        
        if problems["security_issues"]:
            report += "\n## Security Problemleri\n"
            for issue in problems["security_issues"][:3]:
                report += f"- {issue}\n"
        
        return report
    
    def send_notification(self, report: str, email_config: Dict):
        """Email bildirimi gönder"""
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['from']
            msg['To'] = email_config['to']
            msg['Subject'] = f"GitHub Workflow Problem Raporu - {datetime.now().strftime('%Y-%m-%d')}"
            
            msg.attach(MIMEText(report, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logging.info("Notification email sent successfully")
        except Exception as e:
            logging.error(f"Error sending notification: {e}")
    
    def create_github_issue(self, report: str) -> Optional[int]:
        """GitHub issue oluştur"""
        url = f"{self.base_url}/issues"
        
        issue_data = {
            "title": f"🤖 Workflow Problem Raporu - {datetime.now().strftime('%Y-%m-%d')}",
            "body": report,
            "labels": ["workflow", "monitoring", "automation"]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=issue_data)
            response.raise_for_status()
            issue = response.json()
            logging.info(f"GitHub issue created: {issue['html_url']}")
            return issue['number']
        except requests.RequestException as e:
            logging.error(f"Error creating GitHub issue: {e}")
            return None
    
    def run_monitoring(self, days: int = 7, create_issue: bool = True, send_email: bool = False, email_config: Dict = None):
        """Ana monitoring fonksiyonu"""
        logging.info(f"Starting workflow monitoring for last {days} days")
        
        # Workflow çalışmalarını al
        runs = self.get_workflow_runs(days=days)
        logging.info(f"Found {len(runs)} workflow runs")
        
        # Problemleri analiz et
        problems = self.analyze_workflow_problems(runs)
        
        # Rapor oluştur
        report = self.generate_report(problems)
        
        # Raporu dosyaya kaydet
        with open(f"workflow-report-{datetime.now().strftime('%Y%m%d')}.md", 'w') as f:
            f.write(report)
        
        logging.info("Report generated and saved")
        
        # GitHub issue oluştur
        if create_issue and (problems['failed_runs'] or problems['recurring_issues']):
            issue_number = self.create_github_issue(report)
            if issue_number:
                logging.info(f"GitHub issue #{issue_number} created")
        
        # Email bildirimi gönder
        if send_email and email_config:
            self.send_notification(report, email_config)
        
        return problems

def main():
    """Ana fonksiyon"""
    import argparse
    
    # Command line arguments
    parser = argparse.ArgumentParser(description='GitHub Workflow Monitor')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--days', type=int, default=7, help='Number of days to monitor')
    parser.add_argument('--no-issue', action='store_true', help='Do not create GitHub issue')
    parser.add_argument('--email', action='store_true', help='Send email notification')
    args = parser.parse_args()
    
    # Debug mode
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Debug mode enabled")
    
    # Konfigürasyon
    github_token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'sarperhorata')
    repo_name = os.getenv('GITHUB_REPOSITORY_NAME', 'buzz2remote')
    
    if not github_token:
        logging.error("GITHUB_TOKEN environment variable not set")
        return
    
    # Monitor oluştur
    monitor = WorkflowMonitor(github_token, repo_owner, repo_name)
    
    # Email konfigürasyonu
    email_config = None
    if args.email:
        email_config = {
            'from': os.getenv('EMAIL_FROM'),
            'to': os.getenv('EMAIL_TO'),
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD')
        }
    
    # Monitoring çalıştır
    problems = monitor.run_monitoring(
        days=args.days, 
        create_issue=not args.no_issue,
        send_email=args.email,
        email_config=email_config
    )
    
    # Sonuçları yazdır
    print(f"\nMonitoring completed!")
    print(f"Failed runs: {len(problems['failed_runs'])}")
    print(f"Recurring issues: {len(problems['recurring_issues'])}")
    print(f"Security issues: {len(problems['security_issues'])}")
    
    if args.debug:
        print(f"\nDetailed problems:")
        for problem_type, items in problems.items():
            if items:
                print(f"  {problem_type}: {len(items)} items")

if __name__ == "__main__":
    main() 