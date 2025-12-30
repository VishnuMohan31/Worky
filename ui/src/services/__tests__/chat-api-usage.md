# Chat API Client Usage Guide

This document provides examples of how to use the chat API client in the Worky frontend application.

## Import

```typescript
import chatApi from '../services/chatApi'
// or import individual functions
import { sendMessage, getHistory, clearSession, checkHealth } from '../services/chatApi'
```

## Basic Usage

### Send a Message

```typescript
try {
  const response = await chatApi.sendMessage(
    'Show me all tasks for Project X',
    sessionId, // optional - will be auto-generated if not provided
    { currentProject: 'proj-123' } // optional context
  )
  
  console.log('Assistant response:', response.message)
  console.log('Data:', response.data)
  console.log('Actions:', response.actions)
  console.log('Cards:', response.cards)
} catch (error) {
  console.error('Error:', error.message)
}
```

### Get Conversation History

```typescript
try {
  const history = await chatApi.getHistory(sessionId, 50) // limit to 50 messages
  
  console.log('Messages:', history.messages)
  console.log('Session metadata:', history.session_metadata)
  console.log('Total messages:', history.total)
} catch (error) {
  console.error('Error:', error.message)
}
```

### Clear a Session

```typescript
try {
  const result = await chatApi.clearSession(sessionId)
  
  if (result.success) {
    console.log('Session cleared:', result.message)
  }
} catch (error) {
  console.error('Error:', error.message)
}
```

### Check Service Health

```typescript
const health = await chatApi.checkHealth()

console.log('Status:', health.status) // 'healthy', 'degraded', or 'unhealthy'
console.log('LLM available:', health.llm_available)
console.log('DB available:', health.db_available)
console.log('Redis available:', health.redis_available)
```

## React Component Example

```typescript
import { useState, useEffect } from 'react'
import chatApi, { ChatResponse } from '../services/chatApi'

function ChatComponent() {
  const [sessionId, setSessionId] = useState<string>()
  const [messages, setMessages] = useState<ChatResponse[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSend = async () => {
    if (!input.trim()) return
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await chatApi.sendMessage(input, sessionId)
      
      // Store session ID for future messages
      if (response.metadata?.request_id && !sessionId) {
        setSessionId(response.metadata.request_id)
      }
      
      setMessages(prev => [...prev, response])
      setInput('')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleClear = async () => {
    if (!sessionId) return
    
    try {
      await chatApi.clearSession(sessionId)
      setMessages([])
      setSessionId(undefined)
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <div>
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className="message">
            <p>{msg.message}</p>
            {msg.cards && msg.cards.map((card, i) => (
              <div key={i} className="card">
                <h4>{card.title}</h4>
                <p>Status: {card.status}</p>
                {card.deep_link && (
                  <a href={card.deep_link}>View Details</a>
                )}
              </div>
            ))}
            {msg.actions && msg.actions.map((action, i) => (
              <button key={i} onClick={() => handleAction(action)}>
                {action.label}
              </button>
            ))}
          </div>
        ))}
      </div>
      
      {error && <div className="error">{error}</div>}
      
      <div className="input">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && handleSend()}
          disabled={loading}
          placeholder="Ask me anything..."
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          {loading ? 'Sending...' : 'Send'}
        </button>
        <button onClick={handleClear} disabled={!sessionId}>
          Clear
        </button>
      </div>
    </div>
  )
}
```

## Response Structure

### ChatResponse

```typescript
{
  status: 'success' | 'error',
  message: string,                    // Human-readable response text
  data?: {                            // Structured data
    // ... any additional data
  },
  cards?: EntityCard[],               // Entity cards for display
  table?: DataTable,                  // Tabular data
  actions?: UIAction[],               // Available UI actions
  metadata?: {
    request_id: string,
    intent_type?: 'query' | 'action' | 'navigation' | 'report' | 'clarification',
    entities_accessed: string[],
    response_time_ms?: number,
    llm_tokens_used?: number
  }
}
```

### EntityCard

```typescript
{
  entity_type: 'project' | 'task' | 'bug' | ...,
  entity_id: string,
  title: string,
  status?: string,
  assignee?: string,
  due_date?: string,
  priority?: string,
  deep_link?: string,
  metadata?: Record<string, any>
}
```

### UIAction

```typescript
{
  action_type: 'view_entity' | 'set_reminder' | 'update_status' | ...,
  label: string,
  entity_type?: 'project' | 'task' | 'bug' | ...,
  entity_id?: string,
  deep_link?: string,
  parameters?: Record<string, any>
}
```

## Error Handling

The chat API client includes built-in error handling and retry logic:

- **Automatic Retries**: Network errors and 5xx server errors are automatically retried up to 2 times with exponential backoff
- **Rate Limiting**: 429 errors are handled gracefully with retry-after information
- **User-Friendly Messages**: All errors are transformed into readable messages
- **Authentication**: 401 errors are logged but don't trigger automatic redirects (let components handle)

### Error Examples

```typescript
// Validation error
try {
  await chatApi.sendMessage('') // Empty query
} catch (error) {
  // Error: "Query cannot be empty"
}

// Query too long
try {
  await chatApi.sendMessage('x'.repeat(2001))
} catch (error) {
  // Error: "Query is too long. Maximum length is 2000 characters."
}

// Network error (will retry automatically)
try {
  await chatApi.sendMessage('Show me tasks')
} catch (error) {
  // Error: "Network Error" (after retries exhausted)
}

// Rate limit error
try {
  await chatApi.sendMessage('Show me tasks')
} catch (error) {
  // Error: "Too many requests. Please try again in 30 seconds."
}
```

## Features

### Retry Logic

The client automatically retries failed requests:
- Network errors: Retried up to 2 times
- Server errors (5xx): Retried up to 2 times
- Rate limits (429): Retried up to 2 times
- Client errors (4xx except 429): Not retried
- Exponential backoff: 1s, 2s, 4s

### Authentication

JWT tokens are automatically included in all requests:
- Token is read from `localStorage.getItem('token')`
- Added to `Authorization: Bearer <token>` header
- No manual token management required

### Session Management

Sessions are automatically managed:
- Session ID can be provided or auto-generated
- Session context maintained across messages
- Sessions expire after 30 minutes of inactivity
- Can be manually cleared with `clearSession()`

## TypeScript Support

Full TypeScript support with exported types:

```typescript
import type {
  ChatRequest,
  ChatResponse,
  ChatHistoryResponse,
  ChatHealthResponse,
  UIAction,
  EntityCard,
  DataTable,
  ChatMetadata,
  ChatMessage,
  SessionContext,
  IntentType,
  ActionType,
  EntityType
} from '../services/chatApi'
```

## Requirements Covered

This implementation satisfies the following requirements from the spec:

- **10.1**: POST /api/v1/chat endpoint with query text, session ID, and user context
- **10.2**: Responses with consistent schema including status, message, data, actions, and metadata
- **10.3**: GET /api/v1/chat/history endpoint for retrieving conversation history
- **10.4**: Example requests and responses in documentation
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Retry Logic**: Automatic retry for transient failures
- **JWT Authentication**: Token automatically included in all requests
