/**
 * Time Panes Container Component
 * Displays four date-based columns for TODO items
 * Requirements: 4.1, 4.2, 4.4, 4.5, 6.2, 8.8
 */

import { useState, useEffect, useMemo } from 'react'
import type { TodoItem, Pane } from '../../types/todo'
import TimePane from './TimePane'
import { moveTodoItem } from '../../services/todoApi'
import { useToast } from '../common/ToastContainer'
import './todo.css'

interface TimePanesProps {
  todoItems: TodoItem[]
  onItemMove: (itemId: string, newDate: Date) => void
  onItemUpdate: (item: TodoItem) => void
  onItemDelete: (itemId: string) => void
  onItemEdit?: (item: TodoItem) => void
  selectedDate?: Date
}

/**
 * Calculate four panes based on the selected date
 * @param baseDate - The date to calculate panes from (defaults to today)
 * @returns Array of four panes with dates and labels
 */
function calculatePanes(baseDate: Date = new Date()): Omit<Pane, 'items'>[] {
  const panes: Omit<Pane, 'items'>[] = []
  
  // Create a new date at midnight to avoid time zone issues
  const base = new Date(baseDate)
  base.setHours(0, 0, 0, 0)
  
  // Yesterday
  const yesterday = new Date(base)
  yesterday.setDate(base.getDate() - 1)
  panes.push({
    label: 'Yesterday',
    date: yesterday,
    dateString: formatDateToISO(yesterday)
  })
  
  // Today
  panes.push({
    label: 'Today',
    date: new Date(base),
    dateString: formatDateToISO(base)
  })
  
  // Tomorrow
  const tomorrow = new Date(base)
  tomorrow.setDate(base.getDate() + 1)
  panes.push({
    label: 'Tomorrow',
    date: tomorrow,
    dateString: formatDateToISO(tomorrow)
  })
  
  // Day After Tomorrow
  const dayAfterTomorrow = new Date(base)
  dayAfterTomorrow.setDate(base.getDate() + 2)
  panes.push({
    label: 'Day After Tomorrow',
    date: dayAfterTomorrow,
    dateString: formatDateToISO(dayAfterTomorrow)
  })
  
  return panes
}

/**
 * Format date to ISO string (YYYY-MM-DD)
 */
function formatDateToISO(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Filter TODO items by target date
 */
function filterItemsByDate(items: TodoItem[], dateString: string): TodoItem[] {
  return items.filter(item => item.target_date === dateString)
}

export default function TimePanes({
  todoItems,
  onItemMove,
  onItemUpdate,
  onItemDelete,
  onItemEdit,
  selectedDate
}: TimePanesProps) {
  const toast = useToast()
  const [draggedItem, setDraggedItem] = useState<TodoItem | null>(null)
  const [isMoving, setIsMoving] = useState(false)
  
  // Calculate panes based on selected date
  const panes = useMemo<Pane[]>(() => {
    const basePanes = calculatePanes(selectedDate)
    return basePanes.map(pane => ({
      ...pane,
      items: filterItemsByDate(todoItems, pane.dateString)
    }))
  }, [todoItems, selectedDate])
  
  /**
   * Handle drag start event
   */
  const handleDragStart = (item: TodoItem) => {
    setDraggedItem(item)
  }
  
  /**
   * Handle drop event on a pane
   * Updates the TODO item's target_date and persists to API
   */
  const handleDrop = async (pane: Pane) => {
    if (!draggedItem) return
    
    // Don't do anything if dropped on the same pane
    if (draggedItem.target_date === pane.dateString) {
      setDraggedItem(null)
      return
    }
    
    try {
      setIsMoving(true)
      
      // Optimistic update - update UI immediately
      onItemMove(draggedItem.id, pane.date)
      
      // Persist to API
      const updatedItem = await moveTodoItem(draggedItem.id, {
        target_date: pane.dateString
      })
      
      // Update with server response
      onItemUpdate(updatedItem)
      
      // Show success toast
      toast.showSuccess(`Moved to ${pane.label}`)
    } catch (error: any) {
      console.error('Failed to move TODO item:', error)
      
      // Show error toast with user-friendly message
      const errorMessage = error?.userMessage || 'Failed to move TODO item. Please try again.'
      toast.showError(errorMessage)
      
      // Revert optimistic update by refreshing
      // The parent component should handle this by refetching
      window.location.reload()
    } finally {
      setIsMoving(false)
      setDraggedItem(null)
    }
  }
  
  /**
   * Handle drag end event
   */
  const handleDragEnd = () => {
    setDraggedItem(null)
  }
  
  return (
    <div className="time-panes-container">
      {panes.map((pane) => (
        <TimePane
          key={pane.dateString}
          pane={pane}
          onDragStart={handleDragStart}
          onDrop={handleDrop}
          onDragEnd={handleDragEnd}
          isDragging={!!draggedItem}
          isDropTarget={draggedItem?.target_date !== pane.dateString}
          onItemUpdate={onItemUpdate}
          onItemDelete={onItemDelete}
          onItemEdit={onItemEdit}
        />
      ))}
      
      {isMoving && (
        <div className="moving-overlay">
          <div className="moving-spinner">Moving...</div>
        </div>
      )}
    </div>
  )
}
