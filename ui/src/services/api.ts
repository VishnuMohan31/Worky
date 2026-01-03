import axios from 'axios'
import { apiConfig } from '../config/api.config'

// Real API calls only - dummy data removed for cleaner code

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

// Simple cache for API responses
const apiCache = new Map<string, { data: any; timestamp: number }>()
const CACHE_DURATION = 30000 // 30 seconds

// Debounce map for preventing duplicate requests
const pendingRequests = new Map<string, Promise<any>>()

// Helper function to get cached data or make request
const getCachedOrFetch = async <T>(cacheKey: string, fetchFn: () => Promise<T>): Promise<T> => {
  // Check cache first
  const cached = apiCache.get(cacheKey)
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data
  }

  // Check if request is already pending
  if (pendingRequests.has(cacheKey)) {
    return pendingRequests.get(cacheKey)
  }

  // Make new request
  const requestPromise = fetchFn().then(data => {
    // Cache the result
    apiCache.set(cacheKey, { data, timestamp: Date.now() })
    // Remove from pending
    pendingRequests.delete(cacheKey)
    return data
  }).catch(error => {
    // Remove from pending on error
    pendingRequests.delete(cacheKey)
    throw error
  })

  // Store pending request
  pendingRequests.set(cacheKey, requestPromise)
  return requestPromise
}

// Helper function to invalidate cache entries
const invalidateCache = (pattern: string) => {
  for (const key of apiCache.keys()) {
    if (key.includes(pattern)) {
      apiCache.delete(key)
    }
  }
}

// Axios instance with config - no dummy data, all real API calls
const apiClient = axios.create(apiConfig)

// Create a separate axios instance for safe API calls that don't trigger logout
const safeApiClient = axios.create(apiConfig)

// Add auth token to requests for both clients
const addAuthToken = (config: any) => {
  const token = localStorage.getItem('token')
  const fullUrl = config.baseURL + config.url
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    // Token added to request (logging removed for production security)
  } else {
    // No token found for request (logging removed for production)
  }
  return config
}

apiClient.interceptors.request.use(addAuthToken)
safeApiClient.interceptors.request.use(addAuthToken)

// Add response interceptor for error handling - MAIN CLIENT (with logout)
apiClient.interceptors.response.use(
  response => response,
  error => {
    // API Error logged (details removed for production security)
    
    // Redirect to login for any 401 error (unauthorized)
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      // 401 Unauthorized - redirecting to login
      localStorage.removeItem('token')
      window.location.href = '/login'
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

// Add response interceptor for SAFE CLIENT (no logout redirect)
safeApiClient.interceptors.response.use(
  response => response,
  error => {
    // Safe API Error (details removed for production)
    
    // Don't redirect to login for 401 errors - just log and reject
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      console.warn('401 Unauthorized for safe call:', url, '- NOT redirecting to login')
    }
    
    // Handle 403 Forbidden - show access denied message
    if (error.response?.status === 403) {
      console.error('Access denied:', error.response.data)
    }
    
    return Promise.reject(error)
  }
)

const api = {
  // Auth
  async login(email: string, password: string) {
    const response = await apiClient.post('/auth/login', { email, password })
    return {
      token: response.data.access_token,
      user: transformUser(response.data.user)
    }
  },

  async getCurrentUser() {
    const response = await apiClient.get('/auth/me')
    return transformUser(response.data)
  },

  // Generic Entity Operations
  async getEntity(type: string, id: string) {
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
    const endpoint = this.getEntityEndpoint(type)
    const response = await apiClient.post(`${endpoint}/`, data)
    return response.data
  },

  async updateEntity(type: string, id: string, data: any) {
    const endpoint = this.getEntityEndpoint(type)
    const response = await apiClient.put(`${endpoint}/${id}`, data)
    return response.data
  },

  async deleteEntity(type: string, id: string) {
    const endpoint = this.getEntityEndpoint(type)
    const response = await apiClient.delete(`${endpoint}/${id}`)
    return response.data
  },

  async getEntityWithContext(type: string, id: string) {
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
    const cacheKey = `statistics:${type}:${id}`
    
    return getCachedOrFetch(cacheKey, async () => {
      const response = await apiClient.get(`/hierarchy/${type}/${id}/statistics`)
      return response.data
    })
  },

  async searchEntities(query: string, types?: string[]) {
    const response = await apiClient.get('/hierarchy/search', { 
      params: { q: query, entity_types: types?.join(',') } 
    })
    return response.data
  },

  // Clients
  async getClients() {
    const response = await apiClient.get('/clients/')
    // The clients endpoint returns paginated data with a 'clients' property
    return response.data.clients || response.data
  },

  async getClient(id: string) {
    const response = await apiClient.get(`/clients/${id}`)
    return response.data
  },

  async getClientStatistics() {
    const response = await apiClient.get('/clients/statistics/dashboard')
    return response.data
  },

  async createClient(data: any) {
    const response = await apiClient.post('/clients/', data)
    return response.data
  },

  async updateClient(id: string, data: any) {
    const response = await apiClient.put(`/clients/${id}`, data)
    return response.data
  },

  // Projects
  async getProjects() {
    const response = await apiClient.get('/projects/')
    if (!Array.isArray(response.data)) {
      console.error('Projects API returned non-array response:', response.data)
      return []
    }
    const transformed = response.data.map((p: any) => transformProject(p)).filter((p: any) => p !== null)
    return transformed
  },

  async getProject(id: string) {
    const response = await apiClient.get(`/projects/${id}`)
    return transformProject(response.data)
  },

  async createProject(data: any) {
    const response = await apiClient.post('/projects/', data)
    return response.data
  },

  async updateProject(id: string, data: any) {
    const response = await apiClient.put(`/projects/${id}`, data)
    return transformProject(response.data)
  },

  // Tasks
  async getTasks(projectId?: string) {
    const response = await apiClient.get('/tasks/', { params: { projectId } })
    return response.data
  },

  async getTask(id: string) {
    const response = await apiClient.get(`/tasks/${id}`)
    return response.data
  },

  async createTask(data: any) {
    const response = await apiClient.post('/tasks/', data)
    return response.data
  },

  async updateTask(id: string, data: any) {
    const response = await apiClient.put(`/tasks/${id}`, data)
    return response.data
  },

  // Bugs
  async getBugs(projectId?: string) {
    const response = await apiClient.get('/bugs/', { params: { projectId } })
    return response.data
  },

  async createBug(data: any) {
    const response = await apiClient.post('/bugs/', data)
    return response.data
  },

  // Users
  async getUsers() {
    const response = await apiClient.get('/users/')
    return response.data
  },

  async updateUserPreferences(data: any) {
    const response = await apiClient.put('/users/me/preferences', data)
    return response.data
  },

  async createUser(userData: any) {
    const response = await apiClient.post('/users/', userData)
    return response.data
  },

  async updateUser(userId: string, userData: any) {
    const response = await apiClient.put(`/users/${userId}`, userData)
    return response.data
  },

  async deleteUser(userId: string) {
    const response = await apiClient.delete(`/users/${userId}`)
    return response.data
  },

  // Phase Management
  async getPhases(includeInactive = false) {
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
    const response = await apiClient.get(`/phases/${id}`)
    return response.data
  },

  async createPhase(data: any) {
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
    const response = await apiClient.post(`/phases/${id}/deactivate`)
    return response.data
  },

  async getPhaseUsage(id: string) {
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
    const response = await apiClient.get('/programs', { params: { client_id: clientId } })
    return response.data
  },

  async getProgram(id: string) {
    const response = await apiClient.get(`/programs/${id}`)
    return response.data
  },

  // Use Cases
  async getUseCases(projectId?: string) {
    const response = await apiClient.get('/usecases', { params: { project_id: projectId } })
    if (!Array.isArray(response.data)) {
      console.error('UseCases API returned non-array response:', response.data)
      return []
    }
    return response.data.map((uc: any) => transformUseCase(uc)).filter((uc: any) => uc !== null)
  },

  // User Stories
  async getUserStories(usecaseId?: string) {
    const response = await apiClient.get('/user-stories', { params: { usecase_id: usecaseId } })
    return response.data
  },

  // Subtasks
  async getSubtasks(taskId?: string) {
    const response = await apiClient.get('/subtasks', { params: { task_id: taskId } })
    return response.data
  },

  // Safe version of getSubtasks that doesn't trigger logout on 401
  async getSubtasksSafe(taskId?: string) {
    try {
      // Use the safe client that doesn't trigger logout on 401
      const response = await safeApiClient.get('/subtasks', { params: { task_id: taskId } })
      return response.data
    } catch (error: any) {
      // Don't let 401 errors propagate to avoid logout
      if (error.response?.status === 401) {
        console.warn('Access denied to subtasks - user may not have permission')
        return []
      }
      // Re-throw other errors
      throw error
    }
  },

  // Bug Management - Additional methods
  async getBug(id: string) {
    const response = await apiClient.get(`/bugs/${id}`)
    return response.data
  },

  async updateBug(id: string, data: any) {
    const response = await apiClient.put(`/bugs/${id}`, data)
    return response.data
  },

  async assignBug(id: string, assigneeId: string) {
    const response = await apiClient.post(`/bugs/${id}/assign`, { assignee_id: assigneeId })
    return response.data
  },

  async resolveBug(id: string, resolutionNotes: string) {
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
    const response = await apiClient.get(`/audit-logs/${entityType}/${entityId}`, { 
      params: filters 
    })
    return response.data
  },

  // Generic HTTP methods for direct API access
  async get(url: string, config?: any) {
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
    const response = await apiClient.get('/qa-metrics/bugs/summary', { params: hierarchyFilter })
    return response.data
  },

  async getBugTrends(startDate?: string, endDate?: string, hierarchyFilter?: any) {
    const params = { ...hierarchyFilter, start_date: startDate, end_date: endDate }
    const response = await apiClient.get('/qa-metrics/bugs/trends', { params })
    return response.data
  },

  async getBugAgingReport(hierarchyFilter?: any) {
    const response = await apiClient.get('/qa-metrics/bugs/aging', { params: hierarchyFilter })
    return response.data
  },

  async getTestExecutionMetrics(testRunId?: string, hierarchyFilter?: any) {
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
  },

  // Team Management Operations
  async getTeams(projectId?: string) {
    try {
      const response = await apiClient.get('/teams/', { params: { project_id: projectId } })
      // Handle paginated response - return items array or full response
      if (response.data && response.data.items) {
        return response.data.items
      }
      if (Array.isArray(response.data)) {
        return response.data
      }
      return []
    } catch (error: any) {
      console.error('Error fetching teams:', error)
      throw error
    }
  },

  async getTeam(id: string) {
    const response = await apiClient.get(`/teams/${id}`)
    return response.data
  },

  async createTeam(data: any) {
    const response = await apiClient.post('/teams/', data)
    return response.data
  },

  async updateTeam(id: string, data: any) {
    const response = await apiClient.put(`/teams/${id}`, data)
    return response.data
  },

  async deleteTeam(id: string) {
    const response = await apiClient.delete(`/teams/${id}`)
    return response.data
  },

  async addTeamMember(teamId: string, userId: string, role?: string) {
    const response = await apiClient.post(`/teams/${teamId}/members`, { 
      user_id: userId, 
      role: role || 'Developer' 
    })
    return response.data
  },

  async removeTeamMember(teamId: string, userId: string) {
    const response = await apiClient.delete(`/teams/${teamId}/members/${userId}`)
    return response.data
  },

  async getTeamMembers(teamId: string) {
    const response = await apiClient.get(`/teams/${teamId}/members`)
    return response.data || []
  },

  // Assignment Operations - NEW
  async getAssignments(filters?: { 
    entity_type?: string, 
    entity_id?: string, 
    assignment_type?: string, 
    user_id?: string 
  }) {
    const cacheKey = `assignments:${JSON.stringify(filters || {})}`
    
    return getCachedOrFetch(cacheKey, async () => {
      const params: any = {}
      if (filters?.entity_type) params.entity_type = filters.entity_type
      if (filters?.entity_id) params.entity_id = filters.entity_id
      if (filters?.assignment_type) params.assignment_type = filters.assignment_type
      if (filters?.user_id) params.user_id = filters.user_id
      
      const response = await apiClient.get('/assignments/', { params })
      return response.data
    })
  },

  async createAssignment(data: any) {
    const response = await apiClient.post('/assignments/', data)
    // Invalidate assignment cache - clear all assignment-related cache
    invalidateCache('assignments')
    // Assignment created successfully, cache invalidated
    return response.data
  },

  async updateAssignment(id: string, data: any) {
    const response = await apiClient.put(`/assignments/${id}`, data)
    // Invalidate assignment cache
    invalidateCache('assignments:')
    return response.data
  },

  async deleteAssignment(id: string) {
    const response = await apiClient.delete(`/assignments/${id}`)
    // Invalidate assignment cache - clear all assignment-related cache
    invalidateCache('assignments')
    // Assignment deleted successfully, cache invalidated
    return response.data
  },

  async getAvailableAssignees(entityType: string, entityId: string) {
    const response = await apiClient.get(`/assignments/available-assignees`, {
      params: { entity_type: entityType, entity_id: entityId }
    })
    return response.data
  },

  // Get eligible users for assignment (uses backend validation rules)
  async getEligibleUsers(entityType: string, entityId: string, assignmentType: string) {
    const response = await apiClient.get(`/validation/eligible-users/${entityType}/${entityId}`, {
      params: { assignment_type: assignmentType }
    })
    return response.data
  },

  // Decision Management
  async getDecisions(params?: { entity_type?: string; decision_status?: string; skip?: number; limit?: number }) {
    const response = await apiClient.get('/decisions/', { params })
    return response.data
  },

  async createDecision(data: {
    note_text: string;
    entity_type: string;
    entity_id: string;
    decision_status?: string;
  }) {
    const response = await apiClient.post('/decisions/', data)
    return response.data
  },

  async updateDecisionStatus(decisionId: string, status: string) {
    const response = await apiClient.put(`/decisions/${decisionId}/status`, {
      decision_status: status
    })
    return response.data
  },

  async getDecisionStats() {
    const response = await apiClient.get('/decisions/stats')
    return response.data
  },

  // Enhanced Entity Notes with Decision Support
  async getEntityNotes(entityType: string, entityId: string, params?: {
    decisions_only?: boolean;
    notes_only?: boolean;
    skip?: number;
    limit?: number;
  }) {
    const response = await apiClient.get(`/hierarchy/${entityType}/${entityId}/notes`, { params })
    return response.data
  },

  async createEntityNote(entityType: string, entityId: string, data: {
    note_text: string;
    is_decision?: boolean;
    decision_status?: string;
  }) {
    const response = await apiClient.post(`/hierarchy/${entityType}/${entityId}/notes`, data)
    return response.data
  },

  async updateDecisionStatusInEntity(entityType: string, entityId: string, noteId: string, status: string) {
    const response = await apiClient.put(`/hierarchy/${entityType}/${entityId}/notes/${noteId}/decision-status`, {
      decision_status: status
    })
    return response.data
  }
}

export default api

// Export a typed API interface for better type safety
export interface HierarchyAPI {
  // Generic Entity Operations
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
  createUser: (userData: any) => Promise<any>
  updateUser: (userId: string, userData: any) => Promise<any>
  deleteUser: (userId: string) => Promise<any>
  
  // Auth Operations
  login: (email: string, password: string) => Promise<any>
  
  // Audit Operations
  getAuditLogs: (entityType: string, entityId: string, filters?: any) => Promise<any>

  // Team Operations
  getTeams: (projectId?: string) => Promise<any[]>
  getTeam: (id: string) => Promise<any>
  createTeam: (data: any) => Promise<any>
  updateTeam: (id: string, data: any) => Promise<any>
  deleteTeam: (id: string) => Promise<any>
  addTeamMember: (teamId: string, userId: string, role?: string) => Promise<any>
  removeTeamMember: (teamId: string, userId: string) => Promise<any>
  getTeamMembers: (teamId: string) => Promise<any[]>

  // Assignment Operations
  getAssignments: (filters?: { 
    entity_type?: string, 
    entity_id?: string, 
    assignment_type?: string, 
    user_id?: string 
  }) => Promise<any[]>
  createAssignment: (data: any) => Promise<any>
  updateAssignment: (id: string, data: any) => Promise<any>
  deleteAssignment: (id: string) => Promise<any>
  getAvailableAssignees: (entityType: string, entityId: string) => Promise<any[]>
}

// Ensure api conforms to the interface
export const typedApi: HierarchyAPI = api