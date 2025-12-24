/**
 * Program Detail Page
 * View program details and navigate to related projects
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import OwnershipDisplay from '../components/ownership/OwnershipDisplay'

export default function ProgramDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [program, setProgram] = useState<any>(null)
  const [client, setClient] = useState<any>(null)
  const [projects, setProjects] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  
  const isAdmin = user?.role === 'Admin'

  useEffect(() => {
    loadProgramDetails()
  }, [id])

  const loadProgramDetails = async () => {
    try {
      // Load program
      const allPrograms = await api.getEntityList('program')
      const programData = allPrograms.find((p: any) => p.id === id)
      
      if (!programData) {
        console.error('Program not found')
        return
      }
      
      setProgram(programData)

      // Load client
      const clientData = await api.getClient(programData.client_id)
      setClient(clientData)

      // Load projects for this program
      const allProjects = await api.getProjects()
      const programProjects = allProjects.filter((p: any) => p.programId === id)
      setProjects(programProjects)
    } catch (error) {
      console.error('Failed to load program details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleViewAllProjects = () => {
    // Navigate to projects page with client and program pre-selected
    navigate(`/projects?client=${program.client_id}&program=${id}`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!program) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Program not found</p>
        <button
          onClick={() => navigate('/programs')}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Back to Programs
        </button>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/programs')}
          className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
        >
          ← Back to Programs
        </button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{program.name}</h1>
            <p className="text-gray-600 mt-1">Program Details</p>
          </div>
        </div>
      </div>

      {/* Program Information */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Owner Management - AT TOP */}
        <div className="lg:col-span-3 bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <OwnershipDisplay
            entityType="program"
            entityId={program.id}
            onOwnershipChange={() => {
              // Refresh program data if needed
              console.log('Program ownership updated')
            }}
          />
        </div>

        {/* Main Details */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Program Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Client</label>
              <p className="text-gray-900">{client?.name || 'N/A'}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Description</label>
              <p className="text-gray-900">{program.description || 'No description provided'}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Status</label>
                <p>
                  <span className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${
                    program.status === 'Active' ? 'bg-green-100 text-green-800' :
                    program.status === 'Planning' ? 'bg-yellow-100 text-yellow-800' :
                    program.status === 'On Hold' ? 'bg-orange-100 text-orange-800' :
                    program.status === 'Completed' ? 'bg-blue-100 text-blue-800' :
                    program.status === 'Cancelled' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {program.status}
                  </span>
                </p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Total Projects</label>
                <p className="text-2xl font-bold text-gray-900">{projects.length}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Start Date</label>
                <p className="text-gray-900">
                  {program.start_date ? new Date(program.start_date).toLocaleDateString() : 'Not set'}
                </p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">End Date</label>
                <p className="text-gray-900">
                  {program.end_date ? new Date(program.end_date).toLocaleDateString() : 'Not set'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Projects</span>
                <span className="text-xl font-bold text-gray-900">{projects.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">In Progress</span>
                <span className="text-xl font-bold text-green-600">
                  {projects.filter(p => p.status === 'In Progress').length}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Completed</span>
                <span className="text-xl font-bold text-blue-600">
                  {projects.filter(p => p.status === 'Completed').length}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={handleViewAllProjects}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            View All Projects →
          </button>
        </div>
      </div>

      {/* Projects List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Projects</h2>
          <button
            onClick={handleViewAllProjects}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View All →
          </button>
        </div>

        {projects.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <p className="text-gray-500">No projects in this program yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Project Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dates
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {projects.slice(0, 5).map((project: any) => (
                  <tr
                    key={project.id}
                    onClick={() => navigate(`/projects/${project.id}`)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{project.name}</div>
                      <div className="text-sm text-gray-500">{project.description}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        project.status === 'In Progress' ? 'bg-green-100 text-green-800' :
                        project.status === 'Planning' ? 'bg-yellow-100 text-yellow-800' :
                        project.status === 'Completed' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {project.status}
                      </span>
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {project.startDate} - {project.endDate}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
