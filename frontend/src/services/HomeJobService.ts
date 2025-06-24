import { Job } from '../types/job';

// Mock data for jobs
const MOCK_JOBS: Job[] = [
  {
    id: '1',
    title: 'Senior Full Stack Developer',
    companyId: '1',
    company: { id: '1', name: 'TechCorp', logo: 'https://via.placeholder.com/150' },
    description: 'We are looking for a senior full stack developer to join our team.',
    requirements: ['5+ years experience', 'React expertise', 'Node.js knowledge'],
    responsibilities: ['Lead development', 'Mentor junior developers'],
    skills: ['React', 'TypeScript', 'Node.js'],
    location: 'Remote',
    job_type: 'Full-time',
    salary: { currency: 'USD' },
    experience: { min: 3, max: 8 },
    education: 'Bachelor',
    benefits: ['Health Insurance', 'Flexible Schedule'],
    applicationUrl: 'https://example.com/apply',
    source: 'company',
    sourceUrl: 'https://techcorp.com/careers',
    status: 'active',
    postedAt: new Date()
  },
  {
    id: '2',
    title: 'Frontend Developer',
    companyId: '2',
    company: { id: '2', name: 'StartupCo', logo: 'https://via.placeholder.com/150' },
    description: 'Join our frontend team to build amazing user experiences.',
    requirements: ['React experience', 'CSS expertise'],
    responsibilities: ['Build UI components', 'Optimize performance'],
    skills: ['React', 'CSS', 'JavaScript'],
    location: 'San Francisco, CA',
    job_type: 'Full-time',
    salary: { currency: 'USD' },
    experience: { min: 2, max: 5 },
    education: 'Bachelor',
    benefits: ['Stock Options', 'Free Lunch'],
    applicationUrl: 'https://example.com/apply',
    source: 'company',
    sourceUrl: 'https://startupco.com/careers',
    status: 'active',
    postedAt: new Date()
  },
  {
    id: '3',
    title: 'Backend Engineer',
    companyId: '3',
    company: { id: '3', name: 'DataFlow', logo: 'https://via.placeholder.com/150' },
    description: 'Build scalable backend systems for our data platform.',
    requirements: ['Python expertise', 'Database knowledge'],
    responsibilities: ['Design APIs', 'Optimize databases'],
    skills: ['Python', 'PostgreSQL', 'Docker'],
    location: 'New York, NY',
    job_type: 'Full-time',
    salary: { currency: 'USD' },
    experience: { min: 3, max: 7 },
    education: 'Bachelor',
    benefits: ['Health Insurance', 'Remote Work'],
    applicationUrl: 'https://example.com/apply',
    source: 'company',
    sourceUrl: 'https://dataflow.com/careers',
    status: 'active',
    postedAt: new Date()
  }
];

// Get featured jobs for homepage (first 3 jobs)
export const getFeaturedJobs = async (): Promise<Job[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));
  return MOCK_JOBS.slice(0, 3);
};

// Get job statistics for homepage
export const getJobStats = async () => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));
  
  return {
    totalJobs: 150,
    newJobsThisWeek: 25,
    activeCompanies: 45,
    remoteJobs: 95
  };
};

// Get all jobs
export const getAllJobs = async (): Promise<Job[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));
  return MOCK_JOBS;
};

// Get job by ID
export const getJobById = async (id: string): Promise<Job | null> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));
  
  const job = MOCK_JOBS.find(job => job.id === id);
  return job || null;
};

// Get recent jobs (sorted by posted date)
export const getRecentJobs = async (limit: number = 5): Promise<Job[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));
  
  return MOCK_JOBS
    .sort((a, b) => b.postedAt.getTime() - a.postedAt.getTime())
    .slice(0, limit);
};

export class HomejobService {
  static getFeaturedJobs = getFeaturedJobs;
  static getJobStats = getJobStats;
  static getAllJobs = getAllJobs;
  static getJobById = getJobById;
  static getRecentJobs = getRecentJobs;
} 