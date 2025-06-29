import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MultiJobAutocomplete from '../../components/MultiJobAutocomplete';

// Mock ReactDOM Portal
jest.mock('react-dom', () => ({
  ...jest.requireActual('react-dom'),
  createPortal: (element: any) => element,
}));

// Mock getApiUrl
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockResolvedValue('http://localhost:8002/api/v1')
}));

interface Position {
  title: string;
  count: number;
  category?: string;
}

describe('MultiJobAutocomplete', () => {
  const mockOnPositionsChange = jest.fn();
  const mockOnSearch = jest.fn();

  const mockPositions: Position[] = [
    {
      title: 'Software Engineer',
      count: 150,
      category: 'Technology'
    },
    {
      title: 'Product Manager',
      count: 89,
      category: 'Management'
    }
  ];

  const defaultProps = {
    selectedPositions: [] as Position[],
    onPositionsChange: mockOnPositionsChange,
    onSearch: mockOnSearch,
    placeholder: 'Search and select job titles...'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock fetch for job titles search
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockPositions)
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders input field correctly', () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    expect(screen.getByPlaceholderText('Search and select job titles...')).toBeInTheDocument();
  });

  it('shows loading state during search', async () => {
    // Mock delayed response
    global.fetch = jest.fn().mockImplementation(() =>
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve(mockPositions)
        }), 100)
      )
    );

    render(<MultiJobAutocomplete {...defaultProps} />);
    const input = screen.getByPlaceholderText('Search and select job titles...');
    
    fireEvent.change(input, { target: { value: 'software' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Searching positions...')).toBeInTheDocument();
    });
  });

  it('displays search results correctly', async () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    const input = screen.getByPlaceholderText('Search and select job titles...');
    
    fireEvent.change(input, { target: { value: 'software' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('150 jobs')).toBeInTheDocument();
    });
  });

  it('calls onPositionsChange when position is selected', async () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    const input = screen.getByPlaceholderText('Search and select job titles...');
    
    fireEvent.change(input, { target: { value: 'software' } });
    fireEvent.focus(input);

    await waitFor(() => {
      const positionButton = screen.getByText('Software Engineer');
      fireEvent.click(positionButton);
    });

    expect(mockOnPositionsChange).toHaveBeenCalledWith([mockPositions[0]]);
  });

  it('shows selected positions', () => {
    const propsWithSelected = {
      ...defaultProps,
      selectedPositions: [mockPositions[0]]
    };

    render(<MultiJobAutocomplete {...propsWithSelected} />);
    
    expect(screen.getByText('Selected Positions (1/10):')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    expect(screen.getByText('(150)')).toBeInTheDocument();
  });

  it('removes position when X is clicked', () => {
    const propsWithSelected = {
      ...defaultProps,
      selectedPositions: [mockPositions[0]]
    };

    render(<MultiJobAutocomplete {...propsWithSelected} />);
    
    const removeButton = screen.getByRole('button', { name: /✕/ });
    fireEvent.click(removeButton);

    expect(mockOnPositionsChange).toHaveBeenCalledWith([]);
  });

  it('clears all selections', () => {
    const propsWithSelected = {
      ...defaultProps,
      selectedPositions: mockPositions
    };

    render(<MultiJobAutocomplete {...propsWithSelected} />);
    
    const clearAllButton = screen.getByText('Clear All');
    fireEvent.click(clearAllButton);

    expect(mockOnPositionsChange).toHaveBeenCalledWith([]);
  });

  it('handles keyboard navigation', async () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    const input = screen.getByPlaceholderText('Search and select job titles...');
    
    fireEvent.change(input, { target: { value: 'software' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });

    fireEvent.keyDown(input, { key: 'ArrowDown' });
    fireEvent.keyDown(input, { key: 'Enter' });

    expect(mockOnPositionsChange).toHaveBeenCalledWith([mockPositions[0]]);
  });

  it('handles escape key to close dropdown', async () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    const input = screen.getByPlaceholderText('Search and select job titles...');
    
    fireEvent.change(input, { target: { value: 'software' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });

    fireEvent.keyDown(input, { key: 'Escape' });
    
    await waitFor(() => {
      expect(screen.queryByText('Software Engineer')).not.toBeInTheDocument();
    });
  });

  it('calls onSearch when search button is clicked', () => {
    const propsWithSelected = {
      ...defaultProps,
      selectedPositions: [mockPositions[0]]
    };

    render(<MultiJobAutocomplete {...propsWithSelected} />);
    
    const searchButton = screen.getByRole('button', { name: /Search/ });
    fireEvent.click(searchButton);

    expect(mockOnSearch).toHaveBeenCalledWith([mockPositions[0]]);
  });

  it('disables search button when no positions selected', () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const searchButton = screen.getByRole('button', { name: /Search/ });
    expect(searchButton).toBeDisabled();
  });

  it('handles API errors gracefully', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('API Error'));
    
    render(<MultiJobAutocomplete {...defaultProps} />);
    const input = screen.getByPlaceholderText('Search and select job titles...');
    
    fireEvent.change(input, { target: { value: 'software' } });
    fireEvent.focus(input);

    // Should not show any results and not crash
    await waitFor(() => {
      expect(screen.queryByText('Software Engineer')).not.toBeInTheDocument();
    });
  });

  it('prevents duplicate selections', async () => {
    const propsWithSelected = {
      ...defaultProps,
      selectedPositions: [mockPositions[0]]
    };

    render(<MultiJobAutocomplete {...propsWithSelected} />);
    const input = screen.getByPlaceholderText('Search and select job titles...');
    
    fireEvent.change(input, { target: { value: 'software' } });
    fireEvent.focus(input);

    await waitFor(() => {
      // Should not show already selected position in dropdown
      expect(screen.queryByText('Software Engineer')).not.toBeInTheDocument();
    });
  });

  it('validates required props', () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    // @ts-expect-error Testing missing required props
    render(<MultiJobAutocomplete />);
    
    consoleError.mockRestore();
  });
}); 