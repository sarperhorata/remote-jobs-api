import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter, useNavigate } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import Home from '../../pages/Home';
import { jobService } from '../../services/jobService';

// Mock services
jest.mock('../../services/jobService', () => ({
  jobService: {
    getJobs: jest.fn(),
    getJobStats: jest.fn(),
    getTopPositions: jest.fn(),
  }
}));

// Mock components to isolate the Home component
jest.mock('../../components/Layout', () => ({ children }: { children: React.ReactNode }) => <div data-testid="mock-layout">{children}</div>);
jest.mock('../../components/AuthModal', () => () => <div data-testid="mock-auth-modal">Auth Modal</div>);
jest.mock('../../components/Onboarding', () => () => <div data-testid="mock-onboarding">Onboarding</div>);
jest.mock('../../components/MultiJobAutocomplete', () => ({ onSelect, placeholder }: { onSelect: (position: any) => void; placeholder?: string }) => (
  <div data-testid="mock-autocomplete">
    <input placeholder={placeholder} />
    <button onClick={() => onSelect({ title: 'Developer', count: 100 })}>Select Developer</button>
  </div>
));

// Mock react-router-dom hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

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

// Mock window.open
Object.defineProperty(window, 'open', {
  writable: true,
  value: jest.fn(),
});

const MockWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>{children}</AuthProvider>
  </BrowserRouter>
);

describe('Home Page', () => {
  const mockNavigate = jest.fn();

  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    (useNavigate as jest.Mock).mockReturnValue(mockNavigate);

    // Provide default successful mock responses for services
    (jobService.getJobs as jest.Mock).mockResolvedValue({
      jobs: [
        { _id: '1', title: 'Senior Frontend Developer', company: 'TechBuzz Ltd.', created_at: new Date().toISOString(), skills: ['React'] },
        { _id: '2', title: 'AI Product Manager', company: 'FutureAI Corp.', created_at: new Date().toISOString(), skills: ['AI', 'Product'] },
      ],
      total: 2,
      page: 1,
      limit: 25, // Corrected to match component's default
    });

    (jobService.getJobStats as jest.Mock).mockResolvedValue({
        totalJobs: 38123,
        totalCompanies: 2456,
        totalCountries: 157,
    });

    (jobService.getTopPositions as jest.Mock).mockResolvedValue([
        { _id: 'Developer', count: 5000 },
        { _id: 'Manager', count: 3000 },
    ]);
  });

  test('renders main heading and hero section correctly', async () => {
    render(<MockWrapper><Home /></MockWrapper>);
    
    // Use findBy* to wait for elements that appear after data loading
    expect(await screen.findByText(/Find Your Perfect/i)).toBeInTheDocument();
    expect(await screen.findByText(/Remote Job 🐝/i)).toBeInTheDocument();
    expect(await screen.findByText(/Discover thousands of remote opportunities/i)).toBeInTheDocument();
  });

  test('renders statistics section with data from API', async () => {
    render(<MockWrapper><Home /></MockWrapper>);
    
    // findBy* is great for waiting for text that appears after an API call
    expect(await screen.findByText('38K+')).toBeInTheDocument();
    expect(await screen.findByText('2K+')).toBeInTheDocument();
    expect(await screen.findByText('150+')).toBeInTheDocument();
  });

  test('renders "Hot Remote Jobs" and displays job cards', async () => {
    render(<MockWrapper><Home /></MockWrapper>);
    
    expect(await screen.findByText('🔥 Hot Remote Jobs')).toBeInTheDocument();
    // Wait for job cards to be rendered
    const jobCards = await screen.findAllByText(/Developer|Manager/i);
    expect(jobCards.length).toBeGreaterThan(0);
  });

  test('job cards are clickable and navigate to job details', async () => {
    render(<MockWrapper><Home /></MockWrapper>);
    
    // Wait for job cards to appear and get the first one
    const jobLinks = await screen.findAllByText('Senior Frontend Developer');
    fireEvent.click(jobLinks[0]);
    
    // Check if navigate was called with the correct path
    await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/jobs/1');
    });
  });

  test('calls jobService.getJobs on component mount with correct pagination', async () => {
    render(<MockWrapper><Home /></MockWrapper>);
    
    // Wait for any text from the jobs list to ensure the API has been called
    await screen.findAllByText('Senior Frontend Developer');
    
    // Check that getJobs was called with the default page and limit
    expect(jobService.getJobs).toHaveBeenCalledWith(1, 25);
  });

  test('renders all feature cards in "Why Choose Buzz2Remote?" section', async () => {
    render(<MockWrapper><Home /></MockWrapper>);

    // Use findBy* for each feature card to ensure they are all rendered
    expect(await screen.findByText(/🎯 Smart Matching/i)).toBeInTheDocument();
    expect(await screen.findByText(/Our AI finds the perfect job matches based on your skills, experience, and preferences/i)).toBeInTheDocument();
    
    expect(await screen.findByText(/🌍 Global Opportunities/i)).toBeInTheDocument();
    expect(await screen.findByText(/Access remote jobs from companies worldwide, in your timezone/i)).toBeInTheDocument();
    
    expect(await screen.findByText(/💰 Salary Transparency/i)).toBeInTheDocument();
    expect(await screen.findByText(/See salary ranges upfront - no surprises, just honest compensation/i)).toBeInTheDocument();
  });
}); 