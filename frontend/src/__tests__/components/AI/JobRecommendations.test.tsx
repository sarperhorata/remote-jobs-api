import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AIJobRecommendations from '../../../components/AI/JobRecommendations';

// Mock the API config
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockResolvedValue('http://localhost:8000')
}));

// Mock fetch
global.fetch = jest.fn();

// Mock JobCard component
jest.mock('../../components/JobCard/JobCard', () => {
  return function MockJobCard({ job }: { job: any }) {
    return (
      <div data-testid={`job-card-${job.id}`}>
        <h3>{job.title}</h3>
        <p>{job.company}</p>
      </div>
    );
  };
});

const mockJobs = [
  {
    id: '1',
    title: 'Senior React Developer',
    company: 'Tech Corp',
    location: 'Remote',
    salary: '$120k - $150k',
    type: 'Full-time',
    description: 'We are looking for a senior React developer...',
    requirements: ['React', 'TypeScript', '5+ years experience'],
    benefits: ['Health insurance', '401k', 'Remote work'],
    posted_date: '2024-01-15',
    application_deadline: '2024-02-15',
    company_logo: 'https://example.com/logo.png',
    job_url: 'https://example.com/job/1'
  },
  {
    id: '2',
    title: 'Frontend Engineer',
    company: 'Startup Inc',
    location: 'San Francisco, CA',
    salary: '$100k - $130k',
    type: 'Full-time',
    description: 'Join our growing team...',
    requirements: ['JavaScript', 'React', '3+ years experience'],
    benefits: ['Stock options', 'Flexible hours'],
    posted_date: '2024-01-10',
    application_deadline: '2024-02-10',
    company_logo: 'https://example.com/logo2.png',
    job_url: 'https://example.com/job/2'
  }
];

const mockSkillsDemand = [
  {
    skill: 'React',
    demand_count: 1250,
    average_salary: 120000,
    company_count: 450,
    trend: 'increasing'
  },
  {
    skill: 'Python',
    demand_count: 980,
    average_salary: 110000,
    company_count: 320,
    trend: 'stable'
  }
];

const mockSalaryInsights = {
  average_salary: 115000,
  salary_range: {
    min: 80000,
    max: 150000
  },
  total_jobs_analyzed: 2500,
  companies_offering: 180,
  market_trend: 'increasing'
};

const renderJobRecommendations = (props = {}) => {
  return render(<AIJobRecommendations {...props} />);
};

describe('AIJobRecommendations', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    test('renders loading state initially', () => {
      (global.fetch as jest.Mock).mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderJobRecommendations();
      
      expect(screen.getByText('AI is analyzing job opportunities...')).toBeInTheDocument();
      expect(screen.getByText(/brain/i)).toBeInTheDocument();
    });

    test('renders with default props', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('AI-Powered Insights')).toBeInTheDocument();
        expect(screen.getByText('Personalized job recommendations and market analysis')).toBeInTheDocument();
      });
    });

    test('renders with custom className', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations({ className: 'custom-class' });

      await waitFor(() => {
        const container = screen.getByText('AI-Powered Insights').closest('div');
        expect(container).toHaveClass('custom-class');
      });
    });

    test('renders tab navigation', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('Recommendations')).toBeInTheDocument();
        expect(screen.getByText('Skills Demand')).toBeInTheDocument();
        expect(screen.getByText('Salary Insights')).toBeInTheDocument();
      });
    });
  });

  describe('Data Loading', () => {
    test('loads recommendations successfully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('Top Matches for You')).toBeInTheDocument();
        expect(screen.getByText('2 recommendations')).toBeInTheDocument();
        expect(screen.getByTestId('job-card-1')).toBeInTheDocument();
        expect(screen.getByTestId('job-card-2')).toBeInTheDocument();
      });
    });

    test('loads skills demand data successfully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ skills_demand: mockSkillsDemand })
      });

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('Skills Demand')).toBeInTheDocument();
      });

      const skillsTab = screen.getByText('Skills Demand');
      fireEvent.click(skillsTab);

      await waitFor(() => {
        expect(screen.getByText('React')).toBeInTheDocument();
        expect(screen.getByText('Python')).toBeInTheDocument();
      });
    });

    test('loads salary insights data successfully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ salary_insights: mockSalaryInsights })
      });

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('Salary Insights')).toBeInTheDocument();
      });

      const salaryTab = screen.getByText('Salary Insights');
      fireEvent.click(salaryTab);

      await waitFor(() => {
        expect(screen.getByText(/115,000/i)).toBeInTheDocument();
        expect(screen.getByText(/80,000/i)).toBeInTheDocument();
        expect(screen.getByText(/150,000/i)).toBeInTheDocument();
      });
    });

    test('handles API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('AI Analysis Unavailable')).toBeInTheDocument();
        expect(screen.getByText('Network error')).toBeInTheDocument();
        expect(screen.getByText('Retry Analysis')).toBeInTheDocument();
      });
    });

    test('handles partial API failures', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ recommendations: mockJobs })
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 500
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ salary_insights: mockSalaryInsights })
        });

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('Top Matches for You')).toBeInTheDocument();
      });
    });
  });

  describe('Tab Navigation', () => {
    beforeEach(async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations();
      await waitFor(() => {
        expect(screen.getByText('AI-Powered Insights')).toBeInTheDocument();
      });
    });

    test('switches to skills demand tab', async () => {
      const skillsTab = screen.getByText('Skills Demand');
      fireEvent.click(skillsTab);

      expect(skillsTab.closest('button')).toHaveClass('bg-white');
      expect(screen.getByText('Recommendations').closest('button')).not.toHaveClass('bg-white');
    });

    test('switches to salary insights tab', async () => {
      const salaryTab = screen.getByText('Salary Insights');
      fireEvent.click(salaryTab);

      expect(salaryTab.closest('button')).toHaveClass('bg-white');
      expect(screen.getByText('Recommendations').closest('button')).not.toHaveClass('bg-white');
    });

    test('returns to recommendations tab', async () => {
      const skillsTab = screen.getByText('Skills Demand');
      const recommendationsTab = screen.getByText('Recommendations');
      
      fireEvent.click(skillsTab);
      fireEvent.click(recommendationsTab);

      expect(recommendationsTab.closest('button')).toHaveClass('bg-white');
      expect(skillsTab.closest('button')).not.toHaveClass('bg-white');
    });
  });

  describe('Recommendations Tab', () => {
    beforeEach(async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations();
      await waitFor(() => {
        expect(screen.getByText('Top Matches for You')).toBeInTheDocument();
      });
    });

    test('displays job recommendations', () => {
      expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
      expect(screen.getByText('Frontend Engineer')).toBeInTheDocument();
      expect(screen.getByText('Tech Corp')).toBeInTheDocument();
      expect(screen.getByText('Startup Inc')).toBeInTheDocument();
    });

    test('shows recommendation count', () => {
      expect(screen.getByText('2 recommendations')).toBeInTheDocument();
    });

    test('handles empty recommendations', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: [] })
      });

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('No recommendations available')).toBeInTheDocument();
      });
    });
  });

  describe('Skills Demand Tab', () => {
    beforeEach(async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ skills_demand: mockSkillsDemand })
      });

      renderJobRecommendations();
      await waitFor(() => {
        expect(screen.getByText('AI-Powered Insights')).toBeInTheDocument();
      });

      const skillsTab = screen.getByText('Skills Demand');
      fireEvent.click(skillsTab);
    });

    test('displays skills demand data', async () => {
      await waitFor(() => {
        expect(screen.getByText('React')).toBeInTheDocument();
        expect(screen.getByText('Python')).toBeInTheDocument();
        expect(screen.getByText('1,250')).toBeInTheDocument();
        expect(screen.getByText('980')).toBeInTheDocument();
      });
    });

    test('shows skill demand metrics', async () => {
      await waitFor(() => {
        expect(screen.getByText(/120,000/i)).toBeInTheDocument();
        expect(screen.getByText(/110,000/i)).toBeInTheDocument();
        expect(screen.getByText('450')).toBeInTheDocument();
        expect(screen.getByText('320')).toBeInTheDocument();
      });
    });

    test('handles empty skills data', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ skills_demand: [] })
      });

      renderJobRecommendations();

      const skillsTab = screen.getByText('Skills Demand');
      fireEvent.click(skillsTab);

      await waitFor(() => {
        expect(screen.getByText('No skills demand data available')).toBeInTheDocument();
      });
    });
  });

  describe('Salary Insights Tab', () => {
    beforeEach(async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ salary_insights: mockSalaryInsights })
      });

      renderJobRecommendations();
      await waitFor(() => {
        expect(screen.getByText('AI-Powered Insights')).toBeInTheDocument();
      });

      const salaryTab = screen.getByText('Salary Insights');
      fireEvent.click(salaryTab);
    });

    test('displays salary insights data', async () => {
      await waitFor(() => {
        expect(screen.getByText(/115,000/i)).toBeInTheDocument();
        expect(screen.getByText(/80,000/i)).toBeInTheDocument();
        expect(screen.getByText(/150,000/i)).toBeInTheDocument();
        expect(screen.getByText('2,500')).toBeInTheDocument();
        expect(screen.getByText('180')).toBeInTheDocument();
      });
    });

    test('shows market trend', async () => {
      await waitFor(() => {
        expect(screen.getByText('increasing')).toBeInTheDocument();
      });
    });

    test('handles null salary insights', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ salary_insights: null })
      });

      renderJobRecommendations();

      const salaryTab = screen.getByText('Salary Insights');
      fireEvent.click(salaryTab);

      await waitFor(() => {
        expect(screen.getByText('No salary insights available')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    test('shows retry button on error', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('Retry Analysis')).toBeInTheDocument();
      });
    });

    test('retries data loading when retry button is clicked', async () => {
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ recommendations: mockJobs })
        });

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByText('Retry Analysis')).toBeInTheDocument();
      });

      const retryButton = screen.getByText('Retry Analysis');
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText('Top Matches for You')).toBeInTheDocument();
      });
    });
  });

  describe('API Calls', () => {
    test('makes correct API calls with proper parameters', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations({ userId: 'test-user', limit: 10 });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/api/ai/recommendations?user_id=test-user&limit=10'
        );
        expect(global.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/api/ai/skills-demand?limit=10'
        );
        expect(global.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/api/ai/salary-insights?position=developer'
        );
      });
    });

    test('uses default parameters when not provided', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations();

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/api/ai/recommendations?user_id=demo_user&limit=6'
        );
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper heading structure', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations();

      await waitFor(() => {
        expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('AI-Powered Insights');
        expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Top Matches for You');
      });
    });

    test('has proper button roles', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockJobs })
      });

      renderJobRecommendations();

      await waitFor(() => {
        const tabButtons = screen.getAllByRole('button');
        expect(tabButtons).toHaveLength(3);
      });
    });
  });
});