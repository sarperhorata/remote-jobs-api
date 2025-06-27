#!/usr/bin/env python3
"""
Emergency Script to Clean Hardcoded Secrets from Files

Bu script, GitHub'a yüklenen gizli bilgileri otomatik olarak temizler.
"""

import os
import re
import glob
from pathlib import Path

def clean_hardcoded_secrets():
    """Remove hardcoded secrets from all files"""
    
    print("🚨 EMERGENCY SECRET CLEANUP STARTED")
    print("=" * 50)
    
    # Patterns to find and replace
    secret_patterns = [
        # MongoDB connection strings with credentials
        (r'mongodb\+srv://[^:]+:[^@]+@[^/]+', 'process.env.MONGODB_URI'),
        (r"mongodb\+srv://[^:]+:[^@]+@[^/]+", 'process.env.MONGODB_URI'),
        
        # Specific exposed credentials
        (r'mongodb\+srv://myremotejobs:cH622T5iGoc9tzfe@[^"\']+', 'process.env.MONGODB_URI'),
        (r'mongodb\+srv://sarperhorata:wEW5oQbUiNBaPGFk@[^"\']+', 'process.env.MONGODB_URI'),
        (r'mongodb\+srv://remotejobs:taBQw9bkYRAtFUOS@[^"\']+', 'process.env.MONGODB_URI'),
        
        # OpenAI API keys
        (r'sk-proj-[A-Za-z0-9_-]+', 'process.env.OPENAI_API_KEY'),
        
        # Telegram bot tokens (if any)
        (r'[0-9]+:AA[A-Za-z0-9_-]+', 'process.env.TELEGRAM_BOT_TOKEN'),
    ]
    
    # Files to clean (recursively find)
    file_patterns = [
        'backend*/src/scripts/*.ts',
        'backend*/src/config/*.ts',
        'backend*/utils/*.py',
        'backend*/config/*.py',
        'remote-jobs/backend*/src/scripts/*.ts',
        'remote-jobs/backend*/src/config/*.ts',
        'remote-jobs/backend*/utils/*.py',
        'backend_backup/src/scripts/*.ts',
        'backend_backup/src/config/*.ts',
        'backend_backup/utils/*.py',
    ]
    
    files_cleaned = 0
    total_replacements = 0
    
    # Get all files to process
    all_files = []
    for pattern in file_patterns:
        all_files.extend(glob.glob(pattern, recursive=True))
    
    print(f"📁 Found {len(all_files)} files to check")
    
    for file_path in all_files:
        try:
            if not os.path.exists(file_path):
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_replacements = 0
            
            # Apply all secret cleaning patterns
            for pattern, replacement in secret_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"   🔍 Found {len(matches)} secrets in {file_path}")
                    for match in matches:
                        print(f"      ❌ Removing: {match[:20]}...")
                    
                    # Replace with environment variable
                    content = re.sub(pattern, replacement, content)
                    file_replacements += len(matches)
                    total_replacements += len(matches)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                files_cleaned += 1
                print(f"✅ Cleaned {file_path} ({file_replacements} replacements)")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
    
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"   Files processed: {len(all_files)}")
    print(f"   Files cleaned: {files_cleaned}")
    print(f"   Total secrets removed: {total_replacements}")
    
    return files_cleaned > 0

def update_gitignore():
    """Update .gitignore to prevent future secret commits"""
    
    print("\n🔒 Updating .gitignore...")
    
    gitignore_additions = """
# === SECURITY: Prevent Secret Leaks ===
# Environment files
.env
.env.local
.env.production
.env.development
.env.staging
*.env
.env.*

# Secret files
secrets/
secret/
config/secrets.json
credentials.json
keys/
*.key
*.pem

# Database configuration files
database.json
db-config.json
mongo-config.js

# API keys and tokens
api-keys.txt
tokens.txt
auth-tokens.json

# Backup files that might contain secrets
*.backup
*.bak
backup/

# macOS specific
.DS_Store
"""
    
    try:
        # Read current .gitignore
        gitignore_path = ".gitignore"
        current_content = ""
        
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                current_content = f.read()
        
        # Check if security section already exists
        if "=== SECURITY: Prevent Secret Leaks ===" not in current_content:
            with open(gitignore_path, 'a') as f:
                f.write(gitignore_additions)
            print("✅ .gitignore updated with security rules")
        else:
            print("📝 .gitignore already has security rules")
            
    except Exception as e:
        print(f"❌ Error updating .gitignore: {str(e)}")

def create_env_template():
    """Create a secure .env template"""
    
    print("\n📝 Creating .env template...")
    
    env_template = """# 🔒 Buzz2Remote Environment Variables Template
# Copy this to .env and fill in your actual values
# NEVER commit .env files to git!

# API Configuration
API_HOST=0.0.0.0
API_PORT=5001
API_DEBUG=False
API_RELOAD=False

# Domain Configuration
DOMAIN=buzz2remote.com
FRONTEND_URL=https://buzz2remote.com
BACKEND_URL=https://buzz2remote-api.onrender.com

# Database Configuration
# Get this from MongoDB Atlas Dashboard
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority

# Logging Configuration
LOG_LEVEL=INFO

# Telegram Configuration
# Get bot token from @BotFather
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
# Get channel ID by adding bot to @buzz2remote and using get_telegram_channel_id.py
TELEGRAM_CHAT_ID=your-channel-id-here
TELEGRAM_CHANNEL=@buzz2remote

# CORS Configuration
CORS_ORIGINS=https://buzz2remote.com,https://www.buzz2remote.com

# Render Configuration
RENDER_SERVICE_ID=your-render-service-id
RENDER_API_KEY=your-render-api-key
RENDER_URL=https://buzz2remote-api.onrender.com
RENDER_DEPLOY_HOOK=your-deploy-hook-url

# Netlify Configuration
NETLIFY_SITE_ID=your-netlify-site-id
NETLIFY_AUTH_TOKEN=your-netlify-auth-token

# OpenAI Configuration (for CV parsing)
# Get from OpenAI Dashboard → API Keys
OPENAI_API_KEY=your-openai-api-key-here

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=support@buzz2remote.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=Buzz2Remote <support@buzz2remote.com>

# Security Keys
SECRET_KEY=your-super-secret-key-for-jwt
JWT_SECRET=your-jwt-secret-key

# Production vs Development
NODE_ENV=production
"""
    
    try:
        with open('.env.template', 'w') as f:
            f.write(env_template)
        print("✅ Created .env.template - copy this to .env and fill in real values")
    except Exception as e:
        print(f"❌ Error creating .env template: {str(e)}")

def verify_cleanup():
    """Verify that no secrets remain in the repository"""
    
    print("\n🔍 Verifying cleanup...")
    
    dangerous_patterns = [
        r'mongodb\+srv://[^:]+:[^@]+@',
        r'sk-proj-[A-Za-z0-9_-]{20,}',
        r'cH622T5iGoc9tzfe',
        r'wEW5oQbUiNBaPGFk',
        r'taBQw9bkYRAtFUOS'
    ]
    
    found_secrets = []
    
    # Check all non-ignored files
    for root, dirs, files in os.walk('.'):
        # Skip git and node_modules
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv']]
        
        for file in files:
            if file.endswith(('.ts', '.js', '.py', '.json', '.md', '.txt', '.env')):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in dangerous_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            found_secrets.append((file_path, pattern, matches))
                            
                except Exception:
                    continue
    
    if found_secrets:
        print("❌ WARNING: Secrets still found in repository!")
        for file_path, pattern, matches in found_secrets:
            print(f"   {file_path}: {len(matches)} matches for {pattern}")
        return False
    else:
        print("✅ No secrets found in repository!")
        return True

def main():
    """Main cleanup function"""
    
    print("🚨 EMERGENCY SECRET CLEANUP")
    print("This script will remove hardcoded secrets from your files")
    print("=" * 60)
    
    # Step 1: Clean hardcoded secrets
    secrets_cleaned = clean_hardcoded_secrets()
    
    # Step 2: Update .gitignore
    update_gitignore()
    
    # Step 3: Create .env template
    create_env_template()
    
    # Step 4: Verify cleanup
    cleanup_verified = verify_cleanup()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. 🔑 IMMEDIATELY change all MongoDB passwords")
    print("2. 🔑 Generate new OpenAI API key")
    print("3. 📝 Copy .env.template to .env and fill in new credentials")
    print("4. 🧪 Test: python3 test_telegram.py")
    print("5. 🚀 Commit these cleaned files")
    print("6. 🗂️ Consider cleaning git history (see URGENT_SECURITY_CLEANUP.md)")
    
    if secrets_cleaned:
        print("\n✅ Hardcoded secrets have been cleaned from files!")
    
    if not cleanup_verified:
        print("\n⚠️ Some secrets may still remain - manual review needed!")
    
    print("\n📖 See URGENT_SECURITY_CLEANUP.md for detailed instructions")

if __name__ == "__main__":
    main() 