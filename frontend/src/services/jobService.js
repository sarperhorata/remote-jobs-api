import { Job, JobApplication } from '../types/job';
import { MockDataService } from './MockDataService';

// Mock data
const mockJobs: Job[] = [
  {
    id: '1',
    title: 'Head of Product',
    company: {
      id: '1',
      name: 'Atomic',
      logo: 'https://via.placeholder.com/150',
      description: 'We are a fast-growing, mission-driven company powering the expansion of financial services and wealth creation globally. We build critical financial infrastructure that allows consumer-facing companies to offer engaging investing experiences to their customers in a frictionless way.',
      website: 'https://atomicvest.com',
      location: 'Remote',
      size: '50-200',
      industry: 'FinTech',
    },
    companyId: '1',
    description: `The Head of Product Management will be responsible for owning our suite of Product offerings. This will include optimizing our onboarding experience, our module experience once the user is onboarded, defining the feature roadmap for new upcoming features and owning the scoping and roll-out of said features. This is a hands-on leadership position that will have a direct and long-lasting impact on the business.`,
    requirements: [
      '8+ years of Product Management experience in a high-growth environment',
      'Obsessed with product quality and an eye for design',
      'Comfort working within highly complex ecosystem and system level problems',
      'Consumer financial journey experience is a plus',
      'Strong expertise managing all product management phases including product discovery, development, and go-to-market plans',
      'Highly analytical and data driven individual',
      'Metrics oriented, highly systematic, organized, scrappy and hungry',
      'Can thrive with a high level of autonomy and responsibility',
      'Excellent business acumen'
    ],
    responsibilities: [
      'Own the product roadmap and strategy for our suite of products',
      'Work closely with engineering, design, and business teams to define and execute on product initiatives',
      'Conduct user research and gather feedback to inform product decisions',
      'Define and track key metrics to measure product success',
      'Lead product development from ideation to launch',
      'Manage and mentor a team of product managers'
    ],
    skills: ['Product Management', 'FinTech', 'Leadership', 'Strategy', 'Analytics'],
    location: 'Remote',
    type: 'Full-time',
    salary: {
      min: 150000,
      max: 200000,
      currency: 'USD'
    },
    experience: {
      min: 8,
      max: 15
    },
    education: 'Bachelor\'s degree in Business, Computer Science, or related field',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    applicationUrl: 'https://atomicvest.com/careers',
    source: 'Direct',
    sourceUrl: 'https://atomicvest.com',
    status: 'active',
    postedAt: new Date('2024-03-20'),
    expiresAt: new Date('2024-04-20'),
  },
  {
    id: '2',
    title: 'Senior Frontend Developer',
    company: {
      id: '1',
      name: 'Tech Corp',
      logo: 'https://via.placeholder.com/150',
      description: 'Leading technology company',
      website: 'https://techcorp.com',
      location: 'San Francisco, CA',
      size: '1000-5000',
      industry: 'Technology',
    },
    companyId: '1',
    description: 'We are looking for a Senior Frontend Developer to join our team. You will be responsible for building and maintaining our web applications.',
    requirements: [
      '5+ years of experience with React',
      'Strong TypeScript skills',
      'Experience with state management libraries',
      'Understanding of web performance optimization',
      'Experience with CI/CD pipelines'
    ],
    responsibilities: [
      'Develop and maintain web applications',
      'Write clean, maintainable code',
      'Collaborate with designers and backend developers',
      'Participate in code reviews'
    ],
    skills: ['React', 'TypeScript', 'Node.js'],
    location: 'Remote',
    type: 'Full-time',
    salary: {
      min: 100000,
      max: 150000,
      currency: 'USD'
    },
    experience: {
      min: 5,
      max: 10
    },
    education: 'Bachelor\'s degree in Computer Science or related field',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    applicationUrl: 'https://techcorp.com/careers',
    source: 'Direct',
    sourceUrl: 'https://techcorp.com',
    status: 'active',
    postedAt: new Date('2024-03-20'),
    expiresAt: new Date('2024-04-20'),
  },
  // Add more mock jobs...
];

const mockCompanies = [
  {
    id: 1,
    name: 'Tech Corp',
    logo: 'https://via.placeholder.com/150',
    description: 'Leading technology company',
    website: 'https://techcorp.com',
    location: 'Remote',
    size: '100-500',
    industry: 'Technology',
  },
  // Add more mock companies...
];

// Mock applications
const mockApplications: JobApplication[] = [
  {
    id: 1,
    jobId: 1,
    userId: 1,
    status: 'pending',
    appliedAt: new Date().toISOString(),
    resume: 'https://example.com/resume.pdf',
    coverLetter: 'I am excited to apply for this position...',
  },
];

// Local storage keys
const APPLICATIONS_KEY = 'applications';
const SAVED_JOBS_KEY = 'savedJobs';

// Helper functions for local storage
const getApplications = (): JobApplication[] => {
  const stored = localStorage.getItem(APPLICATIONS_KEY);
  return stored ? JSON.parse(stored) : mockApplications;
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

// API functions
export const getJobs = async (params: any = {}): Promise<{ jobs: Job[]; total: number }> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  
  let filteredJobs = [...mockJobs];
  
  // Apply filters
  if (params.search) {
    const searchLower = params.search.toLowerCase();
    filteredJobs = filteredJobs.filter(job => 
      job.title.toLowerCase().includes(searchLower) || 
      job.company.name.toLowerCase().includes(searchLower) ||
      job.description.toLowerCase().includes(searchLower)
    );
  }
  
  if (params.location) {
    filteredJobs = filteredJobs.filter(job => 
      job.location.toLowerCase().includes(params.location.toLowerCase())
    );
  }
  
  if (params.type) {
    filteredJobs = filteredJobs.filter(job => 
      job.type.toLowerCase() === params.type.toLowerCase()
    );
  }
  
  return {
    jobs: filteredJobs,
    total: filteredJobs.length
  };
};

export const getJobById = async (id: string): Promise<Job | null> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return mockJobs.find(job => job.id === id) || null;
};

export const getCompanyById = async (id: string) => {
  await new Promise(resolve => setTimeout(resolve, 500));
  return mockJobs.find(job => job.company.id === id)?.company || null;
};

export const getSimilarJobs = async (jobId: string): Promise<Job[]> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  const job = mockJobs.find(j => j.id === jobId);
  if (!job) return [];
  
  return mockJobs
    .filter(j => j.id !== jobId && j.type === job.type)
    .slice(0, 3);
};

export const applyForJob = async (jobId: string, userId: string, data: any = {}): Promise<JobApplication> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  
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
  await new Promise(resolve => setTimeout(resolve, 500));
  return getApplications().filter(app => app.userId.toString() === userId);
};

export const saveJobForLater = async (jobId: string): Promise<void> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  saveJob(jobId);
};

export const unsaveJobFromLater = async (jobId: string): Promise<void> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  unsaveJob(jobId);
};

export const getSavedJobsForUser = async (userId: string): Promise<Job[]> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  const savedJobIds = getSavedJobs();
  return mockJobs.filter(job => savedJobIds.includes(job.id));
};

// Export a named JobService class for consistency
export class JobService {
  static async getJobs(filters?: any): Promise<Job[]> {
    return await getJobs(filters).then(res => res.jobs);
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
    // Return 3 random jobs as featured
    const { jobs } = await getJobs();
    return jobs.slice(0, 3);
  }

  static async getJobStats() {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Return mock stats
    return {
      totalJobs: '1500+',
      remoteJobs: '85%',
      hottestCompany: 'Amazon',
      jobsLast24h: '150+',
      totalCompanies: '300+',
      mostSearchedTerm: 'React'
    };
  }

  static async getSystemStatus() {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
      api: { status: 'operational', latency: '120ms' },
      database: { status: 'operational', latency: '85ms' },
      crawler: { status: 'operational', lastRun: '2 hours ago' },
      website: { status: 'operational', uptime: '99.9%' },
      search: { status: 'operational', message: 'All systems go' },
      notification: { status: 'operational', message: 'Working normally' },
      incidents: [] // No incidents
    };
  }

  static async getJobApplications(userId: string): Promise<{ applications: any[], savedJobs: any[] }> {
    // Retrieve both applications and saved jobs
    return { 
      applications: await getJobApplications(userId),
      savedJobs: await getSavedJobsForUser(userId)
    };
  }
}

export default JobService; 