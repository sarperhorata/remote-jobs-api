#!/usr/bin/env node

/**
 * Pre-commit lint checker
 * This script runs before commits to catch lint errors early
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Running pre-commit lint checks...\n');

let hasErrors = false;
const errors = [];

// Function to run command and capture output
function runCommand(command, description) {
  try {
    console.log(`⏳ ${description}...`);
    const output = execSync(command, { 
      encoding: 'utf8', 
      stdio: 'pipe',
      cwd: process.cwd()
    });
    console.log(`✅ ${description} passed\n`);
    return { success: true, output };
  } catch (error) {
    console.log(`❌ ${description} failed\n`);
    hasErrors = true;
    errors.push({
      description,
      error: error.stdout || error.stderr || error.message
    });
    return { success: false, error: error.stdout || error.stderr || error.message };
  }
}

// Check if ESLint config exists
const eslintConfigPath = path.join(process.cwd(), '.eslintrc.js');
const eslintConfigExists = fs.existsSync(eslintConfigPath) || 
                          fs.existsSync(path.join(process.cwd(), '.eslintrc.json')) ||
                          fs.existsSync(path.join(process.cwd(), 'eslint.config.js'));

if (!eslintConfigExists) {
  console.log('⚠️  ESLint config not found, skipping lint checks');
} else {
  // Run ESLint
  const eslintResult = runCommand(
    'npx eslint src/ --ext .ts,.tsx --max-warnings 0',
    'ESLint check'
  );

  // Run TypeScript check
  const tsConfigPath = path.join(process.cwd(), 'tsconfig.json');
  if (fs.existsSync(tsConfigPath)) {
    runCommand(
      'npx tsc --noEmit --project tsconfig.json',
      'TypeScript type check'
    );
  } else {
    console.log('⚠️  tsconfig.json not found, skipping TypeScript check');
  }
}

// Check for common import errors
console.log('⏳ Checking for common import issues...');
const srcDir = path.join(process.cwd(), 'src');
if (fs.existsSync(srcDir)) {
  checkImportIssues(srcDir);
}

// Function to check for import issues
function checkImportIssues(dir) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory() && !file.startsWith('.')) {
      checkImportIssues(filePath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      checkFileImports(filePath);
    }
  });
}

function checkFileImports(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    
    // Common lucide-react icons that are often used
    const commonIcons = ['X', 'Check', 'Eye', 'EyeOff', 'Heart', 'ChevronDown', 'User', 'LogOut'];
    
    // Check if file uses any of these icons in JSX
    const usedIcons = [];
    const importedIcons = [];
    
    lines.forEach((line, index) => {
      // More precise check for icon usage in JSX (avoid false positives)
      commonIcons.forEach(icon => {
        // Only match actual JSX element usage, not comments or strings
        const jsxPattern = new RegExp(`<${icon}\\s*[^>]*>|<${icon}\\s*/>`, 'g');
        if (jsxPattern.test(line) && !line.trim().startsWith('//') && !line.trim().startsWith('*')) {
          usedIcons.push({ icon, line: index + 1, content: line.trim() });
        }
      });
      
      // Check for imports
      if (line.includes("from 'lucide-react'") || line.includes('from "lucide-react"')) {
        const match = line.match(/import\s*{\s*([^}]+)\s*}\s*from\s*['"]lucide-react['"]/);
        if (match) {
          const imports = match[1].split(',').map(imp => imp.trim());
          importedIcons.push(...imports);
        }
      }
    });
    
    // Check for missing imports (only if file actually uses JSX)
    const hasJsx = content.includes('<') && content.includes('>') && 
                  (content.includes('React') || content.includes('tsx') || filePath.includes('.tsx'));
    
    if (hasJsx) {
      usedIcons.forEach(({ icon, line, content }) => {
        if (!importedIcons.includes(icon)) {
          hasErrors = true;
          errors.push({
            description: 'Missing import',
            error: `${filePath}:${line} - Icon '${icon}' is used but not imported from lucide-react\n  > ${content}`
          });
        }
      });
    }
    
  } catch (error) {
    // Ignore files that can't be read
  }
}

console.log('✅ Import issues check completed\n');

// Summary
if (hasErrors) {
  console.log('❌ Pre-commit checks failed!\n');
  console.log('Errors found:\n');
  
  errors.forEach((error, index) => {
    console.log(`${index + 1}. ${error.description}:`);
    console.log(`   ${error.error}\n`);
  });
  
  console.log('Please fix these issues before committing.\n');
  console.log('Quick fixes:');
  console.log('- Add missing imports to your files');
  console.log('- Run: npx eslint src/ --ext .ts,.tsx --fix');
  console.log('- Check TypeScript errors with: npx tsc --noEmit\n');
  
  process.exit(1);
} else {
  console.log('✅ All pre-commit checks passed! Ready to commit.\n');
  process.exit(0);
} 