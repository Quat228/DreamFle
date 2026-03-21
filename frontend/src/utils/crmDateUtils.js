/**
 * CRM-specific date utilities for admin timezone handling
 * All times are displayed and input in admin's local timezone
 */

/**
 * Convert UTC date string to local datetime-local format for input field
 * @param {string} utcDateString - ISO date string from backend (UTC)
 * @returns {string} Format: "YYYY-MM-DDTHH:mm" in local timezone
 */
export const utcToLocalInput = (utcDateString) => {
  if (!utcDateString) return '';
  
  const date = new Date(utcDateString); // Automatically converts UTC to local
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

/**
 * Convert local datetime-local input to UTC ISO string for API
 * @param {string} localInput - Format: "YYYY-MM-DDTHH:mm" (interpreted as local time)
 * @returns {string} ISO string in UTC
 */
export const localInputToUTC = (localInput) => {
  if (!localInput) return null;
  
  // Create date from local input (browser interprets as local time)
  const localDate = new Date(localInput);
  
  // Convert to UTC ISO string
  return localDate.toISOString();
};

/**
 * Format date for CRM display with timezone info
 * @param {string} dateString - ISO date string from backend (UTC)
 * @returns {string} Formatted date in local timezone with timezone abbreviation
 */
export const formatCRMDate = (dateString) => {
  if (!dateString) return 'Not set';
  
  const date = new Date(dateString);
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const timezoneAbbr = date.toLocaleString('en-US', { timeZoneName: 'short' }).split(' ').pop();
  
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  }) + ` (${timezone})`;
};

/**
 * Get admin's timezone name
 * @returns {string} Timezone name (e.g., "America/Los_Angeles")
 */
export const getAdminTimezone = () => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
};

/**
 * Get admin's timezone abbreviation
 * @returns {string} Timezone abbreviation (e.g., "PST", "EST")
 */
export const getAdminTimezoneAbbr = () => {
  const now = new Date();
  return now.toLocaleString('en-US', { timeZoneName: 'short' }).split(' ').pop();
};







