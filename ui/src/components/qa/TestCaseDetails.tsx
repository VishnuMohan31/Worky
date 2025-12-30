/**
 * TestCaseDetails Component
 * Displays full test case information with execution history and linked bugs
 */
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../services/api'
import { TestCase } from '../../types/entities'
import Modal from '../common/Modal'
import CommentsSection from './CommentsSection'

interface TestCaseDetailsProps {
  testCaseId: string
  onClose: () => void
  onExecute?: (testCaseId: string) => void
}

interface TestExecution {
  id: string
  execution_status: string
  execution_date: string
  executed_by: string
  executor_name?: string
  actual_result?: string
  execution_notes?: string
  environment?: string
}

interface LinkedBug {
  id: string
  title: string
  severity: string
  status: string
  created_at: string
}

export default function TestCaseDetails({
  testCaseId,
  onClose,
  onExecute
}: TestCaseDetailsProps) {
  const { t } = useTranslation()
  
  const [testCase, setTestCase] = useState<TestCase | null>(null)
  const [executions, setExecutions] = useState<TestExecution[]>([])
  const [linkedBugs, setLinkedBugs] = useState<LinkedBug[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [activeTab, setActiveTab] = useState<'details' | 'executions' | 'bugs' | 'comments'>('details')
  
  useEffect(() => {
    loadTestCaseDetails()
  }, [testCaseId])
  
  const loadTestCaseDetails = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Load test case
      const testCaseData = await api.get(`/test-cases/${testCaseId}`)
      setTestCase(testCaseData)
      
      // Load executions
      try {
        const executionsData = await api.get(`/test-cases/${testCaseId}/executions`)
        setExecutions(executionsData)
      } catch (err) {
        console.error('Failed to load executions:', err)
        setExecutions([])
      }
      
      // Load linked bugs
      try {
        const bugsData = await api.get(`/test-cases/${testCaseId}/bugs`)
        setLinkedBugs(bugsData)
      } catch (err) {
        console.error('Failed to load linked bugs:', err)
        setLinkedBugs([])
      }
    } catch (err: any) {
      console.error('Failed to load test case:', err)
      setError(err.message || 'Failed to load test case details')
    } finally {
      setIsLoading(false)
    }
  }
  
  const parseTestSteps = (stepsJson?: string) => {
    if (!stepsJson) return []
    try {
      return JSON.parse(stepsJson)
    } catch {
      return []
    }
  }
  
  const parseTags = (tagsJson?: string) => {
    if (!tagsJson) return []
    try {
      return JSON.parse(tagsJson)
    } catch {
      return []
    }
  }
  
  if (isLoading) {
    return (
      <Modal isOpen={true} onClose={onClose} title="Test Case Details" size="xl">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading test case details...</div>
        </div>
      </Modal>
    )
  }
  
  if (error || !testCase) {
    return (
      <Modal isOpen={true} onClose={onClose} title="Test Case Details" size="xl">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">{error || 'Test case not found'}</div>
        </div>
      </Modal>
    )
  }
  
  const testSteps = parseTestSteps(testCase.test_steps)
  const tags = parseTags(testCase.tags)
  
  return (
    <Modal isOpen={true} onClose={onClose} title={`Test Case: ${testCase.test_case_name}`} size="xl">
      <div className="space-y-6">
        {/* Header Actions */}
        <div className="flex items-center justify-between pb-4 border-b">
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              testCase.status === 'Passed' ? 'bg-green-100 text-green-800' :
              testCase.status === 'Failed' ? 'bg-red-100 text-red-800' :
              testCase.status === 'Blocked' ? 'bg-yellow-100 text-yellow-800' :
              testCase.status === 'Skipped' ? 'bg-gray-100 text-gray-800' :
              'bg-blue-100 text-blue-800'
            }`}>
              {testCase.status}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              testCase.priority === 'P0' ? 'bg-red-100 text-red-800' :
              testCase.priority === 'P1' ? 'bg-orange-100 text-orange-800' :
              testCase.priority === 'P2' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {testCase.priority}
            </span>
          </div>
          {onExecute && (
            <button
              onClick={() => onExecute(testCaseId)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              ▶ Execute Test
            </button>
          )}
        </div>
        
        {/* Tabs */}
        <div className="border-b">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('details')}
              className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                activeTab === 'details'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Details
            </button>
            <button
              onClick={() => setActiveTab('executions')}
              className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                activeTab === 'executions'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Execution History ({executions.length})
            </button>
            <button
              onClick={() => setActiveTab('bugs')}
              className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                activeTab === 'bugs'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Linked Bugs ({linkedBugs.length})
            </button>
            <button
              onClick={() => setActiveTab('comments')}
              className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                activeTab === 'comments'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Comments
            </button>
          </div>
        </div>
        
        {/* Tab Content */}
        <div className="min-h-[400px]">
          {/* Details Tab */}
          {activeTab === 'details' && (
            <div className="space-y-6">
              {/* Description */}
              {testCase.test_case_description && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Description</h3>
                  <p className="text-gray-600">{testCase.test_case_description}</p>
                </div>
              )}
              
              {/* Component */}
              {testCase.component_attached_to && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Component</h3>
                  <p className="text-gray-600">{testCase.component_attached_to}</p>
                </div>
              )}
              
              {/* Test Steps */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Test Steps</h3>
                <ol className="space-y-2">
                  {testSteps.map((step: any, index: number) => (
                    <li key={index} className="flex gap-3">
                      <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                        {step.step || index + 1}
                      </span>
                      <span className="text-gray-600">{step.description || step}</span>
                    </li>
                  ))}
                </ol>
              </div>
              
              {/* Expected Result */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Expected Result</h3>
                <p className="text-gray-600">{testCase.expected_result}</p>
              </div>
              
              {/* Actual Result (if executed) */}
              {testCase.actual_result && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Actual Result</h3>
                  <p className="text-gray-600">{testCase.actual_result}</p>
                </div>
              )}
              
              {/* Inference (if executed) */}
              {testCase.inference && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Inference</h3>
                  <p className="text-gray-600">{testCase.inference}</p>
                </div>
              )}
              
              {/* Remarks */}
              {testCase.remarks && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Remarks</h3>
                  <p className="text-gray-600">{testCase.remarks}</p>
                </div>
              )}
              
              {/* Last Execution */}
              {testCase.executed_by && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Last Execution</h3>
                  <div className="flex items-center gap-4 text-sm">
                    <span className={`font-medium ${
                      testCase.status === 'Passed' ? 'text-green-600' :
                      testCase.status === 'Failed' ? 'text-red-600' :
                      'text-yellow-600'
                    }`}>
                      {testCase.status}
                    </span>
                    {testCase.executed_at && (
                      <span className="text-gray-500">
                        {new Date(testCase.executed_at).toLocaleString()}
                      </span>
                    )}
                    <span className="text-gray-500">
                      by User {testCase.executed_by}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Executions Tab */}
          {activeTab === 'executions' && (
            <div>
              {executions.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-gray-400 text-4xl mb-3">📊</div>
                  <p className="text-gray-600">No execution history yet</p>
                  {onExecute && (
                    <button
                      onClick={() => onExecute(testCaseId)}
                      className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Execute Test
                    </button>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  {executions.map(execution => (
                    <div key={execution.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          execution.execution_status === 'Passed' ? 'bg-green-100 text-green-800' :
                          execution.execution_status === 'Failed' ? 'bg-red-100 text-red-800' :
                          execution.execution_status === 'Blocked' ? 'bg-orange-100 text-orange-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {execution.execution_status}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(execution.execution_date).toLocaleString()}
                        </span>
                      </div>
                      {execution.executor_name && (
                        <p className="text-sm text-gray-600 mb-2">
                          Executed by: {execution.executor_name}
                        </p>
                      )}
                      {execution.environment && (
                        <p className="text-sm text-gray-600 mb-2">
                          Environment: {execution.environment}
                        </p>
                      )}
                      {execution.actual_result && (
                        <div className="mt-2">
                          <p className="text-sm font-medium text-gray-700">Actual Result:</p>
                          <p className="text-sm text-gray-600">{execution.actual_result}</p>
                        </div>
                      )}
                      {execution.execution_notes && (
                        <div className="mt-2">
                          <p className="text-sm font-medium text-gray-700">Notes:</p>
                          <p className="text-sm text-gray-600">{execution.execution_notes}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {/* Bugs Tab */}
          {activeTab === 'bugs' && (
            <div>
              {linkedBugs.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-gray-400 text-4xl mb-3">🐛</div>
                  <p className="text-gray-600">No linked bugs</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {linkedBugs.map(bug => (
                    <div key={bug.id} className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{bug.title}</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          bug.severity === 'Critical' ? 'bg-red-100 text-red-800' :
                          bug.severity === 'High' ? 'bg-orange-100 text-orange-800' :
                          bug.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {bug.severity}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-sm text-gray-600">
                        <span className="font-mono">{bug.id}</span>
                        <span>•</span>
                        <span>{bug.status}</span>
                        <span>•</span>
                        <span>{new Date(bug.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {/* Comments Tab */}
          {activeTab === 'comments' && (
            <CommentsSection
              entityType="test_case"
              entityId={testCaseId}
              showSystemNotes={false}
            />
          )}
        </div>
      </div>
    </Modal>
  )
}
