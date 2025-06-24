#!/usr/bin/env python3
"""
🧹 BUZZ2REMOTE PROJECT CLEANUP & OPTIMIZATION
Comprehensive cleanup script for project optimization
"""

import os
import shutil
import glob
import json
from pathlib import Path
from datetime import datetime, timedelta

class ProjectCleaner:
    def __init__(self):
        self.root_dir = Path(".")
        self.cleaned_files = []
        self.errors = []
        self.space_saved = 0
        
    def log_action(self, action, details=""):
        """Log cleanup actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {action}")
        if details:
            print(f"   └── {details}")
        self.cleaned_files.append(f"{action}: {details}")
    
    def get_file_size(self, path):
        """Get file size in bytes"""
        try:
            return os.path.getsize(path)
        except:
            return 0
    
    def safe_remove(self, path, description=""):
        """Safely remove file/directory"""
        try:
            path = Path(path)
            if path.exists():
                size = 0
                if path.is_file():
                    size = self.get_file_size(path)
                elif path.is_dir():
                    size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                
                if path.is_file():
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                
                self.space_saved += size
                self.log_action(f"✅ Removed {description or path.name}", f"Saved {size/1024:.1f}KB")
                return True
        except Exception as e:
            self.errors.append(f"Failed to remove {path}: {e}")
            self.log_action(f"❌ Failed to remove {path}", str(e))
            return False
        return False
    
    def cleanup_root_directory(self):
        """Clean up root directory mess"""
        print("\n🧹 CLEANING ROOT DIRECTORY")
        print("=" * 50)
        
        # 1. Remove external job JSON files
        external_job_files = list(self.root_dir.glob("external_jobs_*.json"))
        for file in external_job_files:
            self.safe_remove(file, f"External job file: {file.name}")
        
        # 2. Remove API cache files
        api_cache_files = list(self.root_dir.glob(".api_requests_*.json"))
        for file in api_cache_files:
            self.safe_remove(file, f"API cache file: {file.name}")
        
        # 3. Remove log files
        log_files = ["external_api_cron.log", "nohup.out"]
        for file in log_files:
            self.safe_remove(self.root_dir / file, f"Log file: {file}")
        
        # 4. Remove system files
        system_files = [".DS_Store"]
        for file in system_files:
            self.safe_remove(self.root_dir / file, f"System file: {file}")
        
        # 5. Remove test files from root
        test_files = [
            "test_email.py", "simple_test.py", "test_integrations.py",
            "test_telegram.py", "test_*.py", "external_*.json"
        ]
        for pattern in test_files:
            for file in self.root_dir.glob(pattern):
                if file.is_file():
                    self.safe_remove(file, f"Test file: {file.name}")
    
    def cleanup_backend_directory(self):
        """Clean up backend directory"""
        print("\n🧹 CLEANING BACKEND DIRECTORY")
        print("=" * 50)
        
        backend_dir = self.root_dir / "backend"
        if not backend_dir.exists():
            return
        
        # 1. Remove external job files in backend
        external_files = list(backend_dir.glob("external_jobs_*.json"))
        for file in external_files:
            self.safe_remove(file, f"Backend external job file: {file.name}")
        
        # 2. Remove API cache files in backend
        api_files = list(backend_dir.glob(".api_requests_*.json"))
        for file in api_files:
            self.safe_remove(file, f"Backend API cache: {file.name}")
        
        # 3. Remove large log files
        large_logs = ["nohup.out", "backend.log"]
        for log in large_logs:
            log_path = backend_dir / log
            if log_path.exists() and self.get_file_size(log_path) > 100000:  # >100KB
                self.safe_remove(log_path, f"Large log file: {log}")
        
        # 4. Remove system files
        self.safe_remove(backend_dir / ".DS_Store", "Backend .DS_Store")
        
        # 5. Remove old requirements
        self.safe_remove(backend_dir / "requirements_old.txt", "Old requirements file")
        
        # 6. Remove export files
        export_files = list(backend_dir.glob("export*.json"))
        for file in export_files:
            if self.get_file_size(file) > 500000:  # >500KB
                self.safe_remove(file, f"Large export file: {file.name}")
    
    def remove_duplicate_directories(self):
        """Remove duplicate directories"""
        print("\n🧹 REMOVING DUPLICATE DIRECTORIES")
        print("=" * 50)
        
        # Remove backend_backup
        backup_dir = self.root_dir / "backend_backup"
        if backup_dir.exists():
            self.safe_remove(backup_dir, "Complete backend backup directory")
        
        # Remove venv_backup
        venv_backup = self.root_dir / "backend" / "venv_backup"
        if venv_backup.exists():
            self.safe_remove(venv_backup, "Virtual environment backup")
        
        # Remove nested frontend directories
        nested_frontend = self.root_dir / "frontend" / "frontend"
        if nested_frontend.exists():
            self.safe_remove(nested_frontend, "Nested frontend directory")
    
    def optimize_gitignore(self):
        """Optimize .gitignore for better coverage"""
        print("\n🧹 OPTIMIZING .GITIGNORE")
        print("=" * 50)
        
        gitignore_path = self.root_dir / ".gitignore"
        
        additional_rules = [
            "",
            "# === CLEANUP OPTIMIZATION RULES ===",
            "# External job files",
            "external_jobs_*.json",
            "*.log",
            "nohup.out",
            "",
            "# API cache files", 
            ".api_requests_*.json",
            "",
            "# Large export files",
            "export*.json",
            "",
            "# System files",
            ".DS_Store",
            "Thumbs.db",
            "",
            "# Test outputs",
            "test_output/",
            "*.tmp",
            "",
            "# Backup directories",
            "*_backup/",
            "backup_*/",
        ]
        
        try:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write('\n'.join(additional_rules))
            self.log_action("✅ Updated .gitignore", "Added cleanup optimization rules")
        except Exception as e:
            self.errors.append(f"Failed to update .gitignore: {e}")
    
    def create_data_directory_structure(self):
        """Create organized data directory structure"""
        print("\n🧹 CREATING ORGANIZED DATA STRUCTURE")
        print("=" * 50)
        
        # Create data directories
        data_dirs = [
            "data/external_jobs",
            "data/logs", 
            "data/cache",
            "data/exports",
            "data/temp"
        ]
        
        for dir_path in data_dirs:
            full_path = self.root_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.log_action(f"✅ Created directory", dir_path)
        
        # Create .gitkeep files
        for dir_path in data_dirs:
            gitkeep = self.root_dir / dir_path / ".gitkeep"
            gitkeep.touch()
    
    def fix_sentry_dependency(self):
        """Fix sentry SDK dependency issue"""
        print("\n🧹 FIXING SENTRY DEPENDENCY")
        print("=" * 50)
        
        requirements_path = self.root_dir / "backend" / "requirements.txt"
        
        if requirements_path.exists():
            try:
                with open(requirements_path, 'r') as f:
                    content = f.read()
                
                if "sentry-sdk" not in content:
                    with open(requirements_path, 'a') as f:
                        f.write("\n# Error monitoring\nsentry-sdk[fastapi]==2.32.0\n")
                    self.log_action("✅ Added sentry-sdk to requirements.txt")
                else:
                    self.log_action("✅ Sentry SDK already in requirements.txt")
                    
            except Exception as e:
                self.errors.append(f"Failed to update requirements.txt: {e}")
    
    def create_cleanup_script(self):
        """Create automated cleanup script"""
        print("\n🧹 CREATING AUTOMATED CLEANUP SCRIPT")
        print("=" * 50)
        
        cleanup_script = '''#!/bin/bash
# Automated cleanup script for Buzz2Remote project

echo "🧹 Starting automated cleanup..."

# Remove external job files older than 7 days
find . -name "external_jobs_*.json" -mtime +7 -delete 2>/dev/null

# Remove API cache files older than 1 day  
find . -name ".api_requests_*.json" -mtime +1 -delete 2>/dev/null

# Remove log files larger than 10MB
find . -name "*.log" -size +10M -delete 2>/dev/null

# Remove system files
find . -name ".DS_Store" -delete 2>/dev/null

# Clean Python cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

echo "✅ Cleanup completed!"
'''
        
        script_path = self.root_dir / "scripts" / "auto_cleanup.sh"
        script_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(script_path, 'w') as f:
                f.write(cleanup_script)
            os.chmod(script_path, 0o755)
            self.log_action("✅ Created automated cleanup script", str(script_path))
        except Exception as e:
            self.errors.append(f"Failed to create cleanup script: {e}")
    
    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        print("\n📊 CLEANUP REPORT")
        print("=" * 50)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_space_saved_mb": round(self.space_saved / (1024 * 1024), 2),
            "files_cleaned": len(self.cleaned_files),
            "errors": len(self.errors),
            "actions_performed": self.cleaned_files,
            "errors_encountered": self.errors
        }
        
        # Save report
        report_path = self.root_dir / "data" / "cleanup_report.json"
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            self.log_action("✅ Saved cleanup report", str(report_path))
        except Exception as e:
            self.errors.append(f"Failed to save report: {e}")
        
        # Print summary
        print(f"\n🎯 CLEANUP SUMMARY:")
        print(f"📁 Files cleaned: {len(self.cleaned_files)}")
        print(f"💾 Space saved: {self.space_saved/1024/1024:.2f} MB")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n⚠️ ERRORS ENCOUNTERED:")
            for error in self.errors:
                print(f"   • {error}")
    
    def run_complete_cleanup(self):
        """Run complete project cleanup"""
        print("🚀 BUZZ2REMOTE PROJECT CLEANUP & OPTIMIZATION")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Execute cleanup steps
        self.cleanup_root_directory()
        self.cleanup_backend_directory()
        self.remove_duplicate_directories()
        self.optimize_gitignore()
        self.create_data_directory_structure()
        self.fix_sentry_dependency()
        self.create_cleanup_script()
        self.generate_cleanup_report()
        
        print(f"\n🎉 CLEANUP COMPLETED!")
        print(f"💾 Total space saved: {self.space_saved/1024/1024:.2f} MB")

if __name__ == '__main__':
    cleaner = ProjectCleaner()
    cleaner.run_complete_cleanup() 