import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import JobDetail from '../../components/JobDetail';
import { Job } from '../../types/job';

// Mock DOMPurify
jest.mock('dompurify', () => ({
  sanitize: (html: string) => html,
}));

const mockJob: Job = {
  _id: 'job-1',
  id: 'job-1',
  title: 'Senior React Developer',
  company: {
    name: 'Tech Corp',
    logo: 'https://example.com/logo.png'
  },
  companyName: 'Tech Corp',
  company_logo: 'https://example.com/logo.png',
  location: 'Remote',
  job_type: 'Full-time',
  description: 'We are looking for a senior React developer...',
  skills: ['React', 'TypeScript', 'Node.js'],
  postedAt: '2024-01-15T10:00:00Z',
  salary_min: 80000,
  salary_max: 120000,
  salary_currency: 'USD'
};

const mockSimilarJobs: Job[] = [
  {
    _id: 'job-2',
    id: 'job-2',
    title: 'Frontend Developer',
    company: 'Another Corp',
    companyName: 'Another Corp',
    location: 'Remote',
    job_type: 'Full-time',
    description: 'Frontend developer position...',
    skills: ['React', 'JavaScript', 'CSS'],
    postedAt: '2024-01-14T10:00:00Z'
  }
];

const renderJobDetail = (job: Job = mockJob, similarJobs: Job[] = [], onApply = jest.fn()) => {
  return render(<JobDetail job={job} similarJobs={similarJobs} onApply={onApply} />);
};

describe('JobDetail Component', () => {
  test('renders job title and company name', () => {
    renderJobDetail();
    
    expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
  });

  test('renders company logo when available', () => {
    renderJobDetail();
    
    const logo = screen.getByAltText('Tech Corp');
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', 'https://example.com/logo.png');
    expect(logo).toHaveClass('w-16', 'h-16', 'rounded', 'mr-4');
  });

  test('handles missing company logo gracefully', () => {
    const jobWithoutLogo = { 
      ...mockJob, 
      company: { name: 'Tech Corp' },
      company_logo: undefined,
      companyLogo: undefined
    };
    renderJobDetail(jobWithoutLogo);
    
    expect(screen.queryByAltText('Tech Corp')).not.toBeInTheDocument();
  });

  test('renders job metadata correctly', () => {
    renderJobDetail();
    
    expect(screen.getByText('Remote')).toBeInTheDocument();
    expect(screen.getByText('Full-time')).toBeInTheDocument();
    expect(screen.getByText(/Posted/)).toBeInTheDocument();
  });

  test('renders job description', () => {
    renderJobDetail();
    
    expect(screen.getByText('Job Description')).toBeInTheDocument();
    expect(screen.getByText('We are looking for a senior React developer...')).toBeInTheDocument();
  });

  test('renders required skills', () => {
    renderJobDetail();
    
    expect(screen.getByText('Required Skills')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
    expect(screen.getByText('Node.js')).toBeInTheDocument();
  });

  test('renders apply button', () => {
    renderJobDetail();
    
    const applyButton = screen.getByText('Apply Now');
    expect(applyButton).toBeInTheDocument();
    expect(applyButton).toHaveClass('w-full', 'bg-blue-600', 'text-white');
  });

  test('calls onApply when apply button is clicked', () => {
    const onApply = jest.fn();
    renderJobDetail(mockJob, [], onApply);
    
    const applyButton = screen.getByText('Apply Now');
    fireEvent.click(applyButton);
    
    expect(onApply).toHaveBeenCalledWith('job-1');
  });

  test('renders similar jobs section when available', () => {
    renderJobDetail(mockJob, mockSimilarJobs);
    
    expect(screen.getByText('Similar Jobs')).toBeInTheDocument();
    expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    expect(screen.getByText('Another Corp')).toBeInTheDocument();
  });

  test('does not render similar jobs section when empty', () => {
    renderJobDetail(mockJob, []);
    
    expect(screen.queryByText('Similar Jobs')).not.toBeInTheDocument();
  });

  test('handles string company name', () => {
    const jobWithStringCompany = { ...mockJob, company: 'String Company' };
    renderJobDetail(jobWithStringCompany);
    
    expect(screen.getByText('String Company')).toBeInTheDocument();
  });

  test('handles missing company name gracefully', () => {
    const jobWithoutCompany = { ...mockJob, company: undefined, companyName: undefined };
    renderJobDetail(jobWithoutCompany);
    
    expect(screen.getByText('Unknown Company')).toBeInTheDocument();
  });

  test('handles missing skills gracefully', () => {
    const jobWithoutSkills = { ...mockJob, skills: undefined };
    renderJobDetail(jobWithoutSkills);
    
    expect(screen.getByText('Required Skills')).toBeInTheDocument();
    // Should not crash when skills is undefined
  });

  test('handles missing postedAt date', () => {
    const jobWithoutDate = { ...mockJob, postedAt: undefined };
    renderJobDetail(jobWithoutDate);
    
    expect(screen.getByText(/Posted Recently/)).toBeInTheDocument();
  });

  test('renders similar job skills correctly', () => {
    renderJobDetail(mockJob, mockSimilarJobs);
    
    const reactElements = screen.getAllByText('React');
    expect(reactElements).toHaveLength(2); // One in main job, one in similar job
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('CSS')).toBeInTheDocument();
  });

  test('limits similar job skills to 3', () => {
    const similarJobWithManySkills = {
      ...mockSimilarJobs[0],
      skills: ['React', 'JavaScript', 'CSS', 'HTML', 'TypeScript', 'Node.js']
    };
    renderJobDetail(mockJob, [similarJobWithManySkills]);
    
    // Should only show first 3 skills from similar job
    const reactElements = screen.getAllByText('React');
    expect(reactElements).toHaveLength(2); // One in main job, one in similar job
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('CSS')).toBeInTheDocument();
    expect(screen.queryByText('HTML')).not.toBeInTheDocument();
    // TypeScript appears in main job skills, so it should be present
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
  });

  test('handles job with different ID formats', () => {
    const jobWithIdOnly = { ...mockJob, _id: undefined, id: 'job-123' };
    const onApply = jest.fn();
    renderJobDetail(jobWithIdOnly, [], onApply);
    
    const applyButton = screen.getByText('Apply Now');
    fireEvent.click(applyButton);
    
    expect(onApply).toHaveBeenCalledWith('job-123');
  });

  test('handles job with no ID gracefully', () => {
    const jobWithoutId = { ...mockJob, _id: undefined, id: undefined };
    const onApply = jest.fn();
    renderJobDetail(jobWithoutId, [], onApply);
    
    const applyButton = screen.getByText('Apply Now');
    fireEvent.click(applyButton);
    
    expect(onApply).toHaveBeenCalledWith('');
  });

  test('has correct container styling', () => {
    renderJobDetail();
    
    const container = screen.getByText('Senior React Developer').closest('.bg-white.rounded-lg.shadow-md.p-6');
    expect(container).toBeInTheDocument();
  });

  test('similar jobs are clickable', () => {
    const originalLocation = window.location;
    delete window.location;
    window.location = { href: '' } as any;
    
    renderJobDetail(mockJob, mockSimilarJobs);
    
    const similarJob = screen.getByText('Frontend Developer').closest('.p-4.border.rounded-lg');
    expect(similarJob).toHaveClass('cursor-pointer');
    
    // Restore original location
    window.location = originalLocation;
  });
});