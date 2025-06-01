import { Job, JobApplication } from '../types/job';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

// Helper functions for local storage
const APPLICATIONS_KEY = 'applications';
const SAVED_JOBS_KEY = 'savedJobs';

const getApplications = (): JobApplication[] => {
  const stored = localStorage.getItem(APPLICATIONS_KEY);
  return stored ? JSON.parse(stored) : [];
};

const saveApplication = (application: JobApplication) => {
  const applications = getApplications();
  applications.push(application);
  localStorage.setItem(APPLICATIONS_KEY, JSON.stringify(applications));
};

const getSavedJobs = (): string[] => {
  const stored = localStorage.getItem(SAVED_JOBS_KEY);
  return stored ? JSON.parse(stored) : [];
};

const saveJob = (jobId: string) => {
  const savedJobs = getSavedJobs();
  if (!savedJobs.includes(jobId)) {
    savedJobs.push(jobId);
    localStorage.setItem(SAVED_JOBS_KEY, JSON.stringify(savedJobs));
  }
};

const unsaveJob = (jobId: string) => {
  const savedJobs = getSavedJobs();
  const updated = savedJobs.filter(id => id !== jobId);
  localStorage.setItem(SAVED_JOBS_KEY, JSON.stringify(updated));
};

// Real API functions
export const getJobs = async (params: any = {}): Promise<{ items?: Job[]; jobs?: Job[]; total: number; total_pages?: number; }> => {
  try {
    const searchParams = new URLSearchParams();
    
    if (params.page) searchParams.append('skip', ((params.page - 1) * 10).toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.company) searchParams.append('company', params.company);
    if (params.location) searchParams.append('location', params.location);
    if (params.sort_by) searchParams.append('sort_by', params.sort_by);
    
    const response = await fetch(`${API_BASE_URL}/jobs/?${searchParams}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch jobs');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching jobs:', error);
    // Return empty result on error
    return { items: [], jobs: [], total: 0 };
  }
};

export const getJobById = async (id: string): Promise<Job | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${id}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch job');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching job:', error);
    return null;
  }
};

export const getSimilarJobs = async (jobId: string): Promise<Job[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/similar`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch similar jobs');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching similar jobs:', error);
    return [];
  }
};

export const searchJobs = async (query: string, params: any = {}): Promise<Job[]> => {
  try {
    const searchParams = new URLSearchParams();
    searchParams.append('query', query);
    
    if (params.skip) searchParams.append('skip', params.skip.toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());
    
    const response = await fetch(`${API_BASE_URL}/jobs/search/?${searchParams}`);
    
    if (!response.ok) {
      throw new Error('Failed to search jobs');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error searching jobs:', error);
    return [];
  }
};

export const getJobStatistics = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/statistics/`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch job statistics');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching job statistics:', error);
    return {
      total_jobs: 0,
      jobs_by_company: [],
      jobs_by_location: []
    };
  }
};

// Local storage functions for user actions
export const applyForJob = async (jobId: string, userId: string, data: any = {}): Promise<JobApplication> => {
  const application: JobApplication = {
    id: Date.now(),
    jobId: parseInt(jobId),
    userId: parseInt(userId),
    status: 'pending',
    appliedAt: new Date().toISOString(),
    resume: data.resume,
    coverLetter: data.coverLetter,
  };
  
  saveApplication(application);
  return application;
};

export const getJobApplications = async (userId: string): Promise<JobApplication[]> => {
  return getApplications().filter(app => app.userId.toString() === userId);
};

export const saveJobForLater = async (jobId: string): Promise<void> => {
  saveJob(jobId);
};

export const unsaveJobFromLater = async (jobId: string): Promise<void> => {
  unsaveJob(jobId);
};

export const getSavedJobsForUser = async (userId: string): Promise<Job[]> => {
  const savedJobIds = getSavedJobs();
  const savedJobs: Job[] = [];
  
  // Fetch each saved job
  for (const jobId of savedJobIds) {
    const job = await getJobById(jobId);
    if (job) {
      savedJobs.push(job);
    }
  }
  
  return savedJobs;
};

// Export a named JobService class for consistency
export class JobService {
  static async getJobs(filters?: any): Promise<Job[]> {
    const result = await getJobs(filters);
    return result.items || result.jobs || [];
  }

  static async getJobById(id: string): Promise<Job | null> {
    return await getJobById(id);
  }

  static async getSimilarJobs(jobId: string): Promise<Job[]> {
    return await getSimilarJobs(jobId);
  }

  static async saveJob(userId: string, jobId: string): Promise<void> {
    await saveJob(jobId);
  }

  static async unsaveJob(userId: string, jobId: string): Promise<void> {
    await unsaveJob(jobId);
  }

  static async applyForJob(userId: string, jobId: string, data: any = {}): Promise<void> {
    await applyForJob(jobId, userId, data);
  }

  static async getFeaturedJobs(): Promise<Job[]> {
    const result = await getJobs({ limit: 3 });
    return result.items || result.jobs || [];
  }

  static async getJobStats() {
    return await getJobStatistics();
  }

  static async getJobApplications(userId: string): Promise<{ applications: any[], savedJobs: any[] }> {
    return { 
      applications: await getJobApplications(userId),
      savedJobs: await getSavedJobsForUser(userId)
    };
  }
}

export default JobService; 