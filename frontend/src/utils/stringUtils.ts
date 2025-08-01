// String utility functions

/**
 * Capitalizes the first letter of a string
 */
export const capitalize = (str: string): string => {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Truncates a string to a specified length
 */
export const truncate = (str: string, length: number, suffix: string = '...'): string => {
  if (!str || str.length <= length) return str;
  return str.substring(0, length).trim() + suffix;
};

/**
 * Converts a string to a URL-friendly slug
 */
export const slugify = (str: string): string => {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

/**
 * Removes HTML tags from a string
 */
export const stripHtml = (str: string): string => {
  if (!str) return str;
  return str.replace(/<[^>]*>/g, '');
};

/**
 * Converts a string to title case
 */
export const toTitleCase = (str: string): string => {
  if (!str) return str;
  return str.replace(/\w\S*/g, (txt) => 
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
};

/**
 * Checks if a string is empty or contains only whitespace
 */
export const isEmpty = (str: string): boolean => {
  return !str || str.trim().length === 0;
};

/**
 * Counts words in a string
 */
export const wordCount = (str: string): number => {
  if (!str) return 0;
  return str.trim().split(/\s+/).length;
};

/**
 * Extracts the first sentence from a string
 */
export const getFirstSentence = (str: string): string => {
  if (!str) return str;
  const sentences = str.match(/[^.!?]+[.!?]+/g);
  return sentences ? sentences[0].trim() : str;
};

/**
 * Generates a random string of specified length
 */
export const generateRandomString = (length: number): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

/**
 * Masks sensitive information like email addresses
 */
export const maskEmail = (email: string): string => {
  if (!email || !email.includes('@')) return email;
  const [local, domain] = email.split('@');
  const maskedLocal = local.length > 2 
    ? local.charAt(0) + '*'.repeat(local.length - 2) + local.charAt(local.length - 1)
    : local;
  return `${maskedLocal}@${domain}`;
};

/**
 * Formats numbers with commas
 */
export const formatNumber = (num: number): string => {
  return num.toLocaleString('en-US');
};

/**
 * Formats currency
 */
export const formatCurrency = (amount: number, currency: string = 'USD', decimals: number = 2): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(amount);
};

/**
 * Formats phone numbers
 */
export const formatPhoneNumber = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length !== 10) return phone;
  return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
};

/**
 * Validates email addresses
 */
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  // Additional checks for edge cases
  if (email.includes('..') || email.includes('@.') || email.includes('.@')) {
    return false;
  }
  return emailRegex.test(email);
};

/**
 * Validates password strength
 */
export const validatePassword = (password: string): boolean => {
  if (!password || password.length < 8) return false;
  
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  
  return hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar;
};

/**
 * Removes special characters from string
 */
export const removeSpecialCharacters = (str: string): string => {
  if (!str) return str;
  return str.replace(/[^\w\s]/g, '');
};

/**
 * Formats a date to a readable string
 */
export const formatDate = (date: Date | string, format: string = 'MMM dd, yyyy'): string => {
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(dateObj.getTime())) return 'Invalid Date';
    
    if (format === 'YYYY-MM-DD') {
      return dateObj.toISOString().split('T')[0];
    }
    if (format === 'MM/DD/YYYY') {
      return `${(dateObj.getMonth() + 1).toString().padStart(2, '0')}/${dateObj.getDate().toString().padStart(2, '0')}/${dateObj.getFullYear()}`;
    }
    
    return dateObj.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  } catch {
    return 'Invalid Date';
  }
};

/**
 * Formats relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

  if (diffInMs < 0) {
    const absDiffInHours = Math.floor(Math.abs(diffInMs) / (1000 * 60 * 60));
    return `in ${absDiffInHours} hour${absDiffInHours !== 1 ? 's' : ''}`;
  }

  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
  }
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
  }
  return `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`;
};

/**
 * Generates a unique ID
 */
export const generateId = (): string => {
  return Math.random().toString(36).substring(2, 10);
};

/**
 * Validates phone number format
 */
export const validatePhone = (phone: string): boolean => {
  if (!phone) return false;
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
  const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
  return phoneRegex.test(cleanPhone);
};

/**
 * Extracts domain from URL
 */
export const extractDomain = (url: string): string => {
  if (!url) return '';
  try {
    const urlObj = new URL(url.startsWith('http') ? url : `https://${url}`);
    return urlObj.hostname.replace(/^www\./, '');
  } catch {
    return '';
  }
};

/**
 * Masks phone number
 */
export const maskPhone = (phone: string): string => {
  if (!phone || phone.length < 7) return phone;
  const parts = phone.split('-');
  if (parts.length >= 3) {
    return `${parts[0]}-***-${parts[2]}`;
  }
  return phone.replace(/(\d{3})\d{3}(\d{4})/, '$1-***-$2');
};

/**
 * Counts words in a string
 */
export const countWords = (str: string): number => {
  if (!str) return 0;
  return str.trim().split(/\s+/).length;
};

/**
 * Counts characters in a string
 */
export const countCharacters = (str: string): number => {
  if (!str) return 0;
  return str.length;
};

/**
 * Removes HTML tags from a string
 */
export const removeHtmlTags = (str: string): string => {
  if (!str) return str;
  return str.replace(/<[^>]*>/g, '');
};

/**
 * Escapes HTML characters
 */
export const escapeHtml = (str: string): string => {
  if (!str) return str;
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

/**
 * Unescapes HTML entities
 */
export const unescapeHtml = (str: string): string => {
  if (!str) return str;
  return str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
};