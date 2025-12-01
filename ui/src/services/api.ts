import axios from 'axios'
import { apiConfig, endpoints } from '../config/api.config'

// Toggle between dummy data and real API
const USE_DUMMY_DATA = false // Set to true for dummy data, false for real API

// Helper function to transform API response from snake_case to camelCase
const transformUser = (user: any) => {
  if (!user) return null
  return {
    id: user.id,
    email: user.email,
    fullName: user.full_name,
    role: user.role,
    clientId: user.client_id,
    theme: user.theme || 'snow',
    language: user.language || 'en',
    isActive: user.is_active
  }
}

// Helper function to transform use case from snake_case to camelCase
const transformUseCase = (usecase: any) => {
  if (!usecase || typeof usecase !== 'object') {
    console.warn('transformUseCase: Invalid usecase data', usecase)
    return null
  }
  
  try {
    return {
      id: usecase.id || null,
      name: usecase.name || '',
      projectId: usecase.project_id || usecase.projectId || null,
      status: usecase.status || 'Draft',
      priority: usecase.priority || 'Medium',
      shortDescription: usecase.short_description || usecase.shortDescription || null,
      longDescription: usecase.long_description || usecase.longDescription || null,
      description: usecase.short_description || usecase.shortDescription || usecase.description || null, // For backward compatibility
      createdAt: usecase.created_at || usecase.createdAt || null,
      updatedAt: usecase.updated_at || usecase.updatedAt || null
    }
  } catch (error) {
    console.error('Error transforming usecase:', error, usecase)
    return null
  }
}

// Helper function to transform project from snake_case to camelCase
const transformProject = (project: any) => {
  if (!project || typeof project !== 'object') {
    console.warn('transformProject: Invalid project data', project)
    return null
  }
  // Format date from YYYY-MM-DD to MM/DD/YYYY
  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return null
    try {
      const date = new Date(dateStr)
      if (isNaN(date.getTime())) return dateStr
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const year = date.getFullYear()
      return `${month}/${day}/${year}`
    } catch {
      return dateStr
    }
  }
  
  try {
    return {
      id: project.id || null,
      name: project.name || '',
      programId: project.program_id || project.programId || null,
      programName: project.program_name || project.programName || null,
      startDate: formatDate(project.start_date || project.startDate),
      endDate: formatDate(project.end_date || project.endDate),
      status: project.status || 'Planning',
      description: project.short_description || project.long_description || project.description || null,
      shortDescription: project.short_description || project.shortDescription || null,
      longDescription: project.long_description || project.longDescription || null,
      repositoryUrl: project.repository_url || project.repositoryUrl || null,
      createdAt: project.created_at || project.createdAt || null,
      updatedAt: project.updated_at || project.updatedAt || null,
      progress: project.progress || 0,
      sprint_length_weeks: project.sprint_length_weeks || project.sprintLengthWeeks || '2',
      sprint_starting_day: project.sprint_starting_day || project.sprintStartingDay || 'Monday'
    }
  } catch (error) {
    console.error('Error transforming project:', error, project)
    return null
  }
}

// Axios instance with config - no dummy data, all real API calls
const apiClient = axios.create(apiConfig)

// Add auth token to requests
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  const fullUrl = config.baseURL + config.url
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    console.log('Adding auth token to request:', fullUrl, 'Token:', token.substring(0, 20) + '...')
  } else {
    console.log('No token found for request:', fullUrl)
  }
  return config
})

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.log('API Error:', error.config?.url, 'Status:', error.response?.status, 'Message:', error.response?.data)
    
    // Only redirect to login for 401 on auth endpoints
    // For other endpoints, let the component handle the error
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      console.log('401 Unauthorized for:', url)
      
      // Only redirect if it's an auth-related endpoint
      if (url.includes('/auth/me') || url.includes('/auth/login')) {
        console.log('Auth endpoint failed - redirecting to login and clearing token')
        localStorage.removeItem('token')
        window.location.href = '/login'
      } else {
        console.log('Non-auth endpoint failed with 401 - not redirecting, letting component handle it')
      }
    }
    
    // Handle 403 Forbidden - show access denied message
    if (error.response?.status === 403) {
      console.error('Access denied:', error.response.data)
    }
    
    // Don't redirect on network errors (ERR_CONNECTION_REFUSED, etc.)
    // Let the component handle these errors
    
    return Promise.reject(error)
  }
)

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

const api = {
  // Auth
  async login(email: string, password: string) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return {
        token: 'dummy-jwt-token-' + Date.now(),
        user: dummyUser
      }
    }
    const response = await apiClient.post('/auth/login', { email, password })
    return {
      token: response.data.access_token,
      user: transformUser(response.data.user)
    }
  },

  async getCurrentUser() {
    if (USE_DUMMY_DATA) {
      await delay(300)
      return dummyUser
    }
    const response = await apiClient.get('/auth/me')
    return transformUser(response.data)
  },

  // Generic Entity Operations
  async getEntity(type: string, id: string) {
    if (USE_DUMMY_DATA) {
      await delay(300)
      // Return dummy data based on type
      const dummyData: any = {
        client: dummyClients,
        project: dummyProjects,
        task: dummyTasks
      }
      return dummyData[type]?.find((item: any) => item.id === id) || null
    }
    const endpoint = this.getEntityEndpoint(type)
    const response = await apiClient.get(`${endpoint}/${id}`)
    return response.data
  },

  // Helper function to get the correct endpoint path for entity types
  getEntityEndpoint(type: string): string {
    // Special cases for entity types that don't follow standard pluralization
    const endpointMap: Record<string, string> = {
      'userstory': '/user-stories',
      'user_story': '/user-stories'
    }
    
    if (endpointMap[type]) {
      return endpointMap[type]
    }
    
    // Standard pluralization: add 's' to the end
    return `/${type}s`
  },

  async getEntityList(type: string, filters?: Record<string, any>) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      const dummyData: any = {
        client: dummyClients,
        program: dummyPrograms,
        project: dummyProjects,
        usecase: dummyUseCases,
        task: dummyTasks,
        bug: dummyBugs,
        user: dummyUsers
      }
      return dummyData[type] || []
    }
    const endpoint = this.getEntityEndpoint(type)
    const response = await apiClient.get(`${endpoint}/`, { params: filters })
    if (!Array.isArray(response.data)) {
      return []
    }
    // Transform usecases to camelCase
    if (type === 'usecase') {
      return response.data.map((uc: any) => transformUseCase(uc)).filter((uc: any) => uc !== null)
    }
    return response.data
  },

  async createEntity(type: string, data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      const newEntity = { 
        id: `${type}-${Date.now()}`, 
        ...data,
        created_at: new Date().toISOString()
      }
      
      // Add to the appropriate dummy array
      if (type === 'program') {
        dummyPrograms.push(newEntity)
      } else if (type === 'project') {
        dummyProjects.push(newEntity)
      } else if (type === 'usecase') {
        dummyUseCases.push(newEntity)
      } else if (type === 'task') {
        dummyTasks.push(newEntity)
      } else if (type === 'bug') {
        dummyBugs.push(newEntity)
      }
      
      return newEntity
    }
    const endpoint = this.getEntityEndpoint(type)
    const response = await apiClient.post(`${endpoint}/`, data)
    return response.data
  },

  async updateEntity(type: string, id: string, data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      
      // Find and update in the appropriate dummy array
      let targetArray: any[] = []
      if (type === 'program') targetArray = dummyPrograms
      else if (type === 'project') targetArray = dummyProjects
      else if (type === 'usecase') targetArray = dummyUseCases
      else if (type === 'task') targetArray = dummyTasks
      else if (type === 'bug') targetArray = dummyBugs
      
      const index = targetArray.findIndex(item => item.id === id)
      if (index !== -1) {
        targetArray[index] = { ...targetArray[index], ...data, updated_at: new Date().toISOString() }
        return targetArray[index]
      }
      
      return { id, ...data }
    }
    const endpoint = this.getEntityEndpoint(type)
    const response = await apiClient.put(`${endpoint}/${id}`, data)
    return response.data
  },

  async deleteEntity(type: string, id: string) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { success: true }
    }
    const endpoint = this.getEntityEndpoint(type)
    const response = await apiClient.delete(`${endpoint}/${id}`)
    return response.data
  },

  async getEntityWithContext(type: string, id: string) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      const entity = await api.getEntity(type, id)
      
      // Mock parent and children based on type
      let parent = null
      let children: any[] = []
      let breadcrumb: any[] = []
      
      if (type === 'project') {
        parent = dummyPrograms.find(p => p.id === entity?.programId)
        children = dummyUseCases.filter(uc => uc.project_id === id)
        breadcrumb = [
          { id: 'client-1', name: 'DataLegos', type: 'client' },
          { id: parent?.id, name: parent?.name, type: 'program' },
          { id: entity?.id, name: entity?.name, type: 'project' }
        ]
      }
      
      return {
        entity,
        parent,
        children,
        breadcrumb
      }
    }
    
    try {
      const response = await apiClient.get(`/hierarchy/${type}/${id}`)
      return response.data
    } catch (error: any) {
      // If the hierarchy endpoint fails, fall back to basic entity fetch
      console.warn(`Hierarchy endpoint failed for ${type}/${id}, falling back to basic fetch`, error)
      
      try {
        const entity = await api.getEntity(type, id)
        
        // Build basic context without parent/children
        return {
          entity,
          parent: null,
          children: [],
          breadcrumb: [
            { id: entity.id, name: entity.name || entity.title, type }
          ]
        }
      } catch (fallbackError) {
        console.error(`Failed to fetch entity ${type}/${id}:`, fallbackError)
        throw fallbackError
      }
    }
  },

  async getEntityStatistics(type: string, id: string) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      if (type === 'project') {
        return {
          total_usecases: 8,
          usecases_in_development: 3,
          usecases_in_testing: 2,
          usecases_completed: 3,
          total_user_stories: 24,
          total_tasks: 67,
          completion_percentage: 45
        }
      }
      if (type === 'usecase') {
        return {
          total_user_stories: 6,
          user_stories_in_progress: 2,
          user_stories_in_testing: 1,
          user_stories_completed: 3,
          total_tasks: 18,
          completion_percentage: 50
        }
      }
      return {
        status_counts: {
          'To Do': 5,
          'In Progress': 3,
          'Done': 12
        },
        phase_distribution: [
          { phase: 'Development', count: 8 },
          { phase: 'Testing', count: 6 },
          { phase: 'Design', count: 4 },
          { phase: 'Analysis', count: 2 }
        ],
        completion_percentage: 60,
        rollup_counts: {
          tasks: 20,
          subtasks: 45,
          bugs: 3
        }
      }
    }
    const response = await apiClient.get(`/hierarchy/${type}/${id}/statistics`)
    return response.data
  },

  async searchEntities(query: string, types?: string[]) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      const allEntities = [
        ...dummyProjects.map(p => ({ ...p, type: 'project', displayName: p.name })),
        ...dummyTasks.map(t => ({ ...t, type: 'task', displayName: t.title }))
      ]
      return allEntities.filter(e => 
        e.displayName?.toLowerCase().includes(query.toLowerCase()) ||
        (e as any).description?.toLowerCase().includes(query.toLowerCase())
      )
    }
    const response = await apiClient.get('/hierarchy/search', { 
      params: { q: query, entity_types: types?.join(',') } 
    })
    return response.data
  },

  // Clients
  async getClients() {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return dummyClients
    }
    const response = await apiClient.get('/clients/')
    // The clients endpoint returns paginated data with a 'clients' property
    return response.data.clients || response.data
  },

  async getClient(id: string) {
    if (USE_DUMMY_DATA) {
      await delay(300)
      return dummyClients.find(c => c.id === id)
    }
    const response = await apiClient.get(`/clients/${id}`)
    return response.data
  },

  async getClientStatistics() {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return {
        total_clients: 3,
        clients_with_ongoing_projects: 2,
        clients_with_no_projects: 0,
        total_projects_across_clients: 5,
        total_ongoing_projects: 3,
        clients: [
          {
            id: 'client-1',
            name: 'DataLegos',
            description: 'Internal projects',
            industry: 'Technology',
            contact_email: 'contact@datalegos.com',
            contact_phone: '+1-555-0100',
            is_active: true,
            total_projects: 2,
            ongoing_projects: 2,
            completed_projects: 0,
            latest_project: {
              id: 'proj-1',
              name: 'Worky Platform',
              status: 'In Progress',
              created_at: '2025-01-01T00:00:00'
            },
            created_at: '2024-01-01T00:00:00',
            updated_at: '2025-01-10T00:00:00'
          },
          {
            id: 'client-2',
            name: 'Acme Corp',
            description: 'Enterprise client',
            industry: 'Manufacturing',
            contact_email: 'info@acmecorp.com',
            contact_phone: '+1-555-0200',
            is_active: true,
            total_projects: 2,
            ongoing_projects: 1,
            completed_projects: 1,
            latest_project: {
              id: 'proj-3',
              name: 'Mobile App',
              status: 'In Progress',
              created_at: '2024-11-01T00:00:00'
            },
            created_at: '2024-03-15T00:00:00',
            updated_at: '2025-01-08T00:00:00'
          },
          {
            id: 'client-3',
            name: 'TechStart Inc',
            description: 'Startup client',
            industry: 'SaaS',
            contact_email: 'hello@techstart.io',
            contact_phone: '+1-555-0300',
            is_active: true,
            total_projects: 1,
            ongoing_projects: 0,
            completed_projects: 1,
            latest_project: {
              id: 'proj-4',
              name: 'Website Redesign',
              status: 'Completed',
              created_at: '2024-09-01T00:00:00'
            },
            created_at: '2024-06-20T00:00:00',
            updated_at: '2024-12-15T00:00:00'
          }
        ]
      }
    }
    const response = await apiClient.get('/clients/statistics/dashboard')
    return response.data
  },

  async createClient(data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { id: 'client-' + Date.now(), ...data, isActive: true }
    }
    const response = await apiClient.post('/clients/', data)
    return response.data
  },

  async updateClient(id: string, data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { id, ...data }
    }
    const response = await apiClient.put(`/clients/${id}`, data)
    return response.data
  },

  // Projects
  async getProjects() {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return dummyProjects
    }
    const response = await apiClient.get('/projects/')
    if (!Array.isArray(response.data)) {
      console.error('Projects API returned non-array response:', response.data)
      return []
    }
    const transformed = response.data.map((p: any) => transformProject(p)).filter((p: any) => p !== null)
    return transformed
  },

  async getProject(id: string) {
    if (USE_DUMMY_DATA) {
      await delay(300)
      return dummyProjects.find(p => p.id === id)
    }
    const response = await apiClient.get(`/projects/${id}`)
    return transformProject(response.data)
  },

  async createProject(data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { id: 'proj-' + Date.now(), ...data }
    }
    const response = await apiClient.post('/projects/', data)
    return response.data
  },

  async updateProject(id: string, data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { id, ...data }
    }
    const response = await apiClient.put(`/projects/${id}`, data)
    return transformProject(response.data)
  },

  // Tasks
  async getTasks(projectId?: string) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return projectId 
        ? dummyTasks.filter(t => t.projectId === projectId)
        : dummyTasks
    }
    const response = await apiClient.get('/tasks/', { params: { projectId } })
    return response.data
  },

  async getTask(id: string) {
    if (USE_DUMMY_DATA) {
      await delay(300)
      return dummyTasks.find(t => t.id === id)
    }
    const response = await apiClient.get(`/tasks/${id}`)
    return response.data
  },

  async createTask(data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { id: 'task-' + Date.now(), ...data, progress: 0 }
    }
    const response = await apiClient.post('/tasks/', data)
    return response.data
  },

  async updateTask(id: string, data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { id, ...data }
    }
    const response = await apiClient.put(`/tasks/${id}`, data)
    return response.data
  },

  // Bugs
  async getBugs(projectId?: string) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return projectId
        ? dummyBugs.filter(b => b.projectId === projectId)
        : dummyBugs
    }
    const response = await apiClient.get('/bugs/', { params: { projectId } })
    return response.data
  },

  async createBug(data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { id: 'bug-' + Date.now(), ...data, createdAt: new Date().toISOString() }
    }
    const response = await apiClient.post('/bugs/', data)
    return response.data
  },

  // Users
  async getUsers() {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return dummyUsers
    }
    const response = await apiClient.get('/users/')
    return response.data
  },

  async updateUserPreferences(data: any) {
    if (USE_DUMMY_DATA) {
      await delay(300)
      return { ...dummyUser, ...data }
    }
    const response = await apiClient.put('/users/me/preferences', data)
    return response.data
  },

  // Phase Management
  async getPhases(includeInactive = false) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      const phases = [
        { id: 'phase-1', name: 'Development', description: 'Development work', color: '#3498db', isActive: true, displayOrder: 1 },
        { id: 'phase-2', name: 'Analysis', description: 'Analysis and planning', color: '#9b59b6', isActive: true, displayOrder: 2 },
        { id: 'phase-3', name: 'Design', description: 'Design and architecture', color: '#e67e22', isActive: true, displayOrder: 3 },
        { id: 'phase-4', name: 'Testing', description: 'Testing and QA', color: '#1abc9c', isActive: true, displayOrder: 4 }
      ]
      return includeInactive ? phases : phases.filter(p => p.isActive)
    }
    const response = await apiClient.get('/phases/', { params: { include_inactive: includeInactive } })
    // Transform snake_case to camelCase
    return response.data.map((phase: any) => ({
      id: phase.id,
      name: phase.name,
      description: phase.short_description || phase.description || '',
      color: phase.color,
      isActive: phase.is_active,
      displayOrder: phase.order
    }))
  },

  async getPhase(id: string) {
    if (USE_DUMMY_DATA) {
      await delay(300)
      const phases = await api.getPhases(true)
      return phases.find((p: any) => p.id === id)
    }
    const response = await apiClient.get(`/phases/${id}`)
    return response.data
  },

  async createPhase(data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { id: 'phase-' + Date.now(), ...data, isActive: true }
    }
    // Transform camelCase to snake_case for API
    const apiData = {
      name: data.name,
      short_description: data.description,
      color: data.color,
      is_active: data.isActive,
      order: data.displayOrder
    }
    const response = await apiClient.post('/phases/', apiData)
    return response.data
  },

  async updatePhase(id: string, data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { id, ...data }
    }
    // Transform camelCase to snake_case for API
    const apiData = {
      name: data.name,
      short_description: data.description,
      color: data.color,
      is_active: data.isActive,
      order: data.displayOrder
    }
    const response = await apiClient.put(`/phases/${id}`, apiData)
    return response.data
  },

  async deactivatePhase(id: string) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return { success: true }
    }
    const response = await apiClient.post(`/phases/${id}/deactivate`)
    return response.data
  },

  async getPhaseUsage(id: string) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return {
        totalCount: 25,
        taskCount: 15,
        subtaskCount: 10,
        taskStatusBreakdown: {
          'To Do': 5,
          'In Progress': 7,
          'Done': 3
        },
        subtaskStatusBreakdown: {
          'To Do': 3,
          'In Progress': 4,
          'Done': 3
        }
      }
    }
    const response = await apiClient.get(`/phases/${id}/usage`)
    // Transform the response
    const data = response.data
    return {
      totalCount: data.usage?.total_count || 0,
      taskCount: data.usage?.task_count || 0,
      subtaskCount: data.usage?.subtask_count || 0,
      taskStatusBreakdown: data.usage?.task_status_breakdown || {},
      subtaskStatusBreakdown: data.usage?.subtask_status_breakdown || {}
    }
  },

  // Programs
  async getPrograms(clientId?: string) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return [
        { id: 'prog-1', name: 'Internal Tools', clientId: 'client-1', status: 'Active' },
        { id: 'prog-2', name: 'Customer Solutions', clientId: 'client-1', status: 'Active' }
      ]
    }
    const response = await apiClient.get('/programs', { params: { client_id: clientId } })
    return response.data
  },

  async getProgram(id: string) {
    if (USE_DUMMY_DATA) {
      await delay(300)
      const programs = await api.getPrograms()
      return programs.find((p: any) => p.id === id)
    }
    const response = await apiClient.get(`/programs/${id}`)
    return response.data
  },

  // Use Cases
  async getUseCases(projectId?: string) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return [
        { id: 'uc-1', name: 'User Authentication', projectId: 'proj-1', status: 'In Progress', priority: 'High' },
        { id: 'uc-2', name: 'Task Management', projectId: 'proj-1', status: 'Planning', priority: 'High' }
      ]
    }
    const response = await apiClient.get('/usecases', { params: { project_id: projectId } })
    if (!Array.isArray(response.data)) {
      console.error('UseCases API returned non-array response:', response.data)
      return []
    }
    return response.data.map((uc: any) => transformUseCase(uc)).filter((uc: any) => uc !== null)
  },

  // User Stories
  async getUserStories(usecaseId?: string) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return [
        { id: 'us-1', name: 'As a user, I want to login', usecaseId: 'uc-1', status: 'In Progress', priority: 'High' },
        { id: 'us-2', name: 'As a user, I want to reset password', usecaseId: 'uc-1', status: 'To Do', priority: 'Medium' }
      ]
    }
    const response = await apiClient.get('/user-stories', { params: { usecase_id: usecaseId } })
    return response.data
  },

  // Subtasks
  async getSubtasks(taskId?: string) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return [
        { id: 'st-1', name: 'Write unit tests', taskId: 'task-1', status: 'Done', phaseId: 'phase-4' },
        { id: 'st-2', name: 'Code review', taskId: 'task-1', status: 'Done', phaseId: 'phase-1' }
      ]
    }
    const response = await apiClient.get('/subtasks', { params: { task_id: taskId } })
    return response.data
  },

  // Bug Management - Additional methods
  async getBug(id: string) {
    if (USE_DUMMY_DATA) {
      await delay(300)
      return dummyBugs.find(b => b.id === id)
    }
    const response = await apiClient.get(`/bugs/${id}`)
    return response.data
  },

  async updateBug(id: string, data: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      const index = dummyBugs.findIndex(b => b.id === id)
      if (index !== -1) {
        dummyBugs[index] = { ...dummyBugs[index], ...data }
        return dummyBugs[index]
      }
      return { id, ...data }
    }
    const response = await apiClient.put(`/bugs/${id}`, data)
    return response.data
  },

  async assignBug(id: string, assigneeId: string) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return api.updateBug(id, { assignedTo: assigneeId, status: 'Assigned' })
    }
    const response = await apiClient.post(`/bugs/${id}/assign`, { assignee_id: assigneeId })
    return response.data
  },

  async resolveBug(id: string, resolutionNotes: string) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      return api.updateBug(id, { 
        status: 'Resolved', 
        resolutionNotes,
        resolvedAt: new Date().toISOString()
      })
    }
    const response = await apiClient.post(`/bugs/${id}/resolve`, { resolution_notes: resolutionNotes })
    return response.data
  },

  // Sprint Operations
  async getProjectSprints(projectId: string, includePast: boolean = false) {
    const response = await apiClient.get(`/projects/${projectId}/sprints`, {
      params: { include_past: includePast }
    })
    return response.data
  },

  async getSprint(sprintId: string) {
    const response = await apiClient.get(`/sprints/${sprintId}`)
    return response.data
  },

  async getSprintTasks(sprintId: string) {
    const response = await apiClient.get(`/sprints/${sprintId}/tasks`)
    return response.data
  },

  async assignTaskToSprint(sprintId: string, taskId: string) {
    const response = await apiClient.post(`/sprints/${sprintId}/assign-task/${taskId}`)
    return response.data
  },

  async unassignTaskFromSprint(sprintId: string, taskId: string) {
    const response = await apiClient.delete(`/sprints/${sprintId}/unassign-task/${taskId}`)
    return response.data
  },

  async createSprint(data: any) {
    const response = await apiClient.post('/sprints', data)
    return response.data
  },

  async updateSprint(sprintId: string, data: any) {
    const response = await apiClient.put(`/sprints/${sprintId}`, data)
    return response.data
  },

  async deleteSprint(sprintId: string) {
    await apiClient.delete(`/sprints/${sprintId}`)
  },

  async getDefaultSprintDates(projectId: string) {
    const response = await apiClient.get(`/projects/${projectId}/sprint-default-dates`)
    return response.data
  },

  // Audit Logs
  async getAuditLogs(entityType: string, entityId: string, filters?: any) {
    if (USE_DUMMY_DATA) {
      await delay(500)
      
      // Generate dummy audit logs
      const dummyAuditLogs = [
        {
          id: 'audit-1',
          user_id: 'user-1',
          user_name: 'John Doe',
          action: 'CREATE',
          entity_type: entityType,
          entity_id: entityId,
          changes: null,
          created_at: '2025-01-10T10:30:00Z',
          ip_address: '192.168.1.100',
          user_agent: 'Mozilla/5.0'
        },
        {
          id: 'audit-2',
          user_id: 'user-2',
          user_name: 'Jane Smith',
          action: 'UPDATE',
          entity_type: entityType,
          entity_id: entityId,
          changes: {
            status: { old: 'To Do', new: 'In Progress' },
            assigned_to: { old: null, new: 'user-2' }
          },
          created_at: '2025-01-11T14:20:00Z',
          ip_address: '192.168.1.101',
          user_agent: 'Mozilla/5.0'
        },
        {
          id: 'audit-3',
          user_id: 'user-2',
          user_name: 'Jane Smith',
          action: 'UPDATE',
          entity_type: entityType,
          entity_id: entityId,
          changes: {
            description: { 
              old: 'Initial description', 
              new: 'Updated description with more details' 
            }
          },
          created_at: '2025-01-12T09:15:00Z',
          ip_address: '192.168.1.101',
          user_agent: 'Mozilla/5.0'
        },
        {
          id: 'audit-4',
          user_id: 'user-3',
          user_name: 'Bob Johnson',
          action: 'VIEW',
          entity_type: entityType,
          entity_id: entityId,
          changes: null,
          created_at: '2025-01-12T11:45:00Z',
          ip_address: '192.168.1.102',
          user_agent: 'Mozilla/5.0'
        },
        {
          id: 'audit-5',
          user_id: 'user-1',
          user_name: 'John Doe',
          action: 'UPDATE',
          entity_type: entityType,
          entity_id: entityId,
          changes: {
            status: { old: 'In Progress', new: 'Done' },
            completed_at: { old: null, new: '2025-01-13T16:30:00Z' }
          },
          created_at: '2025-01-13T16:30:00Z',
          ip_address: '192.168.1.100',
          user_agent: 'Mozilla/5.0'
        }
      ]
      
      // Apply filters
      let filteredLogs = [...dummyAuditLogs]
      
      if (filters?.action) {
        filteredLogs = filteredLogs.filter(log => log.action === filters.action)
      }
      
      if (filters?.date_from) {
        const fromDate = new Date(filters.date_from)
        filteredLogs = filteredLogs.filter(log => new Date(log.created_at) >= fromDate)
      }
      
      if (filters?.date_to) {
        const toDate = new Date(filters.date_to)
        toDate.setHours(23, 59, 59, 999) // End of day
        filteredLogs = filteredLogs.filter(log => new Date(log.created_at) <= toDate)
      }
      
      // Sort by created_at descending (newest first)
      filteredLogs.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      
      // Pagination
      const page = filters?.page || 1
      const pageSize = filters?.page_size || 100
      const startIndex = (page - 1) * pageSize
      const endIndex = startIndex + pageSize
      const paginatedLogs = filteredLogs.slice(startIndex, endIndex)
      
      return {
        items: paginatedLogs,
        total: filteredLogs.length,
        page: page,
        page_size: pageSize,
        has_more: endIndex < filteredLogs.length
      }
    }
    
    const response = await apiClient.get(`/audit-logs/${entityType}/${entityId}`, { 
      params: filters 
    })
    return response.data
  },

  // Generic HTTP methods for direct API access
  async get(url: string, config?: any) {
    // Handle notes endpoint in dummy mode
    if (USE_DUMMY_DATA && url.includes('/notes')) {
      await delay(300)
      // Extract entity key from URL (e.g., "client/client-1")
      const match = url.match(/hierarchy\/([^\/]+)\/([^\/]+)\/notes/)
      if (match) {
        const entityKey = `${match[1]}-${match[2]}`
        return dummyNotes[entityKey] || []
      }
      return []
    }
    
    try {
      const response = await apiClient.get(url, config)
      return response.data
    } catch (error: any) {
      // For notes endpoints, don't let 401 trigger redirect
      if (url.includes('/notes') && error.response?.status === 401) {
        throw error // Re-throw but interceptor won't redirect
      }
      throw error
    }
  },

  async post(url: string, data?: any, config?: any) {
    // Handle notes endpoint in dummy mode
    if (USE_DUMMY_DATA && url.includes('/notes')) {
      await delay(300)
      return {
        id: 'note-' + Date.now(),
        entity_type: 'Client',
        entity_id: 'client-1',
        note_text: data.note_text,
        created_by: '1',
        created_at: new Date().toISOString(),
        creator_name: 'Admin User',
        creator_email: 'admin@datalegos.com'
      }
    }
    
    const response = await apiClient.post(url, data, config)
    return response.data
  },

  async put(url: string, data?: any, config?: any) {
    const response = await apiClient.put(url, data, config)
    return response.data
  },

  async delete(url: string, config?: any) {
    const response = await apiClient.delete(url, config)
    return response.data
  },

  // QA Metrics
  async getBugSummaryMetrics(hierarchyFilter?: any) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return {
        total_bugs: 127,
        open_bugs: 45,
        closed_bugs: 82,
        resolution_rate: 64.6,
        average_resolution_time: 5.2,
        by_severity: {
          'Blocker': 3,
          'Critical': 12,
          'Major': 35,
          'Minor': 52,
          'Trivial': 25
        },
        by_priority: {
          'P0 (Critical)': 8,
          'P1 (High)': 28,
          'P2 (Medium)': 61,
          'P3 (Low)': 30
        },
        by_status: {
          'New': 12,
          'Open': 15,
          'In Progress': 18,
          'Fixed': 25,
          'Verified': 20,
          'Closed': 37
        }
      }
    }
    const response = await apiClient.get('/qa-metrics/bugs/summary', { params: hierarchyFilter })
    return response.data
  },

  async getBugTrends(startDate?: string, endDate?: string, hierarchyFilter?: any) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      const dates = []
      const created = []
      const resolved = []
      const today = new Date()
      
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(date.getDate() - i)
        dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))
        created.push(Math.floor(Math.random() * 10) + 5)
        resolved.push(Math.floor(Math.random() * 8) + 3)
      }
      
      return { dates, created, resolved }
    }
    const params = { ...hierarchyFilter, start_date: startDate, end_date: endDate }
    const response = await apiClient.get('/qa-metrics/bugs/trends', { params })
    return response.data
  },

  async getBugAgingReport(hierarchyFilter?: any) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return {
        age_ranges: [
          { range: '0-7 days', count: 28, percentage: 22.0 },
          { range: '8-30 days', count: 45, percentage: 35.4 },
          { range: '31-90 days', count: 38, percentage: 29.9 },
          { range: '90+ days', count: 16, percentage: 12.6 }
        ],
        average_age_by_severity: {
          'Blocker': 2.5,
          'Critical': 8.3,
          'Major': 25.7,
          'Minor': 42.1,
          'Trivial': 58.9
        }
      }
    }
    const response = await apiClient.get('/qa-metrics/bugs/aging', { params: hierarchyFilter })
    return response.data
  },

  async getTestExecutionMetrics(testRunId?: string, hierarchyFilter?: any) {
    if (USE_DUMMY_DATA) {
      await delay(400)
      return {
        total_executions: 245,
        passed: 180,
        failed: 45,
        blocked: 12,
        skipped: 8,
        pass_rate: 73.5,
        fail_rate: 18.4,
        execution_coverage: 82.3,
        total_test_cases: 150,
        executed_test_cases: 123
      }
    }
    const params = { ...hierarchyFilter, test_run_id: testRunId }
    const response = await apiClient.get('/qa-metrics/test-execution/summary', { params })
    return response.data
  },

  // Organization Operations
  async getOrganizations(isActive?: boolean) {
    const params = isActive !== undefined ? { is_active: isActive } : {}
    const response = await apiClient.get('/organizations/', { params })
    return response.data.organizations || []
  },

  async getOrganization(id: string) {
    const response = await apiClient.get(`/organizations/${id}`)
    return response.data
  },

  async createOrganization(data: any) {
    const response = await apiClient.post('/organizations/', data)
    return response.data
  },

  async updateOrganization(id: string, data: any) {
    const response = await apiClient.put(`/organizations/${id}`, data)
    return response.data
  },

  async deleteOrganization(id: string) {
    const response = await apiClient.delete(`/organizations/${id}`)
    return response.data
  }
}

export default api

// Export a typed API interface for better type safety
export interface HierarchyAPI {
  // Generic Entity Operations (Requirements: 11.1, 11.2, 11.3, 11.4, 11.5)
  getEntity: (type: string, id: string) => Promise<any>
  getEntityList: (type: string, filters?: Record<string, any>) => Promise<any[]>
  createEntity: (type: string, data: any) => Promise<any>
  updateEntity: (type: string, id: string, data: any) => Promise<any>
  deleteEntity: (type: string, id: string) => Promise<any>
  getEntityWithContext: (type: string, id: string) => Promise<any>
  getEntityStatistics: (type: string, id: string) => Promise<any>
  searchEntities: (query: string, types?: string[]) => Promise<any[]>
  
  // Client Operations
  getClients: () => Promise<any[]>
  getClient: (id: string) => Promise<any>
  getClientStatistics: () => Promise<any>
  createClient: (data: any) => Promise<any>
  updateClient: (id: string, data: any) => Promise<any>
  
  // Program Operations
  getPrograms: (clientId?: string) => Promise<any[]>
  getProgram: (id: string) => Promise<any>
  
  // Project Operations
  getProjects: () => Promise<any[]>
  getProject: (id: string) => Promise<any>
  createProject: (data: any) => Promise<any>
  updateProject: (id: string, data: any) => Promise<any>
  
  // Use Case Operations
  getUseCases: (projectId?: string) => Promise<any[]>
  
  // User Story Operations
  getUserStories: (usecaseId?: string) => Promise<any[]>
  
  // Task Operations
  getTasks: (projectId?: string) => Promise<any[]>
  getTask: (id: string) => Promise<any>
  createTask: (data: any) => Promise<any>
  updateTask: (id: string, data: any) => Promise<any>
  
  // Subtask Operations
  getSubtasks: (taskId?: string) => Promise<any[]>
  
  // Bug Operations
  getBugs: (projectId?: string) => Promise<any[]>
  getBug: (id: string) => Promise<any>
  createBug: (data: any) => Promise<any>
  updateBug: (id: string, data: any) => Promise<any>
  assignBug: (id: string, assigneeId: string) => Promise<any>
  resolveBug: (id: string, resolutionNotes: string) => Promise<any>
  
  // Phase Operations
  getPhases: (includeInactive?: boolean) => Promise<any[]>
  getPhase: (id: string) => Promise<any>
  createPhase: (data: any) => Promise<any>
  updatePhase: (id: string, data: any) => Promise<any>
  deactivatePhase: (id: string) => Promise<any>
  getPhaseUsage: (id: string) => Promise<any>
  
  // User Operations
  getUsers: () => Promise<any[]>
  getCurrentUser: () => Promise<any>
  updateUserPreferences: (data: any) => Promise<any>
  
  // Auth Operations
  login: (email: string, password: string) => Promise<any>
  
  // Audit Operations
  getAuditLogs: (entityType: string, entityId: string, filters?: any) => Promise<any>
}

// Ensure api conforms to the interface
export const typedApi: HierarchyAPI = api
