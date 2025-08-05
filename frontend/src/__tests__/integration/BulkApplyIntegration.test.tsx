import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import BulkApplyManager from '../../components/BulkApplyManager';
import BulkJobSelector from '../../components/BulkJobSelector';
import AutoFormFiller from '../../components/AutoFormFiller';
import BulkApplyQueue from '../../components/BulkApplyQueue';

// Mock API services
jest.mock('../../services/api', () => ({
  analyzeForm: jest.fn(),
  fillForm: jest.fn(),
  submitForm: jest.fn(),
  submitBulkApplication: jest.fn(),
  getApplicationStatus: jest.fn(),
}));

// Mock hooks
jest.mock('../../hooks/useProfile', () => ({
  __esModule: true,
  default: () => ({
    profile: {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@example.com',
      phone: '+1234567890',
      experience: '5 years',
      skills: ['React', 'TypeScript', 'Node.js'],
      education: 'Bachelor in Computer Science',
      location: 'New York, NY',
      linkedin: 'https://linkedin.com/in/johndoe',
      github: 'https://github.com/johndoe',
      portfolio: 'https://johndoe.dev'
    },
    updateProfile: jest.fn(),
    loading: false,
    error: null
  })
}));

describe('Bulk Apply Integration Tests', () => {
  const mockJobs = [
    {
      id: '1',
      title: 'Senior React Developer',
      company: 'Tech Corp',
      url: 'https://example.com/job/1',
      location: 'New York, NY',
      salary: '$100k - $150k'
    },
    {
      id: '2',
      title: 'Frontend Engineer',
      company: 'Startup Inc',
      url: 'https://example.com/job/2',
      location: 'San Francisco, CA',
      salary: '$90k - $130k'
    },
    {
      id: '3',
      title: 'UI/UX Developer',
      company: 'Design Studio',
      url: 'https://example.com/job/3',
      location: 'Remote',
      salary: '$80k - $120k'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('End-to-End Bulk Apply Flow', () => {
    it('completes full bulk apply workflow successfully', async () => {
      const { analyzeForm, fillForm, submitForm, submitBulkApplication } = require('../../services/api');
      
      // Mock API responses
      analyzeForm.mockResolvedValue({
        fields: [
          { name: 'firstName', type: 'text', required: true },
          { name: 'email', type: 'email', required: true },
          { name: 'experience', type: 'textarea', required: false }
        ],
        form_type: 'application',
        confidence: 0.85,
        estimated_time: 30
      });

      fillForm.mockResolvedValue({
        success: true,
        filled_fields: {
          firstName: 'John',
          email: 'john.doe@example.com',
          experience: '5 years of experience in React development'
        },
        missing_fields: [],
        confidence: 0.9
      });

      submitForm.mockResolvedValue({
        success: true,
        application_id: 'app_123',
        message: 'Application submitted successfully',
        timestamp: new Date().toISOString()
      });

      submitBulkApplication.mockResolvedValue({
        success: true,
        applicationId: 'bulk_app_456'
      });

      // Render the main manager component
      render(<BulkApplyManager />);

      // Step 1: Job Selection
      expect(screen.getByText('Step 1: Select Jobs')).toBeInTheDocument();
      
      // Select jobs
      const jobCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(jobCheckboxes[0]); // Select first job
      fireEvent.click(jobCheckboxes[1]); // Select second job

      // Verify job selection
      expect(screen.getByText('2 jobs selected')).toBeInTheDocument();

      // Proceed to next step
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      // Step 2: Form Configuration
      await waitFor(() => {
        expect(screen.getByText('Step 2: Configure Form Filling')).toBeInTheDocument();
      });

      // Configure form settings
      const autoFillCheckbox = screen.getByLabelText(/auto fill forms/i);
      fireEvent.click(autoFillCheckbox);

      const generateCoverLetterCheckbox = screen.getByLabelText(/generate cover letter/i);
      fireEvent.click(generateCoverLetterCheckbox);

      // Proceed to next step
      const nextStepButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextStepButton);

      // Step 3: Process Applications
      await waitFor(() => {
        expect(screen.getByText('Step 3: Process Applications')).toBeInTheDocument();
      });

      // Start bulk apply
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      // Verify processing
      await waitFor(() => {
        expect(screen.getByText('Processing...')).toBeInTheDocument();
      });

      // Wait for completion
      await waitFor(() => {
        expect(screen.getByText('All steps completed successfully!')).toBeInTheDocument();
      });

      // Verify final results
      expect(screen.getByText('Applications submitted: 2')).toBeInTheDocument();
      expect(screen.getByText('Success Rate: 100%')).toBeInTheDocument();
    });

    it('handles errors gracefully during bulk apply workflow', async () => {
      const { analyzeForm, fillForm, submitForm } = require('../../services/api');
      
      // Mock API errors
      analyzeForm.mockRejectedValue(new Error('Network error'));
      fillForm.mockRejectedValue(new Error('Form filling failed'));
      submitForm.mockRejectedValue(new Error('Submission failed'));

      render(<BulkApplyManager />);

      // Select jobs and proceed
      const jobCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(jobCheckboxes[0]);

      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      // Configure form and proceed
      await waitFor(() => {
        expect(screen.getByText('Step 2: Configure Form Filling')).toBeInTheDocument();
      });

      const nextStepButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextStepButton);

      // Start processing
      await waitFor(() => {
        expect(screen.getByText('Step 3: Process Applications')).toBeInTheDocument();
      });

      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      // Verify error handling
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });

      // Verify retry functionality
      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();
    });
  });

  describe('Component Integration', () => {
    it('integrates BulkJobSelector with BulkApplyManager', async () => {
      const onJobsSelected = jest.fn();
      const onNext = jest.fn();

      render(<BulkJobSelector jobs={mockJobs} onJobsSelected={onJobsSelected} onNext={onNext} />);

      // Select jobs
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]);
      fireEvent.click(checkboxes[1]);

      // Verify selection callback
      expect(onJobsSelected).toHaveBeenCalledWith([
        mockJobs[0],
        mockJobs[1]
      ]);

      // Proceed to next step
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      expect(onNext).toHaveBeenCalled();
    });

    it('integrates AutoFormFiller with BulkApplyManager', async () => {
      const { analyzeForm, fillForm, submitForm } = require('../../services/api');
      
      analyzeForm.mockResolvedValue({
        fields: [{ name: 'firstName', type: 'text', required: true }]
      });
      fillForm.mockResolvedValue({ success: true, filled_fields: {} });
      submitForm.mockResolvedValue({ success: true, application_id: 'app_123' });

      const onComplete = jest.fn();
      const onError = jest.fn();
      const onProgress = jest.fn();

      render(
        <AutoFormFiller
          jobUrl="https://example.com/job/1"
          jobTitle="Senior Developer"
          companyName="Tech Corp"
          onComplete={onComplete}
          onError={onError}
          onProgress={onProgress}
        />
      );

      // Start form filling
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      // Verify progress updates
      await waitFor(() => {
        expect(onProgress).toHaveBeenCalledWith(25);
      });

      await waitFor(() => {
        expect(onProgress).toHaveBeenCalledWith(75);
      });

      // Verify completion
      await waitFor(() => {
        expect(onComplete).toHaveBeenCalledWith({
          success: true,
          application_id: 'app_123'
        });
      });
    });

    it('integrates BulkApplyQueue with BulkApplyManager', async () => {
      const { submitBulkApplication } = require('../../services/api');
      
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app_123' });

      const onComplete = jest.fn();
      const onError = jest.fn();
      const onProgress = jest.fn();

      render(
        <BulkApplyQueue
          jobs={mockJobs}
          onComplete={onComplete}
          onError={onError}
          onProgress={onProgress}
          rateLimit={1000}
          maxRetries={3}
        />
      );

      // Start queue processing
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      // Verify progress updates
      await waitFor(() => {
        expect(onProgress).toHaveBeenCalledWith(33);
      });

      await waitFor(() => {
        expect(onProgress).toHaveBeenCalledWith(67);
      });

      await waitFor(() => {
        expect(onProgress).toHaveBeenCalledWith(100);
      });

      // Verify completion
      await waitFor(() => {
        expect(onComplete).toHaveBeenCalledWith({
          completed: 3,
          total: 3,
          success: true
        });
      });
    });
  });

  describe('Data Flow Integration', () => {
    it('passes data correctly between components', async () => {
      const { analyzeForm, fillForm, submitForm } = require('../../services/api');
      
      analyzeForm.mockResolvedValue({
        fields: [{ name: 'firstName', type: 'text', required: true }]
      });
      fillForm.mockResolvedValue({ success: true, filled_fields: {} });
      submitForm.mockResolvedValue({ success: true, application_id: 'app_123' });

      render(<BulkApplyManager />);

      // Select jobs
      const jobCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(jobCheckboxes[0]);

      // Verify job data is passed correctly
      expect(screen.getByText('Senior React Developer at Tech Corp')).toBeInTheDocument();

      // Proceed to form configuration
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      // Verify form configuration receives job data
      await waitFor(() => {
        expect(screen.getByText('Job: Senior React Developer at Tech Corp')).toBeInTheDocument();
      });

      // Configure and proceed
      const nextStepButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextStepButton);

      // Verify queue receives correct data
      await waitFor(() => {
        expect(screen.getByText('1 job in queue')).toBeInTheDocument();
      });
    });

    it('maintains state consistency across components', async () => {
      render(<BulkApplyManager />);

      // Select jobs
      const jobCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(jobCheckboxes[0]);
      fireEvent.click(jobCheckboxes[1]);

      // Verify state is maintained
      expect(screen.getByText('2 jobs selected')).toBeInTheDocument();

      // Go back and modify selection
      const backButton = screen.getByRole('button', { name: /back/i });
      fireEvent.click(backButton);

      // Unselect one job
      fireEvent.click(jobCheckboxes[1]);

      // Verify state is updated
      expect(screen.getByText('1 job selected')).toBeInTheDocument();

      // Proceed and verify state consistency
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Step 2: Configure Form Filling')).toBeInTheDocument();
      });
    });
  });

  describe('Error Recovery Integration', () => {
    it('recovers from component errors and continues workflow', async () => {
      const { analyzeForm, fillForm, submitForm } = require('../../services/api');
      
      // First attempt fails, second succeeds
      analyzeForm
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          fields: [{ name: 'firstName', type: 'text', required: true }]
        });

      fillForm.mockResolvedValue({ success: true, filled_fields: {} });
      submitForm.mockResolvedValue({ success: true, application_id: 'app_123' });

      render(<BulkApplyManager />);

      // Select jobs and proceed
      const jobCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(jobCheckboxes[0]);

      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Step 2: Configure Form Filling')).toBeInTheDocument();
      });

      const nextStepButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextStepButton);

      // Start processing
      await waitFor(() => {
        expect(screen.getByText('Step 3: Process Applications')).toBeInTheDocument();
      });

      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      // Verify error occurs
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });

      // Retry
      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

      // Verify recovery
      await waitFor(() => {
        expect(screen.getByText('All steps completed successfully!')).toBeInTheDocument();
      });
    });

    it('handles partial failures in bulk operations', async () => {
      const { submitBulkApplication } = require('../../services/api');
      
      // Mock partial failures
      submitBulkApplication
        .mockResolvedValueOnce({ success: true, applicationId: 'app_1' })
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ success: true, applicationId: 'app_3' });

      render(<BulkApplyManager />);

      // Select all jobs
      const jobCheckboxes = screen.getAllByRole('checkbox');
      jobCheckboxes.forEach(checkbox => fireEvent.click(checkbox));

      // Proceed through steps
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Step 2: Configure Form Filling')).toBeInTheDocument();
      });

      const nextStepButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextStepButton);

      // Start processing
      await waitFor(() => {
        expect(screen.getByText('Step 3: Process Applications')).toBeInTheDocument();
      });

      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      // Verify partial success
      await waitFor(() => {
        expect(screen.getByText('Success Rate: 67%')).toBeInTheDocument();
        expect(screen.getByText('Failed: 1')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Integration', () => {
    it('handles large job lists efficiently', async () => {
      const largeJobList = Array.from({ length: 50 }, (_, i) => ({
        id: `${i}`,
        title: `Job ${i}`,
        company: `Company ${i}`,
        url: `https://example.com/job/${i}`,
        location: 'Remote',
        salary: '$50k - $100k'
      }));

      render(<BulkApplyManager />);

      // Select all jobs
      const jobCheckboxes = screen.getAllByRole('checkbox');
      jobCheckboxes.forEach(checkbox => fireEvent.click(checkbox));

      // Verify performance
      expect(screen.getByText('50 jobs selected')).toBeInTheDocument();

      // Proceed without performance issues
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Step 2: Configure Form Filling')).toBeInTheDocument();
      });
    });

    it('maintains responsiveness during long operations', async () => {
      const { submitBulkApplication } = require('../../services/api');
      
      // Mock slow operations
      submitBulkApplication.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );

      render(<BulkApplyManager />);

      // Select jobs and start processing
      const jobCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(jobCheckboxes[0]);

      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Step 2: Configure Form Filling')).toBeInTheDocument();
      });

      const nextStepButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextStepButton);

      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      // Verify UI remains responsive
      await waitFor(() => {
        expect(screen.getByText('Processing...')).toBeInTheDocument();
      });

      // Cancel operation
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      fireEvent.click(cancelButton);

      expect(screen.getByText('Operation cancelled')).toBeInTheDocument();
    });
  });

  describe('Accessibility Integration', () => {
    it('maintains accessibility throughout the workflow', async () => {
      render(<BulkApplyManager />);

      // Verify initial accessibility
      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow');
      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuemax');

      // Navigate with keyboard
      const nextButton = screen.getByRole('button', { name: /next/i });
      nextButton.focus();
      expect(nextButton).toHaveFocus();

      userEvent.keyboard('{Enter}');
      
      // Verify step change is announced
      await waitFor(() => {
        expect(screen.getByText('Step 2: Configure Form Filling')).toBeInTheDocument();
      });
    });

    it('provides proper feedback for screen readers', async () => {
      render(<BulkApplyManager />);

      // Select jobs
      const jobCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(jobCheckboxes[0]);

      // Verify selection feedback
      expect(screen.getByText('1 job selected')).toBeInTheDocument();

      // Proceed and verify progress feedback
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Progress: 67%')).toBeInTheDocument();
      });
    });
  });
}); 