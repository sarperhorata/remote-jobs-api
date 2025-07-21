import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import AuthModal from '../../components/AuthModal';

beforeAll(() => {
  process.env.REACT_APP_API_URL = 'http://localhost:8001';
});

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('LinkedIn OAuth Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('AuthModal LinkedIn Button', () => {
    const renderAuthModal = () => {
      return render(
        <BrowserRouter>
          <AuthModal isOpen={true} onClose={() => {}} />
        </BrowserRouter>
      );
    };

    it('should render LinkedIn login button', () => {
      renderAuthModal();
      
      const linkedInButton = screen.getByText(/sign in with linkedin/i);
      expect(linkedInButton).toBeInTheDocument();
    });

    it('should call LinkedIn auth URL endpoint when button is clicked', async () => {
      const mockAuthUrl = 'https://www.linkedin.com/oauth/v2/authorization?client_id=test&redirect_uri=test&scope=r_liteprofile%20r_emailaddress&state=random_state';
      
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ auth_url: mockAuthUrl })
      });

      // Mock window.location.href
      Object.defineProperty(window, 'location', {
        value: { href: '' },
        writable: true
      });

      renderAuthModal();
      
      const linkedInButton = screen.getByText(/sign in with linkedin/i);
      fireEvent.click(linkedInButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/auth/linkedin/auth-url'),
          expect.any(Object)
        );
      });

      await waitFor(() => {
        expect(window.location.href).toBe(mockAuthUrl);
      });
    });

    it('should show error message when LinkedIn auth fails', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'LinkedIn authentication failed' })
      });

      renderAuthModal();
      
      const linkedInButton = screen.getByText(/sign in with linkedin/i);
      fireEvent.click(linkedInButton);

      await waitFor(() => {
        expect(screen.getByText(/linkedin authentication failed/i)).toBeInTheDocument();
      });
    });

    it('should handle network errors gracefully', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      renderAuthModal();
      
      const linkedInButton = screen.getByText(/sign in with linkedin/i);
      fireEvent.click(linkedInButton);

      await waitFor(() => {
        expect(screen.getByText(/linkedin authentication failed/i)).toBeInTheDocument();
      });
    });
  });
}); 