#!/bin/bash

# Auto Fix Common Issues Script
# Bu script GitHub workflow'larındaki yaygın problemleri otomatik olarak çözer

set -e

echo "🔧 Starting auto-fix process..."

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log fonksiyonu
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Frontend düzeltmeleri
fix_frontend() {
    log "Fixing frontend issues..."
    
    cd frontend
    
    # Linting düzeltmeleri
    if npm run lint:fix; then
        success "Frontend linting issues fixed"
    else
        warning "Some linting issues could not be auto-fixed"
    fi
    
    # Formatting düzeltmeleri
    if npm run format; then
        success "Frontend formatting issues fixed"
    else
        warning "Some formatting issues could not be auto-fixed"
    fi
    
    # Type checking
    if npm run type-check; then
        success "Frontend type checking passed"
    else
        warning "Frontend type checking issues found"
    fi
    
    cd ..
}

# Backend düzeltmeleri
fix_backend() {
    log "Fixing backend issues..."
    
    cd backend
    
    # Black formatting
    if command -v black &> /dev/null; then
        if black . --line-length=88 --quiet; then
            success "Backend formatting issues fixed"
        else
            warning "Some formatting issues could not be auto-fixed"
        fi
    else
        warning "Black not installed, skipping formatting"
    fi
    
    # isort import sorting
    if command -v isort &> /dev/null; then
        if isort . --profile=black --quiet; then
            success "Backend import sorting fixed"
        else
            warning "Some import sorting issues could not be auto-fixed"
        fi
    else
        warning "isort not installed, skipping import sorting"
    fi
    
    # autopep8 linting fixes
    if command -v autopep8 &> /dev/null; then
        if autopep8 --in-place --recursive --aggressive --aggressive .; then
            success "Backend linting issues fixed"
        else
            warning "Some linting issues could not be auto-fixed"
        fi
    else
        warning "autopep8 not installed, skipping linting fixes"
    fi
    
    cd ..
}

# Dependency güncellemeleri
update_dependencies() {
    log "Checking for outdated dependencies..."
    
    # Frontend dependencies
    cd frontend
    if npm outdated; then
        warning "Frontend has outdated dependencies"
    else
        success "Frontend dependencies are up to date"
    fi
    cd ..
    
    # Backend dependencies
    cd backend
    if pip list --outdated; then
        warning "Backend has outdated dependencies"
    else
        success "Backend dependencies are up to date"
    fi
    cd ..
}

# Security kontrolleri
security_check() {
    log "Running security checks..."
    
    # Frontend security audit
    cd frontend
    if npm audit --audit-level=moderate; then
        success "Frontend security audit passed"
    else
        warning "Frontend security issues found"
    fi
    cd ..
    
    # Backend security check
    cd backend
    if command -v safety &> /dev/null; then
        if safety check; then
            success "Backend security check passed"
        else
            warning "Backend security issues found"
        fi
    else
        warning "safety not installed, skipping backend security check"
    fi
    cd ..
}

# Test coverage analizi
analyze_coverage() {
    log "Analyzing test coverage..."
    
    # Frontend coverage
    cd frontend
    if [ -f "coverage/coverage-summary.json" ]; then
        coverage=$(cat coverage/coverage-summary.json | jq -r '.total.lines.pct' 2>/dev/null || echo "Unknown")
        log "Frontend coverage: ${coverage}%"
    else
        warning "Frontend coverage report not found"
    fi
    cd ..
    
    # Backend coverage
    cd backend
    if [ -f "htmlcov/index.html" ]; then
        success "Backend coverage report generated"
    else
        warning "Backend coverage report not found"
    fi
    cd ..
}

# Performance analizi
analyze_performance() {
    log "Analyzing performance..."
    
    # Frontend bundle size
    cd frontend
    if [ -d "build" ]; then
        bundle_size=$(du -sh build/ 2>/dev/null | cut -f1 || echo "Unknown")
        log "Frontend bundle size: ${bundle_size}"
    else
        warning "Frontend build directory not found"
    fi
    cd ..
}

# Ana fonksiyon
main() {
    # Debug modu kontrolü
    DEBUG_MODE=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            --debug)
                DEBUG_MODE=true
                set -x  # Debug modu aktif
                shift
                ;;
            --help)
                echo "Usage: $0 [--debug] [--help]"
                echo "  --debug    Enable debug mode"
                echo "  --help     Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    log "Starting auto-fix process for Buzz2Remote..."
    
    if [ "$DEBUG_MODE" = true ]; then
        log "Debug mode enabled"
    fi
    
    # Git status kontrolü
    if [ -n "$(git status --porcelain)" ]; then
        warning "Working directory has uncommitted changes"
    fi
    
    # Düzeltmeleri uygula
    fix_frontend
    fix_backend
    update_dependencies
    security_check
    analyze_coverage
    analyze_performance
    
    # Sonuç raporu
    log "Auto-fix process completed!"
    
    # Değişiklikleri göster
    if [ -n "$(git status --porcelain)" ]; then
        log "Changes made:"
        git status --porcelain
        success "Auto-fix completed with changes"
    else
        success "Auto-fix completed - no changes needed"
    fi
}

# Script'i çalıştır
main "$@" 