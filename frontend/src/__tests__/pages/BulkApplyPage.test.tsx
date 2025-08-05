import React from 'react';
import { render, screen } from '@testing-library/react';
import BulkApplyPage from '../../pages/BulkApplyPage';

// Mock the BulkApplyManager component
jest.mock('../../components/BulkApplyManager', () => {
  return function MockBulkApplyManager() {
    return <div data-testid="bulk-apply-manager">Bulk Apply Manager</div>;
  };
});

// Mock useAuth hook
const mockUseAuth = {
  user: {
    id: '1',
    email: 'test@example.com',
    name: 'Test User'
  },
  login: jest.fn(),
  logout: jest.fn(),
  register: jest.fn()
};

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => mockUseAuth
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/', search: '', hash: '', state: null }),
  useParams: () => ({}),
  useSearchParams: () => [new URLSearchParams(), jest.fn()],
}));

// Mock react-helmet-async
jest.mock('react-helmet-async', () => ({
  Helmet: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe('BulkApplyPage', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  describe('Page Structure', () => {
    it('renders the page title and description', () => {
      render(<BulkApplyPage />);
      
      expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
      expect(screen.getByText(/Apply to multiple jobs automatically/)).toBeInTheDocument();
    });

    it('renders the main BulkApplyManager component', () => {
      render(<BulkApplyPage />);
      
      expect(screen.getByTestId('bulk-apply-manager')).toBeInTheDocument();
    });

    it('renders feature cards', () => {
      render(<BulkApplyPage />);
      
      expect(screen.getByText('Smart Selection')).toBeInTheDocument();
      expect(screen.getByText('Auto Fill Forms')).toBeInTheDocument();
      expect(screen.getByText('Smart Queue')).toBeInTheDocument();
    });

    it('renders pro tips section', () => {
      render(<BulkApplyPage />);
      
      expect(screen.getByText('Pro Tips')).toBeInTheDocument();
      expect(screen.getByText(/Update your profile and resume/)).toBeInTheDocument();
    });
  });

  describe('User Information', () => {
    it('displays user welcome message when user is logged in', () => {
      render(<BulkApplyPage />);
      
      expect(screen.getByText(/Welcome back, Test User!/)).toBeInTheDocument();
      expect(screen.getByText(/Your profile data will be used/)).toBeInTheDocument();
    });

    it('does not display user info when user is not logged in', () => {
      mockUseAuth.user = null;
      
      render(<BulkApplyPage />);
      
      expect(screen.queryByText(/Welcome back/)).not.toBeInTheDocument();
    });
  });

  describe('SEO and Meta Tags', () => {
    it('renders with proper meta tags', () => {
      render(<BulkApplyPage />);
      
      // Check if Helmet is used (meta tags are rendered)
      expect(document.title).toBe('Bulk Job Application - Buzz2Remote');
    });
  });

  describe('Responsive Design', () => {
    it('renders with proper responsive classes', () => {
      render(<BulkApplyPage />);
      
      // Find the main container div
      const container = document.querySelector('.container');
      expect(container).toHaveClass('container', 'mx-auto', 'px-4', 'py-8');
    });

    it('renders feature grid with responsive classes', () => {
      render(<BulkApplyPage />);
      
      // Find the feature grid container
      const featureGrid = document.querySelector('.grid.md\\:grid-cols-3');
      expect(featureGrid).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper heading hierarchy', () => {
      render(<BulkApplyPage />);
      
      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toHaveTextContent('Bulk Job Application');
      
      const h3Elements = screen.getAllByRole('heading', { level: 3 });
      expect(h3Elements).toHaveLength(4); // 3 feature cards + 1 pro tips
    });

    it('has proper semantic structure', () => {
      render(<BulkApplyPage />);
      
      // Check for main content areas
      expect(screen.getByText('Smart Selection')).toBeInTheDocument();
      expect(screen.getByText('Auto Fill Forms')).toBeInTheDocument();
      expect(screen.getByText('Smart Queue')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('handles missing user gracefully', () => {
      mockUseAuth.user = null;
      
      render(<BulkApplyPage />);
      
      // Page should still render without user info
      expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
      expect(screen.getByTestId('bulk-apply-manager')).toBeInTheDocument();
    });
  });

  describe('Integration', () => {
    it('integrates with BulkApplyManager component', () => {
      render(<BulkApplyPage />);
      
      const manager = screen.getByTestId('bulk-apply-manager');
      expect(manager).toBeInTheDocument();
      expect(manager).toHaveTextContent('Bulk Apply Manager');
    });

    it('provides proper context to child components', () => {
      render(<BulkApplyPage />);
      
      // Check if the page provides proper styling and layout
      const mainContainer = document.querySelector('.min-h-screen');
      expect(mainContainer).toBeInTheDocument();
    });
  });
}); 