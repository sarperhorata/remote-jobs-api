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
  return str.substring(0, length) + suffix;
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