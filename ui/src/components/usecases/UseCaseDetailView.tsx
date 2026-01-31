import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'
import EntityNotes from '../hierarchy/EntityNotes'
import EnhancedAssignmentDisplay from '../assignments/EnhancedAssignmentDisplay'

interface UseCaseDetail {
  id: string
  name: string
  description?: string
  short_description?: string
  shortDescription?: string
  long_description?: string
  longDescription?: string
  status: string
  priority: string
  project_id?: string
  projectId?: string
  created_at?: string
  createdAt?: string
  updated_at?: string
  updatedAt?: string
}

interface UseCaseStats {
  total_user_stories: number
  user_stories_in_progress: number
  user_stories_in_testing: number
  user_stories_completed: number
  total_tasks: number
  completion_percentage: number
}

interface UseCaseDetailViewProps {
  usecase: UseCaseDetail
  clientId?: string
  programId?: string
  projectId?: string
  onClose: () => void
  onUpdate: () => void
}

const UseCaseDetailView: React.FC<UseCaseDetailViewProps> = ({ 
  usecase, 
  clientId, 
  programId, 
  projectId, 
  onClose, 
  onUpdate 
}) => {
  const navigate = useNavigate()
  const [isEditing, setIsEditing] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [stats, setStats] = useState<UseCaseStats | null>(null)
  const [loadingStats, setLoadingStats] = useState(true)
  // Helper to get short_description from usecase
  const getShortDescription = (uc: UseCaseDetail) => {
    return (uc as any).shortDescription || (uc as any).short_description || ''
  }

  // Helper to get long_description from usecase
  const getLongDescription = (uc: UseCaseDetail) => {
    return (uc as any).longDescription || (uc as any).long_description || ''
  }

  const [formData, setFormData] = useState({
    name: usecase.name,
    short_description: getShortDescription(usecase),
    long_description: getLongDescription(usecase),
    status: usecase.status,
    priority: usecase.priority
  })

  useEffect(() => {
    loadStats()
  }, [usecase.id])

  const loadStats = async () => {
    try {
      setLoadingStats(true)
      const response = await api.getEntityStatistics('usecase', usecase.id)
      setStats(response)
    } catch (error: any) {
      // Silently handle 401/404 errors - statistics are optional
      if (error.response?.status !== 401 && error.response?.status !== 404) {
        console.error('Failed to load use case stats:', error)
      }
      setStats(null)
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
        priority: formData.priority,
        short_description: formData.short_description || null,
        long_description: formData.long_description || null
      }
      
      // Remove empty strings and convert to null
      Object.keys(updateData).forEach(key => {
        if (updateData[key] === '') {
          updateData[key] = null
        }
      })
      
      await api.updateEntity('usecase', usecase.id, updateData)
      setIsEditing(false)
      onUpdate()
    } catch (error: any) {
      console.error('Failed to update use case:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to update use case. Please try again.'
      alert(errorMessage)
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      name: usecase.name,
      short_description: getShortDescription(usecase),
      long_description: getLongDescription(usecase),
      status: usecase.status,
      priority: usecase.priority
    })
    setIsEditing(false)
  }

  const handleViewUserStories = () => {
    const params = new URLSearchParams()
    if (clientId) params.append('client', clientId)
    if (programId) params.append('program', programId)
    if (projectId || usecase.project_id) params.append('project', projectId || usecase.project_id || '')
    params.append('usecase', usecase.id)
    navigate(`/userstories?${params.toString()}`)
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

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'High': 'bg-red-100 text-red-800',
      'Medium': 'bg-yellow-100 text-yellow-800',
      'Low': 'bg-green-100 text-green-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
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
              {isEditing ? 'Edit Use Case' : 'Use Case Details'}
            </h2>
            <span className={`px-3 py-1 text-sm rounded ${getStatusColor(usecase.status)}`}>
              {usecase.status}
            </span>
            <span className={`px-3 py-1 text-sm rounded ${getPriorityColor(usecase.priority)}`}>
              {usecase.priority} Priority
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
            {/* Left Column */}
            <div className="lg:col-span-2 space-y-6">
              {/* Assignment Management - AT TOP */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)',
                  borderLeft: '4px solid var(--primary-color)'
                }}
              >
                <EnhancedAssignmentDisplay
                  entityType="usecase"
                  entityId={usecase.id}
                  onAssignmentChange={() => {
                    // Refresh assignments if needed
                    console.log('Use case assignments updated')
                  }}
                />
              </div>

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
                      Use Case Name
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
                        {usecase.name}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Short Description
                    </label>
                    {isEditing ? (
                      <textarea
                        name="short_description"
                        value={formData.short_description}
                        onChange={handleInputChange}
                        rows={2}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                        placeholder="Brief summary with key search terms..."
                      />
                    ) : (
                      <p className="text-base" style={{ color: 'var(--text-color)' }}>
                        {getShortDescription(usecase) || 'No short description provided'}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Long Description
                    </label>
                    {isEditing ? (
                      <textarea
                        name="long_description"
                        value={formData.long_description}
                        onChange={handleInputChange}
                        rows={4}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                        placeholder="Detailed explanation of the use case..."
                      />
                    ) : (
                      <p className="text-base" style={{ color: 'var(--text-color)' }}>
                        {getLongDescription(usecase) || 'No long description provided'}
                      </p>
                    )}
                  </div>

                  {isEditing && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                          Status
                        </label>
                        <select
                          name="status"
                          value={formData.status}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2 rounded-md border"
                          style={{ 
                            backgroundColor: 'var(--surface-color)',
                            borderColor: 'var(--border-color)',
                            color: 'var(--text-color)'
                          }}
                        >
                          <option value="Draft">Draft</option>
                          <option value="In Review">In Review</option>
                          <option value="Approved">Approved</option>
                          <option value="In Progress">In Progress</option>
                          <option value="Completed">Completed</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                          Priority
                        </label>
                        <select
                          name="priority"
                          value={formData.priority}
                          onChange={handleInputChange}
                          className="w-full px-4 py-2 rounded-md border"
                          style={{ 
                            backgroundColor: 'var(--surface-color)',
                            borderColor: 'var(--border-color)',
                            color: 'var(--text-color)'
                          }}
                        >
                          <option value="Low">Low</option>
                          <option value="Medium">Medium</option>
                          <option value="High">High</option>
                          <option value="Critical">Critical</option>
                        </select>
                      </div>
                    </div>
                  )}
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
                    Use Case Performance
                  </h3>
                  <button
                    onClick={handleViewUserStories}
                    className="px-4 py-2 text-sm rounded-md hover:opacity-90 transition-opacity"
                    style={{ 
                      backgroundColor: 'var(--primary-color)',
                      color: 'white'
                    }}
                  >
                    View User Stories →
                  </button>
                </div>

                {loadingStats ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : stats ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-4 gap-4">
                      <div className="text-center p-4 rounded-lg" style={{ backgroundColor: 'var(--surface-color)' }}>
                        <p className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
                          {stats.total_user_stories}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                          Total Stories
                        </p>
                      </div>
                      <div className="text-center p-4 rounded-lg" style={{ backgroundColor: 'var(--surface-color)' }}>
                        <p className="text-2xl font-bold text-blue-600">
                          {stats.user_stories_in_progress}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                          In Progress
                        </p>
                      </div>
                      <div className="text-center p-4 rounded-lg" style={{ backgroundColor: 'var(--surface-color)' }}>
                        <p className="text-2xl font-bold text-yellow-600">
                          {stats.user_stories_in_testing}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                          In Testing
                        </p>
                      </div>
                      <div className="text-center p-4 rounded-lg" style={{ backgroundColor: 'var(--surface-color)' }}>
                        <p className="text-2xl font-bold text-green-600">
                          {stats.user_stories_completed}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                          Completed
                        </p>
                      </div>
                    </div>

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

                    <div className="pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
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

              {/* Notes Section */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)',
                  borderLeft: '4px solid var(--primary-color)'
                }}
              >
                <EntityNotes entityType="usecase" entityId={usecase.id} />
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
                      {formatDate(usecase.created_at)}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Last Updated
                    </p>
                    <p className="text-sm" style={{ color: 'var(--text-color)' }}>
                      {formatDate(usecase.updated_at)}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Use Case ID
                    </p>
                    <p className="text-xs font-mono" style={{ color: 'var(--text-color)' }}>
                      {usecase.id}
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

export default UseCaseDetailView
