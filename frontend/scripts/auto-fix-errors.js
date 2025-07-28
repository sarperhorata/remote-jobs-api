#!/usr/bin/env node

/**
 * Auto Error Detection and Fixing Script
 * Automatically detects and fixes common deployment errors
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class AutoErrorFixer {
  constructor() {
    this.errors = [];
    this.fixes = [];
    this.projectRoot = path.resolve(__dirname, '..');
    this.srcPath = path.join(this.projectRoot, 'src');
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = {
      info: 'ℹ️',
      success: '✅',
      warning: '⚠️',
      error: '❌'
    }[type];
    
    console.log(`${prefix} [${timestamp}] ${message}`);
  }

  async runBuild() {
    try {
      this.log('Running build to detect errors...');
      execSync('npm run build', { 
        cwd: this.projectRoot, 
        stdio: 'pipe',
        encoding: 'utf8'
      });
      this.log('Build successful!', 'success');
      return true;
    } catch (error) {
      this.log('Build failed, analyzing errors...', 'warning');
      this.analyzeBuildError(error.stdout || error.stderr || error.message);
      return false;
    }
  }

  analyzeBuildError(errorOutput) {
    this.log('Analyzing build errors...');
    
    // Common error patterns
    const errorPatterns = [
      {
        pattern: /Module not found: Error: Can't resolve '([^']+)'/g,
        type: 'import_error',
        fix: this.fixImportError.bind(this)
      },
      {
        pattern: /Cannot find module '([^']+)'/g,
        type: 'module_not_found',
        fix: this.fixModuleNotFound.bind(this)
      },
      {
        pattern: /TS\d+: Property '([^']+)' does not exist on type '([^']+)'/g,
        type: 'typescript_property_error',
        fix: this.fixTypeScriptPropertyError.bind(this)
      },
      {
        pattern: /'([^']+)' is defined but never used/g,
        type: 'unused_variable',
        fix: this.fixUnusedVariable.bind(this)
      },
      {
        pattern: /Missing dependency '([^']+)' in useEffect/g,
        type: 'use_effect_dependency',
        fix: this.fixUseEffectDependency.bind(this)
      }
    ];

    for (const pattern of errorPatterns) {
      let match;
      while ((match = pattern.pattern.exec(errorOutput)) !== null) {
        this.errors.push({
          type: pattern.type,
          message: match[0],
          details: match.slice(1),
          fix: pattern.fix
        });
      }
    }
  }

  async fixImportError(error) {
    const [modulePath] = error.details;
    this.log(`Fixing import error for: ${modulePath}`);
    
    // Find the correct path
    const possiblePaths = this.findPossiblePaths(modulePath);
    
    for (const filePath of this.findFilesWithImport(modulePath)) {
      for (const possiblePath of possiblePaths) {
        if (fs.existsSync(path.resolve(this.srcPath, possiblePath))) {
          await this.updateImportInFile(filePath, modulePath, possiblePath);
          this.fixes.push(`Fixed import: ${modulePath} -> ${possiblePath} in ${filePath}`);
          break;
        }
      }
    }
  }

  async fixModuleNotFound(error) {
    const [moduleName] = error.details;
    this.log(`Fixing module not found: ${moduleName}`);
    
    // Check if it's a missing dependency
    if (this.isExternalModule(moduleName)) {
      await this.installMissingDependency(moduleName);
    } else {
      await this.fixImportError(error);
    }
  }

  async fixTypeScriptPropertyError(error) {
    const [propertyName, typeName] = error.details;
    this.log(`Fixing TypeScript property error: ${propertyName} on ${typeName}`);
    
    // Common property name fixes
    const propertyFixes = {
      'remote': 'isRemote',
      'id': '_id',
      'company_name': 'company.name',
      'job_type': 'jobType',
      'posted_date': 'postedAt'
    };
    
    if (propertyFixes[propertyName]) {
      await this.replacePropertyInFiles(propertyName, propertyFixes[propertyName]);
      this.fixes.push(`Fixed property: ${propertyName} -> ${propertyFixes[propertyName]}`);
    }
  }

  async fixUnusedVariable(error) {
    const [variableName] = error.details;
    this.log(`Fixing unused variable: ${variableName}`);
    
    // Remove unused imports/variables
    await this.removeUnusedVariable(variableName);
    this.fixes.push(`Removed unused variable: ${variableName}`);
  }

  async fixUseEffectDependency(error) {
    const [dependency] = error.details;
    this.log(`Fixing useEffect dependency: ${dependency}`);
    
    // Add missing dependency to useEffect
    await this.addUseEffectDependency(dependency);
    this.fixes.push(`Added useEffect dependency: ${dependency}`);
  }

  findPossiblePaths(modulePath) {
    const baseName = path.basename(modulePath);
    const possiblePaths = [
      modulePath,
      `${modulePath}.tsx`,
      `${modulePath}.ts`,
      `${modulePath}.jsx`,
      `${modulePath}.js`,
      `../components/${baseName}`,
      `../components/${baseName}.tsx`,
      `../components/${baseName}.ts`,
      `../components/${baseName}/index.tsx`,
      `../components/${baseName}/index.ts`,
      `../types/${baseName}`,
      `../types/${baseName}.ts`,
      `../utils/${baseName}`,
      `../utils/${baseName}.ts`,
      `../services/${baseName}`,
      `../services/${baseName}.ts`
    ];
    
    return possiblePaths;
  }

  findFilesWithImport(modulePath) {
    const files = [];
    this.walkDir(this.srcPath, (filePath) => {
      if (filePath.endsWith('.tsx') || filePath.endsWith('.ts')) {
        const content = fs.readFileSync(filePath, 'utf8');
        if (content.includes(`from '${modulePath}'`) || content.includes(`from "${modulePath}"`)) {
          files.push(filePath);
        }
      }
    });
    return files;
  }

  async updateImportInFile(filePath, oldImport, newImport) {
    try {
      let content = fs.readFileSync(filePath, 'utf8');
      content = content.replace(
        new RegExp(`from ['"]${oldImport}['"]`, 'g'),
        `from '${newImport}'`
      );
      fs.writeFileSync(filePath, content);
      this.log(`Updated import in ${filePath}`, 'success');
    } catch (error) {
      this.log(`Failed to update import in ${filePath}: ${error.message}`, 'error');
    }
  }

  isExternalModule(moduleName) {
    // Check if it's an external npm package
    return !moduleName.startsWith('.') && !moduleName.startsWith('/');
  }

  async installMissingDependency(moduleName) {
    try {
      this.log(`Installing missing dependency: ${moduleName}`);
      execSync(`npm install ${moduleName}`, { 
        cwd: this.projectRoot, 
        stdio: 'pipe' 
      });
      this.log(`Installed ${moduleName}`, 'success');
    } catch (error) {
      this.log(`Failed to install ${moduleName}: ${error.message}`, 'error');
    }
  }

  async replacePropertyInFiles(oldProperty, newProperty) {
    this.walkDir(this.srcPath, (filePath) => {
      if (filePath.endsWith('.tsx') || filePath.endsWith('.ts')) {
        try {
          let content = fs.readFileSync(filePath, 'utf8');
          const regex = new RegExp(`\\.${oldProperty}\\b`, 'g');
          if (regex.test(content)) {
            content = content.replace(regex, `.${newProperty}`);
            fs.writeFileSync(filePath, content);
            this.log(`Updated property in ${filePath}`, 'success');
          }
        } catch (error) {
          this.log(`Failed to update property in ${filePath}: ${error.message}`, 'error');
        }
      }
    });
  }

  async removeUnusedVariable(variableName) {
    this.walkDir(this.srcPath, (filePath) => {
      if (filePath.endsWith('.tsx') || filePath.endsWith('.ts')) {
        try {
          let content = fs.readFileSync(filePath, 'utf8');
          // Remove unused imports
          const importRegex = new RegExp(`import\\s+{[^}]*\\b${variableName}\\b[^}]*}\\s+from\\s+['"][^'"]+['"];?\\n?`, 'g');
          content = content.replace(importRegex, '');
          
          // Remove unused variable declarations
          const varRegex = new RegExp(`\\b(const|let|var)\\s+${variableName}\\s*=\\s*[^;]+;?\\n?`, 'g');
          content = content.replace(varRegex, '');
          
          fs.writeFileSync(filePath, content);
        } catch (error) {
          this.log(`Failed to remove unused variable in ${filePath}: ${error.message}`, 'error');
        }
      }
    });
  }

  async addUseEffectDependency(dependency) {
    this.walkDir(this.srcPath, (filePath) => {
      if (filePath.endsWith('.tsx') || filePath.endsWith('.ts')) {
        try {
          let content = fs.readFileSync(filePath, 'utf8');
          const useEffectRegex = /useEffect\s*\(\s*\(\)\s*=>\s*\{[^}]*\},\s*\[([^\]]*)\]\s*\)/g;
          content = content.replace(useEffectRegex, (match, deps) => {
            if (!deps.includes(dependency)) {
              const newDeps = deps ? `${deps}, ${dependency}` : dependency;
              return match.replace(`[${deps}]`, `[${newDeps}]`);
            }
            return match;
          });
          fs.writeFileSync(filePath, content);
        } catch (error) {
          this.log(`Failed to add useEffect dependency in ${filePath}: ${error.message}`, 'error');
        }
      }
    });
  }

  walkDir(dir, callback) {
    if (fs.existsSync(dir)) {
      fs.readdirSync(dir).forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        if (stat.isDirectory()) {
          this.walkDir(filePath, callback);
        } else {
          callback(filePath);
        }
      });
    }
  }

  async runLinting() {
    try {
      this.log('Running ESLint to check for code quality issues...');
      execSync('npm run lint', { 
        cwd: this.projectRoot, 
        stdio: 'pipe',
        encoding: 'utf8'
      });
      this.log('Linting passed!', 'success');
    } catch (error) {
      this.log('Linting failed, fixing auto-fixable issues...', 'warning');
      try {
        execSync('npm run lint -- --fix', { 
          cwd: this.projectRoot, 
          stdio: 'pipe',
          encoding: 'utf8'
        });
        this.log('Auto-fixed linting issues', 'success');
      } catch (fixError) {
        this.log(`Failed to auto-fix linting issues: ${fixError.message}`, 'error');
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
      this.log('Type checking passed!', 'success');
    } catch (error) {
      this.log('Type checking failed, analyzing errors...', 'warning');
      this.analyzeBuildError(error.stdout || error.stderr || error.message);
    }
  }

  async runAllFixes() {
    this.log('Starting automatic error fixing...');
    
    // Run all error fixes
    for (const error of this.errors) {
      try {
        await error.fix(error);
      } catch (fixError) {
        this.log(`Failed to fix error: ${error.message}`, 'error');
      }
    }
  }

  generateReport() {
    this.log('=== AUTO ERROR FIX REPORT ===');
    this.log(`Total errors detected: ${this.errors.length}`);
    this.log(`Total fixes applied: ${this.fixes.length}`);
    
    if (this.fixes.length > 0) {
      this.log('\nApplied fixes:');
      this.fixes.forEach((fix, index) => {
        this.log(`${index + 1}. ${fix}`);
      });
    }
    
    if (this.errors.length > this.fixes.length) {
      this.log('\nUnfixed errors:');
      this.errors.slice(this.fixes.length).forEach((error, index) => {
        this.log(`${index + 1}. ${error.message}`);
      });
    }
  }

  async run() {
    this.log('🚀 Starting Auto Error Detection and Fixing System');
    
    // Step 1: Run type checking
    await this.runTypeChecking();
    
    // Step 2: Run linting
    await this.runLinting();
    
    // Step 3: Run build
    const buildSuccess = await this.runBuild();
    
    // Step 4: Apply fixes if needed
    if (this.errors.length > 0) {
      await this.runAllFixes();
      
      // Step 5: Try build again
      if (!buildSuccess) {
        this.log('Retrying build after fixes...');
        await this.runBuild();
      }
    }
    
    // Step 6: Generate report
    this.generateReport();
    
    this.log('Auto error fixing completed!', 'success');
  }
}

// Run the auto fixer
const fixer = new AutoErrorFixer();
fixer.run().catch(error => {
  console.error('❌ Auto error fixing failed:', error);
  process.exit(1);
}); 