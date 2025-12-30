import { useEffect, useState, useCallback } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'

interface Task {
  id: string
  title: string
  description: string
  status: string
  priority: string
  projectId: string
  assignedToName: string
  dueDate: string
  progress: number
  sprint_id?: string
}

interface Sprint {
  id: string
  name: string
  start_date: string
  end_date: string
  status: string
}

export default function KanbanPage() {
  const { t } = useLanguage()
  const [projects, setProjects] = useState<any[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [sprints, setSprints] = useState<Sprint[]>([])
  const [selectedSprintId, setSelectedSprintId] = useState<string>('')
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingSprints, setLoadingSprints] = useState(false)
  const [loadingTasks, setLoadingTasks] = useState(false)
  const [draggedTask, setDraggedTask] = useState<Task | null>(null)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadSprints()
    } else {
      setSprints([])
      setSelectedSprintId('')
      setTasks([])
    }
  }, [selectedProjectId])

  useEffect(() => {
    if (selectedSprintId) {
      loadTasks()
    } else {
      setTasks([])
    }
  }, [selectedSprintId])

  const loadProjects = async () => {
    try {
      const data = await api.getProjects()
      setProjects(data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSprints = async () => {
    if (!selectedProjectId) return
    setLoadingSprints(true)
    try {
      const data = await api.getProjectSprints(selectedProjectId, false)
      setSprints(data)
      if (data.length > 0 && !selectedSprintId) {
        setSelectedSprintId(data[0].id)
      }
    } catch (error) {
      console.error('Failed to load sprints:', error)
    } finally {
      setLoadingSprints(false)
    }
  }

  const loadTasks = useCallback(async () => {
    if (!selectedSprintId) return
    setLoadingTasks(true)
    try {
      const data = await api.getSprintTasks(selectedSprintId)
      // Transform tasks to match the expected format
      const transformedTasks = data.map((task: any) => ({
        id: task.id,
        title: task.title || task.name,
        description: task.description || '',
        status: task.status || 'To Do',
        priority: task.priority || 'Medium',
        projectId: task.project_id || task.projectId || '',
        assignedToName: task.assigned_to_name || task.assignedToName || 'Unassigned',
        dueDate: task.due_date ? new Date(task.due_date).toLocaleDateString() : '',
        progress: task.progress || 0,
        sprint_id: task.sprint_id || selectedSprintId
      }))
      setTasks(transformedTasks)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setLoadingTasks(false)
    }
  }, [selectedSprintId])

  const columns = ['To Do', 'In Progress', 'Done']

  const getTasksByStatus = (status: string) => {
    return tasks.filter(task => task.status === status)
  }

  const handleDragStart = (e: React.DragEvent, task: Task) => {
    console.log(`🚀 Starting drag for task "${task.title}" with status "${task.status}"`)
    setDraggedTask(task)
    e.dataTransfer.effectAllowed = 'move'
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    // Only log occasionally to avoid spam
    if (Math.random() < 0.01) {
      console.log(`🎯 Dragging over column`)
    }
  }

  const handleDrop = async (e: React.DragEvent, newStatus: string) => {
    e.preventDefault()
    
    console.log(`🔄 Attempting to drop task "${draggedTask?.title}" from "${draggedTask?.status}" to "${newStatus}"`)
    
    if (!draggedTask) {
      console.log('❌ No dragged task found')
      setDraggedTask(null)
      return
    }
    
    if (draggedTask.status === newStatus) {
      console.log('❌ Task already has this status, ignoring drop')
      setDraggedTask(null)
      return
    }

    try {
      console.log(`📡 Calling API to update task ${draggedTask.id} status to ${newStatus}`)
      // Update task status via API
      await api.updateTask(draggedTask.id, { status: newStatus })
      
      console.log(`✅ API call successful, updating local state`)
      // Update local state
      setTasks(tasks.map(task => 
        task.id === draggedTask.id 
          ? { ...task, status: newStatus }
          : task
      ))
      
      console.log(`✅ Task "${draggedTask.title}" successfully moved from "${draggedTask.status}" to "${newStatus}"`)
    } catch (error) {
      console.error('❌ Failed to update task status:', error)
      console.error('Error details:', error)
      alert(`Failed to update task status: ${error.message || error}`)
    } finally {
      setDraggedTask(null)
    }
  }

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task)
  }

  const closeDetails = () => {
    setSelectedTask(null)
  }

  const formatSprintDisplay = (sprint: Sprint) => {
    const startDate = new Date(sprint.start_date).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    }).toUpperCase()
    const endDate = new Date(sprint.end_date).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    }).toUpperCase()
    return `${sprint.id} (${startDate} to ${endDate})`
  }

  if (loading) {
    return <div style={{ color: 'var(--text-color)' }}>{t('loading')}</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text-color)' }}>
        {t('kanban')} 📋
      </h1>

      {/* Project and Sprint Selection */}
      <div className="mb-6 flex gap-4 items-end">
        <div className="flex-1">
          <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
            Select Project:
          </label>
          <select
            value={selectedProjectId}
            onChange={(e) => {
              setSelectedProjectId(e.target.value)
              setSelectedSprintId('')
              setTasks([])
            }}
            className="w-full p-2 rounded border"
            style={{
              backgroundColor: 'var(--background-color)',
              color: 'var(--text-color)',
              borderColor: 'var(--border-color)'
            }}
          >
            <option value="">Select a project...</option>
            {projects.map(project => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1">
          <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
            Select Sprint:
          </label>
          <select
            value={selectedSprintId}
            onChange={(e) => setSelectedSprintId(e.target.value)}
            disabled={!selectedProjectId || loadingSprints}
            className="w-full p-2 rounded border"
            style={{
              backgroundColor: 'var(--background-color)',
              color: 'var(--text-color)',
              borderColor: 'var(--border-color)',
              opacity: !selectedProjectId || loadingSprints ? 0.6 : 1
            }}
          >
            <option value="">Select a sprint...</option>
            {sprints.map(sprint => (
              <option key={sprint.id} value={sprint.id}>
                {formatSprintDisplay(sprint)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loadingTasks && (
        <div className="mb-4 text-center" style={{ color: 'var(--text-color)' }}>
          Loading tasks...
        </div>
      )}

      {!selectedSprintId && (
        <div className="mb-4 p-4 rounded text-center" style={{ 
          backgroundColor: 'var(--surface-color)',
          border: '1px solid var(--border-color)',
          color: 'var(--text-secondary)'
        }}>
          Please select a project and sprint to view tasks
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {columns.map(column => (
          <div 
            key={column}
            className="rounded-lg p-4"
            style={{ 
              backgroundColor: 'var(--surface-color)',
              border: '2px solid var(--border-color)',
              minHeight: '500px' // Ensure adequate drop zone
            }}
            onDragOver={handleDragOver}
            onDrop={(e) => {
              console.log(`📥 Drop event triggered on column: ${column}`)
              handleDrop(e, column)
            }}
            onDragEnter={(e) => {
              e.preventDefault()
              console.log(`🎯 Drag entered column: ${column}`)
            }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
                {column}
              </h2>
              <span className="px-2 py-1 text-xs rounded"
                    style={{ 
                      backgroundColor: 'var(--secondary-color)',
                      color: 'var(--text-color)'
                    }}>
                {getTasksByStatus(column).length}
              </span>
            </div>

            <div className="space-y-3 min-h-[400px]">
              {getTasksByStatus(column).map(task => (
                <div 
                  key={task.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, task)}
                  className="p-3 rounded shadow-sm hover:shadow-md transition-shadow cursor-move"
                  style={{ 
                    backgroundColor: 'var(--background-color)',
                    border: '1px solid var(--border-color)',
                    opacity: draggedTask?.id === task.id ? 0.5 : 1
                  }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium flex-1" style={{ color: 'var(--text-color)' }}>
                      {task.title}
                    </h3>
                    <button
                      onClick={() => handleTaskClick(task)}
                      className="ml-2 px-2 py-1 text-xs rounded hover:opacity-80"
                      style={{ 
                        backgroundColor: 'var(--primary-color)',
                        color: 'white'
                      }}
                    >
                      Details
                    </button>
                  </div>
                  
                  <div className="text-xs mb-2" style={{ color: 'var(--text-secondary)' }}>
                    📁 Project ID: {task.projectId}
                  </div>
                  
                  <div className="flex items-center justify-between text-xs"
                       style={{ color: 'var(--text-secondary)' }}>
                    <span>👤 {task.assignedToName}</span>
                    <span className="px-2 py-1 rounded"
                          style={{
                            backgroundColor: getPriorityColor(task.priority),
                            color: 'white'
                          }}>
                      {task.priority}
                    </span>
                  </div>
                  
                  <div className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
                    📅 {task.dueDate}
                  </div>
                  
                  {/* Progress bar */}
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        className="h-1.5 rounded-full transition-all"
                        style={{ 
                          width: `${task.progress}%`,
                          backgroundColor: 'var(--primary-color)'
                        }} 
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Task Details Modal */}
      {selectedTask && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={closeDetails}
        >
          <div 
            className="rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            style={{ 
              backgroundColor: 'var(--surface-color)',
              border: '1px solid var(--border-color)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
                {selectedTask.title}
              </h2>
              <button
                onClick={closeDetails}
                className="text-2xl hover:opacity-70"
                style={{ color: 'var(--text-color)' }}
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
                  Description
                </label>
                <p className="mt-1" style={{ color: 'var(--text-color)' }}>
                  {selectedTask.description || 'No description'}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
                    Status
                  </label>
                  <p className="mt-1 px-3 py-1 rounded inline-block"
                     style={{
                       backgroundColor: getStatusColor(selectedTask.status),
                       color: 'white'
                     }}>
                    {selectedTask.status}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
                    Priority
                  </label>
                  <p className="mt-1 px-3 py-1 rounded inline-block"
                     style={{
                       backgroundColor: getPriorityColor(selectedTask.priority),
                       color: 'white'
                     }}>
                    {selectedTask.priority}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
                    Assigned To
                  </label>
                  <p className="mt-1" style={{ color: 'var(--text-color)' }}>
                    {selectedTask.assignedToName}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
                    Due Date
                  </label>
                  <p className="mt-1" style={{ color: 'var(--text-color)' }}>
                    {selectedTask.dueDate}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
                    Project ID
                  </label>
                  <p className="mt-1" style={{ color: 'var(--text-color)' }}>
                    {selectedTask.projectId}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
                    Progress
                  </label>
                  <p className="mt-1" style={{ color: 'var(--text-color)' }}>
                    {selectedTask.progress}%
                  </p>
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold mb-2 block" style={{ color: 'var(--text-secondary)' }}>
                  Progress
                </label>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="h-3 rounded-full transition-all"
                    style={{ 
                      width: `${selectedTask.progress}%`,
                      backgroundColor: 'var(--primary-color)'
                    }} 
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={closeDetails}
                className="px-4 py-2 rounded"
                style={{ 
                  backgroundColor: 'var(--primary-color)',
                  color: 'white'
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 p-4 rounded"
           style={{ 
             backgroundColor: 'var(--surface-color)',
             border: '1px solid var(--border-color)'
           }}>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          💡 <strong>Drag & Drop:</strong> Drag tasks between columns to update their status. Click "Details" to view full task information.
        </p>
      </div>
    </div>
  )
}

function getPriorityColor(priority: string) {
  switch (priority) {
    case 'High': return 'var(--error-color)'
    case 'Medium': return 'var(--warning-color)'
    case 'Low': return 'var(--info-color)'
    default: return 'var(--text-secondary)'
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case 'Done': return 'var(--success-color)'
    case 'In Progress': return 'var(--info-color)'
    case 'To Do': return 'var(--text-secondary)'
    default: return 'var(--text-secondary)'
  }
}
