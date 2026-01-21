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
  name?: string
  short_description?: string
  long_description?: string
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
  const [sprintTasksSearchQuery, setSprintTasksSearchQuery] = useState<string>('')
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
      console.log('Loading sprints for project:', selectedProjectId)
      const data = await api.getProjectSprints(selectedProjectId, false)
      console.log('Sprints loaded:', data)
      setSprints(data)
      if (data.length > 0 && !selectedSprintId) {
        console.log('Auto-selecting first sprint:', data[0].id)
        setSelectedSprintId(data[0].id)
      }
    } catch (error) {
      console.error('Failed to load sprints:', error)
      setSprints([]) // Set empty array on error
    } finally {
      setLoadingSprints(false)
    }
  }

  const loadSprintTasks = async () => {
    setLoadingTasks(true)
    try {
      console.log('Loading tasks for sprint:', selectedSprintId)
      const data = await api.getSprintTasks(selectedSprintId)
      console.log('Sprint tasks loaded:', data)
      setSprintTasks(data)
    } catch (error) {
      console.error('Failed to load sprint tasks:', error)
      setSprintTasks([]) // Set empty array on error
    } finally {
      setLoadingTasks(false)
    }
  }

  const loadAllTasks = async () => {
    try {
      // Get tasks filtered by the selected project
      const data = await api.getTasks(selectedProjectId)
      console.log('Loaded tasks for project:', selectedProjectId, data)
      setAllTasks(data)
    } catch (error) {
      console.error('Failed to load tasks:', error)
      setAllTasks([]) // Set empty array on error
    }
  }

  const handleAssignTask = async (taskId: string) => {
    try {
      await api.assignTaskToSprint(selectedSprintId, taskId)
      // Reload all data to get updated counts
      await Promise.all([
        loadSprintTasks(),
        loadAllTasks(),
        loadSprints() // This will refresh sprint statistics
      ])
    } catch (error: any) {
      console.error('Failed to assign task:', error)
      alert(error.response?.data?.detail || 'Failed to assign task to sprint')
    }
  }

  const handleUnassignTask = async (taskId: string) => {
    try {
      await api.unassignTaskFromSprint(selectedSprintId, taskId)
      // Reload all data to get updated counts
      await Promise.all([
        loadSprintTasks(),
        loadAllTasks(),
        loadSprints() // This will refresh sprint statistics
      ])
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
  
  // Filter unassigned tasks - tasks that don't have a sprint_id OR have a different sprint_id
  const unassignedTasks = allTasks.filter(t => !t.sprint_id || t.sprint_id === null || t.sprint_id === '')
  
  console.log('All tasks:', allTasks.length)
  console.log('Unassigned tasks:', unassignedTasks.length)
  console.log('Sprint tasks:', sprintTasks.length)
  
  // Filter unassigned tasks by search query
  const filteredUnassignedTasks = unassignedTasks.filter(task => {
    if (!searchQuery.trim()) return true
    
    const query = searchQuery.toLowerCase()
    const title = (task.title || task.name || '').toLowerCase()
    const description = (task.description || task.short_description || task.long_description || '').toLowerCase()
    const status = (task.status || '').toLowerCase()
    const assignedTo = (task.assigned_to || '').toLowerCase()
    
    // Debug search filtering
    const matches = title.includes(query) || 
                   description.includes(query) || 
                   status.includes(query) || 
                   assignedTo.includes(query)
    
    if (searchQuery.trim()) {
      console.log(`Search "${query}" in task "${title}":`, {
        title: title.includes(query),
        description: description.includes(query),
        status: status.includes(query),
        assignedTo: assignedTo.includes(query),
        matches
      })
    }
    
    return matches
  })
  
  // Debug search results
  if (searchQuery.trim()) {
    console.log(`Search results for "${searchQuery}":`, {
      totalUnassigned: unassignedTasks.length,
      filteredResults: filteredUnassignedTasks.length,
      searchQuery: searchQuery
    })
  }
  
  // Filter sprint tasks by search query
  const filteredSprintTasks = sprintTasks.filter(task => {
    if (!sprintTasksSearchQuery.trim()) return true
    
    const query = sprintTasksSearchQuery.toLowerCase()
    const title = (task.title || task.name || '').toLowerCase()
    const description = (task.description || task.short_description || task.long_description || '').toLowerCase()
    const status = (task.status || '').toLowerCase()
    const assignedTo = (task.assigned_to || '').toLowerCase()
    
    return title.includes(query) || 
           description.includes(query) || 
           status.includes(query) || 
           assignedTo.includes(query)
  })
  
  // Calculate completion rate with debugging
  const calculateCompletionRate = () => {
    if (!selectedSprint || selectedSprint.task_count === 0) {
      console.log('No sprint selected or no tasks in sprint')
      return 0
    }
    
    const totalTasks = selectedSprint.task_count
    const completedTasks = selectedSprint.completed_task_count
    const rate = Math.round((completedTasks / totalTasks) * 100)
    
    console.log('Sprint Progress Calculation:', {
      sprintId: selectedSprint.id,
      totalTasks,
      completedTasks,
      inProgress: selectedSprint.in_progress_task_count,
      todo: selectedSprint.todo_task_count,
      completionRate: rate
    })
    
    return rate
  }
  
  const completionRate = calculateCompletionRate()

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
                    
                    {/* Verification: Show actual task statuses from loaded tasks */}
                    {sprintTasks.length > 0 && (
                      <details className="mt-4">
                        <summary className="cursor-pointer text-xs" style={{ color: 'var(--text-secondary)' }}>
                          Verify Task Statuses ({sprintTasks.length} loaded tasks)
                        </summary>
                        <div className="mt-2 text-xs space-y-1">
                          {sprintTasks.map(task => (
                            <div key={task.id} className="flex justify-between">
                              <span>{task.title || task.id}</span>
                              <span style={{ 
                                color: task.status === 'Done' ? 'var(--success-color)' : 
                                       task.status === 'In Progress' ? 'var(--info-color)' : 
                                       'var(--text-secondary)' 
                              }}>
                                {task.status}
                              </span>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
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
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold" style={{ color: 'var(--text-color)' }}>
                    Sprint Tasks
                  </h2>
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    {filteredSprintTasks.length} of {sprintTasks.length} tasks
                  </span>
                </div>
                
                {/* Search Bar for Sprint Tasks */}
                {sprintTasks.length > 0 && (
                  <div className="mb-4">
                    <div className="relative">
                      <input
                        type="text"
                        placeholder="Search sprint tasks..."
                        value={sprintTasksSearchQuery}
                        onChange={(e) => setSprintTasksSearchQuery(e.target.value)}
                        className="w-full px-4 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        style={{
                          backgroundColor: 'var(--background-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                      />
                      {sprintTasksSearchQuery && (
                        <button
                          onClick={() => setSprintTasksSearchQuery('')}
                          className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                          title="Clear search"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  </div>
                )}
                
                {loadingTasks ? (
                  <div style={{ color: 'var(--text-color)' }}>Loading tasks...</div>
                ) : filteredSprintTasks.length === 0 ? (
                  <div className="text-center py-8">
                    <p style={{ color: 'var(--text-secondary)' }}>
                      {sprintTasksSearchQuery.trim() 
                        ? `No sprint tasks found matching "${sprintTasksSearchQuery}"`
                        : sprintTasks.length === 0 
                          ? 'No tasks assigned to this sprint.'
                          : 'No tasks match your search.'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {filteredSprintTasks.map(task => {
                      // Debug log for each sprint task
                      console.log('Rendering sprint task:', task)
                      
                      // Get task title with fallbacks
                      const taskTitle = task.title || task.name || task.short_description || `Task ${task.id}` || 'Untitled Task'
                      const taskDescription = task.description || task.short_description || task.long_description
                      
                      return (
                        <div key={task.id}
                             className="flex items-center justify-between p-3 rounded"
                             style={{ backgroundColor: 'var(--background-color)' }}>
                          <div className="flex-1">
                            <h3 className="font-medium" style={{ color: 'var(--text-color)' }}>
                              {taskTitle}
                            </h3>
                            {taskDescription && (
                              <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                                {taskDescription.length > 100 
                                  ? `${taskDescription.substring(0, 100)}...` 
                                  : taskDescription}
                              </p>
                            )}
                            <div className="flex items-center gap-4 mt-2">
                              {task.due_date && (
                                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                  Due: {formatDate(task.due_date)}
                                </p>
                              )}
                              {task.assigned_to && (
                                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                  Assigned: {task.assigned_to}
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="px-3 py-1 rounded text-sm"
                                  style={{
                                    backgroundColor: getStatusColor(task.status),
                                    color: 'white'
                                  }}>
                              {task.status || 'No Status'}
                            </span>
                            <button
                              onClick={() => handleUnassignTask(task.id)}
                              className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                      )
                    })}
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
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Search tasks by title, description, status, or assignee..."
                      value={searchQuery}
                      onChange={(e) => {
                        console.log('Search query changed:', e.target.value)
                        setSearchQuery(e.target.value)
                      }}
                      className="w-full px-4 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      style={{
                        backgroundColor: 'var(--background-color)',
                        borderColor: 'var(--border-color)',
                        color: 'var(--text-color)'
                      }}
                    />
                    {searchQuery && (
                      <button
                        onClick={() => {
                          console.log('Clearing search')
                          setSearchQuery('')
                        }}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        title="Clear search"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                  {searchQuery && (
                    <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
                      Searching for: "{searchQuery}" - Found {filteredUnassignedTasks.length} of {unassignedTasks.length} tasks
                    </p>
                  )}
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
                      {filteredUnassignedTasks.map(task => {
                        // Debug log for each task
                        console.log('Rendering task:', task)
                        
                        // Get task title with fallbacks
                        const taskTitle = task.title || task.name || task.short_description || `Task ${task.id}` || 'Untitled Task'
                        const taskDescription = task.description || task.short_description || task.long_description
                        
                        return (
                          <div key={task.id}
                               className="flex items-center justify-between p-3 rounded"
                               style={{ backgroundColor: 'var(--background-color)' }}>
                            <div className="flex-1">
                              <h3 className="font-medium" style={{ color: 'var(--text-color)' }}>
                                {taskTitle}
                              </h3>
                              {taskDescription && (
                                <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                                  {taskDescription.length > 100 
                                    ? `${taskDescription.substring(0, 100)}...` 
                                    : taskDescription}
                                </p>
                              )}
                              <div className="flex items-center gap-4 mt-2">
                                {task.due_date && (
                                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                    Due: {formatDate(task.due_date)}
                                  </p>
                                )}
                                {task.assigned_to && (
                                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                    Assigned: {task.assigned_to}
                                  </p>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="px-3 py-1 rounded text-sm"
                                    style={{
                                      backgroundColor: getStatusColor(task.status),
                                      color: 'white'
                                    }}>
                                {task.status || 'No Status'}
                              </span>
                              <button
                                onClick={() => handleAssignTask(task.id)}
                                className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                              >
                                Add to Sprint
                              </button>
                            </div>
                          </div>
                        )
                      })}
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
    case 'Completed': return 'var(--success-color)'
    case 'In Progress': return 'var(--info-color)'
    case 'In Review': return 'var(--info-color)'
    case 'Planning': return 'var(--warning-color)'
    case 'On-Hold': return 'var(--text-secondary)'
    case 'Blocked': return 'var(--text-secondary)'
    case 'Canceled': return 'var(--error-color)'
    default: return 'var(--text-secondary)'
  }
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return 'No due date'
  
  try {
    // Handle different date formats
    let date: Date
    
    // If it's already a valid date string, try to parse it
    if (dateStr.includes('T') || dateStr.includes('-')) {
      date = new Date(dateStr)
    } else {
      // If it's a timestamp or other format
      date = new Date(dateStr)
    }
    
    // Check if the date is valid
    if (isNaN(date.getTime())) {
      // Try parsing as ISO date string
      const isoMatch = dateStr.match(/(\d{4})-(\d{2})-(\d{2})/)
      if (isoMatch) {
        date = new Date(parseInt(isoMatch[1]), parseInt(isoMatch[2]) - 1, parseInt(isoMatch[3]))
      } else {
        return dateStr // Return original string if we can't parse it
      }
    }
    
    // Format as MM/DD/YYYY
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const year = date.getFullYear()
    
    return `${month}/${day}/${year}`
  } catch (error) {
    console.warn('Error formatting date:', dateStr, error)
    return dateStr || 'Invalid date'
  }
}