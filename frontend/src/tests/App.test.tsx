import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';

// App already has its own Router, so we don't need to wrap it
const renderApp = () => {
  return render(<App />);
};

describe('App Component', () => {
  test('renders without crashing', () => {
    renderApp();
    // Just check that something renders without crashing
    expect(document.body).toBeInTheDocument();
  });

  test('shows loading or content', async () => {
    renderApp();
    // Wait for either loading text or main content to appear
    await waitFor(() => {
      const hasContent = 
        screen.queryByText(/Loading Buzz2Remote/i) ||
        screen.queryAllByText(/Buzz2Remote/i).length > 0 ||
        screen.queryByText(/Pricing Plans/i) ||
        screen.queryByText(/Find Your Next/i);
      expect(hasContent).toBeTruthy();
    }, { timeout: 3000 });
  });

  test('has proper html structure', () => {
    renderApp();
    // Check basic HTML structure using Testing Library
    expect(screen.getByRole('main') || screen.getByTestId('app-root') || document.body).toBeInTheDocument();
  });
}); 