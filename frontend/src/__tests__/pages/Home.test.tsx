import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import '@testing-library/jest-dom';
import Home from '../../pages/Home';
import * as jobService from '../../services/jobService';

jest.mock('../../services/jobService');
jest.mock('../../components/AuthModal', () => () => <div data-testid="auth-modal" />);
jest.mock('../../components/Onboarding', () => () => <div data-testid="onboarding-modal" />);
jest.mock('../../components/MultiJobAutocomplete', () => () => <div data-testid="multi-job-autocomplete" />);

const mockJobService = jobService as jest.Mocked<typeof jobService>;

const mockJobs = [
  { _id: '1', title: 'Frontend Developer', company: { name: 'Tech Corp' }, created_at: new Date().toISOString() },
  { _id: '2', title: 'Backend Engineer', company: { name: 'Startup Inc' }, created_at: new Date().toISOString() }
];

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false, staleTime: Infinity } },
});

const renderHome = () => render(
  <QueryClientProvider client={queryClient}>
    <MemoryRouter><Home /></MemoryRouter>
  </QueryClientProvider>
);

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockJobService.getJobs.mockResolvedValue({
      jobs: mockJobs, total: 2, page: 1, pages: 1
    });
  });

  it('renders main content and loads featured jobs', async () => {
    renderHome();
    expect(screen.getByText('Find Your Next')).toBeInTheDocument();
    expect(screen.getByText('Remote Buzz')).toBeInTheDocument();
    expect(screen.getByTestId('multi-job-autocomplete')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(mockJobService.getJobs).toHaveBeenCalledTimes(1);
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
    });
  });
}); 