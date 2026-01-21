/**
 * Subtasks Page
 * List and manage subtasks with hierarchy selection
 */
import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import SubtaskModal from '../components/subtasks/SubtaskModal'
import type { Subtask, Task, UserStory, UseCase, Project, Program, Client, User, Phase } from '../types/entities'

export default function SubtasksPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [searchParams] = useSearchParams()
  
  // Helper function to safely format numbers
  const formatNumber = (value: any, decimals: number = 1): string => {
    if (value == null) return '-'
    const num = typeof value === 'number' ? value : Number(value)
    if (isNaN(num)) return '-'
    return num.toFixed(decimals)
  }
  
  // Hierarchy selections
  const [selectedClientId, setSelectedClientId] = useState<string>('')
  const [selectedProgramId, setSelectedProgramId] = useState<string>('')
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [selectedUseCaseId, setSelectedUseCaseId] = useState<string>('')
  const [selectedUserStoryId, setSelectedUserStoryId] = useState<string>('')
  const [selectedTaskId, setSelectedTaskId] = useState<string>('')
  
  // Data arrays
  const [clients, setClients] = useState<Client[]>([])
  const [programs, setPrograms] = useState<Program[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [usecases, setUsecases] = useState<UseCase[]>([])
  const [userstories, setUserstories] = useState<UserStory[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [subtasks, setSubtasks] = useState<Subtask[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [phases, setPhases] = useState<Phase[]>([])
  
  // Loading states
  const [loadingClients, setLoadingClients] = useState(true)
  const [loadingPrograms, setLoadingPrograms] = useState(false)
  const [loadingProjects, setLoadingProjects] = useState(false)
  const [loadingUseCases, setLoadingUseCases] = useState(false)
  const [loadingUserStories, setLoadingUserStories] = useState(false)
  const [loadingTasks, setLoadingTasks] = useState(false)
  const [loadingSubtasks, setLoadingSubtasks] = useState(false)
  
  // UI state
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingSubtask, setEditingSubtask] = useState<Subtask | null>(null)
  const [authError, setAuthError] = useState(false)
  
  const isAdmin = user?.role === 'Admin'

  // Load users and phases for assignment
  useEffect(() => {
    const loadUsersAndPhases = async () => {
      try {
        const [usersData, phasesData] = await Promise.all([
          api.getUsersSafe(),
          api.getPhasesSafe()
        ])
        setUsers(usersData)
        setPhases(phasesData)
      } catch (err) {
        console.error('Failed to load users or phases:', err)
      }
    }
    loadUsersAndPhases()
  }, [])

  // Load clients on mount and resolve hierarchy from URL
  useEffect(() => {
    const loadClients = async () => {
      try {
        const clientsData = await api.getClientsSafe()
        setClients(clientsData)
        
        // Parse URL parameters
        const clientParam = searchParams.get('client')
        const programParam = searchParams.get('program')
        const projectParam = searchParams.get('project')
        const usecaseParam = searchParams.get('usecase')
        const userstoryParam = searchParams.get('userstory')
        const taskParam = searchParams.get('task')
        
        // If task is passed but parent hierarchy isn't, resolve it
        if (taskParam && (!clientParam || !programParam || !projectParam || !usecaseParam || !userstoryParam)) {
          try {
            const allTasks = await api.getTasksSafe()
            const task = allTasks.find((t: any) => t.id === taskParam)
            if (task) {
              const taskUserStoryId = task.userStoryId || task.user_story_id
              if (taskUserStoryId && !userstoryParam) {
                // Find the user story to get usecase, project, program, client
                try {
                  const allStories = await api.getEntityListSafe('userstory')
                  const story = allStories.find((s: any) => s.id === taskUserStoryId)
                  if (story) {
                    const storyUseCaseId = story.usecaseId || story.usecase_id
                    if (storyUseCaseId && !usecaseParam) {
                      try {
                        const allUseCases = await api.getEntityListSafe('usecase')
                        const usecase = allUseCases.find((uc: any) => uc.id === storyUseCaseId)
                        if (usecase) {
                          const usecaseProjectId = usecase.projectId || usecase.project_id
                          if (usecaseProjectId && !projectParam) {
                            try {
                              const allProjects = await api.getProjectsSafe()
                              const project = allProjects.find((p: any) => p.id === usecaseProjectId)
                              if (project) {
                                const projectProgramId = project.programId
                                if (projectProgramId) {
                                  try {
                                    const allPrograms = await api.getEntityListSafe('program')
                                    const program = allPrograms.find((p: any) => p.id === projectProgramId)
                                    if (program) {
                                      const programClientId = program.client_id || program.clientId
                                      if (programClientId && !clientParam) {
                                        setSelectedClientId(programClientId)
                                      }
                                      if (!programParam) {
                                        setSelectedProgramId(projectProgramId)
                                      }
                                    }
                                  } catch (programErr) {
                                    console.warn('Failed to load programs for hierarchy resolution:', programErr)
                                  }
                                }
                                if (!projectParam) {
                                  setSelectedProjectId(usecaseProjectId)
                                }
                              }
                            } catch (projectErr) {
                              console.warn('Failed to load projects for hierarchy resolution:', projectErr)
                            }
                          }
                          if (!usecaseParam) {
                            setSelectedUseCaseId(storyUseCaseId)
                          }
                        }
                      } catch (usecaseErr) {
                        console.warn('Failed to load usecases for hierarchy resolution:', usecaseErr)
                      }
                    }
                    if (!userstoryParam) {
                      setSelectedUserStoryId(taskUserStoryId)
                    }
                  }
                } catch (storyErr) {
                  console.warn('Failed to load user stories for hierarchy resolution:', storyErr)
                }
              }
              if (taskParam) {
                setSelectedTaskId(taskParam)
              }
            }
          } catch (taskErr) {
            console.warn('Failed to load tasks for hierarchy resolution:', taskErr)
          }
        }
        
        // Set parameters if they exist
        if (clientParam) setSelectedClientId(clientParam)
        if (programParam) setSelectedProgramId(programParam)
        if (projectParam) setSelectedProjectId(projectParam)
        if (usecaseParam) setSelectedUseCaseId(usecaseParam)
        if (userstoryParam) setSelectedUserStoryId(userstoryParam)
        if (taskParam) setSelectedTaskId(taskParam)
      } catch (err) {
        console.error('Failed to load clients:', err)
      } finally {
        setLoadingClients(false)
      }
    }
    loadClients()
  }, [searchParams])

  // Load programs when client changes
  useEffect(() => {
    const loadPrograms = async () => {
      if (!selectedClientId) {
        setPrograms([])
        const programParam = searchParams.get('program')
        if (!programParam) {
          setSelectedProgramId('')
        }
        return
      }
      
      setLoadingPrograms(true)
      try {
        const allPrograms = await api.getEntityListSafe('program')
        // Check both camelCase and snake_case for client_id
        const filteredPrograms = allPrograms.filter((p: any) => 
          (p.clientId === selectedClientId || p.client_id === selectedClientId)
        )
        setPrograms(filteredPrograms)
      } catch (err) {
        console.error('Failed to load programs:', err)
      } finally {
        setLoadingPrograms(false)
      }
    }
    loadPrograms()
  }, [selectedClientId, searchParams])

  // Load projects when program changes
  useEffect(() => {
    const loadProjects = async () => {
      if (!selectedProgramId) {
        setProjects([])
        const projectParam = searchParams.get('project')
        if (!projectParam) {
          setSelectedProjectId('')
        }
        return
      }
      
      setLoadingProjects(true)
      try {
        const allProjects = await api.getProjectsSafe()
        // Check both camelCase and snake_case for program_id, filter out nulls
        const filteredProjects = allProjects
          .filter((p: any) => p !== null) // Filter out null values first
          .filter((p: any) => (p.programId === selectedProgramId))
        setProjects(filteredProjects as any[])
      } catch (err) {
        console.error('Failed to load projects:', err)
      } finally {
        setLoadingProjects(false)
      }
    }
    loadProjects()
  }, [selectedProgramId, searchParams])

  // Load use cases when project changes
  useEffect(() => {
    const loadUseCases = async () => {
      if (!selectedProjectId) {
        setUsecases([])
        const usecaseParam = searchParams.get('usecase')
        if (!usecaseParam) {
          setSelectedUseCaseId('')
        }
        return
      }
      
      setLoadingUseCases(true)
      try {
        const allUseCases = await api.getEntityListSafe('usecase')
        // Check both camelCase and snake_case for project_id
        const filteredUseCases = allUseCases.filter((uc: any) => 
          (uc.projectId === selectedProjectId || uc.project_id === selectedProjectId)
        )
        setUsecases(filteredUseCases)
      } catch (err) {
        console.error('Failed to load use cases:', err)
      } finally {
        setLoadingUseCases(false)
      }
    }
    loadUseCases()
  }, [selectedProjectId, searchParams])

  // Load user stories when use case changes
  useEffect(() => {
    const loadUserStories = async () => {
      if (!selectedUseCaseId) {
        setUserstories([])
        const userstoryParam = searchParams.get('userstory')
        if (!userstoryParam) {
          setSelectedUserStoryId('')
        }
        return
      }
      
      setLoadingUserStories(true)
      try {
        const allStories = await api.getEntityListSafe('userstory')
        // Check both camelCase and snake_case for usecase_id
        const filteredStories = allStories.filter((s: any) => 
          (s.usecaseId === selectedUseCaseId || s.usecase_id === selectedUseCaseId)
        )
        setUserstories(filteredStories)
      } catch (err) {
        console.error('Failed to load user stories:', err)
      } finally {
        setLoadingUserStories(false)
      }
    }
    loadUserStories()
  }, [selectedUseCaseId, searchParams])

  // Load tasks when user story changes
  useEffect(() => {
    const loadTasks = async () => {
      if (!selectedUserStoryId) {
        setTasks([])
        const taskParam = searchParams.get('task')
        if (!taskParam) {
          setSelectedTaskId('')
        }
        return
      }
      
      setLoadingTasks(true)
      try {
        const allTasks = await api.getTasksSafe()
        // Check both camelCase and snake_case for user_story_id
        const filteredTasks = allTasks.filter((t: any) => 
          (t.userStoryId === selectedUserStoryId || t.user_story_id === selectedUserStoryId)
        )
        setTasks(filteredTasks)
      } catch (err) {
        console.error('Failed to load tasks:', err)
      } finally {
        setLoadingTasks(false)
      }
    }
    loadTasks()
  }, [selectedUserStoryId, searchParams])

  // Load subtasks when task changes
  useEffect(() => {
    const loadSubtasks = async () => {
      if (!selectedTaskId) {
        setSubtasks([])
        return
      }
      
      setLoadingSubtasks(true)
      try {
        // Use safe API call that doesn't trigger logout on permission errors
        const allSubtasks = await api.getSubtasksSafe(selectedTaskId)
        
        // If we get a valid array response, filter it
        if (Array.isArray(allSubtasks)) {
          // Check both camelCase and snake_case for task_id
          const filteredSubtasks = allSubtasks.filter((st: any) => 
            (st.taskId === selectedTaskId || st.task_id === selectedTaskId)
          )
          setSubtasks(filteredSubtasks)
        } else {
          // If response is not an array, set empty array
          setSubtasks([])
        }
      } catch (err: any) {
        // Check if this is an authentication error
        if (err.response?.status === 401) {
          setAuthError(true)
        }
        // Always set empty array on error
        setSubtasks([])
      } finally {
        setLoadingSubtasks(false)
      }
    }
    loadSubtasks()
  }, [selectedTaskId])

  // Filter and sort subtasks
  const filteredSubtasks = useMemo(() => {
    return subtasks.filter((subtask: Subtask) => {
      const matchesSearch = !searchQuery || 
        subtask.name?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === 'all' || subtask.status === filterStatus
      return matchesSearch && matchesStatus
    })
  }, [subtasks, searchQuery, filterStatus])

  const statuses = Array.from(new Set(subtasks.map((st: Subtask) => st.status).filter(Boolean)))

  // Get selected entities for breadcrumb
  const selectedClient = clients.find(c => c.id === selectedClientId)
  const selectedProgram = programs.find(p => p.id === selectedProgramId)
  const selectedProject = projects.find(p => p.id === selectedProjectId)
  const selectedUseCase = usecases.find(uc => uc.id === selectedUseCaseId)
  const selectedUserStory = userstories.find(us => us.id === selectedUserStoryId)
  const selectedTask = tasks.find(t => t.id === selectedTaskId)

  // Show loading state
  if (loadingClients) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // Check if all required selections are made
  const hasRequiredSelections = selectedClientId && selectedProgramId && selectedProjectId && 
    selectedUseCaseId && selectedUserStoryId && selectedTaskId

  // Get user name for assigned_to field
  const getUserName = (userId?: string) => {
    if (!userId) return '-'
    const user = users.find(u => u.id === userId)
    return user?.full_name || '-'
  }

  // Get phase name for phase_id field
  const getPhaseName = (phaseId?: string) => {
    if (!phaseId) return '-'
    const phase = phases.find(p => p.id === phaseId)
    return phase?.name || '-'
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Subtasks</h1>
        <p className="text-sm sm:text-base text-gray-600 mt-1">Manage subtasks and track granular work items</p>
      </div>

      {/* Breadcrumb Navigation */}
      {(selectedClient || selectedProgram || selectedProject || selectedUseCase || selectedUserStory || selectedTask) && (
        <div className="mb-4 flex items-center gap-2 text-xs sm:text-sm overflow-x-auto pb-2">
          {selectedClient && (
            <>
              <button
                onClick={() => navigate(`/clients`)}
                className="text-blue-600 hover:text-blue-800 hover:underline font-medium whitespace-nowrap"
              >
                {selectedClient.name}
              </button>
              {selectedProgram && <span className="text-gray-400">→</span>}
            </>
          )}
          {selectedProgram && (
            <>
              <button
                onClick={() => navigate(`/programs/${selectedProgramId}`)}
                className="text-blue-600 hover:text-blue-800 hover:underline font-medium whitespace-nowrap"
              >
                {selectedProgram.name}
              </button>
              {selectedProject && <span className="text-gray-400">→</span>}
            </>
          )}
          {selectedProject && (
            <>
              <button
                onClick={() => navigate(`/projects/${selectedProjectId}`)}
                className="text-blue-600 hover:text-blue-800 hover:underline font-medium whitespace-nowrap"
              >
                {selectedProject.name}
              </button>
              {selectedUseCase && <span className="text-gray-400">→</span>}
            </>
          )}
          {selectedUseCase && (
            <>
              <button
                onClick={() => navigate(`/usecases?client=${selectedClientId}&program=${selectedProgramId}&project=${selectedProjectId}`)}
                className="text-blue-600 hover:text-blue-800 hover:underline font-medium whitespace-nowrap"
              >
                {selectedUseCase.name}
              </button>
              {selectedUserStory && <span className="text-gray-400">→</span>}
            </>
          )}
          {selectedUserStory && (
            <>
              <button
                onClick={() => navigate(`/userstories?client=${selectedClientId}&program=${selectedProgramId}&project=${selectedProjectId}&usecase=${selectedUseCaseId}`)}
                className="text-blue-600 hover:text-blue-800 hover:underline font-medium whitespace-nowrap"
              >
                {selectedUserStory.name}
              </button>
              {selectedTask && <span className="text-gray-400">→</span>}
            </>
          )}
          {selectedTask && (
            <button
              onClick={() => navigate(`/tasks?client=${selectedClientId}&program=${selectedProgramId}&project=${selectedProjectId}&usecase=${selectedUseCaseId}&userstory=${selectedUserStoryId}`)}
              className="text-blue-600 hover:text-blue-800 hover:underline font-medium whitespace-nowrap"
            >
              {selectedTask.name}
            </button>
          )}
        </div>
      )}
      
      {/* Compact Hierarchy Filter Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-4 mb-6">
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
            <span className="text-xs sm:text-sm font-medium text-gray-700 whitespace-nowrap">Client:</span>
            <select
              value={selectedClientId}
              onChange={(e) => setSelectedClientId(e.target.value)}
              className="px-2 sm:px-3 py-1 sm:py-1.5 text-xs sm:text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[120px]"
            >
              <option value="">Select...</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>

          {selectedClientId && (
            <>
              <span className="text-gray-400 hidden sm:inline">→</span>
              <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
                <span className="text-xs sm:text-sm font-medium text-gray-700 whitespace-nowrap">Program:</span>
                <select
                  value={selectedProgramId}
                  onChange={(e) => setSelectedProgramId(e.target.value)}
                  disabled={loadingPrograms}
                  className="px-2 sm:px-3 py-1 sm:py-1.5 text-xs sm:text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 min-w-[120px]"
                >
                  <option value="">Select...</option>
                  {programs.map((program) => (
                    <option key={program.id} value={program.id}>
                      {program.name}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          {selectedProgramId && (
            <>
              <span className="text-gray-400 hidden sm:inline">→</span>
              <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
                <span className="text-xs sm:text-sm font-medium text-gray-700 whitespace-nowrap">Project:</span>
                <select
                  value={selectedProjectId}
                  onChange={(e) => setSelectedProjectId(e.target.value)}
                  disabled={loadingProjects}
                  className="px-2 sm:px-3 py-1 sm:py-1.5 text-xs sm:text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 min-w-[120px]"
                >
                  <option value="">Select...</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          {selectedProjectId && (
            <>
              <span className="text-gray-400 hidden sm:inline">→</span>
              <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
                <span className="text-xs sm:text-sm font-medium text-gray-700 whitespace-nowrap">Use Case:</span>
                <select
                  value={selectedUseCaseId}
                  onChange={(e) => setSelectedUseCaseId(e.target.value)}
                  disabled={loadingUseCases}
                  className="px-2 sm:px-3 py-1 sm:py-1.5 text-xs sm:text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 min-w-[120px]"
                >
                  <option value="">Select...</option>
                  {usecases.map((usecase) => (
                    <option key={usecase.id} value={usecase.id}>
                      {usecase.name}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          {selectedUseCaseId && (
            <>
              <span className="text-gray-400 hidden sm:inline">→</span>
              <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
                <span className="text-xs sm:text-sm font-medium text-gray-700 whitespace-nowrap">User Story:</span>
                <select
                  value={selectedUserStoryId}
                  onChange={(e) => setSelectedUserStoryId(e.target.value)}
                  disabled={loadingUserStories}
                  className="px-2 sm:px-3 py-1 sm:py-1.5 text-xs sm:text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 min-w-[120px]"
                >
                  <option value="">Select...</option>
                  {userstories.map((story) => (
                    <option key={story.id} value={story.id}>
                      {story.name}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          {selectedUserStoryId && (
            <>
              <span className="text-gray-400 hidden sm:inline">→</span>
              <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
                <span className="text-xs sm:text-sm font-medium text-gray-700 whitespace-nowrap">Task:</span>
                <select
                  value={selectedTaskId}
                  onChange={(e) => setSelectedTaskId(e.target.value)}
                  disabled={loadingTasks}
                  className="px-2 sm:px-3 py-1 sm:py-1.5 text-xs sm:text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 min-w-[120px]"
                >
                  <option value="">Select...</option>
                  {tasks.map((task) => (
                    <option key={task.id} value={task.id}>
                      {task.name}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Show authentication error modal - blocks interaction */}
      {authError && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md mx-4">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg className="h-10 w-10 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-medium text-gray-900">
                Session Expired
              </h3>
            </div>
            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-2">
                Your authentication session has expired after 30 minutes of inactivity.
              </p>
              <p className="text-sm text-gray-600 mb-2">
                <strong>To view subtasks, you must log in again.</strong>
              </p>
              <p className="text-xs text-gray-500">
                This is a security measure to protect your account.
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  localStorage.removeItem('token')
                  window.location.href = '/login'
                }}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Go to Login
              </button>
              <button
                onClick={() => setAuthError(false)}
                className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-300 transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Show message if selections not made */}
      {!hasRequiredSelections && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <div className="text-blue-600 font-medium mb-1">
            Please select Client, Program, Project, Use Case, User Story, and Task
          </div>
          <p className="text-blue-600 text-sm">
            Subtasks are organized under tasks. Please make all selections above to view subtasks.
          </p>
        </div>
      )}

      {/* Show content only when all selections are made */}
      {hasRequiredSelections && (
        <>
          {/* Filters */}
          <div className="bg-white rounded-lg shadow p-3 sm:p-4 mb-6">
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <input
                type="text"
                placeholder="Search subtasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Status</option>
                {statuses.map((status: string) => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
              <button 
                onClick={() => {
                  setEditingSubtask(null)
                  setIsModalOpen(true)
                }}
                disabled={!isAdmin || !selectedTaskId}
                className={`px-4 sm:px-6 py-2 text-sm sm:text-base rounded-lg transition-colors whitespace-nowrap ${
                  isAdmin && selectedTaskId
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
                title={
                  !isAdmin ? 'Only Admin users can create subtasks' : 
                  !selectedTaskId ? 'Please select a task first' : 
                  'Create new subtask'
                }
              >
                + New Subtask
              </button>
            </div>
          </div>
          
          {/* Subtasks List */}
          {loadingSubtasks ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              {/* Desktop Table View */}
              <div className="hidden lg:block overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Title
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Assigned To
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Phase
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Est. Hours
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Duration
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Points
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredSubtasks.map((subtask: Subtask) => (
                      <tr
                        key={subtask.id}
                        onClick={() => navigate(`/hierarchy/subtask/${subtask.id}`)}
                        className="hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{subtask.name}</div>
                          {subtask.short_description && (
                            <div className="text-sm text-gray-500 line-clamp-1">{subtask.short_description}</div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            subtask.status === 'Done' ? 'bg-green-100 text-green-800' :
                            subtask.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {subtask.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {getUserName(subtask.assigned_to)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {getPhaseName(subtask.phase_id)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatNumber(subtask.estimated_hours)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {subtask.duration_days || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatNumber(subtask.scrum_points)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile/Tablet Card View */}
              <div className="lg:hidden divide-y divide-gray-200">
                {filteredSubtasks.map((subtask: Subtask) => (
                  <div
                    key={subtask.id}
                    onClick={() => navigate(`/hierarchy/subtask/${subtask.id}`)}
                    className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 truncate">{subtask.name}</h3>
                        {subtask.short_description && (
                          <p className="text-xs text-gray-500 line-clamp-2 mt-1">{subtask.short_description}</p>
                        )}
                      </div>
                      <span className={`ml-2 px-2 py-1 text-xs font-medium rounded whitespace-nowrap ${
                        subtask.status === 'Done' ? 'bg-green-100 text-green-800' :
                        subtask.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {subtask.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-gray-500">Assigned:</span>
                        <span className="ml-1 text-gray-900">{getUserName(subtask.assigned_to)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Phase:</span>
                        <span className="ml-1 text-gray-900">{getPhaseName(subtask.phase_id)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Est. Hours:</span>
                        <span className="ml-1 text-gray-900">
                          {formatNumber(subtask.estimated_hours)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Duration:</span>
                        <span className="ml-1 text-gray-900">{subtask.duration_days || '-'} days</span>
                      </div>
                      {subtask.scrum_points != null && (
                        <div>
                          <span className="text-gray-500">Points:</span>
                          <span className="ml-1 text-gray-900">{formatNumber(subtask.scrum_points)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              {filteredSubtasks.length === 0 && (
                <div className="text-center py-12">
                  <div className="text-blue-600 mb-2">
                    <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012-2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                    </svg>
                  </div>
                  <p className="text-sm sm:text-base text-gray-600 font-medium mb-1">
                    No subtasks available for this task
                  </p>
                  <p className="text-xs text-gray-500 mb-3">
                    {!isAdmin 
                      ? "You can only view subtasks that are assigned to you. Contact your administrator if you need access to other subtasks." 
                      : "No subtasks have been created for this task yet. Click 'New Subtask' to create one."
                    }
                  </p>
                  <p className="text-xs text-gray-400 italic">
                    💡 If you believe there should be subtasks here, try refreshing the page or logging in again.
                  </p>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Subtask Modal */}
      <SubtaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={async () => {
          try {
            // Use safe API call that doesn't trigger logout on permission errors
            const allSubtasks = await api.getSubtasksSafe(selectedTaskId)
            
            // If we get a valid array response, filter it
            if (Array.isArray(allSubtasks)) {
              const filteredSubtasks = allSubtasks.filter((st: any) => st.task_id === selectedTaskId)
              setSubtasks(filteredSubtasks)
            } else {
              setSubtasks([])
            }
          } catch (err: any) {
            // Always set empty array on error
            setSubtasks([])
          }
        }}
        subtask={editingSubtask}
        selectedClientId={selectedClientId}
        selectedProgramId={selectedProgramId}
        selectedProjectId={selectedProjectId}
        selectedUseCaseId={selectedUseCaseId}
        selectedUserStoryId={selectedUserStoryId}
        selectedTaskId={selectedTaskId}
        clients={clients}
        programs={programs}
        projects={projects}
        usecases={usecases}
        userstories={userstories}
        tasks={tasks}
        users={users}
        phases={phases}
        isAdmin={isAdmin}
      />
    </div>
  )
}
