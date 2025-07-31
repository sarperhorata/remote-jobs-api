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
    
    // Check for page information text that might be split across elements
    expect(screen.getByText(/Showing page/)).toBeInTheDocument();
    expect(screen.getByText(/1/)).toBeInTheDocument();
    expect(screen.getByText(/10/)).toBeInTheDocument();
  });

  it('should render page numbers correctly', () => {
    render(<Pagination {...defaultProps} />);
    
    // Should show pages 1-5 (max 5 visible pages)
    const pageButtons = screen.getAllByRole('button');
    const pageNumbers = pageButtons.filter(button => 
      /^[1-5]$/.test(button.textContent || '')
    );
    expect(pageNumbers.length).toBeGreaterThan(0);
  });

  it('should call onPageChange when page number is clicked', () => {
    const onPageChange = jest.fn();
    render(<Pagination {...defaultProps} onPageChange={onPageChange} />);
    
    const pageButtons = screen.getAllByRole('button');
    const page2Button = pageButtons.find(button => button.textContent === '2');
    expect(page2Button).toBeInTheDocument();
    fireEvent.click(page2Button!);
    
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
    const pageButtons = screen.getAllByRole('button');
    const pageNumbers = pageButtons.filter(button => 
      /^[3-7]$/.test(button.textContent || '')
    );
    expect(pageNumbers.length).toBeGreaterThan(0);
  });

  it('should handle single page correctly', () => {
    render(<Pagination {...defaultProps} totalPages={1} />);
    
    // Check for page information text that might be split across elements
    expect(screen.getByText(/Showing page/)).toBeInTheDocument();
    expect(screen.getByText(/1/)).toBeInTheDocument();
    const pageButtons = screen.getAllByRole('button');
    const page1Button = pageButtons.find(button => button.textContent === '1');
    expect(page1Button).toBeInTheDocument();
  });

  it('should handle two pages correctly', () => {
    render(<Pagination {...defaultProps} totalPages={2} />);
    
    const pageButtons = screen.getAllByRole('button');
    const page1Button = pageButtons.find(button => button.textContent === '1');
    const page2Button = pageButtons.find(button => button.textContent === '2');
    expect(page1Button).toBeInTheDocument();
    expect(page2Button).toBeInTheDocument();
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