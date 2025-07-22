import { 
  formatDate, 
  formatRelativeTime, 
  formatDateRange,
  isDateValid,
  getDaysDifference,
  formatTimeAgo
} from '../../utils/dateUtils';

describe('dateUtils', () => {
  beforeEach(() => {
    // Mock current date to 2024-01-15
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2024-01-15T12:00:00Z'));
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('formatDate', () => {
    test('formats date correctly', () => {
      const date = new Date('2024-01-15T10:30:00Z');
      const result = formatDate(date);
      expect(result).toBe('Jan 15, 2024');
    });

    test('handles different date formats', () => {
      const date1 = new Date('2024-12-25T00:00:00Z');
      const date2 = new Date('2023-06-01T12:00:00Z');
      
      expect(formatDate(date1)).toBe('Dec 25, 2024');
      expect(formatDate(date2)).toBe('Jun 1, 2023');
    });

    test('handles invalid date', () => {
      const invalidDate = new Date('invalid');
      const result = formatDate(invalidDate);
      expect(result).toBe('Invalid Date');
    });
  });

  describe('formatRelativeTime', () => {
    test('formats time as "just now" for recent times', () => {
      const recentTime = new Date('2024-01-15T11:59:30Z'); // 30 seconds ago
      const result = formatRelativeTime(recentTime);
      expect(result).toBe('just now');
    });

    test('formats time as minutes ago', () => {
      const fiveMinutesAgo = new Date('2024-01-15T11:55:00Z');
      const result = formatRelativeTime(fiveMinutesAgo);
      expect(result).toBe('5 minutes ago');
    });

    test('formats time as hours ago', () => {
      const twoHoursAgo = new Date('2024-01-15T10:00:00Z');
      const result = formatRelativeTime(twoHoursAgo);
      expect(result).toBe('2 hours ago');
    });

    test('formats time as days ago', () => {
      const threeDaysAgo = new Date('2024-01-12T12:00:00Z');
      const result = formatRelativeTime(threeDaysAgo);
      expect(result).toBe('3 days ago');
    });

    test('formats time as weeks ago', () => {
      const twoWeeksAgo = new Date('2024-01-01T12:00:00Z');
      const result = formatRelativeTime(twoWeeksAgo);
      expect(result).toBe('2 weeks ago');
    });

    test('formats time as months ago', () => {
      const threeMonthsAgo = new Date('2023-10-15T12:00:00Z');
      const result = formatRelativeTime(threeMonthsAgo);
      expect(result).toBe('3 months ago');
    });

    test('formats time as years ago', () => {
      const twoYearsAgo = new Date('2022-01-15T12:00:00Z');
      const result = formatRelativeTime(twoYearsAgo);
      expect(result).toBe('2 years ago');
    });

    test('handles future dates', () => {
      const futureDate = new Date('2024-01-16T12:00:00Z');
      const result = formatRelativeTime(futureDate);
      expect(result).toBe('in 1 day');
    });
  });

  describe('formatDateRange', () => {
    test('formats date range correctly', () => {
      const startDate = new Date('2024-01-01T00:00:00Z');
      const endDate = new Date('2024-01-31T23:59:59Z');
      const result = formatDateRange(startDate, endDate);
      expect(result).toBe('Jan 1 - Jan 31, 2024');
    });

    test('formats same day range', () => {
      const date = new Date('2024-01-15T12:00:00Z');
      const result = formatDateRange(date, date);
      expect(result).toBe('Jan 15, 2024');
    });

    test('formats different year range', () => {
      const startDate = new Date('2023-12-01T00:00:00Z');
      const endDate = new Date('2024-01-31T23:59:59Z');
      const result = formatDateRange(startDate, endDate);
      expect(result).toBe('Dec 1, 2023 - Jan 31, 2024');
    });

    test('handles invalid dates', () => {
      const invalidDate = new Date('invalid');
      const validDate = new Date('2024-01-15T12:00:00Z');
      const result = formatDateRange(invalidDate, validDate);
      expect(result).toBe('Invalid Date');
    });
  });

  describe('isDateValid', () => {
    test('returns true for valid dates', () => {
      const validDate = new Date('2024-01-15T12:00:00Z');
      expect(isDateValid(validDate)).toBe(true);
    });

    test('returns false for invalid dates', () => {
      const invalidDate = new Date('invalid');
      expect(isDateValid(invalidDate)).toBe(false);
    });

    test('returns false for null', () => {
      expect(isDateValid(null)).toBe(false);
    });

    test('returns false for undefined', () => {
      expect(isDateValid(undefined)).toBe(false);
    });
  });

  describe('getDaysDifference', () => {
    test('calculates days difference correctly', () => {
      const date1 = new Date('2024-01-15T12:00:00Z');
      const date2 = new Date('2024-01-20T12:00:00Z');
      const result = getDaysDifference(date1, date2);
      expect(result).toBe(5);
    });

    test('calculates negative difference for past dates', () => {
      const date1 = new Date('2024-01-20T12:00:00Z');
      const date2 = new Date('2024-01-15T12:00:00Z');
      const result = getDaysDifference(date1, date2);
      expect(result).toBe(-5);
    });

    test('returns 0 for same day', () => {
      const date = new Date('2024-01-15T12:00:00Z');
      const result = getDaysDifference(date, date);
      expect(result).toBe(0);
    });

    test('handles different times on same day', () => {
      const date1 = new Date('2024-01-15T00:00:00Z');
      const date2 = new Date('2024-01-15T23:59:59Z');
      const result = getDaysDifference(date1, date2);
      expect(result).toBe(0);
    });
  });

  describe('formatTimeAgo', () => {
    test('formats seconds ago', () => {
      const thirtySecondsAgo = new Date('2024-01-15T11:59:30Z');
      const result = formatTimeAgo(thirtySecondsAgo);
      expect(result).toBe('30 seconds ago');
    });

    test('formats minutes ago', () => {
      const fiveMinutesAgo = new Date('2024-01-15T11:55:00Z');
      const result = formatTimeAgo(fiveMinutesAgo);
      expect(result).toBe('5 minutes ago');
    });

    test('formats hours ago', () => {
      const twoHoursAgo = new Date('2024-01-15T10:00:00Z');
      const result = formatTimeAgo(twoHoursAgo);
      expect(result).toBe('2 hours ago');
    });

    test('formats days ago', () => {
      const threeDaysAgo = new Date('2024-01-12T12:00:00Z');
      const result = formatTimeAgo(threeDaysAgo);
      expect(result).toBe('3 days ago');
    });

    test('formats weeks ago', () => {
      const twoWeeksAgo = new Date('2024-01-01T12:00:00Z');
      const result = formatTimeAgo(twoWeeksAgo);
      expect(result).toBe('2 weeks ago');
    });

    test('formats months ago', () => {
      const threeMonthsAgo = new Date('2023-10-15T12:00:00Z');
      const result = formatTimeAgo(threeMonthsAgo);
      expect(result).toBe('3 months ago');
    });

    test('formats years ago', () => {
      const twoYearsAgo = new Date('2022-01-15T12:00:00Z');
      const result = formatTimeAgo(twoYearsAgo);
      expect(result).toBe('2 years ago');
    });

    test('handles singular forms', () => {
      const oneMinuteAgo = new Date('2024-01-15T11:59:00Z');
      const oneHourAgo = new Date('2024-01-15T11:00:00Z');
      const oneDayAgo = new Date('2024-01-14T12:00:00Z');
      
      expect(formatTimeAgo(oneMinuteAgo)).toBe('1 minute ago');
      expect(formatTimeAgo(oneHourAgo)).toBe('1 hour ago');
      expect(formatTimeAgo(oneDayAgo)).toBe('1 day ago');
    });
  });
});