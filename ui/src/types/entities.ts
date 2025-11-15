/**
 * TypeScript type definitions for all entities
 */

// Base entity interface
export interface BaseEntity {
  id: string
  created_at: string
  updated_at?: string
  created_by?: string
  updated_by?: string
  is_deleted?: boolean
}

// Client
export interface Client extends BaseEntity {
  name: string
  short_description?: string
  long_description?: string
  is_active: boolean
}

// Program
export interface Program extends BaseEntity {
  client_id: string
  name: string
  short_description?: string
  long_description?: string
  start_date?: string
  end_date?: string
  status: string
}

// Project
export interface Project extends BaseEntity {
  program_id: string
  name: string
  short_description?: string
  long_description?: string
  start_date?: string
  end_date?: string
  status: string
  repository_url?: string
}

// Use Case
export interface UseCase extends BaseEntity {
  project_id: string
  name: string
  short_description?: string
  long_description?: string
  priority: string
  status: string
}

// User Story
export interface UserStory extends BaseEntity {
  usecase_id: string
  name: string
  short_description?: string
  long_description?: string
  acceptance_criteria?: string
  story_points?: number
  priority: string
  status: string
}

// Task
export interface Task extends BaseEntity {
  user_story_id: string
  phase_id: string
  name: string
  short_description?: string
  long_description?: string
  status: string
  priority: string
  assigned_to?: string
  estimated_hours?: number
  actual_hours?: number
  start_date?: string
  due_date?: string
  completed_at?: string
}

// Subtask
export interface Subtask extends BaseEntity {
  task_id: string
  phase_id: string
  name: string
  short_description?: string
  long_description?: string
  status: string
  assigned_to?: string
  estimated_hours?: number
  actual_hours?: number
  completed_at?: string
}

// Phase
export interface Phase extends BaseEntity {
  name: string
  short_description?: string
  long_description?: string
  color: string
  is_active: boolean
  display_order: number
}

// Bug
export interface Bug extends BaseEntity {
  entity_type: string
  entity_id: string
  title: string
  short_description?: string
  long_description?: string
  severity: 'Critical' | 'High' | 'Medium' | 'Low'
  priority: 'P0' | 'P1' | 'P2' | 'P3'
  status: string
  assigned_to?: string
  reported_by: string
  resolution_notes?: string
  closed_at?: string
}

// User
export interface User extends BaseEntity {
  email: string
  full_name: string
  role: 'Admin' | 'Architect' | 'Designer' | 'Developer' | 'Tester'
  client_id: string
  is_active: boolean
  theme?: string
  language?: string
}

// Entity with context (for hierarchy navigation)
export interface EntityWithContext<T = any> {
  entity: T
  parent?: any
  children?: any[]
  breadcrumb?: BreadcrumbItem[]
}

// Breadcrumb item
export interface BreadcrumbItem {
  id: string
  name: string
  type: string
}

// Statistics
export interface EntityStatistics {
  status_counts: Record<string, number>
  phase_distribution?: Array<{ phase: string; count: number }>
  completion_percentage: number
  rollup_counts?: Record<string, number>
}

// Search result
export interface SearchResult {
  id: string
  name: string
  type: string
  status?: string
  hierarchy_path?: string
  description?: string
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

// Form data types
export interface EntityFormData {
  name: string
  short_description?: string
  long_description?: string
  status?: string
  start_date?: string
  end_date?: string
  [key: string]: any
}

export interface TaskFormData extends EntityFormData {
  user_story_id: string
  phase_id: string
  priority: string
  assigned_to?: string
  estimated_hours?: number
  due_date?: string
}

export interface SubtaskFormData extends EntityFormData {
  task_id: string
  phase_id: string
  assigned_to?: string
  estimated_hours?: number
}

export interface BugFormData {
  entity_type: string
  entity_id: string
  title: string
  short_description?: string
  long_description?: string
  severity: 'Critical' | 'High' | 'Medium' | 'Low'
  priority: 'P0' | 'P1' | 'P2' | 'P3'
  assigned_to?: string
}

export interface PhaseFormData {
  name: string
  short_description?: string
  long_description?: string
  color: string
  is_active: boolean
  display_order: number
}

// Filter types
export interface EntityFilters {
  status?: string
  priority?: string
  assigned_to?: string
  phase_id?: string
  start_date?: string
  end_date?: string
  search?: string
}

// Audit Log
export interface AuditLog extends BaseEntity {
  user_id: string
  user_name?: string
  client_id?: string
  project_id?: string
  action: 'CREATE' | 'UPDATE' | 'DELETE' | 'VIEW'
  entity_type: string
  entity_id: string
  changes: Record<string, { old: any; new: any }> | null
  request_id?: string
  ip_address?: string
  user_agent?: string
}

// Audit Log Filters
export interface AuditLogFilters {
  page?: number
  page_size?: number
  date_from?: string
  date_to?: string
  action?: 'CREATE' | 'UPDATE' | 'DELETE' | 'VIEW'
}

// Entity type union
export type EntityType = 'client' | 'program' | 'project' | 'usecase' | 'userstory' | 'task' | 'subtask'

// Entity union type
export type Entity = Client | Program | Project | UseCase | UserStory | Task | Subtask

// Status options
export const STATUS_OPTIONS = {
  planning: ['Planning', 'In Progress', 'Completed', 'On Hold', 'Blocked'],
  task: ['To Do', 'In Progress', 'Done', 'Blocked'],
  bug: ['New', 'Assigned', 'In Progress', 'Fixed', 'Verified', 'Closed']
} as const

// Priority options
export const PRIORITY_OPTIONS = {
  standard: ['High', 'Medium', 'Low'],
  bug: ['P0', 'P1', 'P2', 'P3']
} as const

// Severity options
export const SEVERITY_OPTIONS = ['Critical', 'High', 'Medium', 'Low'] as const

// Role options
export const ROLE_OPTIONS = ['Admin', 'Architect', 'Designer', 'Developer', 'Tester'] as const
