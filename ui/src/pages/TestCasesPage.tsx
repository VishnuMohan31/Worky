/**
 * TestCasesPage Component
 * Page for managing test cases within test runs
 * Requirements: 3.1, 3.10
 */
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import Modal from '../components/common/Modal'
import TestCaseForm, { TestCaseFormData } from '../components/forms/TestCaseForm'
import TestCaseDetails from '../components/qa/TestCaseDetails'
import TestExecutionModal, { TestExecutionData } from '../components/qa/TestExecutionModal'
import BugForm from '../components/forms/BugForm'
import { TestCase, TestRun, BugFormData } from '../types/entities'

// Test case status options for filtering
const TEST_CASE_STATUS_OPTIONS = ['Not Executed', 'Passed', 'Failed', 'Blocked', 'Skipped'] as const

// Test case priority options for filtering
const TEST_CASE_PRIORITY_OPTIONS = ['P0', 'P1', 'P2', 'P3'] as const

export default function TestCasesPage() {
  const { t } = useTranslation()
  
  // State
  const [testRuns, setTestRuns] = useState<TestRun[]>([])
  const [selectedTestRunId, setSelectedTestRunId] = useState<string>('')
  const [testCases, setTestCases] = useState<TestCase[]>([])
  const [filteredTestCases, setFilteredTestCases] = useState<TestCase[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(null)
  const [viewingTestCaseId, setViewingTestCaseId] = useState<string | null>(null)
  const [executingTestCase, setExecutingTestCase] = useState<TestCase | null>(null)
  const [lastExecutionResult, setLastExecutionResult] = useState<{ testCaseId: string; status: string; executionId: string } | null>(null)
  const [showCreateBugModal, setShowCreateBugModal] = useState(false)
  
  // Filter state
  const [filters, setFilters] = useState({
    status: '',
    priority: ''
  })
  
  // Load test runs on mount
  useEffect(() => {
    loadTestRuns()
  }, [])
  
  // Load test cases when test run selection changes
  useEffect(() => {
    if (selectedTestRunId) {
      loadTestCases()
    } else {
      setTestCases([])
      setFilteredTestCases([])
    }
  }, [selectedTestRunId])
  
  // Apply filters
  useEffect(() => {
    applyFilters()
  }, [testCases, filters])
  
  const loadTestRuns = async () => {
    try {
      const data = await api.get('/test-runs/')
      setTestRuns(data)
    } catch (err) {
      console.error('Failed to load test runs:', err)
      setTestRuns([])
    }
  }
  
  const loadTestCases = async () => {
    if (!selectedTestRunId) {
      setTestCases([])
      return
    }
    
    setIsLoading(true)
    setError(null)
    
    try {
      // Requirement 3.1: Fetch test cases from API for selected test run
      const response = await api.get('/test-cases/', { 
        params: { test_run_id: selectedTestRunId } 
      })
      
      // API returns { test_cases: [...], total: number, page: number, page_size: number }
      const testCasesList = response.test_cases || response || []
      setTestCases(testCasesList)
      
      console.log(`Loaded ${testCasesList.length} test cases for test run ${selectedTestRunId}`)
    } catch (err: any) {
      console.error('Failed to load test cases:', err)
      setError(err.message || 'Failed to load test cases')
      setTestCases([])
    } finally {
      setIsLoading(false)
    }
  }
  
  const applyFilters = () => {
    let filtered = [...testCases]
    
    // Requirement 3.10: Add filters for status, priority
    if (filters.status) {
      filtered = filtered.filter(tc => tc.status === filters.status)
    }
    
    if (filters.priority) {
      filtered = filtered.filter(tc => tc.priority === filters.priority)
    }
    
    setFilteredTestCases(filtered)
  }
  
  const handleTestRunChange = (testRunId: string) => {
    setSelectedTestRunId(testRunId)
  }
  
  const handleCreateTestCase = () => {
    setSelectedTestCase(null)
    setIsCreateModalOpen(true)
  }
  
  const handleEditTestCase = (testCase: TestCase) => {
    setSelectedTestCase(testCase)
    setIsCreateModalOpen(true)
  }
  
  const handleViewTestCase = (testCaseId: string) => {
    setViewingTestCaseId(testCaseId)
  }
  
  const handleExecuteTest = (testCaseId: string) => {
    const testCase = filteredTestCases.find(tc => tc.id === testCaseId)
    if (testCase) {
      setExecutingTestCase(testCase)
      // Close details modal if open
      setViewingTestCaseId(null)
    }
  }
  
  const handleTestExecutionSubmit = async (executionData: TestExecutionData) => {
    try {
      // Submit test execution to API
      const response = await api.post('/test-executions/', executionData)
      
      // Update test case with actual result, inference, and status
      // This updates the test case record itself (Requirements: 11.2, 11.3, 11.5, 11.6)
      await api.put(`/test-cases/${executionData.test_case_id}`, {
        actual_result: executionData.actual_result,
        inference: executionData.inference,
        status: executionData.execution_status,
        executed_by: response.executed_by,
        executed_at: response.execution_date
      })
      
      // Store execution result and test case for potential bug creation
      const testCase = filteredTestCases.find(tc => tc.id === executionData.test_case_id)
      setLastExecutionResult({
        testCaseId: executionData.test_case_id,
        status: executionData.execution_status,
        executionId: response.id
      })
      
      // Store the test case for bug creation
      if (testCase) {
        setSelectedTestCase(testCase)
      }
      
      // Close execution modal
      setExecutingTestCase(null)
      
      // Reload test cases to update execution status
      await loadTestCases()
      
      // Show success message
      alert(`Test execution recorded successfully! Status: ${executionData.execution_status}`)
      
      // If test failed, offer to create a bug
      if (executionData.execution_status === 'Failed') {
        const createBug = window.confirm('Test execution failed. Would you like to create a bug?')
        if (createBug) {
          setShowCreateBugModal(true)
        }
      }
    } catch (err: any) {
      console.error('Failed to submit test execution:', err)
      throw new Error(err.message || 'Failed to submit test execution')
    }
  }
  
  const handleCreateBugFromExecution = async (bugData: BugFormData) => {
    try {
      if (!lastExecutionResult) {
        throw new Error('No execution result found')
      }
      
      // Create bug from failed execution
      const response = await api.post(`/test-executions/${lastExecutionResult.executionId}/create-bug`, bugData)
      
      // Close bug creation modal
      setShowCreateBugModal(false)
      setLastExecutionResult(null)
      setSelectedTestCase(null)
      
      // Show success message with bug link
      const bugId = response.id || response.bug_id
      const message = `Bug created successfully!\n\nBug ID: ${bugId}\nTitle: ${bugData.title}\n\nThe bug has been linked to the test case.`
      alert(message)
      
      // Optionally navigate to bug lifecycle page
      // window.location.href = `/bug-lifecycle?bug=${bugId}`
    } catch (err: any) {
      console.error('Failed to create bug:', err)
      throw new Error(err.message || 'Failed to create bug')
    }
  }
  
  const getBugFormInitialData = (): Partial<BugFormData> | undefined => {
    if (!lastExecutionResult) return undefined
    
    const testCase = selectedTestCase || filteredTestCases.find(tc => tc.id === lastExecutionResult.testCaseId)
    if (!testCase) return undefined
    
    // Determine entity type and ID based on test case hierarchy
    let entity_type = ''
    let entity_id = ''
    
    if (testCase.task_id) {
      entity_type = 'Task'
      entity_id = testCase.task_id
    } else if (testCase.user_story_id) {
      entity_type = 'UserStory'
      entity_id = testCase.user_story_id
    } else if (testCase.usecase_id) {
      entity_type = 'UseCase'
      entity_id = testCase.usecase_id
    } else if (testCase.project_id) {
      entity_type = 'Project'
      entity_id = testCase.project_id
    }
    
    // Parse test steps for better formatting
    let testStepsText = ''
    try {
      const steps = JSON.parse(testCase.test_steps || '[]')
      testStepsText = steps.map((step: any) => `${step.step}. ${step.description}`).join('\n')
    } catch {
      testStepsText = testCase.test_steps || ''
    }
    
    return {
      entity_type,
      entity_id,
      title: `Test Failed: ${testCase.title}`,
      short_description: `Failed test case: ${testCase.id}`,
      long_description: `Test case "${testCase.title}" (${testCase.id}) failed during execution.\n\n**Expected Result:**\n${testCase.expected_result}\n\n**Test Steps:**\n${testStepsText}\n\n**Preconditions:**\n${testCase.preconditions || 'None'}`,
      severity: 'High',
      priority: 'P1'
    }
  }
  
  const handleSaveTestCase = async (data: TestCaseFormData) => {
    try {
      // Ensure test_run_id is set
      const testCaseData = {
        ...data,
        test_run_id: selectedTestRunId
      }
      
      if (selectedTestCase) {
        await api.put(`/test-cases/${selectedTestCase.id}`, testCaseData)
      } else {
        await api.post('/test-cases/', testCaseData)
      }
      
      setIsCreateModalOpen(false)
      setSelectedTestCase(null)
      loadTestCases()
    } catch (err) {
      console.error('Failed to save test case:', err)
      throw err
    }
  }
  
  const getSelectedTestRun = () => {
    return testRuns.find(tr => tr.id === selectedTestRunId)
  }
  
  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Test Cases</h1>
            <p className="text-sm text-gray-600 mt-1">
              Manage test cases within test runs
            </p>
          </div>
          <button
            onClick={handleCreateTestCase}
            disabled={!selectedTestRunId}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            + Create Test Case
          </button>
        </div>
      </div>
      
      {/* Test Run Selector */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700 whitespace-nowrap">
            Select Test Run:
          </label>
          <select
            value={selectedTestRunId}
            onChange={(e) => handleTestRunChange(e.target.value)}
            className="flex-1 max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select a Test Run --</option>
            {testRuns.map(testRun => (
              <option key={testRun.id} value={testRun.id}>
                {testRun.name} ({testRun.id}) - {testRun.status}
              </option>
            ))}
          </select>
          
          {selectedTestRunId && getSelectedTestRun() && (
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span className="flex items-center gap-1">
                <span className="font-medium">Total:</span> {getSelectedTestRun()!.total_test_cases}
              </span>
              <span className="text-gray-300">|</span>
              <span className="flex items-center gap-1 text-green-600">
                <span className="font-medium">✓</span> {getSelectedTestRun()!.passed_test_cases}
              </span>
              <span className="flex items-center gap-1 text-red-600">
                <span className="font-medium">✗</span> {getSelectedTestRun()!.failed_test_cases}
              </span>
              <span className="flex items-center gap-1 text-yellow-600">
                <span className="font-medium">⊘</span> {getSelectedTestRun()!.blocked_test_cases}
              </span>
            </div>
          )}
        </div>
      </div>
      
      {/* Filters */}
      <div className="bg-white border-b px-6 py-3">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-gray-700">Filters:</span>
          
          <select
            value={filters.status}
            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            {TEST_CASE_STATUS_OPTIONS.map(status => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
          
          <select
            value={filters.priority}
            onChange={(e) => setFilters(prev => ({ ...prev, priority: e.target.value }))}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Priorities</option>
            {TEST_CASE_PRIORITY_OPTIONS.map(priority => (
              <option key={priority} value={priority}>{priority}</option>
            ))}
          </select>
          
          {(filters.status || filters.priority) && (
            <button
              onClick={() => setFilters({ status: '', priority: '' })}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>
      
      {/* Test Cases List */}
      <div className="flex-1 overflow-auto px-6 py-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading test cases...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-red-500">{error}</div>
          </div>
        ) : !selectedTestRunId ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="text-gray-400 text-5xl mb-4">📋</div>
              <p className="text-gray-600">Select a test run to view its test cases</p>
            </div>
          </div>
        ) : filteredTestCases.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="text-gray-400 text-5xl mb-4">📋</div>
              <p className="text-gray-600 mb-4">No test cases found for this test run</p>
              <button
                onClick={handleCreateTestCase}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create First Test Case
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Component
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Execution
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTestCases.map(testCase => (
                  <tr 
                    key={testCase.id} 
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleViewTestCase(testCase.id)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {testCase.id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div>
                        <div className="font-medium">{testCase.test_case_name}</div>
                        {testCase.test_case_description && (
                          <div className="text-gray-500 text-xs mt-1 line-clamp-1">
                            {testCase.test_case_description}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {testCase.component_attached_to || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        testCase.priority === 'P0' ? 'bg-red-100 text-red-800' :
                        testCase.priority === 'P1' ? 'bg-orange-100 text-orange-800' :
                        testCase.priority === 'P2' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {testCase.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {testCase.executed_by ? (
                        <div>
                          <div className="text-xs font-medium text-gray-700">
                            User {testCase.executed_by}
                          </div>
                          <div className="text-xs text-gray-500">
                            {testCase.executed_at && new Date(testCase.executed_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </div>
                        </div>
                      ) : (
                        <span className="text-gray-400">Not executed</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleEditTestCase(testCase)
                        }}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        Edit
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleExecuteTest(testCase.id)
                        }}
                        className="text-green-600 hover:text-green-900"
                      >
                        Execute
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* Create/Edit Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false)
          setSelectedTestCase(null)
        }}
        title={selectedTestCase ? 'Edit Test Case' : 'Create Test Case'}
        size="xl"
      >
        <TestCaseForm
          initialData={selectedTestCase ? {
            test_run_id: selectedTestCase.test_run_id,
            test_case_name: selectedTestCase.test_case_name,
            test_case_description: selectedTestCase.test_case_description,
            test_case_steps: JSON.parse(selectedTestCase.test_case_steps || '[]'),
            expected_result: selectedTestCase.expected_result,
            component_attached_to: selectedTestCase.component_attached_to,
            priority: selectedTestCase.priority as 'P0' | 'P1' | 'P2' | 'P3',
            remarks: selectedTestCase.remarks
          } : undefined}
          testRunId={selectedTestRunId}
          onSubmit={handleSaveTestCase}
          onCancel={() => {
            setIsCreateModalOpen(false)
            setSelectedTestCase(null)
          }}
          mode={selectedTestCase ? 'edit' : 'create'}
        />
      </Modal>
      
      {/* Test Case Details Modal */}
      {viewingTestCaseId && (
        <TestCaseDetails
          testCaseId={viewingTestCaseId}
          onClose={() => setViewingTestCaseId(null)}
          onExecute={handleExecuteTest}
        />
      )}
      
      {/* Test Execution Modal */}
      {executingTestCase && (
        <TestExecutionModal
          testCase={executingTestCase}
          isOpen={true}
          onClose={() => setExecutingTestCase(null)}
          onSubmit={handleTestExecutionSubmit}
        />
      )}
      
      {/* Create Bug from Failed Execution Modal */}
      <Modal
        isOpen={showCreateBugModal}
        onClose={() => {
          setShowCreateBugModal(false)
          setLastExecutionResult(null)
        }}
        title="Create Bug from Failed Test"
        size="xl"
      >
        <BugForm
          initialData={getBugFormInitialData()}
          onSubmit={handleCreateBugFromExecution}
          onCancel={() => {
            setShowCreateBugModal(false)
            setLastExecutionResult(null)
          }}
          mode="create"
        />
      </Modal>
    </div>
  )
}
