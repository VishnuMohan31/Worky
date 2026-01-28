import React, { useState, useEffect } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'

interface Team {
  id: string
  name: string
  description?: string
  project_id: string
  is_active: boolean
  created_at: string
  updated_at: string
  member_count: number
}

interface Project {
  id: string
  name: string
}

interface User {
  id: string
  full_name: string
  email: string
  role: string
}

interface TeamMember {
  id: string
  team_id: string
  user_id: string
  role: string
  joined_at: string
  is_active: boolean
  user_name?: string
  user_email?: string
}

export default function TeamsPage() {
  const { } = useLanguage()
  const [teams, setTeams] = useState<Team[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null)
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showAddMemberModal, setShowAddMemberModal] = useState(false)

  // Form states
  const [newTeam, setNewTeam] = useState({
    name: '',
    description: '',
    project_id: ''
  })
  const [newMember, setNewMember] = useState({
    user_id: '',
    role: 'Developer'
  })

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    setLoading(true)
    try {
      const [teamsData, projectsData, usersData] = await Promise.all([
        api.getTeams(),
        api.getProjects(),
        api.getUsers()
      ])
      
      console.log('loadInitialData - teamsData:', teamsData)
      console.log('loadInitialData - projectsData:', projectsData)
      console.log('loadInitialData - usersData:', usersData)
      
      // Handle teams response
      let teamsList = []
      if (teamsData && teamsData.items && Array.isArray(teamsData.items)) {
        teamsList = teamsData.items
      } else if (Array.isArray(teamsData)) {
        teamsList = teamsData
      }
      
      setTeams(teamsList)
      setProjects(Array.isArray(projectsData) ? projectsData.filter(p => p !== null) : [])
      setUsers(Array.isArray(usersData) ? usersData : [])
      
      console.log('loadInitialData - final state:', {
        teams: teamsList.length,
        projects: Array.isArray(projectsData) ? projectsData.length : 0,
        users: Array.isArray(usersData) ? usersData.length : 0
      })
    } catch (error) {
      console.error('Failed to load initial data:', error)
      setTeams([])
      setProjects([])
      setUsers([])
    } finally {
      setLoading(false)
    }
  }

  const loadTeamMembers = async (teamId: string) => {
    try {
      console.log(`Loading team members for team: ${teamId}`)
      // Add cache busting parameter to ensure fresh data
      const timestamp = Date.now()
      const members = await api.getTeamMembers(teamId, { _t: timestamp })
      console.log(`API returned ${members.length} members for team ${teamId}:`, members)
      setTeamMembers(Array.isArray(members) ? members : [])
      console.log(`Set teamMembers state with ${Array.isArray(members) ? members.length : 0} members`)
    } catch (error) {
      console.error('Failed to load team members:', error)
      setTeamMembers([])
    }
  }

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate required fields
    if (!newTeam.name.trim()) {
      alert('Please enter a team name')
      return
    }
    if (!newTeam.project_id) {
      alert('Please select a project')
      return
    }
    
    try {
      console.log('Creating team with data:', newTeam)
      const createdTeam = await api.createTeam(newTeam)
      console.log('Team created successfully:', createdTeam)
      setShowCreateModal(false)
      setNewTeam({ name: '', description: '', project_id: '' })
      await loadInitialData()
      alert('Team created successfully!')
    } catch (error: any) {
      console.error('Failed to create team:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create team. Please try again.'
      alert(`Error: ${errorMessage}`)
    }
  }

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedTeam) return
    
    // Validate that a user is selected
    if (!newMember.user_id) {
      alert('Please select a user to add to the team')
      return
    }
    
    console.log('Adding team member:', {
      teamId: selectedTeam.id,
      userId: newMember.user_id,
      role: newMember.role
    })
    
    try {
      const result = await api.addTeamMember(selectedTeam.id, newMember.user_id, newMember.role)
      console.log('API addTeamMember result:', result)
      
      // Close modal and reset form immediately on success
      setShowAddMemberModal(false)
      setNewMember({ user_id: '', role: 'Developer' })
      
      // Refresh both team list and team members from server to ensure consistency
      await Promise.all([
        loadInitialData(), // Refresh teams list with accurate counts
        loadTeamMembers(selectedTeam.id) // Refresh team members list
      ])
      
      alert('Team member added successfully!')
    } catch (error: any) {
      console.error('Failed to add team member:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error'
      
      // Reset form and reload team members on error to get fresh state
      setNewMember({ user_id: '', role: 'Developer' })
      await loadTeamMembers(selectedTeam.id)
      
      alert(`Failed to add team member: ${errorMessage}`)
    }
  }

  const handleRemoveMember = async (userId: string) => {
    if (!selectedTeam) return
    
    // Find member name for confirmation message
    const member = teamMembers.find(m => m.user_id === userId)
    const memberName = member?.user_name || 'this team member'
    
    if (!confirm(`Are you sure you want to remove ${memberName} from ${selectedTeam.name}?`)) {
      return
    }
    
    try {
      await api.removeTeamMember(selectedTeam.id, userId)
      
      // Refresh both team list and team members from server to ensure consistency
      await Promise.all([
        loadInitialData(), // Refresh teams list with accurate counts
        loadTeamMembers(selectedTeam.id) // Refresh team members list
      ])
      
      alert('Team member removed successfully!')
    } catch (error: any) {
      console.error('Failed to remove team member:', error)
      alert(`Failed to remove team member: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleTeamSelect = (team: Team) => {
    setSelectedTeam(team)
    setTeamMembers([]) // Clear previous members
    loadTeamMembers(team.id)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-2">
            <span>👥</span>
            <span>Team Management</span>
          </h1>
          <p className="text-gray-600 mt-1">Manage project teams and team members</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-2 font-medium"
        >
          <span>+</span>
          <span>Create Team</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Teams List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Teams</h2>
          </div>
          <div className="p-4">
            {teams.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-4xl mb-4">🏢</div>
                <p className="text-gray-500 mb-4">No teams found</p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                >
                  Create First Team
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {teams.map((team) => (
                  <div
                    key={team.id}
                    onClick={() => handleTeamSelect(team)}
                    className={`p-3 rounded-md border cursor-pointer transition-colors ${
                      selectedTeam?.id === team.id
                        ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-200'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-medium text-gray-900">{team.name}</h3>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            team.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {team.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">{team.description}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Project: {projects.find(p => p.id === team.project_id)?.name || 'Unknown'}
                        </p>
                      </div>
                      <div className="text-right ml-4">
                        <div className="flex items-center space-x-1 text-sm font-medium text-gray-600">
                          <span>👥</span>
                          <span>{team.member_count}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Team Members */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              {selectedTeam ? `${selectedTeam.name} Members` : 'Select a Team'}
            </h2>
            {selectedTeam && (
              <button
                onClick={() => {
                  // Reset form when opening modal
                  setNewMember({ user_id: '', role: 'Developer' })
                  setShowAddMemberModal(true)
                }}
                className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors flex items-center space-x-2"
              >
                <span>+</span>
                <span>Add Member</span>
              </button>
            )}
          </div>
          <div className="p-4">
            {!selectedTeam ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-4xl mb-4">👥</div>
                <p className="text-gray-500">Select a team to view members</p>
              </div>
            ) : teamMembers.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-4xl mb-4">👤</div>
                <p className="text-gray-500 mb-4">No members in this team</p>
                <button
                  onClick={() => {
                    // Reset form when opening modal
                    setNewMember({ user_id: '', role: 'Developer' })
                    setShowAddMemberModal(true)
                  }}
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                >
                  Add First Member
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {teamMembers.map((member, index) => {
                  console.log(`Rendering member ${index}:`, member);
                  
                  // Ensure we have required data
                  if (!member.id || !member.user_id) {
                    console.warn('Skipping member with missing data:', member);
                    return null;
                  }
                  
                  return (
                    <div
                      key={`${member.id}-${member.user_id}-${index}`} // Unique key with fallback
                      className="flex items-center justify-between p-3 border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-sm">
                            {(member.user_name || 'Unknown')?.charAt(0)?.toUpperCase() || '?'}
                          </span>
                        </div>
                        <div className="flex-1">
                          <span className="font-medium text-gray-900">{member.user_name || 'Unknown User'}</span>
                          <span className="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {member.role || 'Member'}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveMember(member.user_id)}
                        className="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 transition-colors"
                      >
                        Remove
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Team Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Team</h3>
            <form onSubmit={handleCreateTeam}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Team Name
                  </label>
                  <input
                    type="text"
                    value={newTeam.name}
                    onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={newTeam.description}
                    onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project
                  </label>
                  <select
                    value={newTeam.project_id}
                    onChange={(e) => setNewTeam({ ...newTeam, project_id: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select Project...</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Create Team
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Member Modal */}
      {showAddMemberModal && selectedTeam && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Team Member</h3>
            <form onSubmit={handleAddMember}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    User
                  </label>
                  <select
                    key={`user-select-${teamMembers.length}`} // Force re-render when team members change
                    value={newMember.user_id}
                    onChange={(e) => setNewMember({ ...newMember, user_id: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select User...</option>
                    {(() => {
                      const availableUsers = users.filter(user => !teamMembers.some(member => member.user_id === user.id))
                      console.log('Available users for team member addition:', {
                        totalUsers: users.length,
                        teamMembers: teamMembers.length,
                        availableUsers: availableUsers.length,
                        teamMemberIds: teamMembers.map(m => m.user_id),
                        availableUserIds: availableUsers.map(u => u.id)
                      })
                      return availableUsers.map((user) => (
                        <option key={user.id} value={user.id}>
                          {user.full_name} ({user.email})
                        </option>
                      ))
                    })()}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role
                  </label>
                  <select
                    value={newMember.role}
                    onChange={(e) => setNewMember({ ...newMember, role: e.target.value })}
                    className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Developer">Developer</option>
                    <option value="Tester">Tester</option>
                    <option value="Architect">Architect</option>
                    <option value="Designer">Designer</option>
                    <option value="Contact Person">Contact Person</option>
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
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                >
                  Add Member
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}