#!/usr/bin/env node

/**
 * Deployment Monitor
 * Monitors deployment status and automatically fixes common issues
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

class DeploymentMonitor {
  constructor() {
    this.config = {
      netlifySiteId: process.env.NETLIFY_SITE_ID,
      netlifyToken: process.env.NETLIFY_AUTH_TOKEN,
      renderServiceId: process.env.RENDER_SERVICE_ID,
      renderApiKey: process.env.RENDER_API_KEY,
      githubToken: process.env.GITHUB_TOKEN,
      githubRepo: process.env.GITHUB_REPOSITORY
    };
    
    this.errors = [];
    this.fixes = [];
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

  async checkNetlifyDeployment() {
    if (!this.config.netlifySiteId || !this.config.netlifyToken) {
      this.log('Netlify credentials not configured', 'warning');
      return;
    }

    try {
      this.log('Checking Netlify deployment status...');
      
      const options = {
        hostname: 'api.netlify.com',
        path: `/api/v1/sites/${this.config.netlifySiteId}/deploys`,
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.config.netlifyToken}`,
          'Content-Type': 'application/json'
        }
      };

      const response = await this.makeRequest(options);
      const deploys = JSON.parse(response);
      
      if (deploys.length > 0) {
        const latestDeploy = deploys[0];
        this.log(`Latest deployment: ${latestDeploy.state} (${latestDeploy.created_at})`);
        
        if (latestDeploy.state === 'error') {
          this.log('Netlify deployment failed!', 'error');
          this.errors.push(`Netlify deployment error: ${latestDeploy.error_message}`);
          
          // Auto-retry deployment
          await this.retryNetlifyDeployment();
        } else if (latestDeploy.state === 'ready') {
          this.log('Netlify deployment successful!', 'success');
        }
      }
    } catch (error) {
      this.log(`Netlify check failed: ${error.message}`, 'error');
    }
  }

  async checkRenderDeployment() {
    if (!this.config.renderServiceId || !this.config.renderApiKey) {
      this.log('Render credentials not configured', 'warning');
      return;
    }

    try {
      this.log('Checking Render deployment status...');
      
      const options = {
        hostname: 'api.render.com',
        path: `/v1/services/${this.config.renderServiceId}`,
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.config.renderApiKey}`,
          'Content-Type': 'application/json'
        }
      };

      const response = await this.makeRequest(options);
      const service = JSON.parse(response);
      
      this.log(`Render service status: ${service.service.status}`);
      
      if (service.service.status === 'failed') {
        this.log('Render deployment failed!', 'error');
        this.errors.push(`Render deployment error: ${service.service.status}`);
        
        // Auto-restart service
        await this.restartRenderService();
      } else if (service.service.status === 'live') {
        this.log('Render deployment successful!', 'success');
      }
    } catch (error) {
      this.log(`Render check failed: ${error.message}`, 'error');
    }
  }

  async checkGitHubActions() {
    if (!this.config.githubToken || !this.config.githubRepo) {
      this.log('GitHub credentials not configured', 'warning');
      return;
    }

    try {
      this.log('Checking GitHub Actions status...');
      
      const options = {
        hostname: 'api.github.com',
        path: `/repos/${this.config.githubRepo}/actions/runs?per_page=5`,
        method: 'GET',
        headers: {
          'Authorization': `token ${this.config.githubToken}`,
          'User-Agent': 'DeploymentMonitor'
        }
      };

      const response = await this.makeRequest(options);
      const runs = JSON.parse(response);
      
      for (const run of runs.workflow_runs) {
        this.log(`Workflow ${run.name}: ${run.conclusion} (${run.status})`);
        
        if (run.conclusion === 'failure') {
          this.log(`GitHub Actions workflow failed: ${run.name}`, 'error');
          this.errors.push(`GitHub Actions failure: ${run.name}`);
          
          // Auto-retry workflow
          await this.retryGitHubWorkflow(run.id);
        }
      }
    } catch (error) {
      this.log(`GitHub Actions check failed: ${error.message}`, 'error');
    }
  }

  async checkWebsiteHealth() {
    const urls = [
      'https://buzz2remote.com',
      'https://buzz2remote.netlify.app',
      'http://localhost:3000'
    ];

    for (const url of urls) {
      try {
        this.log(`Checking website health: ${url}`);
        
        const response = await this.checkUrl(url);
        if (response.status >= 200 && response.status < 300) {
          this.log(`${url} is healthy (${response.status})`, 'success');
        } else {
          this.log(`${url} returned status ${response.status}`, 'warning');
          this.errors.push(`Website health check failed: ${url} (${response.status})`);
        }
      } catch (error) {
        this.log(`${url} is not accessible: ${error.message}`, 'error');
        this.errors.push(`Website not accessible: ${url}`);
      }
    }
  }

  async checkUrl(url) {
    return new Promise((resolve, reject) => {
      const client = url.startsWith('https') ? https : http;
      
      const req = client.get(url, (res) => {
        resolve({ status: res.statusCode });
      });
      
      req.on('error', (error) => {
        reject(error);
      });
      
      req.setTimeout(10000, () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
    });
  }

  async makeRequest(options) {
    return new Promise((resolve, reject) => {
      const client = options.hostname === 'api.netlify.com' || 
                    options.hostname === 'api.render.com' || 
                    options.hostname === 'api.github.com' ? https : http;
      
      const req = client.request(options, (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          resolve(data);
        });
      });
      
      req.on('error', (error) => {
        reject(error);
      });
      
      req.end();
    });
  }

  async retryNetlifyDeployment() {
    try {
      this.log('Retrying Netlify deployment...');
      
      const options = {
        hostname: 'api.netlify.com',
        path: `/api/v1/sites/${this.config.netlifySiteId}/deploys`,
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.netlifyToken}`,
          'Content-Type': 'application/json'
        }
      };

      await this.makeRequest(options);
      this.log('Netlify deployment retry initiated', 'success');
      this.fixes.push('Retried Netlify deployment');
    } catch (error) {
      this.log(`Failed to retry Netlify deployment: ${error.message}`, 'error');
    }
  }

  async restartRenderService() {
    try {
      this.log('Restarting Render service...');
      
      const options = {
        hostname: 'api.render.com',
        path: `/v1/services/${this.config.renderServiceId}/deploys`,
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.renderApiKey}`,
          'Content-Type': 'application/json'
        }
      };

      await this.makeRequest(options);
      this.log('Render service restart initiated', 'success');
      this.fixes.push('Restarted Render service');
    } catch (error) {
      this.log(`Failed to restart Render service: ${error.message}`, 'error');
    }
  }

  async retryGitHubWorkflow(runId) {
    try {
      this.log(`Retrying GitHub workflow: ${runId}`);
      
      const options = {
        hostname: 'api.github.com',
        path: `/repos/${this.config.githubRepo}/actions/runs/${runId}/rerun`,
        method: 'POST',
        headers: {
          'Authorization': `token ${this.config.githubToken}`,
          'User-Agent': 'DeploymentMonitor'
        }
      };

      await this.makeRequest(options);
      this.log('GitHub workflow retry initiated', 'success');
      this.fixes.push(`Retried GitHub workflow: ${runId}`);
    } catch (error) {
      this.log(`Failed to retry GitHub workflow: ${error.message}`, 'error');
    }
  }

  async runAutoFix() {
    if (this.errors.length > 0) {
      this.log('Running automatic fixes...');
      
      // Run frontend auto-fix
      try {
        const { execSync } = require('child_process');
        execSync('cd frontend && npm run auto-fix', { 
          stdio: 'pipe',
          encoding: 'utf8'
        });
        this.log('Frontend auto-fix completed', 'success');
      } catch (error) {
        this.log(`Frontend auto-fix failed: ${error.message}`, 'error');
      }
      
      // Run backend auto-fix
      try {
        const { execSync } = require('child_process');
        execSync('cd backend && python scripts/fix_security_issues.py', { 
          stdio: 'pipe',
          encoding: 'utf8'
        });
        this.log('Backend auto-fix completed', 'success');
      } catch (error) {
        this.log(`Backend auto-fix failed: ${error.message}`, 'error');
      }
    }
  }

  generateReport() {
    this.log('=== DEPLOYMENT MONITOR REPORT ===');
    this.log(`Total errors detected: ${this.errors.length}`);
    this.log(`Total fixes applied: ${this.fixes.length}`);
    
    if (this.errors.length > 0) {
      this.log('\nErrors detected:');
      this.errors.forEach((error, index) => {
        this.log(`${index + 1}. ${error}`);
      });
    }
    
    if (this.fixes.length > 0) {
      this.log('\nFixes applied:');
      this.fixes.forEach((fix, index) => {
        this.log(`${index + 1}. ${fix}`);
      });
    }
  }

  async run() {
    this.log('🚀 Starting Deployment Monitor');
    
    // Check all deployment platforms
    await Promise.all([
      this.checkNetlifyDeployment(),
      this.checkRenderDeployment(),
      this.checkGitHubActions(),
      this.checkWebsiteHealth()
    ]);
    
    // Run auto-fixes if needed
    await this.runAutoFix();
    
    // Generate report
    this.generateReport();
    
    this.log('Deployment monitoring completed!', 'success');
  }
}

// Run the deployment monitor
const monitor = new DeploymentMonitor();
monitor.run().catch(error => {
  console.error('❌ Deployment monitoring failed:', error);
  process.exit(1);
}); 