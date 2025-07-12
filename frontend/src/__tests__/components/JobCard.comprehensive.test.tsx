import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import JobCard from '../../components/JobCard';
import { Job } from '../../types/job';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

const mockJob: Job = {
  _id: '1',
  title: 'Senior Frontend Developer',
  company: 'TechCorp',
  location: 'Remote',
  job_type: 'Full-time',
  salary_range: '$90k - $130k',
  skills: ['React', 'TypeScript', 'Node.js'],
  created_at: '2023-01-01T00:00:00Z',
  description: 'We are looking for a talented frontend developer to join our team. You will be responsible for building modern web applications using React and TypeScript.',
  company_logo: '💻',
  url: 'https://example.com/job/1',
  is_active: true,
  salary: {
    min: 90000,
    max: 130000,
    currency: 'USD'
  },
  postedAt: new Date('2023-01-01T00:00:00Z')
};

const mockJobWithCompanyObject: Job = {
  ...mockJob,
  _id: '2',
  company: {
    id: 'company1',
    name: 'Google',
    logo: 'https://logo.clearbit.com/google.com',
    website: 'https://google.com',
    description: 'Search engine company'
  }
};

const mockJobWithoutSalary: Job = {
  ...mockJob,
  _id: '3',
  salary: undefined,
  salary_range: undefined
};

const mockJobWithoutPostedAt: Job = {
  ...mockJob,
  _id: '4',
  postedAt: undefined
};

describe('JobCard Component', () => {
  describe('Basic Rendering', () => {
    test('renders job title correctly', () => {
      render(<JobCard job={mockJob} />);
      expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
    });

    test('renders company name correctly', () => {
      render(<JobCard job={mockJob} />);
      expect(screen.getByText('TechCorp')).toBeInTheDocument();
    });

    test('renders job type correctly', () => {
      render(<JobCard job={mockJob} />);
      expect(screen.getByText('Full-time')).toBeInTheDocument();
    });

    test('renders location correctly', () => {
      render(<JobCard job={mockJob} />);
      expect(screen.getByText('Remote')).toBeInTheDocument();
    });

    test('renders job description correctly', () => {
      render(<JobCard job={mockJob} />);
      expect(screen.getByText(/We are looking for a talented frontend developer/)).toBeInTheDocument();
    });

    test('renders view details button', () => {
      render(<JobCard job={mockJob} />);
      expect(screen.getByText('View Details')).toBeInTheDocument();
    });
  });

  describe('Company Name Handling', () => {
    test('handles string company name', () => {
      render(<JobCard job={mockJob} />);
      expect(screen.getByText('TechCorp')).toBeInTheDocument();
    });

    test('handles company object with name', () => {
      render(<JobCard job={mockJobWithCompanyObject} />);
      expect(screen.getByText('Google')).toBeInTheDocument();
    });

    test('handles company object without name', () => {
      const jobWithoutCompanyName = {
        ...mockJobWithCompanyObject,
        company: { 
          id: 'company1',
          name: undefined as any,
          logo: 'https://logo.clearbit.com/google.com',
          website: 'https://google.com',
          description: 'Search engine company'
        }
      };
      render(<JobCard job={jobWithoutCompanyName} />);
      expect(screen.getByText('Unknown Company')).toBeInTheDocument();
    });
  });

  describe('Company Logo', () => {
    test('renders company logo with correct alt text', () => {
      render(<JobCard job={mockJob} />);
      const logo = screen.getByAltText('TechCorp logo');
      expect(logo).toBeInTheDocument();
      expect(logo).toHaveAttribute('src', expect.stringContaining('logo.clearbit.com'));
    });

    test('renders fallback logo when image fails to load', () => {
      render(<JobCard job={mockJob} />);
      const logo = screen.getByAltText('TechCorp logo');
      
      // Simulate image load error
      fireEvent.error(logo);
      
      // Should show fallback with first letter
      expect(screen.getByText('T')).toBeInTheDocument();
    });

    test('uses correct domain mapping for major companies', () => {
      const googleJob = {
        ...mockJob,
        company: 'Google'
      };
      render(<JobCard job={googleJob} />);
      const logo = screen.getByAltText('Google logo');
      expect(logo).toHaveAttribute('src', 'https://logo.clearbit.com/google.com');
    });

    test('generates fallback color based on company name first letter', () => {
      render(<JobCard job={mockJob} />);
      const logo = screen.getByAltText('TechCorp logo');
      
      // Simulate image load error
      fireEvent.error(logo);
      
      // Should show fallback with first letter 'T'
      const fallback = screen.getByText('T');
      expect(fallback).toBeInTheDocument();
      expect(fallback.closest('div')).toHaveClass('bg-blue-500');
    });
  });

  describe('Salary Display', () => {
    test('displays salary range when available', () => {
      render(<JobCard job={mockJob} />);
      expect(screen.getByText('$90,000 - $130,000')).toBeInTheDocument();
    });

    test('does not display salary when not available', () => {
      render(<JobCard job={mockJobWithoutSalary} />);
      expect(screen.queryByText(/\$\d+,\d+ - \$\d+,\d+/)).not.toBeInTheDocument();
    });

    test('handles salary with different currencies', () => {
      const jobWithEUR = {
        ...mockJob,
        salary: {
          min: 50000,
          max: 80000,
          currency: 'EUR'
        }
      };
      render(<JobCard job={jobWithEUR} />);
      expect(screen.getByText('$50,000 - $80,000')).toBeInTheDocument();
    });
  });

  describe('Posted Date', () => {
    test('displays formatted posted date when available', () => {
      render(<JobCard job={mockJob} />);
      expect(screen.getByText(/Posted 1\/1\/2023/)).toBeInTheDocument();
    });

    test('displays "Recently" when postedAt is not available', () => {
      render(<JobCard job={mockJobWithoutPostedAt} />);
      expect(screen.getByText('Posted Recently')).toBeInTheDocument();
    });

    test('handles different date formats', () => {
      const jobWithDifferentDate = {
        ...mockJob,
        postedAt: new Date('2023-12-25T10:30:00Z')
      };
      render(<JobCard job={jobWithDifferentDate} />);
      expect(screen.getByText(/Posted 12\/25\/2023/)).toBeInTheDocument();
    });
  });

  describe('Job Type Badge', () => {
    test('displays job type with correct styling', () => {
      render(<JobCard job={mockJob} />);
      const badge = screen.getByText('Full-time');
      expect(badge).toHaveClass('bg-blue-100', 'text-blue-800');
    });

    test('handles different job types', () => {
      const partTimeJob = {
        ...mockJob,
        job_type: 'Part-time'
      };
      render(<JobCard job={partTimeJob} />);
      expect(screen.getByText('Part-time')).toBeInTheDocument();
    });

    test('handles contract job type', () => {
      const contractJob = {
        ...mockJob,
        job_type: 'Contract'
      };
      render(<JobCard job={contractJob} />);
      expect(screen.getByText('Contract')).toBeInTheDocument();
    });
  });

  describe('Location Icon', () => {
    test('displays location with icon', () => {
      render(<JobCard job={mockJob} />);
      const locationElement = screen.getByText('Remote');
      expect(locationElement).toBeInTheDocument();
      
      // Check that it's within the location container
      const locationContainer = locationElement.closest('div');
      expect(locationContainer).toHaveClass('flex', 'items-center', 'text-sm', 'text-gray-500');
    });

    test('handles different location types', () => {
      const onSiteJob = {
        ...mockJob,
        location: 'San Francisco, CA'
      };
      render(<JobCard job={onSiteJob} />);
      expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
    });
  });

  describe('Description Truncation', () => {
    test('renders description with line-clamp class', () => {
      render(<JobCard job={mockJob} />);
      const description = screen.getByText(/We are looking for a talented frontend developer/);
      expect(description).toHaveClass('line-clamp-3');
    });

    test('handles long descriptions', () => {
      const jobWithLongDescription = {
        ...mockJob,
        description: 'This is a very long description that should be truncated. '.repeat(10)
      };
      render(<JobCard job={jobWithLongDescription} />);
      expect(screen.getByText(/This is a very long description/)).toBeInTheDocument();
    });

    test('handles short descriptions', () => {
      const jobWithShortDescription = {
        ...mockJob,
        description: 'Short description'
      };
      render(<JobCard job={jobWithShortDescription} />);
      expect(screen.getByText('Short description')).toBeInTheDocument();
    });
  });

  describe('Card Styling', () => {
    test('has correct base styling classes', () => {
      render(<JobCard job={mockJob} />);
      const card = screen.getByText('Senior Frontend Developer').closest('div');
      expect(card).toHaveClass('bg-white', 'rounded-lg', 'shadow-md', 'p-6');
    });

    test('has hover effects', () => {
      render(<JobCard job={mockJob} />);
      const card = screen.getByText('Senior Frontend Developer').closest('div');
      expect(card).toHaveClass('hover:shadow-lg', 'transition-shadow');
    });
  });

  describe('Button Styling', () => {
    test('view details button has correct styling', () => {
      render(<JobCard job={mockJob} />);
      const button = screen.getByText('View Details');
      expect(button).toHaveClass('bg-blue-600', 'text-white', 'px-4', 'py-2', 'rounded-md');
    });

    test('button has hover effects', () => {
      render(<JobCard job={mockJob} />);
      const button = screen.getByText('View Details');
      expect(button).toHaveClass('hover:bg-blue-700', 'transition-colors');
    });
  });

  describe('Accessibility', () => {
    test('has proper alt text for company logo', () => {
      render(<JobCard job={mockJob} />);
      const logo = screen.getByAltText('TechCorp logo');
      expect(logo).toBeInTheDocument();
    });

    test('logo has lazy loading attribute', () => {
      render(<JobCard job={mockJob} />);
      const logo = screen.getByAltText('TechCorp logo');
      expect(logo).toHaveAttribute('loading', 'lazy');
    });

    test('button is accessible', () => {
      render(<JobCard job={mockJob} />);
      const button = screen.getByRole('button', { name: 'View Details' });
      expect(button).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('handles job with minimal data', () => {
      const minimalJob: Job = {
        _id: 'minimal',
        title: 'Minimal Job',
        company: 'Minimal Corp',
        location: 'Remote',
        job_type: 'Full-time',
        created_at: '2023-01-01T00:00:00Z',
        description: 'Minimal description',
        company_logo: '🏢',
        url: '#',
        is_active: true
      };
      render(<JobCard job={minimalJob} />);
      
      expect(screen.getByText('Minimal Job')).toBeInTheDocument();
      expect(screen.getByText('Minimal Corp')).toBeInTheDocument();
      expect(screen.getByText('Minimal description')).toBeInTheDocument();
    });

    test('handles job with empty description', () => {
      const jobWithEmptyDescription = {
        ...mockJob,
        description: ''
      };
      render(<JobCard job={jobWithEmptyDescription} />);
      
      // Should still render the card without description
      expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('TechCorp')).toBeInTheDocument();
    });

    test('handles job with special characters in company name', () => {
      const jobWithSpecialChars = {
        ...mockJob,
        company: 'Tech & Co., Inc.'
      };
      render(<JobCard job={jobWithSpecialChars} />);
      expect(screen.getByText('Tech & Co., Inc.')).toBeInTheDocument();
    });
  });
});