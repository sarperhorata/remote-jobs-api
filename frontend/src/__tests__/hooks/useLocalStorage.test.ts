import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from '../../hooks/useLocalStorage';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('useLocalStorage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('initializes with default value when no stored value exists', () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));

    expect(result.current[0]).toBe('default-value');
    expect(localStorageMock.getItem).toHaveBeenCalledWith('test-key');
  });

  test('initializes with stored value when it exists', () => {
    const storedValue = JSON.stringify('stored-value');
    localStorageMock.getItem.mockReturnValue(storedValue);

    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));

    expect(result.current[0]).toBe('stored-value');
    expect(localStorageMock.getItem).toHaveBeenCalledWith('test-key');
  });

  test('updates value and localStorage when setValue is called', () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));

    act(() => {
      result.current[1]('new-value');
    });

    expect(result.current[0]).toBe('new-value');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('test-key', JSON.stringify('new-value'));
  });

  test('handles function updates', () => {
    localStorageMock.getItem.mockReturnValue(JSON.stringify('initial-value'));

    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));

    act(() => {
      result.current[1]((prevValue: string) => prevValue + '-updated');
    });

    expect(result.current[0]).toBe('initial-value-updated');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('test-key', JSON.stringify('initial-value-updated'));
  });

  test('handles complex objects', () => {
    const complexObject = { name: 'John', age: 30, hobbies: ['reading', 'gaming'] };
    localStorageMock.getItem.mockReturnValue(JSON.stringify(complexObject));

    const { result } = renderHook(() => useLocalStorage('user-data', {}));

    expect(result.current[0]).toEqual(complexObject);
  });

  test('handles arrays', () => {
    const arrayData = ['item1', 'item2', 'item3'];
    localStorageMock.getItem.mockReturnValue(JSON.stringify(arrayData));

    const { result } = renderHook(() => useLocalStorage('array-key', []));

    expect(result.current[0]).toEqual(arrayData);
  });

  test('handles invalid JSON in localStorage', () => {
    localStorageMock.getItem.mockReturnValue('invalid-json');

    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));

    expect(result.current[0]).toBe('default-value');
  });

  test('handles null values', () => {
    localStorageMock.getItem.mockReturnValue(JSON.stringify(null));

    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));

    expect(result.current[0]).toBe(null);
  });

  test('handles undefined values', () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));

    expect(result.current[0]).toBe('default-value');
  });

  test('handles boolean values', () => {
    localStorageMock.getItem.mockReturnValue(JSON.stringify(true));

    const { result } = renderHook(() => useLocalStorage('test-key', false));

    expect(result.current[0]).toBe(true);
  });

  test('handles number values', () => {
    localStorageMock.getItem.mockReturnValue(JSON.stringify(42));

    const { result } = renderHook(() => useLocalStorage('test-key', 0));

    expect(result.current[0]).toBe(42);
  });

  test('handles localStorage errors gracefully', () => {
    localStorageMock.setItem.mockImplementation(() => {
      throw new Error('localStorage quota exceeded');
    });

    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));

    // Should not throw error, just log it
    expect(() => {
      act(() => {
        result.current[1]('new-value');
      });
    }).not.toThrow();

    expect(result.current[0]).toBe('new-value');
  });

  test('handles getItem errors gracefully', () => {
    localStorageMock.getItem.mockImplementation(() => {
      throw new Error('localStorage not available');
    });

    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));

    expect(result.current[0]).toBe('default-value');
  });
});