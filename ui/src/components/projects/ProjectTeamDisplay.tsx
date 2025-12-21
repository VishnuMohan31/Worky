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

  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>Loading team...</p>
      </div>
    )
  }

  if (!team) {
    return (
      <div className="text-center py-8">
        <div className="text-6xl mb-4">👥</div>
        <p style={{ color: 'var(--text-secondary)' }}>No team assigned to this project</p>
        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
          Contact an administrator to set up a project team
        </p>
      </div>
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
        <div className="flex items-center text-sm" style={{ color: 'var(--text-secondary)' }}>
          <span className="mr-1">👥</span>
          {team.member_count} members
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
    </div>
  )
}

export default ProjectTeamDisplay