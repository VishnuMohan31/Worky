/**
 * TestRunsPage Component
 * Page for managing test runs with hierarchical filtering
 */
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import Modal from '../components/common/Modal'
import TestRunDetails from '../components/qa/TestRunDetails'
import { TestRun, TEST_RUN_TYPE_OPTIONS, TEST_RUN_STATUS_OPTIONS } from '../types/entities'

interface HierarchySelection {
  clientId?: string
  programId?: string
  projectId?: string
  usecaseId?: string
  userStoryId?: string
  taskId?: string
  subtaskId?: string
}

export default function TestRunsPage() {
  const { t } = useTranslation()
  
  // State
  const [hierarchySelection, setHierarchySelection] = useState<HierarchySelection>({})
  const [testRuns, setTestRuns] = useState<TestRun[]>([])
  const [filteredTestRuns, setFilteredTestRuns] = useState<TestRun[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [selectedTestRun, setSelectedTestRun] = useState<TestRun | null>(null)
  const [viewingTestRunId, setViewingTestRunId] = useState<string | null>(null)
  
  // Filter state
  const [filters, setFilters] = useState({
    status: '',
    run_type: ''
  })
  
  // Hierarchy options
  const [clients, setClients] = useState<any[]>([])
  const [programs, setPrograms] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [usecases, setUsecases] = useState<any[]>([])
  const [userStories, setUserStories] = useState<any[]>([])
  const [tasks, setTasks] = useState<any[]>([])
  const [subtasks, setSubtasks] = useState<any[]>([])
  
  // Load hierarchy options
  useEffect(() => {
    loadClients()
  }, [])
  
  useEffect(() => {
    if (hierarchySelection.clientId) {
      loadPrograms(hierarchySelection.clientId)
    } else {
      setPrograms([])
      setProjects([])
      setUsecases([])
      setUserStories([])
      setTasks([])
      setSubtasks([])
    }
  }, [hierarchySelection.clientId])
  
  useEffect(() => {
    if (hierarchySelection.programId) {
      loadProjects(hierarchySelection.programId)
    } else {
      setProjects([])
      setUsecases([])
      setUserStories([])
      setTasks([])
      setSubtasks([])
    }
  }, [hierarchySelection.programId])
  
  useEffect(() => {
    if (hierarchySelection.projectId) {
      loadUseCases(hierarchySelection.projectId)
    } else {
      setUsecases([])
      setUserStories([])
      setTasks([])
      setSubtasks([])
    }
  }, [hierarchySelection.projectId])
  
  useEffect(() => {
    if (hierarchySelection.usecaseId) {
      loadUserStories(hierarchySelection.usecaseId)
    } else {
      setUserStories([])
      setTasks([])
      setSubtasks([])
    }
  }, [hierarchySelection.usecaseId])
  
  useEffect(() => {
    if (hierarchySelection.userStoryId) {
      loadTasks(hierarchySelection.userStoryId)
    } else {
      setTasks([])
      setSubtasks([])
    }
  }, [hierarchySelection.userStoryId])
  
  useEffect(() => {
    if (hierarchySelection.taskId) {
      loadSubtasks(hierarchySelection.taskId)
    } else {
      setSubtasks([])
    }
  }, [hierarchySelection.taskId])
  
  // Load test runs when hierarchy selection changes
  useEffect(() => {
    if (hierarchySelection.projectId || hierarchySelection.usecaseId || 
        hierarchySelection.userStoryId || hierarchySelection.taskId || 
        hierarchySelection.subtaskId) {
      loadTestRuns()
    }
  }, [hierarchySelection])
  
  // Apply filters
  useEffect(() => {
    applyFilters()
  }, [testRuns, filters])
  
  const loadClients = async () => {
    try {
      const data = await api.getClients()
      setClients(data)
    } catch (err) {
      console.error('Failed to load clients:', err)
    }
  }
  
  const loadPrograms = async (clientId: string) => {
    try {
      const data = await api.getPrograms(clientId)
      setPrograms(data)
    } catch (err) {
      console.error('Failed to load programs:', err)
    }
  }
  
  const loadProjects = async (programId: string) => {
    try {
      const data = await api.get(`/programs/${programId}/projects`)
      setProjects(data)
    } catch (err) {
      console.error('Failed to load projects:', err)
    }
  }
  
  const loadUseCases = async (projectId: string) => {
    try {
      const data = await api.getUseCases(projectId)
      setUsecases(data)
    } catch (err) {
      console.error('Failed to load use cases:', err)
    }
  }
  
  const loadUserStories = async (usecaseId: string) => {
    try {
      const data = await api.getUserStories(usecaseId)
      setUserStories(data)
    } catch (err) {
      console.error('Failed to load user stories:', err)
    }
  }
  
  const loadTasks = async (userStoryId: string) => {
    try {
      const data = await api.get(`/user-stories/${userStoryId}/tasks`)
      setTasks(data)
    } catch (err) {
      console.error('Failed to load tasks:', err)
    }
  }
  
  const loadSubtasks = async (taskId: string) => {
    try {
      const data = await api.getSubtasks(taskId)
      setSubtasks(data)
    } catch (err) {
      console.error('Failed to load subtasks:', err)
    }
  }
  
  const loadTestRuns = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const params: any = {}
      
      if (hierarchySelection.projectId) params.project_id = hierarchySelection.projectId
      if (hierarchySelection.usecaseId) params.usecase_id = hierarchySelection.usecaseId
      if (hierarchySelection.userStoryId) params.user_story_id = hierarchySelection.userStoryId
      if (hierarchySelection.taskId) params.task_id = hierarchySelection.taskId
      if (hierarchySelection.subtaskId) params.subtask_id = hierarchySelection.subtaskId
      
      const data = await api.get('/test-runs/', { params })
      setTestRuns(data)
    } catch (err: any) {
      console.error('Failed to load test runs:', err)
      setError(err.message || 'Failed to load test runs')
      setTestRuns([])
    } finally {
      setIsLoading(false)
    }
  }
  
  const applyFilters = () => {
    let filtered = [...testRuns]
    
    if (filters.status) {
      filtered = filtered.filter(tr => tr.status === filters.status)
    }
    
    if (filters.run_type) {
      filtered = filtered.filter(tr => tr.run_type === filters.run_type)
    }
    
    setFilteredTestRuns(filtered)
  }
  
  const handleHierarchyChange = (field: keyof HierarchySelection, value: string) => {
    setHierarchySelection(prev => {
      const newSelection: HierarchySelection = { ...prev, [field]: value }
      
      // Clear child selections when parent changes
      if (field === 'clientId') {
        newSelection.programId = undefined
        newSelection.projectId = undefined
        newSelection.usecaseId = undefined
        newSelection.userStoryId = undefined
        newSelection.taskId = undefined
        newSelection.subtaskId = undefined
      } else if (field === 'programId') {
        newSelection.projectId = undefined
        newSelection.usecaseId = undefined
        newSelection.userStoryId = undefined
        newSelection.taskId = undefined
        newSelection.subtaskId = undefined
      } else if (field === 'projectId') {
        newSelection.usecaseId = undefined
        newSelection.userStoryId = undefined
        newSelection.taskId = undefined
        newSelection.subtaskId = undefined
      } else if (field === 'usecaseId') {
        newSelection.userStoryId = undefined
        newSelection.taskId = undefined
        newSelection.subtaskId = undefined
      } else if (field === 'userStoryId') {
        newSelection.taskId = undefined
        newSelection.subtaskId = undefined
      } else if (field === 'taskId') {
        newSelection.subtaskId = undefined
      }
      
      return newSelection
    })
  }
  
  const handleCreateTestRun = () => {
    setSelectedTestRun(null)
    setIsCreateModalOpen(true)
  }
  
  const handleViewTestRun = (testRunId: string) => {
    setViewingTestRunId(testRunId)
  }
  
  const handleCloseDetails = () => {
    setViewingTestRunId(null)
  }
  
  const getHierarchyLevel = () => {
    if (hierarchySelection.subtaskId) return { type: 'subtask' as const, id: hierarchySelection.subtaskId }
    if (hierarchySelection.taskId) return { type: 'task' as const, id: hierarchySelection.taskId }
    if (hierarchySelection.userStoryId) return { type: 'user_story' as const, id: hierarchySelection.userStoryId }
    if (hierarchySelection.usecaseId) return { type: 'usecase' as const, id: hierarchySelection.usecaseId }
    if (hierarchySelection.projectId) return { type: 'project' as const, id: hierarchySelection.projectId }
    return null
  }
  
  const calculatePassRate = (testRun: TestRun) => {
    if (testRun.total_test_cases === 0) return 0
    return Math.round((testRun.passed_test_cases / testRun.total_test_cases) * 100)
  }
  
  return (
    <>
      {viewingTestRunId && (
        <TestRunDetails
          testRunId={viewingTestRunId}
          onClose={handleCloseDetails}
        />
      )}
      
      <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Test Runs</h1>
            <p className="text-sm text-gray-600 mt-1">
              Manage test runs across your project hierarchy
            </p>
          </div>
          <button
            onClick={handleCreateTestRun}
            disabled={!getHierarchyLevel()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            + Create Test Run
          </button>
        </div>
      </div>
      
      {/* Hierarchical Selector */}
      <div className="bg-white border-b px-6 py-4">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
          {/* Client */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Client
            </label>
            <select
              value={hierarchySelection.clientId || ''}
              onChange={(e) => handleHierarchyChange('clientId', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Client</option>
              {clients.map(client => (
                <option key={client.id} value={client.id}>{client.name}</option>
              ))}
            </select>
          </div>
          
          {/* Program */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Program
            </label>
            <select
              value={hierarchySelection.programId || ''}
              onChange={(e) => handleHierarchyChange('programId', e.target.value)}
              disabled={!hierarchySelection.clientId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="">Select Program</option>
              {programs.map(program => (
                <option key={program.id} value={program.id}>{program.name}</option>
              ))}
            </select>
          </div>
          
          {/* Project */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project
            </label>
            <select
              value={hierarchySelection.projectId || ''}
              onChange={(e) => handleHierarchyChange('projectId', e.target.value)}
              disabled={!hierarchySelection.programId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="">Select Project</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>{project.name}</option>
              ))}
            </select>
          </div>
          
          {/* Use Case */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Use Case
            </label>
            <select
              value={hierarchySelection.usecaseId || ''}
              onChange={(e) => handleHierarchyChange('usecaseId', e.target.value)}
              disabled={!hierarchySelection.projectId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="">Select Use Case</option>
              {usecases.map(usecase => (
                <option key={usecase.id} value={usecase.id}>{usecase.name}</option>
              ))}
            </select>
          </div>
          
          {/* User Story */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              User Story
            </label>
            <select
              value={hierarchySelection.userStoryId || ''}
              onChange={(e) => handleHierarchyChange('userStoryId', e.target.value)}
              disabled={!hierarchySelection.usecaseId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="">Select User Story</option>
              {userStories.map(story => (
                <option key={story.id} value={story.id}>{story.name}</option>
              ))}
            </select>
          </div>
          
          {/* Task */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Task
            </label>
            <select
              value={hierarchySelection.taskId || ''}
              onChange={(e) => handleHierarchyChange('taskId', e.target.value)}
              disabled={!hierarchySelection.userStoryId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="">Select Task</option>
              {tasks.map(task => (
                <option key={task.id} value={task.id}>{task.title}</option>
              ))}
            </select>
          </div>
          
          {/* Subtask */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subtask
            </label>
            <select
              value={hierarchySelection.subtaskId || ''}
              onChange={(e) => handleHierarchyChange('subtaskId', e.target.value)}
              disabled={!hierarchySelection.taskId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="">Select Subtask</option>
              {subtasks.map(subtask => (
                <option key={subtask.id} value={subtask.id}>{subtask.name}</option>
              ))}
            </select>
          </div>
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
            {TEST_RUN_STATUS_OPTIONS.map(status => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
          
          <select
            value={filters.run_type}
            onChange={(e) => setFilters(prev => ({ ...prev, run_type: e.target.value }))}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            {TEST_RUN_TYPE_OPTIONS.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
          
          {(filters.status || filters.run_type) && (
            <button
              onClick={() => setFilters({ status: '', run_type: '' })}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>
      
      {/* Test Runs List */}
      <div className="flex-1 overflow-auto px-6 py-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading test runs...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-red-500">{error}</div>
          </div>
        ) : !getHierarchyLevel() ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="text-gray-400 text-5xl mb-4">🏃</div>
              <p className="text-gray-600">Select a Project, Use Case, User Story, Task, or Subtask to view test runs</p>
            </div>
          </div>
        ) : filteredTestRuns.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="text-gray-400 text-5xl mb-4">🏃</div>
              <p className="text-gray-600 mb-4">No test runs found</p>
              <button
                onClick={handleCreateTestRun}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create First Test Run
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
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Test Cases
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Pass Rate
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTestRuns.map(testRun => (
                  <tr 
                    key={testRun.id} 
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleViewTestRun(testRun.id)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {testRun.id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div>
                        <div className="font-medium">{testRun.name}</div>
                        {testRun.short_description && (
                          <div className="text-gray-500 text-xs mt-1">{testRun.short_description}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {testRun.run_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        testRun.status === 'Completed' ? 'bg-green-100 text-green-800' :
                        testRun.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {testRun.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{testRun.total_test_cases}</span>
                        <span className="text-gray-400">|</span>
                        <span className="text-green-600">✓ {testRun.passed_test_cases}</span>
                        <span className="text-red-600">✗ {testRun.failed_test_cases}</span>
                        <span className="text-yellow-600">⊘ {testRun.blocked_test_cases}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 w-24">
                          <div 
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${calculatePassRate(testRun)}%` }}
                          />
                        </div>
                        <span className="font-medium">{calculatePassRate(testRun)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleViewTestRun(testRun.id)
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
    </>
  )
}
