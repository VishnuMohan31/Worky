/**
 * EnhancedAssignmentDisplay Component
 * Simple inline display for multiple assignees (Use Case/User Story/Task/Subtask)
 */
import { useState, useEffect, useCallback, useRef } from 'react'
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

// Simplified assignment types - UseCase/UserStory/Task/Subtask use "assignee" from team members
const ASSIGNMENT_TYPES = [
  { value: 'assignee', label: 'Assignee', color: 'bg-blue-100 text-blue-800' }
]

export default function EnhancedAssignmentDisplay({ entityType, entityId, onAssignmentChange }: EnhancedAssignmentDisplayProps) {
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [availableUsers, setAvailableUsers] = useState<User[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRole, setSelectedRole] = useState('assignee')
  const [loading, setLoading] = useState(false)
  const [loadingUsers, setLoadingUsers] = useState(false)
  
  // Refs to prevent multiple simultaneous API calls
  const loadingAssignmentsRef = useRef(false)
  const loadingUsersRef = useRef(false)

  // Load current assignments with useCallback to prevent unnecessary re-renders
  const loadAssignments = useCallback(async () => {
    // Prevent multiple simultaneous calls, but allow if not currently loading
    if (loadingAssignmentsRef.current) {
      console.log('Already loading assignments, skipping...')
      return []
    }
    
    loadingAssignmentsRef.current = true
    try {
      console.log(`Loading assignments for ${entityType}:${entityId}`)
      const assignmentData = await api.getAssignments({
        entity_type: entityType,
        entity_id: entityId
      })
      console.log('Raw assignment data:', assignmentData)
      console.log('Raw assignment data type:', typeof assignmentData, 'Is array:', Array.isArray(assignmentData))
      
      // Handle different response formats
      let assignmentsArray: any[] = []
      if (Array.isArray(assignmentData)) {
        assignmentsArray = assignmentData
      } else if (assignmentData && typeof assignmentData === 'object') {
        // If it's an object, try to extract an array from common properties
        if (Array.isArray(assignmentData.items)) {
          assignmentsArray = assignmentData.items
        } else if (Array.isArray(assignmentData.data)) {
          assignmentsArray = assignmentData.data
        } else {
          console.warn('Unexpected assignment data format:', assignmentData)
        }
      }
      
      console.log('Assignments array:', assignmentsArray)
      
      // Filter for active assignments (exclude owner type for usecase/userstory/task/subtask)
      const activeAssignments = assignmentsArray.filter((a: any) => {
        const isActive = a.is_active === true || a.is_active === undefined
        const isNotOwner = a.assignment_type !== 'owner'
        console.log(`Assignment ${a.id}: is_active=${a.is_active}, assignment_type=${a.assignment_type}, passes=${isActive && isNotOwner}`)
        return isActive && isNotOwner
      })
      console.log('Active assignments (non-owner):', activeAssignments)
      
      const assignmentsData = activeAssignments.map((assignment: any) => ({
        id: assignment.user_id,
        assignmentId: assignment.id,
        name: assignment.user_name || assignment.user?.full_name || 'Unknown User',
        email: assignment.user_email || assignment.user?.email || '',
        role: assignment.user_role || assignment.user?.role || 'Member',
        assignmentType: assignment.assignment_type || 'assignee'
      }))
      
      console.log('Processed assignments data:', assignmentsData)
      setAssignments(assignmentsData)
      return assignmentsData
    } catch (error) {
      console.error('Failed to load assignments:', error)
      setAssignments([])
      return []
    } finally {
      loadingAssignmentsRef.current = false
    }
  }, [entityType, entityId])

  // Load available users with debouncing to prevent excessive API calls
  const loadAvailableUsers = useCallback(async (currentAssignments?: Assignment[]) => {
    // Prevent multiple simultaneous calls
    if (loadingUsersRef.current) {
      console.log('Already loading users, skipping...')
      return
    }
    
    loadingUsersRef.current = true
    setLoadingUsers(true)
    try {
      console.log('Loading available users...')
      
      // Use the provided assignments or current state
      const assignmentsToUse = currentAssignments || assignments
      console.log('Current assignments for filtering:', assignmentsToUse)
      
      // Get available assignees for this entity
      const users = await api.getAvailableAssignees(entityType, entityId)
      console.log('All available users from API:', users)
      
      // Filter out users who are already assigned (regardless of assignment type)
      const assignedUserIds = assignmentsToUse.map(a => a.id)
      console.log(`Already assigned user IDs:`, assignedUserIds)
      
      const available = users.filter((user: User) => 
        !assignedUserIds.includes(user.id) && user.full_name
      )
      
      console.log('Filtered available users:', available)
      setAvailableUsers(available)
    } catch (error) {
      console.error('Failed to load available users:', error)
      // Fallback to all users if available assignees fails
      try {
        const allUsers = await api.getUsers()
        const assignmentsToUse = currentAssignments || assignments
        const assignedUserIds = assignmentsToUse.map(a => a.id)
        const available = allUsers.filter((user: User) => 
          !assignedUserIds.includes(user.id) && user.full_name
        )
        console.log('Fallback: filtered available users from all users:', available)
        setAvailableUsers(available)
      } catch (fallbackError) {
        console.error('Failed to load users:', fallbackError)
        setAvailableUsers([])
      }
    } finally {
      setLoadingUsers(false)
      loadingUsersRef.current = false
    }
  }, [entityType, entityId]) // REMOVED assignments dependency to prevent infinite loop

  // Load assignments on mount and when entity changes
  useEffect(() => {
    // Reset loading flag when entity changes to allow fresh load
    loadingAssignmentsRef.current = false
    // Clear assignments immediately when entity changes
    setAssignments([])
    // Load assignments for the new entity
    loadAssignments()
  }, [entityType, entityId, loadAssignments])

  // Load available users when dropdown opens or role changes
  useEffect(() => {
    if (showDropdown && !loadingUsersRef.current) {
      // Always reload assignments first, then load available users
      loadAssignments().then((freshAssignments) => {
        loadAvailableUsers(freshAssignments)
      })
    }
  }, [showDropdown, selectedRole, loadAssignments, loadAvailableUsers])

  const handleAddAssignment = async (userId: string) => {
    setLoading(true)
    try {
      console.log('Adding assignment:', { entityType, entityId, userId, selectedRole })
      
      await api.createAssignment({
        entity_type: entityType,
        entity_id: entityId,
        user_id: userId,
        assignment_type: selectedRole
      })
      
      console.log('Assignment created successfully')
      
      // Close dropdown and reset form
      setShowDropdown(false)
      setSearchTerm('')
      setSelectedRole('assignee')
      
      // Reload assignments and notify parent
      const freshAssignments = await loadAssignments()
      
      // Update available users with fresh assignment data
      await loadAvailableUsers(freshAssignments)
      
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
      console.log('Removing assignment:', assignmentId)
      
      await api.deleteAssignment(assignmentId)
      
      console.log('Assignment removed successfully')
      
      // Reload assignments and notify parent
      const freshAssignments = await loadAssignments()
      
      // Update available users with fresh assignment data
      await loadAvailableUsers(freshAssignments)
      
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
        {loading && (
          <span className="text-xs text-blue-600">Updating...</span>
        )}
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
                {/* Loading indicator */}
                {loadingUsers && (
                  <div className="mb-3 text-center">
                    <div className="text-sm text-blue-600">Loading available users...</div>
                  </div>
                )}

                {/* Search */}
                <div className="mb-3">
                  <input
                    type="text"
                    placeholder="🔍 Search team members..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                    disabled={loadingUsers}
                  />
                </div>

                {/* Role Selection */}
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Select Team Member:
                  </label>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loadingUsers}
                  >
                    {ASSIGNMENT_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-xs text-gray-500">
                    Assign a team member to this task
                  </p>
                </div>

                {/* User List */}
                <div className="max-h-48 overflow-y-auto">
                  {loadingUsers ? (
                    <div className="text-sm text-gray-500 text-center py-4">
                      Loading users...
                    </div>
                  ) : filteredUsers.length === 0 ? (
                    <div className="text-sm text-gray-500 text-center py-2">
                      {searchTerm ? 'No users found matching your search' : 'No available team members'}
                    </div>
                  ) : (
                    filteredUsers.map((user) => (
                      <button
                        key={user.id}
                        onClick={() => handleAddAssignment(user.id)}
                        className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-md text-sm flex items-center justify-between"
                        disabled={loading || loadingUsers}
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

                {/* Debug Info */}
                <div className="mt-3 pt-2 border-t text-xs text-gray-500">
                  <div>Current assignments: {assignments.length}</div>
                  <div>Available users: {availableUsers.length}</div>
                  <div>Filtered users: {filteredUsers.length}</div>
                </div>

                {/* Close Button */}
                <div className="mt-3 pt-2 border-t">
                  <button
                    onClick={() => setShowDropdown(false)}
                    className="w-full px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                    disabled={loading}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {assignments.length === 0 && (
          <span className="text-sm text-gray-500 italic">No assignees</span>
        )}
      </div>
    </div>
  )
}