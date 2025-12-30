/**
 * TODO Item Form Modal Component
 * Requirements: 2.1, 2.5, 3.2, 4.3, 8.7
 * 
 * Provides a form for creating and editing TODO items with:
 * - Title and description fields
 * - Target date selection
 * - Visibility toggle (public/private)
 * - Optional task/subtask linking with search
 * - Form validation
 */

import { useState, useEffect } from 'react'
import Modal from '../common/Modal'
import type { TodoItem, CreateTodoItemRequest, TodoEntityType } from '../../types/todo'
import { createTodoItem, updateTodoItem } from '../../services/todoApi'
import api from '../../services/api'

interface TodoItemFormModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  item?: TodoItem // If provided, edit mode; otherwise create mode
  initialDate?: string // Initial target date for new items
}

interface FormData {
  title: string
  description: string
  target_date: string
  visibility: 'public' | 'private'
  linked_entity_type: TodoEntityType | ''
  linked_entity_id: string
}

interface FormErrors {
  title?: string
  description?: string
  target_date?: string
  linked_entity_id?: string
  submit?: string
}

interface EntityOption {
  id: string
  title: string
  type: 'task' | 'subtask'
}

export default function TodoItemFormModal({
  isOpen,
  onClose,
  onSuccess,
  item,
  initialDate
}: TodoItemFormModalProps) {
  const isEditMode = !!item

  // Form state
  const [formData, setFormData] = useState<FormData>({
    title: '',
    description: '',
    target_date: initialDate || new Date().toISOString().split('T')[0], // Use initialDate or today's date
    visibility: 'private',
    linked_entity_type: '',
    linked_entity_id: ''
  })

  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Entity search state
  const [entitySearchQuery, setEntitySearchQuery] = useState('')
  const [entityOptions, setEntityOptions] = useState<EntityOption[]>([])
  const [isLoadingEntities, setIsLoadingEntities] = useState(false)
  const [showEntityDropdown, setShowEntityDropdown] = useState(false)

  // Initialize form data when modal opens or item changes
  useEffect(() => {
    if (isOpen) {
      if (item) {
        // Edit mode - populate with existing data
        setFormData({
          title: item.title,
          description: item.description || '',
          target_date: item.target_date,
          visibility: item.visibility,
          linked_entity_type: item.linked_entity_type || '',
          linked_entity_id: item.linked_entity_id || ''
        })
        
        // Set search query to linked entity title if available
        if (item.linked_entity_info) {
          setEntitySearchQuery(item.linked_entity_info.title)
        }
      } else {
        // Create mode - reset to defaults
        setFormData({
          title: '',
          description: '',
          target_date: initialDate || new Date().toISOString().split('T')[0],
          visibility: 'private',
          linked_entity_type: '',
          linked_entity_id: ''
        })
        setEntitySearchQuery('')
      }
      setErrors({})
      setEntityOptions([])
      setShowEntityDropdown(false)
    }
  }, [isOpen, item, initialDate])

  // Load tasks and subtasks for entity search
  useEffect(() => {
    if (entitySearchQuery.length >= 2) {
      loadEntityOptions()
    } else {
      setEntityOptions([])
      setShowEntityDropdown(false)
    }
  }, [entitySearchQuery])

  const loadEntityOptions = async () => {
    setIsLoadingEntities(true)
    try {
      // Fetch both tasks and subtasks
      const [tasks, subtasks] = await Promise.all([
        api.getTasks(),
        api.getSubtasks()
      ])

      // Filter and map to entity options
      const query = entitySearchQuery.toLowerCase()
      
      const taskOptions: EntityOption[] = tasks
        .filter((task: any) => 
          task.title?.toLowerCase().includes(query) ||
          task.name?.toLowerCase().includes(query)
        )
        .slice(0, 10) // Limit to 10 results
        .map((task: any) => ({
          id: task.id,
          title: task.title || task.name,
          type: 'task' as const
        }))

      const subtaskOptions: EntityOption[] = subtasks
        .filter((subtask: any) => 
          subtask.title?.toLowerCase().includes(query) ||
          subtask.name?.toLowerCase().includes(query)
        )
        .slice(0, 10) // Limit to 10 results
        .map((subtask: any) => ({
          id: subtask.id,
          title: subtask.title || subtask.name,
          type: 'subtask' as const
        }))

      setEntityOptions([...taskOptions, ...subtaskOptions])
      setShowEntityDropdown(true)
    } catch (error) {
      console.error('Error loading entity options:', error)
      setEntityOptions([])
    } finally {
      setIsLoadingEntities(false)
    }
  }

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    
    // Clear error for this field
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }))
    }
  }

  const handleEntitySearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setEntitySearchQuery(value)
    
    // Clear linked entity if search is cleared
    if (!value) {
      setFormData(prev => ({
        ...prev,
        linked_entity_type: '',
        linked_entity_id: ''
      }))
    }
  }

  const handleEntitySelect = (entity: EntityOption) => {
    setFormData(prev => ({
      ...prev,
      linked_entity_type: entity.type,
      linked_entity_id: entity.id
    }))
    setEntitySearchQuery(entity.title)
    setShowEntityDropdown(false)
    
    // Clear any previous error
    if (errors.linked_entity_id) {
      setErrors(prev => ({ ...prev, linked_entity_id: undefined }))
    }
  }

  const handleClearEntity = () => {
    setFormData(prev => ({
      ...prev,
      linked_entity_type: '',
      linked_entity_id: ''
    }))
    setEntitySearchQuery('')
    setShowEntityDropdown(false)
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    // Title validation (required, max 255 chars)
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    } else if (formData.title.length > 255) {
      newErrors.title = 'Title must be 255 characters or less'
    }

    // Description validation (max 2000 chars)
    if (formData.description && formData.description.length > 2000) {
      newErrors.description = 'Description must be 2000 characters or less'
    }

    // Target date validation
    if (!formData.target_date) {
      newErrors.target_date = 'Target date is required'
    }

    // Linked entity validation (if entity type is set, ID must be set)
    if (formData.linked_entity_type && !formData.linked_entity_id) {
      newErrors.linked_entity_id = 'Please select a task or subtask from the dropdown'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    setErrors({})

    try {
      // Prepare request data
      const requestData: CreateTodoItemRequest = {
        title: formData.title.trim(),
        description: formData.description.trim() || undefined,
        target_date: formData.target_date,
        visibility: formData.visibility,
        linked_entity_type: formData.linked_entity_type || undefined,
        linked_entity_id: formData.linked_entity_id || undefined
      }

      if (isEditMode && item) {
        // Update existing TODO item
        await updateTodoItem(item.id, requestData)
      } else {
        // Create new TODO item
        await createTodoItem(requestData)
      }

      // Success - close modal and refresh
      onSuccess()
      onClose()
    } catch (error: any) {
      console.error('Error saving TODO item:', error)
      
      // Handle validation errors from API
      if (error.response?.data?.detail) {
        setErrors({ submit: error.response.data.detail })
      } else if (error.response?.data?.field_errors) {
        setErrors(error.response.data.field_errors)
      } else {
        setErrors({ submit: 'Failed to save TODO item. Please try again.' })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditMode ? 'Edit TODO Item' : 'Create TODO Item'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title Field */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
              errors.title ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Enter TODO item title"
            maxLength={255}
            disabled={isSubmitting}
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            {formData.title.length}/255 characters
          </p>
        </div>

        {/* Description Field */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows={4}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
              errors.description ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Enter detailed description (optional)"
            maxLength={2000}
            disabled={isSubmitting}
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            {formData.description.length}/2000 characters
          </p>
        </div>

        {/* Target Date Field */}
        <div>
          <label htmlFor="target_date" className="block text-sm font-medium text-gray-700 mb-1">
            Target Date <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            id="target_date"
            name="target_date"
            value={formData.target_date}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
              errors.target_date ? 'border-red-500' : 'border-gray-300'
            }`}
            disabled={isSubmitting}
          />
          {errors.target_date && (
            <p className="mt-1 text-sm text-red-600">{errors.target_date}</p>
          )}
        </div>

        {/* Visibility Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Visibility
          </label>
          <div className="flex gap-4">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="visibility"
                value="private"
                checked={formData.visibility === 'private'}
                onChange={handleInputChange}
                className="mr-2 text-indigo-600 focus:ring-indigo-500"
                disabled={isSubmitting}
              />
              <span className="text-sm text-gray-700">
                Private (only you can see)
              </span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="visibility"
                value="public"
                checked={formData.visibility === 'public'}
                onChange={handleInputChange}
                className="mr-2 text-indigo-600 focus:ring-indigo-500"
                disabled={isSubmitting}
              />
              <span className="text-sm text-gray-700">
                Public (visible to team)
              </span>
            </label>
          </div>
        </div>

        {/* Link to Task/Subtask Field */}
        <div className="relative">
          <label htmlFor="entity_search" className="block text-sm font-medium text-gray-700 mb-1">
            Link to Task/Subtask (Optional)
          </label>
          <div className="relative">
            <input
              type="text"
              id="entity_search"
              value={entitySearchQuery}
              onChange={handleEntitySearchChange}
              onFocus={() => entityOptions.length > 0 && setShowEntityDropdown(true)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                errors.linked_entity_id ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Search for a task or subtask..."
              disabled={isSubmitting}
              autoComplete="off"
            />
            {formData.linked_entity_id && (
              <button
                type="button"
                onClick={handleClearEntity}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                disabled={isSubmitting}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
          
          {/* Dropdown with search results */}
          {showEntityDropdown && entityOptions.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
              {entityOptions.map((entity) => (
                <button
                  key={`${entity.type}-${entity.id}`}
                  type="button"
                  onClick={() => handleEntitySelect(entity)}
                  className="w-full px-3 py-2 text-left hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-900">{entity.title}</span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      entity.type === 'task' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-purple-100 text-purple-800'
                    }`}>
                      {entity.type}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
          
          {/* Loading indicator */}
          {isLoadingEntities && (
            <p className="mt-1 text-xs text-gray-500">Searching...</p>
          )}
          
          {/* No results message */}
          {entitySearchQuery.length >= 2 && !isLoadingEntities && entityOptions.length === 0 && (
            <p className="mt-1 text-xs text-gray-500">No tasks or subtasks found</p>
          )}
          
          {/* Selected entity indicator */}
          {formData.linked_entity_id && (
            <p className="mt-1 text-xs text-green-600">
              ✓ Linked to {formData.linked_entity_type}: {entitySearchQuery}
            </p>
          )}
          
          {errors.linked_entity_id && (
            <p className="mt-1 text-sm text-red-600">{errors.linked_entity_id}</p>
          )}
          
          <p className="mt-1 text-xs text-gray-500">
            Type at least 2 characters to search for tasks or subtasks
          </p>
        </div>

        {/* Submit Error */}
        {errors.submit && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}

        {/* Form Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Saving...' : isEditMode ? 'Update' : 'Create'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
