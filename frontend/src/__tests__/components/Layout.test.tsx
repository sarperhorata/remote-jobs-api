import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../../components/Layout';

// Mock child components
jest.mock('../../components/Header', () => {
  return function MockHeader() {
    return <div data-testid="header">Header</div>;
  };
});

jest.mock('../../components/Footer', () => {
  return function MockFooter() {
    return <div data-testid="footer">Footer</div>;
  };
});

jest.mock('../../components/CookieDisclaimer', () => {
  return function MockCookieDisclaimer() {
    return <div data-testid="cookie-disclaimer">Cookie Disclaimer</div>;
  };
});

const renderLayout = (children: React.ReactNode) => {
  return render(
    <BrowserRouter>
      <Layout>{children}</Layout>
    </BrowserRouter>
  );
};

describe('Layout Component', () => {
  test('renders layout with all child components', () => {
    renderLayout(<div>Test Content</div>);
    
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('footer')).toBeInTheDocument();
    expect(screen.getByTestId('cookie-disclaimer')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  test('renders children content in main section', () => {
    renderLayout(<div>Main Content</div>);
    
    const mainElement = screen.getByText('Main Content').closest('main');
    expect(mainElement).toBeInTheDocument();
    expect(mainElement).toHaveClass('flex-grow', 'pt-16');
  });

  test('has correct container structure', () => {
    renderLayout(<div>Content</div>);
    
    const container = screen.getByText('Content').closest('.flex.flex-col.min-h-screen');
    expect(container).toBeInTheDocument();
    expect(container).toHaveClass('bg-gray-50', 'dark:bg-gray-900');
  });

  test('renders complex children content', () => {
    const complexContent = (
      <div>
        <h1>Title</h1>
        <p>Description</p>
        <button>Click me</button>
      </div>
    );
    
    renderLayout(complexContent);
    
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  test('maintains proper layout structure with multiple children', () => {
    const multipleChildren = (
      <>
        <div>Child 1</div>
        <div>Child 2</div>
        <div>Child 3</div>
      </>
    );
    
    renderLayout(multipleChildren);
    
    expect(screen.getByText('Child 1')).toBeInTheDocument();
    expect(screen.getByText('Child 2')).toBeInTheDocument();
    expect(screen.getByText('Child 3')).toBeInTheDocument();
    
    // All children should be in the main section
    const mainElement = screen.getByText('Child 1').closest('main');
    expect(mainElement).toContainElement(screen.getByText('Child 2'));
    expect(mainElement).toContainElement(screen.getByText('Child 3'));
  });

  test('handles empty children gracefully', () => {
    renderLayout(null);
    
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('footer')).toBeInTheDocument();
    expect(screen.getByTestId('cookie-disclaimer')).toBeInTheDocument();
  });

  test('renders with string children', () => {
    renderLayout('Simple text content');
    
    expect(screen.getByText('Simple text content')).toBeInTheDocument();
  });

  test('maintains accessibility structure', () => {
    renderLayout(<div>Content</div>);
    
    // Check for semantic HTML structure
    const mainElement = screen.getByText('Content').closest('main');
    expect(mainElement).toBeInTheDocument();
    
    // Header and footer should be present
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('footer')).toBeInTheDocument();
  });
});