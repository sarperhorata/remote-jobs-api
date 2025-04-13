import { Request, Response, NextFunction } from 'express';
import { logger } from '../services/LoggerService';

interface BlockedIP {
  ip: string;
  blockedAt: number;
  reason: string;
}

const blockedIPs: BlockedIP[] = [];
const BLOCK_DURATION = 24 * 60 * 60 * 1000; // 24 hours

export const ipBlocker = (req: Request, res: Response, next: NextFunction) => {
  const ip = req.ip;
  
  if (isIPBlocked(ip)) {
    logger.warn(`Blocked request from IP: ${ip}`);
    return res.status(403).json({
      status: 'error',
      message: 'Access denied. Your IP has been blocked due to suspicious activity.'
    });
  }

  next();
};

export const blockIP = (ip: string, reason: string = 'Rate limit exceeded') => {
  const existingBlock = blockedIPs.find(block => block.ip === ip);
  
  if (existingBlock) {
    existingBlock.blockedAt = Date.now();
    existingBlock.reason = reason;
  } else {
    blockedIPs.push({
      ip,
      blockedAt: Date.now(),
      reason
    });
  }
  
  logger.warn(`IP ${ip} blocked. Reason: ${reason}`);
};

export const isIPBlocked = (ip: string): boolean => {
  const now = Date.now();
  const block = blockedIPs.find(block => block.ip === ip);
  
  if (!block) return false;
  
  if (now - block.blockedAt > BLOCK_DURATION) {
    blockedIPs.splice(blockedIPs.indexOf(block), 1);
    logger.info(`IP ${ip} unblocked after ${BLOCK_DURATION}ms`);
    return false;
  }
  
  return true;
};

// Clean up expired blocks periodically
setInterval(() => {
  const now = Date.now();
  const expiredBlocks = blockedIPs.filter(block => now - block.blockedAt > BLOCK_DURATION);
  
  expiredBlocks.forEach(block => {
    blockedIPs.splice(blockedIPs.indexOf(block), 1);
    logger.info(`IP ${block.ip} unblocked after ${BLOCK_DURATION}ms`);
  });
}, 60 * 60 * 1000); // Check every hour 