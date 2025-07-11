import mongoose from 'mongoose';
import { logger } from '../services/LoggerService';

const MONGODB_URI = process.env.MONGODB_URI || 'process.env.MONGODB_URI/remote-jobs?retryWrites=true&w=majority';

export const connectDB = async () => {
  try {
    await mongoose.connect(MONGODB_URI);
    logger.info('MongoDB connected successfully');
  } catch (error) {
    logger.error('MongoDB connection error:', error);
    process.exit(1);
  }
}; 