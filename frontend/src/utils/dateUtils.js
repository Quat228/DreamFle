/**
 * Date utility functions for timezone-aware date formatting
 * Automatically converts UTC dates from backend to user's local timezone
 */

/**
 * Format a UTC date string to user's local timezone
 * @param {string} dateString - ISO date string from backend (UTC)
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date in user's local timezone
 */
export const formatLocalDate = (dateString, options = {}) => {
  if (!dateString) return null;
  
  const date = new Date(dateString); // JavaScript automatically converts UTC to local
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short', // Shows timezone abbreviation (PST, EST, etc.)
    ...options
  };
  
  return date.toLocaleString('en-US', defaultOptions);
};

/**
 * Format date for short display (e.g., "Dec 3, 1:00 PM PST")
 */
export const formatShortDate = (dateString) => {
  if (!dateString) return null;
  return formatLocalDate(dateString, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  });
};

/**
 * Format date for long display (e.g., "December 3, 2025, 1:00 PM PST")
 */
export const formatLongDate = (dateString) => {
  if (!dateString) return null;
  return formatLocalDate(dateString, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  });
};

/**
 * Format date without time (e.g., "Dec 3, 2025")
 */
export const formatDateOnly = (dateString) => {
  if (!dateString) return null;
  return formatLocalDate(dateString, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Calculate time until a date
 * @param {string} dateString - ISO date string
 * @returns {object} { days, hours, minutes, seconds }
 */
export const getTimeUntil = (dateString) => {
  if (!dateString) return null;
  
  const now = new Date();
  const target = new Date(dateString);
  const diff = target - now;
  
  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 };
  }
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  
  return { days, hours, minutes, seconds };
};

/**
 * Get user's timezone name (e.g., "America/Los_Angeles")
 */
export const getUserTimezone = () => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
};

/**
 * Get user's timezone abbreviation (e.g., "PST", "EST")
 */
export const getUserTimezoneAbbr = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('en-US', { timeZoneName: 'short' }).split(' ').pop();
};

