import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { JobCard } from '../../components/JobCard';
import '@testing-library/jest-dom';

const mockJob = {
  id: '1',
  title: 'Senior React Developer',
  company: 'TechCorp Inc.',
  location: 'Remote',
  description: 'We are looking for a senior React developer to join our team.',
  job_type: 'Full-time',
  salary: {
    min: 80000,
    max: 120000,
    currency: 'USD'
  },
  postedAt: new Date('2024-01-15T10:00:00Z')
};

const renderJobCard = (job = mockJob) => {
  return render(
    <BrowserRouter>
      <JobCard job={job} />
    </BrowserRouter>
  );
};

describe('JobCard', () => {
  it('renders job information correctly', () => {
    renderJobCard();
    
    expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
    expect(screen.getByText('TechCorp Inc.')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
    expect(screen.getByText('Full-time')).toBeInTheDocument();
  });

  it('displays salary range when provided', () => {
    renderJobCard();
    
    expect(screen.getByText('$80,000 - $120,000')).toBeInTheDocument();
  });

  it('handles missing salary information', () => {
    const jobWithoutSalary = { ...mockJob, salary: undefined };
    renderJobCard(jobWithoutSalary);
    
    expect(screen.queryByText('$')).not.toBeInTheDocument();
  });

  it('shows job description', () => {
    renderJobCard();
    
    expect(screen.getByText('We are looking for a senior React developer to join our team.')).toBeInTheDocument();
  });

  it('displays view details button', () => {
    renderJobCard();
    
    expect(screen.getByText('View Details')).toBeInTheDocument();
  });

  it('handles company as object', () => {
    const jobWithCompanyObject = {
      ...mockJob,
      company: { id: '1', name: 'TechCorp Inc.', logo: '' }
    };
    renderJobCard(jobWithCompanyObject);
    
    expect(screen.getByText('TechCorp Inc.')).toBeInTheDocument();
  });
}); 