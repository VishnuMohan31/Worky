/**
 * Task Modal Component
 * Create and edit tasks
 */
import { useState, useEffect } from 'react'
import Modal from '../common/Modal'
import DateInput from '../common/DateInput'
import api from '../../services/api'
import EnhancedAssignmentDisplay from '../assignments/EnhancedAssignmentDisplay'

interface TaskModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  task?: any
  selectedClientId?: string
  selectedProgramId?: string
  selectedProjectId?: string
  selectedUseCaseId?: string
  selectedUserStoryId?: string
  clients: any[]
  programs: any[]
  projects: any[]
  usecases: any[]
  userstories: any[]
  users: any[]
  isAdmin: boolean
}

export default function TaskModal({
  isOpen,
  onClose,
  onSuccess,
  task,
  selectedClientId,
  selectedProgramId,
  selectedProjectId,
  selectedUseCaseId,
  selectedUserStoryId,
  clients,
  programs,
  projects,
  usecases,
  userstories,
  users,
  isAdmin
}: TaskModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    short_description: '',
    long_description: '',
    user_story_id: selectedUserStoryId || '',
    phase_id: '', // Let user select phase instead of hardcoding
    status: 'To Do',
    priority: 'Medium',
    assigned_to: '',
    sprint_id: '',
    due_date: '',
    estimated_hours: 0
  })
  const [sprints, setSprints] = useState<any[]>([])
  const [phases, setPhases] = useState<any[]>([])
  const [loadingSprints, setLoadingSprints] = useState(false)
  const [loadingPhases, setLoadingPhases] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isEditMode = !!task

  useEffect(() => {
    if (selectedProjectId) {
      loadSprints()
    } else {
      setSprints([])
    }
  }, [selectedProjectId, isOpen])

  useEffect(() => {
    if (isOpen) {
      loadPhases()
    }
  }, [isOpen])

  useEffect(() => {
    if (task) {
      setFormData({
        name: task.name || task.title || '',
        short_description: task.short_description || task.shortDescription || '',
        long_description: task.long_description || task.longDescription || '',
        user_story_id: task.user_story_id || task.userStoryId || '',
        phase_id: task.phase_id || task.phaseId || '',
        status: task.status || 'To Do',
        priority: task.priority || 'Medium',
        assigned_to: task.assigned_to || task.assignedTo || '',
        sprint_id: task.sprint_id || task.sprintId || '',
        due_date: task.due_date || task.dueDate || '',
        estimated_hours: task.estimated_hours || task.estimatedHours || 0
      })
    } else {
      setFormData({
        name: '',
        short_description: '',
        long_description: '',
        user_story_id: selectedUserStoryId || '',
        phase_id: '', // Let user select phase instead of hardcoding
        status: 'To Do',
        priority: 'Medium',
        assigned_to: '',
        sprint_id: '',
        due_date: '',
        estimated_hours: 0
      })
    }
    setError('')
  }, [task, selectedUserStoryId, isOpen])

  const loadSprints = async () => {
    if (!selectedProjectId) return
    setLoadingSprints(true)
    try {
      const data = await api.getProjectSprints(selectedProjectId, false)
      setSprints(data)
    } catch (error) {
      console.error('Failed to load sprints:', error)
    } finally {
      setLoadingSprints(false)
    }
  }

  const loadPhases = async () => {
    setLoadingPhases(true)
    try {
      const data = await api.getPhases(false) // Only active phases
      setPhases(data)
    } catch (error) {
      console.error('Failed to load phases:', error)
    } finally {
      setLoadingPhases(false)
    }
  }

  const formatSprintDisplay = (sprint: any) => {
    const formatDate = (dateStr: string) => {
      const date = new Date(dateStr)
      const day = String(date.getDate()).padStart(2, '0')
      const month = date.toLocaleString('default', { month: 'short' }).toUpperCase()
      const year = date.getFullYear()
      return `${day}-${month}-${year}`
    }
    return `${sprint.id} (${formatDate(sprint.start_date)} to ${formatDate(sprint.end_date)})`
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      setError('Task name is required')
      return
    }

    if (!formData.user_story_id) {
      setError('Please select a user story')
      return
    }

    if (!formData.phase_id) {
      setError('Please select a phase')
      return
    }

    setLoading(true)
    setError('')

    try {
      if (isEditMode) {
        await api.updateEntity('task', task.id, formData)
      } else {
        await api.createEntity('task', formData)
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
        setError(err.message || 'Failed to save task')
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
      title={isEditMode ? 'Edit Task' : 'Create New Task'}
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
              entityType="task"
              entityId={task.id}
              onAssignmentChange={() => {
                // Refresh assignments if needed
                console.log('Task assignments updated')
              }}
            />
          </div>
        )}

        {/* Hierarchy Display - Dynamic based on formData.user_story_id */}
        {selectedClientId && selectedProgramId && selectedProjectId && selectedUseCaseId && formData.user_story_id && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
            <div className="font-medium text-blue-900 mb-1">Creating task under:</div>
            <div className="text-blue-700">
              {clients.find(c => c.id === selectedClientId)?.name} → 
              {programs.find(p => p.id === selectedProgramId)?.name} → 
              {projects.find(p => p.id === selectedProjectId)?.name} → 
              {usecases.find(uc => uc.id === selectedUseCaseId)?.name} → 
              {userstories.find(us => us.id === formData.user_story_id)?.name || userstories.find(us => us.id === formData.user_story_id)?.title || 'Select user story...'}
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Task Name *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter task name"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            User Story *
          </label>
          <select
            value={formData.user_story_id}
            onChange={(e) => handleChange('user_story_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select user story...</option>
            {userstories.map((story) => (
              <option key={story.id} value={story.id}>
                {story.name || story.title}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Phase *
          </label>
          <select
            value={formData.phase_id}
            onChange={(e) => handleChange('phase_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
            disabled={loadingPhases}
          >
            <option value="">Select phase...</option>
            {phases.map((phase) => (
              <option key={phase.id} value={phase.id}>
                {phase.name}
              </option>
            ))}
          </select>
          {loadingPhases && (
            <p className="text-xs text-gray-500 mt-1">Loading phases...</p>
          )}
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
            placeholder="Detailed explanation of the task..."
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
              <option value="To Do">To Do</option>
              <option value="In Progress">In Progress</option>
              <option value="Done">Done</option>
              <option value="Blocked">Blocked</option>
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

        {selectedProjectId && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sprint
            </label>
            {loadingSprints ? (
              <div className="text-sm text-gray-500">Loading sprints...</div>
            ) : (
              <select
                value={formData.sprint_id}
                onChange={(e) => handleChange('sprint_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">No Sprint</option>
                {sprints.map((sprint) => (
                  <option key={sprint.id} value={sprint.id}>
                    {formatSprintDisplay(sprint)}
                  </option>
                ))}
              </select>
            )}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Assigned To
            </label>
            <select
              value={formData.assigned_to}
              onChange={(e) => handleChange('assigned_to', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Unassigned</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.full_name || user.email}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Due Date
            </label>
            <DateInput
              value={formData.due_date}
              onChange={(value) => handleChange('due_date', value)}
              className="w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="DD/MM/YYYY"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Estimated Hours
          </label>
          <input
            type="number"
            value={formData.estimated_hours}
            onChange={(e) => handleChange('estimated_hours', parseFloat(e.target.value) || 0)}
            min="0"
            step="0.5"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
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
            {loading ? 'Saving...' : isEditMode ? 'Update Task' : 'Create Task'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
