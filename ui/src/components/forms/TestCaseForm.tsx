/**
 * TestCaseForm Component
 * Form for creating and editing test cases within test runs
 * Requirements: 3.3, 3.4, 3.5, 3.6, 3.7, 3.8
 */
import { useState, useEffect } from 'react'

interface TestStep {
  step: number
  description: string
}

export interface TestCaseFormData {
  test_run_id: string
  test_case_name: string
  test_case_description?: string
  test_case_steps: TestStep[]
  expected_result: string
  component_attached_to?: string
  priority: 'P0' | 'P1' | 'P2' | 'P3'
  remarks?: string
}

interface TestCaseFormProps {
  initialData?: Partial<TestCaseFormData>
  testRunId?: string
  onSubmit: (data: TestCaseFormData) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

const PRIORITY_OPTIONS = ['P0', 'P1', 'P2', 'P3'] as const

export default function TestCaseForm({
  initialData = {},
  testRunId,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create'
}: TestCaseFormProps) {
  const [formData, setFormData] = useState<TestCaseFormData>({
    test_run_id: testRunId || '',
    test_case_name: '',
    test_case_description: '',
    test_case_steps: [{ step: 1, description: '' }],
    expected_result: '',
    component_attached_to: '',
    priority: 'P2',
    remarks: '',
    ...initialData
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({
        ...prev,
        ...initialData,
        test_case_steps: initialData.test_case_steps && initialData.test_case_steps.length > 0
          ? initialData.test_case_steps
          : [{ step: 1, description: '' }]
      }))
    }
  }, [initialData])
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.test_case_name || formData.test_case_name.trim().length === 0) {
      newErrors.test_case_name = 'Test case name is required'
    } else if (formData.test_case_name.length > 255) {
      newErrors.test_case_name = 'Test case name must be less than 255 characters'
    }
    
    if (!formData.expected_result || formData.expected_result.trim().length === 0) {
      newErrors.expected_result = 'Expected result is required'
    }
    
    // Validate test steps - at least one step with description
    const validSteps = formData.test_case_steps.filter(step => step.description.trim().length > 0)
    if (validSteps.length === 0) {
      newErrors.test_case_steps = 'At least one test step is required'
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
    
    // Filter out empty steps and renumber
    const validSteps = formData.test_case_steps
      .filter(step => step.description.trim().length > 0)
      .map((step, index) => ({ step: index + 1, description: step.description.trim() }))
    
    const submitData = {
      ...formData,
      test_case_steps: validSteps,
      test_case_name: formData.test_case_name.trim(),
      expected_result: formData.expected_result.trim()
    }
    
    try {
      await onSubmit(submitData)
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }
  
  const handleChange = (field: keyof TestCaseFormData, value: any) => {
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
  
  const handleStepChange = (index: number, description: string) => {
    const newSteps = [...formData.test_case_steps]
    newSteps[index] = { step: index + 1, description }
    handleChange('test_case_steps', newSteps)
  }
  
  const addStep = () => {
    const newSteps = [
      ...formData.test_case_steps,
      { step: formData.test_case_steps.length + 1, description: '' }
    ]
    handleChange('test_case_steps', newSteps)
  }
  
  const removeStep = (index: number) => {
    if (formData.test_case_steps.length <= 1) {
      return // Keep at least one step
    }
    
    const newSteps = formData.test_case_steps
      .filter((_, i) => i !== index)
      .map((step, i) => ({ step: i + 1, description: step.description }))
    
    handleChange('test_case_steps', newSteps)
  }
  
  const moveStepUp = (index: number) => {
    if (index === 0) return
    
    const newSteps = [...formData.test_case_steps]
    const temp = newSteps[index]
    newSteps[index] = newSteps[index - 1]
    newSteps[index - 1] = temp
    
    // Renumber
    const renumbered = newSteps.map((step, i) => ({ step: i + 1, description: step.description }))
    handleChange('test_case_steps', renumbered)
  }
  
  const moveStepDown = (index: number) => {
    if (index === formData.test_case_steps.length - 1) return
    
    const newSteps = [...formData.test_case_steps]
    const temp = newSteps[index]
    newSteps[index] = newSteps[index + 1]
    newSteps[index + 1] = temp
    
    // Renumber
    const renumbered = newSteps.map((step, i) => ({ step: i + 1, description: step.description }))
    handleChange('test_case_steps', renumbered)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Test Case Name */}
      <div>
        <label htmlFor="test_case_name" className="block text-sm font-medium mb-2">
          Test Case Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="test_case_name"
          value={formData.test_case_name}
          onChange={(e) => handleChange('test_case_name', e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.test_case_name 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="Enter test case name"
          disabled={isLoading}
        />
        {errors.test_case_name && (
          <p className="mt-1 text-sm text-red-500">{errors.test_case_name}</p>
        )}
      </div>
      
      {/* Test Case Description */}
      <div>
        <label htmlFor="test_case_description" className="block text-sm font-medium mb-2">
          Description
        </label>
        <textarea
          id="test_case_description"
          value={formData.test_case_description || ''}
          onChange={(e) => handleChange('test_case_description', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Brief description of what this test case validates"
          disabled={isLoading}
        />
      </div>
      
      {/* Test Steps */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium">
            Test Steps <span className="text-red-500">*</span>
          </label>
          <button
            type="button"
            onClick={addStep}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            disabled={isLoading}
          >
            + Add Step
          </button>
        </div>
        
        <div className="space-y-3">
          {formData.test_case_steps.map((step, index) => (
            <div key={index} className="flex gap-2">
              <div className="flex-shrink-0 w-12 pt-2">
                <span className="text-sm font-medium text-gray-600">
                  {index + 1}.
                </span>
              </div>
              
              <div className="flex-1">
                <textarea
                  value={step.description}
                  onChange={(e) => handleStepChange(index, e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={`Enter step ${index + 1} description`}
                  disabled={isLoading}
                />
              </div>
              
              <div className="flex flex-col gap-1">
                <button
                  type="button"
                  onClick={() => moveStepUp(index)}
                  disabled={index === 0 || isLoading}
                  className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Move up"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                </button>
                
                <button
                  type="button"
                  onClick={() => moveStepDown(index)}
                  disabled={index === formData.test_case_steps.length - 1 || isLoading}
                  className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Move down"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                <button
                  type="button"
                  onClick={() => removeStep(index)}
                  disabled={formData.test_case_steps.length <= 1 || isLoading}
                  className="p-1 text-red-400 hover:text-red-600 disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Remove step"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
        
        {errors.test_case_steps && (
          <p className="mt-1 text-sm text-red-500">{errors.test_case_steps}</p>
        )}
      </div>
      
      {/* Expected Result */}
      <div>
        <label htmlFor="expected_result" className="block text-sm font-medium mb-2">
          Expected Result <span className="text-red-500">*</span>
        </label>
        <textarea
          id="expected_result"
          value={formData.expected_result}
          onChange={(e) => handleChange('expected_result', e.target.value)}
          rows={3}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.expected_result 
              ? 'border-red-500 focus:ring-red-500' 
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="Describe the expected outcome when all steps are executed correctly"
          disabled={isLoading}
        />
        {errors.expected_result && (
          <p className="mt-1 text-sm text-red-500">{errors.expected_result}</p>
        )}
      </div>
      
      {/* Component Attached To and Priority */}
      <div className="grid grid-cols-2 gap-4">
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
            placeholder="e.g., Login Screen, Payment API"
            disabled={isLoading}
          />
        </div>
        
        <div>
          <label htmlFor="priority" className="block text-sm font-medium mb-2">
            Priority <span className="text-red-500">*</span>
          </label>
          <select
            id="priority"
            value={formData.priority}
            onChange={(e) => handleChange('priority', e.target.value as TestCaseFormData['priority'])}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.priority 
                ? 'border-red-500 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            disabled={isLoading}
          >
            {PRIORITY_OPTIONS.map(priority => (
              <option key={priority} value={priority}>
                {priority} {priority === 'P0' ? '(Critical)' : priority === 'P1' ? '(High)' : priority === 'P2' ? '(Medium)' : '(Low)'}
              </option>
            ))}
          </select>
          {errors.priority && (
            <p className="mt-1 text-sm text-red-500">{errors.priority}</p>
          )}
        </div>
      </div>
      
      {/* Remarks */}
      <div>
        <label htmlFor="remarks" className="block text-sm font-medium mb-2">
          Remarks
        </label>
        <textarea
          id="remarks"
          value={formData.remarks || ''}
          onChange={(e) => handleChange('remarks', e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Additional notes or observations"
          disabled={isLoading}
        />
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
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Test Case' : 'Update Test Case'}
        </button>
      </div>
    </form>
  )
}
