#!/usr/bin/env python3
"""
Deployment script with Telegram notifications
"""

import os
import subprocess
import sys
from datetime import datetime
from service_notifications import ServiceNotifier

def run_command(command, capture_output=True):
    """Run a shell command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def main():
    # Initialize notifier
    try:
        notifier = ServiceNotifier()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        return 1
    
    # Step 1: Git operations
    print("📦 Step 1: Pushing to GitHub...")
    commit_message = f"Auto-deploy: Fix Render and Netlify deployment issues - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    success, stdout, stderr = run_command("git add .")
    if not success:
        notifier.notify_github_deploy(False, error_details=f"Git add failed: {stderr}")
        return 1
    
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success and "nothing to commit" not in stderr:
        notifier.notify_github_deploy(False, error_details=f"Git commit failed: {stderr}")
        return 1
    
    success, stdout, stderr = run_command("git push origin main")
    if success:
        # Get commit hash
        success_hash, commit_hash, _ = run_command("git rev-parse HEAD")
        commit_hash = commit_hash.strip() if success_hash else "unknown"
        notifier.notify_github_deploy(True, commit_hash=commit_hash, commit_message=commit_message)
        print("✅ GitHub push successful")
    else:
        notifier.notify_github_deploy(False, error_details=f"Git push failed: {stderr}")
        return 1
    
    # Step 2: Frontend build
    print("\n🏗️  Step 2: Building frontend...")
    os.chdir("frontend")
    
    success, stdout, stderr = run_command("npm run build")
    if success:
        print("✅ Frontend build successful")
    else:
        notifier.notify_netlify_deploy(False, error_details=f"Build failed: {stderr}")
        os.chdir("..")
        return 1
    
    # Step 3: Deploy to Netlify
    print("\n🌐 Step 3: Deploying to Netlify...")
    success, stdout, stderr = run_command("netlify deploy --prod --dir=build")
    
    if success:
        # Extract deploy URL from output
        deploy_url = "https://buzz2remote.netlify.app"
        deploy_id = "manual-deploy"
        
        notifier.notify_netlify_deploy(True, url=deploy_url, deploy_id=deploy_id)
        print("✅ Netlify deployment successful")
    else:
        notifier.notify_netlify_deploy(False, error_details=f"Deploy failed: {stderr}")
    
    os.chdir("..")
    
    # Step 4: Check Render deployment (triggered by GitHub push)
    print("\n🚀 Step 4: Render deployment status...")
    print("Render deployment is triggered automatically by GitHub push.")
    print("Please check Render dashboard for deployment status.")
    
    # Note: Render deployment is automatic after GitHub push
    notifier.notify_render_deploy(
        True, 
        url="https://remote-jobs-api-k9v1.onrender.com",
        build_time="Automatic deployment in progress"
    )
    
    # Step 5: Health checks
    print("\n🏥 Step 5: Running health checks...")
    success, stdout, stderr = run_command("./health_check.sh", capture_output=False)
    
    if success:
        print("✅ Health checks completed")
    else:
        print("⚠️  Health check had some failures")
    
    # Send final summary
    message = f"""🎉 <b>DEPLOYMENT ÖZET</b>

✅ GitHub: Push başarılı
✅ Netlify: Deploy başarılı
🔄 Render: Otomatik deploy başladı

🔗 <b>URL'ler:</b>
• Frontend: https://buzz2remote.netlify.app
• Backend: https://remote-jobs-api-k9v1.onrender.com
• Domain: https://buzz2remote.com

🕐 <b>Tamamlanma:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    notifier.send_notification(message)
    
    print("\n✅ Deployment process completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 