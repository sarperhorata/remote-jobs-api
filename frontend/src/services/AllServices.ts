import { HomeJobService } from './HomeJobService';
import JobService from './jobService';

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
  applyToJob: JobService.applyToJob,
  getFeaturedJobs: JobService.getFeaturedJobs,
  getJobStats: JobService.getJobStats,
  getJobApplications: JobService.getJobApplications
}; 