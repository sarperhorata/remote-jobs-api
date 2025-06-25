import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { AdvancedJobFilter } from "../../components/AdvancedJobFilter";

describe("AdvancedJobFilter", () => {
  const mockOnFiltersChange = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders filter component", () => {
    render(
      <AdvancedJobFilter
        onFiltersChange={mockOnFiltersChange}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText("Advanced Filters")).toBeInTheDocument();
    expect(screen.getByText("Location")).toBeInTheDocument();
    expect(screen.getByText("Remote Type")).toBeInTheDocument();
  });

  test("handles filter changes", () => {
    render(
      <AdvancedJobFilter
        onFiltersChange={mockOnFiltersChange}
        onClose={mockOnClose}
      />
    );

    const locationInput = screen.getByPlaceholderText("e.g., San Francisco");
    fireEvent.change(locationInput, { target: { value: "New York" } });

    expect(locationInput).toHaveValue("New York");
  });

  test("calls onClose when cancel button is clicked", () => {
    render(
      <AdvancedJobFilter
        onFiltersChange={mockOnFiltersChange}
        onClose={mockOnClose}
      />
    );

    const cancelButton = screen.getByText("Cancel");
    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test("calls onFiltersChange when apply filters button is clicked", () => {
    render(
      <AdvancedJobFilter
        onFiltersChange={mockOnFiltersChange}
        onClose={mockOnClose}
      />
    );

    const applyButton = screen.getByText("Apply Filters");
    fireEvent.click(applyButton);

    expect(mockOnFiltersChange).toHaveBeenCalledTimes(1);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test("updates remote type filter", () => {
    render(
      <AdvancedJobFilter
        onFiltersChange={mockOnFiltersChange}
        onClose={mockOnClose}
      />
    );

    const remoteTypeSelect = screen.getByDisplayValue("Any");
    fireEvent.change(remoteTypeSelect, { target: { value: "remote" } });

    expect(remoteTypeSelect).toHaveValue("remote");
  });
});
