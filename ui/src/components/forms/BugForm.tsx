/**
 * BugForm Component
 * Form for creating and editing bugs
 */
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { BugFormData, SEVERITY_OPTIONS } from '../../types/entities'
import api from '../../services/api'

interface BugFormProps {
  initialData?: Partial<BugFormData>
  onSubmit: (data: BugFormData) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

const PRIORITY_OPTIONS = ['P0', 'P1', 'P2', 'P3']
const ENTITY_TYPE_OPTIONS = ['Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask']

export default function BugForm({
  initialData = {},
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create'
}: BugFormProps) {
  const { t } = useTranslation()
  
  const [formData, setFormData] = useState<BugFormData>({
    entity_type: '',
    entity_id: '',
    title: '',
    short_description: '',
    long_description: '',
    severity: 'Medium',
    priority: 'P2',
    assigned_to: '',
    ...initialData
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [users, setUsers] = useState<any[]>([])
  
  useEffect(() => {
    loadUsers()
  }, [])
  
  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({ ...prev, ...initialData }))
    }
  }, [initialData])
  
  const loadUsers = async () => {
    try {
      const data = await api.getUsers()
      setUsers(data)
    } catch (error) {
      console.error('Failed to load users:', error)
    }
  }
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.entity_type) {
      newErrors.entity_type = 'Entity type is required'
    }
    
    if (!formData.entity_id) {
      newErrors.entity_id = 'Entity ID is required'
    }
    
    if (!formData.title || formData.title.trim().length === 0) {
      newErrors.title = 'Title is required'
    } else if (formData.title.length > 255) {
      newErrors.title = 'Title must be less than 255 characters'
    }
    
    if (!formData.long_description || formData.long_description.trim().length === 0) {
      newErrors.long_description = 'Description is required'
    }
    
    if (!formData.severity) {
      newErrors.severity = 'Severity is required'
    }
    
    if (!formData.priority) {
      newErrors.priority = 'Priority is required'
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
  
  const handleChange = (field: keyof BugFormData, value: any) => {
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
      {/* Entity Association */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="entity_type" className="block text-sm font-medium mb-2">
            Entity Type <span className="text-red-500">*</span>
          </label>
          <select
            id="entity_type"
            value={formData.entity_type}
            onChange={(e) => handleChange('entity_type', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.entity_type 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            disabled={isLoading || !!initialData.entity_type}
          >
            <option value="">Select entity type</option>
            {ENTITY_TYPE_OPTIONS.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
          {errors.entity_type && (
            <p className="mt-1 text-sm text-red-500">{errors.entity_type}</p>
          )}
        </div>
        
        <div>
          <label htmlFor="entity_id" className="block text-sm font-medium mb-2">
            Entity ID <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="entity_id"
            value={formData.entity_id}
            onChange={(e) => handleChange('entity_id', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.entity_id 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            placeholder="Enter entity ID"
            disabled={isLoading || !!initialData.entity_id}
          />
          {errors.entity_id && (
            <p className="mt-1 text-sm text-red-500">{errors.entity_id}</p>
          )}
        </div>
      </div>
      
      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-2">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          value={formData.title}
          onChange={(e) => handleChange('title', e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.title 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="Enter bug title"
          disabled={isLoading}
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-500">{errors.title}</p>
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
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Brief description (max 500 characters)"
          maxLength={500}
          disabled={isLoading}
        />
        <p className="mt-1 text-xs text-gray-500">
          {formData.short_description?.length || 0}/500 characters
        </p>
      </div>
      
      {/* Description */}
      <div>
        <label htmlFor="long_description" className="block text-sm font-medium mb-2">
          Description <span className="text-red-500">*</span>
        </label>
        <textarea
          id="long_description"
          value={formData.long_description || ''}
          onChange={(e) => handleChange('long_description', e.target.value)}
          rows={6}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.long_description 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="Detailed description of the bug, including steps to reproduce"
          disabled={isLoading}
        />
        {errors.long_description && (
          <p className="mt-1 text-sm text-red-500">{errors.long_description}</p>
        )}
      </div>
      
      {/* Severity and Priority */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="severity" className="block text-sm font-medium mb-2">
            Severity <span className="text-red-500">*</span>
          </label>
          <select
            id="severity"
            value={formData.severity}
            onChange={(e) => handleChange('severity', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.severity 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            disabled={isLoading}
          >
            {SEVERITY_OPTIONS.map(severity => (
              <option key={severity} value={severity}>{severity}</option>
            ))}
          </select>
          {errors.severity && (
            <p className="mt-1 text-sm text-red-500">{errors.severity}</p>
          )}
        </div>
        
        <div>
          <label htmlFor="priority" className="block text-sm font-medium mb-2">
            Priority <span className="text-red-500">*</span>
          </label>
          <select
            id="priority"
            value={formData.priority}
            onChange={(e) => handleChange('priority', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.priority 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            disabled={isLoading}
          >
            {PRIORITY_OPTIONS.map(priority => (
              <option key={priority} value={priority}>{priority}</option>
            ))}
          </select>
          {errors.priority && (
            <p className="mt-1 text-sm text-red-500">{errors.priority}</p>
          )}
        </div>
      </div>
      
      {/* Assignee */}
      <div>
        <label htmlFor="assigned_to" className="block text-sm font-medium mb-2">
          Assign To
        </label>
        <select
          id="assigned_to"
          value={formData.assigned_to || ''}
          onChange={(e) => handleChange('assigned_to', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        >
          <option value="">Unassigned</option>
          {users.map(user => (
            <option key={user.id} value={user.id}>
              {user.fullName || user.full_name} ({user.role})
            </option>
          ))}
        </select>
      </div>
      
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
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Bug' : 'Update Bug'}
        </button>
      </div>
    </form>
  )
}
