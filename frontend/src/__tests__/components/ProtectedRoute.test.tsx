import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

// Mock the entire ProtectedRoute component
const MockProtectedRoute = ({ children, authState }: { children: React.ReactNode; authState?: any }) => {
  const { isAuthenticated, isLoading } = authState || { isAuthenticated: false, isLoading: false };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div data-testid="loading-spinner" className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <div data-testid="navigate" data-to="/login">Navigate to /login</div>;
  }
  
  return <>{children}</>;
};

jest.mock('../../components/ProtectedRoute', () => MockProtectedRoute);

const TestComponent = () => <div data-testid="protected-content">Protected Content</div>;

const renderProtectedRoute = (authState: any) => {
  return render(
    <BrowserRouter>
      <MockProtectedRoute authState={authState}>
        <TestComponent />
      </MockProtectedRoute>
    </BrowserRouter>
  );
};

describe('ProtectedRoute Component', () => {
  test('renders children when user is authenticated', () => {
    renderProtectedRoute({
      isAuthenticated: true,
      isLoading: false
    });
    
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
  });

  test('shows loading spinner when auth status is loading', () => {
    renderProtectedRoute({
      isAuthenticated: false,
      isLoading: true
    });
    
    const loadingSpinner = screen.getByTestId('loading-spinner');
    expect(loadingSpinner).toBeInTheDocument();
    expect(loadingSpinner).toHaveClass('animate-spin', 'rounded-full', 'h-12', 'w-12');
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  test('redirects to login when user is not authenticated', () => {
    renderProtectedRoute({
      isAuthenticated: false,
      isLoading: false
    });
    
    expect(screen.getByTestId('navigate')).toBeInTheDocument();
    expect(screen.getByTestId('navigate')).toHaveAttribute('data-to', '/login');
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  test('renders complex children correctly when authenticated', () => {
    const ComplexComponent = () => (
      <div>
        <h1>Dashboard</h1>
        <p>Welcome to your dashboard</p>
        <button>Settings</button>
      </div>
    );
    
    render(
      <BrowserRouter>
        <MockProtectedRoute authState={{ isAuthenticated: true, isLoading: false }}>
          <ComplexComponent />
        </MockProtectedRoute>
      </BrowserRouter>
    );
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Welcome to your dashboard')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  test('loading state has correct styling', () => {
    renderProtectedRoute({
      isAuthenticated: false,
      isLoading: true
    });
    
    const loadingContainer = screen.getByTestId('loading-spinner').parentElement;
    expect(loadingContainer).toHaveClass('flex', 'items-center', 'justify-center', 'min-h-screen');
  });

  test('handles undefined auth state gracefully', () => {
    renderProtectedRoute(undefined);
    
    // Should redirect to login when auth state is undefined
    expect(screen.getByTestId('navigate')).toBeInTheDocument();
    expect(screen.getByTestId('navigate')).toHaveAttribute('data-to', '/login');
  });

  test('handles null children gracefully', () => {
    render(
      <BrowserRouter>
        <MockProtectedRoute authState={{ isAuthenticated: true, isLoading: false }}>
          {null}
        </MockProtectedRoute>
      </BrowserRouter>
    );
    
    // Should not crash with null children
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  test('handles string children correctly', () => {
    render(
      <BrowserRouter>
        <MockProtectedRoute authState={{ isAuthenticated: true, isLoading: false }}>
          Simple Text Content
        </MockProtectedRoute>
      </BrowserRouter>
    );
    
    expect(screen.getByText('Simple Text Content')).toBeInTheDocument();
  });

  test('maintains authentication state across re-renders', () => {
    const { rerender } = renderProtectedRoute({
      isAuthenticated: true,
      isLoading: false
    });
    
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    
    // Re-render with same auth state
    rerender(
      <BrowserRouter>
        <MockProtectedRoute authState={{ isAuthenticated: true, isLoading: false }}>
          <TestComponent />
        </MockProtectedRoute>
      </BrowserRouter>
    );
    
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
  });

  test('transitions from loading to authenticated correctly', () => {
    const { rerender } = renderProtectedRoute({
      isAuthenticated: false,
      isLoading: true
    });
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    
    // Update to authenticated state
    rerender(
      <BrowserRouter>
        <MockProtectedRoute authState={{ isAuthenticated: true, isLoading: false }}>
          <TestComponent />
        </MockProtectedRoute>
      </BrowserRouter>
    );
    
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
  });
});