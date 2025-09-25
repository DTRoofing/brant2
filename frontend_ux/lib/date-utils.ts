import { format, parseISO, isValid } from 'date-fns'

/**
 * Format a date string or Date object to a readable format
 * @param date - Date string, Date object, or timestamp
 * @param formatString - Optional format string (default: 'MMM dd, yyyy')
 * @returns Formatted date string
 */
export function formatDate(
  date: string | Date | number,
  formatString: string = 'MMM dd, yyyy'
): string {
  try {
    let dateObj: Date

    if (typeof date === 'string') {
      // Try to parse ISO string first, then fallback to regular parsing
      if (date.includes('T') || date.includes('Z')) {
        dateObj = parseISO(date)
      } else {
        dateObj = new Date(date)
      }
    } else if (typeof date === 'number') {
      // Handle timestamp (assume milliseconds)
      dateObj = new Date(date)
    } else {
      dateObj = date
    }

    // Validate the date
    if (!isValid(dateObj)) {
      console.warn('Invalid date provided to formatDate:', date)
      return 'Invalid Date'
    }

    return format(dateObj, formatString)
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'Invalid Date'
  }
}

/**
 * Format a date to a relative time (e.g., "2 days ago")
 * @param date - Date string, Date object, or timestamp
 * @returns Relative time string
 */
export function formatRelativeTime(date: string | Date | number): string {
  try {
    let dateObj: Date

    if (typeof date === 'string') {
      if (date.includes('T') || date.includes('Z')) {
        dateObj = parseISO(date)
      } else {
        dateObj = new Date(date)
      }
    } else if (typeof date === 'number') {
      dateObj = new Date(date)
    } else {
      dateObj = date
    }

    if (!isValid(dateObj)) {
      return 'Invalid Date'
    }

    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000)

    if (diffInSeconds < 60) {
      return 'Just now'
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60)
      return `${minutes} minute${minutes === 1 ? '' : 's'} ago`
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600)
      return `${hours} hour${hours === 1 ? '' : 's'} ago`
    } else if (diffInSeconds < 2592000) {
      const days = Math.floor(diffInSeconds / 86400)
      return `${days} day${days === 1 ? '' : 's'} ago`
    } else if (diffInSeconds < 31536000) {
      const months = Math.floor(diffInSeconds / 2592000)
      return `${months} month${months === 1 ? '' : 's'} ago`
    } else {
      const years = Math.floor(diffInSeconds / 31536000)
      return `${years} year${years === 1 ? '' : 's'} ago`
    }
  } catch (error) {
    console.error('Error formatting relative time:', error)
    return 'Invalid Date'
  }
}

/**
 * Format a date for display in tables (compact format)
 * @param date - Date string, Date object, or timestamp
 * @returns Compact formatted date string
 */
export function formatTableDate(date: string | Date | number): string {
  return formatDate(date, 'MMM dd, yyyy')
}

/**
 * Format a date for API requests (ISO format)
 * @param date - Date string, Date object, or timestamp
 * @returns ISO formatted date string
 */
export function formatISO(date: string | Date | number): string {
  try {
    let dateObj: Date

    if (typeof date === 'string') {
      if (date.includes('T') || date.includes('Z')) {
        dateObj = parseISO(date)
      } else {
        dateObj = new Date(date)
      }
    } else if (typeof date === 'number') {
      dateObj = new Date(date)
    } else {
      dateObj = date
    }

    if (!isValid(dateObj)) {
      return new Date().toISOString()
    }

    return dateObj.toISOString()
  } catch (error) {
    console.error('Error formatting ISO date:', error)
    return new Date().toISOString()
  }
}

/**
 * Get the current date in a specific format
 * @param formatString - Format string (default: 'yyyy-MM-dd')
 * @returns Current date formatted string
 */
export function getCurrentDate(formatString: string = 'yyyy-MM-dd'): string {
  return format(new Date(), formatString)
}

/**
 * Check if a date is today
 * @param date - Date string, Date object, or timestamp
 * @returns True if the date is today
 */
export function isToday(date: string | Date | number): boolean {
  try {
    let dateObj: Date

    if (typeof date === 'string') {
      if (date.includes('T') || date.includes('Z')) {
        dateObj = parseISO(date)
      } else {
        dateObj = new Date(date)
      }
    } else if (typeof date === 'number') {
      dateObj = new Date(date)
    } else {
      dateObj = date
    }

    if (!isValid(dateObj)) {
      return false
    }

    const today = new Date()
    return (
      dateObj.getDate() === today.getDate() &&
      dateObj.getMonth() === today.getMonth() &&
      dateObj.getFullYear() === today.getFullYear()
    )
  } catch (error) {
    console.error('Error checking if date is today:', error)
    return false
  }
}
