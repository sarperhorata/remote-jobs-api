// Job related types
export interface Job {
  id: string;
  company: string;
  job_title: string;
  link: string;
  description?: string;
  location?: string;
  salary_range?: string;
  requirements?: string[];
  posted_date?: string;
}

// User related types
export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

// Authentication related types
export interface Token {
  access_token: string;
  token_type: string;
}

export interface ApiKey {
  api_key: string;
  owner: string;
  message: string;
}

// System related types
export interface SystemStatus {
  status: string;
  uptime: number;
  lastUpdated: string;
  jobs: {
    total: number;
    sources: Record<string, number>;
  };
} 