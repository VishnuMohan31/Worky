/**
 * Use Cases Page
 * List and manage use cases with client, program, and project selection
 */
import { useState, useEffect, useMemo, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import UseCaseDetailView from '../components/usecases/UseCaseDetailView'
import UseCaseModal from '../components/usecases/UseCaseModal'

export default function UseCasesPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [searchParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterPriority, setFilterPriority] = useState('all')
  const [selectedClientId, setSelectedClientId] = useState<string>('')
  const [selectedProgramId, setSelectedProgramId] = useState<string>('')
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [selectedUseCase, setSelectedUseCase] = useState<any>(null)
  const [clients, setClients] = useState<any[]>([])
  const [programs, setPrograms] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [usecases, setUsecases] = useState<any[]>([])
  const [loadingClients, setLoadingClients] = useState(true)
  const [loadingPrograms, setLoadingPrograms] = useState(false)
  const [loadingProjects, setLoadingProjects] = useState(false)
  const [loadingUseCases, setLoadingUseCases] = useState(false)
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'priority'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUseCase, setEditingUseCase] = useState<any>(null)
  
  const isAdmin = user?.role === 'Admin'
  
  // Load clients on mount and check URL parameters
  useEffect(() => {
    const loadClients = async () => {
      try {
        const clientsData = await api.getClients()
        setClients(clientsData)
        
        // Check URL parameters for pre-selection
        const clientParam = searchParams.get('client')
        const programParam = searchParams.get('program')
        const projectParam = searchParams.get('project')
        
        // If project is passed but program/client aren't, load project first to get its hierarchy
        if (projectParam && (!clientParam || !programParam)) {
          try {
            const allProjects = await api.getProjects()
            const project = allProjects.find((p: any) => p.id === projectParam)
            if (project) {
              const projectProgramId = project.programId || project.program_id
              if (projectProgramId) {
                // Find the program to get the client
                const allPrograms = await api.getEntityList('program')
                const program = allPrograms.find((p: any) => p.id === projectProgramId)
                if (program) {
                  const programClientId = program.client_id || program.clientId
                  if (programClientId) {
                    // Set all hierarchy values - they will trigger dependent useEffects
                    setSelectedClientId(programClientId)
                    setSelectedProgramId(projectProgramId)
                    setSelectedProjectId(projectParam)
                    return
                  }
                }
              }
            }
          } catch (err) {
            console.error('Failed to load project hierarchy:', err)
          }
        }
        
        // Set parameters if they exist
        if (clientParam) setSelectedClientId(clientParam)
        if (programParam) setSelectedProgramId(programParam)
        if (projectParam) setSelectedProjectId(projectParam)
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
        // Don't clear selectedProgramId if it came from URL params
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
        // Don't clear selectedProjectId if it came from URL params
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
        
        // If project was passed via URL but not in filtered list, try to find it
        const projectParam = searchParams.get('project')
        if (projectParam && !filteredProjects.find((p: any) => p.id === projectParam)) {
          // Project might be in all projects but filtered out - find it and check its program
          const project = allProjects.find((p: any) => p.id === projectParam)
          if (project) {
            // The project exists but doesn't match the selected program
            // This shouldn't happen, but let's add it to the list anyway
            console.warn('Project found but program mismatch:', project)
          }
        }
      } catch (err) {
        console.error('Failed to load projects:', err)
      } finally {
        setLoadingProjects(false)
      }
    }
    loadProjects()
  }, [selectedProgramId, searchParams])

  // Load use cases function - reusable and memoized
  const loadUseCases = useCallback(async () => {
    if (!selectedProjectId) {
      setUsecases([])
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
  }, [selectedProjectId])

  // Load use cases when project changes
  useEffect(() => {
    loadUseCases()
  }, [loadUseCases])

  // Filter and sort use cases
  const filteredUseCases = useMemo(() => {
    let filtered = usecases.filter((usecase: any) => {
      const matchesSearch = !searchQuery || 
        usecase.name?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === 'all' || usecase.status === filterStatus
      const matchesPriority = filterPriority === 'all' || usecase.priority === filterPriority
      return matchesSearch && matchesStatus && matchesPriority
    })
    
    // Sort use cases
    filtered.sort((a: any, b: any) => {
      let comparison = 0
      if (sortBy === 'name') {
        comparison = (a.name || '').localeCompare(b.name || '')
      } else if (sortBy === 'status') {
        comparison = (a.status || '').localeCompare(b.status || '')
      } else if (sortBy === 'priority') {
        const priorityOrder: Record<string, number> = { 'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3 }
        comparison = (priorityOrder[a.priority] || 99) - (priorityOrder[b.priority] || 99)
      }
      return sortOrder === 'asc' ? comparison : -comparison
    })
    
    return filtered
  }, [usecases, searchQuery, filterStatus, filterPriority, sortBy, sortOrder])

  // Calculate statistics
  const statistics = useMemo(() => {
    return {
      total: filteredUseCases.length,
      draft: filteredUseCases.filter((uc: any) => uc.status === 'Draft').length,
      inReview: filteredUseCases.filter((uc: any) => uc.status === 'In Review').length,
      approved: filteredUseCases.filter((uc: any) => uc.status === 'Approved').length,
      inProgress: filteredUseCases.filter((uc: any) => uc.status === 'In Progress').length,
      completed: filteredUseCases.filter((uc: any) => uc.status === 'Completed').length,
    }
  }, [filteredUseCases])
  
  const statuses = Array.from(new Set(usecases.map((uc: any) => uc.status).filter(Boolean)))
  const priorities = Array.from(new Set(usecases.map((uc: any) => uc.priority).filter(Boolean)))

  const toggleSort = (field: 'name' | 'status' | 'priority') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('asc')
    }
  }
  
  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'Critical': 'bg-red-100 text-red-800',
      'High': 'bg-orange-100 text-orange-800',
      'Medium': 'bg-yellow-100 text-yellow-800',
      'Low': 'bg-green-100 text-green-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  // Show loading state
  if (loadingClients) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // Check if all required selections are made
  const hasRequiredSelections = selectedClientId && selectedProgramId && selectedProjectId

  // Get selected entity names for breadcrumb
  const selectedClient = clients.find(c => c.id === selectedClientId)
  const selectedProgram = programs.find(p => p.id === selectedProgramId)
  const selectedProject = projects.find(p => p.id === selectedProjectId)

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Use Cases</h1>
        <p className="text-gray-600 mt-1">Manage functional requirements and scenarios</p>
      </div>

      {/* Breadcrumb Navigation */}
      {(selectedClient || selectedProgram || selectedProject) && (
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
            <button
              onClick={() => navigate(`/projects/${selectedProjectId}`)}
              className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
            >
              {selectedProject.name}
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
        </div>
      </div>

      {/* Show message if selections not made */}
      {!hasRequiredSelections && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <div className="text-blue-600 font-medium mb-1">
            Please select Client, Program, and Project
          </div>
          <p className="text-blue-600 text-sm">
            Use cases are organized under projects. Please make all selections above to view use cases.
          </p>
        </div>
      )}

      {/* Show content only when all selections are made */}
      {hasRequiredSelections && (
        <>
          {/* Statistics Dashboard */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Total Use Cases</div>
              <div className="text-2xl font-bold text-gray-900">{statistics.total}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Draft</div>
              <div className="text-2xl font-bold text-gray-600">{statistics.draft}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">In Review</div>
              <div className="text-2xl font-bold text-yellow-600">{statistics.inReview}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Approved</div>
              <div className="text-2xl font-bold text-green-600">{statistics.approved}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">In Progress</div>
              <div className="text-2xl font-bold text-blue-600">{statistics.inProgress}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Completed</div>
              <div className="text-2xl font-bold text-purple-600">{statistics.completed}</div>
            </div>
          </div>
          
          {/* Filters and Sort */}
          <div className="bg-white rounded-lg shadow p-4 mb-6">
            <div className="flex flex-col md:flex-row gap-4">
              <input
                type="text"
                placeholder="Search use cases..."
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
              <div className="flex gap-2">
                <button
                  onClick={() => toggleSort('name')}
                  className={`px-4 py-2 border rounded-lg transition-colors ${
                    sortBy === 'name' 
                      ? 'bg-blue-50 border-blue-500 text-blue-700' 
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Name {sortBy === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
                </button>
                <button
                  onClick={() => toggleSort('priority')}
                  className={`px-4 py-2 border rounded-lg transition-colors ${
                    sortBy === 'priority' 
                      ? 'bg-blue-50 border-blue-500 text-blue-700' 
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Priority {sortBy === 'priority' && (sortOrder === 'asc' ? '↑' : '↓')}
                </button>
              </div>
              <button 
                onClick={() => {
                  setEditingUseCase(null)
                  setIsModalOpen(true)
                }}
                disabled={!isAdmin || !selectedProjectId}
                className={`px-6 py-2 rounded-lg transition-colors whitespace-nowrap ${
                  isAdmin && selectedProjectId
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
                title={
                  !isAdmin ? 'Only Admin users can create use cases' : 
                  !selectedProjectId ? 'Please select a project first' : 
                  'Create new use case'
                }
              >
                + New Use Case
              </button>
            </div>
          </div>
          
          {/* Use Cases Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Use Case Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Priority
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Short Description
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredUseCases.map((usecase: any) => (
                    <tr
                      key={usecase.id}
                      onClick={() => setSelectedUseCase(usecase)}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{usecase.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {usecase.priority && (
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityColor(usecase.priority)}`}>
                            {usecase.priority}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          usecase.status === 'Completed' ? 'bg-purple-100 text-purple-800' :
                          usecase.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                          usecase.status === 'Approved' ? 'bg-green-100 text-green-800' :
                          usecase.status === 'In Review' ? 'bg-yellow-100 text-yellow-800' :
                          usecase.status === 'Draft' ? 'bg-gray-100 text-gray-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {usecase.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 max-w-md truncate">
                        {usecase.shortDescription || usecase.short_description || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {filteredUseCases.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No use cases found for this project</p>
            </div>
          )}
        </>
      )}

      {/* Use Case Detail View Modal */}
      {selectedUseCase && (
        <UseCaseDetailView
          usecase={selectedUseCase}
          clientId={selectedClientId}
          programId={selectedProgramId}
          projectId={selectedProjectId}
          onClose={() => setSelectedUseCase(null)}
          onUpdate={() => {
            loadUseCases()
            setSelectedUseCase(null)
          }}
        />
      )}

      {/* Use Case Modal */}
      <UseCaseModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setEditingUseCase(null)
        }}
        onSuccess={async () => {
          // Reload use cases after successful creation/update
          await loadUseCases()
        }}
        useCase={editingUseCase}
        selectedClientId={selectedClientId}
        selectedProgramId={selectedProgramId}
        selectedProjectId={selectedProjectId}
        clients={clients}
        programs={programs}
        projects={projects}
        isAdmin={isAdmin}
      />
    </div>
  )
}
