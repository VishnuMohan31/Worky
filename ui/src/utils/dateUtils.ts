/**
 * Date utility functions for consistent DD/MM/YYYY formatting across the application
 */

/**
 * Convert a date string from YYYY-MM-DD to DD/MM/YYYY format
 */
export const formatDateForDisplay = (dateString: string): string => {
  // Handle null, undefined, empty string, or invalid values
  if (!dateString || 
      dateString === 'null' || 
      dateString === 'undefined' || 
      dateString === 'NaN' ||
      dateString.trim() === '') {
    return ''
  }
  
  try {
    let date: Date
    
    // Handle various date formats
    if (dateString.includes('/')) {
      // Already in DD/MM/YYYY format
      const [day, month, year] = dateString.split('/')
      if (!day || !month || !year) return ''
      date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
    } else if (dateString.includes('-')) {
      // YYYY-MM-DD format
      if (dateString.length === 10) {
        date = new Date(dateString + 'T00:00:00')
      } else {
        date = new Date(dateString)
      }
    } else {
      // Try to parse as is
      date = new Date(dateString)
    }
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.warn('Invalid date provided to formatDateForDisplay:', dateString)
      return ''
    }
    
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()
    
    // Additional validation
    if (year < 1900 || year > 2100) {
      console.warn('Date year out of reasonable range:', dateString)
      return ''
    }
    
    return `${day}/${month}/${year}`
  } catch (error) {
    console.error('Error formatting date:', error, 'Input:', dateString)
    return ''
  }
}

/**
 * Convert a date string from DD/MM/YYYY to YYYY-MM-DD format (for API/database)
 */
export const formatDateForAPI = (dateString: string): string => {
  if (!dateString) return ''
  
  try {
    // Handle DD/MM/YYYY format
    if (dateString.includes('/')) {
      const [day, month, year] = dateString.split('/')
      if (day && month && year) {
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
      }
    }
    
    // If already in YYYY-MM-DD format, return as is
    if (dateString.match(/^\d{4}-\d{2}-\d{2}$/)) {
      return dateString
    }
    
    // Try to parse as Date and convert
    const date = new Date(dateString)
    if (!isNaN(date.getTime())) {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
    
    return dateString
  } catch (error) {
    console.error('Error converting date for API:', error)
    return dateString
  }
}

/**
 * Validate DD/MM/YYYY date format
 */
export const isValidDateFormat = (dateString: string): boolean => {
  if (!dateString) return true // Empty dates are valid
  
  const ddmmyyyyRegex = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/
  const match = dateString.match(ddmmyyyyRegex)
  
  if (!match) return false
  
  const day = parseInt(match[1], 10)
  const month = parseInt(match[2], 10)
  const year = parseInt(match[3], 10)
  
  // Basic validation
  if (month < 1 || month > 12) return false
  if (day < 1 || day > 31) return false
  if (year < 1900 || year > 2100) return false
  
  // Check if date is valid (handles leap years, etc.)
  const date = new Date(year, month - 1, day)
  return date.getFullYear() === year && 
         date.getMonth() === month - 1 && 
         date.getDate() === day
}

/**
 * Compare two dates in DD/MM/YYYY format
 * Returns: -1 if date1 < date2, 0 if equal, 1 if date1 > date2
 */
export const compareDDMMYYYYDates = (date1: string, date2: string): number => {
  if (!date1 || !date2) return 0
  
  try {
    // Convert both dates to YYYY-MM-DD format for comparison
    const apiDate1 = formatDateForAPI(date1)
    const apiDate2 = formatDateForAPI(date2)
    
    // If conversion failed, try direct comparison
    if (!apiDate1 || !apiDate2) return 0
    
    const d1 = new Date(apiDate1 + 'T00:00:00')
    const d2 = new Date(apiDate2 + 'T00:00:00')
    
    if (isNaN(d1.getTime()) || isNaN(d2.getTime())) return 0
    
    if (d1 < d2) return -1
    if (d1 > d2) return 1
    return 0
  } catch (error) {
    console.error('Error comparing dates:', error)
    return 0
  }
}

/**
 * Get today's date in DD/MM/YYYY format
 */
export const getTodayDDMMYYYY = (): string => {
  const today = new Date()
  const day = String(today.getDate()).padStart(2, '0')
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const year = today.getFullYear()
  
  return `${day}/${month}/${year}`
}

/**
 * Format a Date object to DD/MM/YYYY string
 */
export const formatDateObjectToDDMMYYYY = (date: Date): string => {
  if (!date || isNaN(date.getTime())) return ''
  
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  
  return `${day}/${month}/${year}`
}

/**
 * Parse DD/MM/YYYY string to Date object
 */
export const parseDDMMYYYYToDate = (dateString: string): Date | null => {
  if (!dateString || !isValidDateFormat(dateString)) return null
  
  try {
    const [day, month, year] = dateString.split('/').map(Number)
    return new Date(year, month - 1, day)
  } catch (error) {
    console.error('Error parsing date:', error)
    return null
  }
}