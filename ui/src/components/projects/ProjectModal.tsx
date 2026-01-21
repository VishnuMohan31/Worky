/**
 * Project Modal Component
 * Create and edit projects
 */
import { useState, useEffect } from 'react'
import Modal from '../common/Modal'
import DateInput from '../common/DateInput'
import api from '../../services/api'
import OwnerSelector from '../ownership/OwnerSelector'
import { formatDateForAPI } from '../../utils/dateUtils'

interface ProjectModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  project?: any
  selectedClientId?: string
  selectedProgramId?: string
  clients: any[]
  programs: any[]
  isAdmin: boolean
}

export default function ProjectModal({
  isOpen,
  onClose,
  onSuccess,
  project,
  selectedClientId,
  selectedProgramId,
  clients,
  programs,
  isAdmin
}: ProjectModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    short_description: '',
    long_description: '',
    program_id: selectedProgramId || '',
    status: 'Planning',
    start_date: '',
    end_date: '',
    repository_url: ''
  })
  const [selectedOwners, setSelectedOwners] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isEditMode = !!project

  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name || '',
        short_description: project.short_description || project.shortDescription || '',
        long_description: project.long_description || project.longDescription || '',
        program_id: project.program_id || project.programId || '',
        status: project.status || 'Planning',
        start_date: project.start_date || project.startDate || '',
        end_date: project.end_date || project.endDate || '',
        repository_url: project.repository_url || project.repositoryUrl || ''
      })
    } else {
      setFormData({
        name: '',
        short_description: '',
        long_description: '',
        program_id: selectedProgramId || '',
        status: 'Planning',
        start_date: '',
        end_date: '',
        repository_url: ''
      })
    }
    setSelectedOwners([])
    setError('')
  }, [project, selectedProgramId, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isAdmin) {
      setError('Only Admin users can create or edit projects')
      return
    }

    if (!formData.name.trim()) {
      setError('Project name is required')
      return
    }

    if (!formData.program_id) {
      setError('Please select a program')
      return
    }

    // Date validation - handle both YYYY-MM-DD and DD/MM/YYYY formats
    if (formData.start_date && formData.end_date) {
      let startDate: Date
      let endDate: Date
      
      try {
        // Handle both formats
        if (formData.start_date.includes('/')) {
          // DD/MM/YYYY format
          const apiStartDate = formatDateForAPI(formData.start_date)
          startDate = new Date(apiStartDate + 'T00:00:00')
        } else {
          // YYYY-MM-DD format
          startDate = new Date(formData.start_date + 'T00:00:00')
        }
        
        if (formData.end_date.includes('/')) {
          // DD/MM/YYYY format
          const apiEndDate = formatDateForAPI(formData.end_date)
          endDate = new Date(apiEndDate + 'T00:00:00')
        } else {
          // YYYY-MM-DD format
          endDate = new Date(formData.end_date + 'T00:00:00')
        }
        
        if (!isNaN(startDate.getTime()) && !isNaN(endDate.getTime()) && endDate < startDate) {
          setError('End date cannot be before start date')
          return
        }
      } catch (error) {
        console.error('Date validation error:', error)
      }
    }

    setLoading(true)
    setError('')

    try {
      let projectId: string
      
      if (isEditMode) {
        await api.updateEntity('project', project.id, formData)
        projectId = project.id
      } else {
        const newProject = await api.createEntity('project', formData)
        projectId = newProject.id
      }
      
      // Handle owner assignments for new projects only (edit mode handles assignments directly)
      if (selectedOwners.length > 0 && !isEditMode) {
        try {
          // Create owner assignments
          for (const ownerId of selectedOwners) {
            await api.createAssignment({
              entity_type: 'project',
              entity_id: projectId,
              user_id: ownerId,
              assignment_type: 'owner'
            })
          }
          console.log(`Successfully assigned ${selectedOwners.length} owners to project ${projectId}`)
        } catch (ownerError) {
          console.error('Failed to assign owners:', ownerError)
          // Don't fail the entire operation, just show a warning
          setError('Project created successfully, but failed to assign some owners. You can assign them later from the project details.')
          return // Don't close modal immediately so user can see the message
        }
      }
      
      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to save project')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear error when user starts typing
    if (error) {
      setError('')
    }
  }

  // Helper function to check if dates are valid
  const isDateRangeValid = () => {
    if (!formData.start_date || !formData.end_date) return true
    
    try {
      let startDate: Date
      let endDate: Date
      
      // Handle both formats
      if (formData.start_date.includes('/')) {
        const apiStartDate = formatDateForAPI(formData.start_date)
        startDate = new Date(apiStartDate + 'T00:00:00')
      } else {
        startDate = new Date(formData.start_date + 'T00:00:00')
      }
      
      if (formData.end_date.includes('/')) {
        const apiEndDate = formatDateForAPI(formData.end_date)
        endDate = new Date(apiEndDate + 'T00:00:00')
      } else {
        endDate = new Date(formData.end_date + 'T00:00:00')
      }
      
      if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return true
      
      return endDate >= startDate
    } catch (error) {
      return true
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditMode ? 'Edit Project' : 'Create New Project'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Owner Assignment - MOVED TO TOP */}
        {isAdmin && (
          <div className="mb-6 pb-4 border-b border-gray-200">
            <OwnerSelector
              entityType="project"
              selectedOwners={selectedOwners}
              onOwnersChange={setSelectedOwners}
              disabled={loading}
              existingEntityId={isEditMode ? project.id : undefined}
            />
          </div>
        )}

        {/* Hierarchy Display - Dynamic based on formData.program_id */}
        {selectedClientId && formData.program_id && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
            <div className="font-medium text-blue-900 mb-1">Creating project under:</div>
            <div className="text-blue-700">
              {clients.find(c => c.id === selectedClientId)?.name} → 
              {programs.find(p => p.id === formData.program_id)?.name || 'Select program...'}
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Project Name *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter project name"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Program *
          </label>
          <select
            value={formData.program_id}
            onChange={(e) => handleChange('program_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select program...</option>
            {programs.map((program) => (
              <option key={program.id} value={program.id}>
                {program.name}
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
            placeholder="Detailed explanation of the project..."
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
              <option value="Planning">Planning</option>
              <option value="Active">Active</option>
              <option value="On Hold">On Hold</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Repository URL
            </label>
            <input
              type="url"
              value={formData.repository_url}
              onChange={(e) => handleChange('repository_url', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://github.com/..."
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <DateInput
              value={formData.start_date}
              onChange={(value) => handleChange('start_date', value)}
              className="w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="DD/MM/YYYY"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <DateInput
              value={formData.end_date}
              onChange={(value) => handleChange('end_date', value)}
              min={formData.start_date || undefined}
              className="w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="DD/MM/YYYY"
            />
            {formData.start_date && formData.end_date && !isDateRangeValid() && (
              <p className="text-red-500 text-xs mt-1">End date cannot be before start date</p>
            )}
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
            {loading ? 'Saving...' : isEditMode ? 'Update Project' : 'Create Project'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
