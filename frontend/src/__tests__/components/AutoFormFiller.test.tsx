import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import AutoFormFiller from '../../components/AutoFormFiller';

// Mock dependencies
jest.mock('../../services/api', () => ({
  analyzeForm: jest.fn(),
  fillForm: jest.fn(),
  submitForm: jest.fn(),
}));

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

describe('AutoFormFiller Component', () => {
  const mockProps = {
    jobUrl: 'https://example.com/job/123',
    jobTitle: 'Senior React Developer',
    companyName: 'Tech Corp',
    onComplete: jest.fn(),
    onError: jest.fn(),
    onProgress: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders the component with initial state', () => {
      render(<AutoFormFiller {...mockProps} />);
      
      expect(screen.getByText('Auto Form Filler')).toBeInTheDocument();
      expect(screen.getByText('Job: Senior React Developer at Tech Corp')).toBeInTheDocument();
      expect(screen.getByText('URL: https://example.com/job/123')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /start form filling/i })).toBeInTheDocument();
    });

    it('shows loading state when component is processing', () => {
      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);
      
      expect(screen.getByText('Analyzing form...')).toBeInTheDocument();
    });

    it('displays form fields when analysis is complete', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({
        fields: [
          { name: 'firstName', type: 'text', required: true },
          { name: 'email', type: 'email', required: true },
          { name: 'experience', type: 'textarea', required: false }
        ]
      });

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Form Fields Detected:')).toBeInTheDocument();
        expect(screen.getByText('firstName (text, required)')).toBeInTheDocument();
        expect(screen.getByText('email (email, required)')).toBeInTheDocument();
        expect(screen.getByText('experience (textarea, optional)')).toBeInTheDocument();
      });
    });
  });

  describe('Form Analysis', () => {
    it('calls analyzeForm API when start button is clicked', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({ fields: [] });

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(analyzeForm).toHaveBeenCalledWith(mockProps.jobUrl);
      });
    });

    it('handles form analysis errors gracefully', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockRejectedValue(new Error('Analysis failed'));

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Error: Analysis failed')).toBeInTheDocument();
        expect(mockProps.onError).toHaveBeenCalledWith('Analysis failed');
      });
    });

    it('shows progress during form analysis', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      expect(screen.getByText('Analyzing form...')).toBeInTheDocument();
      expect(mockProps.onProgress).toHaveBeenCalledWith(25);
    });
  });

  describe('Form Filling', () => {
    it('fills form fields with profile data', async () => {
      const { analyzeForm, fillForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({
        fields: [
          { name: 'firstName', type: 'text', required: true },
          { name: 'email', type: 'email', required: true }
        ]
      });
      fillForm.mockResolvedValue({ success: true });

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(fillForm).toHaveBeenCalledWith(mockProps.jobUrl, {
          firstName: 'John',
          email: 'john.doe@example.com'
        });
      });
    });

    it('handles form filling errors', async () => {
      const { analyzeForm, fillForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({
        fields: [{ name: 'firstName', type: 'text', required: true }]
      });
      fillForm.mockRejectedValue(new Error('Filling failed'));

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Error: Filling failed')).toBeInTheDocument();
        expect(mockProps.onError).toHaveBeenCalledWith('Filling failed');
      });
    });

    it('shows progress during form filling', async () => {
      const { analyzeForm, fillForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({
        fields: [{ name: 'firstName', type: 'text', required: true }]
      });
      fillForm.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Filling form...')).toBeInTheDocument();
        expect(mockProps.onProgress).toHaveBeenCalledWith(75);
      });
    });
  });

  describe('Form Submission', () => {
    it('submits form after successful filling', async () => {
      const { analyzeForm, fillForm, submitForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({
        fields: [{ name: 'firstName', type: 'text', required: true }]
      });
      fillForm.mockResolvedValue({ success: true });
      submitForm.mockResolvedValue({ success: true, applicationId: 'app123' });

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(submitForm).toHaveBeenCalledWith(mockProps.jobUrl);
        expect(screen.getByText('Form submitted successfully!')).toBeInTheDocument();
        expect(mockProps.onComplete).toHaveBeenCalledWith({
          success: true,
          applicationId: 'app123'
        });
      });
    });

    it('handles submission errors', async () => {
      const { analyzeForm, fillForm, submitForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({
        fields: [{ name: 'firstName', type: 'text', required: true }]
      });
      fillForm.mockResolvedValue({ success: true });
      submitForm.mockRejectedValue(new Error('Submission failed'));

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Error: Submission failed')).toBeInTheDocument();
        expect(mockProps.onError).toHaveBeenCalledWith('Submission failed');
      });
    });
  });

  describe('User Interactions', () => {
    it('allows user to retry after error', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockRejectedValueOnce(new Error('Analysis failed'))
        .mockResolvedValueOnce({ fields: [] });

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Error: Analysis failed')).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(analyzeForm).toHaveBeenCalledTimes(2);
      });
    });

    it('allows user to cancel operation', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      fireEvent.click(cancelButton);

      expect(screen.getByText('Operation cancelled')).toBeInTheDocument();
    });

    it('shows field mapping options', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({
        fields: [
          { name: 'firstName', type: 'text', required: true },
          { name: 'email', type: 'email', required: true }
        ]
      });

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Field Mappings:')).toBeInTheDocument();
        expect(screen.getByText('firstName → John')).toBeInTheDocument();
        expect(screen.getByText('email → john.doe@example.com')).toBeInTheDocument();
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles empty form fields', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({ fields: [] });

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('No form fields detected')).toBeInTheDocument();
      });
    });

    it('handles missing profile data', async () => {
      jest.doMock('../../hooks/useProfile', () => ({
        __esModule: true,
        default: () => ({
          profile: null,
          updateProfile: jest.fn(),
          loading: false,
          error: null
        })
      }));

      render(<AutoFormFiller {...mockProps} />);
      
      expect(screen.getByText('Profile data not available')).toBeInTheDocument();
    });

    it('handles network timeouts', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockImplementation(() => new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 100)
      ));

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Error: Request timeout')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<AutoFormFiller {...mockProps} />);
      
      expect(screen.getByRole('button', { name: /start form filling/i })).toHaveAttribute('aria-label');
      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow');
    });

    it('supports keyboard navigation', async () => {
      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      startButton.focus();
      
      expect(startButton).toHaveFocus();
      
      userEvent.keyboard('{Enter}');
      
      await waitFor(() => {
        expect(screen.getByText('Analyzing form...')).toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    it('debounces rapid button clicks', async () => {
      const { analyzeForm } = require('../../services/api');
      analyzeForm.mockResolvedValue({ fields: [] });

      render(<AutoFormFiller {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start form filling/i });
      
      // Rapid clicks
      fireEvent.click(startButton);
      fireEvent.click(startButton);
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(analyzeForm).toHaveBeenCalledTimes(1);
      });
    });
  });
}); 