import { useState, useEffect } from 'react'
import api from '../../services/api'
import Modal from '../common/Modal'

interface Assignment {
  id: string
  entity_type: string
  entity_id: string
  user_id: string
  assignment_type: string
  assigned_at: string
  is_active: boolean
  user_name?: string
  user_email?: string
  entity_name?: string
}

interface AvailableAssignee {
  id: string
  full_name: string
  email: string
  role: string
  is_team_member: boolean
  current_assignments: string[]
}

interface AssignmentSelectorProps {
  entityType: string
  entityId: string
  onAssignmentChange?: () => void
}

export default function AssignmentSelector({ 
  entityType, 
  entityId, 
  onAssignmentChange 
}: AssignmentSelectorProps) {
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [availableAssignees, setAvailableAssignees] = useState<AvailableAssignee[]>([])
  const [loading, setLoading] = useState(false)
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [newAssignment, setNewAssignment] = useState({
    user_id: '',
    assignment_type: getDefaultAssignmentType(entityType)
  })

  useEffect(() => {
    loadAssignments()
    setNewAssignment(prev => ({ ...prev, assignment_type: getDefaultAssignmentType(entityType) }))
  }, [entityType, entityId])

  useEffect(() => {
    if (showAssignModal) {
      loadAvailableAssignees()
    }
  }, [showAssignModal, entityType, entityId, newAssignment.assignment_type, assignments])

  function getDefaultAssignmentType(entityType: string): string {
    // Client, Program, Project = Owner
    if (['client', 'program', 'project'].includes(entityType)) return 'owner'
    // UseCase, UserStory, Task, Subtask = Assignee (from team members)
    if (['usecase', 'userstory', 'task', 'subtask'].includes(entityType)) return 'assignee'
    return 'assignee'
  }

  const loadAssignments = async () => {
    try {
      setLoading(true)
      const response = await api.getAssignments({
        entity_type: entityType,
        entity_id: entityId
      })
      setAssignments(response)
    } catch (error) {
      console.error('Failed to load assignments:', error)
      alert('Failed to load assignments')
    } finally {
      setLoading(false)
    }
  }

  const loadAvailableAssignees = async () => {
    try {
      const response = await api.getAvailableAssignees(entityType, entityId)
      
      // Filter out users who are already assigned to this entity (regardless of assignment type)
      const assignedUserIds = new Set(
        assignments
          .filter(a => a.is_active)
          .map(a => a.user_id)
      )
      
      const filteredAssignees = response.filter(
        (user: any) => !assignedUserIds.has(user.id)
      )
      
      setAvailableAssignees(filteredAssignees)
    } catch (error) {
      console.error('Failed to load available assignees:', error)
      alert('Failed to load available assignees')
    }
  }

  const handleCreateAssignment = async () => {
    if (!newAssignment.user_id) {
      alert('Please select a user')
      return
    }

    setLoading(true)
    
    try {
      await api.createAssignment({
        entity_type: entityType,
        entity_id: entityId,
        user_id: newAssignment.user_id,
        assignment_type: newAssignment.assignment_type
      })
      
      alert('Assigned successfully')
      
      // Reload assignments first to update the filter, then close modal and reset form
      await loadAssignments()
      setShowAssignModal(false)
      setNewAssignment({ user_id: '', assignment_type: getDefaultAssignmentType(entityType) })
      onAssignmentChange?.()
    } catch (error: any) {
      console.error('Failed to create assignment:', error)
      alert(error.response?.data?.detail || 'Failed to create assignment')
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveAssignment = async (assignmentId: string) => {
    try {
      await api.deleteAssignment(assignmentId)
      
      alert('Unassigned successfully')
      
      loadAssignments()
      onAssignmentChange?.()
    } catch (error: any) {
      console.error('Failed to remove assignment:', error)
      alert(error.response?.data?.detail || 'Failed to remove assignment')
    }
  }

  const getAssignmentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'owner': 'Owner',
      'assignee': 'Assignee',
      'contact_person': 'Contact Person',
      'developer': 'Developer',
      'tester': 'Tester',
      'designer': 'Designer',
      'reviewer': 'Reviewer',
      'lead': 'Lead'
    }
    return labels[type] || type
  }

  const getAssignmentTypeIcon = (type: string) => {
    switch (type) {
      case 'owner':
        return '🛡️'
      case 'assignee':
        return '👤'
      case 'contact_person':
        return '👤'
      case 'developer':
        return '💻'
      case 'tester':
        return '🧪'
      case 'designer':
        return '🎨'
      case 'reviewer':
        return '👁️'
      case 'lead':
        return '⭐'
      default:
        return '👤'
    }
  }

  const getAssignmentTypeColor = (type: string) => {
    switch (type) {
      case 'owner':
        return 'bg-red-100 text-red-800'
      case 'assignee':
        return 'bg-blue-100 text-blue-800'
      case 'contact_person':
        return 'bg-blue-100 text-blue-800'
      case 'developer':
        return 'bg-green-100 text-green-800'
      case 'tester':
        return 'bg-purple-100 text-purple-800'
      case 'designer':
        return 'bg-pink-100 text-pink-800'
      case 'reviewer':
        return 'bg-orange-100 text-orange-800'
      case 'lead':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getInitials = (name?: string) => {
    if (!name) return '?'
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const getAvailableAssignmentTypes = (entityType: string) => {
    const types = []
    if (entityType === 'client') {
      types.push({ value: 'contact_person', label: 'Contact Person' })
    }
    if (['program', 'project'].includes(entityType)) {
      types.push({ value: 'owner', label: 'Owner' })
    }
    if (['usecase', 'userstory', 'task', 'subtask'].includes(entityType)) {
      // For usecases, userstories, tasks, and subtasks, only use 'assignee' type
      // Team members are assigned as assignees
      types.push({ value: 'assignee', label: 'Assignee' })
    }
    return types
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            Assignments ({assignments.length})
          </h3>
          
          <button
            onClick={() => setShowAssignModal(true)}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors flex items-center"
          >
            <span className="mr-2">👥</span>
            Assign User
          </button>
        </div>
      </div>

      <Modal
        isOpen={showAssignModal}
        onClose={() => setShowAssignModal(false)}
        title="Assign User"
        size="md"
      >
        <div className="space-y-4">
          {getAvailableAssignmentTypes(entityType).length > 1 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Assignment Type</label>
              <select
                value={newAssignment.assignment_type}
                onChange={(e) => {
                  setNewAssignment({ ...newAssignment, assignment_type: e.target.value, user_id: '' })
                  // Reload available assignees when assignment type changes
                  setTimeout(loadAvailableAssignees, 100)
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {getAvailableAssignmentTypes(entityType).map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">User</label>
            <select
              value={newAssignment.user_id}
              onChange={(e) => setNewAssignment({ ...newAssignment, user_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select user</option>
              {availableAssignees.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.full_name} ({user.email}) {user.is_team_member ? '- Team Member' : ''}
                </option>
              ))}
              {availableAssignees.length === 0 && (
                <option value="" disabled>
                  No eligible users found
                </option>
              )}
            </select>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <button
              onClick={() => setShowAssignModal(false)}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateAssignment}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Assigning...' : 'Assign'}
            </button>
          </div>
        </div>
      </Modal>
      
      <div className="p-6">
        {loading ? (
          <div className="text-center py-4">Loading assignments...</div>
        ) : assignments.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No assignments found
          </div>
        ) : (
          <div className="space-y-3">
            {assignments.map((assignment) => (
              <div
                key={assignment.id}
                className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-gray-600">
                      {getInitials(assignment.user_name)}
                    </span>
                  </div>
                  
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">{assignment.user_name || 'Unknown User'}</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getAssignmentTypeColor(assignment.assignment_type)}`}>
                        <span className="flex items-center">
                          <span className="mr-1">{getAssignmentTypeIcon(assignment.assignment_type)}</span>
                          <span>{getAssignmentTypeLabel(assignment.assignment_type)}</span>
                        </span>
                      </span>
                    </div>
                    <div className="text-sm text-gray-500">
                      {assignment.user_email}
                    </div>
                    <div className="text-xs text-gray-400">
                      Assigned: {new Date(assignment.assigned_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleRemoveAssignment(assignment.id)}
                  className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
                  title="Remove assignment"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}