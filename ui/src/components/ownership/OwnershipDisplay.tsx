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
      const assignments = await api.getAssignments(entityType, entityId)
      const ownerAssignments = assignments.filter((a: any) => a.assignment_type === 'owner' && a.is_active)
      
      const ownersData = ownerAssignments.map((assignment: any) => ({
        id: assignment.user_id,
        assignmentId: assignment.id,
        name: assignment.user_name || 'Unknown User',
        email: assignment.user_email || '',
        role: assignment.user_role || 'Owner'
      }))
      
      setOwners(ownersData)
    } catch (error) {
      console.error('Failed to load owners:', error)
    }
  }

  const loadAvailableUsers = async () => {
    try {
      const users = await api.getUsers()
      // Filter out users who are already owners
      const ownerIds = owners.map(o => o.id)
      const available = users.filter((user: User) => 
        !ownerIds.includes(user.id) && user.full_name
      )
      setAvailableUsers(available)
    } catch (error) {
      console.error('Failed to load users:', error)
    }
  }

  const handleAddOwner = async (userId: string) => {
    setLoading(true)
    try {
      await api.createAssignment({
        entity_type: entityType,
        entity_id: entityId,
        user_id: userId,
        assignment_type: 'owner'
      })
      
      setShowDropdown(false)
      setSearchTerm('')
      await loadOwners()
      onOwnershipChange?.()
    } catch (error) {
      console.error('Failed to add owner:', error)
      alert('Failed to add owner. Please try again.')
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
      <div className="flex items-center gap-2 mb-2">
        <span className="text-sm font-medium text-gray-700">Owners:</span>
      </div>
      
      <div className="flex flex-wrap items-center gap-2">
        {/* Current Owners */}
        {owners.map((owner) => (
          <div
            key={owner.assignmentId}
            className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
          >
            <span>{owner.name}</span>
            <button
              onClick={() => handleRemoveOwner(owner.assignmentId)}
              className="ml-1 text-blue-600 hover:text-blue-800 font-bold"
              disabled={loading}
              title="Remove owner"
            >
              ×
            </button>
          </div>
        ))}

        {/* Add Owner Button */}
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
            disabled={loading}
          >
            + Add Owner
          </button>

          {/* Dropdown */}
          {showDropdown && (
            <div className="absolute top-full left-0 mt-1 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
              <div className="p-3">
                {/* Search */}
                <div className="mb-3">
                  <input
                    type="text"
                    placeholder="🔍 Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                </div>

                {/* User List */}
                <div className="max-h-48 overflow-y-auto">
                  {filteredUsers.length === 0 ? (
                    <div className="text-sm text-gray-500 text-center py-2">
                      {searchTerm ? 'No users found' : 'No available users'}
                    </div>
                  ) : (
                    filteredUsers.map((user) => (
                      <button
                        key={user.id}
                        onClick={() => handleAddOwner(user.id)}
                        className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-md text-sm flex items-center justify-between"
                        disabled={loading}
                      >
                        <div>
                          <div className="font-medium">{user.full_name}</div>
                          <div className="text-gray-500 text-xs">{user.email}</div>
                        </div>
                        <span className="text-xs text-gray-400">({user.role})</span>
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

        {owners.length === 0 && (
          <span className="text-sm text-gray-500 italic">No owners assigned</span>
        )}
      </div>
    </div>
  )
}