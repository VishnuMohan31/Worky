import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'
import OwnershipDisplay from '../components/ownership/OwnershipDisplay'

export default function ProjectDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { t } = useLanguage()
  const [project, setProject] = useState<any>(null)
  const [tasks, setTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProjectData()
  }, [id])

  const loadProjectData = async () => {
    try {
      const [projectData, tasksData] = await Promise.all([
        api.getProject(id!),
        api.getTasks(id)
      ])
      setProject(projectData)
      setTasks(tasksData)
    } catch (error) {
      console.error('Failed to load project:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div style={{ color: 'var(--text-color)' }}>{t('loading')}</div>
  }

  if (!project) {
    return <div style={{ color: 'var(--text-color)' }}>Project not found</div>
  }

  return (
    <div>
      <button onClick={() => navigate('/projects')}
              className="mb-4 text-sm"
              style={{ color: 'var(--primary-color)' }}>
        ← Back to Projects
      </button>

      {/* Owner Management - AT TOP */}
      <div className="rounded-lg p-6 shadow-md mb-6"
           style={{ 
             backgroundColor: 'var(--surface-color)',
             border: '1px solid var(--border-color)',
             borderLeft: '4px solid var(--primary-color)'
           }}>
        <OwnershipDisplay
          entityType="project"
          entityId={project.id}
          onOwnershipChange={() => {
            // Refresh project data if needed
            console.log('Project ownership updated')
          }}
        />
      </div>

      <div className="rounded-lg p-6 shadow-md mb-6"
           style={{ 
             backgroundColor: 'var(--surface-color)',
             border: '1px solid var(--border-color)'
           }}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--text-color)' }}>
              {project.name}
            </h1>
            <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
              {project.description}
            </p>
          </div>
          <span className="px-4 py-2 rounded"
                style={{
                  backgroundColor: getStatusColor(project.status),
                  color: 'white'
                }}>
            {project.status}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 mt-6">
          <div>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Start Date</p>
            <p className="font-medium" style={{ color: 'var(--text-color)' }}>{project.startDate}</p>
          </div>
          <div>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>End Date</p>
            <p className="font-medium" style={{ color: 'var(--text-color)' }}>{project.endDate}</p>
          </div>
        </div>

        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Progress</span>
            <span className="font-medium" style={{ color: 'var(--text-color)' }}>{project.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div className="h-3 rounded-full transition-all"
                 style={{ 
                   width: `${project.progress}%`,
                   backgroundColor: 'var(--primary-color)'
                 }} />
          </div>
        </div>
      </div>

      <div className="rounded-lg p-6 shadow-md"
           style={{ 
             backgroundColor: 'var(--surface-color)',
             border: '1px solid var(--border-color)'
           }}>
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
          Project Tasks ({tasks.length})
        </h2>
        <div className="space-y-3">
          {tasks.map(task => (
            <div key={task.id}
                 className="flex items-center justify-between p-4 rounded"
                 style={{ backgroundColor: 'var(--background-color)' }}>
              <div className="flex-1">
                <h3 className="font-medium mb-1" style={{ color: 'var(--text-color)' }}>
                  {task.title}
                </h3>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  Assigned to: {task.assignedToName} • Due: {task.dueDate}
                </p>
              </div>
              <span className="px-3 py-1 rounded text-sm ml-4"
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
