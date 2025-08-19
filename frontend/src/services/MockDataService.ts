import { Company } from '../types/Company';
import { Job } from '../types/job';

// Companies data
const companies: Company[] = [
  {
    _id: '1',
    id: '1',
    name: 'Google',
    website: 'https://careers.google.com',
    logo: 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/google_logo.max-1000x1000.png',
    description: 'Google is an American multinational technology company that specializes in Internet-related services and products.',
    industry: 'Technology',
    size: '10000+',
    location: 'Mountain View, CA',
    remotePolicy: 'Hybrid',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    techStack: ['Python', 'Java', 'C++', 'Go', 'JavaScript', 'TensorFlow', 'Kubernetes'],
    social_links: {
      linkedin: 'https://www.linkedin.com/company/google',
      twitter: 'https://twitter.com/google',
      facebook: 'https://github.com/google'
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    _id: '2',
    id: '2',
    name: 'Microsoft',
    website: 'https://careers.microsoft.com',
    logo: 'https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31',
    description: 'Microsoft Corporation is an American multinational technology corporation which produces computer software, consumer electronics, personal computers, and related services.',
    industry: 'Technology',
    size: '10000+',
    location: 'Redmond, WA',
    remotePolicy: 'Hybrid',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    techStack: ['C#', '.NET', 'Azure', 'TypeScript', 'React', 'PowerShell', 'Docker'],
    social_links: {
      linkedin: 'https://www.linkedin.com/company/microsoft',
      twitter: 'https://twitter.com/microsoft',
      facebook: 'https://github.com/microsoft'
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    _id: '3',
    id: '3',
    name: 'Amazon',
    website: 'https://www.amazon.jobs',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/4/4a/Amazon_icon.svg',
    description: 'Amazon.com, Inc. is an American multinational technology company which focuses on e-commerce, cloud computing, digital streaming, and artificial intelligence.',
    industry: 'Technology',
    size: '10000+',
    location: 'Seattle, WA',
    remotePolicy: 'Hybrid',
    benefits: ['Health Insurance', '401k', 'Stock Options', 'Flexible Hours', 'Remote Work'],
    techStack: ['Java', 'Python', 'AWS', 'React', 'Node.js', 'Docker', 'Kubernetes'],
    social_links: {
      linkedin: 'https://www.linkedin.com/company/amazon',
      twitter: 'https://twitter.com/amazon',
      facebook: 'https://github.com/aws'
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

// Time zones
const timeZones = [
  { region: 'US Remote', gmt: 'GMT-8 to GMT-4' },
  { region: 'Europe Remote', gmt: 'GMT+0 to GMT+3' },
  { region: 'Asia Pacific Remote', gmt: 'GMT+7 to GMT+12' }
];

// Job categories
const categories = [
  'Software Development',
  'Data Science',
  'DevOps',
  'Product Management',
  'UX/UI Design'
];

// Job types
const jobTypes = [
  'Full-time',
  'Part-time',
  'Contract',
  'Freelance',
  'Internship'
];

// Generate jobs
const jobs: Job[] = [];
let jobId = 1;

companies.forEach(company => {
  // Generate 3-5 jobs per company
  const numJobs = Math.floor(Math.random() * 3) + 3;
  for (let i = 0; i < numJobs; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)];
    const timeZone = timeZones[Math.floor(Math.random() * timeZones.length)];
    const type = jobTypes[Math.floor(Math.random() * jobTypes.length)];
    
    jobs.push({
      id: String(jobId++),
      title: `${category} - ${company.name}`,
      companyId: company.id,
      company: company,
      description: `We are looking for a ${category} professional to join our team at ${company.name}.`,
      requirements: [
        '5+ years of experience',
        'Strong communication skills',
        'Team player',
        'Problem-solving abilities'
      ],
      responsibilities: [
        'Develop and maintain software applications',
        'Collaborate with cross-functional teams',
        'Write clean, maintainable code',
        'Participate in code reviews'
      ],
      skills: company.techStack?.slice(0, 5) || [],
      location: timeZone.region,
      job_type: type,
      salary: {
        min: 80000,
        max: 150000,
        currency: 'USD'
      },
      experience: {
        min: 3,
        max: 8
      },
      education: 'Bachelor\'s degree in Computer Science or related field',
      benefits: company.benefits || ['Health Insurance', 'Flexible Hours'],
      applicationUrl: `${company.website || 'https://example.com'}/apply`,
      source: 'Direct',
      sourceUrl: company.website || 'https://example.com',
      status: 'active',
      postedAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000),
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
    });
  }
});

export class MockDataService {
  static getCompanies(): Promise<Company[]> {
    return Promise.resolve(companies);
  }

  static getCompanyById(id: string): Promise<Company | null> {
    const company = companies.find(c => c.id === id);
    return Promise.resolve(company || null);
  }

  static getJobs(filters?: any): Promise<Job[]> {
    let filteredJobs = [...jobs];
    
    if (filters) {
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        filteredJobs = filteredJobs.filter(job => 
          job.title.toLowerCase().includes(searchLower) || 
          job.description.toLowerCase().includes(searchLower) ||
          job.skills.some(skill => skill.toLowerCase().includes(searchLower))
        );
      }
      
      if (filters.location) {
        filteredJobs = filteredJobs.filter(job => job.location === filters.location);
      }
      
      if (filters.type) {
        filteredJobs = filteredJobs.filter(job => job.job_type === filters.type);
      }
      
      if (filters.category) {
        filteredJobs = filteredJobs.filter(job => job.title.includes(filters.category));
      }
    }
    
    return Promise.resolve(filteredJobs);
  }

  static getJobById(id: string): Promise<Job | null> {
    const job = jobs.find(j => j.id === id);
    return Promise.resolve(job || null);
  }

  static getSimilarJobs(jobId: string): Promise<Job[]> {
    const job = jobs.find(j => j.id === jobId);
    if (!job) return Promise.resolve([]);
    
    const similarJobs = jobs
      .filter(j => j.id !== jobId && 
                 (j.companyId === job.companyId || 
                  j.skills.some(skill => job.skills.includes(skill))))
      .slice(0, 3);
      
    return Promise.resolve(similarJobs);
  }

  static async getFeaturedJobs(): Promise<Job[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Return 3 featured jobs
    return jobs.slice(0, 3);
  }
} 