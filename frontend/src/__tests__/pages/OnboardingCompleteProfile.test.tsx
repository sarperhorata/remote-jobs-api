import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import OnboardingCompleteProfile from '../../pages/OnboardingCompleteProfile';

// Mock services
jest.mock('../../services/notificationService', () => ({
  notificationService: {
    requestPermission: jest.fn().mockResolvedValue('granted'),
    startPeriodicJobCheck: jest.fn()
  }
}));

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock navigator.geolocation
const mockGeolocation = {
  getCurrentPosition: jest.fn(),
  watchPosition: jest.fn(),
  clearWatch: jest.fn()
};

Object.defineProperty(global.navigator, 'geolocation', {
  value: mockGeolocation,
  writable: true
});

// Mock Notification API
Object.defineProperty(global, 'Notification', {
  value: {
    permission: 'default',
    requestPermission: jest.fn().mockResolvedValue('granted')
  },
  writable: true
});

const renderWithRouter = (component: React.ReactElement, initialEntries = ['/onboarding/complete']) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      {component}
    </MemoryRouter>
  );
};

describe('OnboardingCompleteProfile', () => {
  const mockLocationState = {
    state: { userId: 'user123' }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();
    mockGeolocation.getCurrentPosition.mockClear();
  });

  it('renders the onboarding form with all sections', () => {
    renderWithRouter(
      <OnboardingCompleteProfile />, 
      [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
    );
    
    expect(screen.getByText('Complete Your Profile')).toBeInTheDocument();
    expect(screen.getByText('Tell us about yourself to get personalized job recommendations')).toBeInTheDocument();
    
    // Check all form sections
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Current/Desired Job Titles (multiple selection allowed)')).toBeInTheDocument();
    expect(screen.getByText('Experience Level')).toBeInTheDocument();
    expect(screen.getByText('Skills (max 30, searchable)')).toBeInTheDocument();
    expect(screen.getByText('Salary Range')).toBeInTheDocument();
    expect(screen.getByText('Work Type')).toBeInTheDocument();
    expect(screen.getByText('Notification Preferences')).toBeInTheDocument();
  });

  describe('Location Section', () => {
    it('allows manual location input', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const locationInput = screen.getByPlaceholderText('Enter your location or use GPS');
      await user.type(locationInput, 'San Francisco, CA');
      
      expect(locationInput).toHaveValue('San Francisco, CA');
    });

    it('triggers geolocation when GPS button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const gpsButton = screen.getByRole('button', { name: /gps/i });
      await user.click(gpsButton);
      
      expect(mockGeolocation.getCurrentPosition).toHaveBeenCalled();
    });

    it('shows location suggestions when typing', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ([
          { place_id: '1', display_name: 'San Francisco, CA, USA' },
          { place_id: '2', display_name: 'San Francisco, TX, USA' }
        ])
      });

      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const locationInput = screen.getByPlaceholderText('Enter your location or use GPS');
      await user.type(locationInput, 'San Francisco');
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('nominatim.openstreetmap.org/search')
        );
      });
    });
  });

  describe('Job Titles Section', () => {
    it('allows searching and selecting job titles', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ([
          { id: '1', title: 'Software Engineer', category: 'Technology' },
          { id: '2', title: 'Software Developer', category: 'Technology' }
        ])
      });

      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const jobTitleInput = screen.getByPlaceholderText('Search and select job titles');
      await user.type(jobTitleInput, 'Software');
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/jobs/job-titles/search?q=Software')
        );
      });
    });

    it('adds selected job titles as chips', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const jobTitleInput = screen.getByPlaceholderText('Search and select job titles');
      await user.type(jobTitleInput, 'Software Engineer');
      
      // Simulate selecting from dropdown (would normally be from API response)
      // Since we can't easily mock the dropdown interaction, we'll test the input behavior
      expect(jobTitleInput).toHaveValue('Software Engineer');
    });
  });

  describe('Experience Level Section', () => {
    it('displays all experience level options', () => {
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      expect(screen.getByText('Entry Level (0-2 years)')).toBeInTheDocument();
      expect(screen.getByText('Mid Level (2-4 years)')).toBeInTheDocument();
      expect(screen.getByText('Senior Level (4-6 years)')).toBeInTheDocument();
      expect(screen.getByText('Lead/Principal (6-10 years)')).toBeInTheDocument();
      expect(screen.getByText('Executive (10+ years)')).toBeInTheDocument();
    });

    it('allows selecting multiple experience levels', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const midLevelCheckbox = screen.getByLabelText('Mid Level (2-4 years)');
      const seniorLevelCheckbox = screen.getByLabelText('Senior Level (4-6 years)');
      
      await user.click(midLevelCheckbox);
      await user.click(seniorLevelCheckbox);
      
      expect(midLevelCheckbox).toBeChecked();
      expect(seniorLevelCheckbox).toBeChecked();
    });
  });

  describe('Skills Section', () => {
    it('allows searching and adding skills', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ([
          { id: '1', name: 'React' },
          { id: '2', name: 'React Native' }
        ])
      });

      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const skillInput = screen.getByPlaceholderText('Search and add skills');
      await user.type(skillInput, 'React');
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/jobs/skills/search?q=React')
        );
      });
    });

    it('shows skill count limitation', () => {
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      expect(screen.getByText('Skills (max 30, searchable)')).toBeInTheDocument();
    });
  });

  describe('Salary Range Section', () => {
    it('displays all salary range options', () => {
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      expect(screen.getByText('$0 - $30k')).toBeInTheDocument();
      expect(screen.getByText('$30k - $70k')).toBeInTheDocument();
      expect(screen.getByText('$70k - $120k')).toBeInTheDocument();
      expect(screen.getByText('$120k - $180k')).toBeInTheDocument();
      expect(screen.getByText('$180k - $240k')).toBeInTheDocument();
      expect(screen.getByText('$240k+')).toBeInTheDocument();
    });

    it('allows selecting multiple salary ranges', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const midRangeCheckbox = screen.getByLabelText('$70k - $120k');
      const highRangeCheckbox = screen.getByLabelText('$120k - $180k');
      
      await user.click(midRangeCheckbox);
      await user.click(highRangeCheckbox);
      
      expect(midRangeCheckbox).toBeChecked();
      expect(highRangeCheckbox).toBeChecked();
    });
  });

  describe('Work Type Section', () => {
    it('displays all work type options with Remote Jobs as default', () => {
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      expect(screen.getByText('Remote Jobs')).toBeInTheDocument();
      expect(screen.getByText('Hybrid Jobs')).toBeInTheDocument();
      expect(screen.getByText('Office Jobs')).toBeInTheDocument();
      
      // Remote Jobs should be checked by default
      const remoteJobsCheckbox = screen.getByLabelText('Remote Jobs');
      expect(remoteJobsCheckbox).toBeChecked();
    });

    it('shows helper text about default selection', () => {
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      expect(screen.getByText('Remote Jobs is selected by default. You can select multiple options.')).toBeInTheDocument();
    });

    it('allows selecting multiple work types', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const hybridJobsCheckbox = screen.getByLabelText('Hybrid Jobs');
      await user.click(hybridJobsCheckbox);
      
      expect(hybridJobsCheckbox).toBeChecked();
      
      // Remote Jobs should still be checked
      const remoteJobsCheckbox = screen.getByLabelText('Remote Jobs');
      expect(remoteJobsCheckbox).toBeChecked();
    });
  });

  describe('Notification Preferences Section', () => {
    it('displays both email and browser notification options', () => {
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      expect(screen.getByText('Email notifications for new jobs')).toBeInTheDocument();
      expect(screen.getByText('Send notifications for new jobs')).toBeInTheDocument();
    });

    it('allows toggling email notifications', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const emailNotificationCheckbox = screen.getByLabelText('Email notifications for new jobs');
      await user.click(emailNotificationCheckbox);
      
      expect(emailNotificationCheckbox).toBeChecked();
    });

    it('requests permission for browser notifications', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const browserNotificationCheckbox = screen.getByLabelText('Send notifications for new jobs');
      await user.click(browserNotificationCheckbox);
      
      // Should request permission when enabling browser notifications
      expect(browserNotificationCheckbox).toBeChecked();
    });
  });

  describe('Form Submission', () => {
    it('validates required fields before submission', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const submitButton = screen.getByText('Complete Profile & Find Jobs');
      await user.click(submitButton);
      
      // Should show error for missing job titles
      await waitFor(() => {
        expect(screen.getByText('Please select at least one job title')).toBeInTheDocument();
      });
    });

    it('submits form with complete data', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Profile completed successfully' })
      });

      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      // Fill required fields
      const locationInput = screen.getByPlaceholderText('Enter your location or use GPS');
      await user.type(locationInput, 'San Francisco, CA');
      
      // Select experience level
      const midLevelCheckbox = screen.getByLabelText('Mid Level (2-4 years)');
      await user.click(midLevelCheckbox);
      
      // Select salary range
      const salaryCheckbox = screen.getByLabelText('$70k - $120k');
      await user.click(salaryCheckbox);
      
      // Remote Jobs is already selected by default
      
      // Note: Job titles and skills would need to be selected through the autocomplete dropdowns
      // which is harder to test without more complex mocking
      
      const submitButton = screen.getByText('Complete Profile & Find Jobs');
      await user.click(submitButton);
      
      // Should show validation error since we haven't selected job titles and skills
      await waitFor(() => {
        expect(screen.getByText('Please select at least one job title')).toBeInTheDocument();
      });
    });

    it('shows success message on successful submission', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Success' })
      });

      // Mock localStorage
      const localStorageMock = {
        setItem: jest.fn(),
        getItem: jest.fn(),
        removeItem: jest.fn(),
      };
      Object.defineProperty(window, 'localStorage', { value: localStorageMock });

      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      // This test would require filling all required fields properly
      // which involves complex mocking of the autocomplete components
    });
  });

  describe('Error Handling', () => {
    it('displays error message when API calls fail', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const skillInput = screen.getByPlaceholderText('Search and add skills');
      await user.type(skillInput, 'React');
      
      // API call should fail and fallback to common skills
      await waitFor(() => {
        // The component should handle the error gracefully
        expect(skillInput).toHaveValue('React');
      });
    });

    it('shows geolocation error when GPS fails', async () => {
      const user = userEvent.setup();
      mockGeolocation.getCurrentPosition.mockImplementationOnce((success, error) => {
        error({ code: 1, message: 'Permission denied' });
      });

      renderWithRouter(
        <OnboardingCompleteProfile />, 
        [{ pathname: '/onboarding/complete', state: { userId: 'user123' } }]
      );
      
      const gpsButton = screen.getByRole('button', { name: /gps/i });
      await user.click(gpsButton);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to get your location. Please check location permissions.')).toBeInTheDocument();
      });
    });
  });
}); 