/**
 * Task Form Component
 * Form for creating/editing tasks with phase selection and assignee
 */
import { useState, useEffect } from 'react'
import EntityForm, { EntityFormData } from './EntityForm'
import DateInput from '../common/DateInput'
import type { TaskFormData, User } from '../../types/entities'
import api from '../../services/api'

interface TaskFormProps {
  initialData?: Partial<TaskFormData>
  onSubmit: (data: TaskFormData) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  userStoryId?: string
}

const taskStatusOptions = ['Planning', 'In Progress', 'Completed', 'Blocked', 'In Review', 'On-Hold', 'Canceled']
const priorityOptions = ['High', 'Medium', 'Low']

export default function TaskForm({
  initialData = {},
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  userStoryId
}: TaskFormProps) {
  const [users, setUsers] = useState<User[]>([])
  const [loadingData, setLoadingData] = useState(true)
  const [formData, setFormData] = useState<TaskFormData>({
    name: '',
    short_description: '',
    long_description: '',
    status: taskStatusOptions[0],
    user_story_id: userStoryId || '',
    phase_id: '',
    priority: priorityOptions[0],
    assigned_to: '',
    estimated_hours: undefined,
    due_date: '',
    start_date: '',
    end_date: '',
    ...initialData
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  useEffect(() => {
    loadFormData()
  }, [])
  
  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({ ...prev, ...initialData }))
    }
  }, [initialData])
  
  const loadFormData = async () => {
    try {
      setLoadingData(true)
      const usersData = await api.getUsers()
      
      setUsers(usersData.filter((u: User) => u.is_active))
    } catch (error) {
      console.error('Error loading form data:', error)
    } finally {
      setLoadingData(false)
    }
  }
  
  const validateTaskForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.priority) {
      newErrors.priority = 'Priority is required'
    }
    
    if (formData.estimated_hours !== undefined && formData.estimated_hours < 0) {
      newErrors.estimated_hours = 'Estimated hours must be positive'
    }
    
    if (formData.due_date && formData.start_date) {
      if (new Date(formData.start_date) > new Date(formData.due_date)) {
        newErrors.due_date = 'Due date must be after start date'
      }
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }
  
  const handleEntityFormSubmit = async (entityData: EntityFormData) => {
    // Merge entity form data with task-specific data
    const taskData: TaskFormData = {
      ...entityData,
      name: entityData.name || '', // Ensure name is always a string
      user_story_id: formData.user_story_id,
      phase_id: formData.phase_id,
      priority: formData.priority,
      assigned_to: formData.assigned_to || undefined,
      estimated_hours: formData.estimated_hours,
      due_date: formData.due_date || undefined
    }
    
    // Validate task-specific fields
    if (!validateTaskForm()) {
      return
    }
    
    await onSubmit(taskData)
  }
  
  const handleChange = (field: keyof TaskFormData, value: any) => {
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
  
  if (loadingData) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">Loading form data...</div>
      </div>
    )
  }
  
  const additionalFields = (
    <>
      {/* Priority */}
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
          {priorityOptions.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
        {errors.priority && (
          <p className="mt-1 text-sm text-red-500">{errors.priority}</p>
        )}
      </div>
      
      {/* Assignee */}
      <div>
        <label htmlFor="assigned_to" className="block text-sm font-medium mb-2">
          Assigned To
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
              {user.full_name} ({user.role})
            </option>
          ))}
        </select>
      </div>
      
      {/* Estimated Hours and Due Date */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="estimated_hours" className="block text-sm font-medium mb-2">
            Estimated Hours
          </label>
          <input
            type="number"
            id="estimated_hours"
            value={formData.estimated_hours || ''}
            onChange={(e) => handleChange('estimated_hours', e.target.value ? parseFloat(e.target.value) : undefined)}
            min="0"
            step="0.5"
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.estimated_hours 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            placeholder="0.0"
            disabled={isLoading}
          />
          {errors.estimated_hours && (
            <p className="mt-1 text-sm text-red-500">{errors.estimated_hours}</p>
          )}
        </div>
        
        <div>
          <label htmlFor="due_date" className="block text-sm font-medium mb-2">
            Due Date
          </label>
          <DateInput
            value={formData.due_date || ''}
            onChange={(value) => handleChange('due_date', value)}
            min={formData.start_date || undefined}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.due_date 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            disabled={isLoading}
            placeholder="DD/MM/YYYY"
          />
          {errors.due_date && (
            <p className="mt-1 text-sm text-red-500">{errors.due_date}</p>
          )}
        </div>
      </div>
    </>
  )
  
  return (
    <EntityForm
      initialData={formData}
      onSubmit={handleEntityFormSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      mode={mode}
      entityType="Task"
      statusOptions={taskStatusOptions}
      additionalFields={additionalFields}
    />
  )
}
