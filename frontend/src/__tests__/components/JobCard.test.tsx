import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import JobCard from '../../components/JobCard';

// Mock AuthContext
const mockAuthContext = {
  isAuthenticated: false,
  user: null,
  login: jest.fn(),
  logout: jest.fn(),
  signup: jest.fn(),
  isLoading: false
};

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('JobCard', () => {
  const mockJob = {
    _id: '1',
    id: '1',
    title: 'Senior Frontend Developer',
    company: {
      id: 'company1',
      name: 'TechCorp',
      logo: '💻'
    },
    location: 'Remote',
    job_type: 'Full-time',
    salary_min: 80000,
    salary_max: 120000,
    salary_currency: 'USD',
    description: 'We are looking for a senior frontend developer...',
    requirements: ['React', 'TypeScript', '5+ years experience'],
    benefits: ['Health insurance', 'Remote work', 'Flexible hours'],
    created_at: '2024-01-15T10:00:00Z',
    url: 'https://example.com/job/1',
    is_active: true,
    is_featured: false,
    is_remote: true,
    experience_level: 'Senior',
    skills: ['React', 'TypeScript', 'JavaScript']
  };

  beforeEach(() => {
    mockAuthContext.isAuthenticated = false;
    mockAuthContext.user = null;
  });

  it('renders job information correctly', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
    expect(screen.getByText('TechCorp')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
    expect(screen.getByText('Full-time')).toBeInTheDocument();
    expect(screen.getByText('$80,000 - $120,000')).toBeInTheDocument();
  });

  it('displays company logo', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    expect(screen.getByText('💻')).toBeInTheDocument();
  });

  it('shows remote badge for remote jobs', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    expect(screen.getByText('🌍 Remote')).toBeInTheDocument();
  });

  it('shows featured badge for featured jobs', () => {
    const featuredJob = { ...mockJob, is_featured: true };
    renderWithProviders(<JobCard job={featuredJob} />);

    expect(screen.getByText('⭐ Featured')).toBeInTheDocument();
  });

  it('displays experience level', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    expect(screen.getByText('Senior')).toBeInTheDocument();
  });

  it('shows skills tags', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
  });

  it('handles missing salary information', () => {
    const jobWithoutSalary = { ...mockJob, salary_min: null, salary_max: null };
    renderWithProviders(<JobCard job={jobWithoutSalary} />);

    expect(screen.queryByText('$80,000 - $120,000')).not.toBeInTheDocument();
  });

  it('handles missing company logo', () => {
    const jobWithoutLogo = { 
      ...mockJob, 
      company: { ...mockJob.company, logo: null } 
    };
    renderWithProviders(<JobCard job={jobWithoutLogo} />);

    // Should show default company initial
    expect(screen.getByText('T')).toBeInTheDocument();
  });

  it('handles missing skills', () => {
    const jobWithoutSkills = { ...mockJob, skills: null };
    renderWithProviders(<JobCard job={jobWithoutSkills} />);

    expect(screen.queryByText('React')).not.toBeInTheDocument();
  });

  it('navigates to job detail page when clicked', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    const jobCard = screen.getByRole('link', { name: /senior frontend developer/i });
    expect(jobCard).toHaveAttribute('href', '/job/1');
  });

  it('shows apply button for authenticated users', () => {
    mockAuthContext.isAuthenticated = true;
    mockAuthContext.user = { _id: 'user1', email: 'test@example.com' };

    renderWithProviders(<JobCard job={mockJob} />);

    expect(screen.getByRole('button', { name: /apply/i })).toBeInTheDocument();
  });

  it('shows login prompt for unauthenticated users', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    expect(screen.getByRole('button', { name: /login to apply/i })).toBeInTheDocument();
  });

  it('handles apply button click for authenticated users', () => {
    mockAuthContext.isAuthenticated = true;
    mockAuthContext.user = { _id: 'user1', email: 'test@example.com' };

    renderWithProviders(<JobCard job={mockJob} />);

    const applyButton = screen.getByRole('button', { name: /apply/i });
    fireEvent.click(applyButton);

    // Should navigate to application page
    expect(window.location.pathname).toBe('/job/1/apply');
  });

  it('handles save job functionality', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    // Should show saved state
    expect(screen.getByRole('button', { name: /saved/i })).toBeInTheDocument();
  });

  it('handles share job functionality', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    const shareButton = screen.getByRole('button', { name: /share/i });
    fireEvent.click(shareButton);

    // Should show share options or copy link
    expect(screen.getByText(/link copied/i)).toBeInTheDocument();
  });

  it('displays job posting date', () => {
    renderWithProviders(<JobCard job={mockJob} />);

    // Should show relative time like "2 hours ago" or "Today"
    expect(screen.getByText(/ago|today|yesterday/i)).toBeInTheDocument();
  });

  it('handles different job types', () => {
    const partTimeJob = { ...mockJob, job_type: 'Part-time' };
    renderWithProviders(<JobCard job={partTimeJob} />);

    expect(screen.getByText('Part-time')).toBeInTheDocument();
  });

  it('handles different experience levels', () => {
    const juniorJob = { ...mockJob, experience_level: 'Junior' };
    renderWithProviders(<JobCard job={juniorJob} />);

    expect(screen.getByText('Junior')).toBeInTheDocument();
  });

  it('handles non-remote jobs', () => {
    const onSiteJob = { ...mockJob, is_remote: false, location: 'New York, NY' };
    renderWithProviders(<JobCard job={onSiteJob} />);

    expect(screen.getByText('New York, NY')).toBeInTheDocument();
    expect(screen.queryByText('🌍 Remote')).not.toBeInTheDocument();
  });

  it('handles jobs without requirements', () => {
    const jobWithoutRequirements = { ...mockJob, requirements: null };
    renderWithProviders(<JobCard job={jobWithoutRequirements} />);

    // Should still render without crashing
    expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
  });

  it('handles jobs without benefits', () => {
    const jobWithoutBenefits = { ...mockJob, benefits: null };
    renderWithProviders(<JobCard job={jobWithoutBenefits} />);

    // Should still render without crashing
    expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
  });

  it('applies custom className prop', () => {
    renderWithProviders(<JobCard job={mockJob} className="custom-class" />);

    const jobCard = screen.getByRole('article');
    expect(jobCard).toHaveClass('custom-class');
  });

  it('handles compact view mode', () => {
    renderWithProviders(<JobCard job={mockJob} compact={true} />);

    // Should render in compact mode with less information
    expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
    expect(screen.getByText('TechCorp')).toBeInTheDocument();
    // Should not show detailed description in compact mode
    expect(screen.queryByText('We are looking for a senior frontend developer...')).not.toBeInTheDocument();
  });
});
