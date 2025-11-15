import { useEffect, useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'

export default function SprintPage() {
  const { t } = useLanguage()
  const [tasks, setTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTasks()
  }, [])

  const loadTasks = async () => {
    try {
      const data = await api.getTasks()
      setTasks(data)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const sprintData = {
    name: 'Sprint 1',
    startDate: '2025-01-01',
    endDate: '2025-01-14',
    totalTasks: tasks.length,
    completedTasks: tasks.filter(t => t.status === 'Done').length,
    inProgressTasks: tasks.filter(t => t.status === 'In Progress').length,
    todoTasks: tasks.filter(t => t.status === 'To Do').length
  }

  const completionRate = sprintData.totalTasks > 0 
    ? Math.round((sprintData.completedTasks / sprintData.totalTasks) * 100)
    : 0

  if (loading) {
    return <div style={{ color: 'var(--text-color)' }}>{t('loading')}</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text-color)' }}>
        {t('sprint')} 🏃
      </h1>

      {/* Sprint Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="rounded-lg p-6 shadow-md"
             style={{ 
               backgroundColor: 'var(--surface-color)',
               border: '1px solid var(--border-color)'
             }}>
          <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
            {sprintData.name}
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span style={{ color: 'var(--text-secondary)' }}>Duration:</span>
              <span style={{ color: 'var(--text-color)' }}>
                {sprintData.startDate} - {sprintData.endDate}
              </span>
            </div>
            <div className="flex justify-between">
              <span style={{ color: 'var(--text-secondary)' }}>Total Tasks:</span>
              <span style={{ color: 'var(--text-color)' }}>{sprintData.totalTasks}</span>
            </div>
            <div className="flex justify-between">
              <span style={{ color: 'var(--text-secondary)' }}>Completed:</span>
              <span style={{ color: 'var(--success-color)' }}>{sprintData.completedTasks}</span>
            </div>
            <div className="flex justify-between">
              <span style={{ color: 'var(--text-secondary)' }}>In Progress:</span>
              <span style={{ color: 'var(--info-color)' }}>{sprintData.inProgressTasks}</span>
            </div>
            <div className="flex justify-between">
              <span style={{ color: 'var(--text-secondary)' }}>To Do:</span>
              <span style={{ color: 'var(--text-secondary)' }}>{sprintData.todoTasks}</span>
            </div>
          </div>
        </div>

        {/* Burndown Chart Placeholder */}
        <div className="rounded-lg p-6 shadow-md"
             style={{ 
               backgroundColor: 'var(--surface-color)',
               border: '1px solid var(--border-color)'
             }}>
          <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
            Sprint Progress
          </h2>
          <div className="flex items-center justify-center h-40">
            <div className="text-center">
              <div className="text-6xl font-bold mb-2" style={{ color: 'var(--primary-color)' }}>
                {completionRate}%
              </div>
              <p style={{ color: 'var(--text-secondary)' }}>Complete</p>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 mt-4">
            <div className="h-4 rounded-full transition-all"
                 style={{ 
                   width: `${completionRate}%`,
                   backgroundColor: 'var(--success-color)'
                 }} />
          </div>
        </div>
      </div>

      {/* Sprint Tasks */}
      <div className="rounded-lg p-6 shadow-md"
           style={{ 
             backgroundColor: 'var(--surface-color)',
             border: '1px solid var(--border-color)'
           }}>
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
          Sprint Tasks
        </h2>
        <div className="space-y-3">
          {tasks.map(task => (
            <div key={task.id}
                 className="flex items-center justify-between p-3 rounded"
                 style={{ backgroundColor: 'var(--background-color)' }}>
              <div className="flex-1">
                <h3 className="font-medium" style={{ color: 'var(--text-color)' }}>
                  {task.title}
                </h3>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  {task.assignedToName} • {task.dueDate}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  {task.progress}%
                </span>
                <span className="px-3 py-1 rounded text-sm"
                      style={{
                        backgroundColor: getStatusColor(task.status),
                        color: 'white'
                      }}>
                  {task.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 p-4 rounded"
           style={{ 
             backgroundColor: 'var(--surface-color)',
             border: '1px solid var(--border-color)'
           }}>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          💡 <strong>Note:</strong> This is a simplified sprint board. In production, this would include a burndown chart using D3.js or Chart.js, sprint velocity tracking, and daily standup notes.
        </p>
      </div>
    </div>
  )
}

function getStatusColor(status: string) {
  switch (status) {
    case 'Done': return 'var(--success-color)'
    case 'In Progress': return 'var(--info-color)'
    case 'To Do': return 'var(--text-secondary)'
    default: return 'var(--text-secondary)'
  }
}
