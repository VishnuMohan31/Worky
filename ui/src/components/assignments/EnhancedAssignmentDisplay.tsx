/**
 * EnhancedAssignmentDisplay Component
 * Simple inline display for multiple assignees (Use Case/User Story/Task/Subtask)
 */
import { useState, useEffect } from 'react'
import api from '../../services/api'

interface Assignment {
  id: string
  assignmentId: string
  name: string
  email: string
  role: string
  assignmentType: string
}

interface User {
  id: string
  full_name: string
  email: string
  role: string
  is_team_member?: boolean
}

interface EnhancedAssignmentDisplayProps {
  entityType: 'usecase' | 'userstory' | 'task' | 'subtask'
  entityId: string
  onAssignmentChange?: () => void
}

const ASSIGNMENT_TYPES = [
  { value: 'developer', label: 'Developer', color: 'bg-green-100 text-green-800' },
  { value: 'tester', label: 'Tester', color: 'bg-purple-100 text-purple-800' },
  { value: 'designer', label: 'Designer', color: 'bg-pink-100 text-pink-800' },
  { value: 'reviewer', label: 'Reviewer', color: 'bg-orange-100 text-orange-800' },
  { value: 'lead', label: 'Lead', color: 'bg-blue-100 text-blue-800' }
]

export default function EnhancedAssignmentDisplay({ entityType, entityId, onAssignmentChange }: EnhancedAssignmentDisplayProps) {
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [availableUsers, setAvailableUsers] = useState<User[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRole, setSelectedRole] = useState('developer')
  const [loading, setLoading] = useState(false)

  // Load current assignments
  useEffect(() => {
    loadAssignments()
  }, [entityType, entityId])

  // Load available users when dropdown opens
  useEffect(() => {
    if (showDropdown) {
      loadAvailableUsers()
    }
  }, [showDropdown])

  const loadAssignments = async () => {
    try {
      const assignmentData = await api.getAssignments(entityType, entityId)
      const activeAssignments = assignmentData.filter((a: any) => 
        a.is_active && a.assignment_type !== 'owner'
      )
      
      const assignmentsData = activeAssignments.map((assignment: any) => ({
        id: assignment.user_id,
        assignmentId: assignment.id,
        name: assignment.user_name || 'Unknown User',
        email: assignment.user_email || '',
        role: assignment.user_role || 'Member',
        assignmentType: assignment.assignment_type || 'developer'
      }))
      
      setAssignments(assignmentsData)
    } catch (error) {
      console.error('Failed to load assignments:', error)
    }
  }

  const loadAvailableUsers = async () => {
    try {
      // Get available assignees for this entity
      const users = await api.getAvailableAssignees(entityType, entityId)
      
      // Filter out users who are already assigned
      const assignedIds = assignments.map(a => a.id)
      const available = users.filter((user: User) => 
        !assignedIds.includes(user.id) && user.full_name
      )
      
      setAvailableUsers(available)
    } catch (error) {
      console.error('Failed to load available users:', error)
      // Fallback to all users if available assignees fails
      try {
        const allUsers = await api.getUsers()
        const assignedIds = assignments.map(a => a.id)
        const available = allUsers.filter((user: User) => 
          !assignedIds.includes(user.id) && user.full_name
        )
        setAvailableUsers(available)
      } catch (fallbackError) {
        console.error('Failed to load users:', fallbackError)
      }
    }
  }

  const handleAddAssignment = async (userId: string) => {
    setLoading(true)
    try {
      await api.createAssignment({
        entity_type: entityType,
        entity_id: entityId,
        user_id: userId,
        assignment_type: selectedRole
      })
      
      setShowDropdown(false)
      setSearchTerm('')
      setSelectedRole('developer')
      await loadAssignments()
      onAssignmentChange?.()
    } catch (error) {
      console.error('Failed to add assignment:', error)
      alert('Failed to add assignment. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveAssignment = async (assignmentId: string) => {
    if (!confirm('Are you sure you want to remove this assignment?')) return
    
    setLoading(true)
    try {
      await api.deleteAssignment(assignmentId)
      await loadAssignments()
      onAssignmentChange?.()
    } catch (error) {
      console.error('Failed to remove assignment:', error)
      alert('Failed to remove assignment. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Filter users based on search term
  const filteredUsers = availableUsers.filter(user =>
    user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Get color for assignment type
  const getAssignmentTypeColor = (type: string) => {
    const assignmentType = ASSIGNMENT_TYPES.find(t => t.value === type)
    return assignmentType?.color || 'bg-gray-100 text-gray-800'
  }

  // Get label for assignment type
  const getAssignmentTypeLabel = (type: string) => {
    const assignmentType = ASSIGNMENT_TYPES.find(t => t.value === type)
    return assignmentType?.label || type
  }

  return (
    <div className="assignment-display">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-sm font-medium text-gray-700">Assigned:</span>
      </div>
      
      <div className="flex flex-wrap items-center gap-2">
        {/* Current Assignments */}
        {assignments.map((assignment) => (
          <div
            key={assignment.assignmentId}
            className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${getAssignmentTypeColor(assignment.assignmentType)}`}
          >
            <span>{assignment.name}</span>
            <span className="text-xs opacity-75">({getAssignmentTypeLabel(assignment.assignmentType)})</span>
            <button
              onClick={() => handleRemoveAssignment(assignment.assignmentId)}
              className="ml-1 hover:opacity-80 font-bold"
              disabled={loading}
              title="Remove assignment"
            >
              ×
            </button>
          </div>
        ))}

        {/* Add Assignment Button */}
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
            disabled={loading}
          >
            + Assign
          </button>

          {/* Dropdown */}
          {showDropdown && (
            <div className="absolute top-full left-0 mt-1 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
              <div className="p-3">
                {/* Search */}
                <div className="mb-3">
                  <input
                    type="text"
                    placeholder="🔍 Search team members..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                </div>

                {/* Role Selection */}
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Assignment Role:
                  </label>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {ASSIGNMENT_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* User List */}
                <div className="max-h-48 overflow-y-auto">
                  {filteredUsers.length === 0 ? (
                    <div className="text-sm text-gray-500 text-center py-2">
                      {searchTerm ? 'No users found' : 'No available team members'}
                    </div>
                  ) : (
                    filteredUsers.map((user) => (
                      <button
                        key={user.id}
                        onClick={() => handleAddAssignment(user.id)}
                        className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-md text-sm flex items-center justify-between"
                        disabled={loading}
                      >
                        <div>
                          <div className="font-medium">{user.full_name}</div>
                          <div className="text-gray-500 text-xs">{user.email}</div>
                        </div>
                        <div className="text-right">
                          <span className="text-xs text-gray-400">({user.role})</span>
                          {user.is_team_member && (
                            <div className="text-xs text-green-600">Team Member</div>
                          )}
                        </div>
                      </button>
                    ))
                  )}
                </div>

                {/* Close Button */}
                <div className="mt-3 pt-2 border-t">
                  <button
                    onClick={() => setShowDropdown(false)}
                    className="w-full px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {assignments.length === 0 && (
          <span className="text-sm text-gray-500 italic">No assignments</span>
        )}
      </div>
    </div>
  )
}