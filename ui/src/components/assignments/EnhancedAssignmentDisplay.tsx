/**
 * EnhancedAssignmentDisplay Component
 * Simple inline display for multiple assignees (Use Case/User Story/Task/Subtask)
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import api from '../../services/api'
import Modal from '../common/Modal'

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
  const [showModal, setShowModal] = useState(false)
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

  // Load available users when modal opens or role changes
  useEffect(() => {
    if (showModal && !loadingUsersRef.current) {
      // Always reload assignments first, then load available users
      loadAssignments().then((freshAssignments) => {
        loadAvailableUsers(freshAssignments)
      })
    }
  }, [showModal, selectedRole, loadAssignments, loadAvailableUsers])

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
      
      // Close modal and reset form
      setShowModal(false)
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
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.role.toLowerCase().includes(searchTerm.toLowerCase())
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

  // Get user initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  // Handle modal close
  const handleCloseModal = () => {
    setShowModal(false)
    setSearchTerm('')
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
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-sm font-medium hover:bg-blue-100 transition-colors border border-blue-200"
          disabled={loading}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Assign
        </button>

        {/* Assignment Modal */}
        <Modal
          isOpen={showModal}
          onClose={handleCloseModal}
          title="Assign Team Members"
          size="md"
        >
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search by name, email, or role..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
                disabled={loadingUsers}
              />
            </div>

            {/* Role Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Assignment Type
              </label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loadingUsers}
              >
                {ASSIGNMENT_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Loading State */}
            {loadingUsers && (
              <div className="flex items-center justify-center py-8">
                <div className="flex flex-col items-center space-y-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="text-sm text-gray-500">Loading available team members...</p>
                </div>
              </div>
            )}

            {/* User List */}
            {!loadingUsers && (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {filteredUsers.length === 0 ? (
                  <div className="text-center py-8">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <p className="mt-2 text-sm text-gray-500">
                      {searchTerm ? 'No team members found matching your search' : 'No available team members'}
                    </p>
                  </div>
                ) : (
                  filteredUsers.map((user) => (
                    <button
                      key={user.id}
                      onClick={() => handleAddAssignment(user.id)}
                      className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={loading || loadingUsers}
                    >
                      <div className="flex items-center space-x-3">
                        {/* Avatar */}
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm shadow-sm">
                            {getInitials(user.full_name)}
                          </div>
                        </div>
                        
                        {/* User Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <p className="text-sm font-semibold text-gray-900 truncate">
                              {user.full_name}
                            </p>
                            {user.is_team_member && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                Team
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-500 truncate mt-0.5">
                            {user.email}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {user.role}
                          </p>
                        </div>

                        {/* Arrow Icon */}
                        <div className="flex-shrink-0">
                          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </div>
                    </button>
                  ))
                )}
              </div>
            )}

            {/* Footer Info */}
            {!loadingUsers && filteredUsers.length > 0 && (
              <div className="pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500 text-center">
                  {filteredUsers.length} {filteredUsers.length === 1 ? 'team member' : 'team members'} available
                </p>
              </div>
            )}
          </div>
        </Modal>

        {assignments.length === 0 && (
          <span className="text-sm text-gray-500 italic">No assignees</span>
        )}
      </div>
    </div>
  )
}