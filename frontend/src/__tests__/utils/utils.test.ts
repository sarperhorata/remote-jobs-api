// Test file for utility functions
import { cn } from '../../utils/cn';

describe('Utility Functions', () => {
  describe('cn (className utility)', () => {
    it('should combine class names correctly', () => {
      expect(cn('class1', 'class2')).toBe('class1 class2');
      expect(cn('class1', null, 'class2')).toBe('class1 class2');
      expect(cn('class1', undefined, 'class2')).toBe('class1 class2');
      expect(cn('class1', false, 'class2')).toBe('class1 class2');
      expect(cn('class1', true && 'class2')).toBe('class1 class2');
    });

    it('should handle conditional classes', () => {
      const isActive = true;
      const isDisabled = false;
      
      expect(cn('base-class', isActive && 'active', isDisabled && 'disabled'))
        .toBe('base-class active');
    });

    it('should handle arrays and objects', () => {
      expect(cn(['class1', 'class2'])).toBe('class1 class2');
      expect(cn({ 'class1': true, 'class2': false, 'class3': true }))
        .toBe('class1 class3');
    });

    it('should handle mixed inputs', () => {
      expect(cn('base', ['class1', 'class2'], { 'class3': true, 'class4': false }))
        .toBe('base class1 class2 class3');
    });
  });

  describe('formatCurrency', () => {
    const formatCurrency = (amount: number, currency = 'USD'): string => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency
      }).format(amount);
    };

    it('should format USD currency correctly', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00');
      expect(formatCurrency(1000.50)).toBe('$1,000.50');
    });

    it('should handle zero and negative amounts', () => {
      expect(formatCurrency(0)).toBe('$0.00');
      expect(formatCurrency(-500)).toBe('-$500.00');
    });
  });

  describe('validateEmail', () => {
    const validateEmail = (email: string): boolean => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    };

    it('should validate correct email formats', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.co.uk')).toBe(true);
    });

    it('should reject invalid email formats', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
      expect(validateEmail('')).toBe(false);
    });
  });

  describe('localStorage utilities', () => {
    const setLocalStorage = (key: string, value: any): void => {
      localStorage.setItem(key, JSON.stringify(value));
    };

    const getLocalStorage = (key: string): any => {
      const item = localStorage.getItem(key);
      if (!item) return null;
      try {
        return JSON.parse(item);
      } catch {
        return item;
      }
    };

    beforeEach(() => {
      localStorage.clear();
    });

    it('should store and retrieve simple values', () => {
      setLocalStorage('test', 'value');
      expect(getLocalStorage('test')).toBe('value');

      setLocalStorage('number', 42);
      expect(getLocalStorage('number')).toBe(42);
    });

    it('should handle non-existent keys', () => {
      expect(getLocalStorage('nonexistent')).toBeNull();
    });
  });
}); 