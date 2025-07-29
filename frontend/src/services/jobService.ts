import { Job, JobApplication } from '../types/job';
import { getApiUrl } from '../utils/apiConfig';

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

const getSavedJobsLocal = (): string[] => {
  const stored = localStorage.getItem(SAVED_JOBS_KEY);
  return stored ? JSON.parse(stored) : [];
};

const saveJobLocal = (jobId: string) => {
  const savedJobs = getSavedJobsLocal();
  if (!savedJobs.includes(jobId)) {
    savedJobs.push(jobId);
    localStorage.setItem(SAVED_JOBS_KEY, JSON.stringify(savedJobs));
  }
};

const unsaveJobLocal = (jobId: string) => {
  const savedJobs = getSavedJobsLocal();
  const updated = savedJobs.filter(id => id !== jobId);
  localStorage.setItem(SAVED_JOBS_KEY, JSON.stringify(updated));
};

// Real API functions with dynamic URL detection
export const getJobs = async (params: any = {}): Promise<{ items?: Job[]; jobs?: Job[]; total: number; total_pages?: number; }> => {
  try {
    const API_BASE_URL = await getApiUrl();
    const searchParams = new URLSearchParams();
    
    // Use page instead of skip for consistency with backend
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.company) searchParams.append('company', params.company);
    if (params.location) searchParams.append('location', params.location);
    if (params.sort_by) searchParams.append('sort_by', params.sort_by);
    if (params.q) searchParams.append('q', params.q);
    if (params.work_type) searchParams.append('work_type', params.work_type);
    if (params.job_type) searchParams.append('job_type', params.job_type);
    if (params.experience_level) searchParams.append('experience_level', params.experience_level);
    if (params.posted_age) searchParams.append('posted_age', params.posted_age);
    
    const response = await fetch(`${API_BASE_URL}/jobs/search?${searchParams}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching jobs:', error);
    throw error; // Re-throw the error instead of returning empty result
  }
};

export const getJobById = async (id: string): Promise<Job | null> => {
  try {
    const API_BASE_URL = await getApiUrl();
    const response = await fetch(`${API_BASE_URL}/jobs/${id}`);
    
    if (!response.ok) {
      throw new Error('Job not found');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching job:', error);
    throw error; // Re-throw the error instead of returning null
  }
};

export const getSimilarJobs = async (jobId: string): Promise<Job[]> => {
  try {
    const API_BASE_URL = await getApiUrl();
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

export const searchJobs = async (filters: any = {}, page: number = 1): Promise<Job[]> => {
  try {
    const API_BASE_URL = await getApiUrl();
    const searchParams = new URLSearchParams();
    
    // Add filters to search params
    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined && filters[key] !== null) {
        searchParams.append(key, filters[key].toString());
      }
    });
    
    // Add pagination
    searchParams.append('page', page.toString());
    
    const response = await fetch(`${API_BASE_URL}/jobs/search?${searchParams}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Internal server error');
    }
    
    const data = await response.json();
    return data.items || data.jobs || [];
  } catch (error) {
    console.error('Error searching jobs:', error);
    throw error; // Re-throw the error for proper error handling in tests
  }
};

export const getJobStatistics = async () => {
  try {
    const API_BASE_URL = await getApiUrl();
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
  saveJobLocal(jobId);
};

export const unsaveJobFromLater = async (jobId: string): Promise<void> => {
  unsaveJobLocal(jobId);
};

export const getSavedJobsForUser = async (userId: string): Promise<Job[]> => {
  const savedJobIds = getSavedJobsLocal();
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

// Export a named JobServiceClass for consistency
export class JobServiceClass {
  static async getBaseURL(): Promise<string> {
    return await getApiUrl();
  }

  static async getJobs(page = 1, perPage = 10, filters?: any): Promise<Job[]> {
    try {
      const API_BASE_URL = await getApiUrl();
      const searchParams = new URLSearchParams();
      searchParams.append('page', page.toString());
      searchParams.append('limit', perPage.toString());
      
      if (filters) {
        if (filters.location) searchParams.append('location', filters.location);
        if (filters.company) searchParams.append('company', filters.company);
        if (filters.search) searchParams.append('q', filters.search);
      }

      const response = await fetch(`${API_BASE_URL}/jobs/search?${searchParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Null safety check
      if (!data) {
        return [];
      }
      
      return data.jobs || data.items || data;
    } catch (error) {
      console.error('Error fetching jobs:', error);
      throw error;
    }
  }

  static async getJobById(id: string): Promise<Job | null> {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching job:', error);
      throw error;
    }
  }

  static async getSimilarJobs(jobId: string): Promise<Job[]> {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/similar`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch similar jobs');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching similar jobs:', error);
      return [];
    }
  }

  static async searchJobs(query: string, params?: any): Promise<{ jobs: Job[]; total: number }> {
    try {
      const API_BASE_URL = await getApiUrl();
      
      // Handle empty query
      if (!query || query.trim() === '') {
        return { jobs: [], total: 0 };
      }
      
      const searchParams = new URLSearchParams();
      searchParams.append('q', query);
      
      if (params?.page) searchParams.append('page', params.page.toString());
      if (params?.per_page) searchParams.append('per_page', params.per_page.toString());

      const response = await fetch(`${API_BASE_URL}/jobs/search?${searchParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      // Add null check for response
      if (!response || !response.ok) {
        throw new Error(`HTTP ${response?.status || 'unknown'}: ${response?.statusText || 'unknown error'}`);
      }
      
      const data = await response.json();
      return {
        jobs: data.items || data.jobs || data,
        total: data.total || data.length || 0
      };
    } catch (error) {
      console.error('Error searching jobs:', error);
      throw error;
    }
  }

  static async getJobStatistics() {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/statistics`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch job statistics');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching job statistics:', error);
      throw error;
    }
  }

  static async getFeaturedJobs(): Promise<Job[]> {
    const result = await getJobs({ limit: 3 });
    return result.items || result.jobs || [];
  }

  static async getJobStats() {
    return await getJobStatistics();
  }

  static async createJob(jobData: any) {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(jobData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating job:', error);
      throw error;
    }
  }

  static async updateJob(id: string, jobData: any) {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(jobData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error updating job:', error);
      throw error;
    }
  }

  static async deleteJob(id: string) {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return response.ok;
    } catch (error) {
      console.error('Error deleting job:', error);
      throw error;
    }
  }

  static async applyToJob(jobId: string, applicationData: any) {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(applicationData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error applying to job:', error);
      throw error;
    }
  }

  static async getMyApplications() {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/applications`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching applications:', error);
      throw error;
    }
  }

  static async saveJob(userId: string, jobId: string): Promise<void> {
    await saveJobLocal(jobId);
  }

  static async unsaveJob(userId: string, jobId: string): Promise<void> {
    await unsaveJobLocal(jobId);
  }

  static async getJobApplications(userId: string): Promise<{ applications: any[], savedJobs: any[] }> {
    return { 
      applications: await getJobApplications(userId),
      savedJobs: await getSavedJobsForUser(userId)
    };
  }

  // v2: Form Scraping Methods
  static async scrapeJobApplicationForm(jobId: string, url: string): Promise<any> {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/scrape-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({ url })
      });

      if (!response.ok) {
        throw new Error(`Failed to scrape form: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error scraping form:', error);
      throw error;
    }
  }

  static async submitScrapedFormApplication(jobId: string, applicationData: any): Promise<any> {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/apply-scraped`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(applicationData)
      });

      if (!response.ok) {
        throw new Error(`Failed to submit application: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error submitting scraped application:', error);
      throw error;
    }
  }

  // v3: Automated Application Methods
  static async submitAutomatedApplication(jobId: string, applicationData: any): Promise<any> {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/apply-automated`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(applicationData)
      });

      if (!response.ok) {
        throw new Error(`Failed to submit automated application: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error submitting automated application:', error);
      throw error;
    }
  }

  // User Profile Methods
  static async getUserProfile(): Promise<any> {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/users/profile`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get user profile: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching user profile:', error);
      throw error;
    }
  }

  // Analytics and Tracking
  static async trackJobInteraction(jobId: string, action: string): Promise<void> {
    try {
      const API_BASE_URL = await getApiUrl();
      await fetch(`${API_BASE_URL}/jobs/${jobId}/track`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action, timestamp: new Date().toISOString() })
      });
    } catch (error) {
      console.error('Failed to track job interaction:', error);
    }
  }

  // Autocomplete helper for home page
  static async getJobTitleSuggestions(query: string, limit: number = 10): Promise<{ title: string; count: number; category: string }[]> {
    try {
      const API_BASE_URL = await getApiUrl();
      const response = await fetch(`${API_BASE_URL}/jobs/job-titles/search?q=${encodeURIComponent(query)}&limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch job title suggestions: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching job title suggestions:', error);
      // Fallback data
      return [
        { title: 'Software Engineer', count: 1250, category: 'Technology' },
        { title: 'Product Manager', count: 890, category: 'Management' },
        { title: 'Frontend Developer', count: 670, category: 'Technology' },
        { title: 'Data Scientist', count: 540, category: 'Technology' },
        { title: 'UX Designer', count: 320, category: 'Design' }
      ];
    }
  }
}

// Export individual functions for compatibility
export const jobService = {
  searchJobs: async (params: any) => {
    const result = await getJobs(params);
    return { jobs: result.items || result.jobs || [], total: result.total };
  },
  getJobs: async (page = 1, perPage = 10, filters?: any) => {
    return await JobServiceClass.getJobs(page, perPage, filters);
  },
  getJobById: async (id: string) => {
    return await JobServiceClass.getJobById(id);
  },
  getSimilarJobs: async (jobId: string) => {
    return await JobServiceClass.getSimilarJobs(jobId);
  },
  getFeaturedJobs: async () => {
    return await JobServiceClass.getFeaturedJobs();
  },
  getJobStats: async () => {
    return await JobServiceClass.getJobStats();
  },
  getJobStatistics: async () => {
    return await JobServiceClass.getJobStatistics();
  },
  applyToJob: async (jobId: string, applicationData: any) => {
    return await JobServiceClass.applyToJob(jobId, applicationData);
  },
  createJob: async (jobData: any) => {
    return await JobServiceClass.createJob(jobData);
  },
  updateJob: async (id: string, jobData: any) => {
    return await JobServiceClass.updateJob(id, jobData);
  },
  deleteJob: async (id: string) => {
    return await JobServiceClass.deleteJob(id);
  },
  saveJob: async (jobId: string) => {
    await saveJobLocal(jobId);
  },
  unsaveJob: async (userId: string, jobId: string) => {
    await unsaveJobLocal(jobId);
  },
  getUserProfile: JobServiceClass.getUserProfile,
  scrapeJobApplicationForm: JobServiceClass.scrapeJobApplicationForm,
  submitScrapedFormApplication: JobServiceClass.submitScrapedFormApplication,
  submitAutomatedApplication: JobServiceClass.submitAutomatedApplication,
  getMyApplications: JobServiceClass.getMyApplications,
  trackJobInteraction: JobServiceClass.trackJobInteraction,
  getJobTitleSuggestions: JobServiceClass.getJobTitleSuggestions
};

// Export individual functions for test compatibility
export const getJobsByCompany = async (companyId: string): Promise<Job[]> => {
  try {
    const API_BASE_URL = await getApiUrl();
    const response = await fetch(`${API_BASE_URL}/companies/${companyId}/jobs`);
    
    if (!response.ok) {
      throw new Error('Company not found');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching jobs by company:', error);
    throw error;
  }
};

export const getSavedJobs = async (): Promise<Job[]> => {
  try {
    const API_BASE_URL = await getApiUrl();
    const response = await fetch(`${API_BASE_URL}/jobs/saved`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Unauthorized');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching saved jobs:', error);
    throw error;
  }
};

export const saveJob = async (jobId: string): Promise<any> => {
  try {
    const API_BASE_URL = await getApiUrl();
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/save`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Job already saved');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error saving job:', error);
    throw error;
  }
};

export const unsaveJob = async (jobId: string): Promise<any> => {
  try {
    const API_BASE_URL = await getApiUrl();
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/unsave`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Job not found in saved jobs');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error unsaving job:', error);
    throw error;
  }
};

export const applyToJob = async (jobId: string, applicationData: any): Promise<any> => {
  try {
    const API_BASE_URL = await getApiUrl();
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/apply`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(applicationData)
    });
    
    if (!response.ok) {
      throw new Error('Already applied to this job');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error applying to job:', error);
    throw error;
  }
};

export const getJobRecommendations = async (): Promise<{ jobs: Job[]; total: number }> => {
  try {
    const API_BASE_URL = await getApiUrl();
    const response = await fetch(`${API_BASE_URL}/jobs/recommendations`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      return { jobs: [], total: 0 };
    }
    
    const data = await response.json();
    return { jobs: data.jobs || [], total: data.total || 0 };
  } catch (error) {
    console.error('Error fetching job recommendations:', error);
    return { jobs: [], total: 0 };
  }
};

export default JobServiceClass; 