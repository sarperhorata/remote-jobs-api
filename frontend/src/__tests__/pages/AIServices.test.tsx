import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import AIServices from '../../pages/AIServices';

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
  useLocation: () => ({ pathname: '/ai-services' }),
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

describe('AIServices Page', () => {
  beforeEach(() => {
    // Mock fetch for API calls
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders AI Services page with correct title', () => {
    renderWithProviders(<AIServices />);
    
    expect(screen.getByText('AI-Powered Career Services')).toBeInTheDocument();
    expect(screen.getByText(/Leverage artificial intelligence to parse your resume/)).toBeInTheDocument();
  });

  test('displays tab navigation with three tabs', () => {
    renderWithProviders(<AIServices />);
    
    expect(screen.getByText('Resume Parser')).toBeInTheDocument();
    expect(screen.getByText('Job Matching')).toBeInTheDocument();
    expect(screen.getByText('Salary Prediction')).toBeInTheDocument();
  });

  test('starts with resume parser tab active', () => {
    renderWithProviders(<AIServices />);
    
    expect(screen.getByText('Upload your resume')).toBeInTheDocument();
    expect(screen.getByText('Supported formats: PDF, DOCX, TXT (Max 10MB)')).toBeInTheDocument();
  });

  test('allows file upload and displays file info', async () => {
    renderWithProviders(<AIServices />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });
  });

  test('shows parse resume button when file is uploaded', async () => {
    renderWithProviders(<AIServices />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('Parse Resume')).toBeInTheDocument();
    });
  });

  test('parses resume and shows results', async () => {
    renderWithProviders(<AIServices />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const parseButton = screen.getByText('Parse Resume');
      fireEvent.click(parseButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Parsed Resume Data')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john.doe@email.com')).toBeInTheDocument();
    });
  });

  test('switches to job matching tab and shows requirement message', async () => {
    renderWithProviders(<AIServices />);
    
    const jobMatchingTab = screen.getByText('Job Matching');
    fireEvent.click(jobMatchingTab);
    
    await waitFor(() => {
      expect(screen.getByText('Parse Your Resume First')).toBeInTheDocument();
      expect(screen.getByText(/Upload and parse your resume to find the best job matches/)).toBeInTheDocument();
    });
  });

  test('switches to salary prediction tab and shows requirement message', async () => {
    renderWithProviders(<AIServices />);
    
    const salaryTab = screen.getByText('Salary Prediction');
    fireEvent.click(salaryTab);
    
    await waitFor(() => {
      expect(screen.getByText('Parse Your Resume First')).toBeInTheDocument();
      expect(screen.getByText(/Upload and parse your resume to get accurate salary predictions/)).toBeInTheDocument();
    });
  });

  test('finds job matches after resume is parsed', async () => {
    renderWithProviders(<AIServices />);
    
    // First parse a resume
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const parseButton = screen.getByText('Parse Resume');
      fireEvent.click(parseButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Parsed Resume Data')).toBeInTheDocument();
    });
    
    // Switch to job matching tab
    const jobMatchingTab = screen.getByText('Job Matching');
    fireEvent.click(jobMatchingTab);
    
    await waitFor(() => {
      const findMatchesButton = screen.getByText('Find Job Matches');
      fireEvent.click(findMatchesButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('92% Match')).toBeInTheDocument();
    });
  });

  test('predicts salary after resume is parsed', async () => {
    renderWithProviders(<AIServices />);
    
    // First parse a resume
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const parseButton = screen.getByText('Parse Resume');
      fireEvent.click(parseButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Parsed Resume Data')).toBeInTheDocument();
    });
    
    // Switch to salary prediction tab
    const salaryTab = screen.getByText('Salary Prediction');
    fireEvent.click(salaryTab);
    
    await waitFor(() => {
      const predictButton = screen.getByText('Predict Salary');
      fireEvent.click(predictButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('$125,000')).toBeInTheDocument();
      expect(screen.getByText('85% Confidence')).toBeInTheDocument();
    });
  });

  test('displays file type icons correctly', async () => {
    renderWithProviders(<AIServices />);
    
    const file = new File(['test content'], 'test.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('test.docx')).toBeInTheDocument();
    });
  });

  test('shows error message when parsing fails', async () => {
    renderWithProviders(<AIServices />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const parseButton = screen.getByText('Parse Resume');
      fireEvent.click(parseButton);
    });
    
    // Mock a failed API call
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('API Error'));
    
    await waitFor(() => {
      expect(screen.getByText('Resume parsing failed. Please try again.')).toBeInTheDocument();
    });
  });

  test('displays skills in parsed resume', async () => {
    renderWithProviders(<AIServices />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const parseButton = screen.getByText('Parse Resume');
      fireEvent.click(parseButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('React')).toBeInTheDocument();
      expect(screen.getByText('Node.js')).toBeInTheDocument();
      expect(screen.getByText('Python')).toBeInTheDocument();
    });
  });

  test('displays experience in parsed resume', async () => {
    renderWithProviders(<AIServices />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileInput = screen.getByAcceptingFiles();
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      const parseButton = screen.getByText('Parse Resume');
      fireEvent.click(parseButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('Tech Corp')).toBeInTheDocument();
      expect(screen.getByText('2020 - Present')).toBeInTheDocument();
    });
  });
}); 