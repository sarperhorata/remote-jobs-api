// Mock localStorage with persistent data storage
const storage: { [key: string]: string } = {};

const mockStorage = {
  getItem: jest.fn((key: string) => storage[key] || null),
  setItem: jest.fn((key: string, value: string) => {
    storage[key] = value;
  }),
  removeItem: jest.fn((key: string) => {
    delete storage[key];
  }),
  clear: jest.fn(() => {
    Object.keys(storage).forEach(key => delete storage[key]);
  }),
  length: 0,
  key: jest.fn()
};

Object.defineProperty(window, 'localStorage', {
  value: mockStorage,
  writable: true
});

describe('Cache Service Tests', () => {
  // Test implementation
});

export {}; 