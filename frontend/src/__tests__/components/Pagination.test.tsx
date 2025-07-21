import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Pagination from '../../components/Pagination';

// Mock data
const mockProps = {
  currentPage: 1,
  totalPages: 10,
  onPageChange: jest.fn(),
  totalItems: 100,
  itemsPerPage: 10,
};

describe('Pagination Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders pagination controls', () => {
    render(<Pagination {...mockProps} />);
    
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  test('displays current page information', () => {
    render(<Pagination {...mockProps} />);
    
    expect(screen.getByText('Page 1 of 10')).toBeInTheDocument();
  });

  test('displays total items information', () => {
    render(<Pagination {...mockProps} />);
    
    expect(screen.getByText('Showing 1-10 of 100 results')).toBeInTheDocument();
  });

  test('shows previous button when not on first page', () => {
    render(<Pagination {...mockProps} currentPage={2} />);
    
    const prevButton = screen.getByRole('button', { name: /previous/i });
    expect(prevButton).toBeInTheDocument();
  });

  test('does not show previous button on first page', () => {
    render(<Pagination {...mockProps} currentPage={1} />);
    
    const prevButton = screen.queryByRole('button', { name: /previous/i });
    expect(prevButton).not.toBeInTheDocument();
  });

  test('shows next button when not on last page', () => {
    render(<Pagination {...mockProps} currentPage={1} />);
    
    const nextButton = screen.getByRole('button', { name: /next/i });
    expect(nextButton).toBeInTheDocument();
  });

  test('does not show next button on last page', () => {
    render(<Pagination {...mockProps} currentPage={10} />);
    
    const nextButton = screen.queryByRole('button', { name: /next/i });
    expect(nextButton).not.toBeInTheDocument();
  });

  test('calls onPageChange when next button is clicked', () => {
    render(<Pagination {...mockProps} currentPage={1} />);
    
    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);
    
    expect(mockProps.onPageChange).toHaveBeenCalledWith(2);
  });

  test('calls onPageChange when previous button is clicked', () => {
    render(<Pagination {...mockProps} currentPage={2} />);
    
    const prevButton = screen.getByRole('button', { name: /previous/i });
    fireEvent.click(prevButton);
    
    expect(mockProps.onPageChange).toHaveBeenCalledWith(1);
  });

  test('displays page numbers when total pages is small', () => {
    render(<Pagination {...mockProps} totalPages={5} />);
    
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  test('shows ellipsis when total pages is large', () => {
    render(<Pagination {...mockProps} totalPages={20} currentPage={10} />);
    
    expect(screen.getByText('...')).toBeInTheDocument();
  });

  test('calls onPageChange when page number is clicked', () => {
    render(<Pagination {...mockProps} totalPages={5} />);
    
    const page2Button = screen.getByText('2');
    fireEvent.click(page2Button);
    
    expect(mockProps.onPageChange).toHaveBeenCalledWith(2);
  });

  test('highlights current page', () => {
    render(<Pagination {...mockProps} currentPage={3} totalPages={5} />);
    
    const currentPageButton = screen.getByText('3');
    expect(currentPageButton).toHaveClass('bg-blue-600', 'text-white');
  });

  test('handles single page gracefully', () => {
    render(<Pagination {...mockProps} totalPages={1} currentPage={1} />);
    
    // Should render without crashing
    expect(screen.getByText('Page 1 of 1')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /next/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /previous/i })).not.toBeInTheDocument();
  });

  test('displays correct items range for last page', () => {
    render(<Pagination {...mockProps} currentPage={10} totalItems={95} itemsPerPage={10} />);
    
    expect(screen.getByText('Showing 91-95 of 95 results')).toBeInTheDocument();
  });

  test('handles zero total items', () => {
    render(<Pagination {...mockProps} totalItems={0} />);
    
    expect(screen.getByText('Showing 0-0 of 0 results')).toBeInTheDocument();
  });
}); 