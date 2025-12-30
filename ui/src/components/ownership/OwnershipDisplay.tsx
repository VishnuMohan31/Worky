/**
 * OwnershipDisplay Component
 * Simple inline display for multiple owners (Client/Program/Project)
 */
import { useState, useEffect } from 'react'
import api from '../../services/api'

interface Owner {
  id: string
  assignmentId: string
  name: string
  email: string
  role: string
}

interface User {
  id: string
  full_name: string
  email: string
  role: string
  primary_role?: string
  secondary_roles?: string[]
}

interface OwnershipDisplayProps {
  entityType: 'client' | 'program' | 'project'
  entityId: string
  onOwnershipChange?: () => void
}

export default function OwnershipDisplay({ entityType, entityId, onOwnershipChange }: OwnershipDisplayProps) {
  const [owners, setOwners] = useState<Owner[]>([])
  const [availableUsers, setAvailableUsers] = useState<User[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)

  // Load current owners
  useEffect(() => {
    loadOwners()
  }, [entityType, entityId])

  // Load available users when dropdown opens
  useEffect(() => {
    if (showDropdown) {
      loadAvailableUsers()
    }
  }, [showDropdown])

  const loadOwners = async () => {
    try {
      console.log('Loading owners for:', { entityType, entityId })
      const assignments = await api.getAssignments({
        entity_type: entityType,
        entity_id: entityId,
        assignment_type: 'owner'
      })
      console.log('All assignments:', assignments)
      
      const ownerAssignments = assignments.filter((a: any) => a.assignment_type === 'owner' && a.is_active)
      console.log('Owner assignments:', ownerAssignments)
      
      const ownersData = ownerAssignments.map((assignment: any) => ({
        id: assignment.user_id,
        assignmentId: assignment.id,
        name: assignment.user_name || 'Unknown User',
        email: assignment.user_email || '',
        role: assignment.user_role || 'Owner'
      }))
      
      console.log('Processed owners data:', ownersData)
      setOwners(ownersData)
    } catch (error: any) {
      console.error('Failed to load owners:', error)
      
      if (error.response?.status === 401) {
        console.log('Authentication failed, redirecting to login')
        window.location.href = '/login'
      }
    }
  }

  const loadAvailableUsers = async () => {
    try {
      console.log('Loading eligible users for ownership...')
      
      // Use the backend validation endpoint to get only eligible users
      // This ensures frontend and backend validation rules are always in sync
      const eligibleUsers = await api.getEligibleUsers(entityType, entityId, 'owner')
      console.log('Eligible users from backend:', eligibleUsers)
      
      // Filter out users who are already owners
      const ownerIds = owners.map(o => o.id)
      
      const available = eligibleUsers
        .filter((user: any) => !ownerIds.includes(user.id) && user.full_name)
        .map((user: any) => ({
          id: user.id,
          full_name: user.full_name,
          email: user.email,
          role: user.role, // This is already the primary_role from backend
          primary_role: user.role,
          secondary_roles: []
        }))
      
      console.log('Available users for ownership:', available)
      setAvailableUsers(available)
    } catch (error: any) {
      console.error('Failed to load eligible users:', error)
      
      // Fallback to old method if the validation endpoint fails
      if (error.response?.status === 404 || error.response?.status === 500) {
        console.log('Falling back to manual filtering...')
        try {
          const users = await api.getUsers()
          const ownerIds = owners.map(o => o.id)
          const eligibleRoles = ['Admin', 'Owner', 'Project Manager', 'Architect']
          
          const available = users.filter((user: User) => 
            !ownerIds.includes(user.id) && 
            user.full_name &&
            eligibleRoles.includes(user.role)
          )
          setAvailableUsers(available)
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError)
        }
      }
      
      if (error.response?.status === 401) {
        console.log('Authentication failed, redirecting to login')
        window.location.href = '/login'
      }
    }
  }

  const handleAddOwner = async (userId: string) => {
    setLoading(true)
    try {
      console.log('Adding owner:', { entityType, entityId, userId })
      
      const assignmentData = {
        entity_type: entityType,
        entity_id: entityId,
        user_id: userId,
        assignment_type: 'owner'
      }
      
      console.log('Assignment data:', assignmentData)
      
      const result = await api.createAssignment(assignmentData)
      console.log('Assignment created:', result)
      
      setShowDropdown(false)
      setSearchTerm('')
      await loadOwners()
      onOwnershipChange?.()
    } catch (error: any) {
      console.error('Failed to add owner:', error)
      
      let errorMessage = 'Failed to add owner. Please try again.'
      
      if (error.response) {
        const status = error.response.status
        const data = error.response.data
        
        console.error('Error response:', { status, data })
        
        if (status === 401) {
          errorMessage = 'Authentication failed. Please log in again.'
          // Redirect to login
          window.location.href = '/login'
          return
        } else if (status === 403) {
          errorMessage = 'You do not have permission to assign owners.'
        } else if (status === 400) {
          if (data?.detail) {
            errorMessage = data.detail
          } else {
            errorMessage = 'Invalid request. Please check the data and try again.'
          }
        } else if (status === 422) {
          if (data?.detail) {
            if (Array.isArray(data.detail)) {
              errorMessage = data.detail.map((err: any) => err.msg).join(', ')
            } else {
              errorMessage = data.detail
            }
          } else {
            errorMessage = 'Validation error. Please check your input.'
          }
        } else {
          errorMessage = data?.detail || data?.message || `Server error (${status})`
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      alert(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveOwner = async (assignmentId: string) => {
    if (!confirm('Are you sure you want to remove this owner?')) return
    
    setLoading(true)
    try {
      await api.deleteAssignment(assignmentId)
      await loadOwners()
      onOwnershipChange?.()
    } catch (error) {
      console.error('Failed to remove owner:', error)
      alert('Failed to remove owner. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Filter users based on search term
  const filteredUsers = availableUsers.filter(user =>
    user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="ownership-display">
      {/* Current Owners */}
      <div className="mb-4">
        {owners.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {owners.map((owner) => (
              <div
                key={owner.assignmentId}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg text-sm font-medium"
              >
                <div className="flex items-center justify-center w-6 h-6 bg-blue-100 rounded-full">
                  <span className="text-xs font-bold">{owner.name.charAt(0).toUpperCase()}</span>
                </div>
                <div className="flex flex-col">
                  <span className="font-semibold">{owner.name}</span>
                  <span className="text-xs text-blue-600">{owner.email}</span>
                </div>
                <button
                  onClick={() => handleRemoveOwner(owner.assignmentId)}
                  className="ml-2 text-blue-600 hover:text-blue-800 hover:bg-blue-100 rounded-full p-1 transition-colors"
                  disabled={loading}
                  title="Remove owner"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-600">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
            </svg>
            <span className="text-sm">No owners assigned yet</span>
          </div>
        )}
      </div>

      {/* Add Owner Section */}
      <div className="relative">
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
          disabled={loading}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Owner
        </button>

        {/* Dropdown */}
        {showDropdown && (
          <div className="absolute top-full left-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
            <div className="p-4">
              {/* Search */}
              <div className="mb-4">
                <div className="relative">
                  <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <input
                    type="text"
                    placeholder="Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    autoFocus
                  />
                </div>
              </div>

              {/* User List */}
              <div className="max-h-64 overflow-y-auto">
                {filteredUsers.length === 0 ? (
                  <div className="text-sm text-gray-500 text-center py-4">
                    {searchTerm ? (
                      'No users found matching your search'
                    ) : availableUsers.length === 0 ? (
                      <div>
                        <p className="mb-2">No eligible users available</p>
                        <p className="text-xs text-gray-400">
                          Only Admin, Owner, Architect, and Project Manager roles can be assigned as owners
                        </p>
                      </div>
                    ) : (
                      'No users found'
                    )}
                  </div>
                ) : (
                  <div className="space-y-1">
                    {filteredUsers.map((user) => (
                      <button
                        key={user.id}
                        onClick={() => handleAddOwner(user.id)}
                        className="w-full text-left px-3 py-3 hover:bg-gray-50 rounded-md text-sm flex items-center gap-3 transition-colors"
                        disabled={loading}
                      >
                        <div className="flex items-center justify-center w-8 h-8 bg-gray-100 rounded-full">
                          <span className="text-sm font-semibold text-gray-600">{user.full_name.charAt(0).toUpperCase()}</span>
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{user.full_name}</div>
                          <div className="text-gray-500 text-xs">{user.email}</div>
                        </div>
                        <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded font-medium">{user.primary_role || user.role}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="mt-4 pt-3 border-t border-gray-200 flex justify-between items-center">
                <span className="text-xs text-gray-500">
                  {filteredUsers.length} eligible user{filteredUsers.length !== 1 ? 's' : ''} available
                  {availableUsers.length === 0 && (
                    <span className="block text-gray-400 mt-1">
                      (Admin/Owner/Architect/PM roles only)
                    </span>
                  )}
                </span>
                <button
                  onClick={() => setShowDropdown(false)}
                  className="text-sm text-gray-600 hover:text-gray-800 px-3 py-1 rounded hover:bg-gray-100 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}