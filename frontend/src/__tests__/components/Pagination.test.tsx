import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Pagination } from '../../components/Pagination';

describe('Pagination Component', () => {
  const defaultProps = {
    currentPage: 1,
    totalPages: 10,
    onPageChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render pagination with current page and total pages', () => {
    render(<Pagination {...defaultProps} />);
    
    expect(screen.getByText(/Showing page 1 of 10/)).toBeInTheDocument();
  });

  it('should render page numbers correctly', () => {
    render(<Pagination {...defaultProps} />);
    
    // Should show pages 1-5 (max 5 visible pages)
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('should call onPageChange when page number is clicked', () => {
    const onPageChange = jest.fn();
    render(<Pagination {...defaultProps} onPageChange={onPageChange} />);
    
    const pageButton = screen.getByText('2');
    fireEvent.click(pageButton);
    
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('should call onPageChange when previous button is clicked', () => {
    const onPageChange = jest.fn();
    render(<Pagination {...defaultProps} currentPage={2} onPageChange={onPageChange} />);
    
    const previousButtons = screen.getAllByText('Previous');
    const mobilePreviousButton = previousButtons[0]; // Mobile version
    fireEvent.click(mobilePreviousButton);
    
    expect(onPageChange).toHaveBeenCalledWith(1);
  });

  it('should call onPageChange when next button is clicked', () => {
    const onPageChange = jest.fn();
    render(<Pagination {...defaultProps} currentPage={2} onPageChange={onPageChange} />);
    
    const nextButtons = screen.getAllByText('Next');
    const mobileNextButton = nextButtons[0]; // Mobile version
    fireEvent.click(mobileNextButton);
    
    expect(onPageChange).toHaveBeenCalledWith(3);
  });

  it('should disable previous button on first page', () => {
    render(<Pagination {...defaultProps} currentPage={1} />);
    
    const previousButtons = screen.getAllByText('Previous');
    const mobilePreviousButton = previousButtons[0];
    expect(mobilePreviousButton).toBeDisabled();
  });

  it('should disable next button on last page', () => {
    render(<Pagination {...defaultProps} currentPage={10} />);
    
    const nextButtons = screen.getAllByText('Next');
    const mobileNextButton = nextButtons[0];
    expect(mobileNextButton).toBeDisabled();
  });

  it('should show correct page numbers when current page is in the middle', () => {
    render(<Pagination {...defaultProps} currentPage={5} />);
    
    // Should show pages 3-7 (centered around page 5)
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('6')).toBeInTheDocument();
    expect(screen.getByText('7')).toBeInTheDocument();
  });

  it('should handle single page correctly', () => {
    render(<Pagination {...defaultProps} totalPages={1} />);
    
    expect(screen.getByText(/Showing page 1 of 1/)).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('should handle two pages correctly', () => {
    render(<Pagination {...defaultProps} totalPages={2} />);
    
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('should have proper navigation styling', () => {
    render(<Pagination {...defaultProps} />);
    
    const nav = screen.getByLabelText('Pagination');
    expect(nav).toHaveAttribute('aria-label', 'Pagination');
  });

  it('should have proper accessibility attributes', () => {
    render(<Pagination {...defaultProps} />);
    
    const nav = screen.getByLabelText('Pagination');
    expect(nav).toHaveAttribute('aria-label', 'Pagination');
    
    expect(screen.getAllByText('Previous').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Next').length).toBeGreaterThan(0);
  });

  it('should not call onPageChange when clicking disabled previous button', () => {
    const onPageChange = jest.fn();
    render(<Pagination {...defaultProps} currentPage={1} onPageChange={onPageChange} />);
    
    const previousButtons = screen.getAllByText('Previous');
    const mobilePreviousButton = previousButtons[0]; // Mobile version
    fireEvent.click(mobilePreviousButton);
    
    expect(onPageChange).not.toHaveBeenCalled();
  });

  it('should not call onPageChange when clicking disabled next button', () => {
    const onPageChange = jest.fn();
    render(<Pagination {...defaultProps} currentPage={10} onPageChange={onPageChange} />);
    
    const nextButtons = screen.getAllByText('Next');
    const mobileNextButton = nextButtons[0]; // Mobile version
    fireEvent.click(mobileNextButton);
    
    expect(onPageChange).not.toHaveBeenCalled();
  });
}); 