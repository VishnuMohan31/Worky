import { useState, useEffect } from 'react'
import api from '../../services/api'
import Modal from '../common/Modal'

interface Assignment {
  id: string
  user_id: string
  user_name?: string
  user_email?: string
  assignment_type: string
}

interface User {
  id: string
  full_name: string
  email: string
  role: string
}

interface AssignmentButtonProps {
  entityType: string
  entityId: string
  currentAssignment?: Assignment
  onAssignmentChange?: () => void
  size?: 'sm' | 'md'
  allAssignments?: Assignment[]  // Add support for multiple assignments
}

export default function AssignmentButton({ 
  entityType, 
  entityId, 
  currentAssignment,
  onAssignmentChange,
  size = 'sm',
  allAssignments = []
}: AssignmentButtonProps) {
  const [showModal, setShowModal] = useState(false)
  const [availableUsers, setAvailableUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (showModal) {
      loadAvailableUsers()
      setSearchTerm('')
    }
  }, [showModal, entityType, entityId])

  const loadAvailableUsers = async () => {
    try {
      setLoading(true)
      const response = await api.getAvailableAssignees(entityType, entityId)
      setAvailableUsers(response)
    } catch (error) {
      console.error('Failed to load users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAssign = async (userId: string) => {
    try {
      setLoading(true)
      
      // DO NOT remove existing assignment - allow multiple assignments
      // Create new assignment directly
      console.log('Creating new assignment for user:', userId)
      await api.createAssignment({
        entity_type: entityType,
        entity_id: entityId,
        user_id: userId,
        assignment_type: getAssignmentType(entityType)
      })
      
      // Reload available users to update the list
      await loadAvailableUsers()
      onAssignmentChange?.()
    } catch (error: any) {
      console.error('Failed to assign:', error)
      alert(error.response?.data?.detail || 'Failed to assign user')
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveAssignment = async (assignmentId: string) => {
    if (!confirm('Are you sure you want to remove this assignment?')) return
    
    try {
      setLoading(true)
      console.log('Removing assignment:', assignmentId)
      await api.deleteAssignment(assignmentId)
      // Reload available users after removal
      await loadAvailableUsers()
      onAssignmentChange?.()
    } catch (error: any) {
      console.error('Failed to remove assignment:', error)
      alert(error.response?.data?.detail || 'Failed to remove assignment')
    } finally {
      setLoading(false)
    }
  }

  const handleUnassign = async () => {
    if (!currentAssignment) return
    
    try {
      setLoading(true)
      console.log('Unassigning user from assignment:', currentAssignment.id)
      await api.deleteAssignment(currentAssignment.id)
      await loadAvailableUsers()
      setShowModal(false)
      onAssignmentChange?.()
    } catch (error: any) {
      console.error('Failed to unassign:', error)
      alert(error.response?.data?.detail || 'Failed to unassign user')
    } finally {
      setLoading(false)
    }
  }

  const getAssignmentType = (entityType: string) => {
    // Client, Program, Project = owner
    if (['client', 'program', 'project'].includes(entityType)) return 'owner'
    // UseCase, UserStory, Task, Subtask = assignee (from team members)
    if (['usecase', 'userstory', 'task', 'subtask'].includes(entityType)) return 'assignee'
    return 'assignee'
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const buttonSize = size === 'sm' ? 'w-7 h-7 text-xs' : 'w-9 h-9 text-sm'
  const assignmentCount = allAssignments.length
  const hasAssignments = assignmentCount > 0

  // Filter available users based on search and existing assignments
  const filteredAvailableUsers = availableUsers.filter(user => {
    const matchesSearch = !searchTerm || 
      user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.role.toLowerCase().includes(searchTerm.toLowerCase())
    
    const notAssigned = !allAssignments.some(a => 
      a.user_id === user.id && a.assignment_type === getAssignmentType(entityType)
    )
    
    return matchesSearch && notAssigned
  })

  const handleCloseModal = () => {
    setShowModal(false)
    setSearchTerm('')
  }

  return (
    <>
      <button
        onClick={(e) => {
          e.stopPropagation()
          setShowModal(true)
        }}
        className={`${buttonSize} rounded-full flex items-center justify-center transition-all duration-200 border-2 font-medium ${
          hasAssignments
            ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 hover:border-blue-300 shadow-sm'
            : 'bg-gray-50 text-gray-500 border-gray-200 hover:bg-gray-100 hover:border-gray-300 hover:text-gray-700'
        }`}
        title={hasAssignments ? `${assignmentCount} assignment${assignmentCount > 1 ? 's' : ''}` : 'Assign user'}
      >
        {hasAssignments ? (
          <span className="font-semibold">
            {assignmentCount > 1 ? assignmentCount : getInitials(allAssignments[0]?.user_name || 'U')}
          </span>
        ) : (
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        )}
      </button>

      {/* Manage Assignments Modal */}
      <Modal
        isOpen={showModal}
        onClose={handleCloseModal}
        title="Manage Assignments"
        size="md"
      >
        <div className="space-y-4">
          {/* Current Assignments Section */}
          {allAssignments.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-900">
                  Current Assignments ({allAssignments.length})
                </h3>
              </div>
              <div className="space-y-2">
                {allAssignments.map((assignment) => (
                  <div
                    key={assignment.id}
                    className="flex items-center justify-between p-3 rounded-lg border border-gray-200 bg-blue-50 hover:bg-blue-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm shadow-sm flex-shrink-0">
                        {getInitials(assignment.user_name || 'U')}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900 truncate">
                          {assignment.user_name || 'Unknown User'}
                        </p>
                        <p className="text-xs text-gray-500 capitalize">
                          {assignment.assignment_type}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleRemoveAssignment(assignment.id)}
                      className="ml-3 p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0"
                      title="Remove assignment"
                      disabled={loading}
                    >
                      <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Add Assignment Section */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Add Team Member
            </h3>
            
            {/* Search Bar */}
            <div className="relative mb-4">
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
                disabled={loading}
              />
            </div>

            {/* Available Users List */}
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="flex flex-col items-center space-y-2">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <p className="text-sm text-gray-500">Loading team members...</p>
                  </div>
                </div>
              ) : filteredAvailableUsers.length === 0 ? (
                <div className="text-center py-8">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-500">
                    {searchTerm ? 'No team members found matching your search' : 'No available team members'}
                  </p>
                </div>
              ) : (
                filteredAvailableUsers.map((user) => (
                  <button
                    key={user.id}
                    onClick={() => handleAssign(user.id)}
                    className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={loading}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm shadow-sm">
                          {getInitials(user.full_name)}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900 truncate">
                          {user.full_name}
                        </p>
                        <p className="text-sm text-gray-500 truncate mt-0.5">
                          {user.email}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          {user.role}
                        </p>
                      </div>
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

            {/* Footer Info */}
            {!loading && filteredAvailableUsers.length > 0 && (
              <div className="pt-3 border-t border-gray-200 mt-4">
                <p className="text-xs text-gray-500 text-center">
                  {filteredAvailableUsers.length} {filteredAvailableUsers.length === 1 ? 'team member' : 'team members'} available
                </p>
              </div>
            )}
          </div>
        </div>
      </Modal>
    </>
  )
}