#!/usr/bin/env node

/**
 * Pre-commit Hook
 * Runs before each commit to catch and fix common errors
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class PreCommitHook {
  constructor() {
    this.projectRoot = path.resolve(__dirname, '..');
    this.errors = [];
    this.fixes = [];
  }

  log(message, type = 'info') {
    const prefix = {
      info: 'ℹ️',
      success: '✅',
      warning: '⚠️',
      error: '❌'
    }[type];
    
    console.log(`${prefix} ${message}`);
  }

  async runLinting() {
    try {
      this.log('Running ESLint...');
      execSync('npm run lint', { 
        cwd: this.projectRoot, 
        stdio: 'pipe',
        encoding: 'utf8'
      });
      this.log('ESLint passed!', 'success');
      return true;
    } catch (error) {
      this.log('ESLint failed, attempting auto-fix...', 'warning');
      try {
        execSync('npm run lint -- --fix', { 
          cwd: this.projectRoot, 
          stdio: 'pipe',
          encoding: 'utf8'
        });
        this.log('ESLint auto-fix completed', 'success');
        return true;
      } catch (fixError) {
        this.log('ESLint auto-fix failed', 'error');
        return false;
      }
    }
  }

  async runTypeChecking() {
    try {
      this.log('Running TypeScript type checking...');
      execSync('npx tsc --noEmit', { 
        cwd: this.projectRoot, 
        stdio: 'pipe',
        encoding: 'utf8'
      });
      this.log('TypeScript check passed!', 'success');
      return true;
    } catch (error) {
      this.log('TypeScript check failed', 'error');
      this.errors.push('TypeScript type errors detected');
      return false;
    }
  }

  async runBuild() {
    try {
      this.log('Running production build...');
      execSync('npm run build', { 
        cwd: this.projectRoot, 
        stdio: 'pipe',
        encoding: 'utf8'
      });
      this.log('Build successful!', 'success');
      return true;
    } catch (error) {
      this.log('Build failed', 'error');
      this.errors.push('Build errors detected');
      return false;
    }
  }

  async runTests() {
    try {
      this.log('Running tests...');
      execSync('npm test -- --coverage --watchAll=false', { 
        cwd: this.projectRoot, 
        stdio: 'pipe',
        encoding: 'utf8'
      });
      this.log('Tests passed!', 'success');
      return true;
    } catch (error) {
      this.log('Tests failed', 'warning');
      this.errors.push('Test failures detected');
      return false;
    }
  }

  async checkDependencies() {
    try {
      this.log('Checking for security vulnerabilities...');
      const result = execSync('npm audit --audit-level=moderate', { 
        cwd: this.projectRoot, 
        stdio: 'pipe',
        encoding: 'utf8'
      });
      
      if (result.includes('found 0 vulnerabilities')) {
        this.log('No security vulnerabilities found', 'success');
        return true;
      } else {
        this.log('Security vulnerabilities found, attempting auto-fix...', 'warning');
        try {
          execSync('npm audit fix', { 
            cwd: this.projectRoot, 
            stdio: 'pipe',
            encoding: 'utf8'
          });
          this.log('Security vulnerabilities auto-fixed', 'success');
          return true;
        } catch (fixError) {
          this.log('Failed to auto-fix security vulnerabilities', 'error');
          return false;
        }
      }
    } catch (error) {
      this.log('Security check failed', 'error');
      return false;
    }
  }

  async checkBundleSize() {
    try {
      this.log('Checking bundle size...');
      execSync('npm run build', { 
        cwd: this.projectRoot, 
        stdio: 'pipe',
        encoding: 'utf8'
      });
      
      const buildPath = path.join(this.projectRoot, 'build', 'static', 'js');
      if (fs.existsSync(buildPath)) {
        const files = fs.readdirSync(buildPath);
        let totalSize = 0;
        
        files.forEach(file => {
          if (file.endsWith('.js')) {
            const filePath = path.join(buildPath, file);
            const stats = fs.statSync(filePath);
            totalSize += stats.size;
          }
        });
        
        const sizeInMB = (totalSize / 1024 / 1024).toFixed(2);
        this.log(`Bundle size: ${sizeInMB}MB`);
        
        if (totalSize > 2 * 1024 * 1024) { // 2MB limit
          this.log('Bundle size is too large!', 'warning');
          this.errors.push('Bundle size exceeds 2MB limit');
        } else {
          this.log('Bundle size is acceptable', 'success');
        }
      }
    } catch (error) {
      this.log('Bundle size check failed', 'error');
    }
  }

  async checkImportErrors() {
    this.log('Checking for import errors...');
    
    const srcPath = path.join(this.projectRoot, 'src');
    const files = this.getAllFiles(srcPath, ['.tsx', '.ts']);
    
    for (const file of files) {
      try {
        const content = fs.readFileSync(file, 'utf8');
        const importMatches = content.match(/import.*from\s+['"]([^'"]+)['"]/g);
        
        if (importMatches) {
          for (const match of importMatches) {
            const importPath = match.match(/from\s+['"]([^'"]+)['"]/)[1];
            
            if (!importPath.startsWith('.') && !importPath.startsWith('/')) {
              // External package
              continue;
            }
            
            const resolvedPath = path.resolve(path.dirname(file), importPath);
            const possibleExtensions = ['.tsx', '.ts', '.jsx', '.js', '/index.tsx', '/index.ts'];
            
            let found = false;
            for (const ext of possibleExtensions) {
              if (fs.existsSync(resolvedPath + ext)) {
                found = true;
                break;
              }
            }
            
            if (!found) {
              this.log(`Import error in ${file}: ${importPath}`, 'error');
              this.errors.push(`Import error: ${importPath} in ${file}`);
            }
          }
        }
      } catch (error) {
        this.log(`Error checking imports in ${file}: ${error.message}`, 'error');
      }
    }
  }

  getAllFiles(dir, extensions) {
    const files = [];
    
    if (fs.existsSync(dir)) {
      fs.readdirSync(dir).forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory()) {
          files.push(...this.getAllFiles(filePath, extensions));
        } else if (extensions.some(ext => file.endsWith(ext))) {
          files.push(filePath);
        }
      });
    }
    
    return files;
  }

  async run() {
    this.log('🚀 Running pre-commit checks...');
    
    const checks = [
      this.runLinting(),
      this.runTypeChecking(),
      this.checkDependencies(),
      this.checkImportErrors(),
      this.runTests(),
      this.runBuild(),
      this.checkBundleSize()
    ];
    
    const results = await Promise.all(checks);
    const allPassed = results.every(result => result !== false);
    
    if (allPassed) {
      this.log('All pre-commit checks passed!', 'success');
      process.exit(0);
    } else {
      this.log('Pre-commit checks failed!', 'error');
      this.log('Errors found:');
      this.errors.forEach((error, index) => {
        this.log(`${index + 1}. ${error}`);
      });
      this.log('Please fix these errors before committing.');
      process.exit(1);
    }
  }
}

// Run pre-commit hook
const hook = new PreCommitHook();
hook.run().catch(error => {
  console.error('❌ Pre-commit hook failed:', error);
  process.exit(1);
}); 