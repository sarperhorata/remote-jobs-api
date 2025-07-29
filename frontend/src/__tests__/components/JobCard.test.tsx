import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobCard from '../../components/JobCard';

// Mock the useAuth hook
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { id: '1', email: 'test@example.com' },
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
  }),
}));

// Mock data
const mockJob = {
  id: '1',
  title: 'Senior React Developer',
  company: 'Tech Corp',
  location: 'Remote',
  salary: '$80k - $120k',
  description: 'We are looking for a senior React developer...',
  job_type: 'Full-time',
  work_type: 'Remote',
  experience_level: 'Senior',
  posted_date: '2024-01-01',
  company_logo: 'https://example.com/logo.png',
  skills: ['React', 'TypeScript', 'Node.js'],
  benefits: ['Health Insurance', '401k', 'Flexible Hours'],
  is_saved: false,
  is_applied: false,
};

const renderWithRouter = (component: React.ReactElement) => {
  return render(component);
};

describe('JobCard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders job information correctly', () => {
    renderWithRouter(<JobCard job={mockJob} />);
    
    expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
    expect(screen.getByText('$80k - $120k')).toBeInTheDocument();
  });

  test('displays job type and work type', () => {
    renderWithRouter(<JobCard job={mockJob} />);
    
    expect(screen.getByText('Full-time')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
  });

  test('shows experience level', () => {
    renderWithRouter(<JobCard job={mockJob} />);
    
    expect(screen.getByText('Senior')).toBeInTheDocument();
  });

  test('displays skills', () => {
    renderWithRouter(<JobCard job={mockJob} />);
    
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
    expect(screen.getByText('Node.js')).toBeInTheDocument();
  });

  test('shows company logo when available', () => {
    renderWithRouter(<JobCard job={mockJob} />);
    
    const logo = screen.getByAltText('Tech Corp logo');
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', 'https://example.com/logo.png');
  });

  test('handles missing company logo gracefully', () => {
    const jobWithoutLogo = { ...mockJob, company_logo: null };
    renderWithRouter(<JobCard job={jobWithoutLogo} />);
    
    // Should still render without crashing
    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
  });

  test('displays posted date', () => {
    renderWithRouter(<JobCard job={mockJob} />);
    
    expect(screen.getByText(/2024-01-01/)).toBeInTheDocument();
  });

  test('shows save button when not saved', () => {
    renderWithRouter(<JobCard job={mockJob} />);
    
    const saveButton = screen.getByRole('button', { name: /save/i });
    expect(saveButton).toBeInTheDocument();
  });

  test('shows unsave button when already saved', () => {
    const savedJob = { ...mockJob, is_saved: true };
    renderWithRouter(<JobCard job={savedJob} />);
    
    const unsaveButton = screen.getByRole('button', { name: /unsave/i });
    expect(unsaveButton).toBeInTheDocument();
  });

  test('shows apply button when not applied', () => {
    renderWithRouter(<JobCard job={mockJob} />);
    
    const applyButton = screen.getByRole('button', { name: /apply/i });
    expect(applyButton).toBeInTheDocument();
  });

  test('shows applied status when already applied', () => {
    const appliedJob = { ...mockJob, is_applied: true };
    renderWithRouter(<JobCard job={appliedJob} />);
    
    expect(screen.getByText(/applied/i)).toBeInTheDocument();
  });
});
