import { useEffect, useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'

export default function DashboardPage() {
  const { t } = useLanguage()
  const [stats, setStats] = useState({
    totalProjects: 0,
    activeTasks: 0,
    openBugs: 0,
    teamMembers: 0
  })
  const [recentTasks, setRecentTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      console.log('Loading dashboard data...')
      
      // Load data with individual error handling using safe methods
      const [projects, tasks, bugs, users] = await Promise.all([
        api.getProjectsSafe().then(data => { console.log('Projects:', data); return data }).catch(err => { console.error('Projects error:', err); return [] }),
        api.getTasksSafe().then(data => { console.log('Tasks:', data); return data }).catch(err => { console.error('Tasks error:', err); return [] }),
        api.getBugs().then(data => { console.log('Bugs:', data); return data }).catch(err => { console.error('Bugs error:', err); return [] }),
        api.getUsersSafe().then(data => { console.log('Users:', data); return data }).catch(err => { console.error('Users error:', err); return [] })
      ])

      console.log('All data loaded successfully')

      setStats({
        totalProjects: Array.isArray(projects) ? projects.length : 0,
        activeTasks: Array.isArray(tasks) ? tasks.filter((t: any) => 
          t.status !== 'Completed' && 
          t.status !== 'Canceled'
        ).length : 0,
        openBugs: Array.isArray(bugs) ? bugs.filter((b: any) => 
          b.status === 'Open' || 
          b.status === 'New' || 
          b.status === 'Planning'
        ).length : 0,
        teamMembers: Array.isArray(users) ? users.length : 0
      })

      setRecentTasks(Array.isArray(tasks) ? tasks.slice(0, 5) : [])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      // Set default values on error
      setStats({
        totalProjects: 0,
        activeTasks: 0,
        openBugs: 0,
        teamMembers: 0
      })
      setRecentTasks([])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div style={{ color: 'var(--text-color)' }}>{t('loading')}</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text-color)' }}>
        {t('dashboard')}
      </h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title={t('projects')}
          value={stats.totalProjects}
          icon="📁"
          color="var(--primary-color)"
        />
        <StatCard
          title={t('tasks')}
          value={stats.activeTasks}
          icon="✓"
          color="var(--info-color)"
        />
        <StatCard
          title={t('bugs')}
          value={stats.openBugs}
          icon="🐛"
          color="var(--error-color)"
        />
        <StatCard
          title={t('users')}
          value={stats.teamMembers}
          icon="👥"
          color="var(--success-color)"
        />
      </div>

      {/* Recent Tasks */}
      <div className="rounded-lg p-6 shadow-md"
           style={{ 
             backgroundColor: 'var(--surface-color)',
             border: '1px solid var(--border-color)'
           }}>
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
          Recent Tasks
        </h2>
        <div className="space-y-3">
          {recentTasks.map(task => (
            <div key={task.id} 
                 className="flex items-center justify-between p-3 rounded"
                 style={{ backgroundColor: 'var(--background-color)' }}>
              <div className="flex-1">
                <h3 className="font-medium" style={{ color: 'var(--text-color)' }}>
                  {task.title}
                </h3>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  Assigned to: {task.assignedToName}
                </p>
              </div>
              <span className="px-3 py-1 rounded text-sm"
                    style={{
                      backgroundColor: getStatusColor(task.status),
                      color: 'white'
                    }}>
                {task.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, color }: any) {
  return (
    <div className="rounded-lg p-6 shadow-md"
         style={{ 
           backgroundColor: 'var(--surface-color)',
           border: '1px solid var(--border-color)'
         }}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {title}
          </p>
          <p className="text-3xl font-bold mt-2" style={{ color: 'var(--text-color)' }}>
            {value}
          </p>
        </div>
        <div className="text-4xl" style={{ color }}>
          {icon}
        </div>
      </div>
    </div>
  )
}

function getStatusColor(status: string) {
  switch (status) {
    // Planning phase - Yellow/Orange (Warning)
    case 'Planning': 
      return 'var(--warning-color)'
    
    // Active work - Blue (Info)
    case 'In Progress': 
      return 'var(--info-color)'
    
    // Completed work - Green (Success)
    case 'Completed': 
      return 'var(--success-color)'
    
    // Paused work - Gray (Secondary)
    case 'On Hold': 
      return 'var(--text-secondary)'
    
    // Blocked work - Red (Error)
    case 'Blocked': 
      return 'var(--error-color)'
    
    // Legacy statuses (for backward compatibility)
    case 'Done': 
      return 'var(--success-color)'
    case 'To Do': 
      return 'var(--warning-color)'
    case 'In Review': 
      return 'var(--info-color)'
    case 'Cancelled': 
      return 'var(--error-color)'
    
    default: 
      return 'var(--text-secondary)'
  }
}
