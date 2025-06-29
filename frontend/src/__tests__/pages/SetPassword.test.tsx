import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import SetPassword from '../../pages/SetPassword';
import { onboardingService } from '../../services/onboardingService';

// Mock the service
jest.mock('../../services/onboardingService');

// Mock react-router-dom
jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useSearchParams: () => [
      new URLSearchParams('?token=test-token'),
      jest.fn()
    ],
    useNavigate: () => jest.fn(),
  };
});

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('SetPassword', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders set password form', () => {
    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );

    expect(screen.getByText('Set Your Password')).toBeInTheDocument();
    expect(screen.getByLabelText('New Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
  });

  it('validates password requirements', async () => {
    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );

    const passwordInput = screen.getByLabelText('New Password');
    const confirmInput = screen.getByLabelText('Confirm Password');
    const submitButton = screen.getByRole('button', { name: /set password/i });

    fireEvent.change(passwordInput, { target: { value: '123' } });
    fireEvent.change(confirmInput, { target: { value: '123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument();
    });
  });

  it('validates password confirmation match', async () => {
    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );

    const passwordInput = screen.getByLabelText('New Password');
    const confirmInput = screen.getByLabelText('Confirm Password');
    const submitButton = screen.getByRole('button', { name: /set password/i });

    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmInput, { target: { value: 'different123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ message: 'Password set successfully' })
    });
    global.fetch = mockFetch;

    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );

    const passwordInput = screen.getByLabelText('New Password');
    const confirmInput = screen.getByLabelText('Confirm Password');
    const submitButton = screen.getByRole('button', { name: /set password/i });

    fireEvent.change(passwordInput, { target: { value: 'ValidPassword123!' } });
    fireEvent.change(confirmInput, { target: { value: 'ValidPassword123!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/auth/set-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: 'test-token',
          password: 'ValidPassword123!'
        })
      });
    });
  });

  it('should show password strength indicator', async () => {
    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );
    
    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    
    await user.type(passwordInput, 'weak');
    expect(screen.getByText(/Zayıf/i)).toBeInTheDocument();
    expect(screen.getByTestId('strength-indicator')).toHaveClass('strength-weak');

    await user.clear(passwordInput);
    await user.type(passwordInput, 'MediumPass123');
    expect(screen.getByText(/Orta/i)).toBeInTheDocument();
    expect(screen.getByTestId('strength-indicator')).toHaveClass('strength-medium');

    await user.clear(passwordInput);
    await user.type(passwordInput, 'StrongPass123!@#');
    expect(screen.getByText(/Güçlü/i)).toBeInTheDocument();
    expect(screen.getByTestId('strength-indicator')).toHaveClass('strength-strong');
  });

  it('should handle invalid token error', async () => {
    (onboardingService.setPassword).mockRejectedValue(
      new Error('Geçersiz veya süresi dolmuş token')
    );

    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );
    
    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifre Belirle/i });

    await user.type(passwordInput, 'SecurePass123!');
    await user.type(confirmInput, 'SecurePass123!');
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Geçersiz veya süresi dolmuş token/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Yeni doğrulama emaili almak için/i)).toBeInTheDocument();
  });

  it('should handle server error', async () => {
    (onboardingService.setPassword).mockRejectedValue(
      new Error('Server error')
    );

    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );
    
    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifre Belirle/i });

    await user.type(passwordInput, 'SecurePass123!');
    await user.type(confirmInput, 'SecurePass123!');
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Server error/i)).toBeInTheDocument();
    });
  });

  it('should toggle password visibility', async () => {
    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );
    
    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    const toggleButton = screen.getByTestId('password-toggle');

    // Initially password type
    expect(passwordInput).toHaveAttribute('type', 'password');

    // Click to show password
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');

    // Click to hide password
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('should disable submit button when form is invalid', async () => {
    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );
    
    const submitButton = screen.getByRole('button', { name: /Şifre Belirle/i });
    
    // Initially disabled
    expect(submitButton).toBeDisabled();

    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    await user.type(passwordInput, 'weak');
    
    // Still disabled for weak password
    expect(submitButton).toBeDisabled();

    await user.clear(passwordInput);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    await user.type(passwordInput, 'StrongPass123!');
    await user.type(confirmInput, 'StrongPass123!');
    
    // Enabled when both passwords are valid and match
    expect(submitButton).toBeEnabled();
  });

  it('should show loading state during submission', async () => {
    (onboardingService.setPassword).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );
    
    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifre Belirle/i });

    await user.type(passwordInput, 'SecurePass123!');
    await user.type(confirmInput, 'SecurePass123!');
    
    fireEvent.click(submitButton);

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  it('should handle missing token in URL', () => {
    (require('react-router-dom').useSearchParams).mockReturnValue([
      new URLSearchParams('')
    ]);

    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );

    expect(screen.getByText(/Geçersiz Bağlantı/i)).toBeInTheDocument();
    expect(screen.getByText(/Şifre belirleme bağlantısı geçersiz/i)).toBeInTheDocument();
  });

  it('should show password requirements checklist', async () => {
    render(
      <TestWrapper>
        <SetPassword />
      </TestWrapper>
    );
    
    expect(screen.getByText(/En az 8 karakter/i)).toBeInTheDocument();
    expect(screen.getByText(/En az bir büyük harf/i)).toBeInTheDocument();
    expect(screen.getByText(/En az bir küçük harf/i)).toBeInTheDocument();
    expect(screen.getByText(/En az bir rakam/i)).toBeInTheDocument();
    expect(screen.getByText(/En az bir özel karakter/i)).toBeInTheDocument();

    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    await user.type(passwordInput, 'StrongPass123!');

    // Requirements should be marked as met
    expect(screen.getByTestId('requirement-length')).toHaveClass('requirement-met');
    expect(screen.getByTestId('requirement-uppercase')).toHaveClass('requirement-met');
    expect(screen.getByTestId('requirement-lowercase')).toHaveClass('requirement-met');
    expect(screen.getByTestId('requirement-number')).toHaveClass('requirement-met');
    expect(screen.getByTestId('requirement-special')).toHaveClass('requirement-met');
  });
}); 