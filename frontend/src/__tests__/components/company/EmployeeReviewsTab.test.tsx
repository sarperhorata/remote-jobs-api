import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import EmployeeReviewsTab from '../../../components/company/EmployeeReviewsTab';

// Mock setTimeout to control the delay
jest.useFakeTimers();

describe('EmployeeReviewsTab', () => {
  const mockCompanyId = 'test-company-123';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('renders loading state initially', () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    // Check for loading skeleton
    expect(screen.getByText('Employee Reviews')).toBeInTheDocument();
  });

  it('renders reviews when data is loaded', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    // Fast-forward the timer to skip the 1 second delay
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Sarah Johnson')).toBeInTheDocument();
      expect(screen.getByText('Michael Chen')).toBeInTheDocument();
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('Product Manager')).toBeInTheDocument();
    });
  });

  it('displays review details correctly', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
      expect(screen.getByText('Current')).toBeInTheDocument();
    });
  });

  it('displays star ratings correctly', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      // Check for star rating display
      const starElements = document.querySelectorAll('.text-yellow-400');
      expect(starElements.length).toBeGreaterThan(0);
    });
  });

  it('displays helpful count and verification badge', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Helpful (24)')).toBeInTheDocument();
      expect(screen.getByText('Helpful (18)')).toBeInTheDocument();
    });
  });

  it('handles filter changes', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      const filterButton = screen.getByText('Filters');
      fireEvent.click(filterButton);
      
      const ratingFilter = screen.getByDisplayValue('All Ratings');
      fireEvent.change(ratingFilter, { target: { value: '5' } });
    });
  });

  it('handles sort changes', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      const sortSelect = screen.getByDisplayValue('Most Recent');
      fireEvent.change(sortSelect, { target: { value: 'rating' } });
    });
  });

  it('displays review date correctly', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      // Check for date display (formatted by toLocaleDateString)
      expect(screen.getByText('1/15/2024')).toBeInTheDocument();
      expect(screen.getByText('1/10/2024')).toBeInTheDocument();
    });
  });

  it('displays employment status badges', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      const statusBadges = screen.getAllByText('Current');
      expect(statusBadges.length).toBeGreaterThan(0);
      
      const formerBadges = screen.getAllByText('Former');
      expect(formerBadges.length).toBeGreaterThan(0);
    });
  });

  it('handles helpful button click', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      const helpfulButtons = screen.getAllByText(/Helpful/);
      expect(helpfulButtons.length).toBeGreaterThan(0);
      
      fireEvent.click(helpfulButtons[0]);
    });
  });

  it('displays rating distribution chart', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Rating Distribution')).toBeInTheDocument();
      expect(screen.getAllByText('5').length).toBeGreaterThan(0);
      expect(screen.getAllByText('4').length).toBeGreaterThan(0);
    });
  });

  it('displays average rating', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Average Rating')).toBeInTheDocument();
      // Should show average rating (calculated from mock data)
      expect(screen.getByText('4.2')).toBeInTheDocument();
    });
  });

  it('displays total reviews count', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Total Reviews')).toBeInTheDocument();
      expect(screen.getAllByText('5').length).toBeGreaterThan(0); // 5 reviews in mock data
    });
  });

  it('displays current and former employee counts', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Current Employees')).toBeInTheDocument();
      expect(screen.getByText('Former Employees')).toBeInTheDocument();
      // Should show counts from mock data
      expect(screen.getAllByText('3').length).toBeGreaterThan(0); // 3 current employees
      expect(screen.getAllByText('2').length).toBeGreaterThan(0); // 2 former employees
    });
  });

  it('handles empty reviews state', async () => {
    // Mock empty reviews by temporarily modifying the component
    const originalFetch = global.fetch;
    global.fetch = jest.fn().mockResolvedValue({
      json: () => Promise.resolve({ reviews: [] })
    });

    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getByText('No Reviews Found')).toBeInTheDocument();
    });

    global.fetch = originalFetch;
  });

  it('displays pros and cons sections', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getAllByText('Pros').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Cons').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Advice to Management').length).toBeGreaterThan(0);
    });
  });

  it('displays job titles correctly', async () => {
    render(<EmployeeReviewsTab companyId={mockCompanyId} />);
    
    act(() => {
      jest.advanceTimersByTime(100);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('Product Manager')).toBeInTheDocument();
      expect(screen.getByText('Senior UX Designer')).toBeInTheDocument();
    });
  });
});