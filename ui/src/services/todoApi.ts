/**
 * TODO Feature API Service
 * Handles all API calls for TODO items and ADHOC notes
 * Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
 */

import axios from 'axios'
import { apiConfig } from '../config/api.config'
import type {
  TodoItem,
  AdhocNote,
  TodoItemsResponse,
  AdhocNotesResponse,
  TaskSummaryResponse,
  SubtaskSummaryResponse,
  CreateTodoItemRequest,
  UpdateTodoItemRequest,
  MoveTodoItemRequest,
  LinkTodoItemRequest,
  CreateAdhocNoteRequest,
  UpdateAdhocNoteRequest,
  ReorderAdhocNoteRequest,
  FetchTodoItemsParams
} from '../types/todo'

// Create axios instance with config
const todoApiClient = axios.create(apiConfig)

// Add auth token to requests
todoApiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Enhanced error message extraction
 * Provides user-friendly error messages from API responses
 */
function getErrorMessage(error: any): string {
  // Network error
  if (!error.response) {
    return 'Network error. Please check your connection and try again.'
  }
  
  const status = error.response.status
  const data = error.response.data
  
  // Extract error message from various response formats
  if (typeof data === 'string') {
    return data
  }
  
  if (data?.detail) {
    if (typeof data.detail === 'string') {
      return data.detail
    }
    if (Array.isArray(data.detail)) {
      return data.detail.map((d: any) => d.msg || d.message || String(d)).join(', ')
    }
  }
  
  if (data?.message) {
    return data.message
  }
  
  if (data?.error) {
    return data.error
  }
  
  // Status-based fallback messages
  switch (status) {
    case 400:
      return 'Invalid request. Please check your input and try again.'
    case 401:
      return 'Authentication required. Please log in again.'
    case 403:
      return 'You do not have permission to perform this action.'
    case 404:
      return 'The requested item was not found.'
    case 409:
      return 'This action conflicts with existing data.'
    case 422:
      return 'Validation error. Please check your input.'
    case 429:
      return 'Too many requests. Please wait a moment and try again.'
    case 500:
      return 'Server error. Please try again later.'
    case 503:
      return 'Service temporarily unavailable. Please try again later.'
    default:
      return `An error occurred (${status}). Please try again.`
  }
}

/**
 * Retry logic for failed requests
 * Retries transient errors (network issues, 5xx errors)
 */
async function retryRequest<T>(
  requestFn: () => Promise<T>,
  maxRetries = 2,
  delayMs = 1000
): Promise<T> {
  let lastError: any
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn()
    } catch (error: any) {
      lastError = error
      
      // Don't retry on client errors (4xx) except 429 (rate limit)
      const status = error.response?.status
      if (status && status >= 400 && status < 500 && status !== 429) {
        throw error
      }
      
      // Don't retry if this is the last attempt
      if (attempt === maxRetries) {
        throw error
      }
      
      // Wait before retrying (exponential backoff)
      const delay = delayMs * Math.pow(2, attempt)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  
  throw lastError
}

// Add response interceptor for error handling
todoApiClient.interceptors.response.use(
  response => response,
  error => {
    const errorMessage = getErrorMessage(error)
    console.error('TODO API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data
    })
    
    // Attach user-friendly message to error
    error.userMessage = errorMessage
    
    return Promise.reject(error)
  }
)

/**
 * TODO Items API Service
 * Requirements: 8.1, 8.3, 8.4, 8.5
 */

/**
 * Fetch TODO items for the authenticated user
 * @param params - Query parameters for filtering
 * @returns Promise with TODO items response
 */
export async function fetchTodoItems(params?: FetchTodoItemsParams): Promise<TodoItemsResponse> {
  return retryRequest(async () => {
    const response = await todoApiClient.get<TodoItemsResponse>('/todos', { params })
    return response.data
  })
}

/**
 * Create a new TODO item
 * @param data - TODO item creation data
 * @returns Promise with created TODO item
 */
export async function createTodoItem(data: CreateTodoItemRequest): Promise<TodoItem> {
  const response = await todoApiClient.post<TodoItem>('/todos', data)
  return response.data
}

/**
 * Update an existing TODO item
 * @param todoId - ID of the TODO item to update
 * @param data - TODO item update data
 * @returns Promise with updated TODO item
 */
export async function updateTodoItem(todoId: string, data: UpdateTodoItemRequest): Promise<TodoItem> {
  const response = await todoApiClient.put<TodoItem>(`/todos/${todoId}`, data)
  return response.data
}

/**
 * Soft delete a TODO item
 * @param todoId - ID of the TODO item to delete
 * @returns Promise that resolves when deletion is complete
 */
export async function deleteTodoItem(todoId: string): Promise<void> {
  await todoApiClient.delete(`/todos/${todoId}`)
}

/**
 * Move a TODO item to a different date (pane)
 * @param todoId - ID of the TODO item to move
 * @param data - Move request with new target date
 * @returns Promise with updated TODO item
 */
export async function moveTodoItem(todoId: string, data: MoveTodoItemRequest): Promise<TodoItem> {
  const response = await todoApiClient.patch<TodoItem>(`/todos/${todoId}/move`, data)
  return response.data
}

/**
 * Link a TODO item to a task or subtask
 * @param todoId - ID of the TODO item to link
 * @param data - Link request with entity type and ID
 * @returns Promise with updated TODO item including linked entity info
 */
export async function linkTodoItem(todoId: string, data: LinkTodoItemRequest): Promise<TodoItem> {
  const response = await todoApiClient.post<TodoItem>(`/todos/${todoId}/link`, data)
  return response.data
}

/**
 * Unlink a TODO item from its task or subtask
 * @param todoId - ID of the TODO item to unlink
 * @returns Promise with updated TODO item
 */
export async function unlinkTodoItem(todoId: string): Promise<TodoItem> {
  const response = await todoApiClient.delete<TodoItem>(`/todos/${todoId}/link`)
  return response.data
}

/**
 * Fetch read-only summary information for a task
 * @param taskId - ID of the task
 * @returns Promise with task summary data
 */
export async function fetchTaskSummary(taskId: string): Promise<TaskSummaryResponse> {
  const response = await todoApiClient.get<TaskSummaryResponse>(`/tasks/${taskId}/summary`)
  return response.data
}

/**
 * Fetch read-only summary information for a subtask
 * @param subtaskId - ID of the subtask
 * @returns Promise with subtask summary data
 */
export async function fetchSubtaskSummary(subtaskId: string): Promise<SubtaskSummaryResponse> {
  const response = await todoApiClient.get<SubtaskSummaryResponse>(`/subtasks/${subtaskId}/summary`)
  return response.data
}

/**
 * ADHOC Notes API Service
 * Requirements: 8.2
 */

/**
 * Fetch ADHOC notes for the authenticated user
 * @returns Promise with ADHOC notes response
 */
export async function fetchAdhocNotes(): Promise<AdhocNotesResponse> {
  return retryRequest(async () => {
    const response = await todoApiClient.get<AdhocNotesResponse>('/adhoc-notes')
    return response.data
  })
}

/**
 * Create a new ADHOC note
 * @param data - ADHOC note creation data
 * @returns Promise with created ADHOC note
 */
export async function createAdhocNote(data: CreateAdhocNoteRequest): Promise<AdhocNote> {
  const response = await todoApiClient.post<AdhocNote>('/adhoc-notes', data)
  return response.data
}

/**
 * Update an existing ADHOC note
 * @param noteId - ID of the ADHOC note to update
 * @param data - ADHOC note update data
 * @returns Promise with updated ADHOC note
 */
export async function updateAdhocNote(noteId: string, data: UpdateAdhocNoteRequest): Promise<AdhocNote> {
  const response = await todoApiClient.put<AdhocNote>(`/adhoc-notes/${noteId}`, data)
  return response.data
}

/**
 * Soft delete an ADHOC note
 * @param noteId - ID of the ADHOC note to delete
 * @returns Promise that resolves when deletion is complete
 */
export async function deleteAdhocNote(noteId: string): Promise<void> {
  await todoApiClient.delete(`/adhoc-notes/${noteId}`)
}

/**
 * Reorder an ADHOC note by updating its position
 * @param noteId - ID of the ADHOC note to reorder
 * @param data - Reorder request with new position
 * @returns Promise with updated ADHOC note
 */
export async function reorderAdhocNote(noteId: string, data: ReorderAdhocNoteRequest): Promise<AdhocNote> {
  const response = await todoApiClient.patch<AdhocNote>(`/adhoc-notes/${noteId}/reorder`, data)
  return response.data
}

/**
 * Export all TODO API functions as a single object for convenience
 */
export const todoApi = {
  // TODO Items
  fetchTodoItems,
  createTodoItem,
  updateTodoItem,
  deleteTodoItem,
  moveTodoItem,
  linkTodoItem,
  unlinkTodoItem,
  fetchTaskSummary,
  fetchSubtaskSummary,
  
  // ADHOC Notes
  fetchAdhocNotes,
  createAdhocNote,
  updateAdhocNote,
  deleteAdhocNote,
  reorderAdhocNote
}

export default todoApi
