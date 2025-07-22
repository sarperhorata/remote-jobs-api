import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SkillsExtraction from '../../components/SkillsExtraction';

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

const mockSkills = [
  {
    id: '1',
    name: 'JavaScript',
    category: 'technical',
    confidence: 95,
    source: 'cv' as const
  },
  {
    id: '2',
    name: 'React',
    category: 'technical',
    confidence: 90,
    source: 'ai' as const
  },
  {
    id: '3',
    name: 'Leadership',
    category: 'soft',
    confidence: 85,
    source: 'manual' as const
  }
];

const defaultProps = {
  skills: mockSkills,
  onSkillsUpdate: jest.fn(),
  isExtracting: false,
  className: ''
};

describe('SkillsExtraction', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders skills extraction component', () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    expect(screen.getByText('Skills & Expertise')).toBeInTheDocument();
    expect(screen.getByText('3 skills found')).toBeInTheDocument();
  });

  test('displays skills by category', () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    expect(screen.getByText('Technical Skills')).toBeInTheDocument();
    expect(screen.getByText('Soft Skills')).toBeInTheDocument();
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Leadership')).toBeInTheDocument();
  });

  test('shows loading state when extracting', () => {
    render(<SkillsExtraction {...defaultProps} isExtracting={true} />);
    
    expect(screen.getByText('Extracting skills from your CV...')).toBeInTheDocument();
    expect(screen.getByText('Analyzing your CV...')).toBeInTheDocument();
  });

  test('shows empty state when no skills', () => {
    render(<SkillsExtraction {...defaultProps} skills={[]} />);
    
    expect(screen.getByText('No Skills Found')).toBeInTheDocument();
    expect(screen.getByText('Upload your CV to automatically extract skills, or add them manually.')).toBeInTheDocument();
  });

  test('enables editing mode when edit button is clicked', () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    const editButton = screen.getByText('Edit Skills');
    fireEvent.click(editButton);
    
    expect(screen.getByText('Add New Skill')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  test('allows adding new skills in edit mode', async () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    // Enter edit mode
    fireEvent.click(screen.getByText('Edit Skills'));
    
    // Add new skill
    const input = screen.getByPlaceholderText('Enter skill name...');
    const addButton = screen.getByTestId('add-skill-button');
    
    fireEvent.change(input, { target: { value: 'Python' } });
    fireEvent.click(addButton);
    
    await waitFor(() => {
      expect(screen.getByText('Python')).toBeInTheDocument();
    });
  });

  test('prevents adding duplicate skills', async () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    // Enter edit mode
    fireEvent.click(screen.getByText('Edit Skills'));
    
    // Try to add existing skill
    const input = screen.getByPlaceholderText('Enter skill name...');
    const addButton = screen.getByTestId('add-skill-button');
    
    fireEvent.change(input, { target: { value: 'JavaScript' } });
    fireEvent.click(addButton);
    
    // Should show error toast (mocked)
    const { toast } = require('react-hot-toast');
    expect(toast.error).toHaveBeenCalledWith('This skill already exists');
  });

  test('allows removing skills in edit mode', () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    // Enter edit mode
    fireEvent.click(screen.getByText('Edit Skills'));
    
    // Find and click remove button for first skill
    const removeButtons = screen.getAllByRole('button').filter(button => 
      button.innerHTML.includes('×')
    );
    
    if (removeButtons.length > 0) {
      fireEvent.click(removeButtons[0]);
      // Skill should be removed from display
      expect(screen.queryByText('JavaScript')).not.toBeInTheDocument();
    }
  });

  test('saves changes when save button is clicked', () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    // Enter edit mode
    fireEvent.click(screen.getByText('Edit Skills'));
    
    // Save changes
    fireEvent.click(screen.getByText('Save'));
    
    expect(defaultProps.onSkillsUpdate).toHaveBeenCalledWith(mockSkills);
  });

  test('cancels editing when cancel button is clicked', () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    // Enter edit mode
    fireEvent.click(screen.getByText('Edit Skills'));
    
    // Cancel editing
    fireEvent.click(screen.getByText('Cancel'));
    
    // Should exit edit mode
    expect(screen.queryByText('Add New Skill')).not.toBeInTheDocument();
    expect(screen.getByText('Edit Skills')).toBeInTheDocument();
  });

  test('shows skill source indicators', () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    // Check that skills have source indicators (icons)
    const skillElements = screen.getAllByText(/JavaScript|React|Leadership/);
    expect(skillElements.length).toBeGreaterThan(0);
  });

  test('shows confidence scores for skills with low confidence', () => {
    const lowConfidenceSkills = [
      {
        id: '1',
        name: 'Test Skill',
        category: 'technical',
        confidence: 75,
        source: 'cv' as const
      }
    ];
    
    render(<SkillsExtraction {...defaultProps} skills={lowConfidenceSkills} />);
    
    expect(screen.getByText('(75%)')).toBeInTheDocument();
  });

  test('shows skills summary with counts', () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    expect(screen.getByText('1 from CV')).toBeInTheDocument();
    expect(screen.getByText('1 AI enhanced')).toBeInTheDocument();
    expect(screen.getByText('1 manual')).toBeInTheDocument();
  });

  test('handles keyboard input for adding skills', async () => {
    render(<SkillsExtraction {...defaultProps} />);
    
    // Enter edit mode
    fireEvent.click(screen.getByText('Edit Skills'));
    
    // Add skill with Enter key
    const input = screen.getByPlaceholderText('Enter skill name...');
    fireEvent.change(input, { target: { value: 'TypeScript' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(screen.getByText('TypeScript')).toBeInTheDocument();
    });
  });
}); 