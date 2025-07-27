/**
 * Debug utilities for development
 */

export const debugUtils = {
  log: (message: string, ...args: any[]) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[DEBUG] ${message}`, ...args);
    }
  },
  
  warn: (message: string, ...args: any[]) => {
    if (process.env.NODE_ENV === 'development') {
      console.warn(`[DEBUG WARN] ${message}`, ...args);
    }
  },
  
  error: (message: string, ...args: any[]) => {
    if (process.env.NODE_ENV === 'development') {
      console.error(`[DEBUG ERROR] ${message}`, ...args);
    }
  },
  
  time: (label: string) => {
    if (process.env.NODE_ENV === 'development') {
      console.time(`[DEBUG TIME] ${label}`);
    }
  },
  
  timeEnd: (label: string) => {
    if (process.env.NODE_ENV === 'development') {
      console.timeEnd(`[DEBUG TIME] ${label}`);
    }
  }
};

export default debugUtils; 