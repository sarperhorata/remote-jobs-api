#!/usr/bin/env node

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const chokidar = require('chokidar');

class TestAutomation {
  constructor() {
    this.isRunning = false;
    this.testQueue = [];
    this.watchMode = false;
    this.config = {
      testTypes: ['unit', 'integration', 'performance', 'e2e'],
      watchPatterns: [
        'src/**/*.{js,jsx,ts,tsx}',
        '!src/**/*.test.{js,jsx,ts,tsx}',
        '!src/**/*.spec.{js,jsx,ts,tsx}',
        '!src/**/__tests__/**',
        '!src/**/__mocks__/**',
      ],
      coverageThreshold: {
        global: 80,
        components: 85,
        services: 90,
        utils: 95,
      },
      retryAttempts: 3,
      parallelTests: true,
    };
  }

  log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const colors = {
      info: '\x1b[36m', // Cyan
      success: '\x1b[32m', // Green
      warning: '\x1b[33m', // Yellow
      error: '\x1b[31m', // Red
      reset: '\x1b[0m',
    };
    
    console.log(`${colors[type]}[${timestamp}] ${message}${colors.reset}`);
  }

  async runCommand(command, options = {}) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, options.args || [], {
        stdio: options.silent ? 'pipe' : 'inherit',
        shell: true,
        ...options,
      });

      let stdout = '';
      let stderr = '';

      if (options.silent) {
        child.stdout.on('data', (data) => {
          stdout += data.toString();
        });
        child.stderr.on('data', (data) => {
          stderr += data.toString();
        });
      }

      child.on('close', (code) => {
        if (code === 0) {
          resolve({ code, stdout, stderr });
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });

      child.on('error', (error) => {
        reject(error);
      });
    });
  }

  async runUnitTests() {
    this.log('🧪 Running unit tests...', 'info');
    try {
      await this.runCommand('npm', { args: ['test', '--', '--coverage', '--watchAll=false', '--passWithNoTests'] });
      this.log('✅ Unit tests completed successfully', 'success');
      return true;
    } catch (error) {
      this.log(`❌ Unit tests failed: ${error.message}`, 'error');
      return false;
    }
  }

  async runIntegrationTests() {
    this.log('🔗 Running integration tests...', 'info');
    try {
      await this.runCommand('npm', { args: ['run', 'test:integration'] });
      this.log('✅ Integration tests completed successfully', 'success');
      return true;
    } catch (error) {
      this.log(`❌ Integration tests failed: ${error.message}`, 'error');
      return false;
    }
  }

  async runPerformanceTests() {
    this.log('⚡ Running performance tests...', 'info');
    try {
      await this.runCommand('npm', { args: ['run', 'test:performance'] });
      this.log('✅ Performance tests completed successfully', 'success');
      return true;
    } catch (error) {
      this.log(`❌ Performance tests failed: ${error.message}`, 'error');
      return false;
    }
  }

  async runE2ETests() {
    this.log('🌐 Running E2E tests...', 'info');
    try {
      // Start development server
      const serverProcess = spawn('npm', ['start'], {
        stdio: 'pipe',
        detached: true,
      });

      // Wait for server to start
      await new Promise(resolve => setTimeout(resolve, 10000));

      // Run E2E tests
      await this.runCommand('npm', { args: ['run', 'test:e2e'] });

      // Kill server
      process.kill(-serverProcess.pid);

      this.log('✅ E2E tests completed successfully', 'success');
      return true;
    } catch (error) {
      this.log(`❌ E2E tests failed: ${error.message}`, 'error');
      return false;
    }
  }

  async generateCoverageReport() {
    this.log('📊 Generating coverage report...', 'info');
    try {
      await this.runCommand('node', { args: ['src/__tests__/coverage-report.ts'] });
      this.log('✅ Coverage report generated', 'success');
      return true;
    } catch (error) {
      this.log(`❌ Coverage report generation failed: ${error.message}`, 'error');
      return false;
    }
  }

  async runLinting() {
    this.log('🔍 Running linting...', 'info');
    try {
      await this.runCommand('npm', { args: ['run', 'lint'] });
      this.log('✅ Linting completed successfully', 'success');
      return true;
    } catch (error) {
      this.log(`❌ Linting failed: ${error.message}`, 'error');
      return false;
    }
  }

  async runTypeChecking() {
    this.log('🔧 Running type checking...', 'info');
    try {
      await this.runCommand('npm', { args: ['run', 'type-check'] });
      this.log('✅ Type checking completed successfully', 'success');
      return true;
    } catch (error) {
      this.log(`❌ Type checking failed: ${error.message}`, 'error');
      return false;
    }
  }

  async runAllTests() {
    this.log('🚀 Starting comprehensive test suite...', 'info');
    
    const results = {
      linting: false,
      typeChecking: false,
      unitTests: false,
      integrationTests: false,
      performanceTests: false,
      e2eTests: false,
      coverageReport: false,
    };

    // Run pre-tests
    results.linting = await this.runLinting();
    results.typeChecking = await this.runTypeChecking();

    if (!results.linting || !results.typeChecking) {
      this.log('❌ Pre-tests failed, stopping execution', 'error');
      return results;
    }

    // Run tests
    if (this.config.parallelTests) {
      const testPromises = [
        this.runUnitTests().then(result => { results.unitTests = result; }),
        this.runIntegrationTests().then(result => { results.integrationTests = result; }),
        this.runPerformanceTests().then(result => { results.performanceTests = result; }),
      ];

      await Promise.all(testPromises);
    } else {
      results.unitTests = await this.runUnitTests();
      results.integrationTests = await this.runIntegrationTests();
      results.performanceTests = await this.runPerformanceTests();
    }

    // Run E2E tests last (requires server)
    results.e2eTests = await this.runE2ETests();

    // Generate coverage report
    results.coverageReport = await this.generateCoverageReport();

    // Print summary
    this.printTestSummary(results);

    return results;
  }

  printTestSummary(results) {
    this.log('\n📋 Test Summary', 'info');
    this.log('==============', 'info');
    
    const testTypes = [
      { name: 'Linting', key: 'linting' },
      { name: 'Type Checking', key: 'typeChecking' },
      { name: 'Unit Tests', key: 'unitTests' },
      { name: 'Integration Tests', key: 'integrationTests' },
      { name: 'Performance Tests', key: 'performanceTests' },
      { name: 'E2E Tests', key: 'e2eTests' },
      { name: 'Coverage Report', key: 'coverageReport' },
    ];

    testTypes.forEach(test => {
      const status = results[test.key] ? '✅' : '❌';
      this.log(`${status} ${test.name}`, results[test.key] ? 'success' : 'error');
    });

    const passedTests = Object.values(results).filter(Boolean).length;
    const totalTests = Object.keys(results).length;
    const successRate = Math.round((passedTests / totalTests) * 100);

    this.log(`\n🎯 Success Rate: ${successRate}% (${passedTests}/${totalTests})`, successRate >= 80 ? 'success' : 'warning');
  }

  startWatchMode() {
    this.log('👀 Starting watch mode...', 'info');
    this.watchMode = true;

    const watcher = chokidar.watch(this.config.watchPatterns, {
      ignored: /node_modules/,
      persistent: true,
    });

    let debounceTimer;
    watcher.on('change', (path) => {
      this.log(`📝 File changed: ${path}`, 'info');
      
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(async () => {
        if (!this.isRunning) {
          this.isRunning = true;
          this.log('🔄 Running tests due to file changes...', 'info');
          
          await this.runUnitTests();
          await this.runIntegrationTests();
          
          this.isRunning = false;
          this.log('✅ Watch mode tests completed', 'success');
        }
      }, 1000);
    });

    this.log('👀 Watching for file changes...', 'info');
  }

  async retryFailedTests(testType, maxAttempts = this.config.retryAttempts) {
    this.log(`🔄 Retrying ${testType} tests (attempts: ${maxAttempts})...`, 'warning');
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      this.log(`Attempt ${attempt}/${maxAttempts}`, 'info');
      
      let success = false;
      switch (testType) {
        case 'unit':
          success = await this.runUnitTests();
          break;
        case 'integration':
          success = await this.runIntegrationTests();
          break;
        case 'performance':
          success = await this.runPerformanceTests();
          break;
        case 'e2e':
          success = await this.runE2ETests();
          break;
      }

      if (success) {
        this.log(`✅ ${testType} tests passed on attempt ${attempt}`, 'success');
        return true;
      }

      if (attempt < maxAttempts) {
        this.log(`⏳ Waiting 5 seconds before retry...`, 'warning');
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }

    this.log(`❌ ${testType} tests failed after ${maxAttempts} attempts`, 'error');
    return false;
  }

  async runSpecificTests(testTypes) {
    this.log(`🎯 Running specific tests: ${testTypes.join(', ')}`, 'info');
    
    const results = {};
    
    for (const testType of testTypes) {
      switch (testType) {
        case 'unit':
          results.unit = await this.runUnitTests();
          break;
        case 'integration':
          results.integration = await this.runIntegrationTests();
          break;
        case 'performance':
          results.performance = await this.runPerformanceTests();
          break;
        case 'e2e':
          results.e2e = await this.runE2ETests();
          break;
        case 'lint':
          results.lint = await this.runLinting();
          break;
        case 'type':
          results.type = await this.runTypeChecking();
          break;
        case 'coverage':
          results.coverage = await this.generateCoverageReport();
          break;
        default:
          this.log(`❌ Unknown test type: ${testType}`, 'error');
      }
    }

    return results;
  }
}

// CLI Interface
async function main() {
  const automation = new TestAutomation();
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
🚀 Test Automation Tool

Usage:
  node test-automation.js [command] [options]

Commands:
  all                    Run all tests
  unit                   Run unit tests only
  integration            Run integration tests only
  performance            Run performance tests only
  e2e                    Run E2E tests only
  watch                  Start watch mode
  coverage               Generate coverage report
  lint                   Run linting
  type                   Run type checking
  retry [test-type]      Retry failed tests

Options:
  --parallel             Run tests in parallel
  --retry [attempts]     Number of retry attempts (default: 3)
  --watch                Enable watch mode

Examples:
  node test-automation.js all
  node test-automation.js unit integration
  node test-automation.js watch
  node test-automation.js retry unit --retry 5
    `);
    return;
  }

  const command = args[0];
  const options = args.slice(1);

  try {
    switch (command) {
      case 'all':
        await automation.runAllTests();
        break;
      case 'unit':
        await automation.runUnitTests();
        break;
      case 'integration':
        await automation.runIntegrationTests();
        break;
      case 'performance':
        await automation.runPerformanceTests();
        break;
      case 'e2e':
        await automation.runE2ETests();
        break;
      case 'watch':
        automation.startWatchMode();
        break;
      case 'coverage':
        await automation.generateCoverageReport();
        break;
      case 'lint':
        await automation.runLinting();
        break;
      case 'type':
        await automation.runTypeChecking();
        break;
      case 'retry':
        const testType = options[0];
        const retryAttempts = parseInt(options.find(opt => opt.startsWith('--retry='))?.split('=')[1]) || 3;
        await automation.retryFailedTests(testType, retryAttempts);
        break;
      default:
        // Run specific test types
        await automation.runSpecificTests([command, ...options]);
    }
  } catch (error) {
    automation.log(`❌ Error: ${error.message}`, 'error');
    process.exit(1);
  }
}

// Run if this file is executed directly
if (require.main === module) {
  main();
}

module.exports = TestAutomation;