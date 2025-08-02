import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '../../hooks/useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial-value', 500));

    expect(result.current).toBe('initial-value');
  });

  test('debounces value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    expect(result.current).toBe('initial');

    // Change value
    rerender({ value: 'changed', delay: 500 });
    expect(result.current).toBe('initial'); // Should still be initial

    // Fast forward time
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBe('changed'); // Should now be changed
  });

  test('handles multiple rapid changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    expect(result.current).toBe('initial');

    // Multiple rapid changes
    rerender({ value: 'change1', delay: 500 });
    jest.advanceTimersByTime(100);

    rerender({ value: 'change2', delay: 500 });
    jest.advanceTimersByTime(100);

    rerender({ value: 'change3', delay: 500 });
    jest.advanceTimersByTime(100);

    expect(result.current).toBe('initial'); // Should still be initial

    // Wait for debounce delay
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBe('change3'); // Should be the last value
  });

  test('handles zero delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 0 } }
    );

    expect(result.current).toBe('initial');

    rerender({ value: 'changed', delay: 0 });
    act(() => {
      jest.runAllTimers();
    });
    expect(result.current).toBe('changed'); // Should change immediately
  });

  test('handles negative delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: -100 } }
    );

    expect(result.current).toBe('initial');

    rerender({ value: 'changed', delay: -100 });
    act(() => {
      jest.runAllTimers();
    });
    expect(result.current).toBe('changed'); // Should change immediately
  });

  test('handles undefined value', () => {
    const { result } = renderHook(() => useDebounce(undefined, 500));

    expect(result.current).toBeUndefined();
  });

  test('handles null value', () => {
    const { result } = renderHook(() => useDebounce(null, 500));

    expect(result.current).toBeNull();
  });

  test('handles number values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 0, delay: 500 } }
    );

    expect(result.current).toBe(0);

    rerender({ value: 42, delay: 500 });
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBe(42);
  });

  test('handles boolean values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: false, delay: 500 } }
    );

    expect(result.current).toBe(false);

    rerender({ value: true, delay: 500 });
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toBe(true);
  });

  test('handles object values', () => {
    const initialObject = { name: 'John', age: 30 };
    const changedObject = { name: 'Jane', age: 25 };

    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initialObject, delay: 500 } }
    );

    expect(result.current).toEqual(initialObject);

    rerender({ value: changedObject, delay: 500 });
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toEqual(changedObject);
  });

  test('handles array values', () => {
    const initialArray = [1, 2, 3];
    const changedArray = [4, 5, 6];

    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initialArray, delay: 500 } }
    );

    expect(result.current).toEqual(initialArray);

    rerender({ value: changedArray, delay: 500 });
    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(result.current).toEqual(changedArray);
  });

  test('clears previous timeout on new value', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    expect(result.current).toBe('initial');

    // Change value and advance time partially
    rerender({ value: 'change1', delay: 500 });
    jest.advanceTimersByTime(200);

    // Change value again before first debounce completes
    rerender({ value: 'change2', delay: 500 });
    jest.advanceTimersByTime(200);

    expect(result.current).toBe('initial'); // Should still be initial

    // Complete the debounce delay
    act(() => {
      jest.advanceTimersByTime(300);
    });
    expect(result.current).toBe('change2'); // Should be the last value
  });

  test('handles very long delays', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 10000 } }
    );

    expect(result.current).toBe('initial');

    rerender({ value: 'changed', delay: 10000 });
    act(() => {
      jest.advanceTimersByTime(10000);
    });
    expect(result.current).toBe('changed');
  });

  test('handles very short delays', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 1 } }
    );

    expect(result.current).toBe('initial');

    rerender({ value: 'changed', delay: 1 });
    act(() => {
      jest.advanceTimersByTime(1);
    });
    expect(result.current).toBe('changed');
  });
});