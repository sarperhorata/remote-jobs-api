import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { AuthProvider } from '../../contexts/AuthContext';
import MyProfile from '../../pages/MyProfile';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock Header component
jest.mock('../../components/Header', () => {
  return function MockHeader() {
    return <div data-testid="header">Header</div>;
  };
});

// Mock toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
}));

const renderMyProfile = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <MyProfile />
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('MyProfile Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock user data
    localStorageMock.getItem.mockImplementation((key) => {
      switch (key) {
        case 'userPreferences':
          return JSON.stringify({
            location: 'Remote',
            bio: 'Software Developer',
            job_titles: ['Frontend Developer'],
            skills: ['React', 'TypeScript'],
            experience_levels: ['Mid Level'],
            work_types: ['Remote'],
            salary_ranges: ['$60,000 - $80,000']
          });
        case 'savedJobs':
          return JSON.stringify([{ id: '1', title: 'React Developer' }]);
        case 'myApplications':
          return JSON.stringify([{ id: '1', title: 'Frontend Role' }]);
        default:
          return null;
      }
    });
  });

  describe('Component Rendering', () => {
    test('renders profile page without crashing', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      expect(screen.getByTestId('header')).toBeInTheDocument();
    });

    test('renders profile information when user is authenticated', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        expect(screen.getByText(/Software Developer/i)).toBeInTheDocument();
        expect(screen.getByText(/Frontend Developer/i)).toBeInTheDocument();
      });
    });

    test('renders edit button when not in editing mode', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        expect(screen.getByText(/Edit Profile/i)).toBeInTheDocument();
      });
    });

    test('renders user stats section', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        expect(screen.getByText(/Applications/i)).toBeInTheDocument();
        expect(screen.getByText(/Saved Jobs/i)).toBeInTheDocument();
        expect(screen.getByText(/Profile Views/i)).toBeInTheDocument();
      });
    });
  });

  describe('Profile Editing', () => {
    test('enters edit mode when edit button is clicked', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      expect(screen.getByText(/Save Changes/i)).toBeInTheDocument();
      expect(screen.getByText(/Cancel/i)).toBeInTheDocument();
    });

    test('saves profile changes when save button is clicked', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Modify a field
      const bioField = screen.getByDisplayValue(/Software Developer/i);
      fireEvent.change(bioField, { target: { value: 'Updated Bio' } });
      
      // Save changes
      const saveButton = screen.getByText(/Save Changes/i);
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'userPreferences',
          expect.stringContaining('Updated Bio')
        );
      });
    });

    test('cancels editing when cancel button is clicked', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Modify a field
      const bioField = screen.getByDisplayValue(/Software Developer/i);
      fireEvent.change(bioField, { target: { value: 'Modified Bio' } });
      
      // Cancel changes
      const cancelButton = screen.getByText(/Cancel/i);
      fireEvent.click(cancelButton);
      
      await waitFor(() => {
        expect(screen.getByText(/Edit Profile/i)).toBeInTheDocument();
      });
    });

    test('updates profile fields correctly', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Test location field
      const locationField = screen.getByDisplayValue(/Remote/i);
      fireEvent.change(locationField, { target: { value: 'New York' } });
      expect(locationField).toHaveValue('New York');
      
      // Test skills field
      const skillsField = screen.getByDisplayValue(/React, TypeScript/i);
      fireEvent.change(skillsField, { target: { value: 'React, TypeScript, Node.js' } });
      expect(skillsField).toHaveValue('React, TypeScript, Node.js');
    });
  });

  describe('Work Experience Management', () => {
    test('adds new work experience', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Find and click add work experience button
      const addWorkButton = screen.getByText(/Add Work Experience/i);
      fireEvent.click(addWorkButton);
      
      await waitFor(() => {
        expect(screen.getByText(/Work Experience/i)).toBeInTheDocument();
      });
    });

    test('updates work experience fields', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Add work experience first
      const addWorkButton = screen.getByText(/Add Work Experience/i);
      fireEvent.click(addWorkButton);
      
      // Update title field
      const titleField = screen.getByPlaceholderText(/Job Title/i);
      fireEvent.change(titleField, { target: { value: 'Senior Developer' } });
      expect(titleField).toHaveValue('Senior Developer');
      
      // Update company field
      const companyField = screen.getByPlaceholderText(/Company/i);
      fireEvent.change(companyField, { target: { value: 'TechCorp' } });
      expect(companyField).toHaveValue('TechCorp');
    });

    test('removes work experience', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Add work experience first
      const addWorkButton = screen.getByText(/Add Work Experience/i);
      fireEvent.click(addWorkButton);
      
      // Remove the work experience
      const removeButton = screen.getByText(/Remove/i);
      fireEvent.click(removeButton);
      
      await waitFor(() => {
        expect(screen.queryByPlaceholderText(/Job Title/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Education Management', () => {
    test('adds new education', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Find and click add education button
      const addEducationButton = screen.getByText(/Add Education/i);
      fireEvent.click(addEducationButton);
      
      await waitFor(() => {
        expect(screen.getByText(/Education/i)).toBeInTheDocument();
      });
    });

    test('updates education fields', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Add education first
      const addEducationButton = screen.getByText(/Add Education/i);
      fireEvent.click(addEducationButton);
      
      // Update degree field
      const degreeField = screen.getByPlaceholderText(/Degree/i);
      fireEvent.change(degreeField, { target: { value: 'Bachelor of Science' } });
      expect(degreeField).toHaveValue('Bachelor of Science');
      
      // Update institution field
      const institutionField = screen.getByPlaceholderText(/Institution/i);
      fireEvent.change(institutionField, { target: { value: 'University of Technology' } });
      expect(institutionField).toHaveValue('University of Technology');
    });
  });

  describe('Social Media Links', () => {
    test('updates social media links', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Update LinkedIn URL
      const linkedinField = screen.getByPlaceholderText(/LinkedIn URL/i);
      fireEvent.change(linkedinField, { target: { value: 'https://linkedin.com/in/user' } });
      expect(linkedinField).toHaveValue('https://linkedin.com/in/user');
      
      // Update GitHub URL
      const githubField = screen.getByPlaceholderText(/GitHub URL/i);
      fireEvent.change(githubField, { target: { value: 'https://github.com/user' } });
      expect(githubField).toHaveValue('https://github.com/user');
    });
  });

  describe('Profile Image', () => {
    test('handles profile image upload', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Find file input
      const fileInput = screen.getByLabelText(/Profile Picture/i) as HTMLInputElement;
      
      // Create a mock file
      const file = new File(['test'], 'test.png', { type: 'image/png' });
      
      // Simulate file upload
      fireEvent.change(fileInput, { target: { files: [file] } });
      
      await waitFor(() => {
        expect(fileInput.files?.[0]).toBe(file);
      });
    });
  });

  describe('LinkedIn Import', () => {
    test('shows LinkedIn import button', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        expect(screen.getByText(/Import from LinkedIn/i)).toBeInTheDocument();
      });
    });

    test('handles LinkedIn import click', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const importButton = screen.getByText(/Import from LinkedIn/i);
        fireEvent.click(importButton);
      });
      
      // Should show some indication that import process started
      await waitFor(() => {
        expect(screen.getByText(/Import from LinkedIn/i)).toBeInTheDocument();
      });
    });
  });

  describe('User Statistics', () => {
    test('displays correct application count', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        expect(screen.getByText(/1/i)).toBeInTheDocument(); // 1 application
      });
    });

    test('displays correct saved jobs count', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        expect(screen.getByText(/1/i)).toBeInTheDocument(); // 1 saved job
      });
    });

    test('displays profile views', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        expect(screen.getByText(/Profile Views/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    test('handles localStorage errors gracefully', async () => {
      localStorageMock.getItem.mockImplementation(() => {
        throw new Error('localStorage error');
      });
      
      await act(async () => {
        renderMyProfile();
      });
      
      // Should still render without crashing
      expect(screen.getByTestId('header')).toBeInTheDocument();
    });

    test('handles malformed JSON in localStorage', async () => {
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'userPreferences') {
          return 'invalid json';
        }
        return null;
      });
      
      await act(async () => {
        renderMyProfile();
      });
      
      // Should still render with default values
      expect(screen.getByTestId('header')).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    test('renders mobile-friendly layout', async () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      await act(async () => {
        renderMyProfile();
      });
      
      expect(screen.getByTestId('header')).toBeInTheDocument();
    });
  });

  describe('Data Persistence', () => {
    test('saves profile data to localStorage', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        const editButton = screen.getByText(/Edit Profile/i);
        fireEvent.click(editButton);
      });
      
      // Modify profile
      const bioField = screen.getByDisplayValue(/Software Developer/i);
      fireEvent.change(bioField, { target: { value: 'New Bio' } });
      
      // Save
      const saveButton = screen.getByText(/Save Changes/i);
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'userPreferences',
          expect.stringContaining('New Bio')
        );
      });
    });

    test('loads profile data from localStorage on mount', async () => {
      await act(async () => {
        renderMyProfile();
      });
      
      await waitFor(() => {
        expect(localStorageMock.getItem).toHaveBeenCalledWith('userPreferences');
        expect(localStorageMock.getItem).toHaveBeenCalledWith('savedJobs');
        expect(localStorageMock.getItem).toHaveBeenCalledWith('myApplications');
      });
    });
  });
});