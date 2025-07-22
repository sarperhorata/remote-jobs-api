import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import JobAutocomplete from '../../components/JobAutocomplete';

// Mock window.location
const mockLocation = {
  href: '',
  assign: jest.fn(),
  replace: jest.fn(),
  reload: jest.fn(),
};

Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

const mockPopularPositions = [
  { title: 'React Developer', count: 100, category: 'Technology' },
  { title: 'Backend Developer', count: 80, category: 'Technology' },
  { title: 'Product Manager', count: 60, category: 'Management' },
  { title: 'UX Designer', count: 40, category: 'Design' },
];

// Mock fetch
global.fetch = jest.fn((url) => {
  if (url.includes('/jobs/statistics')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ positions: mockPopularPositions }),
    });
  }
  if (url.includes('/jobs/quick-search-count')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ count: 92 }),
    });
  }
  return Promise.reject('Unknown API');
}) as any;

describe('JobAutocomplete', () => {
  beforeEach(() => {
    mockLocation.href = '';
    jest.clearAllMocks();
  });

  it('shows top 4 popular positions on focus', async () => {
    render(<JobAutocomplete value="" onChange={() => {}} />);
    const input = screen.getByRole('textbox');
    fireEvent.focus(input);
    
    await waitFor(() => {
      expect(screen.getByText('React Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Developer')).toBeInTheDocument();
      expect(screen.getByText('Product Manager')).toBeInTheDocument();
      expect(screen.getByText('UX Designer')).toBeInTheDocument();
    });
  });

  it('navigates to correct URL when a popular position is clicked', async () => {
    render(<JobAutocomplete value="" onChange={() => {}} />);
    const input = screen.getByRole('textbox');
    fireEvent.focus(input);
    
    await waitFor(() => screen.getByText('React Developer'));
    fireEvent.click(screen.getByText('React Developer'));
    
    expect(window.location.href).toContain('/job-search-results?q=React%20Developer');
  });

  it('shows count suggestion when user types 3+ chars', async () => {
    render(<JobAutocomplete value="" onChange={() => {}} />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'react' } });
    
    await waitFor(() => {
      expect(screen.getByText(/We have found 92 'react' jobs/i)).toBeInTheDocument();
    });
  });

  it('navigates to correct URL when count suggestion is clicked', async () => {
    render(<JobAutocomplete value="" onChange={() => {}} />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'react' } });
    
    await waitFor(() => screen.getByText(/We have found 92 'react' jobs/i));
    fireEvent.click(screen.getByText(/We have found 92 'react' jobs/i));
    
    expect(window.location.href).toContain('/job-search-results?q=react');
  });
}); 