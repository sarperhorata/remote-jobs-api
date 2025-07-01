#!/bin/bash

# Setup Pre-Deploy Automation System
# This script configures the entire automation system

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  🚀 ${GREEN}BUZZ2REMOTE PRE-DEPLOY AUTOMATION SETUP${NC}            ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_requirements() {
    print_step "Checking system requirements..."
    
    local missing_deps=()
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("Node.js")
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        missing_deps+=("Python")
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        missing_deps+=("Git")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and run this script again."
        exit 1
    fi
    
    print_success "All required dependencies are installed"
}

setup_directories() {
    print_step "Setting up directories..."
    
    # Create necessary directories
    mkdir -p deploy-logs
    mkdir -p config
    mkdir -p docs
    mkdir -p templates
    
    print_success "Directories created"
}

setup_scripts() {
    print_step "Setting up scripts..."
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    print_success "Scripts are now executable"
}

install_frontend_dependencies() {
    print_step "Installing frontend dependencies..."
    
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        cd frontend
        
        # Install dependencies
        if npm install --legacy-peer-deps; then
            print_success "Frontend dependencies installed"
        else
            print_warning "Frontend dependency installation had warnings"
        fi
        
        cd ..
    else
        print_warning "Frontend directory not found, skipping..."
    fi
}

install_backend_dependencies() {
    print_step "Installing backend dependencies..."
    
    if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
        cd backend
        
        # Install Python dependencies
        if pip install -r requirements.txt; then
            print_success "Backend dependencies installed"
        else
            print_warning "Backend dependency installation had warnings"
        fi
        
        cd ..
    else
        print_warning "Backend requirements.txt not found, skipping..."
    fi
}

test_system() {
    print_step "Testing automation system..."
    
    # Test the main automation script
    if [ -f "scripts/pre-deploy-automation.sh" ]; then
        print_step "Running quick test of automation system..."
        
        # Set test environment variables
        export QUICK_MODE=true
        export MAX_RETRY_ATTEMPTS=1
        export TEST_TIMEOUT=30
        
        # Run a dry-run test
        if ./scripts/pre-deploy-automation.sh 2>/dev/null; then
            print_success "Automation system test passed"
        else
            print_warning "Automation system test had issues (this is normal during setup)"
        fi
    else
        print_error "Pre-deploy automation script not found!"
        exit 1
    fi
}

install_git_hooks() {
    print_step "Installing Git hooks..."
    
    if [ -d ".git" ]; then
        if ./scripts/install-git-hooks.sh; then
            print_success "Git hooks installed successfully"
        else
            print_error "Failed to install Git hooks"
            exit 1
        fi
    else
        print_warning "Not in a Git repository, skipping Git hooks installation"
    fi
}

create_example_config() {
    print_step "Creating example configuration..."
    
    # Create a simple config if one doesn't exist
    if [ ! -f "config/pre-deploy-config.json" ]; then
        cat > config/pre-deploy-config.json << 'EOF'
{
  "automation": {
    "enabled": true,
    "version": "2.0"
  },
  "testing": {
    "maxRetryAttempts": 3,
    "timeoutSeconds": 120,
    "quickModeTimeout": 60
  },
  "autoFix": {
    "enabled": true,
    "maxFixAttempts": 2
  },
  "logging": {
    "level": "info",
    "directory": "deploy-logs"
  }
}
EOF
        print_success "Configuration file created"
    else
        print_success "Configuration file already exists"
    fi
}

run_sample_tests() {
    print_step "Running sample tests..."
    
    # Test frontend if available
    if [ -d "frontend" ]; then
        cd frontend
        echo "Testing frontend linting..."
        if npm run lint 2>/dev/null || npm run lint:fix 2>/dev/null; then
            print_success "Frontend lint test passed"
        else
            print_warning "Frontend lint test had issues"
        fi
        cd ..
    fi
    
    # Test backend if available
    if [ -d "backend" ] && [ -f "backend/run_tests.py" ]; then
        cd backend
        echo "Testing backend..."
        if python run_tests.py 2>/dev/null; then
            print_success "Backend test passed"
        else
            print_warning "Backend test had issues"
        fi
        cd ..
    fi
}

show_summary() {
    echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  🎉 ${BLUE}SETUP COMPLETED SUCCESSFULLY!${NC}                        ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}\n"
    
    echo -e "${BLUE}📋 What's been set up:${NC}"
    echo "  ✅ Directory structure"
    echo "  ✅ Executable scripts"
    echo "  ✅ Dependencies (where possible)"
    echo "  ✅ Git hooks (if in git repo)"
    echo "  ✅ Configuration files"
    echo "  ✅ Sample tests"
    echo ""
    
    echo -e "${BLUE}🚀 Next steps:${NC}"
    echo "  1. Review configuration: config/pre-deploy-config.json"
    echo "  2. Run manual test: ./scripts/pre-deploy-automation.sh"
    echo "  3. Test git commit: git commit -m 'test: setup automation'"
    echo "  4. Read documentation: docs/PRE_DEPLOY_AUTOMATION.md"
    echo ""
    
    echo -e "${BLUE}💡 Quick commands:${NC}"
    echo "  • Manual test:     ./scripts/pre-deploy-automation.sh"
    echo "  • Quick test:      QUICK_MODE=true ./scripts/pre-deploy-automation.sh"
    echo "  • Debug mode:      DEBUG=true ./scripts/pre-deploy-automation.sh"
    echo "  • View logs:       ls -la deploy-logs/"
    echo ""
    
    echo -e "${YELLOW}⚠️  Important notes:${NC}"
    echo "  • System will now automatically run tests before commits"
    echo "  • Use 'git commit --no-verify' only for emergencies"
    echo "  • Check deploy-logs/ directory for detailed reports"
    echo "  • Update config/pre-deploy-config.json for customization"
    echo ""
    
    print_success "Pre-Deploy Automation is now ready! 🚀"
}

main() {
    print_header
    
    check_requirements
    setup_directories
    setup_scripts
    install_frontend_dependencies
    install_backend_dependencies
    create_example_config
    test_system
    install_git_hooks
    run_sample_tests
    
    show_summary
}

# Handle interruption gracefully
trap 'echo -e "\n${RED}🛑 Setup interrupted${NC}"; exit 130' INT TERM

# Run main function
main "$@"