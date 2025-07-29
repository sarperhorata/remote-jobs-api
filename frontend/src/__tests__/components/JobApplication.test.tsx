import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobApplication from '../../components/JobApplication';
import { Job } from '../../types/job';
import { jobService } from '../../services/AllServices';

// Mock jobService
jest.mock('../../services/AllServices', () => ({
  jobService: {
    applyToJob: jest.fn(),
  },
}));

// Mock useNavigate
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

const mockJob: Job = {
  _id: 'job-1',
  id: 'job-1',
  title: 'Senior React Developer',
  company: 'Tech Corp',
  companyName: 'Tech Corp',
  location: 'Remote',
  job_type: 'Full-time',
  description: 'We are looking for a senior React developer...',
  skills: ['React', 'TypeScript', 'Node.js'],
  postedAt: '2024-01-15T10:00:00Z',
  salary_min: 80000,
  salary_max: 120000,
  salary_currency: 'USD'
};

const renderJobApplication = (job: Job = mockJob) => {
  return render(
    <JobApplication job={job} />
  );
};

describe('JobApplication Component', () => {
  const mockApplyToJob = jobService.applyToJob as jest.MockedFunction<typeof jobService.applyToJob>;
  const mockNavigate = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock useNavigate
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);
  });

  test('renders application form with job title', () => {
    renderJobApplication();
    
    expect(screen.getByText('Apply for Senior React Developer')).toBeInTheDocument();
    expect(screen.getByLabelText('Full Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Resume')).toBeInTheDocument();
    expect(screen.getByLabelText('Cover Letter')).toBeInTheDocument();
    expect(screen.getByText('Submit Application')).toBeInTheDocument();
  });

  test('handles form input changes', () => {
    renderJobApplication();
    
    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const coverLetterInput = screen.getByLabelText('Cover Letter');
    
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
    fireEvent.change(coverLetterInput, { target: { value: 'I am interested in this position' } });
    
    expect(nameInput).toHaveValue('John Doe');
    expect(emailInput).toHaveValue('john@example.com');
    expect(coverLetterInput).toHaveValue('I am interested in this position');
  });

  test('handles file upload', () => {
    renderJobApplication();
    
    const fileInput = screen.getByLabelText('Resume');
    const file = new File(['resume content'], 'resume.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    expect(fileInput.files?.[0]).toBe(file);
  });

  test('submits application successfully', async () => {
    mockApplyToJob.mockResolvedValue({ success: true });
    renderJobApplication();
    
    // Fill out the form
    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const fileInput = screen.getByLabelText('Resume');
    const coverLetterInput = screen.getByLabelText('Cover Letter');
    
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
    fireEvent.change(coverLetterInput, { target: { value: 'I am interested in this position' } });
    
    const file = new File(['resume content'], 'resume.pdf', { type: 'application/pdf' });
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // Submit the form
    const submitButton = screen.getByText('Submit Application');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockApplyToJob).toHaveBeenCalledWith('current-user', 'job-1');
      expect(mockNavigate).toHaveBeenCalledWith('/my-jobs');
    });
  });

  test('handles application submission error', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    mockApplyToJob.mockRejectedValue(new Error('Application failed'));
    
    renderJobApplication();
    
    // Fill out the form
    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const fileInput = screen.getByLabelText('Resume');
    
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
    
    const file = new File(['resume content'], 'resume.pdf', { type: 'application/pdf' });
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // Submit the form
    const submitButton = screen.getByText('Submit Application');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Error submitting application:', expect.any(Error));
    });
    
    consoleErrorSpy.mockRestore();
  });

  test('validates required fields', () => {
    renderJobApplication();
    
    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const fileInput = screen.getByLabelText('Resume');
    
    expect(nameInput).toBeRequired();
    expect(emailInput).toBeRequired();
    expect(fileInput).toBeRequired();
  });

  test('has correct form structure and styling', () => {
    renderJobApplication();
    
    const form = screen.getByText('Submit Application').closest('form');
    expect(form).toBeInTheDocument();
    
    const container = screen.getByText('Apply for Senior React Developer').closest('.bg-white.p-6.rounded-lg.shadow-md');
    expect(container).toBeInTheDocument();
    
    const submitButton = screen.getByText('Submit Application');
    expect(submitButton).toHaveClass('bg-blue-600', 'hover:bg-blue-700', 'text-white');
  });

  test('handles different job titles', () => {
    const differentJob = { ...mockJob, title: 'Frontend Developer' };
    renderJobApplication(differentJob);
    
    expect(screen.getByText('Apply for Frontend Developer')).toBeInTheDocument();
  });

  test('file input accepts correct file types', () => {
    renderJobApplication();
    
    const fileInput = screen.getByLabelText('Resume');
    expect(fileInput).toHaveAttribute('accept', '.pdf,.doc,.docx');
  });

  test('cover letter textarea has correct rows', () => {
    renderJobApplication();
    
    const coverLetterInput = screen.getByLabelText('Cover Letter');
    expect(coverLetterInput).toHaveAttribute('rows', '5');
  });



  test('handles multiple file selections', () => {
    renderJobApplication();
    
    const fileInput = screen.getByLabelText('Resume');
    const file1 = new File(['resume content 1'], 'resume1.pdf', { type: 'application/pdf' });
    const file2 = new File(['resume content 2'], 'resume2.pdf', { type: 'application/pdf' });
    
    // Select first file
    fireEvent.change(fileInput, { target: { files: [file1] } });
    expect(fileInput.files?.[0]).toBe(file1);
    
    // Select second file (should replace the first)
    fireEvent.change(fileInput, { target: { files: [file2] } });
    expect(fileInput.files?.[0]).toBe(file2);
  });

  test('handles empty file selection', () => {
    renderJobApplication();
    
    const fileInput = screen.getByLabelText('Resume');
    
    // Initially no file selected
    expect(fileInput.files).toHaveLength(0);
    
    // Select a file
    const file = new File(['resume content'], 'resume.pdf', { type: 'application/pdf' });
    fireEvent.change(fileInput, { target: { files: [file] } });
    expect(fileInput.files?.[0]).toBe(file);
    
    // Clear file selection
    fireEvent.change(fileInput, { target: { files: [] } });
    expect(fileInput.files).toHaveLength(0);
  });

  test('maintains form state during typing', () => {
    renderJobApplication();
    
    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const coverLetterInput = screen.getByLabelText('Cover Letter');
    
    // Type in name
    fireEvent.change(nameInput, { target: { value: 'J' } });
    expect(nameInput).toHaveValue('J');
    
    // Type in email
    fireEvent.change(emailInput, { target: { value: 'j' } });
    expect(emailInput).toHaveValue('j');
    expect(nameInput).toHaveValue('J'); // Name should still have its value
    
    // Type in cover letter
    fireEvent.change(coverLetterInput, { target: { value: 'I' } });
    expect(coverLetterInput).toHaveValue('I');
    expect(nameInput).toHaveValue('J'); // Name should still have its value
    expect(emailInput).toHaveValue('j'); // Email should still have its value
  });
});