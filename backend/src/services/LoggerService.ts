import winston from 'winston';
import path from 'path';
import fs from 'fs';
import { LogdnaWinston } from 'logdna-winston';

const LOGDNA_INGEST_KEY = process.env.LOGDNA_INGEST_KEY || 'your-logdna-ingest-key';
const LOGDNA_HOSTNAME = process.env.LOGDNA_HOSTNAME || 'remote-jobs-backend';
const LOGDNA_APP = process.env.LOGDNA_APP || 'remote-jobs';

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '../../logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
}

// Define log formats
const userLogFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.json()
);

const adminLogFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.json()
);

// Create loggers
const userLogger = winston.createLogger({
  format: userLogFormat,
  transports: [
    new winston.transports.File({ 
      filename: path.join(logsDir, 'user.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5,
    }),
  ],
});

const adminLogger = winston.createLogger({
  format: adminLogFormat,
  transports: [
    new winston.transports.File({ 
      filename: path.join(logsDir, 'admin.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5,
    }),
  ],
});

// Add console transport in development
if (process.env.NODE_ENV !== 'production') {
  userLogger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }));
  adminLogger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }));
}

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: LOGDNA_APP },
  transports: [
    new winston.transports.Console({
      format: winston.format.simple()
    }),
    new LogdnaWinston({
      key: LOGDNA_INGEST_KEY,
      hostname: LOGDNA_HOSTNAME,
      app: LOGDNA_APP,
      env: process.env.NODE_ENV || 'development',
      tags: ['remote-jobs', 'backend']
    })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

export { logger };

export class LoggerService {
  private logger: winston.Logger;

  constructor() {
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service: LOGDNA_APP },
      transports: [
        new winston.transports.Console({
          format: winston.format.simple()
        }),
        new LogdnaWinston({
          key: LOGDNA_INGEST_KEY,
          hostname: LOGDNA_HOSTNAME,
          app: LOGDNA_APP,
          env: process.env.NODE_ENV || 'development',
          tags: ['remote-jobs', 'backend']
        })
      ]
    });

    if (process.env.NODE_ENV !== 'production') {
      this.logger.add(new winston.transports.Console({
        format: winston.format.simple()
      }));
    }
  }

  info(message: string, meta?: any) {
    this.logger.info(message, meta);
  }

  error(message: string, meta?: any) {
    this.logger.error(message, meta);
  }

  warn(message: string, meta?: any) {
    this.logger.warn(message, meta);
  }

  debug(message: string, meta?: any) {
    this.logger.debug(message, meta);
  }

  static logUserAction(userId: string, action: string, details: any) {
    userLogger.info('User Action', {
      userId,
      action,
      details,
      timestamp: new Date().toISOString(),
    });
  }

  static logAdminAction(adminId: string, action: string, details: any) {
    adminLogger.info('Admin Action', {
      adminId,
      action,
      details,
      timestamp: new Date().toISOString(),
    });
  }

  static logError(error: Error, context: string) {
    const errorLog = {
      message: error.message,
      stack: error.stack,
      context,
      timestamp: new Date().toISOString(),
    };

    userLogger.error('Error', errorLog);
    adminLogger.error('Error', errorLog);
  }

  static async cleanOldLogs(daysToKeep: number = 30) {
    const files = fs.readdirSync(logsDir);
    const now = new Date().getTime();

    for (const file of files) {
      const filePath = path.join(logsDir, file);
      const stats = fs.statSync(filePath);
      const daysOld = (now - stats.mtime.getTime()) / (1000 * 60 * 60 * 24);

      if (daysOld > daysToKeep) {
        fs.unlinkSync(filePath);
      }
    }
  }
} 