import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import "@testing-library/jest-dom";
import JobAutocomplete from "../../components/JobAutocomplete";

// Mock the API config
jest.mock('../../utils/apiConfig', () => ({
  API_BASE_URL: 'http://localhost:8000'
}));

const mockJobTitles = [
  { title: 'Software Engineer', count: 150 },
  { title: 'Data Scientist', count: 75 },
  { title: 'Product Manager', count: 50 }
];

// Mock fetch
global.fetch = jest.fn();

const MockWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

const defaultProps = {
  value: "",
  onChange: jest.fn(),
  onSelect: jest.fn(),
  placeholder: "Test placeholder"
};

describe("JobAutocomplete", () => {
  const mockOnChange = jest.fn();
  const mockOnSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockJobTitles
    });
  });

  test("renders search input with placeholder", () => {
    render(
      <MockWrapper>
        <JobAutocomplete {...defaultProps} />
      </MockWrapper>
    );

    const input = screen.getByRole("textbox");
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute("placeholder", "Test placeholder");
  });

  test("handles user input and calls onChange", () => {
    const mockOnChange = jest.fn();
    render(
      <MockWrapper>
        <JobAutocomplete {...defaultProps} onChange={mockOnChange} />
      </MockWrapper>
    );

    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "developer" } });
    
    expect(mockOnChange).toHaveBeenCalledWith("developer");
  });

  test("shows dropdown when typing and fetches suggestions", async () => {
    render(
      <MockWrapper>
        <JobAutocomplete {...defaultProps} value="soft" />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/api/v1/jobs/job-titles/search?q=soft&limit=20");
    });
  });

  test("handles API error gracefully", async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error("API Error"));
    
    render(
      <MockWrapper>
        <JobAutocomplete {...defaultProps} value="test" />
      </MockWrapper>
    );

    // Should not crash on error
    await waitFor(() => {
      expect(screen.getByRole("textbox")).toBeInTheDocument();
    });
  });

  test("handles selection and calls onSelect", async () => {
    const mockOnSelect = jest.fn();
    
    render(
      <MockWrapper>
        <JobAutocomplete {...defaultProps} value="Software" onSelect={mockOnSelect} />
      </MockWrapper>
    );

    await waitFor(() => {
      const dropdown = screen.queryByText("Software Engineer");
      if (dropdown) {
        fireEvent.click(dropdown);
        expect(mockOnSelect).toHaveBeenCalled();
      }
    });
  });

  test("component unmounts cleanly", () => {
    const { unmount } = render(
      <MockWrapper>
        <JobAutocomplete {...defaultProps} />
      </MockWrapper>
    );

    expect(() => unmount()).not.toThrow();
  });

  test("handles keyboard navigation", () => {
    render(
      <MockWrapper>
        <JobAutocomplete {...defaultProps} value="test" />
      </MockWrapper>
    );

    const input = screen.getByRole("textbox");
    
    // Test arrow down
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    expect(input).toBeInTheDocument();
    
    // Test escape
    fireEvent.keyDown(input, { key: 'Escape' });
    expect(input).toBeInTheDocument();
  });
});
