/**
 * Tasks Page
 * List and manage tasks with hierarchy selection
 */
import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import TaskModal from '../components/tasks/TaskModal'
import { formatDateForDisplay } from '../utils/dateUtils'
import { useUserStoryTasks } from '../hooks/useTasks'

export default function TasksPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [searchParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [selectedClientId, setSelectedClientId] = useState<string>('')
  const [selectedProgramId, setSelectedProgramId] = useState<string>('')
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [selectedUseCaseId, setSelectedUseCaseId] = useState<string>('')
  const [selectedUserStoryId, setSelectedUserStoryId] = useState<string>('')
  const [clients, setClients] = useState<any[]>([])
  const [programs, setPrograms] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [usecases, setUsecases] = useState<any[]>([])
  const [userstories, setUserstories] = useState<any[]>([])
  const [users, setUsers] = useState<any[]>([])
  const [loadingClients, setLoadingClients] = useState(true)
  const [loadingPrograms, setLoadingPrograms] = useState(false)
  const [loadingProjects, setLoadingProjects] = useState(false)
  const [loadingUseCases, setLoadingUseCases] = useState(false)
  const [loadingUserStories, setLoadingUserStories] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingTask, setEditingTask] = useState<any>(null)
  
  // Use React Query for task management - shares cache with KanbanPage
  const { data: tasks = [], isLoading: loadingTasks } = useUserStoryTasks(selectedUserStoryId)
  
  const isAdmin = user?.role === 'Admin'

  // Load users for assignment
  useEffect(() => {
    const loadUsers = async () => {
      try {
        const usersData = await api.getUsers()
        setUsers(usersData)
      } catch (err) {
        console.error('Failed to load users:', err)
      }
    }
    loadUsers()
  }, [])

  // Load clients on mount and resolve hierarchy from URL
  useEffect(() => {
    const loadClients = async () => {
      try {
        const clientsData = await api.getClients()
        setClients(clientsData)
        
        const clientParam = searchParams.get('client')
        const programParam = searchParams.get('program')
        const projectParam = searchParams.get('project')
        const usecaseParam = searchParams.get('usecase')
        const userstoryParam = searchParams.get('userstory')
        
        // If project is passed but client/program aren't, resolve hierarchy
        if (projectParam && (!clientParam || !programParam)) {
          try {
            const allProjects = await api.getProjects()
            const project = allProjects.find((p: any) => p.id === projectParam)
            if (project) {
              const projectProgramId = project.programId || project.program_id
              if (projectProgramId && !programParam) {
                const allPrograms = await api.getEntityList('program')
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
              }
            }
          } catch (err) {
            console.error('Failed to resolve project hierarchy:', err)
          }
        }
        
        // If usecase is passed but parent hierarchy isn't, resolve it
        if (usecaseParam && (!clientParam || !programParam || !projectParam)) {
          try {
            const allUseCases = await api.getEntityList('usecase')
            const usecase = allUseCases.find((uc: any) => uc.id === usecaseParam)
            if (usecase) {
              const usecaseProjectId = usecase.projectId || usecase.project_id
              if (usecaseProjectId && !projectParam) {
                const allProjects = await api.getProjects()
                const project = allProjects.find((p: any) => p.id === usecaseProjectId)
                if (project) {
                  const projectProgramId = project.programId || project.program_id
                  if (projectProgramId) {
                    const allPrograms = await api.getEntityList('program')
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
                  }
                  if (!projectParam) {
                    setSelectedProjectId(usecaseProjectId)
                  }
                }
              }
              if (usecaseParam) {
                setSelectedUseCaseId(usecaseParam)
              }
            }
          } catch (err) {
            console.error('Failed to resolve usecase hierarchy:', err)
          }
        }
        
        // If userstory is passed but parent hierarchy isn't, resolve it
        if (userstoryParam && (!clientParam || !programParam || !projectParam || !usecaseParam)) {
          try {
            const allStories = await api.getEntityList('userstory')
            const story = allStories.find((s: any) => s.id === userstoryParam)
            if (story) {
              const storyUseCaseId = story.usecaseId || story.usecase_id
              if (storyUseCaseId && !usecaseParam) {
                // Find the usecase to get project, program, client
                const allUseCases = await api.getEntityList('usecase')
                const usecase = allUseCases.find((uc: any) => uc.id === storyUseCaseId)
                if (usecase) {
                  const usecaseProjectId = usecase.projectId || usecase.project_id
                  if (usecaseProjectId && !projectParam) {
                    // Find the project to get program and client
                    const allProjects = await api.getProjects()
                    const project = allProjects.find((p: any) => p.id === usecaseProjectId)
                    if (project) {
                      const projectProgramId = project.programId || project.program_id
                      if (projectProgramId) {
                        const allPrograms = await api.getEntityList('program')
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
                      }
                      if (!projectParam) {
                        setSelectedProjectId(usecaseProjectId)
                      }
                    }
                  }
                  if (usecaseParam) {
                    setSelectedUseCaseId(usecaseParam)
                  } else if (storyUseCaseId) {
                    setSelectedUseCaseId(storyUseCaseId)
                  }
                }
              }
              if (userstoryParam) {
                setSelectedUserStoryId(userstoryParam)
              }
            }
          } catch (err) {
            console.error('Failed to resolve userstory hierarchy:', err)
          }
        }
        
        // Set parameters if they exist
        if (clientParam) setSelectedClientId(clientParam)
        if (programParam) setSelectedProgramId(programParam)
        if (projectParam) setSelectedProjectId(projectParam)
        if (usecaseParam) setSelectedUseCaseId(usecaseParam)
        if (userstoryParam) setSelectedUserStoryId(userstoryParam)
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
        const allPrograms = await api.getEntityList('program')
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
        } else {
          // If project is in URL but program isn't selected, still load all projects to find it
          try {
            const allProjects = await api.getProjects()
            const project = allProjects.find((p: any) => p.id === projectParam)
            if (project) {
              setProjects([project])
            }
          } catch (err) {
            console.error('Failed to load project from URL:', err)
          }
        }
        return
      }
      
      setLoadingProjects(true)
      try {
        const allProjects = await api.getProjects()
        // Check both camelCase and snake_case for program_id
        const filteredProjects = allProjects.filter((p: any) => 
          (p.programId === selectedProgramId || p.program_id === selectedProgramId)
        )
        setProjects(filteredProjects)
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
        const allUseCases = await api.getEntityList('usecase')
        // Check both camelCase and snake_case for project_id
        const filteredUseCases = allUseCases.filter((uc: any) => {
          const matchesProject = (uc.projectId === selectedProjectId || uc.project_id === selectedProjectId)
          return matchesProject
        })
        setUsecases(filteredUseCases)
      } catch (err) {
        console.error('Failed to load use cases:', err)
        setUsecases([])
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
        const allStories = await api.getEntityList('userstory')
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

  // Tasks are now loaded via React Query hook (useUserStoryTasks)
  // This automatically shares cache with KanbanPage and other pages
  // No need for manual useEffect - React Query handles it

  // Filter and sort tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter((task: any) => {
      const matchesSearch = !searchQuery || 
        task.title?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === 'all' || task.status === filterStatus
      return matchesSearch && matchesStatus
    })
  }, [tasks, searchQuery, filterStatus])

  const statuses = Array.from(new Set(tasks.map((t: any) => t.status).filter(Boolean)))

  // Get selected entities for breadcrumb
  const selectedClient = clients.find(c => c.id === selectedClientId)
  const selectedProgram = programs.find(p => p.id === selectedProgramId)
  const selectedProject = projects.find(p => p.id === selectedProjectId)
  const selectedUseCase = usecases.find(uc => uc.id === selectedUseCaseId)
  const selectedUserStory = userstories.find(us => us.id === selectedUserStoryId)

  // Show loading state
  if (loadingClients) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // Check if all required selections are made
  const hasRequiredSelections = selectedClientId && selectedProgramId && selectedProjectId && selectedUseCaseId && selectedUserStoryId

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
        <p className="text-gray-600 mt-1">Manage project tasks and assignments</p>
      </div>

      {/* Breadcrumb Navigation */}
      {(selectedClient || selectedProgram || selectedProject || selectedUseCase || selectedUserStory) && (
        <div className="mb-4 flex items-center gap-2 text-sm">
          {selectedClient && (
            <>
              <button
                onClick={() => navigate(`/clients`)}
                className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
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
                className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
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
                className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
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
                className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
              >
                {selectedUseCase.name}
              </button>
              {selectedUserStory && <span className="text-gray-400">→</span>}
            </>
          )}
          {selectedUserStory && (
            <button
              onClick={() => navigate(`/userstories?client=${selectedClientId}&program=${selectedProgramId}&project=${selectedProjectId}&usecase=${selectedUseCaseId}`)}
              className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
            >
              {selectedUserStory.title}
            </button>
          )}
        </div>
      )}
      
      {/* Compact Hierarchy Filter Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Client:</span>
            <select
              value={selectedClientId}
              onChange={(e) => setSelectedClientId(e.target.value)}
              className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              <span className="text-gray-400">→</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Program:</span>
                <select
                  value={selectedProgramId}
                  onChange={(e) => setSelectedProgramId(e.target.value)}
                  disabled={loadingPrograms}
                  className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
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
              <span className="text-gray-400">→</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Project:</span>
                <select
                  value={selectedProjectId}
                  onChange={(e) => setSelectedProjectId(e.target.value)}
                  disabled={loadingProjects}
                  className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
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
              <span className="text-gray-400">→</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Use Case:</span>
                <select
                  value={selectedUseCaseId}
                  onChange={(e) => setSelectedUseCaseId(e.target.value)}
                  disabled={loadingUseCases}
                  className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
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
              <span className="text-gray-400">→</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">User Story:</span>
                <select
                  value={selectedUserStoryId}
                  onChange={(e) => setSelectedUserStoryId(e.target.value)}
                  disabled={loadingUserStories}
                  className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                >
                  <option value="">Select...</option>
                  {userstories.map((story) => (
                    <option key={story.id} value={story.id}>
                      {story.title}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Show message if selections not made */}
      {!hasRequiredSelections && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <div className="text-blue-600 font-medium mb-1">
            Please select Client, Program, Project, Use Case, and User Story
          </div>
          <p className="text-blue-600 text-sm">
            Tasks are organized under user stories. Please make all selections above to view tasks.
          </p>
        </div>
      )}

      {/* Show content only when all selections are made */}
      {hasRequiredSelections && (
        <>
          {/* Filters */}
          <div className="bg-white rounded-lg shadow p-4 mb-6">
            <div className="flex gap-4">
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Status</option>
                {statuses.map((status: string) => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
              <button 
                onClick={() => {
                  setEditingTask(null)
                  setIsModalOpen(true)
                }}
                disabled={!isAdmin || !selectedUserStoryId}
                className={`px-6 py-2 rounded-lg transition-colors whitespace-nowrap ${
                  isAdmin && selectedUserStoryId
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
                title={
                  !isAdmin ? 'Only Admin users can create tasks' : 
                  !selectedUserStoryId ? 'Please select a user story first' : 
                  'Create new task'
                }
              >
                + New Task
              </button>
            </div>
          </div>
          
          {/* Tasks List */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Task
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assigned To
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Due Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTasks.map((task: any) => (
                  <tr
                    key={task.id}
                    onClick={() => navigate(`/hierarchy/task/${task.id}`)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{task.title}</div>
                      {task.description && (
                        <div className="text-sm text-gray-500 line-clamp-1">{task.description}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        task.status === 'Done' ? 'bg-green-100 text-green-800' :
                        task.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {task.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {task.assigned_to_name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {task.due_date ? formatDateForDisplay(task.due_date) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredTasks.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">No tasks found for this user story</p>
              </div>
            )}
          </div>
        </>
      )}

      {/* Task Modal */}
      <TaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={async () => {
          const allTasks = await api.getTasks()
          const filteredTasks = allTasks.filter((t: any) => 
            (t.userStoryId === selectedUserStoryId || t.user_story_id === selectedUserStoryId)
          )
          setTasks(filteredTasks)
        }}
        task={editingTask}
        selectedClientId={selectedClientId}
        selectedProgramId={selectedProgramId}
        selectedProjectId={selectedProjectId}
        selectedUseCaseId={selectedUseCaseId}
        selectedUserStoryId={selectedUserStoryId}
        clients={clients}
        programs={programs}
        projects={projects}
        usecases={usecases}
        userstories={userstories}
        users={users}
        isAdmin={isAdmin}
      />
    </div>
  )
}
