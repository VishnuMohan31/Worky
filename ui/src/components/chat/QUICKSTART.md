# Chat Widget Quick Start Guide

## Testing the Chat Widget

### 1. Start the Development Server

```bash
cd ui
npm run dev
```

### 2. Access the Test Page

Navigate to: `http://localhost:5173/test/chat-widget`

(You'll need to log in first if authentication is enabled)

### 3. Test the Widget

1. **Open the widget**: Click the purple chat icon in the bottom-right corner
2. **Send a message**: Type "Show me my tasks" and press Enter
3. **View the response**: See the mock response with action buttons
4. **Click an action**: Try clicking "View All Tasks" button
5. **Minimize**: Click the down arrow in the header
6. **Expand**: Click the up arrow to expand again
7. **Close**: Click the X button to close the widget

### 4. Try Different Queries

The test page includes mock responses for:
- "Show me my tasks"
- "What projects am I working on?"
- "List all bugs"
- "Help"
- Any other message (generic response)

### 5. Test Features

- ✅ **Typing indicator**: Watch the animated dots while waiting for response
- ✅ **Error handling**: Disconnect your network and try sending a message
- ✅ **Keyboard shortcuts**: 
  - Press `Enter` to send
  - Press `Shift + Enter` for new line
- ✅ **Auto-scroll**: Send multiple messages and watch it scroll automatically
- ✅ **Mobile view**: Resize your browser to see responsive design

## Integrating with Real API

### Step 1: Create the API Service

Create `ui/src/services/chatApi.ts`:

```typescript
import { ChatMessage } from '../components/chat'

export async function sendChatMessage(
  message: string,
  sessionId?: string
): Promise<ChatMessage> {
  const response = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({
      query: message,
      session_id: sessionId
    })
  })

  if (!response.ok) {
    throw new Error('Failed to send message')
  }

  const data = await response.json()
  
  return {
    id: data.id || `msg-${Date.now()}`,
    role: 'assistant',
    content: data.message,
    timestamp: new Date(),
    actions: data.actions
  }
}
```

### Step 2: Use in Your App

```typescript
import { ChatWidget } from './components/chat'
import { sendChatMessage } from './services/chatApi'

function App() {
  const [sessionId, setSessionId] = useState<string>()

  const handleSendMessage = async (message: string) => {
    const response = await sendChatMessage(message, sessionId)
    
    // Store session ID from first response
    if (!sessionId && response.sessionId) {
      setSessionId(response.sessionId)
    }
    
    return response
  }

  return (
    <div>
      {/* Your app content */}
      <ChatWidget onSendMessage={handleSendMessage} />
    </div>
  )
}
```

### Step 3: Add to Layout

Add the widget to your main layout component:

```typescript
// ui/src/components/layout/DashboardLayout.tsx
import { ChatWidget } from '../chat'

export default function DashboardLayout() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
      
      {/* Add Chat Widget */}
      <ChatWidget onSendMessage={handleSendMessage} />
    </div>
  )
}
```

## Customization

### Change Colors

Edit `ui/src/components/chat/ChatWidget.css`:

```css
.chat-toggle-button {
  background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}

.chat-header {
  background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}
```

### Change Position

Edit the CSS:

```css
.chat-toggle-button,
.chat-widget {
  bottom: 24px;  /* Change this */
  right: 24px;   /* Change this */
}
```

### Change Size

Edit the CSS:

```css
.chat-widget {
  width: 380px;      /* Change width */
  height: 600px;     /* Change height */
}
```

## Troubleshooting

### Widget not appearing?
- Check that you imported and rendered `<ChatWidget />`
- Check browser console for errors
- Verify the CSS file is being loaded

### Messages not sending?
- Check that `onSendMessage` prop is provided
- Check network tab for API errors
- Verify authentication token is valid

### Styling issues?
- Clear browser cache
- Check for CSS conflicts
- Verify Tailwind CSS is configured

### TypeScript errors?
- Run `npm install` to ensure all dependencies are installed
- Check that types are properly imported
- Verify tsconfig.json has `"jsx": "react-jsx"`

## Next Steps

1. ✅ Task 14: Create frontend chat widget component (COMPLETED)
2. ⏭️ Task 15: Implement chat API client in frontend
3. ⏭️ Task 16: Build rich response rendering components
4. ⏭️ Task 17: Implement session management in frontend
5. ⏭️ Task 18: Add chat widget to main application layout

## Support

For issues or questions:
- Check the README.md in this directory
- Review the IMPLEMENTATION_SUMMARY.md
- Check the requirements in `.kiro/specs/chat-assistant/requirements.md`
- Review the design in `.kiro/specs/chat-assistant/design.md`
