import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import OnboardingCompleteProfile from '../../pages/OnboardingCompleteProfile';
import { getApiUrl } from '../../utils/apiConfig';

// Mocks
jest.mock('../../services/notificationService');
jest.mock('../../utils/apiConfig');

const mockGetApiUrl = getApiUrl as jest.Mock;

const renderComponent = () => {
  return render(
    <MemoryRouter initialEntries={[{ pathname: '/onboarding/complete-profile', state: { userId: '123' } }]}>
      <Routes>
        <Route path="/onboarding/complete-profile" element={<OnboardingCompleteProfile />} />
      </Routes>
    </MemoryRouter>
  );
};

describe('OnboardingCompleteProfile', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    mockGetApiUrl.mockResolvedValue('http://fakeapi.com');
    // Mock fetch for job title and skill searches
    global.fetch = jest.fn((url) =>
      Promise.resolve({
        ok: true,
        json: () => {
          if (url.toString().includes('job-titles')) {
            return Promise.resolve([{ id: '1', title: 'Software Engineer', category: 'Tech' }]);
          }
          if (url.toString().includes('skills')) {
            return Promise.resolve([{ id: 's1', name: 'React' }]);
          }
          return Promise.resolve([]);
        },
      })
    ) as jest.Mock;
  });

  test('renders all sections correctly using robust queries', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /complete your profile/i })).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/enter your location or use gps/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/search and select job titles/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/search and add skills/i)).toBeInTheDocument();
      expect(screen.getByText(/experience level/i)).toBeInTheDocument();
      expect(screen.getByText(/what is your desired salary range/i)).toBeInTheDocument();
    });
  });

  test('shows validation error when submitting with empty required fields', async () => {
    renderComponent();
    
    const completeButton = screen.getByRole('button', { name: /complete profile/i });
    fireEvent.click(completeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/please select at least one job title/i)).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully and shows fallback options', async () => {
    // Mock a failed API response
    mockGetApiUrl.mockRejectedValue(new Error('API Down'));
    
    renderComponent();
    
    // Corrected placeholder text
    const jobTitleInput = screen.getByPlaceholderText(/Search and select job titles/i);
    fireEvent.change(jobTitleInput, { target: { value: 'Software' } });

    // The component should now show fallback options
    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });
  });
}); 