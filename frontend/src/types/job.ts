import { Company } from './Company';

export interface Job {
  id?: string;
  _id?: string;
  title: string;
  companyId?: string;
  company: Company | string; // Can be either Company object or string
  companyName?: string;
  companyLogo?: string;
  company_logo?: string; // Additional field for API compatibility
  description: string;
  requirements?: string[];
  responsibilities?: string[];
  skills?: string[];
  location: string;
  job_type: string;
  salary?: {
    min?: number;
    max?: number;
    currency: string;
  };
  salary_range?: string; // Additional field for API compatibility
  experience?: {
    min?: number;
    max?: number;
  };
  education?: string;
  benefits?: string[];
  applicationUrl?: string;
  url?: string; // Additional field for API compatibility
  source?: string;
  sourceUrl?: string;
  status?: string;
  postedAt?: Date;
  created_at?: string; // Additional field for API compatibility
  expiresAt?: Date;
  is_active?: boolean; // Additional field for API compatibility
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