import { Company } from './Company';

export interface Job {
  id?: string;
  _id?: string;
  title: string;
  companyId?: string;
  company: Company | string; // Can be either Company object or string
  companyName?: string; // Company name as string
  companyDisplayName?: string; // Computed company name for display
  companyLogo?: string;
  company_logo?: string; // Additional field for API compatibility
  description: string;
  job_description?: string; // Additional field for API compatibility
  requirements?: string[];
  responsibilities?: string[];
  skills?: string[];
  location: string;
  job_type: string;
  jobType?: string; // Alias for job_type for backward compatibility
  salary?: {
    min?: number;
    max?: number;
    currency: string;
  };
  salary_range?: string; // Additional field for API compatibility
  experience?: {
    min?: number;
    max?: number;
    unit?: string;
  };
  experience_level?: string; // Additional field for API compatibility
  seniority_level?: string; // Additional field for API compatibility
  work_type?: string; // Remote, Hybrid, On-site
  remote_type?: string; // Additional field for API compatibility
  timezone?: string; // Timezone information like "CET +/- 3 HOURS"
  education?: string;
  benefits?: string[];
  applicationUrl?: string;
  applyUrl?: string; // Apply URL for external applications
  apply_url?: string; // Additional field for API compatibility
  url?: string; // Additional field for API compatibility
  sourceUrl?: string; // Source URL where job was found
  source_url?: string; // Additional field for API compatibility
  source?: string;
  status?: string;
  postedAt?: Date;
  posted_date?: string; // Additional field for API compatibility
  created_at?: string; // Additional field for API compatibility
  createdAt?: string; // Alias for created_at
  expiresAt?: Date;
  is_active?: boolean; // Additional field for API compatibility
  isRemote?: boolean; // Remote job indicator
  applicantCount?: number; // Number of applicants
  views_count?: number; // Number of views
  viewsCount?: number; // Alias for views_count for backward compatibility
  applications_count?: number; // Number of applications
  updated_at?: string;
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