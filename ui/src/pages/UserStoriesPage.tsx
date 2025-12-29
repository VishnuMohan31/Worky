/**
 * User Stories Page
 * List and manage user stories with hierarchy selection
 */
import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import UserStoryModal from '../components/userstories/UserStoryModal'

export default function UserStoriesPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [searchParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterPriority, setFilterPriority] = useState('all')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingStory, setEditingStory] = useState<any>(null)
  const [selectedClientId, setSelectedClientId] = useState<string>('')
  const [selectedProgramId, setSelectedProgramId] = useState<string>('')
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [selectedUseCaseId, setSelectedUseCaseId] = useState<string>('')
  const [clients, setClients] = useState<any[]>([])
  const [programs, setPrograms] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [usecases, setUsecases] = useState<any[]>([])
  const [stories, setStories] = useState<any[]>([])
  const [loadingClients, setLoadingClients] = useState(true)
  const [loadingPrograms, setLoadingPrograms] = useState(false)
  const [loadingProjects, setLoadingProjects] = useState(false)
  const [loadingUseCases, setLoadingUseCases] = useState(false)
  const [loadingStories, setLoadingStories] = useState(false)
  
  const isAdmin = user?.role === 'Admin'

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
        
        // If usecase is passed but project/client/program aren't, resolve hierarchy
        if (usecaseParam && (!clientParam || !programParam || !projectParam)) {
          try {
            const allUseCases = await api.getEntityList('usecase')
            const usecase = allUseCases.find((uc: any) => uc.id === usecaseParam)
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
              if (!usecaseParam) {
                setSelectedUseCaseId(usecaseParam)
              }
            }
          } catch (err) {
            console.error('Failed to resolve usecase hierarchy:', err)
          }
        }
        
        // Set parameters if they exist
        if (clientParam) setSelectedClientId(clientParam)
        if (programParam) setSelectedProgramId(programParam)
        if (projectParam) setSelectedProjectId(projectParam)
        if (usecaseParam) setSelectedUseCaseId(usecaseParam)
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
    const loadStories = async () => {
      if (!selectedUseCaseId) {
        setStories([])
        return
      }
      
      setLoadingStories(true)
      try {
        const allStories = await api.getEntityList('userstory')
        // Check both camelCase and snake_case for usecase_id
        const filteredStories = allStories.filter((s: any) => 
          (s.usecaseId === selectedUseCaseId || s.usecase_id === selectedUseCaseId)
        )
        setStories(filteredStories)
      } catch (err) {
        console.error('Failed to load user stories:', err)
      } finally {
        setLoadingStories(false)
      }
    }
    loadStories()
  }, [selectedUseCaseId])
  
  // Filter and sort stories
  const filteredStories = useMemo(() => {
    return stories.filter((story: any) => {
      const matchesSearch = !searchQuery || 
        story.title?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === 'all' || story.status === filterStatus
      const matchesPriority = filterPriority === 'all' || story.priority === filterPriority
      return matchesSearch && matchesStatus && matchesPriority
    })
  }, [stories, searchQuery, filterStatus, filterPriority])
  
  const statuses = Array.from(new Set(stories.map((s: any) => s.status).filter(Boolean)))
  const priorities = Array.from(new Set(stories.map((s: any) => s.priority).filter(Boolean)))
  
  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'High': 'bg-red-100 text-red-800',
      'Medium': 'bg-yellow-100 text-yellow-800',
      'Low': 'bg-green-100 text-green-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  const getUseCaseName = (usecaseId: string) => {
    const usecase = usecases.find(uc => uc.id === usecaseId)
    return usecase?.name || usecaseId
  }

  // Get selected entities for breadcrumb
  const selectedClient = clients.find(c => c.id === selectedClientId)
  const selectedProgram = programs.find(p => p.id === selectedProgramId)
  const selectedProject = projects.find(p => p.id === selectedProjectId)
  const selectedUseCase = usecases.find(uc => uc.id === selectedUseCaseId)

  // Show loading state
  if (loadingClients) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // Check if we have any stories to show (either from selections or all stories)
  const hasRequiredSelections = true // Always show the list, just filter based on selections
  
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">User Stories</h1>
        <p className="text-gray-600 mt-1">Manage user-centric features and requirements</p>
      </div>

      {/* Breadcrumb Navigation */}
      {(selectedClient || selectedProgram || selectedProject || selectedUseCase) && (
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
            <button
              onClick={() => navigate(`/usecases?client=${selectedClientId}&program=${selectedProgramId}&project=${selectedProjectId}`)}
              className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
            >
              {selectedUseCase.name}
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
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">Total Stories</div>
          <div className="text-2xl font-bold text-gray-900">{filteredStories.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">To Do</div>
          <div className="text-2xl font-bold text-gray-600">
            {filteredStories.filter((s: any) => s.status === 'To Do').length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">In Progress</div>
          <div className="text-2xl font-bold text-blue-600">
            {filteredStories.filter((s: any) => s.status === 'In Progress').length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">Done</div>
          <div className="text-2xl font-bold text-green-600">
            {filteredStories.filter((s: any) => s.status === 'Done').length}
          </div>
        </div>
      </div>

      {/* Show content */}
      {(
        <>
          {/* Filters */}
          <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Search user stories..."
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
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Priority</option>
            {priorities.map((priority: string) => (
              <option key={priority} value={priority}>{priority}</option>
            ))}
          </select>
          <button 
            onClick={() => {
              setEditingStory(null)
              setIsModalOpen(true)
            }}
            disabled={!selectedUseCaseId}
            className={`px-6 py-2 rounded-lg transition-colors ${
              selectedUseCaseId
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
            title={!selectedUseCaseId ? 'Please select a use case first' : 'Create new user story'}
          >
            + New User Story
          </button>
        </div>
      </div>
      
      {/* User Stories List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Story
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Story Points
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Use Case
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredStories.map((story: any) => (
              <tr
                key={story.id}
                onClick={() => navigate(`/hierarchy/userstory/${story.id}`)}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">{story.title}</div>
                  {story.description && (
                    <div className="text-sm text-gray-500 line-clamp-1">{story.description}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">
                    {story.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {story.priority && (
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(story.priority)}`}>
                      {story.priority}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {story.story_points || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {getUseCaseName(story.usecaseId || story.usecase_id || '')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredStories.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">
              {selectedUseCaseId 
                ? 'No user stories found for this use case' 
                : 'No user stories found. Select filters above or create a new user story.'}
            </p>
          </div>
        )}
      </div>
        </>
      )}

      {/* User Story Modal */}
      <UserStoryModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={() => {
          // Reload stories
          const loadStories = async () => {
            try {
              const allStories = await api.getEntityList('userstory')
              if (selectedUseCaseId) {
                const filteredStories = allStories.filter((s: any) => s.usecase_id === selectedUseCaseId)
                setStories(filteredStories)
              } else {
                setStories(allStories)
              }
            } catch (err) {
              console.error('Failed to reload user stories:', err)
            }
          }
          loadStories()
        }}
        userStory={editingStory}
        selectedClientId={selectedClientId}
        selectedProgramId={selectedProgramId}
        selectedProjectId={selectedProjectId}
        selectedUseCaseId={selectedUseCaseId}
        clients={clients}
        programs={programs}
        projects={projects}
        usecases={usecases}
        isAdmin={isAdmin}
      />
    </div>
  )
}
