/**
 * Chat Context
 * Manages chat session state, conversation history, and session lifecycle
 * Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
 */

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { useAuth, AuthContext } from './AuthContext'
import chatApi, { ChatMessage as ApiChatMessage, ChatResponse } from '../services/chatApi'

// ============================================================================
// Types
// ============================================================================

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  actions?: any[]
  cards?: any[]
  table?: any
  chart?: any
  error?: boolean
}

export interface SessionMetadata {
  sessionId: string
  userId: string
  clientId: string
  createdAt: Date
  lastActivity: Date
  messageCount: number
}

interface ChatContextType {
  // Session state
  sessionId: string | null
  sessionMetadata: SessionMetadata | null
  isSessionActive: boolean
  
  // Conversation history
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  
  // Session management
  initializeSession: () => void
  clearSession: () => Promise<void>
  resetSession: () => void
  
  // Message handling
  sendMessage: (query: string, context?: Record<string, any>) => Promise<ChatMessage>
  loadHistory: () => Promise<void>
  
  // Session expiration
  isSessionExpired: boolean
  sessionExpiresAt: Date | null
  refreshSessionActivity: () => void
}

// ============================================================================
// Constants
// ============================================================================

const SESSION_STORAGE_KEY = 'chat_session_id'
const SESSION_METADATA_KEY = 'chat_session_metadata'
const SESSION_TTL_MINUTES = 30
const SESSION_WARNING_MINUTES = 5

// ============================================================================
// Context
// ============================================================================

const ChatContext = createContext<ChatContextType | undefined>(undefined)

// ============================================================================
// Provider Component
// ============================================================================

export function ChatProvider({ children }: { children: ReactNode }) {
  // Use useContext directly to avoid throwing errors during hot reloads
  // Fallback to safe defaults if context is not available
  const authContext = useContext(AuthContext)
  const user = authContext?.user ?? null
  const isAuthenticated = authContext?.isAuthenticated ?? false
  
  // Session state
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionMetadata, setSessionMetadata] = useState<SessionMetadata | null>(null)
  const [isSessionActive, setIsSessionActive] = useState(false)
  
  // Conversation state
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Session expiration state
  const [isSessionExpired, setIsSessionExpired] = useState(false)
  const [sessionExpiresAt, setSessionExpiresAt] = useState<Date | null>(null)

  /**
   * Generate a unique session ID
   */
  const generateSessionId = useCallback((): string => {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(2, 15)
    const userId = user?.id || 'anonymous'
    return `chat_${userId}_${timestamp}_${random}`
  }, [user])

  /**
   * Calculate session expiration time
   */
  const calculateExpirationTime = useCallback((): Date => {
    const now = new Date()
    return new Date(now.getTime() + SESSION_TTL_MINUTES * 60 * 1000)
  }, [])

  /**
   * Initialize a new chat session
   */
  const initializeSession = useCallback(() => {
    if (!isAuthenticated || !user) {
      console.warn('Cannot initialize session: user not authenticated')
      return
    }

    const newSessionId = generateSessionId()
    const now = new Date()
    const expiresAt = calculateExpirationTime()

    const metadata: SessionMetadata = {
      sessionId: newSessionId,
      userId: user.id,
      clientId: user.clientId,
      createdAt: now,
      lastActivity: now,
      messageCount: 0
    }

    // Save to state
    setSessionId(newSessionId)
    setSessionMetadata(metadata)
    setIsSessionActive(true)
    setIsSessionExpired(false)
    setSessionExpiresAt(expiresAt)
    setMessages([])
    setError(null)

    // Persist to localStorage
    localStorage.setItem(SESSION_STORAGE_KEY, newSessionId)
    localStorage.setItem(SESSION_METADATA_KEY, JSON.stringify(metadata))

    console.log('Chat session initialized:', newSessionId)
  }, [isAuthenticated, user, generateSessionId, calculateExpirationTime])

  /**
   * Clear the current session and conversation history
   */
  const clearSession = useCallback(async () => {
    if (!sessionId) {
      return
    }

    try {
      // Call API to clear session on backend
      // Note: If token is already removed (logout scenario), this will handle it gracefully
      await chatApi.clearSession(sessionId)
      // Only log success if we're not in a logout scenario (token still exists)
      const token = localStorage.getItem('token')
      if (token) {
        console.log('Session cleared on backend:', sessionId)
      }
    } catch (err: any) {
      // During logout, 401 errors are expected and handled gracefully
      // Only log errors that aren't related to authentication
      if (err?.response?.status !== 401) {
        console.error('Failed to clear session on backend:', err)
      }
      // Continue with local cleanup even if API call fails
    }

    // Clear local state
    setSessionId(null)
    setSessionMetadata(null)
    setIsSessionActive(false)
    setIsSessionExpired(false)
    setSessionExpiresAt(null)
    setMessages([])
    setError(null)

    // Clear localStorage
    localStorage.removeItem(SESSION_STORAGE_KEY)
    localStorage.removeItem(SESSION_METADATA_KEY)

    console.log('Chat session cleared')
  }, [sessionId])

  /**
   * Reset session (clear and reinitialize)
   */
  const resetSession = useCallback(async () => {
    await clearSession()
    initializeSession()
  }, [clearSession, initializeSession])

  /**
   * Refresh session activity timestamp
   */
  const refreshSessionActivity = useCallback(() => {
    if (!sessionMetadata) {
      return
    }

    const now = new Date()
    const expiresAt = calculateExpirationTime()

    const updatedMetadata: SessionMetadata = {
      ...sessionMetadata,
      lastActivity: now
    }

    setSessionMetadata(updatedMetadata)
    setSessionExpiresAt(expiresAt)
    setIsSessionExpired(false)

    // Update localStorage
    localStorage.setItem(SESSION_METADATA_KEY, JSON.stringify(updatedMetadata))
  }, [sessionMetadata, calculateExpirationTime])

  /**
   * Convert API message to local message format
   */
  const convertApiMessage = useCallback((apiMessage: ApiChatMessage): ChatMessage => {
    return {
      id: apiMessage.id,
      role: apiMessage.role,
      content: apiMessage.content,
      timestamp: new Date(apiMessage.created_at),
      actions: apiMessage.actions,
      error: false
    }
  }, [])

  /**
   * Load conversation history from backend
   */
  const loadHistory = useCallback(async () => {
    if (!sessionId) {
      console.warn('Cannot load history: no active session')
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      const historyResponse = await chatApi.getHistory(sessionId)
      
      // Convert API messages to local format
      const loadedMessages = historyResponse.messages.map(convertApiMessage)
      
      setMessages(loadedMessages)
      
      // Update session metadata if available
      if (historyResponse.session_metadata) {
        const metadata: SessionMetadata = {
          sessionId: historyResponse.session_metadata.session_id,
          userId: historyResponse.session_metadata.user_id,
          clientId: historyResponse.session_metadata.client_id,
          createdAt: new Date(historyResponse.session_metadata.created_at),
          lastActivity: new Date(historyResponse.session_metadata.last_activity),
          messageCount: historyResponse.total
        }
        setSessionMetadata(metadata)
      }

      console.log(`Loaded ${loadedMessages.length} messages from history`)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load conversation history'
      console.error('Load history error:', errorMessage)
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, convertApiMessage])

  /**
   * Send a message and get response
   */
  const sendMessage = useCallback(async (
    query: string,
    context?: Record<string, any>
  ): Promise<ChatMessage> => {
    if (!sessionId) {
      throw new Error('No active session. Please initialize a session first.')
    }

    if (!query.trim()) {
      throw new Error('Message cannot be empty')
    }

    try {
      setIsLoading(true)
      setError(null)

      // Refresh session activity
      refreshSessionActivity()

      // Send message to API
      const response: ChatResponse = await chatApi.sendMessage(query, sessionId, context)

      // Create assistant message from response
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        actions: response.actions,
        cards: response.cards,
        table: response.table,
        error: response.status === 'error'
      }

      // Update message count in metadata
      if (sessionMetadata) {
        const updatedMetadata: SessionMetadata = {
          ...sessionMetadata,
          messageCount: sessionMetadata.messageCount + 2 // user + assistant
        }
        setSessionMetadata(updatedMetadata)
        localStorage.setItem(SESSION_METADATA_KEY, JSON.stringify(updatedMetadata))
      }

      return assistantMessage
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message'
      console.error('Send message error:', errorMessage)
      setError(errorMessage)
      
      // Return error message
      const errorResponse: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Error: ${errorMessage}`,
        timestamp: new Date(),
        error: true
      }
      
      return errorResponse
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, sessionMetadata, refreshSessionActivity])

  /**
   * Check for session expiration periodically
   */
  useEffect(() => {
    if (!sessionExpiresAt || !isSessionActive) {
      return
    }

    const checkExpiration = () => {
      const now = new Date()
      const timeUntilExpiration = sessionExpiresAt.getTime() - now.getTime()
      
      // Session has expired
      if (timeUntilExpiration <= 0) {
        console.log('Session expired')
        setIsSessionExpired(true)
        setIsSessionActive(false)
      }
      // Session expiring soon (within warning window)
      else if (timeUntilExpiration <= SESSION_WARNING_MINUTES * 60 * 1000) {
        console.log(`Session expiring in ${Math.ceil(timeUntilExpiration / 60000)} minutes`)
      }
    }

    // Check immediately
    checkExpiration()

    // Check every minute
    const interval = setInterval(checkExpiration, 60 * 1000)

    return () => clearInterval(interval)
  }, [sessionExpiresAt, isSessionActive])

  /**
   * Restore session from localStorage on mount
   */
  useEffect(() => {
    if (!isAuthenticated || !user) {
      return
    }

    const storedSessionId = localStorage.getItem(SESSION_STORAGE_KEY)
    const storedMetadataStr = localStorage.getItem(SESSION_METADATA_KEY)

    if (storedSessionId && storedMetadataStr) {
      try {
        const storedMetadata = JSON.parse(storedMetadataStr)
        
        // Check if session belongs to current user
        if (storedMetadata.userId !== user.id) {
          console.log('Stored session belongs to different user, clearing')
          localStorage.removeItem(SESSION_STORAGE_KEY)
          localStorage.removeItem(SESSION_METADATA_KEY)
          return
        }

        // Check if session has expired
        const lastActivity = new Date(storedMetadata.lastActivity)
        const now = new Date()
        const minutesSinceActivity = (now.getTime() - lastActivity.getTime()) / (60 * 1000)

        if (minutesSinceActivity >= SESSION_TTL_MINUTES) {
          console.log('Stored session has expired, clearing')
          localStorage.removeItem(SESSION_STORAGE_KEY)
          localStorage.removeItem(SESSION_METADATA_KEY)
          return
        }

        // Restore session
        const metadata: SessionMetadata = {
          sessionId: storedMetadata.sessionId,
          userId: storedMetadata.userId,
          clientId: storedMetadata.clientId,
          createdAt: new Date(storedMetadata.createdAt),
          lastActivity: new Date(storedMetadata.lastActivity),
          messageCount: storedMetadata.messageCount || 0
        }

        const expiresAt = new Date(lastActivity.getTime() + SESSION_TTL_MINUTES * 60 * 1000)

        setSessionId(storedSessionId)
        setSessionMetadata(metadata)
        setIsSessionActive(true)
        setSessionExpiresAt(expiresAt)

        console.log('Restored chat session from localStorage:', storedSessionId)

        // Load conversation history
        // Note: We don't await this to avoid blocking the UI
        chatApi.getHistory(storedSessionId)
          .then(historyResponse => {
            const loadedMessages = historyResponse.messages.map(msg => convertApiMessage(msg))
            setMessages(loadedMessages)
          })
          .catch(err => {
            console.error('Failed to load history on restore:', err)
          })
      } catch (err) {
        console.error('Failed to restore session from localStorage:', err)
        localStorage.removeItem(SESSION_STORAGE_KEY)
        localStorage.removeItem(SESSION_METADATA_KEY)
      }
    }
  }, [isAuthenticated, user, convertApiMessage])

  /**
   * Clear session on user logout
   */
  useEffect(() => {
    if (!isAuthenticated && sessionId) {
      console.log('User logged out, clearing chat session')
      clearSession()
    }
  }, [isAuthenticated, sessionId, clearSession])

  // ============================================================================
  // Context Value
  // ============================================================================

  const contextValue: ChatContextType = {
    // Session state
    sessionId,
    sessionMetadata,
    isSessionActive,
    
    // Conversation history
    messages,
    isLoading,
    error,
    
    // Session management
    initializeSession,
    clearSession,
    resetSession,
    
    // Message handling
    sendMessage,
    loadHistory,
    
    // Session expiration
    isSessionExpired,
    sessionExpiresAt,
    refreshSessionActivity
  }

  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  )
}

// ============================================================================
// Hook
// ============================================================================

export function useChat() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChat must be used within ChatProvider')
  }
  return context
}
