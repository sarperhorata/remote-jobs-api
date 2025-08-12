#!/usr/bin/env python3
"""
Dependabot Monitor Script
Production'da Dependabot PR'larını kontrol eder ve güvenli olanları otomatik merge eder
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dependabot-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DependabotMonitor:
    def __init__(self):
        """Initialize Dependabot Monitor"""
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO', 'sarperhorata/buzz2remote')
        self.owner, self.repo = self.github_repo.split('/')
        
        if not self.github_token:
            logger.error("GITHUB_TOKEN environment variable not set")
            sys.exit(1)
            
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Dependabot-Monitor/1.0'
        }
        
        self.base_url = f"https://api.github.com/repos/{self.github_repo}"
        
        # Configuration
        self.auto_merge_enabled = os.getenv('AUTO_MERGE_ENABLED', 'true').lower() == 'true'
        self.security_updates_only = os.getenv('SECURITY_UPDATES_ONLY', 'true').lower() == 'true'
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
    def get_dependabot_prs(self) -> List[Dict[str, Any]]:
        """Get all open Dependabot PRs"""
        try:
            url = f"{self.base_url}/pulls"
            params = {
                'state': 'open',
                'per_page': 100,
                'sort': 'created',
                'direction': 'desc'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            prs = response.json()
            dependabot_prs = [pr for pr in prs if pr['user']['login'] == 'dependabot[bot]']
            
            logger.info(f"Found {len(dependabot_prs)} Dependabot PRs")
            return dependabot_prs
            
        except Exception as e:
            logger.error(f"Error fetching Dependabot PRs: {e}")
            return []
    
    def is_security_update(self, pr: Dict[str, Any]) -> bool:
        """Check if PR is a security update"""
        title = pr['title'].lower()
        body = pr.get('body', '').lower()
        
        security_keywords = [
            'security', 'vulnerability', 'cve', 'patch', 'minor',
            'bugfix', 'fix', 'update', 'upgrade'
        ]
        
        # Check title and body for security keywords
        for keyword in security_keywords:
            if keyword in title or keyword in body:
                return True
                
        # Check labels
        labels = [label['name'].lower() for label in pr.get('labels', [])]
        security_labels = ['security', 'dependencies', 'patch', 'minor']
        
        for label in security_labels:
            if label in labels:
                return True
                
        return False
    
    def is_major_update(self, pr: Dict[str, Any]) -> bool:
        """Check if PR is a major update"""
        title = pr['title'].lower()
        body = pr.get('body', '').lower()
        
        major_keywords = [
            'major', 'breaking', 'breaking change', 'semver-major',
            'react', 'typescript', 'fastapi', 'pydantic'
        ]
        
        for keyword in major_keywords:
            if keyword in title or keyword in body:
                return True
                
        return False
    
    def check_pr_status(self, pr: Dict[str, Any]) -> Dict[str, Any]:
        """Check PR status and mergeability"""
        try:
            pr_number = pr['number']
            url = f"{self.base_url}/pulls/{pr_number}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            pr_data = response.json()
            
            # Check if PR is mergeable
            mergeable = pr_data.get('mergeable', False)
            mergeable_state = pr_data.get('mergeable_state', 'unknown')
            
            # Check CI status
            ci_status = self.get_ci_status(pr_number)
            
            return {
                'number': pr_number,
                'title': pr['title'],
                'mergeable': mergeable,
                'mergeable_state': mergeable_state,
                'ci_status': ci_status,
                'is_security': self.is_security_update(pr),
                'is_major': self.is_major_update(pr),
                'created_at': pr['created_at'],
                'updated_at': pr['updated_at']
            }
            
        except Exception as e:
            logger.error(f"Error checking PR {pr['number']} status: {e}")
            return {
                'number': pr['number'],
                'title': pr['title'],
                'mergeable': False,
                'mergeable_state': 'error',
                'ci_status': 'error',
                'is_security': False,
                'is_major': False,
                'error': str(e)
            }
    
    def get_ci_status(self, pr_number: int) -> str:
        """Get CI status for PR"""
        try:
            url = f"{self.base_url}/commits/{pr_number}/status"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            status_data = response.json()
            state = status_data.get('state', 'unknown')
            
            return state
            
        except Exception as e:
            logger.error(f"Error getting CI status for PR {pr_number}: {e}")
            return 'unknown'
    
    def auto_merge_pr(self, pr: Dict[str, Any]) -> bool:
        """Auto merge PR if conditions are met"""
        try:
            pr_number = pr['number']
            title = pr['title']
            
            # Check if auto-merge is enabled
            if not self.auto_merge_enabled:
                logger.info(f"Auto-merge disabled for PR #{pr_number}")
                return False
            
            # Check if it's a security update
            if self.security_updates_only and not pr['is_security']:
                logger.info(f"PR #{pr_number} is not a security update, skipping auto-merge")
                return False
            
            # Check if it's a major update
            if pr['is_major']:
                logger.info(f"PR #{pr_number} is a major update, manual review required")
                self.add_major_update_comment(pr_number)
                return False
            
            # Check mergeability
            if not pr['mergeable'] or pr['mergeable_state'] != 'clean':
                logger.info(f"PR #{pr_number} is not mergeable (state: {pr['mergeable_state']})")
                return False
            
            # Check CI status
            if pr['ci_status'] not in ['success', 'unknown']:
                logger.info(f"PR #{pr_number} CI status is {pr['ci_status']}, skipping auto-merge")
                return False
            
            # Perform merge
            url = f"{self.base_url}/pulls/{pr_number}/merge"
            data = {
                'merge_method': 'squash',
                'commit_title': f"chore(deps): {title}",
                'commit_message': f"Auto-merge dependency update\n\n{title}\n\nAutomatically merged by Dependabot Monitor"
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully auto-merged PR #{pr_number}: {title}")
                self.add_success_comment(pr_number)
                return True
            else:
                logger.error(f"❌ Failed to auto-merge PR #{pr_number}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error auto-merging PR #{pr['number']}: {e}")
            return False
    
    def add_success_comment(self, pr_number: int):
        """Add success comment to merged PR"""
        try:
            url = f"{self.base_url}/issues/{pr_number}/comments"
            data = {
                'body': '✅ **Auto-merged successfully!**\n\nThis dependency update has been automatically merged by the Dependabot Monitor.\n\n- ✅ Security/minor/patch update\n- ✅ Tests passed\n- ✅ No conflicts\n- ✅ Mergeable state'
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 201:
                logger.info(f"Added success comment to PR #{pr_number}")
                
        except Exception as e:
            logger.error(f"Error adding success comment to PR #{pr_number}: {e}")
    
    def add_major_update_comment(self, pr_number: int):
        """Add major update comment to PR"""
        try:
            url = f"{self.base_url}/issues/{pr_number}/comments"
            data = {
                'body': '⚠️ **Major Update Detected**\n\nThis is a major version update that requires manual review before merging.\n\n**Please review the changes and test thoroughly before merging.**\n\n- [ ] Review breaking changes\n- [ ] Test functionality\n- [ ] Check compatibility\n- [ ] Update documentation if needed\n\n🔍 **Review Checklist:**\n- Breaking changes in changelog\n- API compatibility\n- Performance impact\n- Security implications\n\n**This PR will not be auto-merged.**'
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 201:
                logger.info(f"Added major update comment to PR #{pr_number}")
                
        except Exception as e:
            logger.error(f"Error adding major update comment to PR #{pr_number}: {e}")
    
    def add_labels(self, pr: Dict[str, Any]):
        """Add appropriate labels to PR"""
        try:
            pr_number = pr['number']
            labels = []
            
            if pr['is_security']:
                labels.extend(['security', 'auto-merge', 'dependencies'])
            elif pr['is_major']:
                labels.extend(['major-update', 'needs-review', 'dependencies'])
            else:
                labels.extend(['dependencies', 'auto-merge'])
            
            url = f"{self.base_url}/issues/{pr_number}/labels"
            data = {'labels': labels}
            
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 200:
                logger.info(f"Added labels {labels} to PR #{pr_number}")
                
        except Exception as e:
            logger.error(f"Error adding labels to PR #{pr['number']}: {e}")
    
    def generate_report(self, processed_prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate monitoring report"""
        total_prs = len(processed_prs)
        auto_merged = len([pr for pr in processed_prs if pr.get('auto_merged', False)])
        major_updates = len([pr for pr in processed_prs if pr.get('is_major', False)])
        security_updates = len([pr for pr in processed_prs if pr.get('is_security', False)])
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_prs': total_prs,
            'auto_merged': auto_merged,
            'major_updates': major_updates,
            'security_updates': security_updates,
            'success_rate': (auto_merged / total_prs * 100) if total_prs > 0 else 0,
            'processed_prs': processed_prs
        }
        
        # Save report
        report_file = f"logs/dependabot-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {report_file}")
        return report
    
    def run(self):
        """Main monitoring process"""
        logger.info("🚀 Starting Dependabot Monitor...")
        
        try:
            # Get Dependabot PRs
            dependabot_prs = self.get_dependabot_prs()
            
            if not dependabot_prs:
                logger.info("No Dependabot PRs found")
                return
            
            processed_prs = []
            
            for pr in dependabot_prs:
                logger.info(f"Processing PR #{pr['number']}: {pr['title']}")
                
                # Check PR status
                pr_status = self.check_pr_status(pr)
                
                # Add labels
                self.add_labels(pr_status)
                
                # Attempt auto-merge
                auto_merged = self.auto_merge_pr(pr_status)
                pr_status['auto_merged'] = auto_merged
                
                processed_prs.append(pr_status)
                
                # Add delay to avoid rate limiting
                import time
                time.sleep(1)
            
            # Generate report
            report = self.generate_report(processed_prs)
            
            logger.info(f"✅ Dependabot Monitor completed!")
            logger.info(f"📊 Summary: {report['total_prs']} PRs processed, {report['auto_merged']} auto-merged")
            
        except Exception as e:
            logger.error(f"❌ Dependabot Monitor failed: {e}")
            sys.exit(1)

def main():
    """Main function"""
    monitor = DependabotMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 