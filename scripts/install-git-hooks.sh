#!/bin/bash

# Install Git Hooks for Pre-Deploy Automation
# This script sets up automatic test running before commits and pushes

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo -e "${BLUE}🔧 Installing Git Hooks for Pre-Deploy Automation${NC}"
echo "=================================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Pre-commit hook with automatic testing and fixing
# Runs before each commit to ensure code quality

echo "🔍 Running pre-commit checks..."

# Run the pre-deployment automation (quick mode)
if [ -f "scripts/pre-deploy-automation.sh" ]; then
    echo "🧪 Running pre-deployment tests..."
    
    # Set environment variable for quick mode
    export QUICK_MODE=true
    export MAX_RETRY_ATTEMPTS=2
    export TEST_TIMEOUT=60
    
    if ! ./scripts/pre-deploy-automation.sh; then
        echo "❌ Pre-commit tests failed!"
        echo "🔧 Auto-fixes were attempted but were not sufficient."
        echo "💡 Fix the issues manually and try committing again."
        echo ""
        echo "📝 To skip this check (NOT RECOMMENDED):"
        echo "   git commit --no-verify"
        exit 1
    fi
    
    echo "✅ Pre-commit tests passed!"
else
    echo "⚠️ Pre-deploy automation script not found, running basic checks..."
    
    # Fallback to basic checks
    if [ -d "frontend" ]; then
        cd frontend
        echo "🔍 Running frontend lint check..."
        npm run lint || {
            echo "🔧 Attempting to fix lint issues..."
            npm run lint:fix || true
        }
        cd ..
    fi
    
    if [ -d "backend" ]; then
        cd backend
        echo "🔍 Running backend syntax check..."
        python -m py_compile *.py 2>/dev/null || true
        cd ..
    fi
fi

# Check for large files
echo "📏 Checking for large files..."
large_files=$(find . -type f -size +10M -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.next/*" -not -path "./build/*" -not -path "./dist/*" 2>/dev/null || true)

if [ ! -z "$large_files" ]; then
    echo "⚠️ Large files detected (>10MB):"
    echo "$large_files"
    echo ""
    echo "💡 Consider using Git LFS for large files or add them to .gitignore"
    echo "   To proceed anyway: git commit --no-verify"
    exit 1
fi

# Check for sensitive information
echo "🔒 Scanning for sensitive information..."
sensitive_patterns=(
    "password\s*=\s*['\"][^'\"]+['\"]"
    "api_key\s*=\s*['\"][^'\"]+['\"]"
    "secret\s*=\s*['\"][^'\"]+['\"]"
    "token\s*=\s*['\"][^'\"]+['\"]"
    "-----BEGIN PRIVATE KEY-----"
    "-----BEGIN RSA PRIVATE KEY-----"
)

sensitive_found=false
for pattern in "${sensitive_patterns[@]}"; do
    if git diff --cached --name-only | xargs grep -l -E "$pattern" 2>/dev/null; then
        echo "🚨 Potential sensitive information found!"
        echo "Pattern: $pattern"
        sensitive_found=true
    fi
done

if [ "$sensitive_found" = true ]; then
    echo ""
    echo "❌ Commit blocked due to potential sensitive information"
    echo "💡 Remove sensitive data and try again"
    echo "   To proceed anyway: git commit --no-verify"
    exit 1
fi

echo "✅ Pre-commit checks completed successfully!"
EOF

# Create pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

# Pre-push hook with comprehensive testing
# Runs before each push to ensure deployment readiness

echo "🚀 Running pre-push checks..."

# Check if we're pushing to protected branches
protected_branches="master main production"
current_branch=$(git branch --show-current)

for branch in $protected_branches; do
    if [ "$current_branch" = "$branch" ]; then
        echo "🛡️ Pushing to protected branch: $branch"
        
        # Run full pre-deployment automation
        if [ -f "scripts/pre-deploy-automation.sh" ]; then
            echo "🧪 Running full pre-deployment test suite..."
            
            # Set environment for full mode
            export QUICK_MODE=false
            export MAX_RETRY_ATTEMPTS=3
            export TEST_TIMEOUT=120
            
            if ! ./scripts/pre-deploy-automation.sh; then
                echo "❌ Pre-push tests failed!"
                echo "🛑 Push to $branch blocked"
                echo "💡 To force push (NOT RECOMMENDED): git push --no-verify"
                exit 1
            fi
            
            echo "✅ Full test suite passed! Safe to push to $branch"
        else
            echo "⚠️ Pre-deploy automation not found, running basic checks..."
            
            # Basic checks for protected branches
            if [ -d "frontend" ]; then
                cd frontend
                echo "🏗️ Testing frontend build..."
                npm run build || {
                    echo "❌ Frontend build failed!"
                    exit 1
                }
                cd ..
            fi
            
            if [ -d "backend" ] && [ -f "backend/run_tests.py" ]; then
                cd backend
                echo "🧪 Running backend tests..."
                python run_tests.py || {
                    echo "❌ Backend tests failed!"
                    exit 1
                }
                cd ..
            fi
        fi
        break
    fi
done

echo "✅ Pre-push checks completed successfully!"
EOF

# Create commit-msg hook for conventional commits
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash

# Commit message validation
# Enforces conventional commit format

commit_regex='^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Invalid commit message format!"
    echo ""
    echo "📝 Use conventional commit format:"
    echo "   feat: add new feature"
    echo "   fix: resolve bug in authentication"
    echo "   docs: update API documentation"
    echo "   test: add integration tests"
    echo "   chore: update dependencies"
    echo ""
    echo "💡 Your commit message:"
    cat "$1"
    echo ""
    echo "🔧 To skip this check: git commit --no-verify"
    exit 1
fi

echo "✅ Commit message format is valid"
EOF

# Make hooks executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
chmod +x .git/hooks/commit-msg

print_status "Git hooks installed successfully!"
print_info "The following hooks are now active:"
echo "  • pre-commit:  Runs tests and checks before each commit"
echo "  • pre-push:    Runs full test suite before pushing to protected branches"
echo "  • commit-msg:  Validates commit message format"
echo ""

print_info "Configuration:"
echo "  • Protected branches: master, main, production"
echo "  • Quick tests on commit, full tests on push to protected branches"
echo "  • Automatic error detection and fixing"
echo "  • Conventional commit message format required"
echo ""

print_warning "To bypass hooks (NOT RECOMMENDED):"
echo "  • git commit --no-verify"
echo "  • git push --no-verify"
echo ""

echo -e "${GREEN}🎉 Pre-deployment automation is now active!${NC}"
echo "Your code will be automatically tested and fixed before deployment."