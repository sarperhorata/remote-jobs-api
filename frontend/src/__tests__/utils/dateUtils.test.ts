import { 
  formatDate, 
  formatRelativeTime, 
  formatDuration, 
  isValidDate,
  getDaysBetween,
  addDays,
  subtractDays,
  isToday,
  isYesterday,
  isThisWeek,
  isThisMonth,
  isThisYear
} from '../../utils/dateUtils';

describe('dateUtils', () => {
  beforeEach(() => {
    // Mock current date to 2024-01-15 12:00:00
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2024-01-15T12:00:00Z'));
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('formatDate', () => {
    it('formats date with default format', () => {
      const date = new Date('2024-01-15T10:30:00Z');
      expect(formatDate(date)).toBe('Jan 15, 2024');
    });

    it('formats date with custom format', () => {
      const date = new Date('2024-01-15T10:30:00Z');
      expect(formatDate(date, 'YYYY-MM-DD')).toBe('2024-01-15');
    });

    it('handles invalid date', () => {
      expect(formatDate('invalid-date')).toBe('Invalid Date');
    });

    it('handles null date', () => {
      expect(formatDate(null)).toBe('Invalid Date');
    });
  });

  describe('formatRelativeTime', () => {
    it('formats time as "just now" for recent times', () => {
      const date = new Date('2024-01-15T11:59:30Z'); // 30 seconds ago
      expect(formatRelativeTime(date)).toBe('just now');
    });

    it('formats time as minutes ago', () => {
      const date = new Date('2024-01-15T11:45:00Z'); // 15 minutes ago
      expect(formatRelativeTime(date)).toBe('15 minutes ago');
    });

    it('formats time as hours ago', () => {
      const date = new Date('2024-01-15T09:00:00Z'); // 3 hours ago
      expect(formatRelativeTime(date)).toBe('3 hours ago');
    });

    it('formats time as days ago', () => {
      const date = new Date('2024-01-13T12:00:00Z'); // 2 days ago
      expect(formatRelativeTime(date)).toBe('2 days ago');
    });

    it('formats time as weeks ago', () => {
      const date = new Date('2024-01-01T12:00:00Z'); // 2 weeks ago
      expect(formatRelativeTime(date)).toBe('2 weeks ago');
    });

    it('formats time as months ago', () => {
      const date = new Date('2023-11-15T12:00:00Z'); // 2 months ago
      expect(formatRelativeTime(date)).toBe('2 months ago');
    });

    it('formats time as years ago', () => {
      const date = new Date('2022-01-15T12:00:00Z'); // 2 years ago
      expect(formatRelativeTime(date)).toBe('2 years ago');
    });

    it('handles future dates', () => {
      const date = new Date('2024-01-16T12:00:00Z'); // 1 day in future
      expect(formatRelativeTime(date)).toBe('in 1 day');
    });
  });

  describe('formatDuration', () => {
    it('formats duration in seconds', () => {
      expect(formatDuration(30)).toBe('30 seconds');
    });

    it('formats duration in minutes', () => {
      expect(formatDuration(90)).toBe('1 minute 30 seconds');
    });

    it('formats duration in hours', () => {
      expect(formatDuration(3661)).toBe('1 hour 1 minute 1 second');
    });

    it('formats duration in days', () => {
      expect(formatDuration(90061)).toBe('1 day 1 hour 1 minute 1 second');
    });

    it('handles zero duration', () => {
      expect(formatDuration(0)).toBe('0 seconds');
    });

    it('handles negative duration', () => {
      expect(formatDuration(-30)).toBe('30 seconds');
    });
  });

  describe('isValidDate', () => {
    it('returns true for valid date', () => {
      expect(isValidDate(new Date('2024-01-15'))).toBe(true);
    });

    it('returns false for invalid date', () => {
      expect(isValidDate(new Date('invalid'))).toBe(false);
    });

    it('returns false for null', () => {
      expect(isValidDate(null)).toBe(false);
    });

    it('returns false for undefined', () => {
      expect(isValidDate(undefined)).toBe(false);
    });
  });

  describe('getDaysBetween', () => {
    it('calculates days between two dates', () => {
      const startDate = new Date('2024-01-15');
      const endDate = new Date('2024-01-20');
      expect(getDaysBetween(startDate, endDate)).toBe(5);
    });

    it('returns 0 for same date', () => {
      const date = new Date('2024-01-15');
      expect(getDaysBetween(date, date)).toBe(0);
    });

    it('handles reverse order', () => {
      const startDate = new Date('2024-01-20');
      const endDate = new Date('2024-01-15');
      expect(getDaysBetween(startDate, endDate)).toBe(5);
    });
  });

  describe('addDays', () => {
    it('adds days to date', () => {
      const date = new Date('2024-01-15');
      const result = addDays(date, 5);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-20');
    });

    it('handles negative days', () => {
      const date = new Date('2024-01-15');
      const result = addDays(date, -5);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-10');
    });
  });

  describe('subtractDays', () => {
    it('subtracts days from date', () => {
      const date = new Date('2024-01-15');
      const result = subtractDays(date, 5);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-10');
    });

    it('handles negative days', () => {
      const date = new Date('2024-01-15');
      const result = subtractDays(date, -5);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-20');
    });
  });

  describe('isToday', () => {
    it('returns true for today', () => {
      const today = new Date('2024-01-15T12:00:00Z');
      expect(isToday(today)).toBe(true);
    });

    it('returns false for other days', () => {
      const yesterday = new Date('2024-01-14T12:00:00Z');
      expect(isToday(yesterday)).toBe(false);
    });
  });

  describe('isYesterday', () => {
    it('returns true for yesterday', () => {
      const yesterday = new Date('2024-01-14T12:00:00Z');
      expect(isYesterday(yesterday)).toBe(true);
    });

    it('returns false for other days', () => {
      const today = new Date('2024-01-15T12:00:00Z');
      expect(isYesterday(today)).toBe(false);
    });
  });

  describe('isThisWeek', () => {
    it('returns true for this week', () => {
      const thisWeek = new Date('2024-01-16T12:00:00Z'); // Tuesday
      expect(isThisWeek(thisWeek)).toBe(true);
    });

    it('returns false for last week', () => {
      const lastWeek = new Date('2024-01-08T12:00:00Z');
      expect(isThisWeek(lastWeek)).toBe(false);
    });
  });

  describe('isThisMonth', () => {
    it('returns true for this month', () => {
      const thisMonth = new Date('2024-01-20T12:00:00Z');
      expect(isThisMonth(thisMonth)).toBe(true);
    });

    it('returns false for last month', () => {
      const lastMonth = new Date('2023-12-15T12:00:00Z');
      expect(isThisMonth(lastMonth)).toBe(false);
    });
  });

  describe('isThisYear', () => {
    it('returns true for this year', () => {
      const thisYear = new Date('2024-06-15T12:00:00Z');
      expect(isThisYear(thisYear)).toBe(true);
    });

    it('returns false for last year', () => {
      const lastYear = new Date('2023-01-15T12:00:00Z');
      expect(isThisYear(lastYear)).toBe(false);
    });
  });
});