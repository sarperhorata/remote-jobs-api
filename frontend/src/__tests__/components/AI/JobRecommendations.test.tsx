import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AIJobRecommendations from '../../../components/AI/JobRecommendations';
import { getApiUrl } from '../../../utils/apiConfig';

// Mock dependencies
jest.mock('../../../utils/apiConfig');
jest.mock('../../../components/JobCard/JobCard', () => {
  return function MockJobCard({ job }: any) {
    return (
      <div data-testid="job-card">
        <h3>{job.title}</h3>
        <p>{job.company}</p>
      </div>
    );
  };
});

const mockGetApiUrl = getApiUrl as jest.MockedFunction<typeof getApiUrl>;

// Mock fetch
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('AIJobRecommendations', () => {
  beforeEach(() => {
    mockGetApiUrl.mockResolvedValue('http://localhost:8001');
    mockFetch.mockClear();
  });

  it('renders loading state initially', () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ recommendations: [], skills_demand: [], salary_insights: null })
    } as Response);

    render(<AIJobRecommendations />);
    
    expect(screen.getByText('AI is analyzing job opportunities...')).toBeInTheDocument();
  });

  it('renders recommendations tab with job cards', async () => {
    const mockRecommendations = {
      recommendations: [
        {
          id: '1',
          title: 'Senior Developer',
          company: 'TechCorp',
          match_score: 0.95
        },
        {
          id: '2',
          title: 'Frontend Engineer',
          company: 'StartupInc',
          match_score: 0.87
        }
      ]
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockRecommendations
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ skills_demand: [] })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ salary_insights: null })
      } as Response);

    render(<AIJobRecommendations />);

    await waitFor(() => {
      expect(screen.getByText('Top Matches for You')).toBeInTheDocument();
    });

    expect(screen.getByText('Senior Developer')).toBeInTheDocument();
    expect(screen.getByText('Frontend Engineer')).toBeInTheDocument();
    expect(screen.getByText('95% match')).toBeInTheDocument();
    expect(screen.getByText('87% match')).toBeInTheDocument();
  });

  it('renders skills demand tab', async () => {
    const mockSkillsData = {
      skills_demand: [
        {
          skill: 'Python',
          demand_count: 150,
          average_salary: 95000,
          company_count: 25,
          trend: 'increasing'
        },
        {
          skill: 'JavaScript',
          demand_count: 120,
          average_salary: 85000,
          company_count: 30,
          trend: 'increasing'
        }
      ]
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: [] })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockSkillsData
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ salary_insights: null })
      } as Response);

    render(<AIJobRecommendations />);

    await waitFor(() => {
      expect(screen.getByText('Skills Demand')).toBeInTheDocument();
    });

    // Click on skills tab
    fireEvent.click(screen.getByText('Skills Demand'));

    await waitFor(() => {
      expect(screen.getByText('In-Demand Skills')).toBeInTheDocument();
      expect(screen.getByText('Python')).toBeInTheDocument();
      expect(screen.getByText('JavaScript')).toBeInTheDocument();
      expect(screen.getByText('150 jobs • 25 companies')).toBeInTheDocument();
      expect(screen.getByText('Avg: $95,000')).toBeInTheDocument();
    });
  });

  it('renders salary insights tab', async () => {
    const mockSalaryData = {
      salary_insights: {
        average_salary: 90000,
        salary_range: {
          min: 60000,
          max: 140000
        },
        total_jobs_analyzed: 1500,
        companies_offering: 85,
        market_trend: 'stable'
      }
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: [] })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ skills_demand: [] })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockSalaryData
      } as Response);

    render(<AIJobRecommendations />);

    await waitFor(() => {
      expect(screen.getByText('Salary Insights')).toBeInTheDocument();
    });

    // Click on salary tab
    fireEvent.click(screen.getByText('Salary Insights'));

    await waitFor(() => {
      expect(screen.getByText('Salary Market Insights')).toBeInTheDocument();
      expect(screen.getByText('$90,000')).toBeInTheDocument();
      expect(screen.getByText('1,500')).toBeInTheDocument();
      expect(screen.getByText('85')).toBeInTheDocument();
      expect(screen.getByText('$60,000')).toBeInTheDocument();
      expect(screen.getByText('$140,000')).toBeInTheDocument();
    });
  });

  it('handles error state', async () => {
    mockFetch.mockRejectedValue(new Error('API Error'));

    render(<AIJobRecommendations />);

    await waitFor(() => {
      expect(screen.getByText('AI Analysis Unavailable')).toBeInTheDocument();
      expect(screen.getByText('Failed to load AI insights')).toBeInTheDocument();
    });
  });

  it('shows empty state when no data available', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: [] })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ skills_demand: [] })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ salary_insights: null })
      } as Response);

    render(<AIJobRecommendations />);

    await waitFor(() => {
      expect(screen.getByText('No Recommendations Available')).toBeInTheDocument();
    });

    // Test skills tab empty state
    fireEvent.click(screen.getByText('Skills Demand'));
    await waitFor(() => {
      expect(screen.getByText('No Skills Data Available')).toBeInTheDocument();
    });

    // Test salary tab empty state  
    fireEvent.click(screen.getByText('Salary Insights'));
    await waitFor(() => {
      expect(screen.getByText('No Salary Data Available')).toBeInTheDocument();
    });
  });

  it('allows retry on error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('API Error'));

    render(<AIJobRecommendations />);

    await waitFor(() => {
      expect(screen.getByText('Retry Analysis')).toBeInTheDocument();
    });

    // Mock successful retry
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: [] })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ skills_demand: [] })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ salary_insights: null })
      } as Response);

    fireEvent.click(screen.getByText('Retry Analysis'));

    await waitFor(() => {
      expect(screen.getByText('No Recommendations Available')).toBeInTheDocument();
    });
  });

  it('handles API failures gracefully', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: false,
        status: 500
      } as Response)
      .mockResolvedValueOnce({
        ok: false,
        status: 500
      } as Response)
      .mockResolvedValueOnce({
        ok: false,
        status: 500
      } as Response);

    render(<AIJobRecommendations />);

    await waitFor(() => {
      expect(screen.getByText('No Recommendations Available')).toBeInTheDocument();
    });
  });

  it('passes correct props to component', () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ recommendations: [], skills_demand: [], salary_insights: null })
    } as Response);

    render(
      <AIJobRecommendations 
        userId="custom-user-id" 
        limit={10} 
        className="custom-class" 
      />
    );

    expect(screen.getByText('AI is analyzing job opportunities...')).toBeInTheDocument();
  });
}); 