/**
 * Subtask Modal Component
 * Modal dialog for creating and editing subtasks
 */
import { useState, useEffect } from 'react'
import Modal from '../common/Modal'
import SubtaskForm from '../forms/SubtaskForm'
import api from '../../services/api'
import EnhancedAssignmentDisplay from '../assignments/EnhancedAssignmentDisplay'
import type { Subtask, SubtaskFormData, Task, Phase, User, Client, Program, Project, UseCase, UserStory } from '../../types/entities'

interface SubtaskModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  subtask?: Subtask | null
  selectedClientId?: string
  selectedProgramId?: string
  selectedProjectId?: string
  selectedUseCaseId?: string
  selectedUserStoryId?: string
  selectedTaskId?: string
  clients: Client[]
  programs: Program[]
  projects: Project[]
  usecases: UseCase[]
  userstories: UserStory[]
  tasks: Task[]
  users: User[]
  phases: Phase[]
  isAdmin: boolean
}

export default function SubtaskModal({
  isOpen,
  onClose,
  onSuccess,
  subtask,
  selectedClientId,
  selectedProgramId,
  selectedProjectId,
  selectedUseCaseId,
  selectedUserStoryId,
  selectedTaskId,
  clients,
  programs,
  projects,
  usecases,
  userstories,
  tasks,
  users,
  phases,
  isAdmin
}: SubtaskModalProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isEditMode = !!subtask

  // Reset error when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setError('')
    }
  }, [isOpen])

  const handleSubmit = async (formData: SubtaskFormData) => {
    setLoading(true)
    setError('')

    try {
      if (isEditMode && subtask) {
        // Update existing subtask
        await api.updateEntity('subtask', subtask.id, formData)
      } else {
        // Create new subtask
        await api.createEntity('subtask', formData)
      }
      
      // Call success callback and close modal
      onSuccess()
      onClose()
    } catch (err: any) {
      // Handle API errors with user-friendly messages
      const detail = err.response?.data?.detail
      let errorMessage: string
      if (Array.isArray(detail)) {
        errorMessage = detail.map((e: any) => e.msg || e.message).join(', ')
      } else if (typeof detail === 'string') {
        errorMessage = detail
      } else {
        errorMessage = err.message || 'Failed to save subtask'
      }
      setError(errorMessage)
      console.error('Subtask save error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setError('')
    onClose()
  }

  // Get hierarchy breadcrumb names
  const clientName = clients.find(c => c.id === selectedClientId)?.name || ''
  const programName = programs.find(p => p.id === selectedProgramId)?.name || ''
  const projectName = projects.find(p => p.id === selectedProjectId)?.name || ''
  const usecaseName = usecases.find(uc => uc.id === selectedUseCaseId)?.name || ''
  const userstoryName = userstories.find(us => us.id === selectedUserStoryId)?.name || ''
  const taskName = tasks.find(t => t.id === selectedTaskId)?.name || ''

  // Prepare initial form data for edit mode
  const initialData = subtask ? {
    name: subtask.name,
    task_id: subtask.task_id,
    short_description: subtask.short_description,
    long_description: subtask.long_description,
    status: subtask.status,
    phase_id: subtask.phase_id,
    assigned_to: subtask.assigned_to,
    estimated_hours: subtask.estimated_hours || 0,
    duration_days: subtask.duration_days || 1,
    scrum_points: subtask.scrum_points
  } : undefined

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleCancel}
      title={isEditMode ? 'Edit Subtask' : 'Create New Subtask'}
      size="lg"
    >
      <div className="space-y-4">
        {/* Assignment Management - AT TOP */}
        {isEditMode && subtask && (
          <div className="mb-6 pb-4 border-b border-gray-200">
            <EnhancedAssignmentDisplay
              entityType="subtask"
              entityId={subtask.id}
              onAssignmentChange={() => {
                // Refresh assignments if needed
                console.log('Subtask assignments updated')
              }}
            />
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Hierarchy Context Display */}
        {selectedClientId && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs sm:text-sm">
            <div className="font-medium text-blue-900 mb-1">
              {isEditMode ? 'Editing subtask under:' : 'Creating subtask under:'}
            </div>
            <div className="text-blue-700 flex flex-wrap items-center gap-1">
              <span className="truncate max-w-[100px] sm:max-w-none">{clientName}</span>
              <span className="text-blue-400">→</span>
              <span className="truncate max-w-[100px] sm:max-w-none">{programName}</span>
              <span className="text-blue-400">→</span>
              <span className="truncate max-w-[100px] sm:max-w-none">{projectName}</span>
              <span className="text-blue-400">→</span>
              <span className="truncate max-w-[100px] sm:max-w-none">{usecaseName}</span>
              <span className="text-blue-400">→</span>
              <span className="truncate max-w-[100px] sm:max-w-none">{userstoryName}</span>
              <span className="text-blue-400">→</span>
              <span className="font-medium truncate max-w-[100px] sm:max-w-none">{taskName}</span>
            </div>
          </div>
        )}

        {/* Subtask Form */}
        <SubtaskForm
          initialData={initialData}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={loading}
          mode={isEditMode ? 'edit' : 'create'}
          taskId={selectedTaskId}
          tasks={tasks}
          users={users}
          phases={phases}
        />
      </div>
    </Modal>
  )
}
