import React from 'react';
import { render, RenderOptions, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { AuthProvider } from '../../contexts/AuthContext';
import { setupMockFetch } from '../mocks/apiMocks';

// Custom render function that includes providers
const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          {children}
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

// Helper function to render with specific providers
const renderWithProviders = (
  ui: React.ReactElement,
  {
    route = '/',
    ...renderOptions
  }: {
    route?: string;
  } & Omit<RenderOptions, 'wrapper'> = {}
) => {
  window.history.pushState({}, 'Test page', route);
  return customRender(ui, renderOptions);
};

// Helper function to wait for loading states
const waitForLoadingToFinish = async () => {
  await waitFor(() => {
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  });
};

// Helper function to setup API mocks
const setupApiMocks = (response: any, status: number = 200) => {
  setupMockFetch(response, status);
};

// Re-export everything
export * from '@testing-library/react';
export { userEvent };

// Override render method
export { customRender as render, renderWithProviders, waitForLoadingToFinish, setupApiMocks };

// Test to ensure the file is recognized as a test suite
describe('Test Utils', () => {
  test('should export render function', () => {
    expect(typeof customRender).toBe('function');
  });
}); 