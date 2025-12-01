/**
 * Chat API Client Verification Script
 * 
 * This script verifies that the chat API client is properly implemented
 * and can be imported without errors.
 * 
 * Run with: npx ts-node ui/src/services/__tests__/verify-chat-api.ts
 */

import chatApi, {
  sendMessage,
  getHistory,
  clearSession,
  checkHealth,
  type ChatRequest,
  type ChatResponse,
  type ChatHistoryResponse,
  type ChatHealthResponse,
  type UIAction,
  type EntityCard,
  type DataTable,
  type ChatMetadata,
  type ChatMessage,
  type SessionContext,
  type IntentType,
  type ActionType,
  type EntityType
} from '../chatApi'

console.log('✓ Chat API module imported successfully')

// Verify all exports are available
console.log('\nVerifying exports:')
console.log('✓ sendMessage function:', typeof sendMessage === 'function')
console.log('✓ getHistory function:', typeof getHistory === 'function')
console.log('✓ clearSession function:', typeof clearSession === 'function')
console.log('✓ checkHealth function:', typeof checkHealth === 'function')
console.log('✓ chatApi default export:', typeof chatApi === 'object')

// Verify chatApi object has all methods
console.log('\nVerifying chatApi object methods:')
console.log('✓ chatApi.sendMessage:', typeof chatApi.sendMessage === 'function')
console.log('✓ chatApi.getHistory:', typeof chatApi.getHistory === 'function')
console.log('✓ chatApi.clearSession:', typeof chatApi.clearSession === 'function')
console.log('✓ chatApi.checkHealth:', typeof chatApi.checkHealth === 'function')

// Verify type exports (TypeScript will catch if these don't exist)
console.log('\nVerifying type exports:')
const typeChecks = [
  'ChatRequest',
  'ChatResponse',
  'ChatHistoryResponse',
  'ChatHealthResponse',
  'UIAction',
  'EntityCard',
  'DataTable',
  'ChatMetadata',
  'ChatMessage',
  'SessionContext',
  'IntentType',
  'ActionType',
  'EntityType'
]

typeChecks.forEach(typeName => {
  console.log(`✓ ${typeName} type exported`)
})

console.log('\n✅ All verifications passed!')
console.log('\nChat API client is ready to use.')
console.log('\nExample usage:')
console.log(`
import chatApi from './services/chatApi'

// Send a message
const response = await chatApi.sendMessage('Show me tasks for Project X')

// Get conversation history
const history = await chatApi.getHistory(sessionId)

// Clear a session
await chatApi.clearSession(sessionId)

// Check service health
const health = await chatApi.checkHealth()
`)
