import { useState, useEffect } from 'react'
import api from '../../services/api'

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
}

export default function AssignmentButton({ 
  entityType, 
  entityId, 
  currentAssignment,
  onAssignmentChange,
  size = 'sm'
}: AssignmentButtonProps) {
  const [showDropdown, setShowDropdown] = useState(false)
  const [availableUsers, setAvailableUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (showDropdown) {
      loadAvailableUsers()
    }
  }, [showDropdown, entityType, entityId])

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
      
      // Remove existing assignment if any
      if (currentAssignment) {
        console.log('Removing existing assignment:', currentAssignment.id)
        await api.deleteAssignment(currentAssignment.id)
      }
      
      // Create new assignment
      console.log('Creating new assignment for user:', userId)
      await api.createAssignment({
        entity_type: entityType,
        entity_id: entityId,
        user_id: userId,
        assignment_type: getAssignmentType(entityType)
      })
      
      setShowDropdown(false)
      onAssignmentChange?.()
    } catch (error: any) {
      console.error('Failed to assign:', error)
      alert(error.response?.data?.detail || 'Failed to assign user')
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
      setShowDropdown(false)
      onAssignmentChange?.()
    } catch (error: any) {
      console.error('Failed to unassign:', error)
      alert(error.response?.data?.detail || 'Failed to unassign user')
    } finally {
      setLoading(false)
    }
  }

  const getAssignmentType = (entityType: string) => {
    if (['task', 'subtask'].includes(entityType)) return 'developer'
    if (['userstory', 'usecase'].includes(entityType)) return 'owner'
    return 'developer'
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

  return (
    <div className="relative">
      <button
        onClick={(e) => {
          e.stopPropagation()
          setShowDropdown(!showDropdown)
        }}
        className={`${buttonSize} rounded-full flex items-center justify-center transition-all duration-200 border-2 font-medium ${
          currentAssignment
            ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 hover:border-blue-300 shadow-sm'
            : 'bg-gray-50 text-gray-500 border-gray-200 hover:bg-gray-100 hover:border-gray-300 hover:text-gray-700'
        }`}
        title={currentAssignment ? `Assigned to ${currentAssignment.user_name}` : 'Assign user'}
      >
        {currentAssignment ? (
          <span className="font-semibold">
            {getInitials(currentAssignment.user_name || 'U')}
          </span>
        ) : (
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        )}
      </button>

      {showDropdown && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setShowDropdown(false)}
          />
          <div className="absolute right-0 mt-2 w-72 bg-white border border-gray-200 rounded-xl shadow-xl z-20 overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50">
              <h4 className="font-semibold text-gray-900 text-sm">
                {currentAssignment ? 'Reassign' : 'Assign'} {entityType.charAt(0).toUpperCase() + entityType.slice(1)}
              </h4>
              <p className="text-xs text-gray-600 mt-1">
                Select a team member to assign this {entityType}
              </p>
            </div>
            
            <div className="max-h-48 overflow-y-auto">
              {loading ? (
                <div className="p-3 text-center text-gray-500">Loading...</div>
              ) : availableUsers.length === 0 ? (
                <div className="p-3 text-center text-gray-500">No users available</div>
              ) : (
                <div className="py-1">
                  {availableUsers.map((user) => (
                    <button
                      key={user.id}
                      onClick={() => handleAssign(user.id)}
                      className="w-full px-4 py-3 text-left hover:bg-blue-50 flex items-center space-x-3 transition-colors duration-150"
                      disabled={loading}
                    >
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center border-2 border-blue-200">
                        <span className="text-xs font-semibold text-blue-700">
                          {getInitials(user.full_name)}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-semibold text-gray-900 truncate">
                          {user.full_name}
                        </div>
                        <div className="text-xs text-gray-500 truncate">
                          {user.role} • {user.email}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            {currentAssignment && (
              <div className="p-3 border-t border-gray-100 bg-gray-50">
                <button
                  onClick={handleUnassign}
                  className="w-full px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg border border-red-200 hover:border-red-300 transition-colors duration-150"
                  disabled={loading}
                >
                  Remove Assignment
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}