import { Request, Response, NextFunction } from 'express';
import { logger } from '../services/LoggerService';
import { isIPBlocked, blockIP } from './ipBlockerMiddleware';

interface RateLimitStore {
  [key: string]: {
    count: number;
    resetTime: number;
  };
}

const store: RateLimitStore = {};

export const rateLimiter = (windowMs: number = 15 * 60 * 1000, max: number = 100) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const ip = req.ip;
    
    if (isIPBlocked(ip)) {
      return res.status(403).json({ error: 'IP is blocked' });
    }

    const now = Date.now();
    
    if (!store[ip]) {
      store[ip] = {
        count: 1,
        resetTime: now + windowMs
      };
    } else if (now > store[ip].resetTime) {
      store[ip] = {
        count: 1,
        resetTime: now + windowMs
      };
    } else {
      store[ip].count++;
      
      if (store[ip].count > max) {
        logger.warn(`Rate limit exceeded for IP: ${ip}`);
        blockIP(ip);
        return res.status(429).json({ error: 'Too many requests' });
      }
    }

    next();
  };
};

// Create different rate limiters for different routes
export const authLimiter = rateLimiter(60 * 60 * 1000, 5);
export const apiLimiter = rateLimiter(15 * 60 * 1000, 100); 