/**
 * OwnerSelector Component
 * Multi-select component for choosing owners during entity creation
 */
import { useState, useEffect } from 'react'
import api from '../../services/api'

interface User {
  id: string
  full_name: string
  email: string
  role: string
}

interface OwnerSelectorProps {
  entityType: 'client' | 'program' | 'project'
  selectedOwners: string[]
  onOwnersChange: (ownerIds: string[]) => void
  disabled?: boolean
  existingEntityId?: string // For edit mode - load existing owners
}

export default function OwnerSelector({ entityType, selectedOwners, onOwnersChange, disabled = false, existingEntityId }: OwnerSelectorProps) {
  const [availableUsers, setAvailableUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showDropdown, setShowDropdown] = useState(false)
  const [existingOwners, setExistingOwners] = useState<User[]>([])

  useEffect(() => {
    loadAvailableUsers()
    if (existingEntityId) {
      loadExistingOwners()
    }
  }, [existingEntityId])

  const loadExistingOwners = async () => {
    if (!existingEntityId) return
    
    try {
      const assignments = await api.getAssignments({
        entity_type: entityType,
        entity_id: existingEntityId,
        assignment_type: 'owner'
      })
      
      const ownerIds = assignments.map((a: any) => a.user_id)
      const users = await api.getUsers()
      const owners = users.filter((u: User) => ownerIds.includes(u.id))
      
      setExistingOwners(owners)
      onOwnersChange(ownerIds) // Set initial selected owners
    } catch (error) {
      console.error('Failed to load existing owners:', error)
    }
  }

  const loadAvailableUsers = async () => {
    setLoading(true)
    try {
      const users = await api.getUsers()
      
      // Filter users by role compatibility for ownership
      const eligibleRoles = ['Admin', 'Owner', 'Project Manager']
      const eligible = users.filter((user: User) => 
        user.full_name && eligibleRoles.includes(user.role)
      )
      
      setAvailableUsers(eligible)
    } catch (error) {
      console.error('Failed to load users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleOwner = async (userId: string) => {
    if (existingEntityId) {
      // Edit mode - directly update assignments in backend
      try {
        if (selectedOwners.includes(userId)) {
          // Remove owner assignment
          const assignments = await api.getAssignments({
            entity_type: entityType,
            entity_id: existingEntityId,
            assignment_type: 'owner',
            user_id: userId
          })
          
          if (assignments.length > 0) {
            await api.deleteAssignment(assignments[0].id)
          }
          
          onOwnersChange(selectedOwners.filter(id => id !== userId))
        } else {
          // Add owner assignment
          await api.createAssignment({
            entity_type: entityType,
            entity_id: existingEntityId,
            user_id: userId,
            assignment_type: 'owner'
          })
          
          onOwnersChange([...selectedOwners, userId])
        }
      } catch (error) {
        console.error('Failed to update owner assignment:', error)
      }
    } else {
      // Create mode - just update local state
      if (selectedOwners.includes(userId)) {
        onOwnersChange(selectedOwners.filter(id => id !== userId))
      } else {
        onOwnersChange([...selectedOwners, userId])
      }
    }
  }

  const getSelectedUsers = () => {
    return availableUsers.filter(user => selectedOwners.includes(user.id))
  }

  const filteredUsers = availableUsers.filter(user =>
    user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="owner-selector">
      <label className="block text-sm font-medium mb-2">
        {existingEntityId ? 'Manage Owners' : 'Assign Owners'}
        <span className="text-gray-500 text-xs ml-2">
          {existingEntityId ? '(Add or remove owners)' : '(Optional - can be added later)'}
        </span>
      </label>
      
      {/* Selected Owners Display */}
      <div className="mb-3">
        {getSelectedUsers().length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {getSelectedUsers().map((user) => (
              <div
                key={user.id}
                className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg text-sm"
              >
                <div className="flex items-center justify-center w-5 h-5 bg-blue-100 rounded-full">
                  <span className="text-xs font-bold">{user.full_name.charAt(0).toUpperCase()}</span>
                </div>
                <span className="font-medium">{user.full_name}</span>
                <button
                  type="button"
                  onClick={() => handleToggleOwner(user.id)}
                  className="text-blue-600 hover:text-blue-800 hover:bg-blue-100 rounded-full p-0.5 transition-colors"
                  disabled={disabled}
                  title="Remove owner"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-gray-500 italic">No owners selected</div>
        )}
      </div>

      {/* Add Owner Button */}
      <div className="relative">
        <button
          type="button"
          onClick={() => setShowDropdown(!showDropdown)}
          className="inline-flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors disabled:opacity-50"
          disabled={disabled || loading}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Owner
        </button>

        {/* Dropdown */}
        {showDropdown && (
          <div className="absolute top-full left-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
            <div className="p-3">
              {/* Search */}
              <div className="mb-3">
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
                  />
                </div>
              </div>

              {/* User List */}
              <div className="max-h-48 overflow-y-auto">
                {filteredUsers.length === 0 ? (
                  <div className="text-sm text-gray-500 text-center py-3">
                    {searchTerm ? (
                      'No users found matching your search'
                    ) : availableUsers.length === 0 ? (
                      <div>
                        <p className="mb-1">No eligible users available</p>
                        <p className="text-xs text-gray-400">
                          Only Admin, Owner, and Project Manager roles can be assigned as owners
                        </p>
                      </div>
                    ) : (
                      'No users found'
                    )}
                  </div>
                ) : (
                  <div className="space-y-1">
                    {filteredUsers.map((user) => {
                      const isSelected = selectedOwners.includes(user.id)
                      return (
                        <button
                          key={user.id}
                          type="button"
                          onClick={() => handleToggleOwner(user.id)}
                          className={`w-full text-left px-3 py-2 rounded-md text-sm flex items-center gap-3 transition-colors ${
                            isSelected 
                              ? 'bg-blue-50 border border-blue-200' 
                              : 'hover:bg-gray-50'
                          }`}
                        >
                          <div className="flex items-center justify-center w-6 h-6 bg-gray-100 rounded-full">
                            <span className="text-xs font-semibold text-gray-600">{user.full_name.charAt(0).toUpperCase()}</span>
                          </div>
                          <div className="flex-1">
                            <div className="font-medium text-gray-900">{user.full_name}</div>
                            <div className="text-gray-500 text-xs">{user.email}</div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded font-medium">{user.role}</span>
                            {isSelected && (
                              <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        </button>
                      )
                    })}
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="mt-3 pt-3 border-t border-gray-200 flex justify-between items-center">
                <span className="text-xs text-gray-500">
                  {selectedOwners.length} owner{selectedOwners.length !== 1 ? 's' : ''} selected
                </span>
                <button
                  type="button"
                  onClick={() => setShowDropdown(false)}
                  className="text-sm text-gray-600 hover:text-gray-800 px-3 py-1 rounded hover:bg-gray-100 transition-colors"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Help Text */}
      <p className="mt-2 text-xs text-gray-500">
        Select users who will be responsible for managing this {entityType}. Only Admin, Owner, and Project Manager roles can be assigned as owners.
      </p>
    </div>
  )
}