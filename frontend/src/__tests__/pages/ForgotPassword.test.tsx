import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ForgotPassword from '../../pages/ForgotPassword';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

// Mock getApiUrl
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockResolvedValue('http://localhost:8000/api/v1')
}));

// Mock fetch
global.fetch = jest.fn();

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ForgotPassword', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
    (global.fetch as jest.Mock).mockClear();
  });

  it('should render forgot password form correctly', () => {
    renderWithRouter(<ForgotPassword />);
    
    expect(screen.getByText('Şifremi Unuttum')).toBeInTheDocument();
    expect(screen.getByText('Email adresinizi girin, size şifre sıfırlama linki gönderelim')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('your@email.com')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Şifre Sıfırlama Linki Gönder' })).toBeInTheDocument();
  });

  it('should handle successful password reset request', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Email sent' })
    });

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('your@email.com');
    const submitButton = screen.getByRole('button', { name: 'Şifre Sıfırlama Linki Gönder' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Email Gönderildi!')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });
  });

  it('should handle error during password reset', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Email not found' })
    });

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('your@email.com');
    const submitButton = screen.getByRole('button', { name: 'Şifre Sıfırlama Linki Gönder' });
    
    fireEvent.change(emailInput, { target: { value: 'notfound@example.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Email not found')).toBeInTheDocument();
    });
  });

  it('should navigate back to login', () => {
    renderWithRouter(<ForgotPassword />);
    
    const backButton = screen.getByText('Giriş Sayfasına Dön');
    fireEvent.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('should show loading state during submission', async () => {
    (global.fetch as jest.Mock).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 100))
    );

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('your@email.com');
    const submitButton = screen.getByRole('button', { name: 'Şifre Sıfırlama Linki Gönder' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);

    expect(screen.getByText('Gönderiliyor...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });
});
