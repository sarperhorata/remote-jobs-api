export interface Company {
  _id: string;
  id: string;
  name: string;
  logo?: string;
  website?: string;
  description?: string;
  industry?: string;
  founded_year?: number;
  company_size?: string;
  headquarters?: string;
  revenue?: string;
  mission?: string;
  vision?: string;
  values?: string[];
  benefits?: string[];
  technologies?: string[];
  // Eksik alanlar eklendi
  size?: string;
  location?: string;
  techStack?: string[];
  remotePolicy?: string;
  social_links?: {
    linkedin?: string;
    twitter?: string;
    facebook?: string;
    instagram?: string;
  };
  contact_info?: {
    email?: string;
    phone?: string;
    address?: string;
  };
  stats?: {
    total_jobs?: number;
    active_jobs?: number;
    total_employees?: number;
    average_rating?: number;
    review_count?: number;
  };
  created_at: string;
  updated_at: string;
}

export interface CompanyJob {
  _id: string;
  title: string;
  company: {
    _id: string;
    name: string;
    logo?: string;
  };
  location: string;
  job_type: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  description: string;
  requirements: string[];
  benefits: string[];
  is_remote: boolean;
  is_featured: boolean;
  experience_level: string;
  skills: string[];
  created_at: string;
  url: string;
}

export interface GlassdoorReview {
  id: string;
  company_id: string;
  reviewer_name: string;
  reviewer_title?: string;
  reviewer_location?: string;
  rating: number;
  pros?: string;
  cons?: string;
  advice?: string;
  review_date: string;
  helpful_count: number;
  overall_rating: number;
  culture_rating: number;
  work_life_balance_rating: number;
  career_opportunities_rating: number;
  compensation_rating: number;
  management_rating: number;
  job_security_rating: number;
  is_verified: boolean;
  is_former_employee: boolean;
  employment_status: 'current' | 'former';
  length_of_employment?: string;
  job_title?: string;
  department?: string;
}

export interface CompanyCulture {
  company_id: string;
  overall_rating: number;
  culture_rating: number;
  work_life_balance_rating: number;
  career_opportunities_rating: number;
  compensation_rating: number;
  management_rating: number;
  job_security_rating: number;
  total_reviews: number;
  recommended_percentage: number;
  ceo_approval_percentage?: number;
  ceo_rating?: number;
  top_benefits: string[];
  top_cons: string[];
  top_pros: string[];
  company_values: string[];
  work_environment: string;
  diversity_rating?: number;
  inclusion_rating?: number;
  last_updated: string;
}

export interface CompanyStats {
  total_jobs: number;
  active_jobs: number;
  total_employees: number;
  average_rating: number;
  review_count: number;
  application_count: number;
  response_rate: number;
  average_response_time: number;
  remote_jobs_percentage: number;
  featured_jobs_count: number;
}

export interface JobFilter {
  keywords?: string;
  location?: string;
  job_type?: string;
  experience_level?: string;
  salary_min?: number;
  salary_max?: number;
  is_remote?: boolean;
  skills?: string[];
  department?: string;
}

export interface ReviewFilter {
  rating?: number;
  employment_status?: 'current' | 'former' | 'all';
  department?: string;
  job_title?: string;
  date_range?: 'all' | 'last_month' | 'last_3_months' | 'last_year';
  verified_only?: boolean;
  sort_by?: 'date' | 'rating' | 'helpful';
}

export interface TabType {
  id: string;
  label: string;
  icon: string;
  count?: number;
  disabled?: boolean;
}

export interface CompanyProfileData {
  company: Company;
  jobs: CompanyJob[];
  culture: CompanyCulture;
  reviews: GlassdoorReview[];
  stats: CompanyStats;
} 