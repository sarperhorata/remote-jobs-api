#!/usr/bin/env node

/**
 * Deployment Monitor & Auto-Fix System
 * Monitors Render, GitHub Actions, Netlify deployments and auto-fixes common issues
 * Runs every 15 minutes via cron job or Render cron service
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
  GITHUB_REPO: process.env.GITHUB_REPO || 'sarperhorata/remote-jobs-api',
  CHECK_INTERVAL: parseInt(process.env.CHECK_INTERVAL) || 15 * 60 * 1000, // 15 minutes
  MAX_RETRIES: parseInt(process.env.MAX_RETRIES) || 3,
  LOG_FILE: process.env.LOG_FILE || path.join(__dirname, '../logs/deployment-monitor.log'),
  IS_RENDER_ENVIRONMENT: process.env.RENDER || false,
  WEBHOOK_URL: process.env.WEBHOOK_URL, // For external notifications
  TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN,
  TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID
};

// Logging utility
class Logger {
  static async log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level}] ${message}`;
    
    console.log(logMessage);
    
    try {
      // Ensure logs directory exists
      await fs.mkdir(path.dirname(CONFIG.LOG_FILE), { recursive: true });
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

// Notification system
class NotificationManager {
  static async sendWebhookNotification(message, severity = 'info') {
    if (!CONFIG.WEBHOOK_URL) return;

    try {
      await axios.post(CONFIG.WEBHOOK_URL, {
        text: message,
        severity: severity,
        timestamp: new Date().toISOString(),
        environment: CONFIG.IS_RENDER_ENVIRONMENT ? 'production' : 'development'
      });
    } catch (error) {
      await Logger.error(`Failed to send webhook notification: ${error.message}`);
    }
  }

  static async sendTelegramNotification(message) {
    // DISABLED - only log instead of sending to Telegram
    await Logger.info(`TELEGRAM NOTIFICATION (DISABLED): ${message}`);
    return;
    
    // Original code commented out to disable Telegram notifications
    // if (!CONFIG.TELEGRAM_BOT_TOKEN || !CONFIG.TELEGRAM_CHAT_ID) return;

    // try {
    //   const telegramUrl = `https://api.telegram.org/bot${CONFIG.TELEGRAM_BOT_TOKEN}/sendMessage`;
    //   await axios.post(telegramUrl, {
    //     chat_id: CONFIG.TELEGRAM_CHAT_ID,
    //     text: message,
    //     parse_mode: 'HTML'
    //   });
    // } catch (error) {
    //   await Logger.error(`Failed to send Telegram notification: ${error.message}`);
    // }
  }

  static async sendNotification(message, severity = 'info') {
    await Promise.all([
      this.sendWebhookNotification(message, severity),
      this.sendTelegramNotification(message)
    ]);
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
          },
          timeout: 10000
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
          },
          timeout: 10000
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
          },
          timeout: 10000
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
    // Skip local health check if running on Render
    if (CONFIG.IS_RENDER_ENVIRONMENT) {
      await Logger.info('Skipping local health check (running on Render)');
      return;
    }

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

  async checkExternalHealth() {
    try {
      // Check if the main application is responding
      const response = await axios.get('https://buzz2remote.onrender.com/health', {
        timeout: 10000
      });
      
      if (response.status !== 200) {
        this.issues.push({
          platform: 'External',
          type: 'health_check_failed',
          message: `External health check failed: ${response.status}`,
          severity: 'high'
        });
      }

      await Logger.info('External health check completed');

    } catch (error) {
      await Logger.error(`External health check failed: ${error.message}`);
      this.issues.push({
        platform: 'External',
        type: 'health_check_failed',
        message: `External health check error: ${error.message}`,
        severity: 'high'
      });
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
    if (CONFIG.IS_RENDER_ENVIRONMENT) return; // Skip local fixes on Render

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
          },
          timeout: 10000
        }
      );

      await Logger.info('Triggered new Render deployment');
      await NotificationManager.sendNotification('🔄 Render deployment retry triggered', 'info');
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
          },
          timeout: 10000
        }
      );

      await Logger.info('Unsuspended Render service');
      await NotificationManager.sendNotification('✅ Render service unsuspended', 'info');
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
          },
          timeout: 10000
        }
      );

      await Logger.info(`Retried GitHub workflow ${workflowId}`);
      await NotificationManager.sendNotification(`🔄 GitHub workflow ${workflowId} retry triggered`, 'info');
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
          },
          timeout: 10000
        }
      );

      await Logger.info('Triggered new Netlify deployment');
      await NotificationManager.sendNotification('🔄 Netlify deployment retry triggered', 'info');
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
    await NotificationManager.sendNotification('🚀 Deployment Monitor started', 'info');

    // Create logs directory if it doesn't exist
    try {
      await fs.mkdir(path.dirname(CONFIG.LOG_FILE), { recursive: true });
    } catch (error) {
      // Directory already exists
    }

    // Initial check
    await this.performCheck();

    // Set up interval (only if not running on external cron)
    if (!process.env.EXTERNAL_CRON) {
      this.interval = setInterval(async () => {
        await this.performCheck();
      }, CONFIG.CHECK_INTERVAL);
    }

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
    await NotificationManager.sendNotification('🛑 Deployment Monitor stopped', 'warn');
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
        this.monitor.checkLocalHealth(),
        this.monitor.checkExternalHealth()
      ]);

      // Report issues
      if (this.monitor.issues.length > 0) {
        await Logger.warn(`⚠️ Found ${this.monitor.issues.length} issues:`);
        
        for (const issue of this.monitor.issues) {
          await Logger.warn(`  - ${issue.platform}: ${issue.message} (${issue.severity})`);
        }

        // Send notification for critical issues
        const criticalIssues = this.monitor.issues.filter(issue => issue.severity === 'critical');
        if (criticalIssues.length > 0) {
          await NotificationManager.sendNotification(
            `🚨 Critical deployment issues detected: ${criticalIssues.length} issues found`,
            'critical'
          );
        }

        // Apply fixes
        await this.applyFixes();
      } else {
        await Logger.info('✅ All deployments are healthy!');
        await NotificationManager.sendNotification('✅ All deployments are healthy!', 'info');
      }

      this.monitor.lastCheck = new Date();

    } catch (error) {
      await Logger.error(`❌ Health check failed: ${error.message}`);
      await NotificationManager.sendNotification(`❌ Health check failed: ${error.message}`, 'error');
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
        await NotificationManager.sendNotification(
          `🔧 Applied ${this.fixer.fixesApplied.length} automatic fixes`,
          'info'
        );
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
      fixes: this.fixer.fixesApplied,
      environment: CONFIG.IS_RENDER_ENVIRONMENT ? 'production' : 'development'
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
    // Run once and exit (for external cron services)
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
    await NotificationManager.sendNotification(`❌ Fatal error: ${error.message}`, 'error');
    process.exit(1);
  });
}

module.exports = { DeploymentMonitoringSystem, DeploymentMonitor, AutoFixer }; 