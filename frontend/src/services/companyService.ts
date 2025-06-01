import { Company } from '../types/Company';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

export const getCompanies = async (params?: {
  page?: number;
  limit?: number;
  search?: string;
}): Promise<{ companies: Company[]; total: number }> => {
  const searchParams = new URLSearchParams();
  
  if (params?.page) searchParams.append('page', params.page.toString());
  if (params?.limit) searchParams.append('limit', params.limit.toString());
  if (params?.search) searchParams.append('search', params.search);
  
  const response = await fetch(`${API_BASE_URL}/companies?${searchParams}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch companies');
  }
  
  const data = await response.json();
  return {
    companies: data.items || data.companies || [],
    total: data.total || 0
  };
};

export const getCompanyById = async (id: string): Promise<Company> => {
  const response = await fetch(`${API_BASE_URL}/companies/${id}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch company');
  }
  
  return response.json();
}; 