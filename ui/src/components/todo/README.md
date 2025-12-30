# TODO Feature Components

This directory contains the React components for the TODO feature.

## Components

### TimePanes.tsx
Container component that manages the four time-based panes (Yesterday, Today, Tomorrow, Day After Tomorrow).

**Features:**
- Calculates pane dates based on current/selected date
- Filters TODO items by target_date for each pane
- Manages drag and drop state
- Handles API calls for moving items
- Implements optimistic UI updates

**Props:**
- `todoItems: TodoItem[]` - All TODO items to display
- `onItemMove: (itemId: string, newDate: Date) => void` - Callback when item is moved
- `onItemUpdate: (item: TodoItem) => void` - Callback when item is updated
- `onItemDelete: (itemId: string) => void` - Callback when item is deleted
- `selectedDate?: Date` - Optional date to calculate panes from (defaults to today)

### TimePane.tsx
Individual pane component that displays TODO items for a specific date.

**Features:**
- Displays pane label, date, and item count
- Renders list of TODO items
- Handles drag over and drop events
- Shows drop indicator when dragging
- Color-coded by pane type

**Props:**
- `pane: Pane` - Pane data including label, date, and items
- `onDragStart: (item: TodoItem) => void` - Callback when drag starts
- `onDrop: (pane: Pane) => void` - Callback when item is dropped
- `onDragEnd: () => void` - Callback when drag ends
- `isDragging: boolean` - Whether any item is being dragged
- `isDropTarget: boolean` - Whether this pane can accept the dragged item
- `onItemUpdate: (item: TodoItem) => void` - Callback when item is updated
- `onItemDelete: (itemId: string) => void` - Callback when item is deleted

### TodoItemCard.tsx
Card component for displaying TODO items in panes.

**Features:**
- Draggable with visual feedback
- Shows title, description, and badges
- Displays visibility indicator (public/private)
- Shows link indicator if linked to task/subtask
- Color-coded border based on visibility
- Edit, delete, and visibility toggle actions
- Expandable linked task info panel

**Props:**
- `item: TodoItem` - The TODO item to display
- `onDragStart: (item: TodoItem) => void` - Callback when drag starts
- `onDragEnd: () => void` - Callback when drag ends
- `onUpdate: (item: TodoItem) => void` - Callback when item is updated
- `onDelete: (itemId: string) => void` - Callback when item is deleted
- `onEdit?: (item: TodoItem) => void` - Optional callback when edit is clicked
- `draggable?: boolean` - Whether the card is draggable (default: true)

### TodoItemFormModal.tsx
Modal form for creating and editing TODO items.

**Features:**
- Create and edit modes
- Form validation (title required, max lengths)
- Target date picker
- Visibility toggle (public/private)
- Task/subtask search and linking
- Real-time character count
- Error handling and display

**Props:**
- `isOpen: boolean` - Whether the modal is open
- `onClose: () => void` - Callback when modal is closed
- `onSuccess: () => void` - Callback when form is successfully submitted
- `item?: TodoItem` - Optional TODO item for edit mode

**Form Fields:**
- Title (required, max 255 characters)
- Description (optional, max 2000 characters)
- Target Date (required, date picker)
- Visibility (radio: Private/Public)
- Link to Task/Subtask (optional, searchable dropdown)

**Validation:**
- Title: Required, 1-255 characters
- Description: Optional, max 2000 characters
- Target Date: Required, valid date
- Linked Entity: If entity type is set, ID must be selected from dropdown

## Styling

All styles are in `todo.css` with the following features:
- Responsive grid layout (4 columns → 2 columns → 1 column)
- Smooth drag and drop animations
- Color-coded panes and items
- Accessibility support (reduced motion, keyboard navigation)
- Dark mode support
- Print styles

## Usage Example

### Basic TODO Page with TimePanes

```tsx
import TimePanes from './components/todo/TimePanes'
import { TodoItem } from './types/todo'

function TodoPage() {
  const [todoItems, setTodoItems] = useState<TodoItem[]>([])
  
  const handleItemMove = (itemId: string, newDate: Date) => {
    // Optimistic update
    setTodoItems(items => 
      items.map(item => 
        item.id === itemId 
          ? { ...item, target_date: formatDateToISO(newDate) }
          : item
      )
    )
  }
  
  const handleItemUpdate = (updatedItem: TodoItem) => {
    setTodoItems(items =>
      items.map(item => item.id === updatedItem.id ? updatedItem : item)
    )
  }
  
  const handleItemDelete = (itemId: string) => {
    setTodoItems(items => items.filter(item => item.id !== itemId))
  }
  
  return (
    <TimePanes
      todoItems={todoItems}
      onItemMove={handleItemMove}
      onItemUpdate={handleItemUpdate}
      onItemDelete={handleItemDelete}
    />
  )
}
```

### Using TodoItemFormModal

```tsx
import { useState } from 'react'
import TodoItemFormModal from './components/todo/TodoItemFormModal'
import { TodoItem } from './types/todo'

function TodoPage() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<TodoItem | undefined>()
  
  const handleCreateClick = () => {
    setEditingItem(undefined)
    setIsModalOpen(true)
  }
  
  const handleEditClick = (item: TodoItem) => {
    setEditingItem(item)
    setIsModalOpen(true)
  }
  
  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingItem(undefined)
  }
  
  const handleModalSuccess = () => {
    // Refresh TODO items from API
    fetchTodoItems()
  }
  
  return (
    <div>
      <button onClick={handleCreateClick}>Create TODO</button>
      
      <TodoItemFormModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onSuccess={handleModalSuccess}
        item={editingItem}
      />
      
      {/* Rest of the page */}
    </div>
  )
}
```

## Drag and Drop Implementation

The drag and drop functionality uses native HTML5 drag and drop API:

1. **Drag Start**: User starts dragging a TODO item card
   - `draggedItem` state is set in TimePanes
   - Card opacity changes to indicate dragging

2. **Drag Over**: User drags over a pane
   - Pane shows visual feedback (border highlight, scale up)
   - Drop indicator appears

3. **Drop**: User drops the item on a pane
   - Optimistic UI update (immediate visual change)
   - API call to persist the move
   - Server response updates the item

4. **Drag End**: Drag operation completes
   - `draggedItem` state is cleared
   - Visual feedback is removed

## Requirements Satisfied

- ✅ 2.1: Visibility toggle for TODO items (public/private)
- ✅ 2.5: Form validation for TODO items
- ✅ 3.2: Optional linking to tasks/subtasks
- ✅ 4.1: Four time-based panes with labels and dates
- ✅ 4.2: Panes calculated relative to current date
- ✅ 4.3: Target date selection in form
- ✅ 4.4: Drag and drop between panes
- ✅ 4.5: Target date updated when moved
- ✅ 6.1: Modern card layout with styling
- ✅ 6.2: Smooth drag and drop interactions
- ✅ 8.7: Input validation with field validators
