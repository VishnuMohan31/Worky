# Rich Response Components Guide

This guide documents the rich response rendering components for the Chat Assistant feature.

## Overview

The chat assistant supports rich responses beyond plain text, including:
- **Entity Cards**: Display structured information about tasks, bugs, projects, etc.
- **Data Tables**: Show tabular data with sorting and pagination
- **Charts**: Visualize aggregate data with bar, pie, and line charts
- **Action Buttons**: Provide clickable actions with appropriate styling and icons

## Components

### 1. MessageCard

Displays entity information as interactive cards with deep links.

**Props:**
```typescript
interface EntityCard {
  entity_type: string        // 'task', 'bug', 'project', etc.
  entity_id: string          // Unique identifier
  title: string              // Display title
  status?: string            // Current status
  assignee?: string          // Assigned user
  due_date?: string          // ISO date string
  priority?: string          // Priority level
  deep_link?: string         // Navigation URL
  metadata?: Record<string, any>  // Additional fields
}
```

**Features:**
- Automatic icon selection based on entity type
- Color-coded status badges
- Priority indicators with appropriate colors
- Due date formatting with overdue warnings
- Clickable cards that navigate to entity detail pages
- Metadata display (up to 3 fields)

**Usage:**
```tsx
import { MessageCard } from '../components/chat'

<MessageCard card={{
  entity_type: 'task',
  entity_id: 'TSK-001',
  title: 'Complete documentation',
  status: 'In Progress',
  assignee: 'John Doe',
  due_date: '2025-12-01T00:00:00Z',
  priority: 'High',
  deep_link: '/tasks/TSK-001',
  metadata: {
    'Story Points': 5,
    'Phase': 'Development'
  }
}} />
```

### 2. ActionButton

Renders clickable action buttons with icons and appropriate styling.

**Props:**
```typescript
interface UIAction {
  action_type: string        // Type of action
  label: string              // Button text
  entity_type?: string       // Related entity type
  entity_id?: string         // Related entity ID
  deep_link?: string         // Navigation URL
  parameters?: Record<string, any>  // Additional parameters
}
```

**Supported Action Types:**
- `view_entity`: Navigate to entity detail page (primary style)
- `set_reminder`: Create a reminder (info style)
- `update_status`: Change entity status (warning style)
- `create_comment`: Add a comment (secondary style)
- `link_commit`: Link a commit/PR (secondary style)
- `suggest_report`: Navigate to report page (success style)

**Features:**
- Automatic icon selection based on action type
- Color-coded styling by action type
- Hover effects and animations
- Custom action handler support

**Usage:**
```tsx
import { ActionButton } from '../components/chat'

<ActionButton 
  action={{
    action_type: 'view_entity',
    label: 'View Details',
    deep_link: '/tasks/TSK-001'
  }}
  onActionClick={(action) => console.log('Action clicked:', action)}
/>
```

### 3. DataTable

Displays tabular data with sorting and pagination support.

**Props:**
```typescript
interface DataTableData {
  columns: string[]          // Column headers
  rows: any[][]              // Data rows
  total_count: number        // Total number of records
  has_more?: boolean         // Whether more data is available
}
```

**Features:**
- Click column headers to sort
- Ascending/descending sort indicators
- Color-coded status and priority columns
- Responsive scrolling (max height 400px)
- Load more button for pagination
- Empty state display
- Cell value formatting (booleans, objects, null values)

**Usage:**
```tsx
import { DataTable } from '../components/chat'

<DataTable 
  data={{
    columns: ['ID', 'Title', 'Status', 'Priority'],
    rows: [
      ['TSK-001', 'Complete docs', 'In Progress', 'High'],
      ['TSK-002', 'Review PRs', 'To Do', 'Medium']
    ],
    total_count: 15,
    has_more: true
  }}
  onLoadMore={() => console.log('Load more clicked')}
/>
```

### 4. ChartVisualization

Renders charts for aggregate data visualization.

**Props:**
```typescript
interface ChartData {
  labels: string[]           // X-axis labels
  datasets: Array<{
    label: string            // Dataset name
    data: number[]           // Data points
    color?: string           // Custom color
  }>
  title?: string             // Chart title
  type?: 'bar' | 'pie' | 'line'  // Chart type
}
```

**Chart Types:**
- **Bar Chart**: Vertical bars for comparing values
- **Pie Chart**: Circular chart showing proportions
- **Line Chart**: Connected points showing trends

**Features:**
- Interactive chart type selector
- Automatic color assignment
- Responsive sizing
- Legend display (for multi-dataset charts)
- Tooltips on hover
- Empty state display

**Usage:**
```tsx
import { ChartVisualization } from '../components/chat'

<ChartVisualization 
  data={{
    title: 'Task Status Distribution',
    labels: ['To Do', 'In Progress', 'Done', 'Blocked'],
    datasets: [{
      label: 'Tasks',
      data: [12, 8, 25, 3]
    }],
    type: 'bar'
  }}
/>
```

## Integration with ChatWidget

The ChatWidget component automatically renders rich components based on the message data:

```typescript
interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  cards?: EntityCard[]       // Entity cards to display
  table?: DataTableData      // Data table to display
  chart?: ChartData          // Chart to display
  actions?: UIAction[]       // Action buttons to display
  error?: boolean
}
```

**Example Response:**
```typescript
const response: ChatMessage = {
  id: 'msg-123',
  role: 'assistant',
  content: 'Here are your recent tasks:',
  timestamp: new Date(),
  cards: [
    {
      entity_type: 'task',
      entity_id: 'TSK-001',
      title: 'Complete documentation',
      status: 'In Progress',
      deep_link: '/tasks/TSK-001'
    }
  ],
  actions: [
    {
      action_type: 'view_entity',
      label: 'View All Tasks',
      deep_link: '/tasks'
    }
  ]
}
```

## Styling

All components use the `RichComponents.css` stylesheet which includes:
- Consistent color scheme matching the chat widget
- Hover effects and animations
- Dark mode support
- Responsive design for mobile devices
- Accessibility features (focus states, ARIA labels)

## Deep Link Navigation

Deep links follow the Worky routing structure:
- Tasks: `/tasks/:taskId`
- Bugs: `/bugs/:bugId`
- Projects: `/projects/:projectId`
- User Stories: `/userstories/:storyId`
- Use Cases: `/usecases/:usecaseId`
- Reports: `/reports`

The components use React Router's `useNavigate` hook for client-side navigation.

## Testing

Use the ChatWidgetTestPage to test all rich components:

```bash
# Navigate to the test page
http://localhost:5173/chat-test

# Try these test queries:
- "show tasks" - Display entity cards
- "list tasks" - Display data table
- "show chart" - Display chart visualization
- "show bugs" - Display bug cards
- "show projects" - Display project cards
```

## API Response Format

The backend should return responses in this format:

```json
{
  "status": "success",
  "message": "Here are your recent tasks:",
  "cards": [
    {
      "entity_type": "task",
      "entity_id": "TSK-001",
      "title": "Complete documentation",
      "status": "In Progress",
      "assignee": "John Doe",
      "due_date": "2025-12-01T00:00:00Z",
      "priority": "High",
      "deep_link": "/tasks/TSK-001",
      "metadata": {
        "Story Points": 5,
        "Phase": "Development"
      }
    }
  ],
  "table": {
    "columns": ["ID", "Title", "Status"],
    "rows": [
      ["TSK-001", "Complete docs", "In Progress"]
    ],
    "total_count": 15,
    "has_more": true
  },
  "chart": {
    "title": "Task Distribution",
    "labels": ["To Do", "In Progress", "Done"],
    "datasets": [{
      "label": "Tasks",
      "data": [12, 8, 25]
    }],
    "type": "bar"
  },
  "actions": [
    {
      "action_type": "view_entity",
      "label": "View All Tasks",
      "deep_link": "/tasks"
    }
  ],
  "metadata": {
    "request_id": "req-123",
    "intent_type": "query",
    "response_time_ms": 250
  }
}
```

## Best Practices

1. **Entity Cards**: Use for displaying 1-5 entities with detailed information
2. **Data Tables**: Use for displaying 5+ entities in a compact format
3. **Charts**: Use for aggregate data and statistics
4. **Action Buttons**: Limit to 2-4 actions per message for clarity
5. **Deep Links**: Always provide deep links for entity cards
6. **Metadata**: Include only the most relevant 2-3 metadata fields
7. **Status Colors**: Use consistent status naming for automatic color coding
8. **Priority Levels**: Use standard priority levels (P0-P3, High/Medium/Low)

## Accessibility

All components include:
- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation support
- Focus indicators
- Screen reader friendly text
- Color contrast compliance

## Browser Support

Components are tested and supported on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

Potential improvements for future iterations:
- Interactive chart tooltips with more details
- Export functionality for tables and charts
- Inline editing for entity cards
- Drag-and-drop for reordering
- Real-time updates via WebSocket
- Custom chart colors and themes
- Advanced filtering for tables
- Pagination controls for large datasets
