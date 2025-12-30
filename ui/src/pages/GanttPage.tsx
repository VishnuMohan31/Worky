import { useEffect, useState, useMemo } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'

type HierarchyLevel = 'client' | 'program' | 'project' | 'usecase' | 'userstory' | 'task'
type DurationLevel = 'program' | 'project' | 'usecase' | 'userstory' | 'task' | 'subtask'

interface GanttItem {
  id: string
  name: string
  title?: string
  startDate?: string
  endDate?: string
  dueDate?: string
  status: string
  progress?: number
  assignedToName?: string
}

const HIERARCHY_LEVELS: { value: HierarchyLevel; label: string }[] = [
  { value: 'client', label: 'Client' },
  { value: 'program', label: 'Program' },
  { value: 'project', label: 'Project' },
  { value: 'usecase', label: 'Use Case' },
  { value: 'userstory', label: 'User Story' },
  { value: 'task', label: 'Task' }
]

const DURATION_LEVELS: { value: DurationLevel; label: string }[] = [
  { value: 'program', label: 'Programs' },
  { value: 'project', label: 'Projects' },
  { value: 'usecase', label: 'Use Cases' },
  { value: 'userstory', label: 'User Stories' },
  { value: 'task', label: 'Tasks' },
  { value: 'subtask', label: 'Subtasks' }
]

// Define which duration levels are available for each hierarchy level
const AVAILABLE_DURATION_LEVELS: Record<HierarchyLevel, DurationLevel[]> = {
  client: ['program', 'project', 'usecase', 'userstory', 'task', 'subtask'],
  program: ['project', 'usecase', 'userstory', 'task', 'subtask'],
  project: ['usecase', 'userstory', 'task', 'subtask'],
  usecase: ['userstory', 'task', 'subtask'],
  userstory: ['task', 'subtask'],
  task: ['subtask']
}

export default function GanttPage() {
  const { } = useLanguage() // Language context available if needed
  const [selectedLevel, setSelectedLevel] = useState<HierarchyLevel>('project')
  const [selectedDurationLevel, setSelectedDurationLevel] = useState<DurationLevel>('task')
  const [items, setItems] = useState<GanttItem[]>([])
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState<'month' | 'week'>('month')
  const [currentUser, setCurrentUser] = useState<any>(null)

  // Hierarchy selections
  const [selectedClientId, setSelectedClientId] = useState<string>('')
  const [selectedProgramId, setSelectedProgramId] = useState<string>('')
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [selectedUseCaseId, setSelectedUseCaseId] = useState<string>('')
  const [selectedUserStoryId, setSelectedUserStoryId] = useState<string>('')
  const [selectedTaskId, setSelectedTaskId] = useState<string>('')

  // Data arrays
  const [clients, setClients] = useState<any[]>([])
  const [programs, setPrograms] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [usecases, setUsecases] = useState<any[]>([])
  const [userstories, setUserstories] = useState<any[]>([])
  const [tasks, setTasks] = useState<any[]>([])

  // Helper function to safely make API calls without causing logout
  const safeApiCall = async (apiFunction: () => Promise<any>, fallbackValue: any = []) => {
    try {
      const result = await apiFunction()
      console.log('✅ Safe API call successful')
      return result
    } catch (error: any) {
      // Log the error but don't let it propagate to avoid logout
      console.warn('⚠️ Safe API call failed:', error.message, 'Status:', error.response?.status)
      
      // For 401 errors, specifically prevent the interceptor from triggering logout
      if (error.response?.status === 401) {
        console.warn('🚫 401 error caught in safeApiCall - using fallback value, NOT redirecting to login')
      }
      
      // For any error, return fallback value instead of throwing
      return fallbackValue
    }
  }

  // Filter available duration levels based on user permissions
  const availableDurationLevels = useMemo(() => {
    // Always return a valid array to prevent hooks order issues
    if (!currentUser) {
      // Return all levels except subtasks for non-authenticated users
      return AVAILABLE_DURATION_LEVELS[selectedLevel].filter(level => level !== 'subtask')
    }
    
    let levels = AVAILABLE_DURATION_LEVELS[selectedLevel]
    
    // For non-admin users, only show subtasks if a specific task is selected
    if (currentUser.role !== 'Admin' && selectedLevel !== 'task') {
      levels = levels.filter(level => level !== 'subtask')
    }
    
    return levels
  }, [selectedLevel, currentUser])

  // Load current user and clients on mount
  useEffect(() => {
    const loadInitialData = async () => {
      // Load current user first
      const user = await safeApiCall(() => api.getCurrentUser(), null)
      setCurrentUser(user)
      
      // Load clients
      const clientsData = await safeApiCall(() => api.getClients(), [])
      setClients(clientsData)
    }
    loadInitialData()
  }, [])

  // Load programs when client is selected
  useEffect(() => {
    const loadPrograms = async () => {
      if (!selectedClientId) {
        setPrograms([])
        return
      }
      const allPrograms = await safeApiCall(() => api.getEntityList('program'), [])
      const filteredPrograms = allPrograms.filter((p: any) => 
        (p.clientId === selectedClientId || p.client_id === selectedClientId)
      )
      setPrograms(filteredPrograms)
    }
    loadPrograms()
  }, [selectedClientId])

  // Load projects when program is selected
  useEffect(() => {
    const loadProjects = async () => {
      if (!selectedProgramId) {
        setProjects([])
        return
      }
      const allProjects = await safeApiCall(() => api.getProjects(), [])
      const filteredProjects = allProjects.filter((p: any) => 
        (p.programId === selectedProgramId || p.program_id === selectedProgramId)
      )
      setProjects(filteredProjects)
    }
    loadProjects()
  }, [selectedProgramId])

  // Load use cases when project is selected
  useEffect(() => {
    const loadUseCases = async () => {
      if (!selectedProjectId) {
        setUsecases([])
        return
      }
      const allUseCases = await safeApiCall(() => api.getEntityList('usecase'), [])
      const filteredUseCases = allUseCases.filter((uc: any) => 
        (uc.projectId === selectedProjectId || uc.project_id === selectedProjectId)
      )
      setUsecases(filteredUseCases)
    }
    loadUseCases()
  }, [selectedProjectId])

  // Load user stories when use case is selected
  useEffect(() => {
    const loadUserStories = async () => {
      if (!selectedUseCaseId) {
        setUserstories([])
        return
      }
      const allStories = await safeApiCall(() => api.getEntityList('userstory'), [])
      const filteredStories = allStories.filter((s: any) => 
        (s.usecaseId === selectedUseCaseId || s.usecase_id === selectedUseCaseId)
      )
      setUserstories(filteredStories)
    }
    loadUserStories()
  }, [selectedUseCaseId])

  // Load tasks when user story is selected
  useEffect(() => {
    const loadTasks = async () => {
      if (!selectedUserStoryId) {
        setTasks([])
        return
      }
      const allTasks = await safeApiCall(() => api.getTasks(), [])
      const filteredTasks = allTasks.filter((t: any) => 
        (t.userStoryId === selectedUserStoryId || t.user_story_id === selectedUserStoryId)
      )
      setTasks(filteredTasks)
    }
    loadTasks()
  }, [selectedUserStoryId])

  // Update available duration levels when hierarchy level or user changes
  useEffect(() => {
    if (availableDurationLevels && availableDurationLevels.length > 0 && !availableDurationLevels.includes(selectedDurationLevel)) {
      // Reset to first available level
      setSelectedDurationLevel(availableDurationLevels[0])
    }
  }, [selectedLevel, availableDurationLevels, selectedDurationLevel])

  // Load items for Gantt chart based on selections
  useEffect(() => {
    // Only load if we have current user data
    if (currentUser) {
      loadGanttItems()
    }
  }, [selectedLevel, selectedDurationLevel, selectedClientId, selectedProgramId, selectedProjectId, selectedUseCaseId, selectedUserStoryId, selectedTaskId, currentUser])

  const loadGanttItems = async () => {
    if (!selectedDurationLevel || !currentUser) return

    setLoading(true)
    try {
      let items: GanttItem[] = []

      switch (selectedDurationLevel) {
        case 'program':
          const allPrograms = await safeApiCall(() => api.getEntityList('program'), [])
          if (selectedLevel === 'client' && selectedClientId) {
            items = allPrograms
              .filter((p: any) => (p.clientId === selectedClientId || p.client_id === selectedClientId))
              .map((p: any) => ({
                id: p.id,
                name: p.name,
                startDate: p.start_date || p.startDate,
                endDate: p.end_date || p.endDate,
                status: p.status || 'Planning',
                progress: p.progress || 0
              }))
          } else {
            items = allPrograms.map((p: any) => ({
              id: p.id,
              name: p.name,
              startDate: p.start_date || p.startDate,
              endDate: p.end_date || p.endDate,
              status: p.status || 'Planning',
              progress: p.progress || 0
            }))
          }
          break

        case 'project':
          const allProjects = await safeApiCall(() => api.getProjects(), [])
          if (selectedLevel === 'client' && selectedClientId) {
            // Get all programs for client, then all projects for those programs
            const clientPrograms = programs.filter((p: any) => 
              (p.clientId === selectedClientId || p.client_id === selectedClientId)
            )
            const programIds = clientPrograms.map((p: any) => p.id)
            items = allProjects
              .filter((p: any) => programIds.includes(p.programId || p.program_id))
              .map((p: any) => ({
                id: p.id,
                name: p.name,
                startDate: p.startDate || p.start_date,
                endDate: p.endDate || p.end_date,
                status: p.status || 'Planning',
                progress: p.progress || 0
              }))
          } else if (selectedLevel === 'program' && selectedProgramId) {
            items = allProjects
              .filter((p: any) => (p.programId === selectedProgramId || p.program_id === selectedProgramId))
              .map((p: any) => ({
                id: p.id,
                name: p.name,
                startDate: p.startDate || p.start_date,
                endDate: p.endDate || p.end_date,
                status: p.status || 'Planning',
                progress: p.progress || 0
              }))
          } else {
            items = allProjects.map((p: any) => ({
              id: p.id,
              name: p.name,
              startDate: p.startDate || p.start_date,
              endDate: p.endDate || p.end_date,
              status: p.status || 'Planning',
              progress: p.progress || 0
            }))
          }
          break

        case 'usecase':
          const allUseCases = await safeApiCall(() => api.getEntityList('usecase'), [])
          if (selectedLevel === 'project' && selectedProjectId) {
            items = allUseCases
              .filter((uc: any) => (uc.projectId === selectedProjectId || uc.project_id === selectedProjectId))
              .map((uc: any) => ({
                id: uc.id,
                name: uc.name,
                startDate: uc.start_date || uc.startDate,
                endDate: uc.end_date || uc.endDate,
                status: uc.status || 'Draft',
                progress: uc.progress || 0
              }))
          } else if (selectedLevel === 'program' && selectedProgramId) {
            // Get all projects for program, then all use cases
            const programProjects = projects.filter((p: any) => 
              (p.programId === selectedProgramId || p.program_id === selectedProgramId)
            )
            const projectIds = programProjects.map((p: any) => p.id)
            items = allUseCases
              .filter((uc: any) => projectIds.includes(uc.projectId || uc.project_id))
              .map((uc: any) => ({
                id: uc.id,
                name: uc.name,
                startDate: uc.start_date || uc.startDate,
                endDate: uc.end_date || uc.endDate,
                status: uc.status || 'Draft',
                progress: uc.progress || 0
              }))
          } else if (selectedLevel === 'client' && selectedClientId) {
            // Get all programs, projects, then use cases
            const clientPrograms = programs.filter((p: any) => 
              (p.clientId === selectedClientId || p.client_id === selectedClientId)
            )
            const programIds = clientPrograms.map((p: any) => p.id)
            const clientProjects = projects.filter((p: any) => 
              programIds.includes(p.programId || p.program_id)
            )
            const projectIds = clientProjects.map((p: any) => p.id)
            items = allUseCases
              .filter((uc: any) => projectIds.includes(uc.projectId || uc.project_id))
              .map((uc: any) => ({
                id: uc.id,
                name: uc.name,
                startDate: uc.start_date || uc.startDate,
                endDate: uc.end_date || uc.endDate,
                status: uc.status || 'Draft',
                progress: uc.progress || 0
              }))
          } else {
            items = allUseCases.map((uc: any) => ({
              id: uc.id,
              name: uc.name,
              startDate: uc.start_date || uc.startDate,
              endDate: uc.end_date || uc.endDate,
              status: uc.status || 'Draft',
              progress: uc.progress || 0
            }))
          }
          break

        case 'userstory':
          const allUserStories = await safeApiCall(() => api.getEntityList('userstory'), [])
          if (selectedLevel === 'usecase' && selectedUseCaseId) {
            items = allUserStories
              .filter((s: any) => (s.usecaseId === selectedUseCaseId || s.usecase_id === selectedUseCaseId))
              .map((s: any) => ({
                id: s.id,
                name: s.title || s.name,
                title: s.title || s.name,
                startDate: s.start_date || s.startDate,
                endDate: s.end_date || s.endDate,
                status: s.status || 'To Do',
                progress: s.progress || 0
              }))
          } else if (selectedLevel === 'project' && selectedProjectId) {
            // Get all use cases for project, then all user stories
            const projectUseCases = usecases.filter((uc: any) => 
              (uc.projectId === selectedProjectId || uc.project_id === selectedProjectId)
            )
            const useCaseIds = projectUseCases.map((uc: any) => uc.id)
            items = allUserStories
              .filter((s: any) => useCaseIds.includes(s.usecaseId || s.usecase_id))
              .map((s: any) => ({
                id: s.id,
                name: s.title || s.name,
                title: s.title || s.name,
                startDate: s.start_date || s.startDate,
                endDate: s.end_date || s.endDate,
                status: s.status || 'To Do',
                progress: s.progress || 0
              }))
          } else {
            items = allUserStories.map((s: any) => ({
              id: s.id,
              name: s.title || s.name,
              title: s.title || s.name,
              startDate: s.start_date || s.startDate,
              endDate: s.end_date || s.endDate,
              status: s.status || 'To Do',
              progress: s.progress || 0
            }))
          }
          break

        case 'task':
          const allTasks = await safeApiCall(() => api.getTasks(), [])
          if (selectedLevel === 'userstory' && selectedUserStoryId) {
            items = allTasks
              .filter((t: any) => (t.userStoryId === selectedUserStoryId || t.user_story_id === selectedUserStoryId))
              .map((t: any) => ({
                id: t.id,
                name: t.title || t.name,
                title: t.title || t.name,
                startDate: t.start_date || t.startDate,
                dueDate: t.dueDate || t.due_date,
                endDate: t.dueDate || t.due_date || t.end_date || t.endDate,
                status: t.status || 'To Do',
                progress: t.progress || 0,
                assignedToName: t.assignedToName || t.assigned_to_name
              }))
          } else if (selectedLevel === 'usecase' && selectedUseCaseId) {
            // Get all user stories for use case, then all tasks
            const useCaseStories = userstories.filter((s: any) => 
              (s.usecaseId === selectedUseCaseId || s.usecase_id === selectedUseCaseId)
            )
            const storyIds = useCaseStories.map((s: any) => s.id)
            items = allTasks
              .filter((t: any) => storyIds.includes(t.userStoryId || t.user_story_id))
              .map((t: any) => ({
                id: t.id,
                name: t.title || t.name,
                title: t.title || t.name,
                startDate: t.start_date || t.startDate,
                dueDate: t.dueDate || t.due_date,
                endDate: t.dueDate || t.due_date || t.end_date || t.endDate,
                status: t.status || 'To Do',
                progress: t.progress || 0,
                assignedToName: t.assignedToName || t.assigned_to_name
              }))
          } else if (selectedLevel === 'project' && selectedProjectId) {
            // Get all use cases, user stories, then tasks
            const projectUseCases = usecases.filter((uc: any) => 
              (uc.projectId === selectedProjectId || uc.project_id === selectedProjectId)
            )
            const useCaseIds = projectUseCases.map((uc: any) => uc.id)
            const projectStories = userstories.filter((s: any) => 
              useCaseIds.includes(s.usecaseId || s.usecase_id)
            )
            const storyIds = projectStories.map((s: any) => s.id)
            items = allTasks
              .filter((t: any) => storyIds.includes(t.userStoryId || t.user_story_id))
              .map((t: any) => ({
                id: t.id,
                name: t.title || t.name,
                title: t.title || t.name,
                startDate: t.start_date || t.startDate,
                dueDate: t.dueDate || t.due_date,
                endDate: t.dueDate || t.due_date || t.end_date || t.endDate,
                status: t.status || 'To Do',
                progress: t.progress || 0,
                assignedToName: t.assignedToName || t.assigned_to_name
              }))
          } else {
            items = allTasks.map((t: any) => ({
              id: t.id,
              name: t.title || t.name,
              title: t.title || t.name,
              startDate: t.start_date || t.startDate,
              dueDate: t.dueDate || t.due_date,
              endDate: t.dueDate || t.due_date || t.end_date || t.endDate,
              status: t.status || 'To Do',
              progress: t.progress || 0,
              assignedToName: t.assignedToName || t.assigned_to_name
            }))
          }
          break

        case 'subtask':
          console.log('🔍 Loading subtasks - User role:', currentUser?.role, 'Selected level:', selectedLevel, 'Task ID:', selectedTaskId)
          
          // Check if user is admin or if we have a specific task selected
          if (currentUser?.role === 'Admin' || (selectedLevel === 'task' && selectedTaskId)) {
            console.log('✅ User has permission to view subtasks, making API call...')
            const allSubtasks = await safeApiCall(() => api.getSubtasksSafe(selectedTaskId || undefined), [])
            console.log('📊 Subtasks API response:', allSubtasks)
            
            if (selectedLevel === 'task' && selectedTaskId) {
              items = allSubtasks
                .filter((st: any) => (st.taskId === selectedTaskId || st.task_id === selectedTaskId))
                .map((st: any) => ({
                  id: st.id,
                  name: st.title || st.name,
                  title: st.title || st.name,
                  startDate: st.start_date || st.startDate,
                  endDate: st.end_date || st.endDate,
                  dueDate: st.due_date || st.dueDate,
                  status: st.status || 'To Do',
                  progress: st.progress || 0,
                  assignedToName: st.assignedToName || st.assigned_to_name
                }))
            } else {
              items = allSubtasks.map((st: any) => ({
                id: st.id,
                name: st.title || st.name,
                title: st.title || st.name,
                startDate: st.start_date || st.startDate,
                endDate: st.end_date || st.endDate,
                dueDate: st.due_date || st.dueDate,
                status: st.status || 'To Do',
                progress: st.progress || 0,
                assignedToName: st.assignedToName || st.assigned_to_name
              }))
            }
            console.log('✅ Processed subtasks items:', items.length)
          } else {
            // For non-admin users without a specific task selected, show empty array
            console.log('❌ Subtasks view requires admin role or specific task selection - showing empty array')
            items = []
          }
          break
      }

      // Add default dates if missing
      const itemsWithDates = items.map((item) => ({
        ...item,
        startDate: item.startDate || new Date().toISOString().split('T')[0],
        endDate: item.endDate || item.dueDate || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      }))

      setItems(itemsWithDates)
    } catch (error) {
      console.error('Failed to load Gantt items:', error)
      // Don't let API errors cause logout - just show empty chart
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  // Calculate timeline range
  const { startDate, endDate, timelineMonths } = useMemo(() => {
    if (items.length === 0) {
      const today = new Date()
      return {
        startDate: today,
        endDate: new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000),
        timelineMonths: [],
        timelineWeeks: []
      }
    }

    const dates = items.flatMap(item => [
      new Date(item.startDate || Date.now()),
      new Date(item.endDate || Date.now())
    ])
    
    const minDate = new Date(Math.min(...dates.map(d => d.getTime())))
    const maxDate = new Date(Math.max(...dates.map(d => d.getTime())))
    
    // Add padding
    minDate.setDate(minDate.getDate() - 7)
    maxDate.setDate(maxDate.getDate() + 7)
    
    // Generate months
    const months: { month: string; year: number; weeks: number }[] = []
    const current = new Date(minDate)
    current.setDate(1)
    
    while (current <= maxDate) {
      const daysInMonth = new Date(current.getFullYear(), current.getMonth() + 1, 0).getDate()
      months.push({
        month: current.toLocaleString('default', { month: 'short' }),
        year: current.getFullYear(),
        weeks: Math.ceil(daysInMonth / 7)
      })
      current.setMonth(current.getMonth() + 1)
    }
    
    // Generate weeks
    const weeks: Date[] = []
    const weekCurrent = new Date(minDate)
    weekCurrent.setDate(weekCurrent.getDate() - weekCurrent.getDay()) // Start of week
    
    while (weekCurrent <= maxDate) {
      weeks.push(new Date(weekCurrent))
      weekCurrent.setDate(weekCurrent.getDate() + 7)
    }
    
    return {
      startDate: minDate,
      endDate: maxDate,
      timelineMonths: months
    }
  }, [items])

  // Calculate task bar position and width
  const getTaskBarStyle = (item: GanttItem) => {
    const itemStart = new Date(item.startDate || Date.now())
    const itemEnd = new Date(item.endDate || Date.now())
    const totalDays = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
    const startOffset = (itemStart.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
    const duration = (itemEnd.getTime() - itemStart.getTime()) / (1000 * 60 * 60 * 24)
    
    const left = (startOffset / totalDays) * 100
    const width = (duration / totalDays) * 100
    
    return {
      left: `${Math.max(0, left)}%`,
      width: `${Math.max(2, width)}%`
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'To Do': '#94a3b8',
      'In Progress': '#3b82f6',
      'Done': '#22c55e',
      'Blocked': '#ef4444',
      'Planning': '#94a3b8',
      'Draft': '#94a3b8',
      'Completed': '#22c55e',
      'On Hold': '#f59e0b'
    }
    return colors[status] || '#94a3b8'
  }

  const exportToPDF = () => {
    alert('Export to PDF functionality - will use jsPDF library')
  }

  const exportToPNG = () => {
    alert('Export to PNG functionality - will use html2canvas library')
  }



  // Get selected entity name for display
  const getSelectedEntityName = () => {
    switch (selectedLevel) {
      case 'client':
        return clients.find(c => c.id === selectedClientId)?.name || ''
      case 'program':
        return programs.find(p => p.id === selectedProgramId)?.name || ''
      case 'project':
        return projects.find(p => p.id === selectedProjectId)?.name || ''
      case 'usecase':
        return usecases.find(uc => uc.id === selectedUseCaseId)?.name || ''
      case 'userstory':
        return userstories.find(us => us.id === selectedUserStoryId)?.title || userstories.find(us => us.id === selectedUserStoryId)?.name || ''
      case 'task':
        return tasks.find(t => t.id === selectedTaskId)?.title || tasks.find(t => t.id === selectedTaskId)?.name || ''
      default:
        return ''
    }
  }

  const isLevelSelected = () => {
    switch (selectedLevel) {
      case 'client':
        return !!selectedClientId
      case 'program':
        return !!selectedProgramId
      case 'project':
        return !!selectedProjectId
      case 'usecase':
        return !!selectedUseCaseId
      case 'userstory':
        return !!selectedUserStoryId
      case 'task':
        return !!selectedTaskId
      default:
        return false
    }
  }

  // Show loading while initializing
  if (!availableDurationLevels || availableDurationLevels.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-2">Initializing...</span>
      </div>
    )
  }

  if (loading && items.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gantt Chart 📈</h1>
          <p className="text-gray-600 mt-1">Project timeline and task scheduling</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('month')}
            className={`px-4 py-2 rounded-md transition-colors ${
              viewMode === 'month'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Month View
          </button>
          <button
            onClick={() => setViewMode('week')}
            className={`px-4 py-2 rounded-md transition-colors ${
              viewMode === 'week'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Week View
          </button>
          <button
            onClick={exportToPDF}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            📄 Export PDF
          </button>
          <button
            onClick={exportToPNG}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
          >
            🖼️ Export PNG
          </button>
        </div>
      </div>

      {/* Level Selection Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Client:
            </label>
            <select
              value={selectedClientId}
              onChange={(e) => {
                setSelectedClientId(e.target.value)
                // Reset dependent selections when client changes
                setSelectedProgramId('')
                setSelectedProjectId('')
                setSelectedUseCaseId('')
                setSelectedUserStoryId('')
                setSelectedTaskId('')
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Client...</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration at level?
            </label>
            <select
              value={selectedDurationLevel}
              onChange={(e) => {
                const newLevel = e.target.value as DurationLevel
                console.log('🎯 Duration level changed to:', newLevel, 'User role:', currentUser?.role)
                console.log('🎯 Available levels:', availableDurationLevels)
                setSelectedDurationLevel(newLevel)
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {availableDurationLevels.map(level => (
                <option key={level} value={level}>
                  {DURATION_LEVELS.find(dl => dl.value === level)?.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What level?
            </label>
            <select
              value={selectedLevel}
              onChange={(e) => {
                setSelectedLevel(e.target.value as HierarchyLevel)
                // Reset dependent hierarchy selections when level changes (but keep client)
                setSelectedProgramId('')
                setSelectedProjectId('')
                setSelectedUseCaseId('')
                setSelectedUserStoryId('')
                setSelectedTaskId('')
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {HIERARCHY_LEVELS.map(level => (
                <option key={level.value} value={level.value}>
                  {level.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            {/* Empty div to maintain grid layout */}
          </div>
        </div>

        {/* Hierarchy Selection Dropdowns */}
        <div className="flex items-center gap-3 flex-wrap">
          {selectedLevel === 'program' && selectedClientId && (
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700">Program:</span>
              <select
                value={selectedProgramId}
                onChange={(e) => setSelectedProgramId(e.target.value)}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Program...</option>
                {programs.map((program) => (
                  <option key={program.id} value={program.id}>
                    {program.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {selectedLevel === 'project' && selectedClientId && (
            <>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Program:</span>
                <select
                  value={selectedProgramId}
                  onChange={(e) => setSelectedProgramId(e.target.value)}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Program...</option>
                  {programs.map((program) => (
                    <option key={program.id} value={program.id}>
                      {program.name}
                    </option>
                  ))}
                </select>
              </div>
              {selectedProgramId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Project:</span>
                    <select
                      value={selectedProjectId}
                      onChange={(e) => setSelectedProjectId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Project...</option>
                      {projects.map((project) => (
                        <option key={project.id} value={project.id}>
                          {project.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
            </>
          )}

          {selectedLevel === 'usecase' && selectedClientId && (
            <>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Program:</span>
                <select
                  value={selectedProgramId}
                  onChange={(e) => setSelectedProgramId(e.target.value)}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Program...</option>
                  {programs.map((program) => (
                    <option key={program.id} value={program.id}>
                      {program.name}
                    </option>
                  ))}
                </select>
              </div>
              {selectedProgramId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Project:</span>
                    <select
                      value={selectedProjectId}
                      onChange={(e) => setSelectedProjectId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Project...</option>
                      {projects.map((project) => (
                        <option key={project.id} value={project.id}>
                          {project.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
              {selectedProjectId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Use Case:</span>
                    <select
                      value={selectedUseCaseId}
                      onChange={(e) => setSelectedUseCaseId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Use Case...</option>
                      {usecases.map((usecase) => (
                        <option key={usecase.id} value={usecase.id}>
                          {usecase.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
            </>
          )}

          {selectedLevel === 'userstory' && selectedClientId && (
            <>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Program:</span>
                <select
                  value={selectedProgramId}
                  onChange={(e) => setSelectedProgramId(e.target.value)}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Program...</option>
                  {programs.map((program) => (
                    <option key={program.id} value={program.id}>
                      {program.name}
                    </option>
                  ))}
                </select>
              </div>
              {selectedProgramId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Project:</span>
                    <select
                      value={selectedProjectId}
                      onChange={(e) => setSelectedProjectId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Project...</option>
                      {projects.map((project) => (
                        <option key={project.id} value={project.id}>
                          {project.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
              {selectedProjectId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Use Case:</span>
                    <select
                      value={selectedUseCaseId}
                      onChange={(e) => setSelectedUseCaseId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Use Case...</option>
                      {usecases.map((usecase) => (
                        <option key={usecase.id} value={usecase.id}>
                          {usecase.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
              {selectedUseCaseId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">User Story:</span>
                    <select
                      value={selectedUserStoryId}
                      onChange={(e) => setSelectedUserStoryId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select User Story...</option>
                      {userstories.map((story) => (
                        <option key={story.id} value={story.id}>
                          {story.title || story.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
            </>
          )}

          {selectedLevel === 'task' && selectedClientId && (
            <>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Program:</span>
                <select
                  value={selectedProgramId}
                  onChange={(e) => setSelectedProgramId(e.target.value)}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Program...</option>
                  {programs.map((program) => (
                    <option key={program.id} value={program.id}>
                      {program.name}
                    </option>
                  ))}
                </select>
              </div>
              {selectedProgramId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Project:</span>
                    <select
                      value={selectedProjectId}
                      onChange={(e) => setSelectedProjectId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Project...</option>
                      {projects.map((project) => (
                        <option key={project.id} value={project.id}>
                          {project.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
              {selectedProjectId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Use Case:</span>
                    <select
                      value={selectedUseCaseId}
                      onChange={(e) => setSelectedUseCaseId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Use Case...</option>
                      {usecases.map((usecase) => (
                        <option key={usecase.id} value={usecase.id}>
                          {usecase.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
              {selectedUseCaseId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">User Story:</span>
                    <select
                      value={selectedUserStoryId}
                      onChange={(e) => setSelectedUserStoryId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select User Story...</option>
                      {userstories.map((story) => (
                        <option key={story.id} value={story.id}>
                          {story.title || story.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
              {selectedUserStoryId && (
                <>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Task:</span>
                    <select
                      value={selectedTaskId}
                      onChange={(e) => setSelectedTaskId(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Task...</option>
                      {tasks.map((task) => (
                        <option key={task.id} value={task.id}>
                          {task.title || task.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}
            </>
          )}
        </div>

        {/* Display selected entity info */}
        {isLevelSelected() && (
          <div className="mt-4 p-3 bg-blue-50 rounded-md">
            <p className="text-sm text-blue-800">
              <span className="font-medium">Viewing:</span> {getSelectedEntityName()} → 
              <span className="font-medium"> Duration Level:</span> {DURATION_LEVELS.find(dl => dl.value === selectedDurationLevel)?.label}
            </p>
          </div>
        )}
      </div>

      {/* Gantt Chart */}
      {isLevelSelected() ? (
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <div style={{ minWidth: '1200px' }}>
              {/* Timeline Header */}
              <div className="flex border-b-2 border-gray-300 bg-gray-50">
                {/* Task Name Column */}
                <div className="w-64 flex-shrink-0 border-r-2 border-gray-300">
                  <div className="px-4 py-3 font-semibold text-gray-700 border-b border-gray-200">
                    {DURATION_LEVELS.find(dl => dl.value === selectedDurationLevel)?.label || 'Item'} Name
                  </div>
                  <div className="px-4 py-2 text-xs font-medium text-gray-600 border-b border-gray-200">
                    Duration
                  </div>
                  <div className="px-4 py-2 text-xs font-medium text-gray-600 border-b border-gray-200">
                    Start
                  </div>
                  <div className="px-4 py-2 text-xs font-medium text-gray-600">
                    End
                  </div>
                </div>

                {/* Timeline Grid */}
                <div className="flex-1">
                  {/* Month Headers */}
                  <div className="flex border-b border-gray-200">
                    {timelineMonths.map((month, idx) => (
                      <div
                        key={idx}
                        className="flex-1 px-2 py-3 text-center font-semibold text-gray-700 border-r border-gray-200"
                        style={{ minWidth: `${month.weeks * 60}px` }}
                      >
                        {month.month} {month.year}
                      </div>
                    ))}
                  </div>

                  {/* Week Grid */}
                  <div className="flex border-b border-gray-200 bg-gray-50">
                    {timelineMonths.map((month, monthIdx) =>
                      Array.from({ length: month.weeks }).map((_, weekIdx) => (
                        <div
                          key={`${monthIdx}-${weekIdx}`}
                          className="flex-1 px-1 py-2 text-center text-xs text-gray-600 border-r border-gray-100"
                          style={{ minWidth: '60px' }}
                        >
                          W{weekIdx + 1}
                        </div>
                      ))
                    )}
                  </div>

                  {/* Day Grid (for week view) */}
                  {viewMode === 'week' && (
                    <div className="flex border-b border-gray-200 bg-gray-50">
                      {timelineMonths.map((month, monthIdx) =>
                        Array.from({ length: month.weeks * 7 }).map((_, dayIdx) => (
                          <div
                            key={`${monthIdx}-${dayIdx}`}
                            className="flex-1 px-1 py-1 text-center text-xs text-gray-500 border-r border-gray-100"
                            style={{ minWidth: '20px' }}
                          >
                            {['M', 'T', 'W', 'T', 'F', 'S', 'S'][dayIdx % 7]}
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Item Rows */}
              {items.map((item, itemIdx) => {
                const barStyle = getTaskBarStyle(item)
                const duration = item.endDate && item.startDate
                  ? Math.ceil((new Date(item.endDate).getTime() - new Date(item.startDate).getTime()) / (1000 * 60 * 60 * 24))
                  : 0

                return (
                  <div key={item.id} className={`flex ${itemIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                    {/* Item Info Column */}
                    <div className="w-64 flex-shrink-0 border-r border-gray-200">
                      <div className="px-4 py-3 border-b border-gray-100">
                        <div className="font-medium text-sm text-gray-900 truncate" title={item.name || item.title}>
                          {item.name || item.title}
                        </div>
                        {item.assignedToName && (
                          <div className="text-xs text-gray-500 mt-1">{item.assignedToName}</div>
                        )}
                      </div>
                      <div className="px-4 py-2 text-xs text-gray-600 border-b border-gray-100">
                        {duration} days
                      </div>
                      <div className="px-4 py-2 text-xs text-gray-600 border-b border-gray-100">
                        {item.startDate ? new Date(item.startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '-'}
                      </div>
                      <div className="px-4 py-2 text-xs text-gray-600">
                        {item.endDate ? new Date(item.endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '-'}
                      </div>
                    </div>

                    {/* Timeline Grid with Item Bar */}
                    <div className="flex-1 relative" style={{ height: '80px' }}>
                      {/* Grid Lines */}
                      <div className="absolute inset-0 flex">
                        {timelineMonths.map((month, monthIdx) =>
                          Array.from({ length: month.weeks }).map((_, weekIdx) => (
                            <div
                              key={`${monthIdx}-${weekIdx}`}
                              className="flex-1 border-r border-gray-100"
                              style={{ minWidth: '60px' }}
                            />
                          ))
                        )}
                      </div>

                      {/* Item Bar */}
                      <div
                        className="absolute top-1/2 transform -translate-y-1/2 h-8 rounded shadow-md flex items-center px-2 cursor-pointer hover:shadow-lg transition-shadow"
                        style={{
                          ...barStyle,
                          backgroundColor: getStatusColor(item.status),
                          minWidth: '40px'
                        }}
                        title={`${item.name || item.title}\n${item.startDate} - ${item.endDate}\nStatus: ${item.status}`}
                      >
                        <span className="text-xs font-medium text-white truncate">
                          {item.name || item.title}
                        </span>
                        {item.progress !== undefined && (
                          <span className="ml-auto text-xs text-white font-semibold">
                            {item.progress}%
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Legend */}
          <div className="border-t border-gray-200 bg-gray-50 px-6 py-4">
            <div className="flex items-center gap-6 text-sm">
              <span className="font-medium text-gray-700">Status:</span>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#94a3b8' }}></div>
                <span className="text-gray-600">To Do</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#3b82f6' }}></div>
                <span className="text-gray-600">In Progress</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#22c55e' }}></div>
                <span className="text-gray-600">Done</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ef4444' }}></div>
                <span className="text-gray-600">Blocked</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow mt-6">
          <p className="text-gray-500">Please select a {HIERARCHY_LEVELS.find(hl => hl.value === selectedLevel)?.label || 'level'} to view the Gantt chart</p>
        </div>
      )}

      {isLevelSelected() && items.length === 0 && !loading && (
        <div className="text-center py-12 bg-white rounded-lg shadow mt-6">
          <p className="text-gray-500">No {DURATION_LEVELS.find(dl => dl.value === selectedDurationLevel)?.label?.toLowerCase() || 'items'} available to display in Gantt chart</p>
        </div>
      )}
    </div>
  )
}
