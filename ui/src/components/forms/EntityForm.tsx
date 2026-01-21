/**
 * Generic Entity Form Component
 * Reusable form for creating/editing entities with common fields
 */
import { useState, useEffect, useRef, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllowedStatusTransitions, VALID_TASK_STATUSES } from '../../utils/statusTransitions'

export interface EntityFormData {
  name?: string
  title?: string
  short_description?: string
  long_description?: string
  status?: string
  start_date?: string
  end_date?: string
  due_date?: string
  [key: string]: any
}

interface EntityFormProps {
  initialData?: Partial<EntityFormData>
  onSubmit: (data: EntityFormData) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  entityType?: string
  statusOptions?: string[]
  additionalFields?: React.ReactNode
  currentStatus?: string | null // Current status for filtering transitions (for tasks/subtasks)
  restrictStatusTransitions?: boolean // Whether to restrict status options based on current status
}

const defaultStatusOptions = ['Planning', 'In Progress', 'Completed', 'Blocked', 'In Review', 'On-Hold', 'Canceled']

export default function EntityForm({
  initialData = {},
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  entityType = 'Entity',
  statusOptions = defaultStatusOptions,
  additionalFields,
  currentStatus,
  restrictStatusTransitions = false
}: EntityFormProps) {
  const { t } = useTranslation()
  
  // Determine if we should use 'title' or 'name' based on initialData
  const useTitleField = 'title' in initialData
  
  const [formData, setFormData] = useState<EntityFormData>({
    name: '',
    short_description: '',
    long_description: '',
    status: statusOptions[0],
    start_date: '',
    end_date: '',
    due_date: '',
    ...initialData
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  // Use a ref to track if initialData has actually changed
  const prevInitialDataRef = useRef<string>('')
  
  // Filter status options based on current status if in edit mode and restrictions are enabled
  // Also ensure current status is always included in the options
  const filteredStatusOptions = useMemo(() => {
    // Get all available status options - include current status if it's not in the default list
    const currentStatusValue = currentStatus || initialData?.status
    let allOptions = [...statusOptions]
    
    // If current status exists and is not in the options list, add it
    if (currentStatusValue && !allOptions.includes(currentStatusValue)) {
      allOptions = [currentStatusValue, ...allOptions]
    }
    
    // If restrictions are enabled and we're in edit mode, filter the options
    if (mode === 'edit' && restrictStatusTransitions && currentStatusValue) {
      const allowedTransitions = getAllowedStatusTransitions(currentStatusValue)
      const filtered = allOptions.filter(option => allowedTransitions.includes(option))
      // Always include current status even if filtering
      if (filtered.length > 0) {
        return filtered
      }
    }
    
    return allOptions
  }, [mode, restrictStatusTransitions, currentStatus, initialData?.status, statusOptions])
  
  useEffect(() => {
    const currentInitialDataStr = JSON.stringify(initialData || {})
    if (currentInitialDataStr !== prevInitialDataRef.current && initialData && Object.keys(initialData).length > 0) {
      setFormData(prev => ({ ...prev, ...initialData }))
      prevInitialDataRef.current = currentInitialDataStr
    }
  }, [initialData])
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    // Check either name or title (depending on entity type)
    const displayName = useTitleField ? (formData.title || '') : (formData.name || '')
    if (!displayName || displayName.trim().length === 0) {
      newErrors.name = useTitleField ? 'Title is required' : 'Name is required'
    } else if (displayName.length > 255) {
      newErrors.name = useTitleField ? 'Title must be less than 255 characters' : 'Name must be less than 255 characters'
    }
    
    if (formData.short_description && formData.short_description.length > 500) {
      newErrors.short_description = 'Short description must be less than 500 characters'
    }
    
    if (formData.start_date && formData.end_date) {
      if (new Date(formData.start_date) > new Date(formData.end_date)) {
        newErrors.end_date = 'End date must be after start date'
      }
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    try {
      await onSubmit(formData)
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }
  
  const handleChange = (field: keyof EntityFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name/Title Field */}
      <div>
        <label htmlFor={useTitleField ? 'title' : 'name'} className="block text-sm font-medium mb-2">
          {useTitleField ? 'Title' : 'Name'} <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id={useTitleField ? 'title' : 'name'}
          value={useTitleField ? (formData.title || '') : (formData.name || '')}
          onChange={(e) => {
            if (useTitleField) {
              handleChange('title', e.target.value)
            } else {
              handleChange('name', e.target.value)
            }
          }}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.name 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder={`Enter ${entityType.toLowerCase()} ${useTitleField ? 'title' : 'name'}`}
          disabled={isLoading}
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-500">{errors.name}</p>
        )}
      </div>
      
      {/* Short Description */}
      <div>
        <label htmlFor="short_description" className="block text-sm font-medium mb-2">
          Short Description
        </label>
        <input
          type="text"
          id="short_description"
          value={formData.short_description || ''}
          onChange={(e) => handleChange('short_description', e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.short_description 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="Brief description (max 500 characters)"
          maxLength={500}
          disabled={isLoading}
        />
        {errors.short_description && (
          <p className="mt-1 text-sm text-red-500">{errors.short_description}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          {formData.short_description?.length || 0}/500 characters
        </p>
      </div>
      
      {/* Long Description */}
      <div>
        <label htmlFor="long_description" className="block text-sm font-medium mb-2">
          Description
        </label>
        <textarea
          id="long_description"
          value={formData.long_description || ''}
          onChange={(e) => handleChange('long_description', e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Detailed description"
          disabled={isLoading}
        />
      </div>
      
      {/* Status */}
      <div>
        <label htmlFor="status" className="block text-sm font-medium mb-2">
          Status
          {mode === 'edit' && restrictStatusTransitions && filteredStatusOptions.length < statusOptions.length && (
            <span className="ml-2 text-xs text-gray-500 font-normal">
              (Only valid transitions shown)
            </span>
          )}
        </label>
        <select
          id="status"
          value={formData.status || filteredStatusOptions[0] || statusOptions[0]}
          onChange={(e) => handleChange('status', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        >
          {filteredStatusOptions.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
        {mode === 'edit' && restrictStatusTransitions && filteredStatusOptions.length < statusOptions.length && (
          <p className="mt-1 text-xs text-gray-500">
            Some status options are hidden because they are not valid transitions from the current status.
          </p>
        )}
      </div>
      
      {/* Date Range */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="start_date" className="block text-sm font-medium mb-2">
            Start Date
          </label>
          <input
            type="date"
            id="start_date"
            value={formData.start_date || ''}
            onChange={(e) => handleChange('start_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
        </div>
        
        <div>
          <label htmlFor="end_date" className="block text-sm font-medium mb-2">
            End Date
          </label>
          <input
            type="date"
            id="end_date"
            value={formData.end_date || ''}
            onChange={(e) => handleChange('end_date', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.end_date 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            disabled={isLoading}
          />
          {errors.end_date && (
            <p className="mt-1 text-sm text-red-500">{errors.end_date}</p>
          )}
        </div>
      </div>
      
      {/* Additional Fields */}
      {additionalFields}
      
      {/* Form Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isLoading}
        >
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create' : 'Update'}
        </button>
      </div>
    </form>
  )
}
