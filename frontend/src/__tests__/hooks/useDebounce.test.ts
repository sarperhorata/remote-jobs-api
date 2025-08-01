import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '../../hooks/useDebounce';

describe('useDebounce Hook', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should return the initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 500));
    expect(result.current).toBe('initial');
  });

  it('should debounce value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    // Change value
    rerender({ value: 'changed', delay: 500 });
    expect(result.current).toBe('initial'); // Should still be initial

    // Fast forward time
    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('changed'); // Should now be changed
  });

  it('should use default delay of 500ms', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value),
      { initialProps: { value: 'initial' } }
    );

    rerender({ value: 'changed' });
    expect(result.current).toBe('initial');

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('changed');
  });

  it('should cancel previous timeout on new value', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 1000 } }
    );

    // Change value multiple times quickly
    rerender({ value: 'first', delay: 1000 });
    rerender({ value: 'second', delay: 1000 });
    rerender({ value: 'third', delay: 1000 });

    expect(result.current).toBe('initial');

    // Advance time less than delay
    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('initial');

    // Advance to full delay
    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('third'); // Should be the last value
  });

  it('should handle different delay values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 200 } }
    );

    rerender({ value: 'changed', delay: 200 });
    expect(result.current).toBe('initial');

    act(() => {
      jest.advanceTimersByTime(200);
    });

    expect(result.current).toBe('changed');
  });

  it('should handle zero delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 0 } }
    );

    rerender({ value: 'changed', delay: 0 });
    
    act(() => {
      jest.advanceTimersByTime(0);
    });
    
    expect(result.current).toBe('changed'); // Should update immediately
  });

  it('should handle negative delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: -100 } }
    );

    rerender({ value: 'changed', delay: -100 });
    
    act(() => {
      jest.advanceTimersByTime(0);
    });
    
    expect(result.current).toBe('changed'); // Should update immediately
  });

  it('should handle undefined and null values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    rerender({ value: undefined, delay: 500 });
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBeUndefined();

    rerender({ value: null, delay: 500 });
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBeNull();
  });

  it('should handle number values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 0, delay: 500 } }
    );

    rerender({ value: 42, delay: 500 });
    expect(result.current).toBe(0);

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe(42);
  });

  it('should handle boolean values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: false, delay: 500 } }
    );

    rerender({ value: true, delay: 500 });
    expect(result.current).toBe(false);

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe(true);
  });

  it('should handle object values', () => {
    const initialObj = { name: 'initial' };
    const changedObj = { name: 'changed' };

    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initialObj, delay: 500 } }
    );

    rerender({ value: changedObj, delay: 500 });
    expect(result.current).toBe(initialObj);

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe(changedObj);
  });

  it('should handle array values', () => {
    const initialArray = [1, 2, 3];
    const changedArray = [4, 5, 6];

    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initialArray, delay: 500 } }
    );

    rerender({ value: changedArray, delay: 500 });
    expect(result.current).toBe(initialArray);

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe(changedArray);
  });
});