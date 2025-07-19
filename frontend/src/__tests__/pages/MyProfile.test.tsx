import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { AuthProvider } from '../../contexts/AuthContext';
import MyProfile from '../../pages/MyProfile';

// Mock the auth context
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: {
      id: '1',
      email: 'test@example.com',
      name: 'Test User'
    }
  })
}));

// Mock the API service
jest.mock('../../services/UserProfileService', () => ({
  getProfile: jest.fn(() => Promise.resolve({
    id: '1',
    name: 'Test User',
    email: 'test@example.com',
    work_experience: [],
    education: []
  })),
  updateProfile: jest.fn(() => Promise.resolve({ success: true }))
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          {component}
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('MyProfile Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders profile page correctly', async () => {
    renderWithRouter(<MyProfile />);
    
    await waitFor(() => {
      expect(screen.getByText(/my profile/i)).toBeInTheDocument();
      expect(screen.getByText(/work experience/i)).toBeInTheDocument();
      expect(screen.getByText(/education/i)).toBeInTheDocument();
    });
  });

  test('adds work experience correctly', async () => {
    renderWithRouter(<MyProfile />);
    
    await waitFor(() => {
      expect(screen.getByText(/add experience/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/add experience/i));

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/job title/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/company/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/location/i)).toBeInTheDocument();
    });
  });

  test('adds education correctly', async () => {
    renderWithRouter(<MyProfile />);
    
    await waitFor(() => {
      expect(screen.getByText(/add education/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/add education/i));

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/institution/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/degree/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/field of study/i)).toBeInTheDocument();
    });
  });

  test('date fields are properly laid out', async () => {
    renderWithRouter(<MyProfile />);
    
    await waitFor(() => {
      expect(screen.getByText(/add experience/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/add experience/i));

    await waitFor(() => {
      // Check that date fields are present
      const startDateInput = screen.getByDisplayValue('');
      expect(startDateInput).toBeInTheDocument();
      
      // Check that "Currently working here" checkbox is present
      expect(screen.getByText(/currently working here/i)).toBeInTheDocument();
    });
  });

  test('education date fields are properly laid out', async () => {
    renderWithRouter(<MyProfile />);
    
    await waitFor(() => {
      expect(screen.getByText(/add education/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/add education/i));

    await waitFor(() => {
      // Check that date fields are present
      const startDateInput = screen.getByDisplayValue('');
      expect(startDateInput).toBeInTheDocument();
      
      // Check that "Currently studying here" checkbox is present
      expect(screen.getByText(/currently studying here/i)).toBeInTheDocument();
    });
  });
}); 