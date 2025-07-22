import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Footer from '../../components/Footer';

const renderFooter = () => {
  return render(
    <BrowserRouter>
      <Footer />
    </BrowserRouter>
  );
};

describe('Footer', () => {
  test('renders footer with current year', () => {
    const currentYear = new Date().getFullYear();
    renderFooter();
    
    expect(screen.getByText(`© ${currentYear} Buzz2Remote. All rights reserved.`)).toBeInTheDocument();
  });

  test('renders footer with correct styling classes', () => {
    renderFooter();
    
    const footer = screen.getByRole('contentinfo');
    expect(footer).toHaveClass('bg-gradient-to-r', 'from-gray-900', 'via-purple-900', 'to-gray-900', 'text-white');
  });

  test('renders footer text with correct styling', () => {
    renderFooter();
    
    const text = screen.getByText('© 2025 Buzz2Remote. All rights reserved.');
    expect(text).toHaveClass('text-sm');
  });

  test('renders container with proper styling', () => {
    renderFooter();
    
    const container = screen.getByText('© 2025 Buzz2Remote. All rights reserved.').parentElement?.parentElement;
    expect(container).toHaveClass('border-t', 'border-gray-700', 'mt-8', 'pt-8', 'flex', 'flex-col', 'md:flex-row', 'justify-between', 'items-center');
  });
});