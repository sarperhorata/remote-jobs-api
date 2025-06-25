import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Home from '../../pages/Home';
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

describe('Home Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockJobService.getJobs.mockResolvedValue([]);
  });

  it('renders main heading', () => {
    renderWithRouter(<Home />);
    expect(screen.getByText(/Find Your Perfect Remote Job/i)).toBeInTheDocument();
  });

  it('renders search form', () => {
    renderWithRouter(<Home />);
    expect(screen.getByPlaceholderText(/Job title/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Location/i)).toBeInTheDocument();
  });

  it('displays hot jobs section', () => {
    renderWithRouter(<Home />);
    expect(screen.getByText(/Hot Remote Jobs/i)).toBeInTheDocument();
  });
}); 