/**
 * API Configuration
 * All API endpoints and configuration parameters
 */

// Get from environment variables or use defaults
// Use relative URL to leverage Vite's proxy configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000')

export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
}

export const endpoints = {
  // Auth
  login: '/auth/login',
  
  // Hierarchy
  hierarchy: '/hierarchy',
  clients: '/hierarchy/clients',
  programs: '/hierarchy/programs',
  projects: '/hierarchy/projects',
  usecases: '/hierarchy/usecases',
  userStories: '/hierarchy/userstories',
  tasks: '/hierarchy/tasks',
  subtasks: '/hierarchy/subtasks',
  
  // Bugs
  bugs: '/bugs',
  
  // Phases
  phases: '/phases',
  
  // Users
  users: '/users',
  currentUser: '/users/me',
  
  // Notes
  notes: (entityType: string, entityId: string) => `/hierarchy/${entityType}/${entityId}/notes`,
  
  // Statistics
  statistics: (entityType: string, entityId: string) => `/hierarchy/${entityType}/${entityId}/statistics`,
  
  // Audit
  auditLogs: (entityType: string, entityId: string) => `/audit-logs/${entityType}/${entityId}`
}
