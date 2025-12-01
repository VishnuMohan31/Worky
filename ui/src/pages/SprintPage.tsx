import { useEffect, useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'

interface Sprint {
  id: string
  name: string
  start_date: string
  end_date: string
  status: string
  task_count: number
  completed_task_count: number
  in_progress_task_count: number
  todo_task_count: number
}

interface Task {
  id: string
  title: string
  description?: string
  status: string
  assigned_to?: string
  due_date?: string
  sprint_id?: string
}

export default function SprintPage() {
  const { t } = useLanguage()
  const [projects, setProjects] = useState<any[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [sprints, setSprints] = useState<Sprint[]>([])
  const [selectedSprintId, setSelectedSprintId] = useState<string>('')
  const [sprintTasks, setSprintTasks] = useState<Task[]>([])
  const [allTasks, setAllTasks] = useState<Task[]>([])
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [loadingSprints, setLoadingSprints] = useState(false)
  const [loadingTasks, setLoadingTasks] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadSprints()
    } else {
      setSprints([])
      setSelectedSprintId('')
      setSprintTasks([])
    }
  }, [selectedProjectId])

  useEffect(() => {
    if (selectedSprintId) {
      loadSprintTasks()
    } else {
      setSprintTasks([])
    }
  }, [selectedSprintId])

  useEffect(() => {
    if (selectedProjectId) {
      loadAllTasks()
    }
  }, [selectedProjectId])

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

  const loadSprintTasks = async () => {
    setLoadingTasks(true)
    try {
      const data = await api.getSprintTasks(selectedSprintId)
      setSprintTasks(data)
    } catch (error) {
      console.error('Failed to load sprint tasks:', error)
    } finally {
      setLoadingTasks(false)
    }
  }

  const loadAllTasks = async () => {
    try {
      const data = await api.getTasks()
      // Filter tasks that belong to this project's hierarchy
      // For now, just get all tasks - you may want to filter by project
      setAllTasks(data)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    }
  }

  const handleAssignTask = async (taskId: string) => {
    try {
      await api.assignTaskToSprint(selectedSprintId, taskId)
      await loadSprintTasks()
      await loadAllTasks()
    } catch (error: any) {
      console.error('Failed to assign task:', error)
      alert(error.response?.data?.detail || 'Failed to assign task to sprint')
    }
  }

  const handleUnassignTask = async (taskId: string) => {
    try {
      await api.unassignTaskFromSprint(selectedSprintId, taskId)
      await loadSprintTasks()
      await loadAllTasks()
    } catch (error: any) {
      console.error('Failed to unassign task:', error)
      alert(error.response?.data?.detail || 'Failed to unassign task from sprint')
    }
  }

  const formatSprintDisplay = (sprint: Sprint) => {
    const formatDate = (dateStr: string) => {
      const date = new Date(dateStr)
      const day = String(date.getDate()).padStart(2, '0')
      const month = date.toLocaleString('default', { month: 'short' }).toUpperCase()
      const year = date.getFullYear()
      return `${day}-${month}-${year}`
    }
    return `${sprint.id} (${formatDate(sprint.start_date)} to ${formatDate(sprint.end_date)})`
  }

  const selectedSprint = sprints.find(s => s.id === selectedSprintId)
  const unassignedTasks = allTasks.filter(t => !t.sprint_id)
  
  // Filter unassigned tasks by search query
  const filteredUnassignedTasks = unassignedTasks.filter(task => {
    if (!searchQuery.trim()) return true
    const query = searchQuery.toLowerCase()
    const title = (task.title || '').toLowerCase()
    const description = (task.description || '').toLowerCase()
    return title.includes(query) || description.includes(query)
  })
  
  const completionRate = selectedSprint && selectedSprint.task_count > 0
    ? Math.round((selectedSprint.completed_task_count / selectedSprint.task_count) * 100)
    : 0

  if (loading) {
    return <div style={{ color: 'var(--text-color)' }}>{t('loading')}</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text-color)' }}>
        Sprint Board 🏃
      </h1>

      {/* Project Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
          Select Project:
        </label>
        <select
          value={selectedProjectId}
          onChange={(e) => setSelectedProjectId(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{
            backgroundColor: 'var(--surface-color)',
            borderColor: 'var(--border-color)',
            color: 'var(--text-color)'
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

      {selectedProjectId && (
        <>
          {/* Sprint Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
              Select Sprint:
            </label>
            {loadingSprints ? (
              <div style={{ color: 'var(--text-color)' }}>Loading sprints...</div>
            ) : (
              <select
                value={selectedSprintId}
                onChange={(e) => setSelectedSprintId(e.target.value)}
                className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{
                  backgroundColor: 'var(--surface-color)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-color)',
                  minWidth: '400px'
                }}
              >
                <option value="">Select a sprint...</option>
                {sprints.map(sprint => (
                  <option key={sprint.id} value={sprint.id}>
                    {formatSprintDisplay(sprint)}
                  </option>
                ))}
              </select>
            )}
          </div>

          {selectedSprint && (
            <>
              {/* Sprint Overview */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="rounded-lg p-6 shadow-md"
                     style={{ 
                       backgroundColor: 'var(--surface-color)',
                       border: '1px solid var(--border-color)'
                     }}>
                  <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                    {selectedSprint.name}
                  </h2>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span style={{ color: 'var(--text-secondary)' }}>Duration:</span>
                      <span style={{ color: 'var(--text-color)' }}>
                        {new Date(selectedSprint.start_date).toLocaleDateString()} - {new Date(selectedSprint.end_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{ color: 'var(--text-secondary)' }}>Total Tasks:</span>
                      <span style={{ color: 'var(--text-color)' }}>{selectedSprint.task_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{ color: 'var(--text-secondary)' }}>Completed:</span>
                      <span style={{ color: 'var(--success-color)' }}>{selectedSprint.completed_task_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{ color: 'var(--text-secondary)' }}>In Progress:</span>
                      <span style={{ color: 'var(--info-color)' }}>{selectedSprint.in_progress_task_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{ color: 'var(--text-secondary)' }}>To Do:</span>
                      <span style={{ color: 'var(--text-secondary)' }}>{selectedSprint.todo_task_count}</span>
                    </div>
                  </div>
                </div>

                {/* Sprint Progress */}
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
              <div className="rounded-lg p-6 shadow-md mb-6"
                   style={{ 
                     backgroundColor: 'var(--surface-color)',
                     border: '1px solid var(--border-color)'
                   }}>
                <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                  Sprint Tasks
                </h2>
                {loadingTasks ? (
                  <div style={{ color: 'var(--text-color)' }}>Loading tasks...</div>
                ) : sprintTasks.length === 0 ? (
                  <p style={{ color: 'var(--text-secondary)' }}>No tasks assigned to this sprint.</p>
                ) : (
                  <div className="space-y-3">
                    {sprintTasks.map(task => (
                      <div key={task.id}
                           className="flex items-center justify-between p-3 rounded"
                           style={{ backgroundColor: 'var(--background-color)' }}>
                        <div className="flex-1">
                          <h3 className="font-medium" style={{ color: 'var(--text-color)' }}>
                            {task.title}
                          </h3>
                          {task.due_date && (
                            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                              Due: {new Date(task.due_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="px-3 py-1 rounded text-sm"
                                style={{
                                  backgroundColor: getStatusColor(task.status),
                                  color: 'white'
                                }}>
                            {task.status}
                          </span>
                          <button
                            onClick={() => handleUnassignTask(task.id)}
                            className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Unassigned Tasks */}
              <div className="rounded-lg p-6 shadow-md"
                   style={{ 
                     backgroundColor: 'var(--surface-color)',
                     border: '1px solid var(--border-color)'
                   }}>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold" style={{ color: 'var(--text-color)' }}>
                    Available Tasks (Unassigned)
                  </h2>
                  <div className="flex items-center gap-2">
                    <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      {filteredUnassignedTasks.length} of {unassignedTasks.length} tasks
                    </span>
                  </div>
                </div>
                
                {/* Search Bar */}
                <div className="mb-4">
                  <input
                    type="text"
                    placeholder="Search tasks by title or description..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      backgroundColor: 'var(--background-color)',
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-color)'
                    }}
                  />
                </div>
                
                {filteredUnassignedTasks.length === 0 ? (
                  <div className="text-center py-8">
                    <p style={{ color: 'var(--text-secondary)' }}>
                      {searchQuery.trim() 
                        ? `No tasks found matching "${searchQuery}"`
                        : 'No unassigned tasks available'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {filteredUnassignedTasks.map(task => (
                      <div key={task.id}
                           className="flex items-center justify-between p-3 rounded"
                           style={{ backgroundColor: 'var(--background-color)' }}>
                        <div className="flex-1">
                          <h3 className="font-medium" style={{ color: 'var(--text-color)' }}>
                            {task.title}
                          </h3>
                          {task.due_date && (
                            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                              Due: {new Date(task.due_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="px-3 py-1 rounded text-sm"
                                style={{
                                  backgroundColor: getStatusColor(task.status),
                                  color: 'white'
                                }}>
                            {task.status}
                          </span>
                          <button
                            onClick={() => handleAssignTask(task.id)}
                            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                          >
                            Add to Sprint
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </>
      )}

      {!selectedProjectId && (
        <div className="mt-6 p-4 rounded"
             style={{ 
               backgroundColor: 'var(--surface-color)',
               border: '1px solid var(--border-color)'
             }}>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Please select a project to view and manage sprints.
          </p>
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
