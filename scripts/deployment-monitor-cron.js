#!/usr/bin/env node

/**
 * Deployment Monitor & Auto-Fix System
 * Monitors Render, GitHub Actions, Netlify deployments and auto-fixes common issues
 * Runs every 15 minutes via cron job
 */

const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const util = require('util');

const execAsync = util.promisify(exec);

// Configuration
const CONFIG = {
  RENDER_SERVICE_ID: process.env.RENDER_SERVICE_ID || 'buzz2remote-backend',
  RENDER_API_KEY: process.env.RENDER_API_KEY,
  NETLIFY_SITE_ID: process.env.NETLIFY_SITE_ID,
  NETLIFY_ACCESS_TOKEN: process.env.NETLIFY_ACCESS_TOKEN,
  GITHUB_TOKEN: process.env.GITHUB_TOKEN,
  GITHUB_REPO: 'sarperhorata/remote-jobs-api',
  CHECK_INTERVAL: 15 * 60 * 1000, // 15 minutes
  MAX_RETRIES: 3,
  LOG_FILE: path.join(__dirname, '../logs/deployment-monitor.log')
};

// Logging utility
class Logger {
  static async log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level}] ${message}`;
    
    console.log(logMessage);
    
    try {
      await fs.appendFile(CONFIG.LOG_FILE, logMessage + '\n');
    } catch (error) {
      console.error('Failed to write to log file:', error.message);
    }
  }

  static async error(message) {
    await this.log(message, 'ERROR');
  }

  static async warn(message) {
    await this.log(message, 'WARN');
  }

  static async info(message) {
    await this.log(message, 'INFO');
  }
}

// Deployment status checker
class DeploymentMonitor {
  constructor() {
    this.lastCheck = new Date();
    this.issues = [];
  }

  async checkRenderDeployment() {
    try {
      if (!CONFIG.RENDER_API_KEY) {
        await Logger.warn('Render API key not configured, skipping Render check');
        return;
      }

      const response = await axios.get(
        `https://api.render.com/v1/services/${CONFIG.RENDER_SERVICE_ID}`,
        {
          headers: {
            'Authorization': `Bearer ${CONFIG.RENDER_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const service = response.data;
      
      if (service.status === 'failed') {
        this.issues.push({
          platform: 'Render',
          type: 'deployment_failed',
          message: `Render deployment failed: ${service.lastDeploy?.error || 'Unknown error'}`,
          severity: 'high'
        });
      } else if (service.status === 'suspended') {
        this.issues.push({
          platform: 'Render',
          type: 'service_suspended',
          message: 'Render service is suspended',
          severity: 'critical'
        });
      }

      await Logger.info(`Render status: ${service.status}`);
      return service;

    } catch (error) {
      await Logger.error(`Render check failed: ${error.message}`);
      this.issues.push({
        platform: 'Render',
        type: 'api_error',
        message: `Render API error: ${error.message}`,
        severity: 'medium'
      });
    }
  }

  async checkGitHubActions() {
    try {
      if (!CONFIG.GITHUB_TOKEN) {
        await Logger.warn('GitHub token not configured, skipping GitHub Actions check');
        return;
      }

      const response = await axios.get(
        `https://api.github.com/repos/${CONFIG.GITHUB_REPO}/actions/runs?per_page=5`,
        {
          headers: {
            'Authorization': `token ${CONFIG.GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json'
          }
        }
      );

      const runs = response.data.workflow_runs;
      
      for (const run of runs) {
        if (run.conclusion === 'failure') {
          this.issues.push({
            platform: 'GitHub Actions',
            type: 'workflow_failed',
            message: `Workflow ${run.name} failed: ${run.head_branch}`,
            severity: 'high',
            details: {
              workflow_id: run.id,
              branch: run.head_branch,
              commit: run.head_sha
            }
          });
        }
      }

      await Logger.info(`GitHub Actions: ${runs.length} recent runs checked`);
      return runs;

    } catch (error) {
      await Logger.error(`GitHub Actions check failed: ${error.message}`);
      this.issues.push({
        platform: 'GitHub Actions',
        type: 'api_error',
        message: `GitHub API error: ${error.message}`,
        severity: 'medium'
      });
    }
  }

  async checkNetlifyDeployment() {
    try {
      if (!CONFIG.NETLIFY_ACCESS_TOKEN || !CONFIG.NETLIFY_SITE_ID) {
        await Logger.warn('Netlify credentials not configured, skipping Netlify check');
        return;
      }

      const response = await axios.get(
        `https://api.netlify.com/api/v1/sites/${CONFIG.NETLIFY_SITE_ID}/deploys?per_page=5`,
        {
          headers: {
            'Authorization': `Bearer ${CONFIG.NETLIFY_ACCESS_TOKEN}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const deploys = response.data;
      
      for (const deploy of deploys) {
        if (deploy.state === 'error') {
          this.issues.push({
            platform: 'Netlify',
            type: 'deployment_failed',
            message: `Netlify deployment failed: ${deploy.error_message || 'Unknown error'}`,
            severity: 'high',
            details: {
              deploy_id: deploy.id,
              branch: deploy.branch
            }
          });
        }
      }

      await Logger.info(`Netlify: ${deploys.length} recent deploys checked`);
      return deploys;

    } catch (error) {
      await Logger.error(`Netlify check failed: ${error.message}`);
      this.issues.push({
        platform: 'Netlify',
        type: 'api_error',
        message: `Netlify API error: ${error.message}`,
        severity: 'medium'
      });
    }
  }

  async checkLocalHealth() {
    try {
      // Check if backend is running locally
      const { stdout } = await execAsync('lsof -i :8001');
      if (!stdout.includes('8001')) {
        this.issues.push({
          platform: 'Local',
          type: 'backend_not_running',
          message: 'Backend not running on port 8001',
          severity: 'medium'
        });
      }

      // Check if frontend is running locally
      const { stdout: frontendCheck } = await execAsync('lsof -i :3002');
      if (!frontendCheck.includes('3002')) {
        this.issues.push({
          platform: 'Local',
          type: 'frontend_not_running',
          message: 'Frontend not running on port 3002',
          severity: 'medium'
        });
      }

      await Logger.info('Local health check completed');

    } catch (error) {
      await Logger.error(`Local health check failed: ${error.message}`);
    }
  }
}

// Auto-fix system
class AutoFixer {
  constructor() {
    this.fixesApplied = [];
  }

  async fixRenderIssues(issues) {
    const renderIssues = issues.filter(issue => issue.platform === 'Render');
    
    for (const issue of renderIssues) {
      if (issue.type === 'deployment_failed') {
        await this.retryRenderDeployment();
      } else if (issue.type === 'service_suspended') {
        await this.unsuspendRenderService();
      }
    }
  }

  async fixGitHubIssues(issues) {
    const githubIssues = issues.filter(issue => issue.platform === 'GitHub Actions');
    
    for (const issue of githubIssues) {
      if (issue.type === 'workflow_failed') {
        await this.retryGitHubWorkflow(issue.details.workflow_id);
      }
    }
  }

  async fixNetlifyIssues(issues) {
    const netlifyIssues = issues.filter(issue => issue.platform === 'Netlify');
    
    for (const issue of netlifyIssues) {
      if (issue.type === 'deployment_failed') {
        await this.retryNetlifyDeployment();
      }
    }
  }

  async fixLocalIssues(issues) {
    const localIssues = issues.filter(issue => issue.platform === 'Local');
    
    for (const issue of localIssues) {
      if (issue.type === 'backend_not_running') {
        await this.startBackend();
      } else if (issue.type === 'frontend_not_running') {
        await this.startFrontend();
      }
    }
  }

  async retryRenderDeployment() {
    try {
      if (!CONFIG.RENDER_API_KEY) return;

      await axios.post(
        `https://api.render.com/v1/services/${CONFIG.RENDER_SERVICE_ID}/deploys`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${CONFIG.RENDER_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );

      await Logger.info('Triggered new Render deployment');
      this.fixesApplied.push('render_deployment_retry');

    } catch (error) {
      await Logger.error(`Failed to retry Render deployment: ${error.message}`);
    }
  }

  async unsuspendRenderService() {
    try {
      if (!CONFIG.RENDER_API_KEY) return;

      await axios.patch(
        `https://api.render.com/v1/services/${CONFIG.RENDER_SERVICE_ID}`,
        { suspend: false },
        {
          headers: {
            'Authorization': `Bearer ${CONFIG.RENDER_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );

      await Logger.info('Unsuspended Render service');
      this.fixesApplied.push('render_unsuspend');

    } catch (error) {
      await Logger.error(`Failed to unsuspend Render service: ${error.message}`);
    }
  }

  async retryGitHubWorkflow(workflowId) {
    try {
      if (!CONFIG.GITHUB_TOKEN) return;

      await axios.post(
        `https://api.github.com/repos/${CONFIG.GITHUB_REPO}/actions/runs/${workflowId}/rerun`,
        {},
        {
          headers: {
            'Authorization': `token ${CONFIG.GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json'
          }
        }
      );

      await Logger.info(`Retried GitHub workflow ${workflowId}`);
      this.fixesApplied.push(`github_workflow_retry_${workflowId}`);

    } catch (error) {
      await Logger.error(`Failed to retry GitHub workflow: ${error.message}`);
    }
  }

  async retryNetlifyDeployment() {
    try {
      if (!CONFIG.NETLIFY_ACCESS_TOKEN || !CONFIG.NETLIFY_SITE_ID) return;

      await axios.post(
        `https://api.netlify.com/api/v1/sites/${CONFIG.NETLIFY_SITE_ID}/deploys`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${CONFIG.NETLIFY_ACCESS_TOKEN}`,
            'Content-Type': 'application/json'
          }
        }
      );

      await Logger.info('Triggered new Netlify deployment');
      this.fixesApplied.push('netlify_deployment_retry');

    } catch (error) {
      await Logger.error(`Failed to retry Netlify deployment: ${error.message}`);
    }
  }

  async startBackend() {
    try {
      await execAsync('cd backend && python main.py', { 
        cwd: path.join(__dirname, '..'),
        detached: true 
      });
      
      await Logger.info('Started backend service');
      this.fixesApplied.push('backend_started');

    } catch (error) {
      await Logger.error(`Failed to start backend: ${error.message}`);
    }
  }

  async startFrontend() {
    try {
      await execAsync('cd frontend && npm start', { 
        cwd: path.join(__dirname, '..'),
        detached: true 
      });
      
      await Logger.info('Started frontend service');
      this.fixesApplied.push('frontend_started');

    } catch (error) {
      await Logger.error(`Failed to start frontend: ${error.message}`);
    }
  }
}

// Main monitoring system
class DeploymentMonitoringSystem {
  constructor() {
    this.monitor = new DeploymentMonitor();
    this.fixer = new AutoFixer();
    this.isRunning = false;
  }

  async start() {
    if (this.isRunning) {
      await Logger.warn('Monitoring system is already running');
      return;
    }

    this.isRunning = true;
    await Logger.info('🚀 Deployment Monitoring System started');

    // Create logs directory if it doesn't exist
    try {
      await fs.mkdir(path.dirname(CONFIG.LOG_FILE), { recursive: true });
    } catch (error) {
      // Directory already exists
    }

    // Initial check
    await this.performCheck();

    // Set up interval
    this.interval = setInterval(async () => {
      await this.performCheck();
    }, CONFIG.CHECK_INTERVAL);

    // Handle graceful shutdown
    process.on('SIGINT', async () => {
      await this.stop();
    });

    process.on('SIGTERM', async () => {
      await this.stop();
    });
  }

  async stop() {
    if (this.interval) {
      clearInterval(this.interval);
    }
    this.isRunning = false;
    await Logger.info('🛑 Deployment Monitoring System stopped');
    process.exit(0);
  }

  async performCheck() {
    try {
      await Logger.info('🔍 Starting deployment health check...');
      
      // Reset issues
      this.monitor.issues = [];
      this.fixer.fixesApplied = [];

      // Perform all checks
      await Promise.all([
        this.monitor.checkRenderDeployment(),
        this.monitor.checkGitHubActions(),
        this.monitor.checkNetlifyDeployment(),
        this.monitor.checkLocalHealth()
      ]);

      // Report issues
      if (this.monitor.issues.length > 0) {
        await Logger.warn(`⚠️ Found ${this.monitor.issues.length} issues:`);
        
        for (const issue of this.monitor.issues) {
          await Logger.warn(`  - ${issue.platform}: ${issue.message} (${issue.severity})`);
        }

        // Apply fixes
        await this.applyFixes();
      } else {
        await Logger.info('✅ All deployments are healthy!');
      }

      this.monitor.lastCheck = new Date();

    } catch (error) {
      await Logger.error(`❌ Health check failed: ${error.message}`);
    }
  }

  async applyFixes() {
    try {
      await Logger.info('🔧 Applying automatic fixes...');

      await Promise.all([
        this.fixer.fixRenderIssues(this.monitor.issues),
        this.fixer.fixGitHubIssues(this.monitor.issues),
        this.fixer.fixNetlifyIssues(this.monitor.issues),
        this.fixer.fixLocalIssues(this.monitor.issues)
      ]);

      if (this.fixer.fixesApplied.length > 0) {
        await Logger.info(`✅ Applied ${this.fixer.fixesApplied.length} fixes:`);
        for (const fix of this.fixer.fixesApplied) {
          await Logger.info(`  - ${fix}`);
        }
      } else {
        await Logger.warn('⚠️ No automatic fixes could be applied');
      }

    } catch (error) {
      await Logger.error(`❌ Failed to apply fixes: ${error.message}`);
    }
  }

  async generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      lastCheck: this.monitor.lastCheck,
      issuesFound: this.monitor.issues.length,
      fixesApplied: this.fixer.fixesApplied.length,
      issues: this.monitor.issues,
      fixes: this.fixer.fixesApplied
    };

    const reportPath = path.join(__dirname, '../logs/deployment-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    return report;
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  const system = new DeploymentMonitoringSystem();

  if (args.includes('--once')) {
    // Run once and exit
    await system.performCheck();
    const report = await system.generateReport();
    console.log('📊 Deployment Report:', JSON.stringify(report, null, 2));
    process.exit(0);
  } else if (args.includes('--report')) {
    // Generate report only
    const report = await system.generateReport();
    console.log('📊 Deployment Report:', JSON.stringify(report, null, 2));
    process.exit(0);
  } else {
    // Start continuous monitoring
    await system.start();
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(async (error) => {
    await Logger.error(`❌ Fatal error: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { DeploymentMonitoringSystem, DeploymentMonitor, AutoFixer }; 