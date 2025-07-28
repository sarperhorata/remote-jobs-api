#!/bin/bash

echo "🧹 Buzz2Remote - Dead Code & Backup Cleanup"
echo "==========================================="

# Get current directory
CURRENT_DIR=$(pwd)

echo "📁 Current directory: $CURRENT_DIR"
echo "🔍 Scanning for dead code and backup files..."

# Count files before cleanup
echo ""
echo "📊 BEFORE CLEANUP:"
echo "=================="

BACKUP_COUNT=$(find . -name "*.bak" -o -name "*.backup" -o -name "*_backup*" | wc -l | tr -d ' ')
VENV_BACKUP_SIZE=$(du -sh backend/venv_backup 2>/dev/null | cut -f1 || echo "0B")
TEMP_COUNT=$(find . -name "temp" -o -name "__pycache__" -o -name "*.pyc" | wc -l | tr -d ' ')
HTMLCOV_COUNT=$(find . -name "htmlcov" | wc -l | tr -d ' ')

echo "• Backup files: $BACKUP_COUNT"
echo "• venv_backup size: $VENV_BACKUP_SIZE"
echo "• Temp/cache files: $TEMP_COUNT"
echo "• HTML coverage dirs: $HTMLCOV_COUNT"

echo ""
echo "🗑️ CLEANING UP:"
echo "==============="

# 1. Remove backup files
echo "1. 🗂️ Removing backup files..."
find . -name "*.bak" -type f -delete 2>/dev/null
find . -name "*.backup" -type f -delete 2>/dev/null
find . -name "*_backup.py" -type f -delete 2>/dev/null
find . -name "*_backup.js" -type f -delete 2>/dev/null
find . -name "*_backup.tsx" -type f -delete 2>/dev/null
find . -name "*_backup.ts" -type f -delete 2>/dev/null

# 2. Remove venv_backup directory
echo "2. 📦 Removing venv_backup directory..."
if [ -d "backend/venv_backup" ]; then
    rm -rf backend/venv_backup
    echo "   ✅ Removed backend/venv_backup"
else
    echo "   ⏭️ venv_backup not found"
fi

# 3. Remove Python cache files
echo "3. 🐍 Removing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -type f -delete 2>/dev/null
find . -name "*.pyo" -type f -delete 2>/dev/null

# 4. Remove Node.js cache and build files (keep essential ones)
echo "4. 📦 Removing Node.js temporary files..."
find frontend -name "node_modules/.cache" -type d -exec rm -rf {} + 2>/dev/null
find frontend -name ".parcel-cache" -type d -exec rm -rf {} + 2>/dev/null

# 5. Remove old HTML coverage reports (keep latest)
echo "5. 📊 Cleaning old coverage reports..."
if [ -d "htmlcov" ]; then
    rm -rf htmlcov
    echo "   ✅ Removed root htmlcov"
fi

if [ -d "backend/htmlcov" ]; then
    echo "   ⏭️ Keeping backend/htmlcov (latest)"
fi

if [ -d "frontend/coverage" ]; then
    echo "   ⏭️ Keeping frontend/coverage (latest)"
fi

# 6. Remove temporary test files
echo "6. 🧪 Removing temporary test files..."
find . -name "test_results_*.json" -type f -delete 2>/dev/null
find . -name "pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null

# 7. Remove old log files (keep recent ones)
echo "7. 📝 Cleaning old log files..."
find . -name "*.log" -type f -mtime +7 -delete 2>/dev/null
find . -name "debug-*.js" -type f -delete 2>/dev/null
find . -name "fix_*.js" -type f -delete 2>/dev/null

# 8. Remove duplicate files
echo "8. 🔄 Removing known duplicate files..."
[ -f "backend/main_backup.py" ] && rm -f backend/main_backup.py
[ -f "frontend/core" ] && rm -f frontend/core
[ -f "frontend/fix_jobmodal.js" ] && rm -f frontend/fix_jobmodal.js

# 9. Remove old archives and exports (keep recent ones)
echo "9. 📁 Cleaning old archives..."
find . -name "*.tar.gz" -type f -mtime +30 -delete 2>/dev/null
find . -name "buzz2remote_backup_*.tar.gz" -type f -delete 2>/dev/null

# 10. Clean up environment backups
echo "10. ⚙️ Removing environment backups..."
find . -name ".env.backup" -type f -delete 2>/dev/null
find . -name "config/.env.backup" -type f -delete 2>/dev/null

echo ""
echo "🔧 OPTIMIZING:"
echo "=============="

# 1. Clean npm cache if needed
if command -v npm >/dev/null 2>&1; then
    echo "1. 📦 Cleaning npm cache..."
    cd frontend && npm cache clean --force >/dev/null 2>&1 && cd ..
    echo "   ✅ npm cache cleaned"
fi

# 2. Clean pip cache if needed
if [ -d ".venv" ]; then
    echo "2. 🐍 Cleaning pip cache..."
    .venv/bin/python -m pip cache purge >/dev/null 2>&1
    echo "   ✅ pip cache cleaned"
fi

echo ""
echo "📊 AFTER CLEANUP:"
echo "================="

# Count files after cleanup
BACKUP_COUNT_AFTER=$(find . -name "*.bak" -o -name "*.backup" -o -name "*_backup*" | wc -l | tr -d ' ')
TEMP_COUNT_AFTER=$(find . -name "temp" -o -name "__pycache__" -o -name "*.pyc" | wc -l | tr -d ' ')
TOTAL_SIZE=$(du -sh . 2>/dev/null | cut -f1)

echo "• Backup files: $BACKUP_COUNT_AFTER (was $BACKUP_COUNT)"
echo "• Temp/cache files: $TEMP_COUNT_AFTER (was $TEMP_COUNT)"
echo "• Total project size: $TOTAL_SIZE"

# Calculate space saved
if [ -d backend/venv_backup ]; then
    echo "⚠️ venv_backup still exists"
else
    echo "✅ venv_backup removed (saved $VENV_BACKUP_SIZE)"
fi

echo ""
echo "🎯 RECOMMENDATIONS:"
echo "=================="

# Check for remaining large files
echo "📁 Largest remaining files:"
find . -type f -size +10M 2>/dev/null | head -5 | while read file; do
    size=$(du -sh "$file" 2>/dev/null | cut -f1)
    echo "   • $file ($size)"
done

# Check for empty directories
EMPTY_DIRS=$(find . -type d -empty 2>/dev/null | wc -l | tr -d ' ')
if [ "$EMPTY_DIRS" -gt 0 ]; then
    echo "📂 Empty directories found: $EMPTY_DIRS"
    echo "   Run: find . -type d -empty -delete"
fi

# Check for development files in production
DEV_FILES=$(find . -name "*.dev.js" -o -name "*.development.*" | wc -l | tr -d ' ')
if [ "$DEV_FILES" -gt 0 ]; then
    echo "⚠️ Development files found: $DEV_FILES"
    echo "   Consider removing for production"
fi

echo ""
echo "✅ CLEANUP COMPLETED SUCCESSFULLY!"
echo "================================="
echo ""
echo "🧹 Removed:"
echo "   • $(($BACKUP_COUNT - $BACKUP_COUNT_AFTER)) backup files"
echo "   • $(($TEMP_COUNT - $TEMP_COUNT_AFTER)) temporary files"
echo "   • Python cache files"
echo "   • Old coverage reports"
echo "   • Duplicate files"
echo ""
echo "💡 To maintain clean code:"
echo "   1. Run this script weekly: ./cleanup_dead_code.sh"
echo "   2. Use .gitignore for temporary files"
echo "   3. Avoid committing backup files"
echo "   4. Regular code reviews for dead code"
echo ""
echo "🚀 Project is now optimized and clean!" 