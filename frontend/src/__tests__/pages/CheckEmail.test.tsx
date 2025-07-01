import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CheckEmail from '../../pages/CheckEmail';

// Mock react-router-dom hooks
const mockNavigate = jest.fn();
const mockLocation = { state: { email: 'test@example.com', message: 'Doğrulama emaili gönderildi' } };

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => mockLocation
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('CheckEmail', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('should render email check message correctly', () => {
    renderWithRouter(<CheckEmail />);
    
    expect(screen.getByText('Email Adresinizi Kontrol Edin')).toBeInTheDocument();
    expect(screen.getByText('Kayıt işleminizi tamamlamak için size email gönderdik')).toBeInTheDocument();
    expect(screen.getByText('Email Gönderildi!')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('should navigate to home when button is clicked', () => {
    renderWithRouter(<CheckEmail />);
    
    const homeButton = screen.getByRole('button', { name: 'Ana Sayfaya Dön' });
    fireEvent.click(homeButton);

    expect(mockNavigate).toHaveBeenCalledWith('/');
  });
});
