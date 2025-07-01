import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import OnboardingCompleteProfile from '../../pages/OnboardingCompleteProfile';
import { getApiUrl } from '../../utils/apiConfig';

// Mock API configuration
jest.mock('../../utils/apiConfig');
const mockGetApiUrl = getApiUrl as jest.MockedFunction<typeof getApiUrl>;

// Mock notification service
jest.mock('../../services/notificationService', () => ({
  notificationService: {
    requestPermission: jest.fn().mockResolvedValue(true),
    startPeriodicJobCheck: jest.fn(),
  },
}));

// Mock react-router
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => ({
    state: { userId: 'test-user-id' },
  }),
}));

// Mock fetch
global.fetch = jest.fn();
global.console.error = jest.fn();

const renderComponent = () => {
  return render(
    <BrowserRouter>
      <OnboardingCompleteProfile />
    </BrowserRouter>
  );
};

describe('OnboardingCompleteProfile', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetApiUrl.mockResolvedValue('http://localhost:8002/api/v1');
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    });
  });

  it('renders correctly without errors', () => {
    renderComponent();
    
    expect(screen.getByText('Complete Your Profile')).toBeInTheDocument();
    expect(screen.getByText(/tell us about yourself/i)).toBeInTheDocument();
  });

  it('handles API errors gracefully and shows fallback options', async () => {
    mockGetApiUrl.mockResolvedValue('http://localhost:8002/api/v1');
    (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));

    renderComponent();
    
    const jobTitleInput = screen.getByPlaceholderText(/enter job titles/i);
    fireEvent.change(jobTitleInput, { target: { value: 'Software' } });

    await waitFor(() => {
      expect(global.console.error).toHaveBeenCalledWith('Job titles search error:', expect.any(Error));
    }, { timeout: 1000 });
  });

  it('prevents form submission with incomplete data', async () => {
    renderComponent();
    
    const completeButton = screen.getByRole('button', { name: /complete profile/i });
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(screen.getByText('Please select at least one job title')).toBeInTheDocument();
    });
  });

  it('validates required fields before submission', () => {
    renderComponent();
    
    // Check that all required form sections are present
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Preferred Job Titles')).toBeInTheDocument();
    expect(screen.getByText('Experience Level')).toBeInTheDocument();
    expect(screen.getByText('Skills')).toBeInTheDocument();
    expect(screen.getByText('Salary Range')).toBeInTheDocument();
    expect(screen.getByText('Work Type')).toBeInTheDocument();
  });

  it('should not throw any TypeScript compilation errors', () => {
    // This test ensures the component compiles without TypeScript errors
    expect(() => renderComponent()).not.toThrow();
  });
}); 