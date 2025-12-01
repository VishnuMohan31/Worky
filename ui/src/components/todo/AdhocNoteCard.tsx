/**
 * ADHOC Note Card Component
 * Displays individual sticky note with edit/delete actions and drag handle
 * Requirements: 5.2, 5.3, 5.5
 */

import { useState } from 'react'
import type { AdhocNote } from '../../types/todo'

interface AdhocNoteCardProps {
  note: AdhocNote
  onEdit: (note: AdhocNote) => void
  onDelete: (noteId: string) => void
  onReorder: (noteId: string, newPosition: number) => void
}

export default function AdhocNoteCard({
  note,
  onEdit,
  onDelete,
  onReorder
}: AdhocNoteCardProps) {
  const [isDeleting, setIsDeleting] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  /**
   * Handle drag start event
   */
  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('adhoc-note-id', note.id)
    e.dataTransfer.setData('adhoc-note-position', note.position.toString())
    setIsDragging(true)
  }

  /**
   * Handle drag end event
   */
  const handleDragEnd = () => {
    setIsDragging(false)
  }

  /**
   * Handle drag over event (allow drop)
   */
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  /**
   * Handle drop event (reorder notes)
   */
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    
    const draggedNoteId = e.dataTransfer.getData('adhoc-note-id')
    const draggedPosition = parseInt(e.dataTransfer.getData('adhoc-note-position'), 10)
    
    // Don't do anything if dropped on itself
    if (draggedNoteId === note.id) {
      return
    }
    
    // Reorder: move dragged note to this note's position
    onReorder(draggedNoteId, note.position)
  }

  /**
   * Handle edit button click
   */
  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation()
    onEdit(note)
  }

  /**
   * Handle delete button click
   */
  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation()
    
    if (!confirm('Are you sure you want to delete this note?')) {
      return
    }

    setIsDeleting(true)
    try {
      await onDelete(note.id)
    } catch (error) {
      console.error('Failed to delete ADHOC note:', error)
      setIsDeleting(false)
    }
  }

  /**
   * Get random rotation for sticky note effect
   * Use note ID to ensure consistent rotation for each note
   */
  const getRotation = (): number => {
    // Generate a pseudo-random rotation based on note ID
    const hash = note.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    const rotations = [-2, -1, 0, 1, 2]
    return rotations[hash % rotations.length]
  }

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Allow Enter or Space to edit note
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onEdit(note)
    }
    // Allow Delete key to delete note
    if (e.key === 'Delete') {
      e.preventDefault()
      handleDelete(e as any)
    }
  }

  return (
    <div
      className={`adhoc-note-card ${isDragging ? 'dragging' : ''} ${isDeleting ? 'deleting' : ''}`}
      style={{
        backgroundColor: note.color,
        transform: `rotate(${getRotation()}deg)`
      }}
      draggable={!isDeleting}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onKeyDown={handleKeyDown}
      role="article"
      aria-label={`ADHOC note: ${note.title}`}
      tabIndex={0}
    >
      {/* Drag Handle */}
      <div className="adhoc-note-drag-handle" aria-label="Drag to reorder">
        <svg
          className="w-4 h-4"
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

      {/* Note Content */}
      <div className="adhoc-note-content">
        <h4 className="adhoc-note-title">{note.title}</h4>
        {note.content && (
          <p className="adhoc-note-text">{note.content}</p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="adhoc-note-actions">
        <button
          onClick={handleEdit}
          className="adhoc-note-action-button adhoc-note-edit-button"
          title="Edit note"
          aria-label="Edit note"
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
        </button>
        <button
          onClick={handleDelete}
          className="adhoc-note-action-button adhoc-note-delete-button"
          title="Delete note"
          aria-label="Delete note"
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
        </button>
      </div>

      {/* Sticky Note Shadow Effect */}
      <div className="adhoc-note-shadow" aria-hidden="true"></div>
    </div>
  )
}
