/**
 * Use Case Modal Component
 * Create and edit use cases
 */
import { useState, useEffect } from 'react'
import Modal from '../common/Modal'
import api from '../../services/api'
import EnhancedAssignmentDisplay from '../assignments/EnhancedAssignmentDisplay'

interface UseCaseModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  useCase?: any
  selectedClientId?: string
  selectedProgramId?: string
  selectedProjectId?: string
  clients: any[]
  programs: any[]
  projects: any[]
  isAdmin: boolean
}

export default function UseCaseModal({
  isOpen,
  onClose,
  onSuccess,
  useCase,
  selectedClientId,
  selectedProgramId,
  selectedProjectId,
  clients,
  programs,
  projects,
  isAdmin
}: UseCaseModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    short_description: '',
    long_description: '',
    project_id: selectedProjectId || '',
    status: 'Draft',
    priority: 'Medium'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isEditMode = !!useCase

  useEffect(() => {
    if (useCase) {
      setFormData({
        name: useCase.name || '',
        short_description: useCase.short_description || useCase.shortDescription || '',
        long_description: useCase.long_description || useCase.longDescription || '',
        project_id: useCase.project_id || useCase.projectId || '',
        status: useCase.status || 'Draft',
        priority: useCase.priority || 'Medium'
      })
    } else {
      setFormData({
        name: '',
        short_description: '',
        long_description: '',
        project_id: selectedProjectId || '',
        status: 'Draft',
        priority: 'Medium'
      })
    }
    setError('')
  }, [useCase, selectedProjectId, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isAdmin) {
      setError('Only Admin users can create or edit use cases')
      return
    }

    if (!formData.name.trim()) {
      setError('Use case name is required')
      return
    }

    if (!formData.project_id) {
      setError('Please select a project')
      return
    }

    setLoading(true)
    setError('')

    try {
      if (isEditMode) {
        await api.updateEntity('usecase', useCase.id, formData)
      } else {
        await api.createEntity('usecase', formData)
      }
      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to save use case')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditMode ? 'Edit Use Case' : 'Create New Use Case'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Assignment Management - AT TOP */}
        {isEditMode && (
          <div className="mb-6 pb-4 border-b border-gray-200">
            <EnhancedAssignmentDisplay
              entityType="usecase"
              entityId={useCase.id}
              onAssignmentChange={() => {
                // Refresh assignments if needed
                console.log('Use case assignments updated')
              }}
            />
          </div>
        )}

        {/* Hierarchy Display */}
        {selectedClientId && selectedProgramId && selectedProjectId && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
            <div className="font-medium text-blue-900 mb-1">Creating use case under:</div>
            <div className="text-blue-700">
              {clients.find(c => c.id === selectedClientId)?.name} → 
              {programs.find(p => p.id === selectedProgramId)?.name} → 
              {projects.find(p => p.id === selectedProjectId)?.name}
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Use Case Name *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter use case name"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Project *
          </label>
          <select
            value={formData.project_id}
            onChange={(e) => handleChange('project_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select project...</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Short Description <span className="text-xs text-gray-500">(Search keywords, summary)</span>
          </label>
          <textarea
            value={formData.short_description}
            onChange={(e) => handleChange('short_description', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Brief summary with key search terms..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Long Description <span className="text-xs text-gray-500">(Detailed explanation)</span>
          </label>
          <textarea
            value={formData.long_description}
            onChange={(e) => handleChange('long_description', e.target.value)}
            rows={5}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Detailed explanation of the use case..."
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Draft">Draft</option>
              <option value="In Review">In Review</option>
              <option value="Approved">Approved</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              value={formData.priority}
              onChange={(e) => handleChange('priority', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Saving...' : isEditMode ? 'Update Use Case' : 'Create Use Case'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
