# Chat Widget Component

A floating chat assistant widget for the Worky platform that enables natural language queries and interactions.

## Features

- ✅ **Floating Widget**: Positioned in bottom-right corner with toggle button
- ✅ **Message Display**: Shows user and assistant messages with distinct styling
- ✅ **Input Field**: Text area with send button for user queries
- ✅ **Typing Indicator**: Animated dots during LLM processing
- ✅ **Error Display**: Clear error messages with dismiss functionality
- ✅ **Collapsible UI**: Minimize/expand and close controls
- ✅ **Action Buttons**: Clickable actions in assistant responses
- ✅ **Auto-scroll**: Automatically scrolls to latest message
- ✅ **Keyboard Support**: Enter to send, Shift+Enter for new line
- ✅ **Responsive Design**: Mobile-friendly layout
- ✅ **Dark Mode Support**: Adapts to system color scheme

## Usage

### Basic Implementation

```tsx
import { ChatWidget } from './components/chat'

function App() {
  return (
    <div>
      {/* Your app content */}
      <ChatWidget />
    </div>
  )
}
```

### With Custom Message Handler

```tsx
import { ChatWidget, ChatMessage } from './components/chat'

function App() {
  const handleSendMessage = async (message: string): Promise<ChatMessage> => {
    // Call your chat API
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: message })
    })
    
    const data = await response.json()
    
    return {
      id: data.id,
      role: 'assistant',
      content: data.message,
      timestamp: new Date(),
      actions: data.actions
    }
  }

  return (
    <div>
      <ChatWidget onSendMessage={handleSendMessage} />
    </div>
  )
}
```

## Props

### ChatWidget

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `onSendMessage` | `(message: string) => Promise<ChatMessage>` | No | Handler for sending messages. If not provided, uses mock responses. |

## Types

### ChatMessage

```typescript
interface ChatMessage {
  id: string                    // Unique message identifier
  role: 'user' | 'assistant'    // Message sender
  content: string               // Message text
  timestamp: Date               // When message was sent
  actions?: ChatAction[]        // Optional action buttons
  error?: boolean               // Whether this is an error message
}
```

### ChatAction

```typescript
interface ChatAction {
  type: string      // Action type (e.g., 'VIEW_ENTITY', 'SET_REMINDER')
  label: string     // Button text
  url?: string      // Navigation URL
  data?: any        // Additional action data
}
```

## Styling

The component uses CSS custom properties for theming. You can customize colors by overriding these variables:

```css
.chat-widget {
  /* Override default styles */
  --chat-primary: #667eea;
  --chat-secondary: #764ba2;
}
```

## Testing

A test page is available at `/test/chat-widget` to verify all features:

1. Navigate to `/test/chat-widget` in your browser
2. Click the chat icon in the bottom-right corner
3. Try the suggested test queries
4. Verify all features work as expected

## Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in message
- **Escape**: Close widget (when focused)

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- Screen reader friendly
- Focus management

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Requirements Fulfilled

This component fulfills the following requirements from the chat assistant spec:

- **1.4**: Natural language query interface
- **8.1**: Deep links to entity detail pages
- **8.2**: Structured cards and tables for results
- **8.3**: Clickable action buttons
- **8.4**: Charts and visualizations support (via actions)
- **8.5**: Pagination controls (via actions)

## Next Steps

To integrate with the actual chat API:

1. Implement `chatApi.ts` service (Task 15)
2. Create `ChatContext` for session management (Task 17)
3. Add rich response rendering components (Task 16)
4. Integrate into main application layout (Task 18)

## Development

The component is located in `ui/src/components/chat/`:

- `ChatWidget.tsx` - Main component
- `ChatWidget.css` - Styles
- `index.ts` - Exports
- `README.md` - Documentation

## Notes

- Maximum query length: 2000 characters
- Messages auto-scroll to bottom
- Session state is managed internally
- Widget position is fixed (bottom-right)
- Animations use CSS keyframes for performance
