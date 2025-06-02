import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Onboarding from '../../components/Onboarding';
import '@testing-library/jest-dom';

describe('Onboarding', () => {
  const mockProps = {
    isOpen: true,
    onClose: jest.fn(),
    onComplete: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => null),
        setItem: jest.fn(() => null),
        removeItem: jest.fn(() => null),
        clear: jest.fn(() => null),
      },
      writable: true,
    });
  });

  it('renders correctly when open', () => {
    render(<Onboarding {...mockProps} />);
    
    expect(screen.getByText('Welcome to Buzz2Remote! 🎉')).toBeInTheDocument();
    expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<Onboarding {...mockProps} isOpen={false} />);
    
    expect(screen.queryByText('Welcome to Buzz2Remote! 🎉')).not.toBeInTheDocument();
  });

  it('closes when close button is clicked', async () => {
    render(<Onboarding {...mockProps} />);
    
    const closeButton = screen.getByText('×');
    fireEvent.click(closeButton);
    
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('progresses through steps when Next is clicked', async () => {
    render(<Onboarding {...mockProps} />);
    
    // Step 1
    expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
    
    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);
    
    // Step 2
    expect(screen.getByText('Step 2 of 5')).toBeInTheDocument();
    expect(screen.getByText('Tell us about yourself')).toBeInTheDocument();
  });

  it('goes back when Previous is clicked', async () => {
    render(<Onboarding {...mockProps} />);
    
    // Go to step 2
    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);
    
    // Go back to step 1
    const previousButton = screen.getByText('Previous');
    fireEvent.click(previousButton);
    
    expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
    expect(screen.getByText('Welcome to Buzz2Remote! 🎉')).toBeInTheDocument();
  });

  it('disables Previous button on first step', () => {
    render(<Onboarding {...mockProps} />);
    
    const previousButton = screen.getByRole('button', { name: /previous/i });
    expect(previousButton).toBeDisabled();
  });

  it('allows filling personal information in step 2', async () => {
    render(<Onboarding {...mockProps} />);
    
    // Go to step 2
    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);
    
    // Fill form fields
    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email Address');
    const locationInput = screen.getByLabelText('Location');
    
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
    fireEvent.change(locationInput, { target: { value: 'San Francisco, CA' } });
    
    expect(nameInput).toHaveValue('John Doe');
    expect(emailInput).toHaveValue('john@example.com');
    expect(locationInput).toHaveValue('San Francisco, CA');
  });

  it('allows selecting experience level in step 3', async () => {
    render(<Onboarding {...mockProps} />);
    
    // Go to step 3
    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);
    fireEvent.click(nextButton);
    
    expect(screen.getByText('Your professional background')).toBeInTheDocument();
    
    // Fill job title
    const jobTitleInput = screen.getByLabelText('Current/Desired Job Title');
    fireEvent.change(jobTitleInput, { target: { value: 'Frontend Developer' } });
    expect(jobTitleInput).toHaveValue('Frontend Developer');
    
    // Select experience level
    const seniorOption = screen.getByLabelText('Senior Level (5+ years)');
    fireEvent.click(seniorOption);
    expect(seniorOption).toBeChecked();
  });

  it('allows selecting skills in step 4', async () => {
    render(<Onboarding {...mockProps} />);
    
    // Navigate to step 4
    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);
    fireEvent.click(nextButton);
    fireEvent.click(nextButton);
    
    expect(screen.getByText('Your skills & expertise')).toBeInTheDocument();
    
    // Select some skills
    const reactSkill = screen.getByText('React');
    const pythonSkill = screen.getByText('Python');
    
    fireEvent.click(reactSkill);
    fireEvent.click(pythonSkill);
    
    expect(screen.getByText('Selected: 2 skills')).toBeInTheDocument();
  });

  it('allows setting job preferences in step 5', async () => {
    render(<Onboarding {...mockProps} />);
    
    // Navigate to step 5
    const nextButton = screen.getByRole('button', { name: /next/i });
    for (let i = 0; i < 4; i++) {
      fireEvent.click(nextButton);
    }
    
    expect(screen.getByText('Job preferences')).toBeInTheDocument();
    
    // Select job types
    const fullTimeButton = screen.getByText('Full-time');
    fireEvent.click(fullTimeButton);
    
    // Select salary range
    const salaryOption = screen.getByLabelText('$80k - $120k');
    fireEvent.click(salaryOption);
    expect(salaryOption).toBeChecked();
    
    // Check remote jobs only checkbox
    const remoteOnlyCheckbox = screen.getByLabelText('Remote jobs only');
    expect(remoteOnlyCheckbox).toBeChecked(); // Should be checked by default
  });

  it('completes onboarding and saves data', async () => {
    render(<Onboarding {...mockProps} />);
    
    // Navigate to final step
    const nextButton = screen.getByRole('button', { name: /next/i });
    for (let i = 0; i < 4; i++) {
      fireEvent.click(nextButton);
    }
    
    // Complete onboarding
    const completeButton = screen.getByRole('button', { name: /complete setup/i });
    fireEvent.click(completeButton);
    
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'userProfile',
      expect.any(String)
    );
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'onboardingCompleted',
      'true'
    );
    expect(mockProps.onComplete).toHaveBeenCalled();
  });

  it('shows correct progress bar percentage', async () => {
    render(<Onboarding {...mockProps} />);
    
    // Check initial progress (step 1 of 5 = 20%)
    const progressBar = document.querySelector('.bg-gradient-to-r.from-orange-500.to-yellow-500');
    expect(progressBar).toHaveStyle('width: 20%');
    
    // Go to step 3 (60%)
    fireEvent.click(screen.getByText('Next'));
    fireEvent.click(screen.getByText('Next'));
    
    await waitFor(() => {
      expect(progressBar).toHaveStyle('width: 60%');
    });
  });

  it('updates step indicators correctly', async () => {
    render(<Onboarding {...mockProps} />);
    
    // Initially only first step should be active
    const stepIndicators = document.querySelectorAll('.w-2.h-2.rounded-full');
    expect(stepIndicators[0]).toHaveClass('bg-blue-600');
    expect(stepIndicators[1]).toHaveClass('bg-gray-300');
    
    // After going to step 2, first two should be active
    fireEvent.click(screen.getByText('Next'));
    
    await waitFor(() => {
      expect(stepIndicators[0]).toHaveClass('bg-blue-600');
      expect(stepIndicators[1]).toHaveClass('bg-blue-600');
      expect(stepIndicators[2]).toHaveClass('bg-gray-300');
    });
  });
}); 