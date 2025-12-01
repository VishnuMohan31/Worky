# TODO Feature Error Handling & User Feedback

This document describes the error handling and user feedback implementation for the TODO feature.

## Overview

The TODO feature implements comprehensive error handling and user feedback mechanisms to provide a robust and user-friendly experience. This includes:

1. **Error Boundary** - Catches React component errors
2. **Toast Notifications** - Provides success/error feedback
3. **Retry Logic** - Automatically retries failed API calls
4. **Loading Skeletons** - Improves perceived performance
5. **User-Friendly Error Messages** - Clear, actionable error messages

## Components

### 1. Error Boundary (`ErrorBoundary.tsx`)

A React error boundary that catches errors in the component tree and displays a fallback UI.

**Features:**
- Catches and logs React component errors
- Displays user-friendly error message
- Provides "Try Again" button to reset error state
- Customizable fallback UI
- Optional error callback for logging

**Usage:**
```tsx
<ErrorBoundary
  fallback={<CustomErrorUI />}
  onError={(error, errorInfo) => {
    // Log to error tracking service
  }}
>
  <YourComponent />
</ErrorBoundary>
```

**Implementation in TODO Feature:**
The entire TodoPage is wrapped with ErrorBoundary to catch any unexpected errors.

### 2. Toast Notifications (`Toast.tsx`, `ToastContainer.tsx`)

A lightweight toast notification system for displaying success, error, warning, and info messages.

**Features:**
- Four toast types: success, error, warning, info
- Auto-dismiss with configurable duration
- Manual dismiss button
- Stacked notifications
- Smooth animations
- Responsive design
- Accessible (ARIA labels, keyboard support)

**Usage:**
```tsx
import { useToast } from '../components/common/ToastContainer'

function MyComponent() {
  const toast = useToast()
  
  // Show different types of toasts
  toast.showSuccess('Item saved successfully!')
  toast.showError('Failed to save item')
  toast.showWarning('This action cannot be undone')
  toast.showInfo('Loading data...')
  
  // Custom duration (default: 5000ms)
  toast.showSuccess('Quick message', 2000)
}
```

**Toast Provider Setup:**
The ToastProvider is added at the app root level in `App.tsx`:
```tsx
<ToastProvider>
  <Router>
    {/* App content */}
  </Router>
</ToastProvider>
```

### 3. API Error Handling & Retry Logic (`todoApi.ts`)

Enhanced API service with automatic retry logic and user-friendly error messages.

**Features:**
- Automatic retry for transient errors (network issues, 5xx errors)
- Exponential backoff retry strategy
- User-friendly error message extraction
- Status-based error handling
- No retry for client errors (4xx) except rate limiting (429)

**Retry Configuration:**
- Max retries: 2
- Initial delay: 1000ms
- Exponential backoff: delay × 2^attempt

**Error Message Extraction:**
The API service extracts user-friendly messages from various error response formats:
- String responses
- `detail` field (string or array)
- `message` field
- `error` field
- Status-based fallback messages

**Example:**
```typescript
// API call with automatic retry
const items = await fetchTodoItems({ start_date, end_date })

// Error handling in component
try {
  await createTodoItem(data)
  toast.showSuccess('TODO item created!')
} catch (error: any) {
  const message = error.userMessage || 'Failed to create item'
  toast.showError(message)
}
```

### 4. Loading Skeletons (`TodoSkeletonLoader.tsx`)

Skeleton loaders that improve perceived performance during data loading.

**Features:**
- Multiple skeleton types: dashboard, pane, item, note
- Animated loading effect
- Matches actual component layout
- Responsive design
- Dark mode support
- Reduced motion support

**Skeleton Types:**
- `dashboard` - Full TODO dashboard skeleton
- `pane` - Single time pane skeleton
- `item` - TODO item card skeleton
- `note` - ADHOC note skeleton

**Usage:**
```tsx
if (isLoading) {
  return <TodoSkeletonLoader type="dashboard" />
}
```

## Error Handling Patterns

### Pattern 1: Query Error Handling (React Query)

Used for data fetching operations:

```tsx
const { data, isLoading, error, refetch } = useQuery({
  queryKey: ['todoItems'],
  queryFn: fetchTodoItems
})

if (isLoading) {
  return <TodoSkeletonLoader type="dashboard" />
}

if (error) {
  const errorMessage = (error as any)?.userMessage || 'Failed to load'
  return (
    <ErrorDisplay
      message={errorMessage}
      onRetry={() => {
        toast.showInfo('Retrying...')
        refetch()
      }}
    />
  )
}
```

### Pattern 2: Mutation Error Handling

Used for create/update/delete operations:

```tsx
const mutation = useMutation({
  mutationFn: createTodoItem,
  onSuccess: () => {
    toast.showSuccess('Item created successfully!')
    queryClient.invalidateQueries(['todoItems'])
  },
  onError: (error: any) => {
    const message = error.userMessage || 'Failed to create item'
    toast.showError(message)
  }
})
```

### Pattern 3: Optimistic Updates with Error Recovery

Used for drag-and-drop and reordering:

```tsx
try {
  // Optimistic update
  onItemMove(itemId, newDate)
  
  // Persist to API
  const updated = await moveTodoItem(itemId, { target_date: newDate })
  
  // Update with server response
  onItemUpdate(updated)
  
  toast.showSuccess('Item moved successfully')
} catch (error: any) {
  const message = error.userMessage || 'Failed to move item'
  toast.showError(message)
  
  // Revert optimistic update
  refetch()
}
```

## User-Friendly Error Messages

### Network Errors
- "Network error. Please check your connection and try again."

### Authentication Errors (401)
- "Authentication required. Please log in again."

### Authorization Errors (403)
- "You do not have permission to perform this action."

### Not Found Errors (404)
- "The requested item was not found."

### Validation Errors (422)
- "Validation error. Please check your input."

### Rate Limiting (429)
- "Too many requests. Please wait a moment and try again."

### Server Errors (5xx)
- "Server error. Please try again later."
- "Service temporarily unavailable. Please try again later."

## Accessibility

All error handling components follow accessibility best practices:

### Toast Notifications
- `role="alert"` for screen reader announcements
- `aria-live="polite"` for non-intrusive notifications
- `aria-label` on close button
- Keyboard accessible (Tab, Enter, Escape)

### Error Boundary
- Clear, descriptive error messages
- Keyboard accessible retry button
- Sufficient color contrast (WCAG AA)

### Loading Skeletons
- Respects `prefers-reduced-motion` setting
- Provides visual feedback without blocking interaction

## Testing Error Handling

### Manual Testing Scenarios

1. **Network Error**
   - Disconnect network
   - Try to load TODO items
   - Verify error message and retry button

2. **API Error**
   - Trigger 500 error from backend
   - Verify user-friendly error message
   - Verify automatic retry (check network tab)

3. **Validation Error**
   - Submit invalid data
   - Verify validation error message
   - Verify no retry attempted

4. **Component Error**
   - Trigger React error (e.g., null reference)
   - Verify error boundary catches it
   - Verify fallback UI displays

5. **Optimistic Update Failure**
   - Drag TODO item to new pane
   - Simulate API failure
   - Verify error toast
   - Verify UI reverts to previous state

### Automated Testing

```typescript
// Example test for error handling
describe('TodoPage Error Handling', () => {
  it('displays error message when API fails', async () => {
    // Mock API failure
    server.use(
      rest.get('/api/v1/todos', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ detail: 'Server error' }))
      })
    )
    
    render(<TodoPage />)
    
    // Wait for error message
    expect(await screen.findByText(/server error/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
  })
  
  it('retries failed requests automatically', async () => {
    let attempts = 0
    server.use(
      rest.get('/api/v1/todos', (req, res, ctx) => {
        attempts++
        if (attempts < 3) {
          return res(ctx.status(500))
        }
        return res(ctx.json({ items: [], total: 0 }))
      })
    )
    
    render(<TodoPage />)
    
    // Wait for successful load after retries
    await waitFor(() => {
      expect(attempts).toBe(3)
    })
  })
})
```

## Performance Considerations

### Toast Notifications
- Lightweight implementation (no external dependencies)
- Efficient rendering (only active toasts)
- Auto-cleanup after dismiss

### Retry Logic
- Exponential backoff prevents server overload
- Limited retry attempts (max 2)
- Smart retry (only for transient errors)

### Loading Skeletons
- CSS-only animations (no JavaScript)
- Minimal DOM elements
- Reuses existing styles

## Future Enhancements

1. **Error Tracking Integration**
   - Send errors to Sentry/LogRocket
   - Track error frequency and patterns
   - Monitor retry success rates

2. **Offline Support**
   - Queue operations when offline
   - Sync when connection restored
   - Show offline indicator

3. **Advanced Retry Strategies**
   - Configurable retry policies per endpoint
   - Circuit breaker pattern
   - Fallback to cached data

4. **Enhanced User Feedback**
   - Progress indicators for long operations
   - Undo/redo functionality
   - Detailed error logs for debugging

## Requirements Satisfied

This implementation satisfies the following requirements from the design document:

- **8.8**: Error handling and user feedback
  - ✅ Error boundary for TODO feature
  - ✅ Toast notifications for success/error messages
  - ✅ User-friendly error messages for API failures
  - ✅ Retry logic for failed API calls
  - ✅ Loading skeletons for better UX

## Related Files

- `ui/src/components/common/ErrorBoundary.tsx` - Error boundary component
- `ui/src/components/common/Toast.tsx` - Toast notification component
- `ui/src/components/common/ToastContainer.tsx` - Toast provider and context
- `ui/src/components/common/toast.css` - Toast styles
- `ui/src/components/todo/TodoSkeletonLoader.tsx` - Loading skeletons
- `ui/src/services/todoApi.ts` - API service with retry logic
- `ui/src/pages/TodoPage.tsx` - Main page with error handling
- `ui/src/components/todo/TimePanes.tsx` - Panes with error handling
- `ui/src/components/todo/AdhocNotesPane.tsx` - Notes with error handling
