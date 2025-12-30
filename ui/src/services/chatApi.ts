/**
 * Chat API Client
 * 
 * Provides functions for interacting with the chat assistant API endpoints.
 * Handles authentication, error handling, and retry logic.
 */

import axios, { AxiosError } from 'axios'
import { apiConfig } from '../config/api.config'

// ============================================================================
// Types
// ============================================================================

export type IntentType = 'query' | 'action' | 'navigation' | 'report' | 'clarification'
export type ActionType = 'view_entity' | 'set_reminder' | 'update_status' | 'create_comment' | 'link_commit' | 'suggest_report'
export type EntityType = 'project' | 'task' | 'subtask' | 'user_story' | 'usecase' | 'bug' | 'program' | 'test_case' | 'user'

export interface ChatRequest {
  query: string
  session_id?: string
  context?: Record<string, any>
}

export interface UIAction {
  action_type: ActionType
  label: string
  entity_type?: EntityType
  entity_id?: string
  deep_link?: string
  parameters?: Record<string, any>
}

export interface EntityCard {
  entity_type: EntityType
  entity_id: string
  title: string
  status?: string
  assignee?: string
  due_date?: string
  priority?: string
  deep_link?: string
  metadata?: Record<string, any>
}

export interface DataTable {
  columns: string[]
  rows: any[][]
  total_count: number
  has_more: boolean
}

export interface ChatMetadata {
  request_id: string
  intent_type?: IntentType
  entities_accessed: string[]
  response_time_ms?: number
  llm_tokens_used?: number
}

export interface ChatResponse {
  status: 'success' | 'error'
  message: string
  data?: Record<string, any>
  cards?: EntityCard[]
  table?: DataTable
  actions?: UIAction[]
  metadata?: ChatMetadata
}

export interface ChatErrorResponse {
  status: 'error'
  error: {
    code: string
    message: string
    details?: any
    timestamp?: string
    request_id?: string
  }
}

export interface ChatMessage {
  id: string
  session_id: string
  user_id: string
  role: 'user' | 'assistant'
  content: string
  intent_type?: IntentType
  entities?: Record<string, any>
  actions?: any[]
  created_at: string
}

export interface SessionContext {
  session_id: string
  user_id: string
  client_id: string
  current_project?: string
  mentioned_entities: Array<{
    entity_type: EntityType
    entity_id: string
    entity_name?: string
  }>
  last_intent?: IntentType
  created_at: string
  last_activity: string
}

export interface ChatHistoryResponse {
  messages: ChatMessage[]
  session_metadata?: SessionContext
  total: number
}

export interface ChatHealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  llm_available: boolean
  db_available: boolean
  redis_available: boolean
  timestamp: string
}

// ============================================================================
// Configuration
// ============================================================================

const CHAT_BASE_URL = `${apiConfig.baseURL}/chat`
const MAX_RETRIES = 2
const RETRY_DELAY_MS = 1000

// Create axios instance for chat API
const chatApiClient = axios.create({
  baseURL: CHAT_BASE_URL,
  timeout: apiConfig.timeout,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
chatApiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add response interceptor for error handling
chatApiClient.interceptors.response.use(
  response => response,
  error => {
    // Log error for debugging
    console.error('Chat API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.error?.message || error.message
    })
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      console.warn('Chat API: Unauthorized - token may be invalid or expired')
      // Don't redirect here - let the component handle it
    }
    
    // Handle 429 Rate Limit
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after']
      console.warn(`Chat API: Rate limit exceeded. Retry after ${retryAfter} seconds`)
    }
    
    return Promise.reject(error)
  }
)

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Delay execution for retry logic
 */
const delay = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Check if error is retryable (network errors, 5xx errors, but not 4xx)
 */
const isRetryableError = (error: AxiosError): boolean => {
  if (!error.response) {
    // Network error - retryable
    return true
  }
  
  const status = error.response.status
  
  // Don't retry client errors (4xx) except 429 (rate limit)
  if (status >= 400 && status < 500 && status !== 429) {
    return false
  }
  
  // Retry server errors (5xx) and rate limits (429)
  return status >= 500 || status === 429
}

/**
 * Execute request with retry logic
 */
async function executeWithRetry<T>(
  requestFn: () => Promise<T>,
  retries: number = MAX_RETRIES
): Promise<T> {
  let lastError: Error | null = null
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error as Error
      
      // Check if we should retry
      if (attempt < retries && error instanceof AxiosError && isRetryableError(error)) {
        const delayMs = RETRY_DELAY_MS * Math.pow(2, attempt) // Exponential backoff
        console.log(`Chat API: Retry attempt ${attempt + 1}/${retries} after ${delayMs}ms`)
        await delay(delayMs)
        continue
      }
      
      // Don't retry or max retries reached
      break
    }
  }
  
  // All retries failed
  throw lastError
}

/**
 * Transform error to user-friendly message
 */
const getErrorMessage = (error: any): string => {
  if (error.response?.data?.error?.message) {
    return error.response.data.error.message
  }
  
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  
  if (error.message) {
    return error.message
  }
  
  return 'An unexpected error occurred. Please try again.'
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Send a chat message and get a response
 * 
 * @param query - The user's natural language query
 * @param sessionId - Optional session ID for conversation context
 * @param context - Optional additional context data
 * @returns ChatResponse with message, data, and actions
 * @throws Error with user-friendly message on failure
 */
export async function sendMessage(
  query: string,
  sessionId?: string,
  context?: Record<string, any>
): Promise<ChatResponse> {
  try {
    // Validate query
    if (!query || !query.trim()) {
      throw new Error('Query cannot be empty')
    }
    
    if (query.length > 2000) {
      throw new Error('Query is too long. Maximum length is 2000 characters.')
    }
    
    // Prepare request
    const request: ChatRequest = {
      query: query.trim(),
      session_id: sessionId,
      context: context || {}
    }
    
    // Execute with retry logic
    const response = await executeWithRetry(async () => {
      return await chatApiClient.post<ChatResponse>('', request)
    })
    
    return response.data
  } catch (error) {
    console.error('sendMessage error:', error)
    throw new Error(getErrorMessage(error))
  }
}

/**
 * Get conversation history for a session
 * 
 * @param sessionId - Session ID to retrieve history for
 * @param limit - Maximum number of messages to return (default: 50)
 * @returns ChatHistoryResponse with messages and session metadata
 * @throws Error with user-friendly message on failure
 */
export async function getHistory(
  sessionId: string,
  limit: number = 50
): Promise<ChatHistoryResponse> {
  try {
    // Validate session ID
    if (!sessionId || !sessionId.trim()) {
      throw new Error('Session ID is required')
    }
    
    // Execute with retry logic
    const response = await executeWithRetry(async () => {
      return await chatApiClient.get<ChatHistoryResponse>(`/history/${sessionId}`, {
        params: { limit }
      })
    })
    
    return response.data
  } catch (error) {
    console.error('getHistory error:', error)
    
    // Handle 404 - session not found
    if (error instanceof AxiosError && error.response?.status === 404) {
      return {
        messages: [],
        total: 0
      }
    }
    
    throw new Error(getErrorMessage(error))
  }
}

/**
 * Clear a chat session and its conversation history
 * 
 * @param sessionId - Session ID to clear
 * @returns Success status
 * @throws Error with user-friendly message on failure
 */
export async function clearSession(sessionId: string): Promise<{ success: boolean; message: string }> {
  try {
    // Validate session ID
    if (!sessionId || !sessionId.trim()) {
      throw new Error('Session ID is required')
    }
    
    // Execute with retry logic (no retry for DELETE operations)
    const response = await chatApiClient.delete<{ success: boolean; message: string; session_id: string }>(
      `/session/${sessionId}`
    )
    
    return {
      success: response.data.success,
      message: response.data.message
    }
  } catch (error) {
    console.error('clearSession error:', error)
    
    // Handle 404 - session not found (consider it success)
    if (error instanceof AxiosError && error.response?.status === 404) {
      return {
        success: true,
        message: 'Session not found or already deleted'
      }
    }
    
    throw new Error(getErrorMessage(error))
  }
}

/**
 * Check the health status of the chat service
 * 
 * @returns ChatHealthResponse with service status
 */
export async function checkHealth(): Promise<ChatHealthResponse> {
  try {
    const response = await chatApiClient.get<ChatHealthResponse>('/health')
    return response.data
  } catch (error) {
    console.error('checkHealth error:', error)
    
    // Return unhealthy status on error
    return {
      status: 'unhealthy',
      llm_available: false,
      db_available: false,
      redis_available: false,
      timestamp: new Date().toISOString()
    }
  }
}

// ============================================================================
// Export
// ============================================================================

const chatApi = {
  sendMessage,
  getHistory,
  clearSession,
  checkHealth
}

export default chatApi
