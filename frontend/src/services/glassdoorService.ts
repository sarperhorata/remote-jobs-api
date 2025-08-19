import { getApiUrl } from '../utils/apiConfig';

// Glassdoor API response types
export interface GlassdoorCompanyInfo {
  id: string;
  name: string;
  website: string;
  industry: string;
  size: string;
  founded: string;
  revenue: string;
  headquarters: string;
  mission: string;
  values: string[];
  benefits: string[];
  workLifeBalance: number;
  cultureAndValues: number;
  careerOpportunities: number;
  compensationAndBenefits: number;
  seniorManagement: number;
  overallRating: number;
  totalReviews: number;
  recommendToFriend: number;
  ceoApproval: number;
  ceoName?: string;
  ceoImage?: string;
}

export interface GlassdoorReview {
  id: string;
  author: string;
  title: string;
  pros: string;
  cons: string;
  advice: string;
  rating: number;
  date: string;
  jobTitle: string;
  location: string;
  employmentStatus: string;
  helpfulCount: number;
  isVerified: boolean;
  sentiment: 'positive' | 'negative' | 'neutral';
}

export interface GlassdoorCultureMetrics {
  overallRating: number;
  totalReviews: number;
  categories: {
    workLifeBalance: number;
    cultureAndValues: number;
    careerOpportunities: number;
    compensationAndBenefits: number;
    seniorManagement: number;
  };
  trends: {
    month: string;
    rating: number;
    reviewCount: number;
  }[];
  topBenefits: string[];
  topPros: string[];
  topCons: string[];
}

export interface GlassdoorSearchParams {
  companyName: string;
  location?: string;
  industry?: string;
}

// Glassdoor API Base URL (using our backend proxy)
const GLASSDOOR_API_BASE = '/api/v1/glassdoor';

// Get company information from Glassdoor
export const getGlassdoorCompanyInfo = async (
  companyName: string,
  location?: string
): Promise<GlassdoorCompanyInfo> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const params = new URLSearchParams({
      company: companyName,
      ...(location && { location })
    });

    const response = await fetch(`${apiUrl}${GLASSDOOR_API_BASE}/company?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch company info: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching Glassdoor company info:', error);
    throw error;
  }
};

// Get company reviews from Glassdoor
export const getGlassdoorReviews = async (
  companyName: string,
  page: number = 1,
  limit: number = 10,
  filters?: {
    rating?: number;
    jobTitle?: string;
    location?: string;
    employmentStatus?: string;
    sentiment?: string;
  }
): Promise<{
  reviews: GlassdoorReview[];
  total: number;
  page: number;
  totalPages: number;
}> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const params = new URLSearchParams({
      company: companyName,
      page: page.toString(),
      limit: limit.toString(),
      ...(filters?.rating && { rating: filters.rating.toString() }),
      ...(filters?.jobTitle && { jobTitle: filters.jobTitle }),
      ...(filters?.location && { location: filters.location }),
      ...(filters?.employmentStatus && { employmentStatus: filters.employmentStatus }),
      ...(filters?.sentiment && { sentiment: filters.sentiment })
    });

    const response = await fetch(`${apiUrl}${GLASSDOOR_API_BASE}/reviews?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch reviews: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching Glassdoor reviews:', error);
    throw error;
  }
};

// Get company culture metrics from Glassdoor
export const getGlassdoorCultureMetrics = async (
  companyName: string
): Promise<GlassdoorCultureMetrics> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const params = new URLSearchParams({
      company: companyName
    });

    const response = await fetch(`${apiUrl}${GLASSDOOR_API_BASE}/culture?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch culture metrics: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching Glassdoor culture metrics:', error);
    throw error;
  }
};

// Search companies on Glassdoor
export const searchGlassdoorCompanies = async (
  searchParams: GlassdoorSearchParams,
  page: number = 1,
  limit: number = 10
): Promise<{
  companies: GlassdoorCompanyInfo[];
  total: number;
  page: number;
  totalPages: number;
}> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const params = new URLSearchParams({
      query: searchParams.companyName,
      page: page.toString(),
      limit: limit.toString(),
      ...(searchParams.location && { location: searchParams.location }),
      ...(searchParams.industry && { industry: searchParams.industry })
    });

    const response = await fetch(`${apiUrl}${GLASSDOOR_API_BASE}/search?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to search companies: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error searching Glassdoor companies:', error);
    throw error;
  }
};

// Get review statistics
export const getReviewStatistics = async (
  companyName: string
): Promise<{
  totalReviews: number;
  averageRating: number;
  ratingDistribution: {
    [key: number]: number;
  };
  recentTrends: {
    month: string;
    averageRating: number;
    reviewCount: number;
  }[];
}> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const params = new URLSearchParams({
      company: companyName
    });

    const response = await fetch(`${apiUrl}${GLASSDOOR_API_BASE}/statistics?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch review statistics: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching review statistics:', error);
    throw error;
  }
};

// Submit a review (for authenticated users)
export const submitReview = async (
  companyName: string,
  reviewData: {
    rating: number;
    title: string;
    pros: string;
    cons: string;
    advice?: string;
    jobTitle: string;
    location: string;
    employmentStatus: string;
  }
): Promise<{ success: boolean; reviewId?: string; message: string }> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    if (!token) {
      throw new Error('Authentication required to submit review');
    }

    const response = await fetch(`${apiUrl}${GLASSDOOR_API_BASE}/reviews`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        company: companyName,
        ...reviewData
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to submit review: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error submitting review:', error);
    throw error;
  }
};

// Rate a review as helpful
export const rateReviewHelpful = async (
  reviewId: string,
  helpful: boolean
): Promise<{ success: boolean; helpfulCount: number }> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    if (!token) {
      throw new Error('Authentication required to rate review');
    }

    const response = await fetch(`${apiUrl}${GLASSDOOR_API_BASE}/reviews/${reviewId}/rate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ helpful })
    });

    if (!response.ok) {
      throw new Error(`Failed to rate review: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error rating review:', error);
    throw error;
  }
};

// Get company comparison data
export const getCompanyComparison = async (
  companyNames: string[]
): Promise<{
  companies: GlassdoorCompanyInfo[];
  comparison: {
    overallRating: number[];
    workLifeBalance: number[];
    cultureAndValues: number[];
    careerOpportunities: number[];
    compensationAndBenefits: number[];
    seniorManagement: number[];
  };
}> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const params = new URLSearchParams({
      companies: companyNames.join(',')
    });

    const response = await fetch(`${apiUrl}${GLASSDOOR_API_BASE}/compare?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch company comparison: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching company comparison:', error);
    throw error;
  }
};

// Mock data for development/testing
export const getMockGlassdoorData = (companyName: string) => {
  return {
    companyInfo: {
      id: 'mock-1',
      name: companyName,
      website: 'https://example.com',
      industry: 'Technology',
      size: '1000-5000 employees',
      founded: '2010',
      revenue: '$100M - $500M',
      headquarters: 'San Francisco, CA',
      mission: 'To revolutionize the way people work',
      values: ['Innovation', 'Transparency', 'Diversity', 'Excellence'],
      benefits: ['Health Insurance', '401k', 'Remote Work', 'Flexible Hours'],
      workLifeBalance: 4.2,
      cultureAndValues: 4.5,
      careerOpportunities: 4.1,
      compensationAndBenefits: 4.3,
      seniorManagement: 3.9,
      overallRating: 4.2,
      totalReviews: 1250,
      recommendToFriend: 85,
      ceoApproval: 92,
      ceoName: 'John Doe',
      ceoImage: 'https://example.com/ceo.jpg'
    },
    reviews: [
      {
        id: 'review-1',
        author: 'Anonymous Employee',
        title: 'Great company culture and work-life balance',
        pros: 'Flexible work hours, great team, good benefits',
        cons: 'Sometimes long hours during crunch time',
        advice: 'Be prepared to work hard but you\'ll be rewarded',
        rating: 5,
        date: '2024-01-15',
        jobTitle: 'Software Engineer',
        location: 'San Francisco, CA',
        employmentStatus: 'Full-time',
        helpfulCount: 12,
        isVerified: true,
        sentiment: 'positive'
      }
    ],
    cultureMetrics: {
      overallRating: 4.2,
      totalReviews: 1250,
      categories: {
        workLifeBalance: 4.2,
        cultureAndValues: 4.5,
        careerOpportunities: 4.1,
        compensationAndBenefits: 4.3,
        seniorManagement: 3.9
      },
      trends: [
        { month: '2024-01', rating: 4.2, reviewCount: 45 },
        { month: '2024-02', rating: 4.3, reviewCount: 52 }
      ],
      topBenefits: ['Health Insurance', '401k', 'Remote Work'],
      topPros: ['Great culture', 'Flexible hours', 'Good pay'],
      topCons: ['Long hours', 'High pressure', 'Fast-paced']
    }
  };
}; 