import { useEffect, useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'

export default function TasksPage() {
  const { t } = useLanguage()
  const [tasks, setTasks] = useState<any[]>([])
  const [filter, setFilter] = useState('all')
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

  const filteredTasks = filter === 'all' 
    ? tasks 
    : tasks.filter(t => t.status === filter)

  if (loading) {
    return <div style={{ color: 'var(--text-color)' }}>{t('loading')}</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-color)' }}>
          {t('tasks')}
        </h1>
        <button className="px-4 py-2 rounded-md"
                style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}>
          + {t('create')} Task
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6">
        {['all', 'To Do', 'In Progress', 'Done'].map(status => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className="px-4 py-2 rounded-md transition-colors"
            style={{
              backgroundColor: filter === status ? 'var(--primary-color)' : 'var(--secondary-color)',
              color: filter === status ? 'white' : 'var(--text-color)'
            }}
          >
            {status === 'all' ? 'All Tasks' : status}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      <div className="space-y-3">
        {filteredTasks.map(task => (
          <div key={task.id}
               className="rounded-lg p-4 shadow-md hover:shadow-lg transition-shadow"
               style={{ 
                 backgroundColor: 'var(--surface-color)',
                 border: '1px solid var(--border-color)'
               }}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
                    {task.title}
                  </h3>
                  <span className="px-2 py-1 text-xs rounded"
                        style={{
                          backgroundColor: getPriorityColor(task.priority),
                          color: 'white'
                        }}>
                    {task.priority}
                  </span>
                </div>
                <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>
                  {task.description}
                </p>
                <div className="flex items-center gap-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
                  <span>👤 {task.assignedToName}</span>
                  <span>📅 Due: {task.dueDate}</span>
                  <span>📊 {task.progress}%</span>
                </div>
              </div>
              <span className="px-3 py-1 rounded text-sm ml-4"
                    style={{
                      backgroundColor: getStatusColor(task.status),
                      color: 'white'
                    }}>
                {task.status}
              </span>
            </div>

            {/* Progress Bar */}
            <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
              <div className="h-2 rounded-full transition-all"
                   style={{ 
                     width: `${task.progress}%`,
                     backgroundColor: 'var(--primary-color)'
                   }} />
            </div>
          </div>
        ))}
      </div>

      {filteredTasks.length === 0 && (
        <div className="text-center py-12" style={{ color: 'var(--text-secondary)' }}>
          {t('noData')}
        </div>
      )}
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

function getPriorityColor(priority: string) {
  switch (priority) {
    case 'High': return 'var(--error-color)'
    case 'Medium': return 'var(--warning-color)'
    case 'Low': return 'var(--info-color)'
    default: return 'var(--text-secondary)'
  }
}
