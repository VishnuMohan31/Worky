/**
 * TestExecutionModal Component
 * Modal for executing test cases and recording results
 */
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import Modal from '../common/Modal'
import { TestCase } from '../../types/entities'

interface TestExecutionModalProps {
  testCase: TestCase
  isOpen: boolean
  onClose: () => void
  onSubmit: (executionData: TestExecutionData) => Promise<void>
}

export interface TestExecutionData {
  test_case_id: string
  execution_status: 'Passed' | 'Failed' | 'Blocked' | 'Skipped'
  actual_result?: string
  inference?: string
  execution_notes?: string
  browser?: string
  os?: string
  device_type?: string
  screenshots?: File[]
  log_files?: File[]
}

const EXECUTION_STATUS_OPTIONS = ['Passed', 'Failed', 'Blocked', 'Skipped'] as const
const BROWSER_OPTIONS = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'Other']
const OS_OPTIONS = ['Windows 11', 'Windows 10', 'macOS', 'Linux', 'iOS', 'Android', 'Other']
const DEVICE_TYPE_OPTIONS = ['Desktop', 'Mobile', 'Tablet', 'Other']

export default function TestExecutionModal({
  testCase,
  isOpen,
  onClose,
  onSubmit
}: TestExecutionModalProps) {
  const { t } = useTranslation()
  
  const [executionData, setExecutionData] = useState<TestExecutionData>({
    test_case_id: testCase.id,
    execution_status: 'Passed',
    actual_result: '',
    inference: '',
    execution_notes: '',
    browser: 'Chrome',
    os: 'Windows 11',
    device_type: 'Desktop',
    screenshots: [],
    log_files: []
  })
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  // Reset form when test case changes
  useEffect(() => {
    setExecutionData({
      test_case_id: testCase.id,
      execution_status: 'Passed',
      actual_result: '',
      inference: '',
      execution_notes: '',
      browser: 'Chrome',
      os: 'Windows 11',
      device_type: 'Desktop',
      screenshots: [],
      log_files: []
    })
    setErrors({})
  }, [testCase.id])
  
  const parseTestSteps = (stepsJson?: string) => {
    if (!stepsJson) return []
    try {
      return JSON.parse(stepsJson)
    } catch {
      return []
    }
  }
  
  const testSteps = parseTestSteps(testCase.test_steps)
  
  const handleChange = (field: keyof TestExecutionData, value: any) => {
    setExecutionData(prev => ({ ...prev, [field]: value }))
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }
  
  const handleFileChange = (field: 'screenshots' | 'log_files', files: FileList | null) => {
    if (files) {
      const fileArray = Array.from(files)
      setExecutionData(prev => ({
        ...prev,
        [field]: [...(prev[field] || []), ...fileArray]
      }))
    }
  }
  
  const removeFile = (field: 'screenshots' | 'log_files', index: number) => {
    setExecutionData(prev => ({
      ...prev,
      [field]: prev[field]?.filter((_, i) => i !== index) || []
    }))
  }
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!executionData.execution_status) {
      newErrors.execution_status = 'Execution status is required'
    }
    
    if (executionData.execution_status === 'Failed' && !executionData.actual_result?.trim()) {
      newErrors.actual_result = 'Actual result is required for failed tests'
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
    try {
      await onSubmit(executionData)
      onClose()
    } catch (error) {
      console.error('Failed to submit test execution:', error)
      setErrors({ submit: 'Failed to submit test execution. Please try again.' })
    } finally {
      setIsSubmitting(false)
    }
  }
  
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Execute Test: ${testCase.title}`}
      size="xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Test Case Details */}
        <div className="bg-gray-50 rounded-lg p-4 space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Test Case ID</h3>
            <p className="text-gray-900 font-mono">{testCase.id}</p>
          </div>
          
          {testCase.preconditions && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Preconditions</h3>
              <p className="text-gray-600">{testCase.preconditions}</p>
            </div>
          )}
          
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Test Steps</h3>
            <ol className="space-y-2">
              {testSteps.map((step: any, index: number) => (
                <li key={index} className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {step.step}
                  </span>
                  <span className="text-gray-600">{step.description}</span>
                </li>
              ))}
            </ol>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Expected Result</h3>
            <p className="text-gray-600">{testCase.expected_result}</p>
          </div>
        </div>
        
        {/* Execution Status */}
        <div>
          <label htmlFor="execution_status" className="block text-sm font-medium mb-2">
            Execution Status <span className="text-red-500">*</span>
          </label>
          <select
            id="execution_status"
            value={executionData.execution_status}
            onChange={(e) => handleChange('execution_status', e.target.value as any)}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.execution_status
                ? 'border-red-500 focus:ring-red-500'
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            disabled={isSubmitting}
          >
            {EXECUTION_STATUS_OPTIONS.map(status => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
          {errors.execution_status && (
            <p className="mt-1 text-sm text-red-500">{errors.execution_status}</p>
          )}
        </div>
        
        {/* Actual Result */}
        <div>
          <label htmlFor="actual_result" className="block text-sm font-medium mb-2">
            Actual Result {executionData.execution_status === 'Failed' && <span className="text-red-500">*</span>}
          </label>
          <textarea
            id="actual_result"
            value={executionData.actual_result || ''}
            onChange={(e) => handleChange('actual_result', e.target.value)}
            rows={4}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
              errors.actual_result
                ? 'border-red-500 focus:ring-red-500'
                : 'border-gray-300 focus:ring-blue-500'
            }`}
            placeholder="Describe what actually happened during test execution"
            disabled={isSubmitting}
          />
          {errors.actual_result && (
            <p className="mt-1 text-sm text-red-500">{errors.actual_result}</p>
          )}
        </div>
        
        {/* Inference */}
        <div>
          <label htmlFor="inference" className="block text-sm font-medium mb-2">
            Inference
          </label>
          <textarea
            id="inference"
            value={executionData.inference || ''}
            onChange={(e) => handleChange('inference', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Your conclusion or analysis of the test execution results"
            disabled={isSubmitting}
          />
          <p className="mt-1 text-xs text-gray-500">
            Provide your analysis of why the test passed/failed and any insights gained
          </p>
        </div>
        
        {/* Execution Notes */}
        <div>
          <label htmlFor="execution_notes" className="block text-sm font-medium mb-2">
            Execution Notes
          </label>
          <textarea
            id="execution_notes"
            value={executionData.execution_notes || ''}
            onChange={(e) => handleChange('execution_notes', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Any additional notes or observations"
            disabled={isSubmitting}
          />
        </div>
        
        {/* Environment Details */}
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Environment Details</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label htmlFor="browser" className="block text-sm font-medium mb-2">
                Browser
              </label>
              <select
                id="browser"
                value={executionData.browser || ''}
                onChange={(e) => handleChange('browser', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isSubmitting}
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
                value={executionData.os || ''}
                onChange={(e) => handleChange('os', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isSubmitting}
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
                value={executionData.device_type || ''}
                onChange={(e) => handleChange('device_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isSubmitting}
              >
                <option value="">Select device</option>
                {DEVICE_TYPE_OPTIONS.map(device => (
                  <option key={device} value={device}>{device}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
        
        {/* File Uploads */}
        <div className="space-y-4">
          {/* Screenshots */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Screenshots
            </label>
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => handleFileChange('screenshots', e.target.files)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isSubmitting}
            />
            {executionData.screenshots && executionData.screenshots.length > 0 && (
              <div className="mt-2 space-y-1">
                {executionData.screenshots.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                    <span className="text-sm text-gray-700">{file.name}</span>
                    <button
                      type="button"
                      onClick={() => removeFile('screenshots', index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                      disabled={isSubmitting}
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Log Files */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Log Files
            </label>
            <input
              type="file"
              accept=".log,.txt,.json"
              multiple
              onChange={(e) => handleFileChange('log_files', e.target.files)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isSubmitting}
            />
            {executionData.log_files && executionData.log_files.length > 0 && (
              <div className="mt-2 space-y-1">
                {executionData.log_files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                    <span className="text-sm text-gray-700">{file.name}</span>
                    <button
                      type="button"
                      onClick={() => removeFile('log_files', index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                      disabled={isSubmitting}
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Submit Error */}
        {errors.submit && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}
        
        {/* Form Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Execution'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
