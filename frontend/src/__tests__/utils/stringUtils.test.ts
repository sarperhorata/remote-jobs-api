import { 
  capitalize, 
  truncate, 
  slugify, 
  formatNumber,
  formatCurrency,
  formatPhoneNumber,
  validateEmail,
  validatePassword,
  generateRandomString,
  removeSpecialCharacters
} from '../../utils/stringUtils';

describe('stringUtils', () => {
  describe('capitalize', () => {
    test('capitalizes first letter of string', () => {
      expect(capitalize('hello')).toBe('Hello');
      expect(capitalize('world')).toBe('World');
    });

    test('handles empty string', () => {
      expect(capitalize('')).toBe('');
    });

    test('handles single character', () => {
      expect(capitalize('a')).toBe('A');
    });

    test('handles already capitalized string', () => {
      expect(capitalize('Hello')).toBe('Hello');
    });

    test('handles string with numbers', () => {
      expect(capitalize('123hello')).toBe('123hello');
    });
  });

  describe('truncate', () => {
    test('truncates string to specified length', () => {
      expect(truncate('Hello world', 5)).toBe('Hello...');
      expect(truncate('This is a long string', 10)).toBe('This is a ...');
    });

    test('returns original string if shorter than limit', () => {
      expect(truncate('Hello', 10)).toBe('Hello');
    });

    test('handles empty string', () => {
      expect(truncate('', 5)).toBe('');
    });

    test('handles custom suffix', () => {
      expect(truncate('Hello world', 5, '***')).toBe('Hello***');
    });

    test('handles zero length', () => {
      expect(truncate('Hello world', 0)).toBe('...');
    });
  });

  describe('slugify', () => {
    test('converts string to slug', () => {
      expect(slugify('Hello World')).toBe('hello-world');
      expect(slugify('This is a Test String')).toBe('this-is-a-test-string');
    });

    test('handles special characters', () => {
      expect(slugify('Hello & World!')).toBe('hello-world');
      expect(slugify('Test@String#123')).toBe('teststring123');
    });

    test('handles multiple spaces', () => {
      expect(slugify('Hello   World')).toBe('hello-world');
    });

    test('handles empty string', () => {
      expect(slugify('')).toBe('');
    });

    test('handles numbers', () => {
      expect(slugify('Test 123 String')).toBe('test-123-string');
    });
  });

  describe('formatNumber', () => {
    test('formats large numbers with commas', () => {
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(1000000)).toBe('1,000,000');
      expect(formatNumber(1234567)).toBe('1,234,567');
    });

    test('handles small numbers', () => {
      expect(formatNumber(123)).toBe('123');
      expect(formatNumber(0)).toBe('0');
    });

    test('handles decimal numbers', () => {
      expect(formatNumber(1234.56)).toBe('1,234.56');
      expect(formatNumber(1000.1)).toBe('1,000.1');
    });

    test('handles negative numbers', () => {
      expect(formatNumber(-1000)).toBe('-1,000');
      expect(formatNumber(-1234567)).toBe('-1,234,567');
    });
  });

  describe('formatCurrency', () => {
    test('formats currency correctly', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00');
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
      expect(formatCurrency(0)).toBe('$0.00');
    });

    test('handles negative amounts', () => {
      expect(formatCurrency(-1000)).toBe('-$1,000.00');
    });

    test('handles custom currency', () => {
      expect(formatCurrency(1000, 'EUR')).toBe('€1,000.00');
      expect(formatCurrency(1000, 'GBP')).toBe('£1,000.00');
    });

    test('handles zero decimal places', () => {
      expect(formatCurrency(1000, 'USD', 0)).toBe('$1,000');
    });
  });

  describe('formatPhoneNumber', () => {
    test('formats US phone number', () => {
      expect(formatPhoneNumber('1234567890')).toBe('(123) 456-7890');
      expect(formatPhoneNumber('5551234567')).toBe('(555) 123-4567');
    });

    test('handles already formatted numbers', () => {
      expect(formatPhoneNumber('(123) 456-7890')).toBe('(123) 456-7890');
    });

    test('handles numbers with spaces', () => {
      expect(formatPhoneNumber('123 456 7890')).toBe('(123) 456-7890');
    });

    test('handles invalid phone numbers', () => {
      expect(formatPhoneNumber('123')).toBe('123');
      expect(formatPhoneNumber('')).toBe('');
    });
  });

  describe('validateEmail', () => {
    test('validates correct email addresses', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.co.uk')).toBe(true);
      expect(validateEmail('test+tag@example.org')).toBe(true);
    });

    test('rejects invalid email addresses', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
      expect(validateEmail('test@.com')).toBe(false);
      expect(validateEmail('')).toBe(false);
    });

    test('handles edge cases', () => {
      expect(validateEmail('test..test@example.com')).toBe(false);
      expect(validateEmail('test@example..com')).toBe(false);
    });
  });

  describe('validatePassword', () => {
    test('validates strong passwords', () => {
      expect(validatePassword('StrongPass123!')).toBe(true);
      expect(validatePassword('MySecureP@ssw0rd')).toBe(true);
    });

    test('rejects weak passwords', () => {
      expect(validatePassword('weak')).toBe(false);
      expect(validatePassword('12345678')).toBe(false);
      expect(validatePassword('password')).toBe(false);
      expect(validatePassword('')).toBe(false);
    });

    test('checks minimum length', () => {
      expect(validatePassword('Short1!')).toBe(false);
      expect(validatePassword('LongEnough1!')).toBe(true);
    });

    test('checks for required character types', () => {
      expect(validatePassword('nouppercase123!')).toBe(false);
      expect(validatePassword('NOLOWERCASE123!')).toBe(false);
      expect(validatePassword('NoNumbers!')).toBe(false);
      expect(validatePassword('NoSpecialChars123')).toBe(false);
    });
  });

  describe('generateRandomString', () => {
    test('generates string of specified length', () => {
      const result = generateRandomString(10);
      expect(result).toHaveLength(10);
      expect(typeof result).toBe('string');
    });

    test('generates different strings', () => {
      const string1 = generateRandomString(10);
      const string2 = generateRandomString(10);
      expect(string1).not.toBe(string2);
    });

    test('handles zero length', () => {
      expect(generateRandomString(0)).toBe('');
    });

    test('generates alphanumeric characters', () => {
      const result = generateRandomString(20);
      expect(result).toMatch(/^[a-zA-Z0-9]+$/);
    });
  });

  describe('removeSpecialCharacters', () => {
    test('removes special characters', () => {
      expect(removeSpecialCharacters('Hello!@#$%^&*()World')).toBe('HelloWorld');
      expect(removeSpecialCharacters('Test@String#123')).toBe('TestString123');
    });

    test('keeps letters and numbers', () => {
      expect(removeSpecialCharacters('Hello123World')).toBe('Hello123World');
    });

    test('handles empty string', () => {
      expect(removeSpecialCharacters('')).toBe('');
    });

    test('handles spaces', () => {
      expect(removeSpecialCharacters('Hello World')).toBe('Hello World');
    });

    test('handles unicode characters', () => {
      expect(removeSpecialCharacters('HelloñWorld')).toBe('HelloWorld');
    });
  });
});