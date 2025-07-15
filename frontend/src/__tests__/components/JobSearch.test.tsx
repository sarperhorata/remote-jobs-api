import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobSearch from '../../components/JobSearch/JobSearch';
import * as jobService from '../../services/jobService';

// Mock jobService
jest.mock('../../services/jobService');

const mockJobService = jobService as jest.Mocked<typeof jobService>;

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('JobSearch', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockJobService.getJobs.mockResolvedValue({ jobs: [], total: 0 });
  });

  it('renders search form', () => {
    renderWithRouter(<JobSearch />);
    
    expect(screen.getByPlaceholderText(/Job title, company, or keywords/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Location/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Search/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Filters/i })).toBeInTheDocument();
  });
}); 