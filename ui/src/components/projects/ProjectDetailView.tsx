import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'
import EntityNotes from '../hierarchy/EntityNotes'
import ProjectTeamDisplay from './ProjectTeamDisplay'

interface ProjectDetail {
  id: string
  name: string
  description: string
  status: string
  program_id: string
  start_date?: string
  end_date?: string
  created_at: string
  updated_at: string
}

interface ProjectStats {
  total_usecases: number
  usecases_in_development: number
  usecases_in_testing: number
  usecases_completed: number
  total_user_stories: number
  total_tasks: number
  completion_percentage: number
}

interface ProjectDetailViewProps {
  project: ProjectDetail
  clientId?: string
  programId?: string
  onClose: () => void
  onUpdate: () => void
}

const ProjectDetailView: React.FC<ProjectDetailViewProps> = ({ project, clientId, programId, onClose, onUpdate }) => {
  const navigate = useNavigate()
  const [isEditing, setIsEditing] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [stats, setStats] = useState<ProjectStats | null>(null)
  const [loadingStats, setLoadingStats] = useState(true)
  // Helper to convert date from MM/DD/YYYY or other formats to YYYY-MM-DD for API
  const convertDateToAPIFormat = (dateStr?: string) => {
    if (!dateStr) return ''
    // If already in YYYY-MM-DD format, return as is
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr
    // Try to parse and convert
    try {
      const date = new Date(dateStr)
      if (!isNaN(date.getTime())) {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
      }
    } catch (e) {
      console.warn('Failed to parse date:', dateStr)
    }
    return dateStr
  }

  // Helper to get short_description from project
  const getShortDescription = (proj: ProjectDetail) => {
    return (proj as any).shortDescription || (proj as any).short_description || ''
  }

  // Helper to get long_description from project
  const getLongDescription = (proj: ProjectDetail) => {
    return (proj as any).longDescription || (proj as any).long_description || ''
  }

  const [formData, setFormData] = useState({
    name: project.name,
    short_description: getShortDescription(project),
    long_description: getLongDescription(project),
    status: project.status,
    start_date: convertDateToAPIFormat(project.start_date || (project as any).startDate),
    end_date: convertDateToAPIFormat(project.end_date || (project as any).endDate)
  })

  useEffect(() => {
    loadStats()
  }, [project.id])

  const loadStats = async () => {
    try {
      setLoadingStats(true)
      const response = await api.getEntityStatistics('project', project.id)
      setStats(response)
    } catch (error) {
      console.error('Failed to load project stats:', error)
    } finally {
      setLoadingStats(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSave = async () => {
    setSubmitting(true)
    try {
      // Transform form data to match API schema
      const updateData: any = {
        name: formData.name,
        status: formData.status,
        short_description: formData.short_description || null,
        long_description: formData.long_description || null,
        start_date: formData.start_date || null,
        end_date: formData.end_date || null
      }
      
      // Remove empty strings and convert to null
      Object.keys(updateData).forEach(key => {
        if (updateData[key] === '') {
          updateData[key] = null
        }
      })
      
      console.log('Updating project with data:', updateData)
      await api.updateProject(project.id, updateData)
      setIsEditing(false)
      onUpdate()
    } catch (error: any) {
      console.error('Failed to update project:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to update project. Please try again.'
      alert(errorMessage)
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      name: project.name,
      short_description: getShortDescription(project),
      long_description: getLongDescription(project),
      status: project.status,
      start_date: convertDateToAPIFormat(project.start_date || (project as any).startDate),
      end_date: convertDateToAPIFormat(project.end_date || (project as any).endDate)
    })
    setIsEditing(false)
  }

  const handleViewUseCases = () => {
    // Navigate with full hierarchy context
    const params = new URLSearchParams()
    if (clientId) params.append('client', clientId)
    if (programId || project.program_id) params.append('program', programId || project.program_id)
    params.append('project', project.id)
    navigate(`/usecases?${params.toString()}`)
    onClose()
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not set'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'Planning': 'bg-gray-100 text-gray-800',
      'In Progress': 'bg-blue-100 text-blue-800',
      'Completed': 'bg-green-100 text-green-800',
      'On Hold': 'bg-yellow-100 text-yellow-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="rounded-lg w-full max-w-6xl max-h-[90vh] flex flex-col"
        style={{ 
          backgroundColor: 'var(--surface-color)',
          border: '1px solid var(--border-color)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div 
          className="flex items-center justify-between p-6 border-b"
          style={{ borderColor: 'var(--border-color)' }}
        >
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
              {isEditing ? 'Edit Project' : 'Project Details'}
            </h2>
            <span className={`px-3 py-1 text-sm rounded ${getStatusColor(project.status)}`}>
              {project.status}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 rounded-md hover:opacity-90 transition-opacity"
                style={{ 
                  backgroundColor: 'var(--primary-color)',
                  color: 'white'
                }}
              >
                Edit
              </button>
            ) : (
              <>
                <button
                  onClick={handleCancel}
                  className="px-4 py-2 rounded-md border hover:opacity-80"
                  style={{ 
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="px-4 py-2 rounded-md hover:opacity-90"
                  style={{ 
                    backgroundColor: 'var(--primary-color)',
                    color: 'white'
                  }}
                  disabled={submitting}
                >
                  {submitting ? 'Saving...' : 'Save Changes'}
                </button>
              </>
            )}
            <button 
              onClick={onClose}
              className="text-2xl hover:opacity-70 ml-2"
              style={{ color: 'var(--text-secondary)' }}
            >
              ×
            </button>
          </div>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Project Information */}
            <div className="lg:col-span-2 space-y-6">
              {/* Basic Information */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                  Basic Information
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Project Name
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                      />
                    ) : (
                      <p className="text-base" style={{ color: 'var(--text-color)' }}>
                        {project.name}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Short Description <span className="text-xs text-gray-500">(Search keywords, summary)</span>
                    </label>
                    {isEditing ? (
                      <textarea
                        name="short_description"
                        value={formData.short_description || ''}
                        onChange={handleInputChange}
                        rows={3}
                        placeholder="Brief summary with key search terms..."
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                      />
                    ) : (
                      <p className="text-base" style={{ color: 'var(--text-color)' }}>
                        {getShortDescription(project) || 'No short description provided'}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Long Description <span className="text-xs text-gray-500">(Detailed explanation)</span>
                    </label>
                    {isEditing ? (
                      <textarea
                        name="long_description"
                        value={formData.long_description || ''}
                        onChange={handleInputChange}
                        rows={6}
                        placeholder="Detailed explanation of the project..."
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                      />
                    ) : (
                      <p className="text-base whitespace-pre-wrap" style={{ color: 'var(--text-color)' }}>
                        {getLongDescription(project) || 'No detailed description provided'}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                        Start Date
                      </label>
                      {isEditing ? (
                        <input
                          type="date"
                          name="start_date"
                          value={formData.start_date || ''}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2 rounded-md border"
                          style={{ 
                            backgroundColor: 'var(--surface-color)',
                            borderColor: 'var(--border-color)',
                            color: 'var(--text-color)'
                          }}
                        />
                      ) : (
                        <p className="text-base" style={{ color: 'var(--text-color)' }}>
                          {formatDate(project.start_date || (project as any).startDate)}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                        End Date
                      </label>
                      {isEditing ? (
                        <input
                          type="date"
                          name="end_date"
                          value={formData.end_date || ''}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2 rounded-md border"
                          style={{ 
                            backgroundColor: 'var(--surface-color)',
                            borderColor: 'var(--border-color)',
                            color: 'var(--text-color)'
                          }}
                        />
                      ) : (
                        <p className="text-base" style={{ color: 'var(--text-color)' }}>
                          {formatDate(project.end_date || (project as any).endDate)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Performance Dashboard */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
                    Project Performance
                  </h3>
                  <button
                    onClick={handleViewUseCases}
                    className="px-4 py-2 text-sm rounded-md hover:opacity-90 transition-opacity"
                    style={{ 
                      backgroundColor: 'var(--primary-color)',
                      color: 'white'
                    }}
                  >
                    View Use Cases →
                  </button>
                </div>

                {loadingStats ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : stats ? (
                  <div className="space-y-4">
                    {/* Use Cases Stats */}
                    <div className="grid grid-cols-4 gap-4">
                      <div className="text-center p-4 rounded-lg" style={{ backgroundColor: 'var(--surface-color)' }}>
                        <p className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
                          {stats.total_usecases}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                          Total Use Cases
                        </p>
                      </div>
                      <div className="text-center p-4 rounded-lg" style={{ backgroundColor: 'var(--surface-color)' }}>
                        <p className="text-2xl font-bold text-blue-600">
                          {stats.usecases_in_development}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                          In Development
                        </p>
                      </div>
                      <div className="text-center p-4 rounded-lg" style={{ backgroundColor: 'var(--surface-color)' }}>
                        <p className="text-2xl font-bold text-yellow-600">
                          {stats.usecases_in_testing}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                          In Testing
                        </p>
                      </div>
                      <div className="text-center p-4 rounded-lg" style={{ backgroundColor: 'var(--surface-color)' }}>
                        <p className="text-2xl font-bold text-green-600">
                          {stats.usecases_completed}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                          Completed
                        </p>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span style={{ color: 'var(--text-secondary)' }}>Overall Progress</span>
                        <span style={{ color: 'var(--text-color)' }} className="font-semibold">
                          {stats.completion_percentage}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div 
                          className="bg-green-600 h-3 rounded-full transition-all"
                          style={{ width: `${stats.completion_percentage}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Additional Stats */}
                    <div className="grid grid-cols-2 gap-4 pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
                      <div className="flex justify-between">
                        <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                          Total User Stories
                        </span>
                        <span className="text-sm font-semibold" style={{ color: 'var(--text-color)' }}>
                          {stats.total_user_stories}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                          Total Tasks
                        </span>
                        <span className="text-sm font-semibold" style={{ color: 'var(--text-color)' }}>
                          {stats.total_tasks}
                        </span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-center py-8" style={{ color: 'var(--text-secondary)' }}>
                    No statistics available
                  </p>
                )}
              </div>

              {/* Team Information Section */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                  Project Team
                </h3>
                <ProjectTeamDisplay projectId={project.id} />
              </div>

              {/* Notes Section */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)',
                  borderLeft: '4px solid var(--primary-color)'
                }}
              >
                <EntityNotes entityType="project" entityId={project.id} />
              </div>
            </div>

            {/* Right Column - Metadata */}
            <div className="space-y-6">
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                  Metadata
                </h3>
                
                <div className="space-y-3">
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Created
                    </p>
                    <p className="text-sm" style={{ color: 'var(--text-color)' }}>
                      {formatDate(project.created_at)}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Last Updated
                    </p>
                    <p className="text-sm" style={{ color: 'var(--text-color)' }}>
                      {formatDate(project.updated_at)}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Project ID
                    </p>
                    <p className="text-xs font-mono" style={{ color: 'var(--text-color)' }}>
                      {project.id}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProjectDetailView
