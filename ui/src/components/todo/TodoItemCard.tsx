/**
 * TODO Item Card Component
 * Displays individual TODO item with all details, actions, and linked task info
 * Requirements: 2.1, 2.2, 3.3, 6.1, 6.3, 6.4
 */

import { useState } from 'react'
import type { TodoItem } from '../../types/todo'
import TaskLinkInfoPanel from './TaskLinkInfoPanel'

interface TodoItemCardProps {
  item: TodoItem
  onDragStart: (item: TodoItem) => void
  onDragEnd: () => void
  onUpdate: (item: TodoItem) => void
  onDelete: (itemId: string) => void
  onEdit?: (item: TodoItem) => void
  draggable?: boolean
}

export default function TodoItemCard({
  item,
  onDragStart,
  onDragEnd,
  onUpdate,
  onDelete,
  onEdit,
  draggable = true
}: TodoItemCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  /**
   * Handle drag start event
   */
  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.effectAllowed = 'move'
    onDragStart(item)
  }

  /**
   * Get visibility color for left border
   */
  const getVisibilityColor = (): string => {
    return item.visibility === 'public' ? 'border-l-green-500' : 'border-l-blue-500'
  }

  /**
   * Get visibility icon
   */
  const getVisibilityIcon = () => {
    if (item.visibility === 'public') {
      return (
        <svg
          className="w-4 h-4 text-green-600"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-label="Public visibility"
        >
          <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
      )
    }
    return (
      <svg
        className="w-4 h-4 text-blue-600"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-label="Private visibility"
      >
        <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    )
  }

  /**
   * Get link indicator icon
   */
  const getLinkIcon = () => {
    if (!item.linked_entity_type) return null

    return (
      <svg
        className="w-4 h-4 text-purple-600"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-label={`Linked to ${item.linked_entity_type}`}
      >
        <path d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
      </svg>
    )
  }

  /**
   * Toggle visibility between public and private
   */
  const handleToggleVisibility = async (e: React.MouseEvent) => {
    e.stopPropagation()
    
    const newVisibility = item.visibility === 'public' ? 'private' : 'public'
    const updatedItem = { ...item, visibility: newVisibility }
    
    try {
      onUpdate(updatedItem)
    } catch (error) {
      console.error('Failed to toggle visibility:', error)
    }
  }

  /**
   * Handle edit button click
   */
  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (onEdit) {
      onEdit(item)
    }
  }

  /**
   * Handle delete button click
   */
  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation()
    
    if (!confirm('Are you sure you want to delete this TODO item?')) {
      return
    }

    setIsDeleting(true)
    try {
      await onDelete(item.id)
    } catch (error) {
      console.error('Failed to delete TODO item:', error)
      setIsDeleting(false)
    }
  }

  /**
   * Toggle expanded state for linked task info
   */
  const handleToggleExpand = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (item.linked_entity_info) {
      setIsExpanded(!isExpanded)
    }
  }

  /**
   * Handle keyboard navigation for drag and drop
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Allow Enter or Space to expand/collapse linked info
    if (e.key === 'Enter' || e.key === ' ') {
      if (item.linked_entity_info) {
        e.preventDefault()
        setIsExpanded(!isExpanded)
      }
    }
  }

  return (
    <div
      className={`todo-item-card ${getVisibilityColor()} ${isDeleting ? 'opacity-50' : ''}`}
      draggable={draggable && !isDeleting}
      onDragStart={handleDragStart}
      onDragEnd={onDragEnd}
      onKeyDown={handleKeyDown}
      role="article"
      aria-label={`TODO item: ${item.title}`}
      tabIndex={0}
    >
      {/* Drag Handle */}
      {draggable && (
        <div className="drag-handle" aria-label="Drag handle">
          <svg
            className="w-4 h-4 text-gray-400"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M4 8h16M4 16h16" />
          </svg>
        </div>
      )}

      {/* Card Content */}
      <div className="todo-item-content">
        {/* Header with Title and Badges */}
        <div className="todo-item-header">
          <h4 className="todo-item-title">{item.title}</h4>
          <div className="todo-item-badges">
            {getVisibilityIcon()}
            {getLinkIcon()}
          </div>
        </div>

        {/* Description */}
        {item.description && (
          <p className="todo-item-description">{item.description}</p>
        )}

        {/* Linked Entity Quick Info */}
        {item.linked_entity_info && (
          <div className="todo-item-link-info">
            <button
              onClick={handleToggleExpand}
              className="link-info-button"
              aria-expanded={isExpanded}
              aria-label={`${isExpanded ? 'Collapse' : 'Expand'} linked ${item.linked_entity_type} information`}
            >
              <span className="link-badge">
                {item.linked_entity_type === 'task' ? 'Task' : 'Subtask'}
              </span>
              <span className="link-title">{item.linked_entity_info.title}</span>
              <svg
                className={`w-4 h-4 text-gray-500 transition-transform ${
                  isExpanded ? 'rotate-180' : ''
                }`}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        )}

        {/* Expandable Linked Task Info Panel */}
        {isExpanded && item.linked_entity_info && item.linked_entity_type && (
          <TaskLinkInfoPanel
            linkedEntity={item.linked_entity_info}
            entityType={item.linked_entity_type}
          />
        )}

        {/* Action Buttons */}
        <div className="todo-item-actions">
          {/* Toggle Visibility Button */}
          <button
            onClick={handleToggleVisibility}
            className="action-button action-button-visibility"
            title={`Make ${item.visibility === 'public' ? 'private' : 'public'}`}
            aria-label={`Toggle visibility to ${item.visibility === 'public' ? 'private' : 'public'}`}
            disabled={isDeleting}
          >
            {item.visibility === 'public' ? (
              <>
                <svg
                  className="w-4 h-4"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                <span className="action-button-text">Make Private</span>
              </>
            ) : (
              <>
                <svg
                  className="w-4 h-4"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span className="action-button-text">Make Public</span>
              </>
            )}
          </button>

          {/* Edit Button */}
          {onEdit && (
            <button
              onClick={handleEdit}
              className="action-button action-button-edit"
              title="Edit TODO item"
              aria-label="Edit TODO item"
              disabled={isDeleting}
            >
              <svg
                className="w-4 h-4"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span className="action-button-text">Edit</span>
            </button>
          )}

          {/* Delete Button */}
          <button
            onClick={handleDelete}
            className="action-button action-button-delete"
            title="Delete TODO item"
            aria-label="Delete TODO item"
            disabled={isDeleting}
          >
            <svg
              className="w-4 h-4"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span className="action-button-text">Delete</span>
          </button>
        </div>
      </div>
    </div>
  )
}
