/**
 * User Story Modal Component
 * Create and edit user stories
 */
import { useState, useEffect } from 'react'
import Modal from '../common/Modal'
import api from '../../services/api'
import EnhancedAssignmentDisplay from '../assignments/EnhancedAssignmentDisplay'

interface UserStoryModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  userStory?: any
  selectedClientId?: string
  selectedProgramId?: string
  selectedProjectId?: string
  selectedUseCaseId?: string
  clients: any[]
  programs: any[]
  projects: any[]
  usecases: any[]
  isAdmin: boolean
}

export default function UserStoryModal({
  isOpen,
  onClose,
  onSuccess,
  userStory,
  selectedClientId,
  selectedProgramId,
  selectedProjectId,
  selectedUseCaseId,
  clients,
  programs,
  projects,
  usecases,
  isAdmin
}: UserStoryModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    short_description: '',
    long_description: '',
    acceptance_criteria: '',
    usecase_id: selectedUseCaseId || '',
    phase_id: '',
    priority: 'Medium',
    status: 'To Do',
    story_points: 0
  })
  const [phases, setPhases] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingPhases, setLoadingPhases] = useState(true)
  const [error, setError] = useState('')

  const isEditMode = !!userStory

  // Load phases on mount
  useEffect(() => {
    const loadPhases = async () => {
      try {
        setLoadingPhases(true)
        const phasesData = await api.getPhases()
        setPhases(phasesData)
        
        // Set default phase if not already set
        if (!formData.phase_id && phasesData.length > 0) {
          setFormData(prev => ({ ...prev, phase_id: phasesData[0].id }))
        }
      } catch (err) {
        console.error('Failed to load phases:', err)
      } finally {
        setLoadingPhases(false)
      }
    }
    
    if (isOpen) {
      loadPhases()
    }
  }, [isOpen])

  useEffect(() => {
    if (userStory) {
      setFormData({
        name: userStory.name || userStory.title || '',
        short_description: userStory.short_description || userStory.shortDescription || '',
        long_description: userStory.long_description || userStory.longDescription || '',
        acceptance_criteria: userStory.acceptance_criteria || userStory.acceptanceCriteria || '',
        usecase_id: userStory.usecase_id || userStory.usecaseId || '',
        phase_id: userStory.phase_id || userStory.phaseId || '',
        priority: userStory.priority || 'Medium',
        status: userStory.status || 'To Do',
        story_points: userStory.story_points || userStory.storyPoints || 0
      })
    } else {
      setFormData({
        name: '',
        short_description: '',
        long_description: '',
        acceptance_criteria: '',
        usecase_id: selectedUseCaseId || '',
        phase_id: phases.length > 0 ? phases[0].id : '',
        priority: 'Medium',
        status: 'To Do',
        story_points: 0
      })
    }
    setError('')
  }, [userStory, selectedUseCaseId, isOpen, phases])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      setError('User story name is required')
      return
    }

    if (!formData.usecase_id) {
      setError('Please select a use case')
      return
    }

    setLoading(true)
    setError('')

    try {
      if (isEditMode) {
        await api.updateEntity('userstory', userStory.id, formData)
      } else {
        await api.createEntity('userstory', formData)
      }
      onSuccess()
      onClose()
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((e: any) => e.msg || e.message).join(', '))
      } else if (typeof detail === 'string') {
        setError(detail)
      } else {
        setError(err.message || 'Failed to save user story')
      }
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
      title={isEditMode ? 'Edit User Story' : 'Create New User Story'}
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
              entityType="userstory"
              entityId={userStory.id}
              onAssignmentChange={() => {
                // Refresh assignments if needed
                console.log('User story assignments updated')
              }}
            />
          </div>
        )}

        {/* Hierarchy Display */}
        {selectedClientId && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
            <div className="font-medium text-blue-900 mb-1">Creating user story under:</div>
            <div className="text-blue-700">
              {clients.find(c => c.id === selectedClientId)?.name} → 
              {programs.find(p => p.id === selectedProgramId)?.name} → 
              {projects.find(p => p.id === selectedProjectId)?.name} → 
              {usecases.find(uc => uc.id === selectedUseCaseId)?.name}
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Name *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="As a user, I want to..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Use Case *
          </label>
          <select
            value={formData.usecase_id}
            onChange={(e) => handleChange('usecase_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select use case...</option>
            {usecases.map((usecase) => (
              <option key={usecase.id} value={usecase.id}>
                {usecase.name}
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
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Detailed explanation of the user story..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Acceptance Criteria
          </label>
          <textarea
            value={formData.acceptance_criteria}
            onChange={(e) => handleChange('acceptance_criteria', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Given... When... Then..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Phase *
          </label>
          <select
            value={formData.phase_id}
            onChange={(e) => handleChange('phase_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loadingPhases}
            required
          >
            <option value="">Select phase...</option>
            {phases.map((phase) => (
              <option key={phase.id} value={phase.id}>
                {phase.name}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-3 gap-4">
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
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="To Do">To Do</option>
              <option value="In Progress">In Progress</option>
              <option value="Done">Done</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Story Points
            </label>
            <input
              type="number"
              value={formData.story_points}
              onChange={(e) => handleChange('story_points', parseInt(e.target.value) || 0)}
              min="0"
              max="100"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
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
            {loading ? 'Saving...' : isEditMode ? 'Update User Story' : 'Create User Story'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
