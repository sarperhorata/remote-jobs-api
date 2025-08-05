import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import SkillsExtraction from '../../pages/SkillsExtraction';

// Mock the Layout component
jest.mock('../../components/Layout', () => {
  return function MockLayout({ children }: { children: React.ReactNode }) {
    return <div data-testid="layout">{children}</div>;
  };
});

// Mock react-router-dom hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/skills-extraction' }),
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <ThemeProvider>
          {component}
        </ThemeProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('SkillsExtraction Page', () => {
  beforeEach(() => {
    // Mock fetch for API calls
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders Skills Extraction page with correct title', () => {
    renderWithProviders(<SkillsExtraction />);
    
    expect(screen.getByText('AI Skills Extraction')).toBeInTheDocument();
    expect(screen.getByText(/Upload your CV and let our AI extract and categorize/)).toBeInTheDocument();
  });

  test('displays file upload area with supported formats', () => {
    renderWithProviders(<SkillsExtraction />);
    
    expect(screen.getByText('Upload your CV/Resume')).toBeInTheDocument();
    expect(screen.getByText('Supported formats: PDF, DOCX, TXT (Max 10MB)')).toBeInTheDocument();
    expect(screen.getByText('Choose File')).toBeInTheDocument();
  });

  test('allows file upload and displays file info', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });
  });

  test('shows extract skills button when file is uploaded', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('Extract Skills')).toBeInTheDocument();
    });
  });

  test('extracts skills and shows results', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Skills Analysis Summary')).toBeInTheDocument();
      expect(screen.getByText('Programming Languages')).toBeInTheDocument();
      expect(screen.getByText('Frameworks & Libraries')).toBeInTheDocument();
    });
  });

  test('displays skills categories correctly', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Programming Languages')).toBeInTheDocument();
      expect(screen.getByText('JavaScript')).toBeInTheDocument();
      expect(screen.getByText('Python')).toBeInTheDocument();
      expect(screen.getByText('React')).toBeInTheDocument();
      expect(screen.getByText('MongoDB')).toBeInTheDocument();
    });
  });

  test('displays skill proficiency levels', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('advanced')).toBeInTheDocument();
      expect(screen.getByText('intermediate')).toBeInTheDocument();
      expect(screen.getByText('beginner')).toBeInTheDocument();
    });
  });

  test('displays confidence scores for skills', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('95%')).toBeInTheDocument();
      expect(screen.getByText('88%')).toBeInTheDocument();
      expect(screen.getByText('82%')).toBeInTheDocument();
    });
  });

  test('displays summary statistics', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Total Skills')).toBeInTheDocument();
      expect(screen.getByText('Avg Confidence')).toBeInTheDocument();
      expect(screen.getByText('Categories')).toBeInTheDocument();
      expect(screen.getByText('Advanced Skills')).toBeInTheDocument();
    });
  });

  test('shows AI recommendations section', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('AI Recommendations')).toBeInTheDocument();
      expect(screen.getByText('Skills to Improve')).toBeInTheDocument();
      expect(screen.getByText('Top Skills')).toBeInTheDocument();
    });
  });

  test('allows editing skills when edit mode is enabled', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      const editButton = screen.getByText('Edit Skills');
      fireEvent.click(editButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Save Changes')).toBeInTheDocument();
    });
  });

  test('shows action buttons after extraction', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Extract Another CV')).toBeInTheDocument();
      expect(screen.getByText('Download Report')).toBeInTheDocument();
      expect(screen.getByText('Update Profile')).toBeInTheDocument();
    });
  });

  test('shows error message when extraction fails', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    // Mock a failed API call
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('API Error'));
    
    await waitFor(() => {
      expect(screen.getByText('Skills extraction failed. Please try again.')).toBeInTheDocument();
    });
  });

  test('displays years of experience for skills', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('4 years')).toBeInTheDocument();
      expect(screen.getByText('3 years')).toBeInTheDocument();
      expect(screen.getByText('2 years')).toBeInTheDocument();
    });
  });

  test('displays different file type icons', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('test.docx')).toBeInTheDocument();
    });
  });

  test('resets to initial state when extract another CV is clicked', async () => {
    renderWithProviders(<SkillsExtraction />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const extractButton = screen.getByText('Extract Skills');
      fireEvent.click(extractButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Skills Analysis Summary')).toBeInTheDocument();
    });
    
    const resetButton = screen.getByText('Extract Another CV');
    fireEvent.click(resetButton);
    
    await waitFor(() => {
      expect(screen.getByText('Upload your CV/Resume')).toBeInTheDocument();
    });
  });
}); 