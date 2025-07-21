// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock window.matchMedia for tests - More robust implementation
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Ensure matchMedia is available globally
if (typeof window !== 'undefined') {
  window.matchMedia = window.matchMedia || function() {
    return {
      matches: false,
      addListener: function() {},
      removeListener: function() {},
      addEventListener: function() {},
      removeEventListener: function() {},
      dispatchEvent: function() {},
    };
  };
}

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock window.scrollTo
Object.defineProperty(window, 'scrollTo', {
  value: jest.fn(),
  writable: true,
});

// Mock window.scroll
Object.defineProperty(window, 'scroll', {
  value: jest.fn(),
  writable: true,
});

// Mock window.scrollY
Object.defineProperty(window, 'scrollY', {
  value: 0,
  writable: true,
});

// Mock window.innerHeight
Object.defineProperty(window, 'innerHeight', {
  value: 768,
  writable: true,
});

// Mock window.innerWidth
Object.defineProperty(window, 'innerWidth', {
  value: 1024,
  writable: true,
});

// Mock window.getComputedStyle
Object.defineProperty(window, 'getComputedStyle', {
  value: () => ({
    getPropertyValue: () => '',
  }),
  writable: true,
});

// Mock console methods to reduce noise in tests
const originalError = console.error;
const originalWarn = console.warn;

console.error = (...args: any[]) => {
  // Filter out specific error messages that are expected in tests
  if (
    typeof args[0] === 'string' &&
    (args[0].includes('Warning: ReactDOM.render is no longer supported') ||
     args[0].includes('Warning: componentWillReceiveProps') ||
     args[0].includes('Warning: componentWillUpdate') ||
     args[0].includes('Warning: componentWillMount') ||
     args[0].includes('Warning: Failed prop type') ||
     args[0].includes('Warning: Each child in a list should have a unique "key" prop'))
  ) {
    return;
  }
  originalError.call(console, ...args);
};

console.warn = (...args: any[]) => {
  // Filter out specific warning messages that are expected in tests
  if (
    typeof args[0] === 'string' &&
    (args[0].includes('Warning: ReactDOM.render is no longer supported') ||
     args[0].includes('Warning: componentWillReceiveProps') ||
     args[0].includes('Warning: componentWillUpdate') ||
     args[0].includes('Warning: componentWillMount') ||
     args[0].includes('Warning: Failed prop type') ||
     args[0].includes('Warning: Each child in a list should have a unique "key" prop'))
  ) {
    return;
  }
  originalWarn.call(console, ...args);
};

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000',
    protocol: 'http:',
    host: 'localhost:3000',
    hostname: 'localhost',
    port: '3000',
    pathname: '/',
    search: '',
    hash: '',
    reload: jest.fn(),
    assign: jest.fn(),
    replace: jest.fn(),
  },
  writable: true,
});

// Mock window.history
Object.defineProperty(window, 'history', {
  value: {
    length: 1,
    scrollRestoration: 'auto',
    state: null,
    back: jest.fn(),
    forward: jest.fn(),
    go: jest.fn(),
    pushState: jest.fn(),
    replaceState: jest.fn(),
  },
  writable: true,
});

// Mock window.navigator
Object.defineProperty(window, 'navigator', {
  value: {
    userAgent: 'node.js',
    language: 'en-US',
    languages: ['en-US', 'en'],
    onLine: true,
    cookieEnabled: true,
    doNotTrack: null,
    geolocation: {},
  },
  writable: true,
});
