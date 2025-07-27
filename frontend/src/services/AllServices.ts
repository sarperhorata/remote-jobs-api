import { HomejobService } from './HomeJobService';
import { jobService as jobServiceInstance } from './jobService';

// Export all services from this file
export { HomejobService };

// For compatibility with existing code
export const jobService = jobServiceInstance; 