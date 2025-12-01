import React, { useState, useEffect } from 'react'
import api from '../../services/api'

interface EntityNote {
  id: string
  entity_type: string
  entity_id: string
  note_text: string
  created_by: string
  created_at: string
  creator_name: string
  creator_email: string
}

interface EntityNotesProps {
  entityType: string
  entityId: string
}

const EntityNotes: React.FC<EntityNotesProps> = ({ entityType, entityId }) => {
  const [notes, setNotes] = useState<EntityNote[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newNoteText, setNewNoteText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)

  const loadNotes = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get(`/hierarchy/${entityType}/${entityId}/notes`)
      setNotes(response.data || response)
    } catch (err: any) {
      console.error('Error loading notes:', err)
      // Check if it's a connection error
      if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error') || err.message?.includes('ERR_CONNECTION_REFUSED')) {
        setError('Cannot connect to server. Please make sure the backend API is running on port 8007.')
      } else if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.')
      } else {
        setError(err.response?.data?.detail || 'Failed to load notes')
      }
      // Set empty notes array so component doesn't break
      setNotes([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadNotes()
  }, [entityType, entityId])

  const handleSubmitNote = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!newNoteText.trim()) {
      return
    }

    try {
      setSubmitting(true)
      setError(null)
      
      await api.post(`/hierarchy/${entityType}/${entityId}/notes`, {
        note_text: newNoteText.trim()
      })
      
      setNewNoteText('')
      setShowAddForm(false)
      await loadNotes()
    } catch (err: any) {
      console.error('Error creating note:', err)
      setError(err.response?.data?.detail || 'Failed to create note')
    } finally {
      setSubmitting(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    
    // Format: "Monday, Nov 15, 2025 at 11:45 AM"
    return date.toLocaleDateString('en-US', { 
      weekday: 'long',
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with Add Note Button */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
          Notes & Comments
          {notes.length > 0 && (
            <span className="ml-2 text-sm font-normal px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
              {notes.length}
            </span>
          )}
        </h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
        >
          {showAddForm ? 'Cancel' : '+ Add Note'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Add Note Form */}
      {showAddForm && (
        <form onSubmit={handleSubmitNote} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <textarea
            value={newNoteText}
            onChange={(e) => setNewNoteText(e.target.value)}
            placeholder="Write your note or comment here..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            disabled={submitting}
            autoFocus
          />
          <div className="flex justify-end gap-2 mt-3">
            <button
              type="button"
              onClick={() => {
                setShowAddForm(false)
                setNewNoteText('')
              }}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm"
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              disabled={submitting || !newNoteText.trim()}
            >
              {submitting ? 'Posting...' : 'Post Note'}
            </button>
          </div>
        </form>
      )}

      {/* Notes List - Scrollable */}
      <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
        {notes.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
              />
            </svg>
            <p className="text-sm">No notes yet. Be the first to add one!</p>
          </div>
        ) : (
          notes.map((note) => (
            <div
              key={note.id}
              className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow"
              style={{
                backgroundColor: 'var(--surface-color)',
                borderColor: 'var(--border-color)'
              }}
            >
              {/* Note Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0"
                    style={{
                      backgroundColor: 'var(--primary-color)',
                      color: 'white',
                      opacity: 0.9
                    }}
                  >
                    {note.creator_name?.charAt(0).toUpperCase() || '?'}
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                      {note.creator_name || 'Unknown User'}
                    </p>
                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                      {formatDate(note.created_at)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Note Content - Scrollable for long notes */}
              <div 
                className="mt-2 pl-0 max-h-40 overflow-y-auto"
                style={{
                  backgroundColor: 'var(--background-color)',
                  padding: '12px',
                  borderRadius: '6px',
                  border: '1px solid var(--border-color)'
                }}
              >
                <p className="text-sm whitespace-pre-wrap leading-relaxed" style={{ color: 'var(--text-primary)' }}>
                  {note.note_text}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default EntityNotes
