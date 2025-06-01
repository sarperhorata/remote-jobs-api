import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobCard from '../../components/JobCard';

const mockJob = {
  id: '1',
  title: 'Senior React Developer',
  company: 'TechCorp Inc.',
  location: 'Remote',
  description: 'We are looking for a senior React developer to join our team.',
  requirements: 'React, TypeScript, Node.js',
  salary_min: 80000,
  salary_max: 120000,
  job_type: 'Full-time',
  created_at: '2024-01-15T10:00:00Z',
  apply_url: 'https://example.com/apply',
  is_active: true
};

const renderJobCard = (job = mockJob, props = {}) => {
  return render(
    <BrowserRouter>
      <JobCard job={job} {...props} />
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
    const jobWithoutSalary = { ...mockJob, salary_min: undefined, salary_max: undefined };
    renderJobCard(jobWithoutSalary);
    
    expect(screen.queryByText('$')).not.toBeInTheDocument();
  });

  it('shows only minimum salary when max is not provided', () => {
    const jobWithMinSalary = { ...mockJob, salary_max: undefined };
    renderJobCard(jobWithMinSalary);
    
    expect(screen.getByText('From $80,000')).toBeInTheDocument();
  });

  it('shows only maximum salary when min is not provided', () => {
    const jobWithMaxSalary = { ...mockJob, salary_min: undefined };
    renderJobCard(jobWithMaxSalary);
    
    expect(screen.getByText('Up to $120,000')).toBeInTheDocument();
  });

  it('truncates long job descriptions', () => {
    const longDescription = 'This is a very long job description that should be truncated after a certain number of characters to maintain the card layout and user experience.';
    const jobWithLongDesc = { ...mockJob, description: longDescription };
    renderJobCard(jobWithLongDesc);
    
    const description = screen.getByText(longDescription.substring(0, 150) + '...');
    expect(description).toBeInTheDocument();
  });

  it('shows full short descriptions', () => {
    const shortDescription = 'Short description.';
    const jobWithShortDesc = { ...mockJob, description: shortDescription };
    renderJobCard(jobWithShortDesc);
    
    expect(screen.getByText(shortDescription)).toBeInTheDocument();
  });

  it('navigates to job detail when clicked', () => {
    renderJobCard();
    
    const jobCard = screen.getByRole('article');
    expect(jobCard.closest('a')).toHaveAttribute('href', '/jobs/1');
  });

  it('shows apply button with correct link', () => {
    renderJobCard();
    
    const applyButton = screen.getByText('Apply Now');
    expect(applyButton.closest('a')).toHaveAttribute('href', 'https://example.com/apply');
    expect(applyButton.closest('a')).toHaveAttribute('target', '_blank');
  });

  it('handles missing apply URL', () => {
    const jobWithoutApplyUrl = { ...mockJob, apply_url: undefined };
    renderJobCard(jobWithoutApplyUrl);
    
    const applyButton = screen.queryByText('Apply Now');
    expect(applyButton).not.toBeInTheDocument();
  });

  it('displays creation date formatted correctly', () => {
    renderJobCard();
    
    expect(screen.getByText(/Posted/)).toBeInTheDocument();
  });

  it('shows job type badge', () => {
    renderJobCard();
    
    const jobTypeBadge = screen.getByText('Full-time');
    expect(jobTypeBadge).toHaveClass('bg-blue-100', 'text-blue-800');
  });

  it('handles different job types with correct styling', () => {
    const partTimeJob = { ...mockJob, job_type: 'Part-time' };
    renderJobCard(partTimeJob);
    
    const jobTypeBadge = screen.getByText('Part-time');
    expect(jobTypeBadge).toHaveClass('bg-green-100', 'text-green-800');
  });

  it('shows remote location with special styling', () => {
    renderJobCard();
    
    const locationElement = screen.getByText('Remote');
    expect(locationElement).toHaveClass('text-purple-600');
  });

  it('handles on-site locations normally', () => {
    const onsiteJob = { ...mockJob, location: 'New York, NY' };
    renderJobCard(onsiteJob);
    
    const locationElement = screen.getByText('New York, NY');
    expect(locationElement).not.toHaveClass('text-purple-600');
  });

  it('shows requirements when provided', () => {
    renderJobCard();
    
    expect(screen.getByText('React, TypeScript, Node.js')).toBeInTheDocument();
  });

  it('handles missing requirements', () => {
    const jobWithoutRequirements = { ...mockJob, requirements: undefined };
    renderJobCard(jobWithoutRequirements);
    
    expect(screen.queryByText('Requirements:')).not.toBeInTheDocument();
  });

  it('handles hover effects', () => {
    renderJobCard();
    
    const jobCard = screen.getByRole('article');
    fireEvent.mouseEnter(jobCard);
    
    expect(jobCard).toHaveClass('hover:shadow-lg');
  });

  it('shows inactive job styling', () => {
    const inactiveJob = { ...mockJob, is_active: false };
    renderJobCard(inactiveJob);
    
    const jobCard = screen.getByRole('article');
    expect(jobCard).toHaveClass('opacity-60');
  });

  it('handles missing job data gracefully', () => {
    const incompleteJob = {
      id: '1',
      title: '',
      company: '',
      location: '',
    };
    
    expect(() => renderJobCard(incompleteJob as any)).not.toThrow();
  });

  it('renders with custom className when provided', () => {
    const customClass = 'custom-job-card';
    renderJobCard(mockJob, { className: customClass });
    
    const jobCard = screen.getByRole('article');
    expect(jobCard).toHaveClass(customClass);
  });

  it('handles click events when onJobClick is provided', () => {
    const onJobClick = jest.fn();
    renderJobCard(mockJob, { onJobClick });
    
    const jobCard = screen.getByRole('article');
    fireEvent.click(jobCard);
    
    expect(onJobClick).toHaveBeenCalledWith(mockJob);
  });

  it('prevents navigation when onJobClick returns false', () => {
    const onJobClick = jest.fn().mockReturnValue(false);
    renderJobCard(mockJob, { onJobClick });
    
    const jobCard = screen.getByRole('article');
    fireEvent.click(jobCard);
    
    expect(onJobClick).toHaveBeenCalled();
  });

  it('shows bookmark button when showBookmark is true', () => {
    renderJobCard(mockJob, { showBookmark: true });
    
    const bookmarkButton = screen.getByLabelText('Bookmark job');
    expect(bookmarkButton).toBeInTheDocument();
  });

  it('handles bookmark toggle', () => {
    const onBookmarkToggle = jest.fn();
    renderJobCard(mockJob, { showBookmark: true, onBookmarkToggle });
    
    const bookmarkButton = screen.getByLabelText('Bookmark job');
    fireEvent.click(bookmarkButton);
    
    expect(onBookmarkToggle).toHaveBeenCalledWith(mockJob.id);
  });

  it('shows correct bookmark state', () => {
    renderJobCard(mockJob, { showBookmark: true, isBookmarked: true });
    
    const bookmarkButton = screen.getByLabelText('Remove bookmark');
    expect(bookmarkButton).toBeInTheDocument();
  });

  it('formats large salary numbers correctly', () => {
    const highSalaryJob = { ...mockJob, salary_min: 150000, salary_max: 250000 };
    renderJobCard(highSalaryJob);
    
    expect(screen.getByText('$150,000 - $250,000')).toBeInTheDocument();
  });

  it('handles international locations', () => {
    const internationalJob = { ...mockJob, location: 'London, UK' };
    renderJobCard(internationalJob);
    
    expect(screen.getByText('London, UK')).toBeInTheDocument();
  });

  it('shows company logo when provided', () => {
    const jobWithLogo = { ...mockJob, company_logo: 'https://example.com/logo.png' };
    renderJobCard(jobWithLogo);
    
    const logo = screen.getByAltText('TechCorp Inc. logo');
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', 'https://example.com/logo.png');
  });

  it('shows fallback when company logo fails to load', () => {
    const jobWithLogo = { ...mockJob, company_logo: 'https://example.com/logo.png' };
    renderJobCard(jobWithLogo);
    
    const logo = screen.getByAltText('TechCorp Inc. logo');
    fireEvent.error(logo);
    
    expect(screen.getByText('TC')).toBeInTheDocument(); // Company initials fallback
  });
}); 