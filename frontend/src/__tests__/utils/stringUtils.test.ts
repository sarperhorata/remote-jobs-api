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
  removeSpecialCharacters,
  normalizeString,
  extractDomain,
  formatFileSize,
  formatDuration,
  pluralize
} from '../../utils/stringUtils';

describe('stringUtils', () => {
  describe('capitalize', () => {
    it('capitalizes first letter of string', () => {
      expect(capitalize('hello')).toBe('Hello');
      expect(capitalize('world')).toBe('World');
    });

    it('handles empty string', () => {
      expect(capitalize('')).toBe('');
    });

    it('handles single character', () => {
      expect(capitalize('a')).toBe('A');
    });

    it('handles already capitalized string', () => {
      expect(capitalize('Hello')).toBe('Hello');
    });
  });

  describe('truncate', () => {
    it('truncates string to specified length', () => {
      expect(truncate('Hello world', 5)).toBe('Hello...');
      expect(truncate('This is a long string', 10)).toBe('This is a...');
    });

    it('returns original string if shorter than limit', () => {
      expect(truncate('Hello', 10)).toBe('Hello');
    });

    it('handles empty string', () => {
      expect(truncate('', 5)).toBe('');
    });

    it('uses custom suffix', () => {
      expect(truncate('Hello world', 5, '***')).toBe('Hello***');
    });
  });

  describe('slugify', () => {
    it('converts string to URL-friendly slug', () => {
      expect(slugify('Hello World')).toBe('hello-world');
      expect(slugify('This is a Test!')).toBe('this-is-a-test');
    });

    it('handles special characters', () => {
      expect(slugify('Hello & World')).toBe('hello-world');
      expect(slugify('Test@123')).toBe('test123');
    });

    it('handles multiple spaces', () => {
      expect(slugify('Hello   World')).toBe('hello-world');
    });

    it('handles empty string', () => {
      expect(slugify('')).toBe('');
    });
  });

  describe('formatNumber', () => {
    it('formats numbers with commas', () => {
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(1234567)).toBe('1,234,567');
    });

    it('handles decimals', () => {
      expect(formatNumber(1000.5)).toBe('1,000.5');
      expect(formatNumber(1234.567)).toBe('1,234.567');
    });

    it('handles zero', () => {
      expect(formatNumber(0)).toBe('0');
    });

    it('handles negative numbers', () => {
      expect(formatNumber(-1000)).toBe('-1,000');
    });
  });

  describe('formatCurrency', () => {
    it('formats currency with default USD', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00');
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
    });

    it('formats currency with custom currency', () => {
      expect(formatCurrency(1000, 'EUR')).toBe('€1,000.00');
      expect(formatCurrency(1000, 'GBP')).toBe('£1,000.00');
    });

    it('handles zero', () => {
      expect(formatCurrency(0)).toBe('$0.00');
    });

    it('handles negative amounts', () => {
      expect(formatCurrency(-1000)).toBe('-$1,000.00');
    });
  });

  describe('formatPhoneNumber', () => {
    it('formats US phone numbers', () => {
      expect(formatPhoneNumber('1234567890')).toBe('(123) 456-7890');
      expect(formatPhoneNumber('5551234567')).toBe('(555) 123-4567');
    });

    it('handles already formatted numbers', () => {
      expect(formatPhoneNumber('(123) 456-7890')).toBe('(123) 456-7890');
    });

    it('handles numbers with country code', () => {
      expect(formatPhoneNumber('+11234567890')).toBe('(123) 456-7890');
    });

    it('returns original if not valid US number', () => {
      expect(formatPhoneNumber('123')).toBe('123');
      expect(formatPhoneNumber('abcdefghij')).toBe('abcdefghij');
    });
  });

  describe('validateEmail', () => {
    it('validates correct email formats', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.co.uk')).toBe(true);
      expect(validateEmail('test+tag@example.com')).toBe(true);
    });

    it('rejects invalid email formats', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
      expect(validateEmail('test@.com')).toBe(false);
    });

    it('handles empty string', () => {
      expect(validateEmail('')).toBe(false);
    });
  });

  describe('validatePassword', () => {
    it('validates strong passwords', () => {
      expect(validatePassword('Password123!')).toBe(true);
      expect(validatePassword('MySecurePass1')).toBe(true);
    });

    it('rejects weak passwords', () => {
      expect(validatePassword('123')).toBe(false); // too short
      expect(validatePassword('password')).toBe(false); // no uppercase
      expect(validatePassword('PASSWORD')).toBe(false); // no lowercase
      expect(validatePassword('Password')).toBe(false); // no number
    });

    it('handles empty string', () => {
      expect(validatePassword('')).toBe(false);
    });
  });

  describe('generateRandomString', () => {
    it('generates string of specified length', () => {
      const result = generateRandomString(10);
      expect(result).toHaveLength(10);
      expect(typeof result).toBe('string');
    });

    it('generates different strings on each call', () => {
      const result1 = generateRandomString(10);
      const result2 = generateRandomString(10);
      expect(result1).not.toBe(result2);
    });

    it('handles zero length', () => {
      expect(generateRandomString(0)).toBe('');
    });
  });

  describe('removeSpecialCharacters', () => {
    it('removes special characters from string', () => {
      expect(removeSpecialCharacters('Hello@World!')).toBe('HelloWorld');
      expect(removeSpecialCharacters('Test#123$')).toBe('Test123');
    });

    it('keeps letters and numbers', () => {
      expect(removeSpecialCharacters('Hello123World')).toBe('Hello123World');
    });

    it('handles empty string', () => {
      expect(removeSpecialCharacters('')).toBe('');
    });

    it('handles string with only special characters', () => {
      expect(removeSpecialCharacters('!@#$%^&*()')).toBe('');
    });
  });

  describe('normalizeString', () => {
    it('normalizes string for comparison', () => {
      expect(normalizeString('  Hello  World  ')).toBe('hello world');
      expect(normalizeString('Test@123!')).toBe('test123');
    });

    it('removes extra whitespace', () => {
      expect(normalizeString('  multiple   spaces  ')).toBe('multiple spaces');
    });

    it('converts to lowercase', () => {
      expect(normalizeString('HELLO WORLD')).toBe('hello world');
    });

    it('handles empty string', () => {
      expect(normalizeString('')).toBe('');
    });
  });

  describe('extractDomain', () => {
    it('extracts domain from URL', () => {
      expect(extractDomain('https://www.example.com/path')).toBe('example.com');
      expect(extractDomain('http://subdomain.example.co.uk')).toBe('example.co.uk');
    });

    it('handles URLs without protocol', () => {
      expect(extractDomain('www.example.com')).toBe('example.com');
      expect(extractDomain('example.com')).toBe('example.com');
    });

    it('handles invalid URLs', () => {
      expect(extractDomain('not-a-url')).toBe('');
      expect(extractDomain('')).toBe('');
    });
  });

  describe('formatFileSize', () => {
    it('formats bytes to human readable size', () => {
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1048576)).toBe('1 MB');
      expect(formatFileSize(1073741824)).toBe('1 GB');
    });

    it('handles bytes less than 1 KB', () => {
      expect(formatFileSize(500)).toBe('500 B');
      expect(formatFileSize(0)).toBe('0 B');
    });

    it('handles decimal sizes', () => {
      expect(formatFileSize(1536)).toBe('1.5 KB');
      expect(formatFileSize(1572864)).toBe('1.5 MB');
    });

    it('handles very large sizes', () => {
      expect(formatFileSize(1099511627776)).toBe('1 TB');
    });
  });

  describe('formatDuration', () => {
    it('formats seconds to human readable duration', () => {
      expect(formatDuration(30)).toBe('30 seconds');
      expect(formatDuration(90)).toBe('1 minute 30 seconds');
      expect(formatDuration(3661)).toBe('1 hour 1 minute 1 second');
    });

    it('handles zero duration', () => {
      expect(formatDuration(0)).toBe('0 seconds');
    });

    it('handles very long durations', () => {
      expect(formatDuration(90061)).toBe('1 day 1 hour 1 minute 1 second');
    });

    it('handles singular forms', () => {
      expect(formatDuration(1)).toBe('1 second');
      expect(formatDuration(60)).toBe('1 minute');
      expect(formatDuration(3600)).toBe('1 hour');
    });
  });

  describe('pluralize', () => {
    it('pluralizes words correctly', () => {
      expect(pluralize('cat', 1)).toBe('cat');
      expect(pluralize('cat', 2)).toBe('cats');
      expect(pluralize('cat', 0)).toBe('cats');
    });

    it('handles custom plural forms', () => {
      expect(pluralize('person', 1, 'people')).toBe('person');
      expect(pluralize('person', 2, 'people')).toBe('people');
    });

    it('handles irregular plurals', () => {
      expect(pluralize('child', 1, 'children')).toBe('child');
      expect(pluralize('child', 2, 'children')).toBe('children');
    });

    it('handles empty string', () => {
      expect(pluralize('', 1)).toBe('');
      expect(pluralize('', 2)).toBe('');
    });
  });
});