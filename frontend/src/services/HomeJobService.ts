import { Job } from '../types/job';

// Mock jobs data
const mockJobs: any[] = [
  {
    id: 1,
    title: 'Head of Product',
    company: 'Atomic',
    logo: 'https://via.placeholder.com/150',
    location: 'Remote',
    type: 'Full-time',
    postedAt: '2024-03-20',
    companyName: 'Atomic',
    companyLogo: 'https://via.placeholder.com/150',
    _id: '1'
  },
  {
    id: 2,
    title: 'Senior Frontend Developer',
    company: 'Tech Corp',
    logo: 'https://via.placeholder.com/150',
    location: 'Remote',
    type: 'Full-time',
    postedAt: '2024-03-21',
    companyName: 'Tech Corp',
    companyLogo: 'https://via.placeholder.com/150',
    _id: '2'
  },
  {
    id: 3,
    title: 'DevOps Engineer',
    company: 'Cloud Inc',
    logo: 'https://via.placeholder.com/150',
    location: 'Remote - US',
    type: 'Full-time',
    postedAt: '2024-03-22',
    companyName: 'Cloud Inc',
    companyLogo: 'https://via.placeholder.com/150',
    _id: '3'
  },
  {
    id: 4,
    title: 'UX/UI Designer',
    company: 'Creative Studio',
    logo: 'https://via.placeholder.com/150',
    location: 'Remote - Europe',
    type: 'Contract',
    postedAt: '2024-03-23',
    companyName: 'Creative Studio',
    companyLogo: 'https://via.placeholder.com/150',
    _id: '4'
  },
  {
    id: 5,
    title: 'Data Scientist',
    company: 'Data Analytics',
    logo: 'https://via.placeholder.com/150',
    location: 'Remote',
    type: 'Full-time',
    postedAt: '2024-03-24',
    companyName: 'Data Analytics',
    companyLogo: 'https://via.placeholder.com/150',
    _id: '5'
  },
  {
    id: 6,
    title: 'Project Manager',
    company: 'Global Systems',
    logo: 'https://via.placeholder.com/150',
    location: 'Remote - APAC',
    type: 'Full-time',
    postedAt: '2024-03-25',
    companyName: 'Global Systems',
    companyLogo: 'https://via.placeholder.com/150',
    _id: '6'
  }
];

class HomeJobService {
  static async getFeaturedJobs(): Promise<any[]> {
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Return mock data
      return mockJobs;
    } catch (error) {
      console.error('Error fetching featured jobs:', error);
      return [];
    }
  }

  static async getJobStats() {
    try {
      // Mock job statistics data
      return {
        totalJobs: '700,374',
        remoteJobs: '35,333',
        hottestCompany: 'CVS (59 applies)',
        jobsLast24h: '39,475',
        totalCompanies: '6,893',
        mostSearchedTerm: '"react"'
      };
    } catch (error) {
      console.error('Error fetching job stats:', error);
      return {
        totalJobs: '700,374',
        remoteJobs: '35,333',
        jobsLast24h: '39,475',
        totalCompanies: '6,893',
      };
    }
  }
}

export { HomeJobService }; 