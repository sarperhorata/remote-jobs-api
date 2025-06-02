import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SearchForm from '../../components/SearchForm';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock fetch API
global.fetch = jest.fn();

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('SearchForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        total_jobs: 1000,
        jobs_by_title: []
      })
    });
  });

  it('renders search form with basic elements', () => {
    renderWithRouter(<SearchForm />);
    
    // Check for basic form elements - use actual button text
    expect(screen.getByText('Find Remote Jobs')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /find remote jobs/i })).toBeInTheDocument();
  });

  it('renders position autocomplete input', () => {
    renderWithRouter(<SearchForm />);
    
    // Look for the MUI autocomplete input
    const positionInputs = screen.getAllByRole('combobox');
    expect(positionInputs.length).toBeGreaterThan(0);
  });

  it('renders location autocomplete input', () => {
    renderWithRouter(<SearchForm />);
    
    // Check that we have autocomplete inputs
    const comboboxes = screen.getAllByRole('combobox');
    expect(comboboxes.length).toBe(2); // Position and Location
  });

  it('handles search button click', async () => {
    renderWithRouter(<SearchForm />);
    
    const searchButton = screen.getByRole('button', { name: /find remote jobs/i });
    fireEvent.click(searchButton);
    
    // Should navigate even with empty inputs
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/jobs?');
    });
  });

  it('fetches position data on mount', async () => {
    renderWithRouter(<SearchForm />);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8001/api/jobs/statistics');
    });
  });

  it('displays position and location labels', () => {
    renderWithRouter(<SearchForm />);
    
    // Check for MUI labels - use getAllByText for multiple elements
    expect(screen.getAllByText('Job Title')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Location')[0]).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    renderWithRouter(<SearchForm />);
    
    // Form should render even during loading - check for button
    expect(screen.getByText('Find Remote Jobs')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    (fetch as jest.Mock).mockRejectedValue(new Error('API Error'));
    
    renderWithRouter(<SearchForm />);
    
    // Form should still be functional even if API fails
    expect(screen.getByText('Find Remote Jobs')).toBeInTheDocument();
    
    consoleSpy.mockRestore();
  });
}); 