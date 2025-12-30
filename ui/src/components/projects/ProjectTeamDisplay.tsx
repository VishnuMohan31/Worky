import { useState, useEffect } from 'react'
import api from '../../services/api'

interface Team {
  id: string
  name: string
  description?: string
  project_id: string
  member_count: number
  is_active: boolean
}

interface TeamMember {
  id: string
  user_id: string
  user_name: string
  user_email: string
  role: string
  joined_at: string
  is_active: boolean
}

interface User {
  id: string
  full_name: string
  email: string
  role: string
}

interface ProjectTeamDisplayProps {
  projectId: string
}

const ProjectTeamDisplay: React.FC<ProjectTeamDisplayProps> = ({ projectId }) => {
  const [team, setTeam] = useState<Team | null>(null)
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [loading, setLoading] = useState(false)
  
  // Modal states
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [allTeams, setAllTeams] = useState<Team[]>([])
  const [allUsers, setAllUsers] = useState<User[]>([])
  const [loadingTeams, setLoadingTeams] = useState(false)
  const [isCreatingNew, setIsCreatingNew] = useState(false)
  const [selectedTeamId, setSelectedTeamId] = useState<string>('')
  const [newTeamData, setNewTeamData] = useState({ name: '', description: '' })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  
  // Add member modal states
  const [showAddMemberModal, setShowAddMemberModal] = useState(false)
  const [newMemberData, setNewMemberData] = useState({ user_id: '', role: 'Developer' })

  useEffect(() => {
    loadProjectTeam()
  }, [projectId])

  const loadProjectTeam = async () => {
    try {
      setLoading(true)
      
      // Get teams for this project
      const teams = await api.getTeams(projectId)
      if (teams && teams.length > 0) {
        const projectTeam = teams[0] // Assuming one team per project
        setTeam(projectTeam)
        
        // Load team members
        const members = await api.getTeamMembers(projectTeam.id)
        setTeamMembers(members)
      } else {
        setTeam(null)
        setTeamMembers([])
      }
    } catch (error) {
      console.error('Failed to load project team:', error)
      setTeam(null)
      setTeamMembers([])
    } finally {
      setLoading(false)
    }
  }

  const loadAllTeamsAndUsers = async () => {
    try {
      setLoadingTeams(true)
      const [teamsData, usersData] = await Promise.all([
        api.getTeams(), // Get all teams
        api.getUsers()
      ])
      setAllTeams(Array.isArray(teamsData) ? teamsData : [])
      setAllUsers(Array.isArray(usersData) ? usersData : [])
    } catch (error) {
      console.error('Failed to load teams and users:', error)
    } finally {
      setLoadingTeams(false)
    }
  }

  const handleOpenAssignModal = () => {
    setShowAssignModal(true)
    setIsCreatingNew(!team) // Default to create new if no team exists
    setSelectedTeamId('')
    setNewTeamData({ name: '', description: '' })
    setError('')
    loadAllTeamsAndUsers()
  }

  const handleAssignTeam = async () => {
    try {
      setSubmitting(true)
      setError('')

      if (isCreatingNew) {
        // Create a new team for this project
        if (!newTeamData.name.trim()) {
          setError('Team name is required')
          return
        }
        
        await api.createTeam({
          name: newTeamData.name.trim(),
          description: newTeamData.description.trim() || null,
          project_id: projectId
        })
      } else {
        // Assign existing team to this project
        if (!selectedTeamId) {
          setError('Please select a team')
          return
        }
        
        // Update the selected team's project_id to this project
        await api.updateTeam(selectedTeamId, {
          project_id: projectId
        })
      }

      setShowAssignModal(false)
      loadProjectTeam() // Refresh
    } catch (error: any) {
      console.error('Failed to assign team:', error)
      setError(error.response?.data?.detail || 'Failed to assign team. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleAddMember = async () => {
    if (!team || !newMemberData.user_id) return
    
    try {
      setSubmitting(true)
      await api.addTeamMember(team.id, newMemberData.user_id, newMemberData.role)
      setShowAddMemberModal(false)
      setNewMemberData({ user_id: '', role: 'Developer' })
      loadProjectTeam() // Refresh to show new member
    } catch (error: any) {
      console.error('Failed to add team member:', error)
      alert(error.response?.data?.detail || 'Failed to add team member')
    } finally {
      setSubmitting(false)
    }
  }

  const handleRemoveMember = async (userId: string) => {
    if (!team) return
    
    if (!confirm('Are you sure you want to remove this member from the team?')) return
    
    try {
      await api.removeTeamMember(team.id, userId)
      loadProjectTeam() // Refresh
    } catch (error: any) {
      console.error('Failed to remove team member:', error)
      alert(error.response?.data?.detail || 'Failed to remove team member')
    }
  }

  // Filter teams that could be assigned (teams from other projects or without projects)
  const availableTeams = allTeams.filter(t => t.project_id !== projectId)

  const getRoleIcon = (role: string) => {
    switch (role.toLowerCase()) {
      case 'owner':
      case 'admin':
        return '🛡️'
      case 'developer':
        return '💻'
      case 'architect':
        return '🏗️'
      case 'designer':
        return '🎨'
      default:
        return '👤'
    }
  }

  const getRoleColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'owner':
      case 'admin':
        return 'bg-red-100 text-red-800'
      case 'developer':
        return 'bg-green-100 text-green-800'
      case 'architect':
        return 'bg-purple-100 text-purple-800'
      case 'designer':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const handleOpenAddMemberModal = () => {
    setShowAddMemberModal(true)
    setNewMemberData({ user_id: '', role: 'Developer' })
    loadAllTeamsAndUsers()
  }

  // Render the assign/change team modal
  const renderAssignModal = () => {
    if (!showAssignModal) return null

    return (
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]"
        onClick={() => setShowAssignModal(false)}
      >
        <div 
          className="rounded-lg p-6 w-full max-w-md max-h-[80vh] overflow-y-auto"
          style={{ 
            backgroundColor: 'var(--surface-color)',
            border: '1px solid var(--border-color)'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
            {team ? 'Change Team' : 'Assign Team'}
          </h3>

          {loadingTeams ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {/* Toggle between create new and select existing */}
              <div className="flex mb-4 border rounded-md overflow-hidden" style={{ borderColor: 'var(--border-color)' }}>
                <button
                  type="button"
                  onClick={() => setIsCreatingNew(true)}
                  className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                    isCreatingNew 
                      ? 'bg-blue-600 text-white' 
                      : 'hover:bg-gray-100'
                  }`}
                  style={!isCreatingNew ? { color: 'var(--text-color)' } : {}}
                >
                  Create New Team
                </button>
                <button
                  type="button"
                  onClick={() => setIsCreatingNew(false)}
                  className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                    !isCreatingNew 
                      ? 'bg-blue-600 text-white' 
                      : 'hover:bg-gray-100'
                  }`}
                  style={isCreatingNew ? { color: 'var(--text-color)' } : {}}
                >
                  Select Existing
                </button>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-md text-sm">
                  {error}
                </div>
              )}

              {isCreatingNew ? (
                // Create new team form
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Team Name *
                    </label>
                    <input
                      type="text"
                      value={newTeamData.name}
                      onChange={(e) => setNewTeamData({ ...newTeamData, name: e.target.value })}
                      placeholder="e.g., Development Team"
                      className="w-full px-3 py-2 border rounded-md"
                      style={{ 
                        backgroundColor: 'var(--background-color)',
                        borderColor: 'var(--border-color)',
                        color: 'var(--text-color)'
                      }}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Description
                    </label>
                    <textarea
                      value={newTeamData.description}
                      onChange={(e) => setNewTeamData({ ...newTeamData, description: e.target.value })}
                      placeholder="Brief description of the team..."
                      rows={3}
                      className="w-full px-3 py-2 border rounded-md"
                      style={{ 
                        backgroundColor: 'var(--background-color)',
                        borderColor: 'var(--border-color)',
                        color: 'var(--text-color)'
                      }}
                    />
                  </div>
                </div>
              ) : (
                // Select existing team
                <div className="space-y-4">
                  {availableTeams.length === 0 ? (
                    <div className="text-center py-4">
                      <p style={{ color: 'var(--text-secondary)' }}>
                        No available teams to assign. Create a new team instead.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {availableTeams.map((t) => (
                        <div
                          key={t.id}
                          onClick={() => setSelectedTeamId(t.id)}
                          className={`p-3 rounded-md border cursor-pointer transition-colors ${
                            selectedTeamId === t.id
                              ? 'border-blue-500 bg-blue-50'
                              : 'hover:bg-gray-50'
                          }`}
                          style={{ 
                            borderColor: selectedTeamId === t.id ? undefined : 'var(--border-color)'
                          }}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium" style={{ color: 'var(--text-color)' }}>
                                {t.name}
                              </p>
                              {t.description && (
                                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                  {t.description}
                                </p>
                              )}
                            </div>
                            <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                              👥 {t.member_count}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={() => setShowAssignModal(false)}
              className="px-4 py-2 rounded-md border transition-colors hover:bg-gray-50"
              style={{ 
                borderColor: 'var(--border-color)',
                color: 'var(--text-color)'
              }}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              onClick={handleAssignTeam}
              disabled={submitting || loadingTeams || (!isCreatingNew && availableTeams.length === 0)}
              className="px-4 py-2 rounded-md font-medium transition-colors disabled:opacity-50"
              style={{ 
                backgroundColor: 'var(--primary-color)',
                color: 'white'
              }}
            >
              {submitting ? 'Assigning...' : (team ? 'Change Team' : 'Assign Team')}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Render the add member modal
  const renderAddMemberModal = () => {
    if (!showAddMemberModal || !team) return null

    // Filter out users who are already team members
    const availableUsers = allUsers.filter(
      u => !teamMembers.some(m => m.user_id === u.id)
    )

    return (
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]"
        onClick={() => setShowAddMemberModal(false)}
      >
        <div 
          className="rounded-lg p-6 w-full max-w-md"
          style={{ 
            backgroundColor: 'var(--surface-color)',
            border: '1px solid var(--border-color)'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
            Add Team Member
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>
                Select User *
              </label>
              <select
                value={newMemberData.user_id}
                onChange={(e) => setNewMemberData({ ...newMemberData, user_id: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-color)'
                }}
              >
                <option value="">Select a user...</option>
                {availableUsers.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.full_name} ({user.email})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>
                Role
              </label>
              <select
                value={newMemberData.role}
                onChange={(e) => setNewMemberData({ ...newMemberData, role: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-color)'
                }}
              >
                <option value="Developer">Developer</option>
                <option value="Tester">Tester</option>
                <option value="Architect">Architect</option>
                <option value="Designer">Designer</option>
                <option value="Lead">Lead</option>
                <option value="Manager">Manager</option>
                <option value="Owner">Owner</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={() => setShowAddMemberModal(false)}
              className="px-4 py-2 rounded-md border transition-colors hover:bg-gray-50"
              style={{ 
                borderColor: 'var(--border-color)',
                color: 'var(--text-color)'
              }}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              onClick={handleAddMember}
              disabled={submitting || !newMemberData.user_id}
              className="px-4 py-2 rounded-md font-medium transition-colors disabled:opacity-50"
              style={{ 
                backgroundColor: 'var(--success-color, #10b981)',
                color: 'white'
              }}
            >
              {submitting ? 'Adding...' : 'Add Member'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Loading state
  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>Loading team...</p>
      </div>
    )
  }

  // No team state
  if (!team) {
    return (
      <>
        <div className="text-center py-8">
          <div className="text-6xl mb-4">👥</div>
          <p style={{ color: 'var(--text-secondary)' }}>No team assigned to this project</p>
          <button
            onClick={handleOpenAssignModal}
            className="mt-4 px-4 py-2 rounded-md font-medium transition-colors"
            style={{ 
              backgroundColor: 'var(--primary-color)',
              color: 'white'
            }}
          >
            + Assign Team
          </button>
        </div>
        {renderAssignModal()}
      </>
    )
  }

  return (
    <div className="space-y-4">
      {/* Team Header */}
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-medium" style={{ color: 'var(--text-color)' }}>
            {team.name}
          </h4>
          {team.description && (
            <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
              {team.description}
            </p>
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center text-sm" style={{ color: 'var(--text-secondary)' }}>
            <span className="mr-1">👥</span>
            {team.member_count} members
          </div>
          <button
            onClick={handleOpenAssignModal}
            className="px-3 py-1.5 text-sm rounded-md border transition-colors hover:bg-gray-50"
            style={{ 
              borderColor: 'var(--border-color)',
              color: 'var(--text-color)'
            }}
          >
            Change Team
          </button>
        </div>
      </div>

      {/* Team Members */}
      {teamMembers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {teamMembers.map((member) => (
            <div
              key={member.id}
              className="flex items-center space-x-3 p-3 rounded-lg border group"
              style={{ 
                backgroundColor: 'var(--surface-color)',
                borderColor: 'var(--border-color)'
              }}
            >
              <div 
                className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{ backgroundColor: 'var(--background-color)' }}
              >
                <span className="text-sm font-medium" style={{ color: 'var(--text-color)' }}>
                  {getInitials(member.user_name)}
                </span>
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <p className="font-medium truncate" style={{ color: 'var(--text-color)' }}>
                    {member.user_name}
                  </p>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRoleColor(member.role)}`}>
                    <span className="flex items-center">
                      <span className="mr-1">{getRoleIcon(member.role)}</span>
                      <span>{member.role}</span>
                    </span>
                  </span>
                </div>
                <p className="text-sm truncate" style={{ color: 'var(--text-secondary)' }}>
                  {member.user_email}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  Joined: {new Date(member.joined_at).toLocaleDateString()}
                </p>
              </div>

              {/* Remove button - shows on hover */}
              <button
                onClick={() => handleRemoveMember(member.user_id)}
                className="opacity-0 group-hover:opacity-100 px-2 py-1 text-xs rounded bg-red-100 text-red-600 hover:bg-red-200 transition-all"
                title="Remove from team"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-4">
          <p style={{ color: 'var(--text-secondary)' }}>No team members found</p>
        </div>
      )}

      {/* Add Member Button */}
      <div className="pt-2">
        <button
          onClick={handleOpenAddMemberModal}
          className="w-full px-4 py-2 rounded-md border-2 border-dashed transition-colors hover:bg-gray-50"
          style={{ 
            borderColor: 'var(--border-color)',
            color: 'var(--text-secondary)'
          }}
        >
          + Add Team Member
        </button>
      </div>

      {/* Modals */}
      {renderAssignModal()}
      {renderAddMemberModal()}
    </div>
  )
}

export default ProjectTeamDisplay