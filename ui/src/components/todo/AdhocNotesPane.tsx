/**
 * ADHOC Notes Pane Component
 * Container for displaying and managing ADHOC sticky notes
 * Requirements: 5.1, 5.3, 5.4, 8.8
 */

import { useState } from 'react'
import type { AdhocNote } from '../../types/todo'
import AdhocNoteCard from './AdhocNoteCard'
import AdhocNoteFormModal from './AdhocNoteFormModal'
import { reorderAdhocNote } from '../../services/todoApi'
import { useToast } from '../common/ToastContainer'

interface AdhocNotesPaneProps {
  notes: AdhocNote[]
  onNoteCreate: (note: Partial<AdhocNote>) => void
  onNoteUpdate: (note: AdhocNote) => void
  onNoteDelete: (noteId: string) => void
  onNoteReorder: (noteId: string, newPosition: number) => void
  onRefresh?: () => void
}

export default function AdhocNotesPane({
  notes,
  onNoteCreate,
  onNoteUpdate,
  onNoteDelete,
  onNoteReorder,
  onRefresh
}: AdhocNotesPaneProps) {
  const toast = useToast()
  const [isFormModalOpen, setIsFormModalOpen] = useState(false)
  const [editingNote, setEditingNote] = useState<AdhocNote | undefined>(undefined)
  const [isReordering, setIsReordering] = useState(false)

  /**
   * Handle opening the form modal for creating a new note
   */
  const handleAddNote = () => {
    setEditingNote(undefined)
    setIsFormModalOpen(true)
  }

  /**
   * Handle opening the form modal for editing an existing note
   */
  const handleEditNote = (note: AdhocNote) => {
    setEditingNote(note)
    setIsFormModalOpen(true)
  }

  /**
   * Handle closing the form modal
   */
  const handleCloseModal = () => {
    setIsFormModalOpen(false)
    setEditingNote(undefined)
  }



  /**
   * Handle reordering notes with optimistic updates and API persistence
   * Requirements: 5.4
   */
  const handleReorder = async (draggedNoteId: string, targetPosition: number) => {
    if (isReordering) return

    try {
      setIsReordering(true)

      // Find the dragged note
      const draggedNote = notes.find(n => n.id === draggedNoteId)
      if (!draggedNote) return

      // Optimistic update - update UI immediately
      onNoteReorder(draggedNoteId, targetPosition)

      // Persist to API
      await reorderAdhocNote(draggedNoteId, { position: targetPosition })

      // Show success toast
      toast.showSuccess('Note reordered successfully')

      // Refresh to get updated positions from server
      if (onRefresh) {
        onRefresh()
      }
    } catch (error: any) {
      console.error('Failed to reorder ADHOC note:', error)
      
      // Show error toast with user-friendly message
      const errorMessage = error?.userMessage || 'Failed to reorder note. Please try again.'
      toast.showError(errorMessage)
      
      // Refresh to revert optimistic update
      if (onRefresh) {
        onRefresh()
      }
    } finally {
      setIsReordering(false)
    }
  }

  /**
   * Sort notes by position
   */
  const sortedNotes = [...notes].sort((a, b) => a.position - b.position)

  return (
    <div className="adhoc-notes-pane">
      {/* Header */}
      <div className="adhoc-notes-header">
        <div className="adhoc-notes-title-section">
          <h3 className="adhoc-notes-title">ADHOC Notes</h3>
          <span className="adhoc-notes-count">{notes.length}</span>
        </div>
        <button
          onClick={handleAddNote}
          className="add-note-button"
          aria-label="Add new ADHOC note"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M12 4v16m8-8H4" />
          </svg>
          <span className="add-note-text">Add Note</span>
        </button>
      </div>

      {/* Notes Grid */}
      <div className="adhoc-notes-content">
        {sortedNotes.length === 0 ? (
          <div className="adhoc-notes-empty">
            <svg
              className="empty-icon"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="empty-text">No ADHOC notes yet</p>
            <p className="empty-subtext">Click "Add Note" to create your first sticky note</p>
          </div>
        ) : (
          <div className="adhoc-notes-grid">
            {sortedNotes.map((note) => (
              <AdhocNoteCard
                key={note.id}
                note={note}
                onEdit={handleEditNote}
                onDelete={onNoteDelete}
                onReorder={handleReorder}
              />
            ))}
          </div>
        )}
      </div>

      {/* Form Modal */}
      <AdhocNoteFormModal
        isOpen={isFormModalOpen}
        note={editingNote}
        onClose={handleCloseModal}
        onSuccess={() => {
          if (onRefresh) {
            onRefresh()
          }
        }}
      />

      {/* Reordering Overlay */}
      {isReordering && (
        <div className="moving-overlay">
          <div className="moving-spinner">Reordering...</div>
        </div>
      )}
    </div>
  )
}
