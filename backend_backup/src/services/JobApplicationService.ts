import { User } from '../models/User';
import { Job } from '../models/Job';
import { logger } from './LoggerService';

export class JobApplicationService {
  private static instance: JobApplicationService;

  private constructor() {}

  public static getInstance(): JobApplicationService {
    if (!JobApplicationService.instance) {
      JobApplicationService.instance = new JobApplicationService();
    }
    return JobApplicationService.instance;
  }

  async applyForJob(userId: string, jobId: string) {
    try {
      const user = await User.findById(userId);
      const job = await Job.findById(jobId);

      if (!user || !job) {
        throw new Error('User or job not found');
      }

      // Check if already applied
      const existingApplication = user.jobApplications.find(
        app => app.jobId.toString() === jobId
      );

      if (existingApplication) {
        throw new Error('Already applied for this job');
      }

      // Add to applications
      user.jobApplications.push({
        jobId,
        status: 'applied',
        appliedAt: new Date(),
        lastUpdated: new Date()
      });

      await user.save();
      logger.info(`User ${userId} applied for job ${jobId}`);
      return user.jobApplications[user.jobApplications.length - 1];
    } catch (error) {
      logger.error(`Error applying for job ${jobId} by user ${userId}:`, error);
      throw error;
    }
  }

  async updateApplicationStatus(userId: string, jobId: string, status: string) {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error('User not found');
      }

      const application = user.jobApplications.find(
        app => app.jobId.toString() === jobId
      );

      if (!application) {
        throw new Error('Application not found');
      }

      application.status = status;
      application.lastUpdated = new Date();

      await user.save();
      logger.info(`Application status updated for user ${userId}, job ${jobId}: ${status}`);
      return application;
    } catch (error) {
      logger.error(`Error updating application status for user ${userId}, job ${jobId}:`, error);
      throw error;
    }
  }

  async saveJob(userId: string, jobId: string) {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error('User not found');
      }

      if (user.savedJobs.includes(jobId)) {
        throw new Error('Job already saved');
      }

      user.savedJobs.push(jobId);
      await user.save();
      
      logger.info(`Job ${jobId} saved by user ${userId}`);
      return user.savedJobs;
    } catch (error) {
      logger.error(`Error saving job ${jobId} for user ${userId}:`, error);
      throw error;
    }
  }

  async unsaveJob(userId: string, jobId: string) {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error('User not found');
      }

      user.savedJobs = user.savedJobs.filter(id => id.toString() !== jobId);
      await user.save();
      
      logger.info(`Job ${jobId} unsaved by user ${userId}`);
      return user.savedJobs;
    } catch (error) {
      logger.error(`Error unsaving job ${jobId} for user ${userId}:`, error);
      throw error;
    }
  }

  async hideJob(userId: string, jobId: string, reason: string) {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error('User not found');
      }

      // Check if already hidden
      const existingHide = user.hiddenJobs.find(
        hide => hide.jobId.toString() === jobId
      );

      if (existingHide) {
        throw new Error('Job already hidden');
      }

      user.hiddenJobs.push({
        jobId,
        reason,
        hiddenAt: new Date()
      });

      await user.save();
      logger.info(`Job ${jobId} hidden by user ${userId} with reason: ${reason}`);
      return user.hiddenJobs[user.hiddenJobs.length - 1];
    } catch (error) {
      logger.error(`Error hiding job ${jobId} for user ${userId}:`, error);
      throw error;
    }
  }

  async getApplicationHistory(userId: string) {
    try {
      const user = await User.findById(userId)
        .populate('jobApplications.jobId')
        .populate('savedJobs')
        .populate('hiddenJobs.jobId');

      if (!user) {
        throw new Error('User not found');
      }

      return {
        applications: user.jobApplications,
        savedJobs: user.savedJobs,
        hiddenJobs: user.hiddenJobs
      };
    } catch (error) {
      logger.error(`Error getting application history for user ${userId}:`, error);
      throw error;
    }
  }
} 