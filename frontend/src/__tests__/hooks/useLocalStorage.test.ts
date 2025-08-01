import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from '../../hooks/useLocalStorage';

describe('useLocalStorage Hook', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should initialize with default value when key does not exist', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    
    expect(result.current[0]).toBe('default-value');
  });

  it('should initialize with stored value when key exists', () => {
    localStorage.setItem('test-key', JSON.stringify('stored-value'));
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    
    expect(result.current[0]).toBe('stored-value');
  });

  it('should update localStorage when value changes', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial-value'));
    
    act(() => {
      result.current[1]('new-value');
    });
    
    expect(result.current[0]).toBe('new-value');
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify('new-value'));
  });

  it('should handle object values', () => {
    const initialValue = { name: 'John', age: 30 };
    const newValue = { name: 'Jane', age: 25 };
    
    const { result } = renderHook(() => useLocalStorage('test-key', initialValue));
    
    expect(result.current[0]).toEqual(initialValue);
    
    act(() => {
      result.current[1](newValue);
    });
    
    expect(result.current[0]).toEqual(newValue);
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify(newValue));
  });

  it('should handle array values', () => {
    const initialValue = [1, 2, 3];
    const newValue = [4, 5, 6];
    
    const { result } = renderHook(() => useLocalStorage('test-key', initialValue));
    
    expect(result.current[0]).toEqual(initialValue);
    
    act(() => {
      result.current[1](newValue);
    });
    
    expect(result.current[0]).toEqual(newValue);
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify(newValue));
  });

  it('should handle null values', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', null));
    
    expect(result.current[0]).toBeNull();
    
    act(() => {
      result.current[1]('not-null');
    });
    
    expect(result.current[0]).toBe('not-null');
    
    act(() => {
      result.current[1](null);
    });
    
    expect(result.current[0]).toBeNull();
  });

  it('should handle undefined values', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', undefined));
    
    expect(result.current[0]).toBeUndefined();
    
    act(() => {
      result.current[1]('defined');
    });
    
    expect(result.current[0]).toBe('defined');
    
    act(() => {
      result.current[1](undefined);
    });
    
    expect(result.current[0]).toBeUndefined();
  });

  it('should handle boolean values', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', false));
    
    expect(result.current[0]).toBe(false);
    
    act(() => {
      result.current[1](true);
    });
    
    expect(result.current[0]).toBe(true);
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify(true));
  });

  it('should handle number values', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 0));
    
    expect(result.current[0]).toBe(0);
    
    act(() => {
      result.current[1](42);
    });
    
    expect(result.current[0]).toBe(42);
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify(42));
  });

  it('should handle function updates', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 0));
    
    act(() => {
      result.current[1]((prev: number) => prev + 1);
    });
    
    expect(result.current[0]).toBe(1);
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify(1));
  });

  it('should handle complex function updates', () => {
    const initialValue = { count: 0, name: 'test' };
    const { result } = renderHook(() => useLocalStorage('test-key', initialValue));
    
    act(() => {
      result.current[1]((prev: any) => ({ ...prev, count: prev.count + 1 }));
    });
    
    expect(result.current[0]).toEqual({ count: 1, name: 'test' });
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify({ count: 1, name: 'test' }));
  });

  it('should handle invalid JSON in localStorage', () => {
    localStorage.setItem('test-key', 'invalid-json');
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    
    expect(result.current[0]).toBe('default-value');
  });

  it('should handle empty string in localStorage', () => {
    localStorage.setItem('test-key', '');
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    
    expect(result.current[0]).toBe('default-value');
  });

  it('should handle multiple hooks with different keys', () => {
    const { result: result1 } = renderHook(() => useLocalStorage('key1', 'value1'));
    const { result: result2 } = renderHook(() => useLocalStorage('key2', 'value2'));
    
    expect(result1.current[0]).toBe('value1');
    expect(result2.current[0]).toBe('value2');
    
    act(() => {
      result1.current[1]('new-value1');
      result2.current[1]('new-value2');
    });
    
    expect(result1.current[0]).toBe('new-value1');
    expect(result2.current[0]).toBe('new-value2');
    expect(localStorage.getItem('key1')).toBe(JSON.stringify('new-value1'));
    expect(localStorage.getItem('key2')).toBe(JSON.stringify('new-value2'));
  });

  it('should handle localStorage errors gracefully', () => {
    // Mock localStorage to throw an error
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = jest.fn().mockImplementation(() => {
      throw new Error('Storage quota exceeded');
    });
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    
    act(() => {
      result.current[1]('new-value');
    });
    
    // Should not throw error, but value might not be updated
    expect(result.current[0]).toBe('new-value');
    
    // Restore original function
    localStorage.setItem = originalSetItem;
  });

  it('should handle localStorage getItem errors', () => {
    // Mock localStorage.getItem to throw an error
    const originalGetItem = localStorage.getItem;
    localStorage.getItem = jest.fn().mockImplementation(() => {
      throw new Error('Storage error');
    });
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    
    // Should fall back to default value
    expect(result.current[0]).toBe('default-value');
    
    // Restore original function
    localStorage.getItem = originalGetItem;
  });

  it('should handle removeItem', () => {
    localStorage.setItem('test-key', JSON.stringify('stored-value'));
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    
    expect(result.current[0]).toBe('stored-value');
    
    act(() => {
      result.current[1]('default-value');
    });
    
    expect(result.current[0]).toBe('default-value');
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify('default-value'));
  });
});