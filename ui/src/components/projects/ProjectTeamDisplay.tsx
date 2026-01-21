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
  const [loadingTeams, setLoadingTeams] = useState(false)
  const [selectedTeamId, setSelectedTeamId] = useState<string>('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  

  useEffect(() => {
    loadProjectTeam()
  }, [projectId])

  const loadProjectTeam = async () => {
    try {
      setLoading(true)
      
      console.log('📥 Loading project team for project:', projectId)
      // Get teams for this project
      const teams = await api.getTeams(projectId)
      console.log('📋 Teams found for project:', teams)
      
      if (teams && teams.length > 0) {
        const projectTeam = teams[0] // Assuming one team per project
        console.log('✅ Project team loaded:', projectTeam)
        setTeam(projectTeam)
        
        // Load team members
        const members = await api.getTeamMembers(projectTeam.id)
        console.log('👥 Team members loaded:', members)
        setTeamMembers(members)
      } else {
        console.log('ℹ️ No team assigned to project')
        setTeam(null)
        setTeamMembers([])
      }
    } catch (error) {
      console.error('❌ Failed to load project team:', error)
      setTeam(null)
      setTeamMembers([])
    } finally {
      setLoading(false)
    }
  }

  const loadAllTeamsAndUsers = async () => {
    try {
      setLoadingTeams(true)
      const teamsData = await api.getTeams() // Get all teams
      setAllTeams(Array.isArray(teamsData) ? teamsData : [])
    } catch (error) {
      console.error('Failed to load teams:', error)
    } finally {
      setLoadingTeams(false)
    }
  }

  const handleOpenAssignModal = () => {
    setShowAssignModal(true)
    setSelectedTeamId('')
    setError('')
    loadAllTeamsAndUsers()
  }

  const handleAssignTeam = async () => {
    try {
      setSubmitting(true)
      setError('')

      if (!selectedTeamId) {
        setError('Please select a team')
        return
      }
      
      console.log('🔄 Changing project team:', {
        projectId,
        currentTeamId: team?.id,
        newTeamId: selectedTeamId
      })
      
      // If there's a current team assigned, unassign it first
      if (team && team.id) {
        try {
          console.log('📤 Unassigning current team:', team.id)
          await api.updateTeam(team.id, {
            project_id: '' // Empty string unassigns the team from the project
          })
          console.log('✅ Current team unassigned successfully')
        } catch (unassignError: any) {
          console.error('❌ Failed to unassign current team:', unassignError)
          // Continue anyway - might already be unassigned
        }
      }
      
      // Update the selected team's project_id to this project
      console.log('📤 Assigning new team:', selectedTeamId, 'to project:', projectId)
      const updatedTeam = await api.updateTeam(selectedTeamId, {
        project_id: projectId
      })
      console.log('✅ Team assigned successfully:', updatedTeam)

      setShowAssignModal(false)
      await loadProjectTeam() // Refresh
      console.log('✅ Project team refreshed')
    } catch (error: any) {
      console.error('❌ Failed to assign team:', error)
      setError(error.response?.data?.detail || 'Failed to assign team. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  // Filter teams that could be assigned (all teams except the currently assigned one)
  const availableTeams = allTeams.filter(t => t.id !== team?.id)

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
              {error && (
                <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-md text-sm">
                  {error}
                </div>
              )}

              {/* Select existing team */}
              <div className="space-y-4">
                {availableTeams.length === 0 ? (
                  <div className="text-center py-4">
                    <p style={{ color: 'var(--text-secondary)' }}>
                      No available teams to assign. Please create a team from the Teams page first.
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
              disabled={submitting || loadingTeams || availableTeams.length === 0 || !selectedTeamId}
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
              className="flex items-center space-x-3 p-3 rounded-lg border"
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
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-4">
          <p style={{ color: 'var(--text-secondary)' }}>No team members found</p>
        </div>
      )}

      {/* Modals */}
      {renderAssignModal()}
    </div>
  )
}

export default ProjectTeamDisplay