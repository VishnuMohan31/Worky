/**
 * BugForm Component
 * Form for creating and editing bugs
 * Enhanced with hierarchy selector, bug type, environment fields, version fields, assignee, and test case link
 * Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
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

const PRIORITY_OPTIONS = ['P1', 'P2', 'P3', 'P4']
const ENTITY_TYPE_OPTIONS = ['Client', 'Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask']
const BUG_CATEGORY_OPTIONS = ['UI', 'Backend', 'Database', 'Integration', 'Performance', 'Security', 'Environment']
const BUG_TYPE_OPTIONS = ['Functional', 'Performance', 'Security', 'UI/UX', 'Data', 'Integration', 'Configuration']
const BROWSER_OPTIONS = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'Other']
const OS_OPTIONS = ['Windows', 'macOS', 'Linux', 'iOS', 'Android', 'Other']
const DEVICE_TYPE_OPTIONS = ['Desktop', 'Mobile', 'Tablet', 'Other']

export default function BugForm({
  initialData = {},
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create'
}: BugFormProps) {
  const { t } = useTranslation()
  
  const [formData, setFormData] = useState<any>({
    entity_type: '',
    entity_id: '',
    title: '',
    short_description: '',
    long_description: '',
    severity: 'Medium',
    priority: 'P2',
    category: '',
    assigned_to: '',
    qa_owner_id: '',
    bug_type: '',
    reproduction_steps: '',
    expected_result: '',
    actual_result: '',
    component_attached_to: '',
    linked_task_id: '',
    linked_commit: '',
    linked_pr: '',
    browser: '',
    os: '',
    device_type: '',
    found_in_version: '',
    fixed_in_version: '',
    test_case_id: '',
    ...initialData
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [users, setUsers] = useState<any[]>([])
  const [testCases, setTestCases] = useState<any[]>([])
  
  useEffect(() => {
    loadUsers()
    loadTestCases()
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
  
  const loadTestCases = async () => {
    try {
      const data = await api.get('/test-cases/')
      setTestCases(data)
    } catch (error) {
      console.error('Failed to load test cases:', error)
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
    
    if (!formData.category) {
      newErrors.category = 'Category is required'
    }
    
    if (!formData.reproduction_steps || formData.reproduction_steps.trim().length === 0) {
      newErrors.reproduction_steps = 'Reproduction steps are required'
    }
    
    if (!formData.expected_result || formData.expected_result.trim().length === 0) {
      newErrors.expected_result = 'Expected result is required'
    }
    
    if (!formData.actual_result || formData.actual_result.trim().length === 0) {
      newErrors.actual_result = 'Actual result is required'
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
      
      {/* Category */}
      <div>
        <label htmlFor="category" className="block text-sm font-medium mb-2">
          Category <span className="text-red-500">*</span>
        </label>
        <select
          id="category"
          value={formData.category || ''}
          onChange={(e) => handleChange('category', e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.category 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          disabled={isLoading}
        >
          <option value="">Select category</option>
          {BUG_CATEGORY_OPTIONS.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
        {errors.category && (
          <p className="mt-1 text-sm text-red-500">{errors.category}</p>
        )}
      </div>
      
      {/* Assignee and QA Owner */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="assigned_to" className="block text-sm font-medium mb-2">
            Assignee (Developer)
          </label>
          <select
            id="assigned_to"
            value={formData.assigned_to || ''}
            onChange={(e) => handleChange('assigned_to', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            <option value="">Unassigned</option>
            {users.filter(u => u.role === 'Developer' || u.role === 'Architect').map(user => (
              <option key={user.id} value={user.id}>
                {user.fullName || user.full_name}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label htmlFor="qa_owner_id" className="block text-sm font-medium mb-2">
            QA Owner
          </label>
          <select
            id="qa_owner_id"
            value={formData.qa_owner_id || ''}
            onChange={(e) => handleChange('qa_owner_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            <option value="">Unassigned</option>
            {users.filter(u => u.role === 'Tester' || u.role === 'Admin').map(user => (
              <option key={user.id} value={user.id}>
                {user.fullName || user.full_name}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Reproduction Steps */}
      <div>
        <label htmlFor="reproduction_steps" className="block text-sm font-medium mb-2">
          Reproduction Steps <span className="text-red-500">*</span>
        </label>
        <textarea
          id="reproduction_steps"
          value={formData.reproduction_steps || ''}
          onChange={(e) => handleChange('reproduction_steps', e.target.value)}
          rows={5}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.reproduction_steps 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="1. Step one&#10;2. Step two&#10;3. Step three"
          disabled={isLoading}
        />
        {errors.reproduction_steps && (
          <p className="mt-1 text-sm text-red-500">{errors.reproduction_steps}</p>
        )}
      </div>
      
      {/* Expected and Actual Results */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="expected_result" className="block text-sm font-medium mb-2">
            Expected Result <span className="text-red-500">*</span>
          </label>
          <textarea
            id="expected_result"
            value={formData.expected_result || ''}
            onChange={(e) => handleChange('expected_result', e.target.value)}
            rows={4}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.expected_result 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            placeholder="What should happen..."
            disabled={isLoading}
          />
          {errors.expected_result && (
            <p className="mt-1 text-sm text-red-500">{errors.expected_result}</p>
          )}
        </div>
        
        <div>
          <label htmlFor="actual_result" className="block text-sm font-medium mb-2">
            Actual Result <span className="text-red-500">*</span>
          </label>
          <textarea
            id="actual_result"
            value={formData.actual_result || ''}
            onChange={(e) => handleChange('actual_result', e.target.value)}
            rows={4}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.actual_result 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            placeholder="What actually happens..."
            disabled={isLoading}
          />
          {errors.actual_result && (
            <p className="mt-1 text-sm text-red-500">{errors.actual_result}</p>
          )}
        </div>
      </div>
      
      {/* Component Attached To */}
      <div>
        <label htmlFor="component_attached_to" className="block text-sm font-medium mb-2">
          Component Attached To
        </label>
        <input
          type="text"
          id="component_attached_to"
          value={formData.component_attached_to || ''}
          onChange={(e) => handleChange('component_attached_to', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., Login Module, Payment API, User Dashboard"
          disabled={isLoading}
        />
      </div>
      
      {/* Bug Type */}
      <div>
        <label htmlFor="bug_type" className="block text-sm font-medium mb-2">
          Bug Type
        </label>
        <select
          id="bug_type"
          value={formData.bug_type || ''}
          onChange={(e) => handleChange('bug_type', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        >
          <option value="">Select bug type</option>
          {BUG_TYPE_OPTIONS.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>
      
      {/* Environment Fields */}
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label htmlFor="browser" className="block text-sm font-medium mb-2">
            Browser
          </label>
          <select
            id="browser"
            value={formData.browser || ''}
            onChange={(e) => handleChange('browser', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            <option value="">Select browser</option>
            {BROWSER_OPTIONS.map(browser => (
              <option key={browser} value={browser}>{browser}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label htmlFor="os" className="block text-sm font-medium mb-2">
            Operating System
          </label>
          <select
            id="os"
            value={formData.os || ''}
            onChange={(e) => handleChange('os', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            <option value="">Select OS</option>
            {OS_OPTIONS.map(os => (
              <option key={os} value={os}>{os}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label htmlFor="device_type" className="block text-sm font-medium mb-2">
            Device Type
          </label>
          <select
            id="device_type"
            value={formData.device_type || ''}
            onChange={(e) => handleChange('device_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            <option value="">Select device type</option>
            {DEVICE_TYPE_OPTIONS.map(device => (
              <option key={device} value={device}>{device}</option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Version Fields */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="found_in_version" className="block text-sm font-medium mb-2">
            Found in Version
          </label>
          <input
            type="text"
            id="found_in_version"
            value={formData.found_in_version || ''}
            onChange={(e) => handleChange('found_in_version', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 1.2.3"
            disabled={isLoading}
          />
        </div>
        
        <div>
          <label htmlFor="fixed_in_version" className="block text-sm font-medium mb-2">
            Fixed in Version
          </label>
          <input
            type="text"
            id="fixed_in_version"
            value={formData.fixed_in_version || ''}
            onChange={(e) => handleChange('fixed_in_version', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 1.2.4"
            disabled={isLoading}
          />
        </div>
      </div>
      
      {/* Linked Items */}
      <div className="border-t pt-4">
        <h3 className="text-md font-semibold text-gray-900 mb-3">Linked Items</h3>
        
        <div className="grid grid-cols-3 gap-4">
          {/* Linked Task */}
          <div>
            <label htmlFor="linked_task_id" className="block text-sm font-medium mb-2">
              Linked Task ID
            </label>
            <input
              type="text"
              id="linked_task_id"
              value={formData.linked_task_id || ''}
              onChange={(e) => handleChange('linked_task_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., TASK-123"
              disabled={isLoading}
            />
          </div>
          
          {/* Linked Commit */}
          <div>
            <label htmlFor="linked_commit" className="block text-sm font-medium mb-2">
              Linked Commit
            </label>
            <input
              type="text"
              id="linked_commit"
              value={formData.linked_commit || ''}
              onChange={(e) => handleChange('linked_commit', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., abc123def"
              disabled={isLoading}
            />
          </div>
          
          {/* Linked PR */}
          <div>
            <label htmlFor="linked_pr" className="block text-sm font-medium mb-2">
              Linked Pull Request
            </label>
            <input
              type="text"
              id="linked_pr"
              value={formData.linked_pr || ''}
              onChange={(e) => handleChange('linked_pr', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., PR #456 or URL"
              disabled={isLoading}
            />
          </div>
        </div>
      </div>
      
      {/* Link to Test Case */}
      <div>
        <label htmlFor="test_case_id" className="block text-sm font-medium mb-2">
          Link to Test Case
        </label>
        <select
          id="test_case_id"
          value={formData.test_case_id || ''}
          onChange={(e) => handleChange('test_case_id', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        >
          <option value="">No test case linked</option>
          {testCases.map(testCase => (
            <option key={testCase.id} value={testCase.id}>
              {testCase.title}
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
