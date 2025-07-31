import { cn } from '../../utils/cn';

describe('cn utility function', () => {
  it('should combine class names correctly', () => {
    const result = cn('class1', 'class2', 'class3');
    expect(result).toBe('class1 class2 class3');
  });

  it('should handle conditional classes', () => {
    const result = cn('base-class', true && 'conditional-class', false && 'hidden-class');
    expect(result).toBe('base-class conditional-class');
  });

  it('should handle object syntax', () => {
    const result = cn('base-class', {
      'active-class': true,
      'inactive-class': false,
      'conditional-class': true
    });
    expect(result).toBe('base-class active-class conditional-class');
  });

  it('should handle mixed syntax', () => {
    const result = cn(
      'base-class',
      'static-class',
      true && 'conditional-class',
      {
        'object-class': true,
        'hidden-class': false
      }
    );
    expect(result).toBe('base-class static-class conditional-class object-class');
  });

  it('should handle empty strings and null values', () => {
    const result = cn('base-class', '', null, undefined, 'valid-class');
    expect(result).toBe('base-class valid-class');
  });

  it('should handle arrays', () => {
    const result = cn('base-class', ['array-class1', 'array-class2']);
    expect(result).toBe('base-class array-class1 array-class2');
  });

  it('should handle nested arrays', () => {
    const result = cn('base-class', [['nested1', 'nested2'], 'flat-class']);
    expect(result).toBe('base-class nested1 nested2 flat-class');
  });

  it('should handle complex combinations', () => {
    const isActive = true;
    const isDisabled = false;
    const theme = 'dark';
    
    const result = cn(
      'base-button',
      'px-4 py-2 rounded',
      isActive && 'bg-blue-500 text-white',
      isDisabled && 'opacity-50 cursor-not-allowed',
      {
        'bg-gray-800': theme === 'dark',
        'bg-white': theme === 'light',
        'border-2': true,
        'border-transparent': !isActive
      }
    );
    
    expect(result).toBe('base-button px-4 py-2 rounded text-white bg-gray-800 border-2');
  });

  it('should handle Tailwind CSS classes', () => {
    const result = cn(
      'flex items-center justify-center',
      'bg-white dark:bg-gray-800',
      'text-gray-900 dark:text-white',
      'hover:bg-gray-100 dark:hover:bg-gray-700'
    );
    
    expect(result).toBe('flex items-center justify-center bg-white dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700');
  });

  it('should handle dynamic class names', () => {
    const size = 'lg';
    const variant = 'primary';
    
    const result = cn(
      'button',
      {
        'text-sm': size === 'sm',
        'text-base': size === 'md',
        'text-lg': size === 'lg',
        'text-xl': size === 'xl'
      },
      {
        'bg-blue-500': variant === 'primary',
        'bg-green-500': variant === 'success',
        'bg-red-500': variant === 'danger'
      }
    );
    
    expect(result).toBe('button text-lg bg-blue-500');
  });

  it('should handle empty input', () => {
    expect(cn()).toBe('');
    expect(cn('')).toBe('');
    expect(cn(null)).toBe('');
    expect(cn(undefined)).toBe('');
  });

  it('should handle single class', () => {
    expect(cn('single-class')).toBe('single-class');
  });

  it('should handle whitespace in class names', () => {
    const result = cn('  class1  ', '  class2  ', 'class3');
    expect(result).toBe('class1 class2 class3');
  });

  it('should handle duplicate classes', () => {
    const result = cn('class1', 'class2', 'class1', 'class3');
    expect(result).toBe('class1 class2 class1 class3');
  });

  it('should handle function calls that return classes', () => {
    const getClasses = () => 'dynamic-class1 dynamic-class2';
    const result = cn('base-class', getClasses());
    expect(result).toBe('base-class dynamic-class1 dynamic-class2');
  });

  it('should handle template literals', () => {
    const prefix = 'btn';
    const size = 'lg';
    const result = cn(`${prefix} ${prefix}-${size}`, 'additional-class');
    expect(result).toBe('btn btn-lg additional-class');
  });
});