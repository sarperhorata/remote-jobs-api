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
    
    const copyrightText = screen.getByText(/©.*Buzz2Remote.*All rights reserved/);
    const parentDiv = copyrightText.parentElement;
    expect(parentDiv).toHaveClass('text-sm', 'text-gray-400');
  });

  test('renders container with proper styling', () => {
    renderFooter();
    
    const container = screen.getByText(/©.*Buzz2Remote.*All rights reserved/).closest('.container');
    expect(container).toHaveClass('container', 'mx-auto');
  });
});