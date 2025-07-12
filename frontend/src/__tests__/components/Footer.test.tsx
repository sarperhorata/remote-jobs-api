import React from 'react';
import { render, screen } from '@testing-library/react';
import Footer from '../../components/Footer';

describe('Footer', () => {
  test('renders footer with current year', () => {
    const currentYear = new Date().getFullYear();
    render(<Footer />);
    
    expect(screen.getByText(`© ${currentYear} Buzz2Remote. All rights reserved.`)).toBeInTheDocument();
  });

  test('renders footer with correct styling classes', () => {
    render(<Footer />);
    
    const footer = screen.getByRole('contentinfo');
    expect(footer).toHaveClass('bg-white/5', 'backdrop-blur-sm', 'border-t', 'border-white/10');
  });

  test('renders footer text with correct styling', () => {
    render(<Footer />);
    
    const text = screen.getByText(/Buzz2Remote/);
    expect(text).toHaveClass('text-sm', 'text-gray-400');
  });

  test('renders container with proper styling', () => {
    render(<Footer />);
    
    const container = screen.getByText(/Buzz2Remote/).parentElement;
    expect(container).toHaveClass('container', 'mx-auto');
  });
});