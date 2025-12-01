/**
 * Time Pane Component
 * Individual pane for displaying TODO items for a specific date
 * Requirements: 4.1, 4.2, 6.1
 */

import { useState } from 'react'
import type { Pane, TodoItem } from '../../types/todo'
import TodoItemCard from './TodoItemCard'

interface TimePaneProps {
  pane: Pane
  onDragStart: (item: TodoItem) => void
  onDrop: (pane: Pane) => void
  onDragEnd: () => void
  isDragging: boolean
  isDropTarget: boolean
  onItemUpdate: (item: TodoItem) => void
  onItemDelete: (itemId: string) => void
  onItemEdit?: (item: TodoItem) => void
}

export default function TimePane({
  pane,
  onDragStart,
  onDrop,
  onDragEnd,
  isDragging,
  isDropTarget,
  onItemUpdate,
  onItemDelete,
  onItemEdit
}: TimePaneProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  
  /**
   * Format date for display (e.g., "Nov 28")
   */
  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
  }
  
  /**
   * Get day of week (e.g., "Friday")
   */
  const getDayOfWeek = (date: Date): string => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long'
    })
  }
  
  /**
   * Handle drag over event
   */
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    if (isDropTarget) {
      setIsDragOver(true)
    }
  }
  
  /**
   * Handle drag leave event
   */
  const handleDragLeave = () => {
    setIsDragOver(false)
  }
  
  /**
   * Handle drop event
   */
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    onDrop(pane)
  }
  
  /**
   * Get pane color based on label
   */
  const getPaneColor = (): string => {
    switch (pane.label) {
      case 'Yesterday':
        return 'border-gray-300'
      case 'Today':
        return 'border-blue-500'
      case 'Tomorrow':
        return 'border-green-500'
      case 'Day After Tomorrow':
        return 'border-purple-500'
      default:
        return 'border-gray-300'
    }
  }
  
  /**
   * Get header background color based on label
   */
  const getHeaderColor = (): string => {
    switch (pane.label) {
      case 'Yesterday':
        return 'bg-gray-50'
      case 'Today':
        return 'bg-blue-50'
      case 'Tomorrow':
        return 'bg-green-50'
      case 'Day After Tomorrow':
        return 'bg-purple-50'
      default:
        return 'bg-gray-50'
    }
  }
  
  return (
    <div
      className={`time-pane ${getPaneColor()} ${
        isDragOver && isDropTarget ? 'drag-over' : ''
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Pane Header */}
      <div className={`time-pane-header ${getHeaderColor()}`}>
        <div className="time-pane-label">
          <h3 className="time-pane-title">{pane.label}</h3>
          <p className="time-pane-date">
            {getDayOfWeek(pane.date)} • {formatDate(pane.date)}
          </p>
        </div>
        <div className="time-pane-count">
          <span className="count-badge">{pane.items.length}</span>
        </div>
      </div>
      
      {/* Pane Content */}
      <div className="time-pane-content">
        {pane.items.length === 0 ? (
          <div className="time-pane-empty">
            <svg
              className="empty-icon"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p className="empty-text">No items for this day</p>
          </div>
        ) : (
          <div className="time-pane-items">
            {pane.items.map((item) => (
              <TodoItemCard
                key={item.id}
                item={item}
                onDragStart={onDragStart}
                onDragEnd={onDragEnd}
                onUpdate={onItemUpdate}
                onDelete={onItemDelete}
                onEdit={onItemEdit}
                draggable={true}
              />
            ))}
          </div>
        )}
        
        {/* Drop indicator */}
        {isDragOver && isDropTarget && (
          <div className="drop-indicator">
            <svg
              className="drop-icon"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
            <p className="drop-text">Drop here</p>
          </div>
        )}
      </div>
    </div>
  )
}
