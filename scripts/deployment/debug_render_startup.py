#!/usr/bin/env python3
"""
Render Startup Debug Script
Identifies FastAPI startup issues and provides solutions
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_file_structure():
    """Check if all required files exist"""
    print("🔍 Checking file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "backend/main.py",
        "backend/requirements.txt"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} exists")
            
            # Check if main.py has FastAPI app
            if file_path.endswith("main.py"):
                with open(file_path, 'r') as f:
                    content = f.read()
                    if "FastAPI" in content and "app =" in content:
                        print(f"      ✅ FastAPI app found in {file_path}")
                    else:
                        print(f"      ❌ No FastAPI app in {file_path}")
        else:
            print(f"   ❌ {file_path} missing")

def check_main_py_locations():
    """Find all main.py files and check FastAPI setup"""
    print("\n📍 Locating main.py files...")
    
    main_files = []
    for root, dirs, files in os.walk("."):
        if "main.py" in files:
            main_path = os.path.join(root, "main.py")
            main_files.append(main_path)
    
    for main_file in main_files:
        print(f"\n   📄 Found: {main_file}")
        try:
            with open(main_file, 'r') as f:
                content = f.read()
                
            # Check for FastAPI components
            has_fastapi = "from fastapi import" in content or "FastAPI" in content
            has_app = "app = " in content
            has_uvicorn = "uvicorn" in content
            
            print(f"      FastAPI import: {'✅' if has_fastapi else '❌'}")
            print(f"      App instance: {'✅' if has_app else '❌'}")
            print(f"      Uvicorn ready: {'✅' if has_uvicorn else '❌'}")
            
            # Check for potential startup issues
            if "import" in content:
                imports = [line.strip() for line in content.split('\n') if line.strip().startswith('import') or line.strip().startswith('from')]
                print(f"      Total imports: {len(imports)}")
                
        except Exception as e:
            print(f"      ❌ Error reading {main_file}: {e}")

def check_requirements():
    """Check requirements.txt files"""
    print("\n📦 Checking requirements.txt files...")
    
    req_files = []
    for root, dirs, files in os.walk("."):
        if "requirements.txt" in files:
            req_path = os.path.join(root, "requirements.txt")
            req_files.append(req_path)
    
    for req_file in req_files:
        print(f"\n   📄 Found: {req_file}")
        try:
            with open(req_file, 'r') as f:
                lines = f.readlines()
                
            # Check for critical dependencies
            critical_deps = ['fastapi', 'uvicorn', 'motor', 'pymongo']
            found_deps = []
            
            for line in lines:
                line = line.strip().lower()
                for dep in critical_deps:
                    if dep in line:
                        found_deps.append(dep)
                        
            print(f"      Total dependencies: {len(lines)}")
            print(f"      Critical deps found: {found_deps}")
            
            missing_deps = set(critical_deps) - set(found_deps)
            if missing_deps:
                print(f"      ❌ Missing: {missing_deps}")
            else:
                print(f"      ✅ All critical dependencies present")
                
        except Exception as e:
            print(f"      ❌ Error reading {req_file}: {e}")

def test_local_import():
    """Test if main.py can be imported locally"""
    print("\n🧪 Testing local imports...")
    
    # Test backend/main.py import
    test_scripts = [
        ("backend/main.py", "backend.main"),
        ("main.py", "main")
    ]
    
    for file_path, import_path in test_scripts:
        if os.path.exists(file_path):
            print(f"\n   Testing {file_path}...")
            try:
                # Try importing
                sys.path.insert(0, os.path.dirname(file_path) or '.')
                
                if import_path == "backend.main":
                    # Add parent directory to path for backend imports
                    sys.path.insert(0, '.')
                
                module = __import__(import_path.split('.')[0])
                if '.' in import_path:
                    for attr in import_path.split('.')[1:]:
                        module = getattr(module, attr)
                
                # Check if app exists
                if hasattr(module, 'app'):
                    print(f"      ✅ FastAPI app imported successfully")
                    app = getattr(module, 'app')
                    print(f"      ✅ App type: {type(app)}")
                else:
                    print(f"      ❌ No 'app' attribute found")
                    
            except ImportError as e:
                print(f"      ❌ Import error: {e}")
            except Exception as e:
                print(f"      ❌ Other error: {e}")

def check_environment_variables():
    """Check if environment variables are accessible"""
    print("\n🔧 Checking environment variables...")
    
    critical_env_vars = [
        'MONGODB_URI',
        'TELEGRAM_BOT_TOKEN',
        'CRON_SECRET_TOKEN',
        'ENVIRONMENT'
    ]
    
    for var in critical_env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {'*' * min(10, len(value))}... (length: {len(value)})")
        else:
            print(f"   ❌ {var}: Not set")

def generate_render_config():
    """Generate correct render.yaml configuration"""
    print("\n⚙️ Generating Render configuration...")
    
    # Determine correct start command based on file structure
    if os.path.exists("backend/main.py"):
        start_command = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
        build_command = "cd backend && pip install -r requirements.txt"
    elif os.path.exists("main.py"):
        start_command = "uvicorn main:app --host 0.0.0.0 --port $PORT"
        build_command = "pip install -r requirements.txt"
    else:
        start_command = "# ERROR: No main.py found"
        build_command = "# ERROR: No requirements.txt found"
    
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "buzz2remote-api",
                "runtime": "python",
                "buildCommand": build_command,
                "startCommand": start_command,
                "plan": "free",
                "env": {
                    "PYTHON_VERSION": "3.11",
                    "ENVIRONMENT": "production"
                }
            }
        ]
    }
    
    print(f"   📄 Recommended start command: {start_command}")
    print(f"   📄 Recommended build command: {build_command}")
    
    return render_config

def main():
    """Main debug function"""
    print("🚀 Render Startup Debug Tool")
    print("=" * 50)
    
    check_file_structure()
    check_main_py_locations()
    check_requirements()
    test_local_import()
    check_environment_variables()
    config = generate_render_config()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    print("\n🔧 RECOMMENDED RENDER SETTINGS:")
    print("1. Build Command:")
    print(f"   {config['services'][0]['buildCommand']}")
    print("\n2. Start Command:")
    print(f"   {config['services'][0]['startCommand']}")
    
    print("\n📋 TROUBLESHOOTING STEPS:")
    print("1. Verify Render service 'Live' status")
    print("2. Check Render deployment logs for errors")
    print("3. Ensure start command is exactly as recommended")
    print("4. Trigger manual redeploy if needed")
    print("5. Test endpoints again after redeploy")
    
    print("\n🔗 USEFUL RENDER DASHBOARD LINKS:")
    print("• Service: https://dashboard.render.com")
    print("• Logs: Check 'Logs' tab in your service")
    print("• Settings: Check 'Settings' tab for start command")
    print("• Environment: Check 'Environment' tab for variables")

if __name__ == "__main__":
    main() 