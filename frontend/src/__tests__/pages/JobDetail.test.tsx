import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobDetailPage from '../../pages/JobDetail';
import { jobService } from '../../services/AllServices';

// Mock the jobService
jest.mock('../../services/AllServices', () => ({
  jobService: {
    getJobById: jest.fn(),
    getSimilarJobs: jest.fn(),
    applyToJob: jest.fn()
  }
}));

// Mock DOMPurify
jest.mock('dompurify', () => ({
  sanitize: jest.fn((html) => html)
}));

// Mock useParams
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ id: '1' }),
  Link: ({ children, to, ...props }: any) => <a href={to} {...props}>{children}</a>
}));

const mockJob = {
  _id: '1',
  id: '1',
  title: 'Senior React Developer',
  company: {
    name: 'TechCorp',
    logo: 'https://example.com/logo.png',
    description: 'A leading tech company',
    website: 'https://techcorp.com'
  },
  description: 'We are looking for a senior React developer...',
  location: 'Remote',
  job_type: 'Full-time',
  postedAt: '2024-01-01T00:00:00.000Z',
  skills: ['React', 'TypeScript', 'Node.js']
};

const mockSimilarJobs = [
  {
    _id: '2',
    id: '2',
    title: 'Frontend Developer',
    company: {
      name: 'StartupXYZ',
      logo: 'https://example.com/logo2.png'
    },
    description: 'Join our growing team...',
    location: 'Remote',
    job_type: 'Full-time',
    postedAt: '2024-01-02T00:00:00.000Z',
    skills: ['React', 'JavaScript']
  }
];

const renderJobDetail = () => {
  return render(
    <BrowserRouter>
      <JobDetailPage />
    </BrowserRouter>
  );
};

describe('JobDetailPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Loading State', () => {
    test('renders loading state initially', () => {
      (jobService.getJobById as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve(mockJob), 100))
      );
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue(mockSimilarJobs);

      renderJobDetail();
      
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  describe('Job Data Display', () => {
    beforeEach(() => {
      (jobService.getJobById as jest.Mock).mockResolvedValue(mockJob);
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue(mockSimilarJobs);
    });

    test('displays job title and company', async () => {
      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
        expect(screen.getByText('TechCorp')).toBeInTheDocument();
      });
    });

    test('displays job details', async () => {
      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('Remote')).toBeInTheDocument();
        expect(screen.getByText('Full-time')).toBeInTheDocument();
        expect(screen.getByText(/posted/i)).toBeInTheDocument();
      });
    });

    test('displays job description', async () => {
      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('Job Description')).toBeInTheDocument();
        expect(screen.getByText(/we are looking for a senior react developer/i)).toBeInTheDocument();
      });
    });

    test('displays required skills', async () => {
      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('Required Skills')).toBeInTheDocument();
        // Use getAllByText to get all React elements and check the first one (job skills)
        const reactElements = screen.getAllByText('React');
        expect(reactElements[0]).toBeInTheDocument();
        expect(screen.getByText('TypeScript')).toBeInTheDocument();
      });
    });

    test('displays company logo when available', async () => {
      renderJobDetail();

      await waitFor(() => {
        const logo = screen.getByAltText('TechCorp');
        expect(logo).toBeInTheDocument();
        expect(logo).toHaveAttribute('src', 'https://example.com/logo.png');
      });
    });
  });

  describe('Company Information', () => {
    beforeEach(() => {
      (jobService.getJobById as jest.Mock).mockResolvedValue(mockJob);
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue(mockSimilarJobs);
    });

    test('displays company information in sidebar', async () => {
      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('About TechCorp')).toBeInTheDocument();
        expect(screen.getByText('A leading tech company')).toBeInTheDocument();
      });
    });

    test('displays company website link when available', async () => {
      renderJobDetail();

      await waitFor(() => {
        const websiteLink = screen.getByText('Visit Website');
        expect(websiteLink).toBeInTheDocument();
        expect(websiteLink).toHaveAttribute('href', 'https://techcorp.com');
      });
    });
  });

  describe('Similar Jobs', () => {
    beforeEach(() => {
      (jobService.getJobById as jest.Mock).mockResolvedValue(mockJob);
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue(mockSimilarJobs);
    });

    test('displays similar jobs section', async () => {
      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('Similar Jobs')).toBeInTheDocument();
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('StartupXYZ')).toBeInTheDocument();
      });
    });

    test('displays skills for similar jobs', async () => {
      renderJobDetail();

      await waitFor(() => {
        // Use getAllByText to get all React elements and check the second one (similar job skills)
        const reactElements = screen.getAllByText('React');
        expect(reactElements[1]).toBeInTheDocument();
        expect(screen.getByText('JavaScript')).toBeInTheDocument();
      });
    });

    test('similar jobs are clickable', async () => {
      renderJobDetail();

      await waitFor(() => {
        const similarJobElement = screen.getByText('Frontend Developer');
        expect(similarJobElement).toBeInTheDocument();
        expect(similarJobElement.closest('div')).toHaveClass('cursor-pointer');
      });
    });
  });

  describe('Apply Functionality', () => {
    beforeEach(() => {
      (jobService.getJobById as jest.Mock).mockResolvedValue(mockJob);
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue(mockSimilarJobs);
    });

    test('displays apply button', async () => {
      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /apply now/i })).toBeInTheDocument();
      });
    });

    test('apply button calls onApply function', async () => {
      // Mock console.log to verify the handleApply function is called
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
      
      renderJobDetail();

      await waitFor(() => {
        const applyButton = screen.getByRole('button', { name: /apply now/i });
        fireEvent.click(applyButton);
      });

      // Verify that the handleApply function was called (it logs to console)
      expect(consoleSpy).toHaveBeenCalledWith('Applying for job: 1');
      
      consoleSpy.mockRestore();
    });
  });

  describe('Error Handling', () => {
    test('shows error message when job not found', async () => {
      (jobService.getJobById as jest.Mock).mockResolvedValue(null);
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue([]);

      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('Job not found')).toBeInTheDocument();
        expect(screen.getByText('Back to Jobs')).toBeInTheDocument();
      });
    });

    test('handles API errors gracefully', async () => {
      (jobService.getJobById as jest.Mock).mockRejectedValue(new Error('API Error'));
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue([]);

      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('Job not found')).toBeInTheDocument();
      });
    });
  });

  describe('Navigation', () => {
    beforeEach(() => {
      (jobService.getJobById as jest.Mock).mockResolvedValue(null);
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue([]);
    });

    test('back to jobs link navigates correctly', async () => {
      renderJobDetail();

      await waitFor(() => {
        const backLink = screen.getByText('Back to Jobs');
        expect(backLink).toHaveAttribute('href', '/jobs');
      });
    });
  });

  describe('Edge Cases', () => {
    test('handles job without company logo', async () => {
      const jobWithoutLogo = { ...mockJob, company: { ...mockJob.company, logo: undefined } };
      (jobService.getJobById as jest.Mock).mockResolvedValue(jobWithoutLogo);
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue(mockSimilarJobs);

      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
        expect(screen.queryByAltText('TechCorp')).not.toBeInTheDocument();
      });
    });

    test('handles job without skills', async () => {
      const jobWithoutSkills = { ...mockJob, skills: undefined };
      const similarJobsWithoutReact = [
        {
          _id: '2',
          id: '2',
          title: 'Backend Developer',
          company: {
            name: 'StartupXYZ',
            logo: 'https://example.com/logo2.png'
          },
          description: 'Join our growing team...',
          location: 'Remote',
          job_type: 'Full-time',
          postedAt: '2024-01-02T00:00:00.000Z',
          skills: ['Python', 'Django']
        }
      ];
      (jobService.getJobById as jest.Mock).mockResolvedValue(jobWithoutSkills);
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue(similarJobsWithoutReact);

      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('Required Skills')).toBeInTheDocument();
        expect(screen.queryByText('React')).not.toBeInTheDocument();
      });
    });

    test('handles job with string company', async () => {
      const jobWithStringCompany = { ...mockJob, company: 'TechCorp' };
      (jobService.getJobById as jest.Mock).mockResolvedValue(jobWithStringCompany);
      (jobService.getSimilarJobs as jest.Mock).mockResolvedValue(mockSimilarJobs);

      renderJobDetail();

      await waitFor(() => {
        expect(screen.getByText('TechCorp')).toBeInTheDocument();
        expect(screen.getByText('About TechCorp')).toBeInTheDocument();
      });
    });
  });
});