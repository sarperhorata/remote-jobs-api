import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobApplicationModal from '../../components/JobSearch/JobApplicationModal';
import * as jobService from '../../services/jobService';

// Mock jobService
jest.mock('../../services/jobService', () => ({
  applyToJob: jest.fn(),
  getUserProfile: jest.fn(),
  autoApply: jest.fn()
}));

const mockJobService = jobService as jest.Mocked<typeof jobService>;

const defaultProps = {
  job: {
    id: '1',
    title: 'Frontend Developer',
    company: 'Tech Corp',
    location: 'Istanbul, Turkey',
    description: 'We are looking for a frontend developer...',
    url: 'https://example.com/job',
    salary_min: 50000,
    salary_max: 80000,
    salary_currency: 'USD',
    posted_date: '2024-01-01',
    job_type: 'Full-time',
    experience_level: 'Mid-level',
    skills: ['React', 'TypeScript'],
    benefits: ['Health insurance', 'Remote work'],
    application_deadline: '2024-12-31',
    contact_email: 'hr@techcorp.com',
    contact_phone: '+1234567890',
    application_url: 'https://example.com/apply'
  },
  isOpen: true,
  onClose: jest.fn(),
  onSubmit: jest.fn()
};

const mockUserProfile = {
  id: 'user123',
  full_name: 'John Doe',
  email: 'john.doe@example.com',
  phone: '+1234567890',
  resume_url: 'https://example.com/resume.pdf',
  linkedin_url: 'https://linkedin.com/in/johndoe',
  github_url: 'https://github.com/johndoe',
  portfolio_url: 'https://johndoe.dev',
  skills: ['React', 'TypeScript', 'Node.js'],
  experience_years: 3,
  education: 'Bachelor in Computer Science',
  bio: 'Experienced frontend developer'
};

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('JobApplicationModal', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockJobService.getUserProfile.mockResolvedValue(mockUserProfile);
  });

  it('should render modal with job details', () => {
    renderWithRouter(<JobApplicationModal {...defaultProps} />);
    
    expect(screen.getByText(/Apply to Frontend Developer/i)).toBeInTheDocument();
    expect(screen.getByText(/Tech Corp/i)).toBeInTheDocument();
    expect(screen.getByText(/Istanbul, Turkey/i)).toBeInTheDocument();
  });

  it('should show application methods', () => {
    renderWithRouter(<JobApplicationModal {...defaultProps} />);
    
    expect(screen.getByText(/Choose Application Method/i)).toBeInTheDocument();
    expect(screen.getByText(/Apply on Company Website/i)).toBeInTheDocument();
    expect(screen.getByText(/Apply Through Platform/i)).toBeInTheDocument();
  });

  it('should close modal when close button is clicked', () => {
    renderWithRouter(<JobApplicationModal {...defaultProps} />);
    
    const closeButton = screen.getByRole('button', { name: '' }); // X button
    fireEvent.click(closeButton);

    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  it('should show complete profile message when profile is incomplete', async () => {
    renderWithRouter(<JobApplicationModal {...defaultProps} />);
    
    await waitFor(() => {
      // Use a more specific query to find the alert message
      const alertMessage = screen.getByText(
        /Complete your profile with CV and contact information to enable one-click applications/i
      ).closest('div');
      
      expect(alertMessage).toBeInTheDocument();
    });
  });

  it('should handle external website application', () => {
    renderWithRouter(<JobApplicationModal {...defaultProps} />);
    
    const externalOption = screen.getByText(/Apply on Company Website/i).closest('div');
    fireEvent.click(externalOption!);

    // Should trigger external application
    expect(defaultProps.onSubmit).toHaveBeenCalled();
  });
}); 