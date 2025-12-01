/**
 * BugLifecyclePage Component
 * Hierarchical bug viewing with advanced filtering
 * Requirements: 4.1, 6.1, 6.2, 6.3, 6.6, 6.7
 */
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import Modal from '../components/common/Modal'
import BugForm from '../components/forms/BugForm'
import BugDetails from '../components/bugs/BugDetails'
import BugMetricsDashboard from '../components/qa/BugMetricsDashboard'
import { Bug, SEVERITY_OPTIONS } from '../types/entities'

interface HierarchySelection {
  clientId?: string
  programId?: string
  projectId?: string
  usecaseId?: string
  userStoryId?: string
  taskId?: string
  subtaskId?: string
}

interface BugFilters {
  status: string[]
  severity: string[]
  priority: string[]
  bugType: string
  assignee: string
  reporter: string
  dateFrom: string
  dateTo: string
  search: string
}

export default function BugLifecyclePage() {
  const { t } = useTranslation()
  
  // Hierarchy selection state
  const [hierarchySelection, setHierarchySelection] = useState<HierarchySelection>({})
  const [includeDescendants, setIncludeDescendants] = useState(true)
  
  // Data state
  const [bugs, setBugs] = useState<Bug[]>([])
  const [filteredBugs, setFilteredBugs] = useState<Bug[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedBug, setSelectedBug] = useState<Bug | null>(null)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  
  // Hierarchy data
  const [clients, setClients] = useState<any[]>([])
  const [programs, setPrograms] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [usecases, setUsecases] = useState<any[]>([])
  const [userStories, setUserStories] = useState<any[]>([])
  const [tasks, setTasks] = useState<any[]>([])
  const [subtasks, setSubtasks] = useState<any[]>([])
  const [users, setUsers] = useState<any[]>([])
  
  // Filter state
  const [filters, setFilters] = useState<BugFilters>({
    status: [],
    severity: [],
    priority: [],
    bugType: '',
    assignee: '',
    reporter: '',
    dateFrom: '',
    dateTo: '',
    search: ''
  })
  const [showFilters, setShowFilters] = useState(false)
  
  // View mode state
  const [viewMode, setViewMode] = useState<'list' | 'metrics'>('list')
  
  // Load initial data
  useEffect(() => {
    loadClients()
    loadUsers()
  }, [])
  
  // Load hierarchy data based on selection
  useEffect(() => {
    if (hierarchySelection.clientId) loadPrograms(hierarchySelection.clientId)
  }, [hierarchySelection.clientId])
  
  useEffect(() => {
    if (hierarchySelection.programId) loadProjects(hierarchySelection.programId)
  }, [hierarchySelection.programId])
  
  useEffect(() => {
    if (hierarchySelection.projectId) loadUseCases(hierarchySelection.projectId)
  }, [hierarchySelection.projectId])
  
  useEffect(() => {
    if (hierarchySelection.usecaseId) loadUserStories(hierarchySelection.usecaseId)
  }, [hierarchySelection.usecaseId])
  
  useEffect(() => {
    if (hierarchySelection.userStoryId) loadTasks(hierarchySelection.userStoryId)
  }, [hierarchySelection.userStoryId])
  
  useEffect(() => {
    if (hierarchySelection.taskId) loadSubtasks(hierarchySelection.taskId)
  }, [hierarchySelection.taskId])
  
  // Apply filters when bugs or filters change
  useEffect(() => {
    applyFilters()
  }, [bugs, filters])
  
  const loadClients = async () => {
    try {
      const data = await api.getClients()
      setClients(data)
    } catch (error) {
      console.error('Failed to load clients:', error)
    }
  }
  
  const loadPrograms = async (clientId: string) => {
    try {
      const data = await api.getPrograms(clientId)
      setPrograms(data)
    } catch (error) {
      console.error('Failed to load programs:', error)
    }
  }
  
  const loadProjects = async (programId: string) => {
    try {
      const data = await api.getEntityList('project', { program_id: programId })
      setProjects(data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }
  
  const loadUseCases = async (projectId: string) => {
    try {
      const data = await api.getUseCases(projectId)
      setUsecases(data)
    } catch (error) {
      console.error('Failed to load use cases:', error)
    }
  }
  
  const loadUserStories = async (usecaseId: string) => {
    try {
      const data = await api.getUserStories(usecaseId)
      setUserStories(data)
    } catch (error) {
      console.error('Failed to load user stories:', error)
    }
  }
  
  const loadTasks = async (userStoryId: string) => {
    try {
      const data = await api.getEntityList('task', { user_story_id: userStoryId })
      setTasks(data)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    }
  }
  
  const loadSubtasks = async (taskId: string) => {
    try {
      const data = await api.getSubtasks(taskId)
      setSubtasks(data)
    } catch (error) {
      console.error('Failed to load subtasks:', error)
    }
  }
  
  const loadUsers = async () => {
    try {
      const data = await api.getUsers()
      setUsers(data)
    } catch (error) {
      console.error('Failed to load users:', error)
    }
  }
  
  const loadBugs = async () => {
    try {
      setLoading(true)
      
      // Build query parameters based on hierarchy selection
      const params: any = {
        include_descendants: includeDescendants
      }
      
      if (hierarchySelection.clientId) params.client_id = hierarchySelection.clientId
      if (hierarchySelection.programId) params.program_id = hierarchySelection.programId
      if (hierarchySelection.projectId) params.project_id = hierarchySelection.projectId
      if (hierarchySelection.usecaseId) params.usecase_id = hierarchySelection.usecaseId
      if (hierarchySelection.userStoryId) params.user_story_id = hierarchySelection.userStoryId
      if (hierarchySelection.taskId) params.task_id = hierarchySelection.taskId
      if (hierarchySelection.subtaskId) params.subtask_id = hierarchySelection.subtaskId
      
      const data = await api.get('/bugs/hierarchy', { params })
      setBugs(data)
    } catch (error) {
      console.error('Failed to load bugs:', error)
      setBugs([])
    } finally {
      setLoading(false)
    }
  }
  
  const applyFilters = () => {
    let filtered = [...bugs]
    
    // Status filter
    if (filters.status.length > 0) {
      filtered = filtered.filter(bug => filters.status.includes(bug.status))
    }
    
    // Severity filter
    if (filters.severity.length > 0) {
      filtered = filtered.filter(bug => filters.severity.includes(bug.severity))
    }
    
    // Priority filter
    if (filters.priority.length > 0) {
      filtered = filtered.filter(bug => filters.priority.includes(bug.priority))
    }
    
    // Bug type filter
    if (filters.bugType) {
      filtered = filtered.filter(bug => (bug as any).bug_type === filters.bugType)
    }
    
    // Assignee filter
    if (filters.assignee) {
      filtered = filtered.filter(bug => bug.assigned_to === filters.assignee)
    }
    
    // Reporter filter
    if (filters.reporter) {
      filtered = filtered.filter(bug => bug.reported_by === filters.reporter)
    }
    
    // Date range filter
    if (filters.dateFrom) {
      const fromDate = new Date(filters.dateFrom)
      filtered = filtered.filter(bug => new Date(bug.created_at) >= fromDate)
    }
    
    if (filters.dateTo) {
      const toDate = new Date(filters.dateTo)
      toDate.setHours(23, 59, 59, 999)
      filtered = filtered.filter(bug => new Date(bug.created_at) <= toDate)
    }
    
    // Search filter
    if (filters.search) {
      const query = filters.search.toLowerCase()
      filtered = filtered.filter(bug =>
        bug.title.toLowerCase().includes(query) ||
        bug.short_description?.toLowerCase().includes(query) ||
        bug.long_description?.toLowerCase().includes(query) ||
        bug.id.toLowerCase().includes(query)
      )
    }
    
    setFilteredBugs(filtered)
  }
  
  const handleHierarchyChange = (level: string, value: string) => {
    const newSelection: HierarchySelection = {}
    
    // Reset all levels below the changed level
    if (level === 'client') {
      newSelection.clientId = value
    } else if (level === 'program') {
      newSelection.clientId = hierarchySelection.clientId
      newSelection.programId = value
    } else if (level === 'project') {
      newSelection.clientId = hierarchySelection.clientId
      newSelection.programId = hierarchySelection.programId
      newSelection.projectId = value
    } else if (level === 'usecase') {
      newSelection.clientId = hierarchySelection.clientId
      newSelection.programId = hierarchySelection.programId
      newSelection.projectId = hierarchySelection.projectId
      newSelection.usecaseId = value
    } else if (level === 'userStory') {
      newSelection.clientId = hierarchySelection.clientId
      newSelection.programId = hierarchySelection.programId
      newSelection.projectId = hierarchySelection.projectId
      newSelection.usecaseId = hierarchySelection.usecaseId
      newSelection.userStoryId = value
    } else if (level === 'task') {
      newSelection.clientId = hierarchySelection.clientId
      newSelection.programId = hierarchySelection.programId
      newSelection.projectId = hierarchySelection.projectId
      newSelection.usecaseId = hierarchySelection.usecaseId
      newSelection.userStoryId = hierarchySelection.userStoryId
      newSelection.taskId = value
    } else if (level === 'subtask') {
      newSelection.clientId = hierarchySelection.clientId
      newSelection.programId = hierarchySelection.programId
      newSelection.projectId = hierarchySelection.projectId
      newSelection.usecaseId = hierarchySelection.usecaseId
      newSelection.userStoryId = hierarchySelection.userStoryId
      newSelection.taskId = hierarchySelection.taskId
      newSelection.subtaskId = value
    }
    
    setHierarchySelection(newSelection)
  }
  
  const handleCreateBug = async (data: any) => {
    try {
      await api.createBug(data)
      setIsCreateModalOpen(false)
      loadBugs()
    } catch (error) {
      console.error('Failed to create bug:', error)
    }
  }
  
  const handleFilterChange = (field: keyof BugFilters, value: any) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }
  
  const clearFilters = () => {
    setFilters({
      status: [],
      severity: [],
      priority: [],
      bugType: '',
      assignee: '',
      reporter: '',
      dateFrom: '',
      dateTo: '',
      search: ''
    })
  }
  
  const hasActiveFilters = () => {
    return filters.status.length > 0 ||
           filters.severity.length > 0 ||
           filters.priority.length > 0 ||
           filters.bugType !== '' ||
           filters.assignee !== '' ||
           filters.reporter !== '' ||
           filters.dateFrom !== '' ||
           filters.dateTo !== '' ||
           filters.search !== ''
  }
  
  const canViewBugs = () => {
    return Object.values(hierarchySelection).some(v => v !== undefined && v !== '')
  }
  
  const getHierarchyPath = (bug: Bug) => {
    const parts: string[] = []
    // This would be populated from bug data with hierarchy information
    return parts.join(' > ') || 'N/A'
  }
  
  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      'Critical': 'bg-red-100 text-red-800 border-red-300',
      'High': 'bg-orange-100 text-orange-800 border-orange-300',
      'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Low': 'bg-green-100 text-green-800 border-green-300'
    }
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-300'
  }
  
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'New': 'bg-blue-100 text-blue-800 border-blue-300',
      'Open': 'bg-purple-100 text-purple-800 border-purple-300',
      'In Progress': 'bg-indigo-100 text-indigo-800 border-indigo-300',
      'Fixed': 'bg-teal-100 text-teal-800 border-teal-300',
      'Ready for Testing': 'bg-cyan-100 text-cyan-800 border-cyan-300',
      'Verified': 'bg-green-100 text-green-800 border-green-300',
      'Closed': 'bg-gray-100 text-gray-800 border-gray-300',
      'Reopened': 'bg-red-100 text-red-800 border-red-300',
      'Deferred': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Rejected': 'bg-gray-100 text-gray-800 border-gray-300'
    }
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300'
  }
  
  const formatDate = (date: string | undefined) => {
    if (!date) return 'N/A'
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }
  
  const STATUS_OPTIONS = ['New', 'Open', 'In Progress', 'Fixed', 'Ready for Testing', 'Retest', 'Verified', 'Closed', 'Reopened', 'Deferred', 'Rejected']
  const PRIORITY_OPTIONS = ['P0', 'P1', 'P2', 'P3']
  const BUG_TYPE_OPTIONS = ['Functional', 'Performance', 'Security', 'UI/UX', 'Data', 'Integration', 'Configuration']
  
  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Bug Lifecycle</h1>
            <p className="text-sm text-gray-600 mt-1">
              View and manage bugs across the project hierarchy
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* View Mode Toggle */}
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'list'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📋 List View
              </button>
              <button
                onClick={() => setViewMode('metrics')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'metrics'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📊 Metrics
              </button>
            </div>
            
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M12 4v16m8-8H4" />
              </svg>
              Create Bug
            </button>
          </div>
        </div>
      </div>
      
      {/* Hierarchical Selector */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Select Hierarchy Level</h2>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={includeDescendants}
                onChange={(e) => setIncludeDescendants(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              Include descendants
            </label>
            <button
              onClick={loadBugs}
              disabled={!canViewBugs() || loading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              View Bugs
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-4 gap-4">
          {/* Client */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Client</label>
            <select
              value={hierarchySelection.clientId || ''}
              onChange={(e) => handleHierarchyChange('client', e.target.value)}
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Program</label>
            <select
              value={hierarchySelection.programId || ''}
              onChange={(e) => handleHierarchyChange('program', e.target.value)}
              disabled={!hierarchySelection.clientId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Select Program</option>
              {programs.map(program => (
                <option key={program.id} value={program.id}>{program.name}</option>
              ))}
            </select>
          </div>
          
          {/* Project */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project</label>
            <select
              value={hierarchySelection.projectId || ''}
              onChange={(e) => handleHierarchyChange('project', e.target.value)}
              disabled={!hierarchySelection.programId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Select Project</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>{project.name}</option>
              ))}
            </select>
          </div>
          
          {/* Use Case */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Use Case</label>
            <select
              value={hierarchySelection.usecaseId || ''}
              onChange={(e) => handleHierarchyChange('usecase', e.target.value)}
              disabled={!hierarchySelection.projectId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Select Use Case</option>
              {usecases.map(usecase => (
                <option key={usecase.id} value={usecase.id}>{usecase.name}</option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-4 mt-4">
          {/* User Story */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">User Story</label>
            <select
              value={hierarchySelection.userStoryId || ''}
              onChange={(e) => handleHierarchyChange('userStory', e.target.value)}
              disabled={!hierarchySelection.usecaseId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Select User Story</option>
              {userStories.map(story => (
                <option key={story.id} value={story.id}>{story.name}</option>
              ))}
            </select>
          </div>
          
          {/* Task */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Task</label>
            <select
              value={hierarchySelection.taskId || ''}
              onChange={(e) => handleHierarchyChange('task', e.target.value)}
              disabled={!hierarchySelection.userStoryId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Select Task</option>
              {tasks.map(task => (
                <option key={task.id} value={task.id}>{task.name || task.title}</option>
              ))}
            </select>
          </div>
          
          {/* Subtask */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Subtask</label>
            <select
              value={hierarchySelection.subtaskId || ''}
              onChange={(e) => handleHierarchyChange('subtask', e.target.value)}
              disabled={!hierarchySelection.taskId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Select Subtask</option>
              {subtasks.map(subtask => (
                <option key={subtask.id} value={subtask.id}>{subtask.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Filters Bar */}
      <div className="bg-white border-b px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
            
            {hasActiveFilters() && (
              <button
                onClick={clearFilters}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Clear All Filters
              </button>
            )}
          </div>
          
          <div className="text-sm text-gray-600">
            Showing {filteredBugs.length} of {bugs.length} bugs
          </div>
        </div>
        
        {/* Advanced Filters Panel */}
        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="grid grid-cols-4 gap-4">
              {/* Search */}
              <div className="col-span-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  placeholder="Search by title, description, or ID..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  multiple
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  size={4}
                >
                  {STATUS_OPTIONS.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
              </div>
              
              {/* Severity Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                <select
                  multiple
                  value={filters.severity}
                  onChange={(e) => handleFilterChange('severity', Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  size={4}
                >
                  {SEVERITY_OPTIONS.map(severity => (
                    <option key={severity} value={severity}>{severity}</option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
              </div>
              
              {/* Priority Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <select
                  multiple
                  value={filters.priority}
                  onChange={(e) => handleFilterChange('priority', Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  size={4}
                >
                  {PRIORITY_OPTIONS.map(priority => (
                    <option key={priority} value={priority}>{priority}</option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
              </div>
              
              {/* Bug Type Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bug Type</label>
                <select
                  value={filters.bugType}
                  onChange={(e) => handleFilterChange('bugType', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  {BUG_TYPE_OPTIONS.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              
              {/* Assignee Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Assignee</label>
                <select
                  value={filters.assignee}
                  onChange={(e) => handleFilterChange('assignee', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Assignees</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.full_name || user.fullName}</option>
                  ))}
                </select>
              </div>
              
              {/* Reporter Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reporter</label>
                <select
                  value={filters.reporter}
                  onChange={(e) => handleFilterChange('reporter', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Reporters</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.full_name || user.fullName}</option>
                  ))}
                </select>
              </div>
              
              {/* Date From */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date From</label>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              {/* Date To */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date To</label>
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {viewMode === 'metrics' ? (
          /* Metrics Dashboard View */
          <BugMetricsDashboard hierarchyFilter={hierarchySelection} />
        ) : (
          /* Bug List View */
          <>
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : bugs.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <svg className="w-16 h-16 text-gray-300 mb-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-1">No Bugs Found</h3>
                <p className="text-gray-500 mb-4">
                  {canViewBugs() 
                    ? 'No bugs found for the selected hierarchy level'
                    : 'Select a hierarchy level and click "View Bugs" to see bugs'
                  }
                </p>
              </div>
            ) : filteredBugs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <svg className="w-16 h-16 text-gray-300 mb-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-1">No Bugs Match Filters</h3>
            <p className="text-gray-500 mb-4">Try adjusting your filters to see more results</p>
            <button
              onClick={clearFilters}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredBugs.map(bug => (
              <div
                key={bug.id}
                onClick={() => setSelectedBug(bug)}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-blue-300 transition-all cursor-pointer group"
              >
                {/* Bug Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-gray-500">{bug.id}</span>
                      <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {bug.title}
                      </h3>
                    </div>
                    {bug.short_description && (
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {bug.short_description}
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Badges */}
                <div className="flex items-center gap-2 flex-wrap mb-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded border ${getSeverityColor(bug.severity)}`}>
                    {bug.severity}
                  </span>
                  <span className="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-800 border border-gray-300">
                    {bug.priority}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(bug.status)}`}>
                    {bug.status}
                  </span>
                  {(bug as any).bug_type && (
                    <span className="px-2 py-1 text-xs font-medium rounded bg-purple-100 text-purple-800 border border-purple-300">
                      {(bug as any).bug_type}
                    </span>
                  )}
                </div>
                
                {/* Footer */}
                <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
                  <div className="flex items-center gap-4">
                    {bug.reported_by && (
                      <div className="flex items-center gap-1">
                        <svg className="w-3.5 h-3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                          <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        <span>Reported by {bug.reported_by}</span>
                      </div>
                    )}
                    {bug.assigned_to && (
                      <div className="flex items-center gap-1">
                        <svg className="w-3.5 h-3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <span>Assigned to {bug.assigned_to}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-1">
                      <svg className="w-3.5 h-3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span>{formatDate(bug.created_at)}</span>
                    </div>
                  </div>
                  <span className="text-blue-600 font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    View Details
                    <svg className="w-3 h-3" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M9 5l7 7-7 7" />
                    </svg>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
          </>
        )}
      </div>
      
      {/* Create Bug Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create Bug"
        size="lg"
      >
        <BugForm
          onSubmit={handleCreateBug}
          onCancel={() => setIsCreateModalOpen(false)}
          initialData={hierarchySelection.clientId ? {
            entity_type: hierarchySelection.subtaskId ? 'Subtask' :
                        hierarchySelection.taskId ? 'Task' :
                        hierarchySelection.userStoryId ? 'UserStory' :
                        hierarchySelection.usecaseId ? 'UseCase' :
                        hierarchySelection.projectId ? 'Project' :
                        hierarchySelection.programId ? 'Program' : 'Client',
            entity_id: hierarchySelection.subtaskId ||
                      hierarchySelection.taskId ||
                      hierarchySelection.userStoryId ||
                      hierarchySelection.usecaseId ||
                      hierarchySelection.projectId ||
                      hierarchySelection.programId ||
                      hierarchySelection.clientId
          } : undefined}
        />
      </Modal>
      
      {/* Bug Details Modal */}
      {selectedBug && (
        <Modal
          isOpen={!!selectedBug}
          onClose={() => setSelectedBug(null)}
          title=""
          size="xl"
        >
          <BugDetails
            bug={selectedBug}
            onUpdate={() => {
              setSelectedBug(null)
              loadBugs()
            }}
            onClose={() => setSelectedBug(null)}
          />
        </Modal>
      )}
    </div>
  )
}
