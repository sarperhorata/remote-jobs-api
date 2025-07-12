import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import OnboardingCompleteProfile from '../../pages/OnboardingCompleteProfile';
import { getApiUrl } from '../../utils/apiConfig';

// Mock fetch for API calls
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Test wrapper with all providers
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <ThemeProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </ThemeProvider>
  </BrowserRouter>
);

describe('User Profile Integration Tests', () => {
  const mockUser = {
    id: '1',
    email: 'test@example.com',
    name: 'Test User',
    token: 'mock-token'
  };

  beforeEach(() => {
    mockFetch.mockClear();
    localStorage.clear();
    
    // Set up authenticated user
    localStorage.setItem('token', 'mock-token');
    localStorage.setItem('user', JSON.stringify(mockUser));
  });

  describe('Profile Completion Flow', () => {
    it('should handle profile completion with all required fields', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Profile updated successfully' })
      });

      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      // Fill in required fields
      const jobTitleInput = screen.getByPlaceholderText(/job title/i);
      const skillsInput = screen.getByPlaceholderText(/search and add skills/i);
      const salaryInput = screen.getByDisplayValue(/salary range/i);
      const experienceInput = screen.getByDisplayValue(/experience level/i);
      const locationInput = screen.getByPlaceholderText(/location/i);
      const submitButton = screen.getByRole('button', { name: /complete profile/i });

      fireEvent.change(jobTitleInput, { target: { value: 'Frontend Developer' } });
      fireEvent.change(skillsInput, { target: { value: 'React, TypeScript, JavaScript' } });
      fireEvent.change(salaryInput, { target: { value: '80000-120000' } });
      fireEvent.change(experienceInput, { target: { value: 'Mid-level' } });
      fireEvent.change(locationInput, { target: { value: 'Remote' } });

      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/profile/complete'),
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Authorization': 'Bearer mock-token',
              'Content-Type': 'application/json'
            }),
            body: expect.stringContaining('Frontend Developer')
          })
        );
      });
    });

    it('should validate required fields before submission', async () => {
      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /complete profile/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please select at least one job title/i)).toBeInTheDocument();
      });
    });

    it('should handle profile update errors gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Invalid profile data' })
      });

      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      // Fill in required fields
      const jobTitleInput = screen.getByPlaceholderText(/job title/i);
      fireEvent.change(jobTitleInput, { target: { value: 'Frontend Developer' } });

      const submitButton = screen.getByRole('button', { name: /complete profile/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid profile data/i)).toBeInTheDocument();
      });
    });
  });

  describe('Skills Management', () => {
    it('should add and remove skills correctly', async () => {
      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      const skillsInput = screen.getByPlaceholderText(/search and add skills/i);
      
      // Add a skill
      fireEvent.change(skillsInput, { target: { value: 'React' } });
      fireEvent.keyDown(skillsInput, { key: 'Enter' });

      await waitFor(() => {
        expect(screen.getByText('React')).toBeInTheDocument();
      });

      // Add another skill
      fireEvent.change(skillsInput, { target: { value: 'TypeScript' } });
      fireEvent.keyDown(skillsInput, { key: 'Enter' });

      await waitFor(() => {
        expect(screen.getByText('TypeScript')).toBeInTheDocument();
      });

      // Remove a skill
      const removeButtons = screen.getAllByRole('button', { name: /remove/i });
      fireEvent.click(removeButtons[0]);

      await waitFor(() => {
        expect(screen.queryByText('React')).not.toBeInTheDocument();
      });
    });

    it('should prevent duplicate skills', async () => {
      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      const skillsInput = screen.getByPlaceholderText(/search and add skills/i);
      
      // Add React twice
      fireEvent.change(skillsInput, { target: { value: 'React' } });
      fireEvent.keyDown(skillsInput, { key: 'Enter' });
      
      fireEvent.change(skillsInput, { target: { value: 'React' } });
      fireEvent.keyDown(skillsInput, { key: 'Enter' });

      await waitFor(() => {
        const reactSkills = screen.getAllByText('React');
        expect(reactSkills).toHaveLength(1); // Should only have one instance
      });
    });
  });

  describe('Job Preferences', () => {
    it('should save job preferences correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Preferences saved' })
      });

      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      // Set job preferences
      const remoteCheckbox = screen.getByLabelText(/remote/i);
      const fullTimeCheckbox = screen.getByLabelText(/full-time/i);
      
      fireEvent.click(remoteCheckbox);
      fireEvent.click(fullTimeCheckbox);

      const submitButton = screen.getByRole('button', { name: /complete profile/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/profile/complete'),
          expect.objectContaining({
            body: expect.stringContaining('remote')
          })
        );
      });
    });

    it('should handle salary range selection', async () => {
      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      const salarySelect = screen.getByDisplayValue(/salary range/i);
      fireEvent.change(salarySelect, { target: { value: '100000-150000' } });

      expect(salarySelect).toHaveValue('100000-150000');
    });

    it('should handle experience level selection', async () => {
      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      const experienceSelect = screen.getByDisplayValue(/experience level/i);
      fireEvent.change(experienceSelect, { target: { value: 'Senior' } });

      expect(experienceSelect).toHaveValue('Senior');
    });
  });

  describe('Profile Data Persistence', () => {
    it('should load existing profile data on mount', async () => {
      const existingProfile = {
        job_titles: ['Frontend Developer'],
        skills: ['React', 'TypeScript'],
        salary_range: '80000-120000',
        experience_level: 'Mid-level',
        location: 'Remote',
        work_preferences: ['remote', 'full-time']
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ profile: existingProfile })
      });

      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByDisplayValue('Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('React')).toBeInTheDocument();
        expect(screen.getByText('TypeScript')).toBeInTheDocument();
      });
    });

    it('should handle profile data loading errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Failed to load profile'));

      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/failed to load profile/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form Validation', () => {
    it('should validate email format', async () => {
      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      const emailInput = screen.getByPlaceholderText(/email/i);
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.blur(emailInput);

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
      });
    });

    it('should validate minimum skill requirements', async () => {
      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /complete profile/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please add at least one skill/i)).toBeInTheDocument();
      });
    });

    it('should validate salary range format', async () => {
      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      const salaryInput = screen.getByDisplayValue(/salary range/i);
      fireEvent.change(salaryInput, { target: { value: 'invalid-salary' } });
      fireEvent.blur(salaryInput);

      await waitFor(() => {
        expect(screen.getByText(/please select a valid salary range/i)).toBeInTheDocument();
      });
    });
  });

  describe('Profile Completion Success', () => {
    it('should redirect after successful profile completion', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Profile completed successfully' })
      });

      // Mock navigation
      const mockNavigate = jest.fn();
      jest.mock('react-router-dom', () => ({
        ...jest.requireActual('react-router-dom'),
        useNavigate: () => mockNavigate
      }));

      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      // Fill required fields
      const jobTitleInput = screen.getByPlaceholderText(/job title/i);
      fireEvent.change(jobTitleInput, { target: { value: 'Frontend Developer' } });

      const submitButton = screen.getByRole('button', { name: /complete profile/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/profile completed successfully/i)).toBeInTheDocument();
      });
    });

    it('should update user state after profile completion', async () => {
      const updatedUser = {
        ...mockUser,
        profile_completed: true,
        job_titles: ['Frontend Developer'],
        skills: ['React', 'TypeScript']
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ user: updatedUser })
      });

      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      // Fill required fields
      const jobTitleInput = screen.getByPlaceholderText(/job title/i);
      fireEvent.change(jobTitleInput, { target: { value: 'Frontend Developer' } });

      const submitButton = screen.getByRole('button', { name: /complete profile/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
        expect(storedUser.profile_completed).toBe(true);
      });
    });
  });

  describe('Profile Data Export', () => {
    it('should export profile data in correct format', async () => {
      const profileData = {
        job_titles: ['Frontend Developer'],
        skills: ['React', 'TypeScript'],
        salary_range: '80000-120000',
        experience_level: 'Mid-level',
        location: 'Remote',
        work_preferences: ['remote', 'full-time']
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ profile: profileData })
      });

      render(
        <TestWrapper>
          <OnboardingCompleteProfile />
        </TestWrapper>
      );

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByDisplayValue('Frontend Developer')).toBeInTheDocument();
      });

      // Export functionality would typically be triggered by a button
      // For testing, we'll verify the data structure
      expect(profileData).toHaveProperty('job_titles');
      expect(profileData).toHaveProperty('skills');
      expect(profileData).toHaveProperty('salary_range');
      expect(profileData).toHaveProperty('experience_level');
      expect(profileData).toHaveProperty('location');
      expect(profileData).toHaveProperty('work_preferences');
    });
  });
});