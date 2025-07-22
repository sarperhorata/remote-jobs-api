import React from 'react';
import { render, screen } from '@testing-library/react';
import DragDropCVUpload from '../../components/DragDropCVUpload';

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('DragDropCVUpload', () => {
  const mockOnFileUpload = jest.fn();
  const mockOnFileRemove = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders upload zone correctly', () => {
    render(
      <DragDropCVUpload
        onFileUpload={mockOnFileUpload}
        onFileRemove={mockOnFileRemove}
      />
    );

    expect(screen.getByText('Upload your CV')).toBeInTheDocument();
    expect(screen.getByText('Drag and drop your CV file here, or click to browse')).toBeInTheDocument();
    expect(screen.getByText('Choose File')).toBeInTheDocument();
  });

  it('shows current CV when cvUrl is provided', () => {
    render(
      <DragDropCVUpload
        onFileUpload={mockOnFileUpload}
        onFileRemove={mockOnFileRemove}
        currentCVUrl="https://example.com/cv.pdf"
      />
    );

    expect(screen.getByText('Current CV')).toBeInTheDocument();
    expect(screen.getByText('Your CV is uploaded and ready')).toBeInTheDocument();
    expect(screen.getByText('View')).toBeInTheDocument();
    expect(screen.getByText('Remove')).toBeInTheDocument();
  });

  it('shows upload progress when isUploading is true', () => {
    render(
      <DragDropCVUpload
        onFileUpload={mockOnFileUpload}
        onFileRemove={mockOnFileRemove}
        isUploading={true}
      />
    );

    expect(screen.getByText('Processing your CV...')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows upload tips', () => {
    render(
      <DragDropCVUpload
        onFileUpload={mockOnFileUpload}
        onFileRemove={mockOnFileRemove}
      />
    );

    expect(screen.getByText('💡 Upload Tips')).toBeInTheDocument();
    expect(screen.getByText(/Use PDF format for best compatibility/)).toBeInTheDocument();
    expect(screen.getByText(/Ensure your CV is up-to-date/)).toBeInTheDocument();
  });

  it('displays supported formats and file size limit', () => {
    render(
      <DragDropCVUpload
        onFileUpload={mockOnFileUpload}
        onFileRemove={mockOnFileRemove}
        maxFileSize={5}
        acceptedFileTypes={['.pdf', '.doc', '.docx']}
      />
    );

    expect(screen.getByText('Supported formats: .pdf, .doc, .docx')).toBeInTheDocument();
    expect(screen.getByText('Maximum file size: 5MB')).toBeInTheDocument();
  });



  it('shows file input with correct accept attribute', () => {
    render(
      <DragDropCVUpload
        onFileUpload={mockOnFileUpload}
        onFileRemove={mockOnFileRemove}
        acceptedFileTypes={['.pdf', '.doc']}
      />
    );

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(fileInput).toHaveAttribute('accept', '.pdf,.doc');
  });
}); 