/**
 * Projects Page
 * List and manage projects with client and program selection
 */
import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import ProjectDetailView from '../components/projects/ProjectDetailView'
import ProjectModal from '../components/projects/ProjectModal'

export default function ProjectsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [searchParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [selectedClientId, setSelectedClientId] = useState<string>('')
  const [selectedProgramId, setSelectedProgramId] = useState<string>('')
  const [clients, setClients] = useState<any[]>([])
  const [programs, setPrograms] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [selectedProject, setSelectedProject] = useState<any>(null)
  const [loadingClients, setLoadingClients] = useState(true)
  const [loadingPrograms, setLoadingPrograms] = useState(false)
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'date'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProject, setEditingProject] = useState<any>(null)
  
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
        
        if (clientParam) {
          setSelectedClientId(clientParam)
        }
        if (programParam) {
          setSelectedProgramId(programParam)
        }
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
        setSelectedProgramId('')
        return
      }
      
      setLoadingPrograms(true)
      try {
        const allPrograms = await api.getEntityList('program')
        const filteredPrograms = allPrograms.filter((p: any) => p.client_id === selectedClientId)
        setPrograms(filteredPrograms)
      } catch (err) {
        console.error('Failed to load programs:', err)
      } finally {
        setLoadingPrograms(false)
      }
    }
    loadPrograms()
  }, [selectedClientId])

  // Load projects function
  const loadProjects = async () => {
    try {
      const data = await api.getProjects()
      setProjects(data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setLoading(false)
    }
  }

  // Load projects on mount
  useEffect(() => {
    loadProjects()
  }, [])

  // Filter and sort projects
  const filteredProjects = useMemo(() => {
    if (!selectedClientId || !selectedProgramId) {
      return []
    }
    
    let filtered = projects.filter((project: any) => {
      const matchesSearch = !searchQuery || 
        project.name?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === 'all' || project.status === filterStatus
      // Use programId (camelCase) since API response is transformed
      const matchesProgram = project.programId === selectedProgramId || project.program_id === selectedProgramId
      
      return matchesSearch && matchesStatus && matchesProgram
    })
    
    // Sort projects
    filtered.sort((a: any, b: any) => {
      let comparison = 0
      if (sortBy === 'name') {
        comparison = (a.name || '').localeCompare(b.name || '')
      } else if (sortBy === 'status') {
        comparison = (a.status || '').localeCompare(b.status || '')
      } else if (sortBy === 'date') {
        comparison = new Date(a.startDate || 0).getTime() - new Date(b.startDate || 0).getTime()
      }
      return sortOrder === 'asc' ? comparison : -comparison
    })
    
    return filtered
  }, [projects, searchQuery, filterStatus, selectedClientId, selectedProgramId, programs, sortBy, sortOrder])

  // Calculate statistics
  const statistics = useMemo(() => {
    const relevantProjects = filteredProjects
    
    return {
      total: relevantProjects.length,
      planning: relevantProjects.filter((p: any) => p.status === 'Planning').length,
      inProgress: relevantProjects.filter((p: any) => p.status === 'In Progress').length,
      onHold: relevantProjects.filter((p: any) => p.status === 'On Hold').length,
      completed: relevantProjects.filter((p: any) => p.status === 'Completed').length,
      cancelled: relevantProjects.filter((p: any) => p.status === 'Cancelled').length,
    }
  }, [filteredProjects])

  const statuses = Array.from(new Set(projects.map((p: any) => p.status).filter(Boolean)))

  const toggleSort = (field: 'name' | 'status' | 'date') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('asc')
    }
  }

  const getClientName = (clientId: string) => {
    const client = clients.find(c => c.id === clientId)
    return client?.name || clientId
  }

  const getProgramName = (programId: string) => {
    const program = programs.find(p => p.id === programId)
    if (!program) {
      // Try to find in all programs
      const allPrograms = projects.map(p => p.programId)
      return programId
    }
    return program?.name || programId
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // Get selected entities for breadcrumb
  const selectedClient = clients.find(c => c.id === selectedClientId)
  const selectedProgram = programs.find(p => p.id === selectedProgramId)
  
  // Check if required selections are made
  const hasRequiredSelections = selectedClientId && selectedProgramId

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
        <p className="text-gray-600 mt-1">Manage your projects and deliverables</p>
      </div>

      {/* Breadcrumb Navigation */}
      {(selectedClient || selectedProgram) && (
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
            <button
              onClick={() => navigate(`/programs/${selectedProgramId}`)}
              className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
            >
              {selectedProgram.name}
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
              disabled={loadingClients}
              className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
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
        </div>
      </div>
      
      {/* Show message if selections not made */}
      {!hasRequiredSelections && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <div className="text-blue-600 font-medium mb-1">
            Please select Client and Program
          </div>
          <p className="text-blue-600 text-sm">
            Projects are organized under programs. Please make all selections above to view projects.
          </p>
        </div>
      )}
      
      {/* Show content only when all selections are made */}
      {hasRequiredSelections && (
        <>
          {/* Statistics Dashboard */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">Total Projects</div>
          <div className="text-2xl font-bold text-gray-900">{statistics.total}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">Planning</div>
          <div className="text-2xl font-bold text-yellow-600">{statistics.planning}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">In Progress</div>
          <div className="text-2xl font-bold text-green-600">{statistics.inProgress}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">On Hold</div>
          <div className="text-2xl font-bold text-orange-600">{statistics.onHold}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">Completed</div>
          <div className="text-2xl font-bold text-blue-600">{statistics.completed}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">Cancelled</div>
          <div className="text-2xl font-bold text-red-600">{statistics.cancelled}</div>
        </div>
      </div>
      
      {/* Filters and Sort */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <input
            type="text"
            placeholder="Search projects..."
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
              onClick={() => toggleSort('status')}
              className={`px-4 py-2 border rounded-lg transition-colors ${
                sortBy === 'status' 
                  ? 'bg-blue-50 border-blue-500 text-blue-700' 
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Status {sortBy === 'status' && (sortOrder === 'asc' ? '↑' : '↓')}
            </button>
            <button
              onClick={() => toggleSort('date')}
              className={`px-4 py-2 border rounded-lg transition-colors ${
                sortBy === 'date' 
                  ? 'bg-blue-50 border-blue-500 text-blue-700' 
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Date {sortBy === 'date' && (sortOrder === 'asc' ? '↑' : '↓')}
            </button>
          </div>
          <button 
            onClick={() => {
              setEditingProject(null)
              setIsModalOpen(true)
            }}
            disabled={!isAdmin || !selectedProgramId}
            className={`px-6 py-2 rounded-lg transition-colors whitespace-nowrap ${
              isAdmin && selectedProgramId
                ? 'bg-blue-600 text-white hover:bg-blue-700' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
            title={
              !isAdmin ? 'Only Admin users can create projects' : 
              !selectedProgramId ? 'Please select Client and Program first' : 
              'Create new project'
            }
          >
            + New Project
          </button>
        </div>
      </div>
      
      {/* Projects List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Project Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Program
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Start Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  End Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredProjects.map((project: any) => (
                <tr
                  key={project.id}
                  onClick={() => setSelectedProject(project)}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{project.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{project.programName || project.programId || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      project.status === 'In Progress' ? 'bg-green-100 text-green-800' :
                      project.status === 'Planning' ? 'bg-yellow-100 text-yellow-800' :
                      project.status === 'On Hold' ? 'bg-orange-100 text-orange-800' :
                      project.status === 'Completed' ? 'bg-blue-100 text-blue-800' :
                      project.status === 'Cancelled' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {project.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {project.startDate || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {project.endDate || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">{project.progress}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                    {project.description || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
          {filteredProjects.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No projects found for this program</p>
            </div>
          )}
        </>
      )}

      {/* Project Detail View Modal */}
      {selectedProject && (
        <ProjectDetailView
          project={selectedProject}
          clientId={selectedClientId !== 'all' ? selectedClientId : undefined}
          programId={selectedProgramId !== 'all' ? selectedProgramId : undefined}
          onClose={() => setSelectedProject(null)}
          onUpdate={() => {
            loadProjects()
            setSelectedProject(null)
          }}
        />
      )}

      {/* Project Modal */}
      <ProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={async () => {
          const data = await api.getProjects()
          setProjects(data)
        }}
        project={editingProject}
        selectedClientId={selectedClientId}
        selectedProgramId={selectedProgramId}
        clients={clients}
        programs={programs}
        isAdmin={isAdmin}
      />
    </div>
  )
}

