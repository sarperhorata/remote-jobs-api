import { HomeJobService } from './HomeJobService';
import JobService from './jobService.js';

// Export all services from this file
export { HomeJobService, JobService };

// For compatibility with existing code
export const jobService = {
  // JobService methods
  getJobs: JobService.getJobs,
  getJobById: JobService.getJobById,
  getSimilarJobs: JobService.getSimilarJobs,
  saveJob: JobService.saveJob,
  unsaveJob: JobService.unsaveJob,
  applyForJob: JobService.applyForJob,
  getFeaturedJobs: JobService.getFeaturedJobs,
  getJobStats: JobService.getJobStats,
  getSystemStatus: JobService.getSystemStatus,
  getJobApplications: JobService.getJobApplications
}; 