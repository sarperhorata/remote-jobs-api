import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import SetPassword from '../../pages/SetPassword';
import { onboardingService } from '../../services/onboardingService';

// Mock the service
jest.mock('../../services/onboardingService');

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', async () => {
  const actual = await jest.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useSearchParams: jest.fn(() => [new URLSearchParams('token=test-token')])
  };
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('SetPassword', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('should render password form correctly', () => {
    renderWithRouter(<SetPassword />);
    
    expect(screen.getByText(/Şifrenizi Belirleyin/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Şifre/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Şifre Tekrar/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Şifre Belirle/i })).toBeInTheDocument();
  });

  it('should show password strength indicator', async () => {
    renderWithRouter(<SetPassword />);
    
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

  it('should validate password requirements', async () => {
    renderWithRouter(<SetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    const submitButton = screen.getByRole('button', { name: /Şifre Belirle/i });

    // Test minimum length
    await user.type(passwordInput, '123');
    fireEvent.click(submitButton);
    expect(screen.getByText(/en az 8 karakter/i)).toBeInTheDocument();

    // Test uppercase requirement
    await user.clear(passwordInput);
    await user.type(passwordInput, 'lowercase123');
    fireEvent.click(submitButton);
    expect(screen.getByText(/büyük harf/i)).toBeInTheDocument();

    // Test number requirement  
    await user.clear(passwordInput);
    await user.type(passwordInput, 'NoNumbers');
    fireEvent.click(submitButton);
    expect(screen.getByText(/rakam/i)).toBeInTheDocument();
  });

  it('should validate password confirmation match', async () => {
    renderWithRouter(<SetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifre Belirle/i });

    await user.type(passwordInput, 'ValidPass123!');
    await user.type(confirmInput, 'DifferentPass123!');
    
    fireEvent.click(submitButton);
    
    expect(screen.getByText(/eşleşmiyor/i)).toBeInTheDocument();
  });

  it('should set password successfully and navigate', async () => {
    const mockResponse = {
      message: 'Şifre başarıyla belirlendi',
      onboarding_step: 2,
      next_step: 'profile_setup'
    };

    (onboardingService.setPassword).mockResolvedValue(mockResponse);

    renderWithRouter(<SetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifre Belirle/i });

    await user.type(passwordInput, 'SecurePass123!');
    await user.type(confirmInput, 'SecurePass123!');
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(onboardingService.setPassword).toHaveBeenCalledWith(
        'test-token',
        'SecurePass123!',
        'SecurePass123!'
      );
    });

    expect(screen.getByText(/Şifre başarıyla belirlendi/i)).toBeInTheDocument();
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding/profile-setup');
    });
  });

  it('should handle invalid token error', async () => {
    (onboardingService.setPassword).mockRejectedValue(
      new Error('Geçersiz veya süresi dolmuş token')
    );

    renderWithRouter(<SetPassword />);
    
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

    renderWithRouter(<SetPassword />);
    
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
    renderWithRouter(<SetPassword />);
    
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
    renderWithRouter(<SetPassword />);
    
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

    renderWithRouter(<SetPassword />);
    
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

    renderWithRouter(<SetPassword />);

    expect(screen.getByText(/Geçersiz Bağlantı/i)).toBeInTheDocument();
    expect(screen.getByText(/Şifre belirleme bağlantısı geçersiz/i)).toBeInTheDocument();
  });

  it('should show password requirements checklist', async () => {
    renderWithRouter(<SetPassword />);
    
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