/**
 * Custom Date Input Component with DD/MM/YYYY format
 */
import React, { useState, useEffect } from 'react'
import { formatDateForDisplay, formatDateForAPI, isValidDateFormat } from '../../utils/dateUtils'

interface DateInputProps {
  value: string // Expected in YYYY-MM-DD format (API format)
  onChange: (value: string) => void // Returns YYYY-MM-DD format (API format)
  placeholder?: string
  disabled?: boolean
  required?: boolean
  className?: string
  style?: React.CSSProperties
  min?: string // YYYY-MM-DD format
  max?: string // YYYY-MM-DD format
  name?: string
  id?: string
}

export default function DateInput({
  value,
  onChange,
  placeholder = 'DD/MM/YYYY',
  disabled = false,
  required = false,
  className = '',
  style = {},
  min,
  max,
  name,
  id
}: DateInputProps) {
  // Internal state for display value (DD/MM/YYYY)
  const [displayValue, setDisplayValue] = useState('')
  const [isValid, setIsValid] = useState(true)

  // Convert API value (YYYY-MM-DD) to display value (DD/MM/YYYY) on mount/value change
  useEffect(() => {
    if (value) {
      const formatted = formatDateForDisplay(value)
      setDisplayValue(formatted)
      setIsValid(true)
    } else {
      setDisplayValue('')
      setIsValid(true)
    }
  }, [value])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value
    setDisplayValue(inputValue)

    // Validate format
    const valid = isValidDateFormat(inputValue) || inputValue === ''
    setIsValid(valid)

    if (valid) {
      // Convert to API format and call onChange
      const apiValue = formatDateForAPI(inputValue)
      onChange(apiValue)
    }
  }

  const handleBlur = () => {
    // Re-validate on blur
    const valid = isValidDateFormat(displayValue) || displayValue === ''
    setIsValid(valid)
    
    if (!valid && displayValue !== '') {
      // If invalid, try to auto-correct common mistakes
      const corrected = autoCorrectDate(displayValue)
      if (corrected && isValidDateFormat(corrected)) {
        setDisplayValue(corrected)
        setIsValid(true)
        const apiValue = formatDateForAPI(corrected)
        onChange(apiValue)
      }
    }
  }

  // Auto-correct common date input mistakes
  const autoCorrectDate = (input: string): string => {
    // Remove extra spaces and non-numeric characters except /
    let cleaned = input.replace(/[^\d/]/g, '')
    
    // Auto-add slashes if missing
    if (cleaned.length === 8 && !cleaned.includes('/')) {
      // DDMMYYYY -> DD/MM/YYYY
      cleaned = `${cleaned.slice(0, 2)}/${cleaned.slice(2, 4)}/${cleaned.slice(4, 8)}`
    } else if (cleaned.length === 6 && !cleaned.includes('/')) {
      // DDMMYY -> DD/MM/20YY (assume 20xx for YY)
      const year = parseInt(cleaned.slice(4, 6))
      const fullYear = year < 50 ? 2000 + year : 1900 + year
      cleaned = `${cleaned.slice(0, 2)}/${cleaned.slice(2, 4)}/${fullYear}`
    }
    
    return cleaned
  }

  // Check if current value violates min/max constraints
  const checkConstraints = (): { violatesMin: boolean; violatesMax: boolean } => {
    if (!displayValue || !isValid) return { violatesMin: false, violatesMax: false }
    
    const apiValue = formatDateForAPI(displayValue)
    const violatesMin = min ? apiValue < min : false
    const violatesMax = max ? apiValue > max : false
    
    return { violatesMin, violatesMax }
  }

  const { violatesMin, violatesMax } = checkConstraints()
  const hasConstraintViolation = violatesMin || violatesMax

  // Convert display value (DD/MM/YYYY) to native date input format (YYYY-MM-DD)
  const getNativeDateValue = (): string => {
    if (!displayValue || !isValidDateFormat(displayValue)) return ''
    const apiValue = formatDateForAPI(displayValue)
    return apiValue
  }

  // Handle native date picker change
  const handleNativeDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const nativeValue = e.target.value // YYYY-MM-DD format
    if (nativeValue) {
      const formatted = formatDateForDisplay(nativeValue)
      setDisplayValue(formatted)
      setIsValid(true)
      onChange(nativeValue)
    }
  }

  // Use ref for native date input
  const nativeInputRef = React.useRef<HTMLInputElement>(null)

  // Open native date picker
  const openDatePicker = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (nativeInputRef.current && !disabled) {
      // Focus first to ensure it's ready
      nativeInputRef.current.focus()
      
      // Try showPicker() first (modern browsers), fallback to click()
      const input = nativeInputRef.current as any
      if (typeof input.showPicker === 'function') {
        try {
          const result = input.showPicker() as Promise<void> | void
          // Check if it returns a Promise
          if (result && typeof (result as Promise<void>).catch === 'function') {
            (result as Promise<void>).catch(() => {
              // Fallback if showPicker fails
              nativeInputRef.current?.click()
            })
          }
        } catch {
          // If showPicker throws, fallback to click
          nativeInputRef.current?.click()
        }
      } else {
        // For browsers without showPicker, use click
        setTimeout(() => {
          nativeInputRef.current?.click()
        }, 10)
      }
    }
  }

  return (
    <div className="relative">
      <input
        type="text"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        name={name}
        id={id}
        className={`${className} pr-10 ${
          !isValid || hasConstraintViolation 
            ? 'border-red-300 bg-red-50' 
            : 'border-gray-300'
        }`}
        style={style}
        maxLength={10} // DD/MM/YYYY = 10 characters
      />
      {/* Calendar icon button */}
      <button
        type="button"
        onClick={openDatePicker}
        disabled={disabled}
        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 rounded p-1 z-10"
        style={{ padding: '4px' }}
        title="Open calendar"
        aria-label="Open calendar"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </button>
      {/* Native date input for calendar picker - hidden but accessible */}
      <input
        ref={nativeInputRef}
        type="date"
        value={getNativeDateValue()}
        onChange={handleNativeDateChange}
        min={min}
        max={max}
        disabled={disabled}
        className="sr-only"
        style={{ position: 'absolute', width: '1px', height: '1px', padding: 0, margin: '-1px', overflow: 'hidden', clip: 'rect(0, 0, 0, 0)', whiteSpace: 'nowrap', borderWidth: 0 }}
        tabIndex={-1}
        aria-hidden="true"
      />
      
      {/* Error messages */}
      {!isValid && displayValue && (
        <p className="text-red-500 text-xs mt-1">
          Please enter a valid date in DD/MM/YYYY format
        </p>
      )}
      
      {isValid && violatesMin && (
        <p className="text-red-500 text-xs mt-1">
          Date must be on or after {formatDateForDisplay(min!)}
        </p>
      )}
      
      {isValid && violatesMax && (
        <p className="text-red-500 text-xs mt-1">
          Date must be on or before {formatDateForDisplay(max!)}
        </p>
      )}
    </div>
  )
}