#!/usr/bin/env node

/**
 * Send Notification Script
 * Sends notifications for deployment errors via various channels
 */

const https = require('https');

class NotificationSender {
  constructor() {
    this.config = {
      telegramBotToken: process.env.TELEGRAM_BOT_TOKEN,
      telegramChatId: process.env.TELEGRAM_CHAT_ID,
      slackWebhookUrl: process.env.SLACK_WEBHOOK_URL,
      emailApiKey: process.env.EMAIL_API_KEY,
      emailFrom: process.env.EMAIL_FROM,
      emailTo: process.env.EMAIL_TO
    };
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

  async sendTelegramNotification(message) {
    if (!this.config.telegramBotToken || !this.config.telegramChatId) {
      this.log('Telegram credentials not configured', 'warning');
      return;
    }

    try {
      const data = JSON.stringify({
        chat_id: this.config.telegramChatId,
        text: `🚨 Deployment Alert\n\n${message}\n\nTime: ${new Date().toISOString()}`,
        parse_mode: 'HTML'
      });

      const options = {
        hostname: 'api.telegram.org',
        path: `/bot${this.config.telegramBotToken}/sendMessage`,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': data.length
        }
      };

      await this.makeRequest(options, data);
      this.log('Telegram notification sent', 'success');
    } catch (error) {
      this.log(`Failed to send Telegram notification: ${error.message}`, 'error');
    }
  }

  async sendSlackNotification(message) {
    if (!this.config.slackWebhookUrl) {
      this.log('Slack webhook not configured', 'warning');
      return;
    }

    try {
      const data = JSON.stringify({
        text: `🚨 Deployment Alert\n\n${message}`,
        attachments: [
          {
            color: '#ff0000',
            fields: [
              {
                title: 'Time',
                value: new Date().toISOString(),
                short: true
              },
              {
                title: 'Environment',
                value: process.env.NODE_ENV || 'development',
                short: true
              }
            ]
          }
        ]
      });

      const url = new URL(this.config.slackWebhookUrl);
      const options = {
        hostname: url.hostname,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': data.length
        }
      };

      await this.makeRequest(options, data);
      this.log('Slack notification sent', 'success');
    } catch (error) {
      this.log(`Failed to send Slack notification: ${error.message}`, 'error');
    }
  }

  async sendEmailNotification(message) {
    if (!this.config.emailApiKey || !this.config.emailFrom || !this.config.emailTo) {
      this.log('Email credentials not configured', 'warning');
      return;
    }

    try {
      const data = JSON.stringify({
        from: this.config.emailFrom,
        to: this.config.emailTo,
        subject: '🚨 Deployment Alert - Buzz2Remote',
        html: `
          <h2>Deployment Alert</h2>
          <p><strong>Message:</strong> ${message}</p>
          <p><strong>Time:</strong> ${new Date().toISOString()}</p>
          <p><strong>Environment:</strong> ${process.env.NODE_ENV || 'development'}</p>
          <hr>
          <p>This is an automated notification from the Buzz2Remote deployment monitor.</p>
        `
      });

      const options = {
        hostname: 'api.mailgun.net',
        path: `/v3/mg.buzz2remote.com/messages`,
        method: 'POST',
        headers: {
          'Authorization': `Basic ${Buffer.from(`api:${this.config.emailApiKey}`).toString('base64')}`,
          'Content-Type': 'application/x-www-form-urlencoded',
          'Content-Length': data.length
        }
      };

      await this.makeRequest(options, data);
      this.log('Email notification sent', 'success');
    } catch (error) {
      this.log(`Failed to send email notification: ${error.message}`, 'error');
    }
  }

  async makeRequest(options, data = null) {
    return new Promise((resolve, reject) => {
      const req = https.request(options, (res) => {
        let responseData = '';
        
        res.on('data', (chunk) => {
          responseData += chunk;
        });
        
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(responseData);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${responseData}`));
          }
        });
      });
      
      req.on('error', (error) => {
        reject(error);
      });
      
      if (data) {
        req.write(data);
      }
      
      req.end();
    });
  }

  async sendAllNotifications(message) {
    this.log('Sending notifications...');
    
    await Promise.all([
      this.sendTelegramNotification(message),
      this.sendSlackNotification(message),
      this.sendEmailNotification(message)
    ]);
    
    this.log('All notifications sent', 'success');
  }
}

// Get message from command line arguments
const message = process.argv[2] || 'Deployment error detected';

// Send notifications
const sender = new NotificationSender();
sender.sendAllNotifications(message).catch(error => {
  console.error('❌ Failed to send notifications:', error);
  process.exit(1);
}); 