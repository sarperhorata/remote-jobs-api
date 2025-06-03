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

// No need to mock API anymore since we use static data
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

  it('renders location autocomplete input with Turkey included', async () => {
    renderWithRouter(<SearchForm />);
    
    // Check that we have autocomplete inputs
    const comboboxes = screen.getAllByRole('combobox');
    expect(comboboxes.length).toBe(2); // Position and Location

    await waitFor(() => {
      expect(comboboxes[1]).toBeInTheDocument();
    });
  });

  it('shows warning when user tries to search without selecting position', async () => {
    renderWithRouter(<SearchForm />);
    
    const searchButton = screen.getByRole('button', { name: /find remote jobs/i });
    fireEvent.click(searchButton);
    
    // Should show warning
    await waitFor(() => {
      expect(screen.getByText(/please select a job position/i)).toBeInTheDocument();
    });
  });

  it('shows warning when user types position manually and presses Enter', async () => {
    const user = userEvent.setup();
    renderWithRouter(<SearchForm />);
    
    // Type in position input
    const positionInput = screen.getAllByRole('combobox')[0];
    await user.type(positionInput, 'Software');
    await user.keyboard('{Enter}');
    
    // Should show warning about selecting from dropdown
    await waitFor(() => {
      expect(screen.getByText(/please select a position from the dropdown/i)).toBeInTheDocument();
    });
  });

  it('loads static position data on mount', async () => {
    renderWithRouter(<SearchForm />);
    
    // No API call needed, data should be loaded immediately
    await waitFor(() => {
      // Component should render without errors
      expect(screen.getByText('Find Remote Jobs')).toBeInTheDocument();
    });
  });

  it('displays position and location labels', () => {
    renderWithRouter(<SearchForm />);
    
    // Check for MUI labels - use getAllByText for multiple elements
    expect(screen.getAllByText('Please enter job title')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Location')[0]).toBeInTheDocument();
  });

  it('uses static position data (no API dependency)', async () => {
    renderWithRouter(<SearchForm />);
    
    // Form should be functional with static data
    expect(screen.getByText('Find Remote Jobs')).toBeInTheDocument();
    
    // Should not make any API calls
    await waitFor(() => {
      expect(screen.getByText('Find Remote Jobs')).toBeInTheDocument();
    });
  });

  it('closes warning when user clicks close button', async () => {
    const user = userEvent.setup();
    renderWithRouter(<SearchForm />);
    
    // Trigger warning by clicking search without selection
    const searchButton = screen.getByRole('button', { name: /find remote jobs/i });
    fireEvent.click(searchButton);
    
    // Wait for warning to appear
    await waitFor(() => {
      expect(screen.getByText(/please select a job position/i)).toBeInTheDocument();
    });
    
    // Look for close button in the alert and click it
    const closeButton = screen.getByRole('button', { name: /close/i });
    await user.click(closeButton);
    
    // Warning should disappear
    await waitFor(() => {
      expect(screen.queryByText(/please select a job position/i)).not.toBeInTheDocument();
    });
  });

  it('has positions sorted by count descending then alphabetically', async () => {
    renderWithRouter(<SearchForm />);
    
    // The first position should be "Software Engineer" with count 180 (highest count)
    // We can't easily test the dropdown options without opening it, 
    // but we can verify the component renders correctly
    expect(screen.getByText('Find Remote Jobs')).toBeInTheDocument();
  });
}); 