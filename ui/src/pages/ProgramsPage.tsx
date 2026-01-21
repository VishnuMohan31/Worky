/**
 * Programs Page
 * List and manage programs with client selection and statistics
 */
import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useEntityList } from '../hooks/useEntity'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import ProgramModal from '../components/programs/ProgramModal'
import { formatDateForDisplay } from '../utils/dateUtils'

export default function ProgramsPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [selectedClientId, setSelectedClientId] = useState<string>('')
  const [clients, setClients] = useState<any[]>([])
  const [loadingClients, setLoadingClients] = useState(true)
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'date'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProgram, setEditingProgram] = useState<any>(null)
  
  const { data: programs = [], isLoading, error, refetch } = useEntityList('program')
  
  const isAdmin = user?.role === 'Admin'
  
  // Load clients on mount
  useEffect(() => {
    const loadClients = async () => {
      try {
        const clientsData = await api.getClients()
        setClients(clientsData)
        
        // Check if we have a pre-selected client from navigation state
        const state = location.state as { selectedClientId?: string; selectedClientName?: string } | null
        if (state?.selectedClientId) {
          setSelectedClientId(state.selectedClientId)
          // Clear the navigation state to prevent re-selection on refresh
          navigate(location.pathname, { replace: true, state: {} })
        }
      } catch (err) {
        console.error('Failed to load clients:', err)
      } finally {
        setLoadingClients(false)
      }
    }
    loadClients()
  }, [])
  
  // Filter and sort programs
  const filteredPrograms = useMemo(() => {
    if (!selectedClientId) return []
    
    let filtered = programs.filter((program: any) => {
      const matchesSearch = !searchQuery || 
        program.name?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === 'all' || program.status === filterStatus
      const matchesClient = program.client_id === selectedClientId
      return matchesSearch && matchesStatus && matchesClient
    })
    
    // Sort programs
    filtered.sort((a: any, b: any) => {
      let comparison = 0
      if (sortBy === 'name') {
        comparison = (a.name || '').localeCompare(b.name || '')
      } else if (sortBy === 'status') {
        comparison = (a.status || '').localeCompare(b.status || '')
      } else if (sortBy === 'date') {
        comparison = new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime()
      }
      return sortOrder === 'asc' ? comparison : -comparison
    })
    
    return filtered
  }, [programs, searchQuery, filterStatus, selectedClientId, sortBy, sortOrder])
  
  // Calculate statistics for selected client
  const statistics = useMemo(() => {
    const relevantPrograms = filteredPrograms
    
    return {
      total: relevantPrograms.length,
      planning: relevantPrograms.filter((p: any) => p.status === 'Planning').length,
      active: relevantPrograms.filter((p: any) => p.status === 'Active').length,
      onHold: relevantPrograms.filter((p: any) => p.status === 'On Hold').length,
      completed: relevantPrograms.filter((p: any) => p.status === 'Completed').length,
      cancelled: relevantPrograms.filter((p: any) => p.status === 'Cancelled').length,
    }
  }, [filteredPrograms])
  
  const statuses = Array.from(new Set(programs.map((p: any) => p.status).filter(Boolean)))
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="text-center text-red-600 p-8">
        Error loading programs: {error.message}
      </div>
    )
  }
  
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
  
  const handleCreateProgram = () => {
    if (!isAdmin) {
      alert('Only Admin users can create programs')
      return
    }
    setEditingProgram(null)
    setIsModalOpen(true)
  }
  
  const handleEditProgram = (e: React.MouseEvent, program: any) => {
    e.stopPropagation() // Prevent row click navigation
    if (!isAdmin) {
      alert('Only Admin users can edit programs')
      return
    }
    setEditingProgram(program)
    setIsModalOpen(true)
  }
  
  const handleModalSuccess = () => {
    refetch()
  }
  
  // Get selected client for breadcrumb
  const selectedClient = clients.find(c => c.id === selectedClientId)
  
  // Check if required selection is made
  const hasRequiredSelections = selectedClientId

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Programs</h1>
        <p className="text-gray-600 mt-1">Manage your programs and initiatives</p>
      </div>

      {/* Breadcrumb Navigation */}
      {selectedClient && (
        <div className="mb-4 flex items-center gap-2 text-sm">
          <button
            onClick={() => navigate(`/clients`)}
            className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
          >
            {selectedClient.name}
          </button>
        </div>
      )}
      
      {/* Client Selector */}
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
        </div>
      </div>
      
      {/* Show message if selection not made */}
      {!hasRequiredSelections && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <div className="text-blue-600 font-medium mb-1">
            Please select a Client
          </div>
          <p className="text-blue-600 text-sm">
            Programs are organized under clients. Please select a client above to view programs.
          </p>
        </div>
      )}
      
      {/* Show content only when selection is made */}
      {hasRequiredSelections && (
        <>
          {/* Statistics Dashboard */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">Total Programs</div>
          <div className="text-2xl font-bold text-gray-900">{statistics.total}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">Planning</div>
          <div className="text-2xl font-bold text-yellow-600">{statistics.planning}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600 mb-1">Active</div>
          <div className="text-2xl font-bold text-green-600">{statistics.active}</div>
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
            placeholder="Search programs..."
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
            onClick={handleCreateProgram}
            disabled={!isAdmin}
            className={`px-6 py-2 rounded-lg transition-colors whitespace-nowrap ${
              isAdmin 
                ? 'bg-blue-600 text-white hover:bg-blue-700' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
            title={!isAdmin ? 'Only Admin users can create programs' : ''}
          >
            + New Program
          </button>
        </div>
      </div>
      
      {/* Programs List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Program Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Client
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
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPrograms.map((program: any) => (
                <tr
                  key={program.id}
                  onClick={() => navigate(`/programs/${program.id}`)}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{program.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{getClientName(program.client_id)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      program.status === 'Active' ? 'bg-green-100 text-green-800' :
                      program.status === 'Planning' ? 'bg-yellow-100 text-yellow-800' :
                      program.status === 'On Hold' ? 'bg-orange-100 text-orange-800' :
                      program.status === 'Completed' ? 'bg-blue-100 text-blue-800' :
                      program.status === 'Cancelled' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {program.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {program.start_date ? formatDateForDisplay(program.start_date) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {program.end_date ? formatDateForDisplay(program.end_date) : '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                    {program.short_description || program.long_description || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={(e) => handleEditProgram(e, program)}
                      disabled={!isAdmin}
                      className={`px-3 py-1 rounded transition-colors ${
                        isAdmin
                          ? 'text-blue-600 hover:bg-blue-50'
                          : 'text-gray-400 cursor-not-allowed'
                      }`}
                      title={!isAdmin ? 'Only Admin users can edit programs' : 'Edit program'}
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
          {filteredPrograms.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No programs found for this client</p>
            </div>
          )}
        </>
      )}
      
      {/* Program Modal */}
      <ProgramModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={handleModalSuccess}
        program={editingProgram}
        selectedClientId={selectedClientId !== 'all' ? selectedClientId : undefined}
        clients={clients}
        isAdmin={isAdmin}
      />
    </div>
  )
}
