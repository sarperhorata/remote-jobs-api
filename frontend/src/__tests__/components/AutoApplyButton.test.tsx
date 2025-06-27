import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AutoApplyButton from '../../components/AutoApplyButton';

// Mock the API configuration
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn(() => Promise.resolve('http://localhost:5001'))
}));

// Mock fetch
global.fetch = jest.fn();

describe('AutoApplyButton', () => {
  const mockProps = {
    jobUrl: 'https://example.com/job/apply',
    jobId: 'job-123',
    onApplied: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem('token', 'test-token');
  });

  afterEach(() => {
    localStorage.clear();
  });

  test('renders initial Auto Apply button', () => {
    render(<AutoApplyButton {...mockProps} />);
    
    const button = screen.getByRole('button', { name: /auto apply/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Auto Apply');
  });

  test('shows analyzing state when clicked', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        auto_apply_supported: true,
        analysis: { supported: true }
      })
    });

    render(<AutoApplyButton {...mockProps} />);
    
    const button = screen.getByRole('button', { name: /auto apply/i });
    fireEvent.click(button);

    expect(screen.getByText('Analyzing...')).toBeInTheDocument();
  });

  test('handles form analysis failure', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Analysis failed'));

    render(<AutoApplyButton {...mockProps} />);
    
    const button = screen.getByRole('button', { name: /auto apply/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Auto Apply Failed')).toBeInTheDocument();
    });

    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  test('shows unsupported message when auto apply is not supported', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        auto_apply_supported: false,
        analysis: { supported: false }
      })
    });

    render(<AutoApplyButton {...mockProps} />);
    
    const button = screen.getByRole('button', { name: /auto apply/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Auto Apply Failed')).toBeInTheDocument();
      expect(screen.getByText(/Auto Apply is not supported/)).toBeInTheDocument();
    });
  });

  test('shows preview when form analysis succeeds', async () => {
    // Mock form analysis success
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          auto_apply_supported: true,
          analysis: { supported: true }
        })
      })
      // Mock preview generation
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          total_fields: 5,
          fields_with_responses: 4,
          user_profile_completeness: {
            overall_percentage: 80,
            ready_for_auto_apply: true
          },
          field_previews: [
            {
              field_name: 'name',
              field_label: 'Full Name',
              generated_value: 'John Doe'
            }
          ]
        })
      });

    render(<AutoApplyButton {...mockProps} />);
    
    const button = screen.getByRole('button', { name: /auto apply/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Auto Apply Preview')).toBeInTheDocument();
    });

    expect(screen.getByText('Form fields detected:')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument();
  });

  test('performs auto apply when confirmed', async () => {
    // Mock form analysis success
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          auto_apply_supported: true,
          analysis: { supported: true }
        })
      })
      // Mock preview generation
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          total_fields: 5,
          fields_with_responses: 4,
          user_profile_completeness: {
            overall_percentage: 80,
            ready_for_auto_apply: true
          },
          field_previews: []
        })
      })
      // Mock auto apply success
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          application_id: 'app-123',
          message: 'Application submitted successfully'
        })
      });

    render(<AutoApplyButton {...mockProps} />);
    
    // Start auto apply process
    const button = screen.getByRole('button', { name: /auto apply/i });
    fireEvent.click(button);

    // Wait for preview to appear
    await waitFor(() => {
      expect(screen.getByText('Auto Apply Preview')).toBeInTheDocument();
    });

    // Confirm auto apply
    const confirmButton = screen.getByText('Confirm Auto Apply');
    fireEvent.click(confirmButton);

    // Check for applying state
    await waitFor(() => {
      expect(screen.getByText('Applying...')).toBeInTheDocument();
    });

    // Wait for success state
    await waitFor(() => {
      expect(screen.getByText('Auto Applied')).toBeInTheDocument();
    });

    // Check that onApplied callback was called
    expect(mockProps.onApplied).toHaveBeenCalledWith('app-123');
  });

  test('handles auto apply failure', async () => {
    // Mock form analysis and preview success, but auto apply failure
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          auto_apply_supported: true,
          analysis: { supported: true }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          total_fields: 5,
          fields_with_responses: 4,
          user_profile_completeness: { ready_for_auto_apply: true },
          field_previews: []
        })
      })
      .mockRejectedValueOnce(new Error('Auto apply failed'));

    render(<AutoApplyButton {...mockProps} />);
    
    const button = screen.getByRole('button', { name: /auto apply/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Auto Apply Preview')).toBeInTheDocument();
    });

    const confirmButton = screen.getByText('Confirm Auto Apply');
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(screen.getByText('Auto Apply Failed')).toBeInTheDocument();
    });
  });

  test('requires login token', async () => {
    localStorage.removeItem('token');

    render(<AutoApplyButton {...mockProps} />);
    
    const button = screen.getByRole('button', { name: /auto apply/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Auto Apply Failed')).toBeInTheDocument();
      expect(screen.getByText(/Please login to use Auto Apply/)).toBeInTheDocument();
    });
  });

  test('handles different button sizes', () => {
    const { rerender } = render(<AutoApplyButton {...mockProps} size="sm" />);
    
    let button = screen.getByRole('button', { name: /auto apply/i });
    expect(button).toHaveClass('px-3', 'py-1.5', 'text-xs');

    rerender(<AutoApplyButton {...mockProps} size="lg" />);
    
    button = screen.getByRole('button', { name: /auto apply/i });
    expect(button).toHaveClass('px-6', 'py-3', 'text-base');
  });

  test('can cancel preview', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          auto_apply_supported: true,
          analysis: { supported: true }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          total_fields: 5,
          fields_with_responses: 4,
          user_profile_completeness: { ready_for_auto_apply: true },
          field_previews: []
        })
      });

    render(<AutoApplyButton {...mockProps} />);
    
    const button = screen.getByRole('button', { name: /auto apply/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Auto Apply Preview')).toBeInTheDocument();
    });

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    // Should go back to initial state
    expect(screen.getByText('Auto Apply')).toBeInTheDocument();
    expect(screen.queryByText('Auto Apply Preview')).not.toBeInTheDocument();
  });
}); 