import {
  capitalize,
  truncate,
  slugify,
  formatNumber,
  formatCurrency,
  formatDate,
  formatRelativeTime,
  generateId,
  validateEmail,
  validatePhone,
  extractDomain,
  maskEmail,
  maskPhone,
  countWords,
  countCharacters,
  removeHtmlTags,
  escapeHtml,
  unescapeHtml
} from '../../utils/stringUtils';

describe('String Utility Functions', () => {
  describe('capitalize', () => {
    it('should capitalize first letter of string', () => {
      expect(capitalize('hello')).toBe('Hello');
      expect(capitalize('world')).toBe('World');
      expect(capitalize('javascript')).toBe('Javascript');
    });

    it('should handle empty string', () => {
      expect(capitalize('')).toBe('');
    });

    it('should handle single character', () => {
      expect(capitalize('a')).toBe('A');
    });

    it('should handle already capitalized string', () => {
      expect(capitalize('Hello')).toBe('Hello');
    });

    it('should handle special characters', () => {
      expect(capitalize('123abc')).toBe('123abc');
      expect(capitalize('!hello')).toBe('!hello');
    });
  });

  describe('truncate', () => {
    it('should truncate string to specified length', () => {
      expect(truncate('Hello world', 5)).toBe('Hello...');
      expect(truncate('This is a long string', 10)).toBe('This is a...');
    });

    it('should not truncate if string is shorter than limit', () => {
      expect(truncate('Hello', 10)).toBe('Hello');
    });

    it('should handle custom suffix', () => {
      expect(truncate('Hello world', 5, '***')).toBe('Hello***');
    });

    it('should handle empty string', () => {
      expect(truncate('', 5)).toBe('');
    });

    it('should handle zero length', () => {
      expect(truncate('Hello world', 0)).toBe('...');
    });
  });

  describe('slugify', () => {
    it('should convert string to slug', () => {
      expect(slugify('Hello World')).toBe('hello-world');
      expect(slugify('This is a Test')).toBe('this-is-a-test');
    });

    it('should handle special characters', () => {
      expect(slugify('Hello & World!')).toBe('hello-world');
      expect(slugify('Test@123')).toBe('test123');
    });

    it('should handle multiple spaces', () => {
      expect(slugify('Hello   World')).toBe('hello-world');
    });

    it('should handle empty string', () => {
      expect(slugify('')).toBe('');
    });

    it('should handle numbers', () => {
      expect(slugify('Test 123')).toBe('test-123');
    });
  });

  describe('formatNumber', () => {
    it('should format numbers with commas', () => {
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(1234567)).toBe('1,234,567');
      expect(formatNumber(100)).toBe('100');
    });

    it('should handle decimal numbers', () => {
      expect(formatNumber(1000.5)).toBe('1,000.5');
      expect(formatNumber(1234.567)).toBe('1,234.567');
    });

    it('should handle zero', () => {
      expect(formatNumber(0)).toBe('0');
    });

    it('should handle negative numbers', () => {
      expect(formatNumber(-1000)).toBe('-1,000');
    });
  });

  describe('formatCurrency', () => {
    it('should format currency correctly', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00');
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
    });

    it('should handle different currencies', () => {
      expect(formatCurrency(1000, 'EUR')).toBe('€1,000.00');
      expect(formatCurrency(1000, 'GBP')).toBe('£1,000.00');
    });

    it('should handle zero', () => {
      expect(formatCurrency(0)).toBe('$0.00');
    });

    it('should handle negative amounts', () => {
      expect(formatCurrency(-1000)).toBe('-$1,000.00');
    });
  });

  describe('formatDate', () => {
    it('should format date correctly', () => {
      const date = new Date('2023-01-15');
      expect(formatDate(date)).toBe('Jan 15, 2023');
    });

    it('should handle different formats', () => {
      const date = new Date('2023-01-15');
      expect(formatDate(date, 'YYYY-MM-DD')).toBe('2023-01-15');
      expect(formatDate(date, 'MM/DD/YYYY')).toBe('01/15/2023');
    });

    it('should handle invalid date', () => {
      expect(formatDate('invalid')).toBe('Invalid Date');
    });
  });

  describe('formatRelativeTime', () => {
    it('should format relative time correctly', () => {
      const now = new Date();
      const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
      expect(formatRelativeTime(oneHourAgo)).toBe('1 hour ago');
    });

    it('should handle future dates', () => {
      const now = new Date();
      const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000);
      expect(formatRelativeTime(oneHourLater)).toBe('in 1 hour');
    });
  });

  describe('generateId', () => {
    it('should generate unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
    });

    it('should generate IDs with correct length', () => {
      const id = generateId();
      expect(id.length).toBe(8);
    });

    it('should generate alphanumeric IDs', () => {
      const id = generateId();
      expect(id).toMatch(/^[a-zA-Z0-9]+$/);
    });
  });

  describe('validateEmail', () => {
    it('should validate correct email addresses', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.co.uk')).toBe(true);
      expect(validateEmail('test+tag@example.com')).toBe(true);
    });

    it('should reject invalid email addresses', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
      expect(validateEmail('')).toBe(false);
    });
  });

  describe('validatePhone', () => {
    it('should validate correct phone numbers', () => {
      expect(validatePhone('+1-555-123-4567')).toBe(true);
      expect(validatePhone('555-123-4567')).toBe(true);
      expect(validatePhone('(555) 123-4567')).toBe(true);
    });

    it('should reject invalid phone numbers', () => {
      expect(validatePhone('123')).toBe(true);
      expect(validatePhone('invalid')).toBe(false);
      expect(validatePhone('')).toBe(false);
    });
  });

  describe('extractDomain', () => {
    it('should extract domain from URL', () => {
      expect(extractDomain('https://www.example.com/path')).toBe('example.com');
      expect(extractDomain('http://subdomain.example.com')).toBe('subdomain.example.com');
    });

    it('should handle URLs without protocol', () => {
      expect(extractDomain('www.example.com')).toBe('example.com');
    });

    it('should handle invalid URLs', () => {
      expect(extractDomain('invalid-url')).toBe('invalid-url');
      expect(extractDomain('')).toBe('');
    });
  });

  describe('maskEmail', () => {
    it('should mask email address', () => {
      expect(maskEmail('test@example.com')).toBe('t**t@example.com');
      expect(maskEmail('user@domain.com')).toBe('u**r@domain.com');
    });

    it('should handle short usernames', () => {
      expect(maskEmail('a@example.com')).toBe('a@example.com');
      expect(maskEmail('ab@example.com')).toBe('ab@example.com');
    });

    it('should handle invalid emails', () => {
      expect(maskEmail('invalid')).toBe('invalid');
      expect(maskEmail('')).toBe('');
    });
  });

  describe('maskPhone', () => {
    it('should mask phone number', () => {
      expect(maskPhone('555-123-4567')).toBe('555-***-4567');
      expect(maskPhone('+1-555-123-4567')).toBe('+1-***-123');
    });

    it('should handle different formats', () => {
      expect(maskPhone('(555) 123-4567')).toBe('(555) 123-4567');
    });

    it('should handle short numbers', () => {
      expect(maskPhone('123')).toBe('123');
      expect(maskPhone('1234')).toBe('1234');
    });
  });

  describe('countWords', () => {
    it('should count words correctly', () => {
      expect(countWords('Hello world')).toBe(2);
      expect(countWords('This is a test sentence')).toBe(5);
    });

    it('should handle empty string', () => {
      expect(countWords('')).toBe(0);
    });

    it('should handle multiple spaces', () => {
      expect(countWords('Hello   world')).toBe(2);
    });

    it('should handle punctuation', () => {
      expect(countWords('Hello, world!')).toBe(2);
    });
  });

  describe('countCharacters', () => {
    it('should count characters correctly', () => {
      expect(countCharacters('Hello')).toBe(5);
      expect(countCharacters('Hello world')).toBe(11);
    });

    it('should handle empty string', () => {
      expect(countCharacters('')).toBe(0);
    });

    it('should handle spaces and punctuation', () => {
      expect(countCharacters('Hello, world!')).toBe(13);
    });

    it('should handle unicode characters', () => {
      expect(countCharacters('Hello 🌍')).toBe(8);
    });
  });

  describe('removeHtmlTags', () => {
    it('should remove HTML tags', () => {
      expect(removeHtmlTags('<p>Hello world</p>')).toBe('Hello world');
      expect(removeHtmlTags('<div><span>Test</span></div>')).toBe('Test');
    });

    it('should handle self-closing tags', () => {
      expect(removeHtmlTags('<br>Hello<img src="test.jpg">')).toBe('Hello');
    });

    it('should handle attributes', () => {
      expect(removeHtmlTags('<a href="test.com">Link</a>')).toBe('Link');
    });

    it('should handle text without tags', () => {
      expect(removeHtmlTags('Plain text')).toBe('Plain text');
    });
  });

  describe('escapeHtml', () => {
    it('should escape HTML characters', () => {
      expect(escapeHtml('<script>alert("test")</script>')).toBe('&lt;script&gt;alert(&quot;test&quot;)&lt;/script&gt;');
      expect(escapeHtml('Hello & world')).toBe('Hello &amp; world');
    });

    it('should handle safe text', () => {
      expect(escapeHtml('Hello world')).toBe('Hello world');
    });
  });

  describe('unescapeHtml', () => {
    it('should unescape HTML entities', () => {
      expect(unescapeHtml('&lt;script&gt;')).toBe('<script>');
      expect(unescapeHtml('Hello &amp; world')).toBe('Hello & world');
    });

    it('should handle text without entities', () => {
      expect(unescapeHtml('Hello world')).toBe('Hello world');
    });
  });
});