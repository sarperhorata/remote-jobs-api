import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import EmailVerification from '../../pages/EmailVerification';

// Mock services
jest.mock('../../services/onboardingService', () => ({
  onboardingService: {
    verifyEmail: jest.fn()
  }
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useSearchParams: () => [new URLSearchParams('?token=test-token')],
  useNavigate: () => jest.fn()
}));

describe('EmailVerification', () => {
  it('renders email verification page', () => {
    render(
      <BrowserRouter>
        <EmailVerification />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Email Doğrulama')).toBeInTheDocument();
  });
}); 