/**
 * TestRunDetails Component
 * Displays full test run information with test case list and metrics
 */
import { useState, useEffect } from 'react'
import api from '../../services/api'
import { TestRun, TestCase } from '../../types/entities'

interface TestRunDetailsProps {
  testRunId: string
  onClose: () => void
  onAddTestCase?: () => void
}

export default function TestRunDetails({ testRunId, onClose, onAddTestCase }: TestRunDetailsProps) {
  const [testRun, setTestRun] = useState<TestRun | null>(null)
  const [testCases, setTestCases] = useState<TestCase[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    loadTestRunDetails()
    loadTestCases()
  }, [testRunId])
  
  const loadTestRunDetails = async () => {
    try {
      const data = await api.get(`/test-runs/${testRunId}`)
      setTestRun(data)
    } catch (err: any) {
      console.error('Failed to load test run details:', err)
      setError(err.message || 'Failed to load test run details')
    } finally {
      setIsLoading(false)
    }
  }
  
  const loadTestCases = async () => {
    try {
      const data = await api.get('/test-cases/', {
        params: { test_run_id: testRunId }
      })
      setTestCases(data.test_cases || [])
    } catch (err: any) {
      console.error('Failed to load test cases:', err)
    }
  }
  
  const calculatePassRate = () => {
    if (!testRun || testRun.total_test_cases === 0) return 0
    return Math.round((testRun.passed_test_cases / testRun.total_test_cases) * 100)
  }
  
  const calculateCompletionRate = () => {
    if (!testRun || testRun.total_test_cases === 0) return 0
    const executed = testRun.passed_test_cases + testRun.failed_test_cases + testRun.blocked_test_cases
    return Math.round((executed / testRun.total_test_cases) * 100)
  }
  
  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="text-gray-500">Loading test run details...</div>
        </div>
      </div>
    )
  }
  
  if (error || !testRun) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="text-red-500">{error || 'Test run not found'}</div>
          <button
            onClick={onClose}
            className="mt-4 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    )
  }
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{testRun.name}</h2>
            <p className="text-sm text-gray-600 mt-1">{testRun.short_description}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {/* Test Run Info */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Test Run Information</h3>
              <div className="space-y-2">
                <div>
                  <span className="text-sm font-medium text-gray-600">ID:</span>
                  <span className="ml-2 text-sm text-gray-900">{testRun.id}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Type:</span>
                  <span className="ml-2 text-sm text-gray-900">{testRun.run_type}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Status:</span>
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                    testRun.status === 'Completed' ? 'bg-green-100 text-green-800' :
                    testRun.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {testRun.status}
                  </span>
                </div>
                {testRun.component_attached_to && (
                  <div>
                    <span className="text-sm font-medium text-gray-600">Component:</span>
                    <span className="ml-2 text-sm text-gray-900">{testRun.component_attached_to}</span>
                  </div>
                )}
                {testRun.purpose && (
                  <div>
                    <span className="text-sm font-medium text-gray-600">Purpose:</span>
                    <p className="mt-1 text-sm text-gray-900">{testRun.purpose}</p>
                  </div>
                )}
              </div>
            </div>
            
            {/* Metrics */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Test Metrics</h3>
              <div className="space-y-4">
                {/* Test Case Counts */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Test Cases</span>
                    <span className="text-sm font-bold text-gray-900">{testRun.total_test_cases}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="bg-green-50 p-2 rounded">
                      <div className="text-green-600 font-medium">Passed</div>
                      <div className="text-green-900 font-bold text-lg">{testRun.passed_test_cases}</div>
                    </div>
                    <div className="bg-red-50 p-2 rounded">
                      <div className="text-red-600 font-medium">Failed</div>
                      <div className="text-red-900 font-bold text-lg">{testRun.failed_test_cases}</div>
                    </div>
                    <div className="bg-yellow-50 p-2 rounded">
                      <div className="text-yellow-600 font-medium">Blocked</div>
                      <div className="text-yellow-900 font-bold text-lg">{testRun.blocked_test_cases}</div>
                    </div>
                  </div>
                </div>
                
                {/* Pass Rate */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Pass Rate</span>
                    <span className="text-sm font-bold text-gray-900">{calculatePassRate()}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-green-500 h-3 rounded-full transition-all"
                      style={{ width: `${calculatePassRate()}%` }}
                    />
                  </div>
                </div>
                
                {/* Completion Rate */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Completion</span>
                    <span className="text-sm font-bold text-gray-900">{calculateCompletionRate()}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-blue-500 h-3 rounded-full transition-all"
                      style={{ width: `${calculateCompletionRate()}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Long Description */}
          {testRun.long_description && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{testRun.long_description}</p>
            </div>
          )}
          
          {/* Test Cases List */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900">Test Cases</h3>
              {onAddTestCase && (
                <button
                  onClick={onAddTestCase}
                  className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                >
                  + Add Test Case
                </button>
              )}
            </div>
            
            {testCases.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <div className="text-gray-400 text-4xl mb-2">📋</div>
                <p className="text-gray-600">No test cases yet</p>
                {onAddTestCase && (
                  <button
                    onClick={onAddTestCase}
                    className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Add First Test Case
                  </button>
                )}
              </div>
            ) : (
              <div className="bg-white border rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        ID
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Name
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Priority
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Executed By
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {testCases.map(testCase => (
                      <tr key={testCase.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {testCase.id}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {testCase.test_case_name}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            testCase.priority === 'P0' ? 'bg-red-100 text-red-800' :
                            testCase.priority === 'P1' ? 'bg-orange-100 text-orange-800' :
                            testCase.priority === 'P2' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {testCase.priority || 'N/A'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            testCase.status === 'Passed' ? 'bg-green-100 text-green-800' :
                            testCase.status === 'Failed' ? 'bg-red-100 text-red-800' :
                            testCase.status === 'Blocked' ? 'bg-yellow-100 text-yellow-800' :
                            testCase.status === 'Skipped' ? 'bg-gray-100 text-gray-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {testCase.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {testCase.executed_by || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
        
        {/* Footer */}
        <div className="px-6 py-4 border-t bg-gray-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
