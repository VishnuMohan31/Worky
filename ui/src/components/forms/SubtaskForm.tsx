/**
 * Subtask Form Component
 * Form for creating/editing subtasks with validation
 */
import { useState, useEffect } from 'react'
import type { SubtaskFormData, Task, Phase, User } from '../../types/entities'

interface SubtaskFormProps {
  initialData?: Partial<SubtaskFormData>
  onSubmit: (data: SubtaskFormData) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  taskId?: string
  tasks?: Task[]
  users?: User[]
  phases?: Phase[]
}

const subtaskStatusOptions = ['To Do', 'In Progress', 'Done', 'Blocked']

export default function SubtaskForm({
  initialData = {},
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  taskId,
  tasks = [],
  users = [],
  phases = []
}: SubtaskFormProps) {
  const [formData, setFormData] = useState<SubtaskFormData>({
    name: '',
    task_id: taskId || '',
    short_description: '',
    long_description: '',
    status: subtaskStatusOptions[0],
    phase_id: '',
    assigned_to: '',
    estimated_hours: 0,
    duration_days: 1,
    scrum_points: undefined,
    ...initialData
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({ ...prev, ...initialData }))
    }
  }, [initialData])
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    // Validate Name (required)
    if (!formData.name || formData.name.trim().length === 0) {
      newErrors.name = 'This field is required'
    }
    
    // Validate Task ID (required)
    if (!formData.task_id) {
      newErrors.task_id = 'This field is required'
    }
    
    // Validate Estimated Hours (required, must be positive)
    if (formData.estimated_hours === undefined || formData.estimated_hours === null) {
      newErrors.estimated_hours = 'This field is required'
    } else if (formData.estimated_hours < 0) {
      newErrors.estimated_hours = 'Must be a positive number'
    }
    
    // Validate Duration Days (required, must be at least 1)
    if (formData.duration_days === undefined || formData.duration_days === null) {
      newErrors.duration_days = 'This field is required'
    } else if (formData.duration_days < 1) {
      newErrors.duration_days = 'Must be at least 1 day'
    } else if (!Number.isInteger(formData.duration_days)) {
      newErrors.duration_days = 'Must be a whole number'
    }
    
    // Validate Scrum Points (optional, but must be non-negative if provided)
    if (formData.scrum_points !== undefined && formData.scrum_points !== null && formData.scrum_points < 0) {
      newErrors.scrum_points = 'Must be a non-negative number'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (field: keyof SubtaskFormData, value: any) => {
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
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    try {
      await onSubmit(formData)
      // Reset form on successful submission
      setFormData({
        name: '',
        task_id: taskId || '',
        short_description: '',
        long_description: '',
        status: subtaskStatusOptions[0],
        phase_id: '',
        assigned_to: '',
        estimated_hours: 0,
        duration_days: 1,
        scrum_points: undefined
      })
      setErrors({})
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }
  
  const handleCancel = () => {
    setErrors({})
    onCancel()
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
      {/* Name Field */}
      <div>
        <label htmlFor="name" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
          Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          className={`w-full px-3 py-2 text-sm sm:text-base border rounded-lg focus:outline-none focus:ring-2 ${
            errors.name 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="Enter subtask name"
          disabled={isLoading}
        />
        {errors.name && (
          <p className="mt-1 text-xs sm:text-sm text-red-500">{errors.name}</p>
        )}
      </div>
      
      {/* Task Dropdown */}
      <div>
        <label htmlFor="task_id" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
          Task <span className="text-red-500">*</span>
        </label>
        <select
          id="task_id"
          value={formData.task_id}
          onChange={(e) => handleChange('task_id', e.target.value)}
          className={`w-full px-3 py-2 text-sm sm:text-base border rounded-lg focus:outline-none focus:ring-2 ${
            errors.task_id 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          disabled={isLoading || !!taskId}
        >
          <option value="">Select a task</option>
          {tasks.map(task => (
            <option key={task.id} value={task.id}>
              {task.name}
            </option>
          ))}
        </select>
        {errors.task_id && (
          <p className="mt-1 text-xs sm:text-sm text-red-500">{errors.task_id}</p>
        )}
      </div>
      
      {/* Short Description Textarea */}
      <div>
        <label htmlFor="short_description" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
          Short Description <span className="text-xs text-gray-500">(Search keywords, summary)</span>
        </label>
        <textarea
          id="short_description"
          value={formData.short_description || ''}
          onChange={(e) => handleChange('short_description', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Brief summary with key search terms..."
          disabled={isLoading}
        />
      </div>

      {/* Long Description Textarea */}
      <div>
        <label htmlFor="long_description" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
          Long Description <span className="text-xs text-gray-500">(Detailed explanation)</span>
        </label>
        <textarea
          id="long_description"
          value={formData.long_description || ''}
          onChange={(e) => handleChange('long_description', e.target.value)}
          rows={4}
          className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Detailed explanation of the subtask..."
          disabled={isLoading}
        />
      </div>
      
      {/* Status and Phase - Two Column Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        {/* Status Dropdown */}
        <div>
          <label htmlFor="status" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
            Status <span className="text-red-500">*</span>
          </label>
          <select
            id="status"
            value={formData.status}
            onChange={(e) => handleChange('status', e.target.value)}
            className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            {subtaskStatusOptions.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        
        {/* Phase Dropdown */}
        <div>
          <label htmlFor="phase_id" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
            Phase
          </label>
          <select
            id="phase_id"
            value={formData.phase_id || ''}
            onChange={(e) => handleChange('phase_id', e.target.value)}
            className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            <option value="">Select a phase</option>
            {phases.map(phase => (
              <option key={phase.id} value={phase.id}>
                {phase.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Assigned To Dropdown */}
      <div>
        <label htmlFor="assigned_to" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
          Assigned To
        </label>
        <select
          id="assigned_to"
          value={formData.assigned_to || ''}
          onChange={(e) => handleChange('assigned_to', e.target.value)}
          className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        >
          <option value="">Unassigned</option>
          {users.map(user => (
            <option key={user.id} value={user.id}>
              {user.full_name} ({user.role})
            </option>
          ))}
        </select>
      </div>
      
      {/* Estimated Hours and Duration Days - Two Column Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        {/* Estimated Hours */}
        <div>
          <label htmlFor="estimated_hours" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
            Estimated Hours <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="estimated_hours"
            value={formData.estimated_hours}
            onChange={(e) => handleChange('estimated_hours', e.target.value ? parseFloat(e.target.value) : 0)}
            min="0"
            step="0.5"
            className={`w-full px-3 py-2 text-sm sm:text-base border rounded-lg focus:outline-none focus:ring-2 ${
              errors.estimated_hours 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            placeholder="0.0"
            disabled={isLoading}
          />
          {errors.estimated_hours && (
            <p className="mt-1 text-xs sm:text-sm text-red-500">{errors.estimated_hours}</p>
          )}
        </div>
        
        {/* Duration Days */}
        <div>
          <label htmlFor="duration_days" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
            Duration Days <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="duration_days"
            value={formData.duration_days}
            onChange={(e) => handleChange('duration_days', e.target.value ? parseInt(e.target.value) : 1)}
            min="1"
            step="1"
            className={`w-full px-3 py-2 text-sm sm:text-base border rounded-lg focus:outline-none focus:ring-2 ${
              errors.duration_days 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            placeholder="1"
            disabled={isLoading}
          />
          {errors.duration_days && (
            <p className="mt-1 text-xs sm:text-sm text-red-500">{errors.duration_days}</p>
          )}
        </div>
      </div>
      
      {/* Scrum Points */}
      <div>
        <label htmlFor="scrum_points" className="block text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-gray-700">
          Scrum Points
        </label>
        <input
          type="number"
          id="scrum_points"
          value={formData.scrum_points || ''}
          onChange={(e) => handleChange('scrum_points', e.target.value ? parseFloat(e.target.value) : undefined)}
          min="0"
          step="0.5"
          className={`w-full px-3 py-2 text-sm sm:text-base border rounded-lg focus:outline-none focus:ring-2 ${
            errors.scrum_points 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="Optional"
          disabled={isLoading}
        />
        {errors.scrum_points && (
          <p className="mt-1 text-xs sm:text-sm text-red-500">{errors.scrum_points}</p>
        )}
      </div>
      
      {/* Form Actions */}
      <div className="flex flex-col-reverse sm:flex-row justify-end gap-2 sm:gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={handleCancel}
          className="w-full sm:w-auto px-4 py-2 text-sm sm:text-base text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="w-full sm:w-auto px-4 py-2 text-sm sm:text-base text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isLoading}
        >
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create' : 'Update'}
        </button>
      </div>
    </form>
  )
}
