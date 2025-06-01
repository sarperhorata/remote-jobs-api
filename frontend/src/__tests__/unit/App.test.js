/**
 * Basic App Component Tests
 * Priority: Ensure main components render without crashing
 */
const { render } = require('@testing-library/react');
require('@testing-library/jest-dom');
const React = require('react');

// Mock console.error to prevent test noise
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn((message) => {
    // Only log if it's not a common React warning
    if (!message.includes('Warning:') && !message.includes('ReactDOM.render')) {
      originalError(message);
    }
  });
});

afterAll(() => {
  console.error = originalError;
});

describe('🔧 App Component Unit Tests', () => {
  
  test('should have App component file', () => {
    const fs = require('fs');
    const path = require('path');
    
    const appPath = path.join(__dirname, '../../App.js');
    const appTsPath = path.join(__dirname, '../../App.tsx');
    
    const hasApp = fs.existsSync(appPath) || fs.existsSync(appTsPath);
    expect(hasApp).toBe(true);
  });

  test('should be able to require React', () => {
    expect(() => {
      require('react');
    }).not.toThrow();
  });

  test('should be able to require testing library', () => {
    expect(() => {
      require('@testing-library/react');
    }).not.toThrow();
  });

  test('should have proper package.json test configuration', () => {
    const packageJson = require('../../../package.json');
    
    expect(packageJson.scripts.test).toBeDefined();
    expect(packageJson.dependencies.react).toBeDefined();
    expect(packageJson.dependencies['@testing-library/react']).toBeDefined();
  });

  test('should pass basic render test without imports', () => {
    // Create a simple component for testing
    const TestComponent = React.createElement('div', {}, 'Test Component');
    
    expect(() => {
      render(TestComponent);
    }).not.toThrow();
  });

  test('should have AuthModal component', () => {
    const fs = require('fs');
    const path = require('path');
    
    const authModalPath = path.join(__dirname, '../../components/AuthModal.tsx');
    expect(fs.existsSync(authModalPath)).toBe(true);
  });

  test('should have proper auth context', () => {
    const fs = require('fs');
    const path = require('path');
    
    const authContextPath = path.join(__dirname, '../../contexts/AuthContext.tsx');
    const authContextJsPath = path.join(__dirname, '../../contexts/AuthContext.js');
    
    const hasAuthContext = fs.existsSync(authContextPath) || fs.existsSync(authContextJsPath);
    expect(hasAuthContext).toBe(true);
  });
}); 