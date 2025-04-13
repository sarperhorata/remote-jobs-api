import { Company } from './Company';

export interface Job {
  id: string;
  _id?: string;
  title: string;
  companyId: string;
  company: Company;
  companyName?: string;
  companyLogo?: string;
  description: string;
  requirements: string[];
  responsibilities: string[];
  skills: string[];
  location: string;
  type: string;
  salary: {
    min?: number;
    max?: number;
    currency: string;
  };
  experience: {
    min?: number;
    max?: number;
  };
  education: string;
  benefits: string[];
  applicationUrl: string;
  source: string;
  sourceUrl: string;
  status: string;
  postedAt: Date;
  expiresAt?: Date;
}

export interface JobApplication {
  id: number;
  jobId: number;
  userId: number;
  status: 'pending' | 'accepted' | 'rejected';
  appliedAt: string;
  resume?: string;
  coverLetter?: string;
  job?: Job;
} 