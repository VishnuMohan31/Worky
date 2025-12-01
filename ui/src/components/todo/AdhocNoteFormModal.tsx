/**
 * ADHOC Note Form Modal Component
 * Requirements: 5.3
 * 
 * Provides a form for creating and editing ADHOC notes with:
 * - Title and content fields
 * - Color picker for note customization
 * - Form validation
 * - Create and edit modes
 */

import { useState, useEffect } from 'react'
import Modal from '../common/Modal'
import type { AdhocNote, CreateAdhocNoteRequest } from '../../types/todo'
import { ADHOC_NOTE_COLORS } from '../../types/todo'
import { createAdhocNote, updateAdhocNote } from '../../services/todoApi'

interface AdhocNoteFormModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  note?: AdhocNote // If provided, edit mode; otherwise create mode
}

interface FormData {
  title: string
  content: string
  color: string
}

interface FormErrors {
  title?: string
  content?: string
  submit?: string
}

export default function AdhocNoteFormModal({
  isOpen,
  onClose,
  onSuccess,
  note
}: AdhocNoteFormModalProps) {
  const isEditMode = !!note

  // Form state
  const [formData, setFormData] = useState<FormData>({
    title: '',
    content: '',
    color: ADHOC_NOTE_COLORS[0] // Default yellow
  })

  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Initialize form data when modal opens or note changes
  useEffect(() => {
    if (isOpen) {
      if (note) {
        // Edit mode - populate with existing data
        setFormData({
          title: note.title,
          content: note.content || '',
          color: note.color
        })
      } else {
        // Create mode - reset to defaults
        setFormData({
          title: '',
          content: '',
          color: ADHOC_NOTE_COLORS[0]
        })
      }
      setErrors({})
    }
  }, [isOpen, note])

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    
    // Clear error for this field
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }))
    }
  }

  const handleColorSelect = (color: string) => {
    setFormData(prev => ({ ...prev, color }))
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    // Title validation (required, max 255 chars)
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    } else if (formData.title.length > 255) {
      newErrors.title = 'Title must be 255 characters or less'
    }

    // Content validation (max 2000 chars)
    if (formData.content && formData.content.length > 2000) {
      newErrors.content = 'Content must be 2000 characters or less'
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
      const requestData: CreateAdhocNoteRequest = {
        title: formData.title.trim(),
        content: formData.content.trim() || undefined,
        color: formData.color
      }

      if (isEditMode && note) {
        // Update existing ADHOC note
        await updateAdhocNote(note.id, requestData)
      } else {
        // Create new ADHOC note
        await createAdhocNote(requestData)
      }

      // Success - close modal and refresh
      onSuccess()
      onClose()
    } catch (error: any) {
      console.error('Error saving ADHOC note:', error)
      
      // Handle validation errors from API
      if (error.response?.data?.detail) {
        setErrors({ submit: error.response.data.detail })
      } else if (error.response?.data?.field_errors) {
        setErrors(error.response.data.field_errors)
      } else {
        setErrors({ submit: 'Failed to save ADHOC note. Please try again.' })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditMode ? 'Edit ADHOC Note' : 'Create ADHOC Note'}
      size="md"
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
            placeholder="Enter note title"
            maxLength={255}
            disabled={isSubmitting}
            autoFocus
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            {formData.title.length}/255 characters
          </p>
        </div>

        {/* Content Field */}
        <div>
          <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
            Content
          </label>
          <textarea
            id="content"
            name="content"
            value={formData.content}
            onChange={handleInputChange}
            rows={6}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
              errors.content ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Enter note content (optional)"
            maxLength={2000}
            disabled={isSubmitting}
          />
          {errors.content && (
            <p className="mt-1 text-sm text-red-600">{errors.content}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            {formData.content.length}/2000 characters
          </p>
        </div>

        {/* Color Picker */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Note Color
          </label>
          <div className="grid grid-cols-8 gap-2">
            {ADHOC_NOTE_COLORS.map((color) => (
              <button
                key={color}
                type="button"
                onClick={() => handleColorSelect(color)}
                className={`w-10 h-10 rounded-md border-2 transition-all hover:scale-110 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
                  formData.color === color
                    ? 'border-indigo-600 ring-2 ring-indigo-600 ring-offset-2 scale-110'
                    : 'border-gray-300'
                }`}
                style={{ backgroundColor: color }}
                disabled={isSubmitting}
                aria-label={`Select color ${color}`}
                title={color}
              >
                {formData.color === color && (
                  <svg
                    className="w-6 h-6 mx-auto text-gray-800"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </button>
            ))}
          </div>
          <p className="mt-2 text-xs text-gray-500">
            Selected color: {formData.color}
          </p>
        </div>

        {/* Preview */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Preview
          </label>
          <div
            className="p-4 rounded-md shadow-md border border-gray-200"
            style={{ backgroundColor: formData.color }}
          >
            <h3 className="font-semibold text-gray-900 mb-2">
              {formData.title || 'Note title...'}
            </h3>
            <p className="text-sm text-gray-800 whitespace-pre-wrap">
              {formData.content || 'Note content...'}
            </p>
          </div>
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
