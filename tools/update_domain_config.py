#!/usr/bin/env python3
"""
Domain Configuration Update Script for buzz2remote.com

Bu script, projedeki tüm domain ayarlarını buzz2remote.com için günceller.
"""

import json
import os
import re
from pathlib import Path

def update_file_content(file_path: str, replacements: dict, description: str = ""):
    """Update file content with replacements"""
    try:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            return False
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_value, new_value in replacements.items():
            content = content.replace(old_value, new_value)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path} - {description}")
            return True
        else:
            print(f"📝 No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {str(e)}")
        return False

def update_json_file(file_path: str, updates: dict, description: str = ""):
    """Update JSON file with new values"""
    try:
        if not os.path.exists(file_path):
            print(f"⚠️ JSON file not found: {file_path}")
            return False
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Deep update
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        deep_update(data, updates)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated JSON: {file_path} - {description}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating JSON {file_path}: {str(e)}")
        return False

def main():
    print("🌐 Buzz2Remote Domain Configuration Update")
    print("=" * 50)
    
    # Domain mappings
    old_domains = [
        "https://remote-jobs-backend.onrender.com",
        "http://localhost:8000",
        "https://buzz2remote.netlify.app"
    ]
    
    new_domain = "https://buzz2remote.com"
    new_api_domain = "https://buzz2remote-api.onrender.com"
    
    # Backend domain updates
    backend_replacements = {
        "https://remote-jobs-backend.onrender.com": new_api_domain,
        "http://localhost:8000": new_api_domain,
        "support@example.com": "support@buzz2remote.com",
        "example.com": "buzz2remote.com"
    }
    
    # Frontend domain updates
    frontend_replacements = {
        "https://buzz2remote.netlify.app": new_domain,
        "http://localhost:3000": new_domain,
        "https://remote-jobs-backend.onrender.com": new_api_domain
    }
    
    print("📝 Updating configuration files...")
    
    # Update backend main.py
    update_file_content(
        "backend/main.py",
        {
            "https://docs.buzz2remote.com": "https://docs.buzz2remote.com",
            "https://buzz2remote.com/terms": "https://buzz2remote.com/terms",
            "https://buzz2remote.com/contact": "https://buzz2remote.com/contact",
            "https://buzz2remote-api.onrender.com": new_api_domain,
            "http://localhost:8000": new_api_domain
        },
        "API documentation URLs"
    )
    
    # Update Render configuration
    update_file_content(
        "render.yaml",
        {
            "https://remote-jobs-backend.onrender.com": new_api_domain,
            "# FRONTEND_URL=http://localhost:3000": f"FRONTEND_URL={new_domain}"
        },
        "Render deployment config"
    )
    
    # Update backend render.yaml if exists
    if os.path.exists("backend/render.yaml"):
        update_file_content(
            "backend/render.yaml",
            backend_replacements,
            "Backend Render config"
        )
    
    # Update deploy scripts
    for script_path in ["deploy.sh", "start.sh"]:
        if os.path.exists(script_path):
            update_file_content(
                script_path,
                {
                    "https://remote-jobs-backend.onrender.com": new_api_domain,
                    "Buzz2Remote": "Buzz2Remote"
                },
                f"Deployment script: {script_path}"
            )
    
    # Update package.json files
    for package_json in ["frontend/package.json", "backend/package.json"]:
        if os.path.exists(package_json):
            update_json_file(
                package_json,
                {
                    "homepage": new_domain,
                    "bugs": {"url": f"{new_domain}/issues"},
                    "repository": {"url": "https://github.com/sarperhorata/buzz2remote"}
                },
                f"Package config: {package_json}"
            )
    
    # Update README.md
    if os.path.exists("README.md"):
        update_file_content(
            "README.md",
            {
                "https://buzz2remote.netlify.app": new_domain,
                "https://remote-jobs-backend.onrender.com": new_api_domain,
                "Remote Jobs API": "Buzz2Remote API"
            },
            "README documentation"
        )
    
    print("\n🔧 Manual steps required:")
    print("1. Netlify Domain Setup:")
    print(f"   - Add custom domain: buzz2remote.com")
    print(f"   - Configure DNS: buzz2remote.com -> {os.getenv('NETLIFY_SITE_ID', 'your-netlify-site')}.netlify.app")
    print(f"   - Enable HTTPS and force redirect")
    
    print("\n2. Render Domain Setup:")
    print(f"   - Update service domain to: buzz2remote-api.onrender.com")
    print(f"   - Update environment variables:")
    print(f"     FRONTEND_URL={new_domain}")
    print(f"     CORS_ORIGINS={new_domain}")
    
    print("\n3. DNS Configuration (at your domain provider):")
    print(f"   A record: buzz2remote.com -> Netlify IP")
    print(f"   CNAME: www.buzz2remote.com -> buzz2remote.com")
    print(f"   CNAME: api.buzz2remote.com -> buzz2remote-api.onrender.com")
    
    print("\n✅ Configuration update completed!")
    print("📋 Don't forget to redeploy both frontend and backend after DNS changes")

if __name__ == "__main__":
    main() 