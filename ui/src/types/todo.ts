/**
 * TypeScript type definitions for TODO feature
 */

// Base TODO entity interface
export interface BaseTodoEntity {
  id: string
  user_id: string
  is_deleted: boolean
  created_at: string
  updated_at: string
}

// TODO Item
export interface TodoItem extends BaseTodoEntity {
  title: string
  description?: string
  target_date: string // ISO date string (YYYY-MM-DD)
  visibility: 'public' | 'private'
  linked_entity_type?: 'task' | 'subtask'
  linked_entity_id?: string
  linked_entity_info?: LinkedTaskInfo
}

// Linked Task/Subtask Info (read-only summary)
export interface LinkedTaskInfo {
  id: string
  title: string
  status: string
  due_date?: string
  assigned_to?: string
  parent_id?: string // user_story_id for tasks, task_id for subtasks
}

// ADHOC Note
export interface AdhocNote extends BaseTodoEntity {
  title: string
  content?: string
  position: number
  color: string // Hex color code (#RRGGBB)
}

// Time Pane (for organizing TODO items by date)
export interface Pane {
  label: 'Yesterday' | 'Today' | 'Tomorrow' | 'Day After Tomorrow'
  date: Date
  dateString: string // ISO date string for API calls
  items: TodoItem[]
}

// API Request Types

export interface CreateTodoItemRequest {
  title: string
  description?: string
  target_date: string // ISO date string
  visibility: 'public' | 'private'
  linked_entity_type?: 'task' | 'subtask'
  linked_entity_id?: string
}

export interface UpdateTodoItemRequest {
  title?: string
  description?: string
  target_date?: string
  visibility?: 'public' | 'private'
}

export interface MoveTodoItemRequest {
  target_date: string // ISO date string
}

export interface LinkTodoItemRequest {
  entity_type: 'task' | 'subtask'
  entity_id: string
}

export interface CreateAdhocNoteRequest {
  title: string
  content?: string
  color?: string
}

export interface UpdateAdhocNoteRequest {
  title?: string
  content?: string
  color?: string
}

export interface ReorderAdhocNoteRequest {
  position: number
}

// API Response Types

export interface TodoItemsResponse {
  items: TodoItem[]
  total: number
}

export interface AdhocNotesResponse {
  notes: AdhocNote[]
  total: number
}

export interface TaskSummaryResponse extends LinkedTaskInfo {
  user_story_id?: string // For tasks
}

export interface SubtaskSummaryResponse extends LinkedTaskInfo {
  task_id?: string // For subtasks
}

// Query Parameters

export interface FetchTodoItemsParams {
  start_date?: string // ISO date string
  end_date?: string // ISO date string
  include_public?: boolean
}

// Form Data Types

export interface TodoItemFormData {
  title: string
  description?: string
  target_date: string
  visibility: 'public' | 'private'
  linked_entity_type?: 'task' | 'subtask'
  linked_entity_id?: string
}

export interface AdhocNoteFormData {
  title: string
  content?: string
  color?: string
}

// Constants

export const TODO_VISIBILITY_OPTIONS = ['public', 'private'] as const
export const TODO_ENTITY_TYPES = ['task', 'subtask'] as const
export const PANE_LABELS = ['Yesterday', 'Today', 'Tomorrow', 'Day After Tomorrow'] as const

// Default colors for ADHOC notes
export const ADHOC_NOTE_COLORS = [
  '#FFEB3B', // Yellow (default)
  '#FFC107', // Amber
  '#FF9800', // Orange
  '#FF5722', // Deep Orange
  '#E91E63', // Pink
  '#9C27B0', // Purple
  '#673AB7', // Deep Purple
  '#3F51B5', // Indigo
  '#2196F3', // Blue
  '#03A9F4', // Light Blue
  '#00BCD4', // Cyan
  '#009688', // Teal
  '#4CAF50', // Green
  '#8BC34A', // Light Green
  '#CDDC39', // Lime
] as const

// Type guards

export function isTodoItem(item: any): item is TodoItem {
  return (
    item &&
    typeof item === 'object' &&
    'title' in item &&
    'target_date' in item &&
    'visibility' in item
  )
}

export function isAdhocNote(note: any): note is AdhocNote {
  return (
    note &&
    typeof note === 'object' &&
    'title' in note &&
    'position' in note &&
    'color' in note
  )
}

export function isLinkedTodoItem(item: TodoItem): boolean {
  return !!(item.linked_entity_type && item.linked_entity_id)
}

// Utility types

export type TodoVisibility = typeof TODO_VISIBILITY_OPTIONS[number]
export type TodoEntityType = typeof TODO_ENTITY_TYPES[number]
export type PaneLabel = typeof PANE_LABELS[number]
export type AdhocNoteColor = typeof ADHOC_NOTE_COLORS[number]
