import { render, screen, fireEvent } from '@testing-library/react';
import { Pagination } from '../../components/Pagination';
import '@testing-library/jest-dom';

describe('Pagination', () => {
  const mockOnPageChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders pagination information correctly', () => {
    render(<Pagination currentPage={2} totalPages={10} onPageChange={mockOnPageChange} />);
    
    expect(screen.getByText(/Showing page/)).toBeInTheDocument();
    expect(screen.getByText(/of/)).toBeInTheDocument();
  });

  it('calls onPageChange when page number is clicked', () => {
    render(<Pagination currentPage={2} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const buttons = screen.getAllByRole('button');
    const page3Button = buttons.find(button => 
      button.textContent === '3' && 
      button.classList.contains('relative') &&
      button.classList.contains('inline-flex')
    );
    
    expect(page3Button).toBeTruthy();
    fireEvent.click(page3Button!);
    
    expect(mockOnPageChange).toHaveBeenCalledWith(3);
  });

  it('calls onPageChange when next button is clicked', () => {
    render(<Pagination currentPage={2} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const nextButtons = screen.getAllByText('Next');
    fireEvent.click(nextButtons[0]); // Mobile version
    
    expect(mockOnPageChange).toHaveBeenCalledWith(3);
  });

  it('calls onPageChange when previous button is clicked', () => {
    render(<Pagination currentPage={2} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const prevButtons = screen.getAllByText('Previous');
    fireEvent.click(prevButtons[0]); // Mobile version
    
    expect(mockOnPageChange).toHaveBeenCalledWith(1);
  });

  it('disables previous button on first page', () => {
    render(<Pagination currentPage={1} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const allButtons = screen.getAllByRole('button');
    const prevButtons = allButtons.filter(button => 
      button.textContent === 'Previous' || 
      (button.querySelector('.sr-only') && button.querySelector('.sr-only')?.textContent === 'Previous')
    );
    
    prevButtons.forEach(button => {
      expect(button).toBeDisabled();
    });
  });

  it('disables next button on last page', () => {
    render(<Pagination currentPage={10} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const allButtons = screen.getAllByRole('button');
    const nextButtons = allButtons.filter(button => 
      button.textContent === 'Next' || 
      (button.querySelector('.sr-only') && button.querySelector('.sr-only')?.textContent === 'Next')
    );
    
    nextButtons.forEach(button => {
      expect(button).toBeDisabled();
    });
  });

  it('highlights current page', () => {
    render(<Pagination currentPage={3} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const buttons = screen.getAllByRole('button');
    const currentPageButton = buttons.find(button => 
      button.textContent === '3' && 
      button.classList.contains('bg-blue-600')
    );
    
    expect(currentPageButton).toBeTruthy();
    expect(currentPageButton).toHaveClass('bg-blue-600', 'text-white');
  });

  it('shows correct page numbers around current page', () => {
    render(<Pagination currentPage={5} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const buttons = screen.getAllByRole('button');
    const pageButtons = buttons.filter(button => 
      /^\d+$/.test(button.textContent || '') &&
      button.classList.contains('relative') &&
      button.classList.contains('inline-flex')
    );
    
    const pageNumbers = pageButtons.map(button => button.textContent);
    expect(pageNumbers).toEqual(['3', '4', '5', '6', '7']);
  });

  it('shows correct page numbers when near start', () => {
    render(<Pagination currentPage={2} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const buttons = screen.getAllByRole('button');
    const pageButtons = buttons.filter(button => 
      /^\d+$/.test(button.textContent || '') &&
      button.classList.contains('relative') &&
      button.classList.contains('inline-flex')
    );
    
    const pageNumbers = pageButtons.map(button => button.textContent);
    expect(pageNumbers).toEqual(['1', '2', '3', '4', '5']);
  });

  it('shows correct page numbers when near end', () => {
    render(<Pagination currentPage={9} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const buttons = screen.getAllByRole('button');
    const pageButtons = buttons.filter(button => 
      /^\d+$/.test(button.textContent || '') &&
      button.classList.contains('relative') &&
      button.classList.contains('inline-flex')
    );
    
    const pageNumbers = pageButtons.map(button => button.textContent);
    expect(pageNumbers).toEqual(['6', '7', '8', '9', '10']);
  });

  it('handles single page correctly', () => {
    render(<Pagination currentPage={1} totalPages={1} onPageChange={mockOnPageChange} />);
    
    const buttons = screen.getAllByRole('button');
    const pageButtons = buttons.filter(button => 
      /^\d+$/.test(button.textContent || '') &&
      button.classList.contains('relative') &&
      button.classList.contains('inline-flex')
    );
    
    expect(pageButtons).toHaveLength(1);
    expect(pageButtons[0].textContent).toBe('1');
    
    const allButtons = screen.getAllByRole('button');
    const prevButtons = allButtons.filter(button => 
      button.textContent === 'Previous' || 
      (button.querySelector('.sr-only') && button.querySelector('.sr-only')?.textContent === 'Previous')
    );
    const nextButtons = allButtons.filter(button => 
      button.textContent === 'Next' || 
      (button.querySelector('.sr-only') && button.querySelector('.sr-only')?.textContent === 'Next')
    );
    
    prevButtons.forEach(button => {
      expect(button).toBeDisabled();
    });
    nextButtons.forEach(button => {
      expect(button).toBeDisabled();
    });
  });

  it('handles few pages correctly', () => {
    render(<Pagination currentPage={2} totalPages={3} onPageChange={mockOnPageChange} />);
    
    const buttons = screen.getAllByRole('button');
    const pageButtons = buttons.filter(button => 
      /^\d+$/.test(button.textContent || '') &&
      button.classList.contains('relative') &&
      button.classList.contains('inline-flex')
    );
    
    const pageNumbers = pageButtons.map(button => button.textContent);
    expect(pageNumbers).toEqual(['1', '2', '3']);
  });

  it('renders without crashing', () => {
    expect(() => render(
      <Pagination currentPage={1} totalPages={5} onPageChange={mockOnPageChange} />
    )).not.toThrow();
  });

  it('has correct aria-label for navigation', () => {
    render(<Pagination currentPage={2} totalPages={10} onPageChange={mockOnPageChange} />);
    
    const nav = screen.getByLabelText('Pagination');
    expect(nav).toBeInTheDocument();
  });

  it('uses screen reader text for navigation buttons', () => {
    render(<Pagination currentPage={2} totalPages={10} onPageChange={mockOnPageChange} />);
    
    // Mobile version has visible text, desktop version has sr-only text
    expect(screen.getAllByText('Previous')).toHaveLength(2); // Mobile + sr-only
    expect(screen.getAllByText('Next')).toHaveLength(2); // Mobile + sr-only
  });
}); 