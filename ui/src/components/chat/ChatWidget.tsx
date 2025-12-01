/**
 * Chat Widget Component
 * Floating chat assistant widget for natural language queries
 * Requirements: 1.4, 8.1, 8.2, 8.3, 8.4, 8.5
 */

import { useState, useRef, useEffect } from 'react'
import './ChatWidget.css'
import './RichComponents.css'
import MessageCard, { EntityCard } from './MessageCard'
import ActionButton, { UIAction } from './ActionButton'
import DataTable, { DataTableData } from './DataTable'
import ChartVisualization, { ChartData } from './ChartVisualization'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  actions?: UIAction[]
  cards?: EntityCard[]
  table?: DataTableData
  chart?: ChartData
  error?: boolean
}

export interface ChatAction {
  type: string
  label: string
  url?: string
  data?: any
}

interface ChatWidgetProps {
  onSendMessage?: (message: string) => Promise<ChatMessage>
  isOpen?: boolean
  onToggle?: (isOpen: boolean) => void
}

export default function ChatWidget({ onSendMessage, isOpen: externalIsOpen, onToggle }: ChatWidgetProps) {
  const [internalIsOpen, setInternalIsOpen] = useState(false)
  
  // Use external control if provided, otherwise use internal state
  const isOpen = externalIsOpen !== undefined ? externalIsOpen : internalIsOpen
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Focus input when widget opens
  useEffect(() => {
    if (isOpen && !isMinimized && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen, isMinimized])

  const handleToggle = () => {
    const newIsOpen = !isOpen
    if (onToggle) {
      onToggle(newIsOpen)
    } else {
      setInternalIsOpen(newIsOpen)
    }
    setIsMinimized(false)
    setError(null)
  }

  const handleMinimize = () => {
    setIsMinimized(!isMinimized)
  }

  const handleClose = () => {
    if (onToggle) {
      onToggle(false)
    } else {
      setInternalIsOpen(false)
    }
    setIsMinimized(false)
  }

  const handleSendMessage = async () => {
    const trimmedMessage = inputValue.trim()
    if (!trimmedMessage || isTyping) return

    // Clear error state
    setError(null)

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmedMessage,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    try {
      // Call the onSendMessage handler if provided
      if (onSendMessage) {
        const assistantMessage = await onSendMessage(trimmedMessage)
        setMessages(prev => [...prev, assistantMessage])
      } else {
        // Default mock response for development
        await new Promise(resolve => setTimeout(resolve, 1000))
        const mockResponse: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: 'This is a placeholder response. Connect the chat API to get real responses.',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, mockResponse])
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message'
      setError(errorMessage)
      
      // Add error message to chat
      const errorResponse: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Error: ${errorMessage}`,
        timestamp: new Date(),
        error: true
      }
      setMessages(prev => [...prev, errorResponse])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleActionClick = (action: UIAction) => {
    // Action handling is now done in ActionButton component
    console.log('Action clicked:', action)
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <>
      {/* Chat Toggle Button */}
      {!isOpen && (
        <button
          className="chat-toggle-button"
          onClick={handleToggle}
          aria-label="Open chat assistant"
          title="Chat Assistant (Ctrl+K)"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <div className={`chat-widget ${isMinimized ? 'minimized' : ''}`}>
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-title">
              <svg
                className="w-5 h-5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span>Chat Assistant</span>
            </div>
            <div className="chat-header-actions">
              <button
                onClick={handleMinimize}
                className="chat-header-button"
                aria-label={isMinimized ? 'Expand chat' : 'Minimize chat'}
                title={isMinimized ? 'Expand' : 'Minimize'}
              >
                {isMinimized ? (
                  <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M5 15l7-7 7 7" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M19 9l-7 7-7-7" />
                  </svg>
                )}
              </button>
              <button
                onClick={handleClose}
                className="chat-header-button"
                aria-label="Close chat"
                title="Close"
              >
                <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages Container */}
          {!isMinimized && (
            <>
              <div className="chat-messages">
                {messages.length === 0 && (
                  <div className="chat-welcome">
                    <svg
                      className="w-12 h-12 text-gray-300 mb-3"
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                      Welcome to Chat Assistant
                    </h3>
                    <p className="text-sm text-gray-500 text-center max-w-xs">
                      Ask me anything about your projects, tasks, or bugs. I'm here to help!
                    </p>
                  </div>
                )}

                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`chat-message ${message.role} ${message.error ? 'error' : ''}`}
                  >
                    <div className="chat-message-avatar">
                      {message.role === 'user' ? (
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                          <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
                        </svg>
                      )}
                    </div>
                    <div className="chat-message-content">
                      <div className="chat-message-text">{message.content}</div>
                      
                      {/* Render entity cards */}
                      {message.cards && message.cards.length > 0 && (
                        <div className="chat-message-cards">
                          {message.cards.map((card, index) => (
                            <MessageCard key={index} card={card} />
                          ))}
                        </div>
                      )}
                      
                      {/* Render data table */}
                      {message.table && (
                        <DataTable data={message.table} />
                      )}
                      
                      {/* Render chart */}
                      {message.chart && (
                        <ChartVisualization data={message.chart} />
                      )}
                      
                      {/* Render action buttons */}
                      {message.actions && message.actions.length > 0 && (
                        <div className="chat-message-actions">
                          {message.actions.map((action, index) => (
                            <ActionButton
                              key={index}
                              action={action}
                              onActionClick={handleActionClick}
                            />
                          ))}
                        </div>
                      )}
                      
                      <div className="chat-message-time">{formatTime(message.timestamp)}</div>
                    </div>
                  </div>
                ))}

                {/* Typing Indicator */}
                {isTyping && (
                  <div className="chat-message assistant">
                    <div className="chat-message-avatar">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                        <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
                      </svg>
                    </div>
                    <div className="chat-message-content">
                      <div className="chat-typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Error Display */}
              {error && (
                <div className="chat-error">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span>{error}</span>
                  <button onClick={() => setError(null)} className="chat-error-close">
                    ×
                  </button>
                </div>
              )}

              {/* Input Area */}
              <div className="chat-input-container">
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything..."
                  className="chat-input"
                  rows={1}
                  disabled={isTyping}
                  maxLength={2000}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className="chat-send-button"
                  aria-label="Send message"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  )
}
