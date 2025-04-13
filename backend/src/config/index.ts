import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: process.env.PORT || 3000,
  mongoUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/remote-jobs',
  jwtSecret: process.env.JWT_SECRET || 'your-secret-key',
  logdnaKey: process.env.LOGDNA_KEY,
  logdnaApp: process.env.LOGDNA_APP || 'remote-jobs',
  logdnaEnv: process.env.NODE_ENV || 'development'
}; 