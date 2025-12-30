/**
 * CommentsSection Component
 * Displays comments in chronological order with author, timestamp, and text
 * Shows "edited" indicator for edited comments
 * Includes "Add Comment" form with rich text formatting support
 * Supports edit/delete for own comments, @mention autocomplete, and file attachments
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.13
 */
import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import api from '../../services/api'

interface Comment {
  id: string
  comment_text: string
  author_id: string
  author_name?: string
  created_at: string
  updated_at: string
  is_edited: boolean
  edited_at?: string
  mentioned_users?: string
  attachments?: string
}

interface SystemNote {
  id: string
  type: 'status_change' | 'assignment_change' | 'field_update'
  timestamp: string
  changed_by: string
  changed_by_name: string
  from_status?: string
  to_status?: string
  from_value?: string
  to_value?: string
  field_name?: string
  resolution_type?: string
  notes?: string
}

interface User {
  id: string
  full_name: string
  email: string
}

interface CommentsSectionProps {
  entityType: 'bug' | 'test_case'
  entityId: string
  onCommentAdded?: () => void
  showSystemNotes?: boolean // Whether to show system-generated notes
}

export default function CommentsSection({
  entityType,
  entityId,
  onCommentAdded,
  showSystemNotes = true
}: CommentsSectionProps) {
  const { user } = useAuth()
  const [comments, setComments] = useState<Comment[]>([])
  const [systemNotes, setSystemNotes] = useState<SystemNote[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newComment, setNewComment] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [filterType, setFilterType] = useState<'all' | 'comments' | 'system'>('all')
  
  // Edit state
  const [editingCommentId, setEditingCommentId] = useState<string | null>(null)
  const [editText, setEditText] = useState('')
  const [isUpdating, setIsUpdating] = useState(false)
  
  // @mention autocomplete state
  const [showMentionSuggestions, setShowMentionSuggestions] = useState(false)
  const [mentionQuery, setMentionQuery] = useState('')
  const [users, setUsers] = useState<User[]>([])
  const [selectedMentionIndex, setSelectedMentionIndex] = useState(0)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  // File attachment state
  const [attachments, setAttachments] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  useEffect(() => {
    loadComments()
    loadUsers()
    if (showSystemNotes && entityType === 'bug') {
      loadSystemNotes()
    }
  }, [entityType, entityId, showSystemNotes])
  
  const loadComments = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const endpoint = entityType === 'bug' 
        ? `/bugs/${entityId}/comments`
        : `/test-cases/${entityId}/comments`
      
      const data = await api.get(endpoint)
      setComments(data)
    } catch (err: any) {
      console.error('Failed to load comments:', err)
      setError(err.message || 'Failed to load comments')
      setComments([])
    } finally {
      setIsLoading(false)
    }
  }
  
  const loadUsers = async () => {
    try {
      const data = await api.getUsers()
      setUsers(data)
    } catch (err) {
      console.error('Failed to load users:', err)
    }
  }
  
  const loadSystemNotes = async () => {
    try {
      const data = await api.get(`/bugs/${entityId}/history`)
      setSystemNotes(data)
    } catch (err) {
      console.error('Failed to load system notes:', err)
      setSystemNotes([])
    }
  }
  
  const handleAddComment = async () => {
    if (!newComment.trim()) return
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      const endpoint = entityType === 'bug'
        ? `/bugs/${entityId}/comments`
        : `/test-cases/${entityId}/comments`
      
      // Extract mentioned users
      const mentionedUserIds = extractMentionedUsers(newComment)
      
      await api.post(endpoint, {
        comment_text: newComment,
        mentioned_users: mentionedUserIds.length > 0 ? JSON.stringify(mentionedUserIds) : undefined
      })
      
      setNewComment('')
      setAttachments([])
      await loadComments()
      
      if (onCommentAdded) {
        onCommentAdded()
      }
    } catch (err: any) {
      console.error('Failed to add comment:', err)
      setError(err.message || 'Failed to add comment')
    } finally {
      setIsSubmitting(false)
    }
  }
  
  const handleEditComment = async (commentId: string) => {
    if (!editText.trim()) return
    
    setIsUpdating(true)
    setError(null)
    
    try {
      await api.put(`/comments/${commentId}`, {
        comment_text: editText
      })
      
      setEditingCommentId(null)
      setEditText('')
      await loadComments()
    } catch (err: any) {
      console.error('Failed to update comment:', err)
      setError(err.message || 'Failed to update comment')
    } finally {
      setIsUpdating(false)
    }
  }
  
  const handleDeleteComment = async (commentId: string) => {
    if (!confirm('Are you sure you want to delete this comment?')) return
    
    setError(null)
    
    try {
      await api.delete(`/comments/${commentId}?entity_type=${entityType}`)
      await loadComments()
    } catch (err: any) {
      console.error('Failed to delete comment:', err)
      setError(err.message || 'Failed to delete comment')
    }
  }
  
  const startEditing = (comment: Comment) => {
    setEditingCommentId(comment.id)
    setEditText(comment.comment_text)
  }
  
  const cancelEditing = () => {
    setEditingCommentId(null)
    setEditText('')
  }
  
  const canEditComment = (comment: Comment) => {
    if (comment.author_id !== user?.id) return false
    
    // Check if within 15 minutes
    const createdAt = new Date(comment.created_at).getTime()
    const now = new Date().getTime()
    const diffMinutes = (now - createdAt) / 60000
    
    return diffMinutes <= 15
  }
  
  const canDeleteComment = (comment: Comment) => {
    return comment.author_id === user?.id
  }
  
  // Extract @mentioned user IDs from text
  const extractMentionedUsers = (text: string): string[] => {
    const mentionRegex = /@\[([^\]]+)\]\(([^)]+)\)/g
    const matches = [...text.matchAll(mentionRegex)]
    return matches.map(match => match[2])
  }
  
  // Handle @mention input
  const handleCommentChange = (text: string, isEdit: boolean = false) => {
    if (isEdit) {
      setEditText(text)
    } else {
      setNewComment(text)
    }
    
    // Check for @ mention trigger
    const cursorPosition = textareaRef.current?.selectionStart || 0
    const textBeforeCursor = text.substring(0, cursorPosition)
    const lastAtIndex = textBeforeCursor.lastIndexOf('@')
    
    if (lastAtIndex !== -1) {
      const textAfterAt = textBeforeCursor.substring(lastAtIndex + 1)
      
      // Check if there's a space after @, if so, don't show suggestions
      if (!textAfterAt.includes(' ') && textAfterAt.length >= 0) {
        setMentionQuery(textAfterAt.toLowerCase())
        setShowMentionSuggestions(true)
        setSelectedMentionIndex(0)
      } else {
        setShowMentionSuggestions(false)
      }
    } else {
      setShowMentionSuggestions(false)
    }
  }
  
  const insertMention = (user: User, isEdit: boolean = false) => {
    const currentText = isEdit ? editText : newComment
    const cursorPosition = textareaRef.current?.selectionStart || 0
    const textBeforeCursor = currentText.substring(0, cursorPosition)
    const textAfterCursor = currentText.substring(cursorPosition)
    const lastAtIndex = textBeforeCursor.lastIndexOf('@')
    
    const beforeMention = currentText.substring(0, lastAtIndex)
    const mention = `@[${user.full_name}](${user.id})`
    const newText = beforeMention + mention + ' ' + textAfterCursor
    
    if (isEdit) {
      setEditText(newText)
    } else {
      setNewComment(newText)
    }
    
    setShowMentionSuggestions(false)
    setMentionQuery('')
    
    // Focus back on textarea
    setTimeout(() => {
      textareaRef.current?.focus()
    }, 0)
  }
  
  const handleKeyDown = (e: React.KeyboardEvent, isEdit: boolean = false) => {
    if (showMentionSuggestions) {
      const filteredUsers = users.filter(u =>
        u.full_name.toLowerCase().includes(mentionQuery) ||
        u.email.toLowerCase().includes(mentionQuery)
      )
      
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedMentionIndex((prev) =>
          prev < filteredUsers.length - 1 ? prev + 1 : prev
        )
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedMentionIndex((prev) => (prev > 0 ? prev - 1 : 0))
      } else if (e.key === 'Enter' && filteredUsers.length > 0) {
        e.preventDefault()
        insertMention(filteredUsers[selectedMentionIndex], isEdit)
      } else if (e.key === 'Escape') {
        setShowMentionSuggestions(false)
      }
    }
  }
  
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setAttachments(prev => [...prev, ...files])
  }
  
  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // Combine comments and system notes into a unified timeline
  const getUnifiedTimeline = () => {
    const items: Array<{ type: 'comment' | 'system'; data: Comment | SystemNote; timestamp: string }> = []
    
    // Add comments
    if (filterType === 'all' || filterType === 'comments') {
      comments.forEach(comment => {
        items.push({
          type: 'comment',
          data: comment,
          timestamp: comment.created_at
        })
      })
    }
    
    // Add system notes
    if ((filterType === 'all' || filterType === 'system') && showSystemNotes && entityType === 'bug') {
      systemNotes.forEach(note => {
        items.push({
          type: 'system',
          data: note,
          timestamp: note.timestamp
        })
      })
    }
    
    // Sort by timestamp
    items.sort((a, b) => {
      const dateA = new Date(a.timestamp).getTime()
      const dateB = new Date(b.timestamp).getTime()
      return sortOrder === 'asc' ? dateA - dateB : dateB - dateA
    })
    
    return items
  }
  
  const timeline = getUnifiedTimeline()
  
  const renderSystemNote = (note: SystemNote) => {
    let icon = '🔄'
    let title = ''
    let description = ''
    
    if (note.type === 'status_change') {
      icon = '🔄'
      title = 'Status changed'
      description = note.from_status 
        ? `from ${note.from_status} to ${note.to_status}`
        : `to ${note.to_status}`
      
      if (note.resolution_type) {
        description += ` (${note.resolution_type})`
      }
    } else if (note.type === 'assignment_change') {
      icon = '👤'
      title = 'Assignment changed'
      description = note.from_value
        ? `from ${note.from_value} to ${note.to_value}`
        : `assigned to ${note.to_value}`
    } else if (note.type === 'field_update') {
      icon = '✏️'
      title = `${note.field_name} updated`
      description = note.from_value
        ? `from "${note.from_value}" to "${note.to_value}"`
        : `set to "${note.to_value}"`
    }
    
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className="text-2xl">{icon}</div>
          
          {/* Content */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="font-medium text-blue-900">{title}</span>
              <span className="text-xs text-blue-600">{formatDate(note.timestamp)}</span>
            </div>
            <p className="text-sm text-blue-800">{description}</p>
            {note.notes && (
              <p className="text-sm text-blue-700 mt-1 italic">{note.notes}</p>
            )}
            <p className="text-xs text-blue-600 mt-1">by {note.changed_by_name}</p>
          </div>
        </div>
      </div>
    )
  }
  
  // Format comment text with basic rich text support
  const formatCommentText = (text: string) => {
    // Convert **bold** to <strong>
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Convert *italic* to <em>
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Convert `code` to <code>
    formatted = formatted.replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">$1</code>')
    // Convert URLs to links
    formatted = formatted.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline">$1</a>'
    )
    // Convert line breaks
    formatted = formatted.replace(/\n/g, '<br />')
    
    return formatted
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">Loading comments...</div>
      </div>
    )
  }
  
  return (
    <div className="space-y-4">
      {/* Header with filters and sort toggle */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-gray-900">
            Activity ({timeline.length})
          </h3>
          
          {/* Filter buttons */}
          {showSystemNotes && entityType === 'bug' && (
            <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setFilterType('all')}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  filterType === 'all'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilterType('comments')}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  filterType === 'comments'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Comments ({comments.length})
              </button>
              <button
                onClick={() => setFilterType('system')}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  filterType === 'system'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                System ({systemNotes.length})
              </button>
            </div>
          )}
        </div>
        
        <button
          onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
        >
          {sortOrder === 'asc' ? (
            <>
              <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
              </svg>
              Oldest first
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
              </svg>
              Newest first
            </>
          )}
        </button>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}
      
      {/* Add Comment Form */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 relative">
        <label htmlFor="new-comment" className="block text-sm font-medium text-gray-700 mb-2">
          Add a comment
        </label>
        <textarea
          ref={textareaRef}
          id="new-comment"
          value={newComment}
          onChange={(e) => handleCommentChange(e.target.value)}
          onKeyDown={(e) => handleKeyDown(e)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          placeholder="Write your comment here... Use @ to mention users, **bold**, *italic*, `code`"
          disabled={isSubmitting}
        />
        
        {/* @mention suggestions dropdown */}
        {showMentionSuggestions && (
          <div className="absolute z-10 mt-1 w-64 bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
            {users
              .filter(u =>
                u.full_name.toLowerCase().includes(mentionQuery) ||
                u.email.toLowerCase().includes(mentionQuery)
              )
              .slice(0, 5)
              .map((u, index) => (
                <button
                  key={u.id}
                  onClick={() => insertMention(u)}
                  className={`w-full text-left px-3 py-2 hover:bg-blue-50 flex items-center gap-2 ${
                    index === selectedMentionIndex ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                    {u.full_name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">{u.full_name}</div>
                    <div className="text-xs text-gray-500">{u.email}</div>
                  </div>
                </button>
              ))}
            {users.filter(u =>
              u.full_name.toLowerCase().includes(mentionQuery) ||
              u.email.toLowerCase().includes(mentionQuery)
            ).length === 0 && (
              <div className="px-3 py-2 text-sm text-gray-500">No users found</div>
            )}
          </div>
        )}
        
        {/* File attachments */}
        {attachments.length > 0 && (
          <div className="mt-2 space-y-1">
            {attachments.map((file, index) => (
              <div key={index} className="flex items-center gap-2 text-sm bg-white border border-gray-200 rounded px-2 py-1">
                <svg className="w-4 h-4 text-gray-500" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
                <span className="flex-1 truncate">{file.name}</span>
                <button
                  onClick={() => removeAttachment(index)}
                  className="text-red-600 hover:text-red-700"
                >
                  <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
        
        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center gap-2">
            <div className="text-xs text-gray-500">
              @mention, **bold**, *italic*, `code`
            </div>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-gray-600 hover:text-gray-900 p-1"
              title="Attach files"
            >
              <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </button>
          </div>
          <button
            onClick={handleAddComment}
            disabled={!newComment.trim() || isSubmitting}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Adding...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M12 4v16m8-8H4" />
                </svg>
                Add Comment
              </>
            )}
          </button>
        </div>
      </div>
      
      {/* Activity Timeline */}
      {timeline.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="text-gray-400 text-4xl mb-2">💬</div>
          <p className="text-gray-600">
            {filterType === 'comments' ? 'No comments yet' : 
             filterType === 'system' ? 'No system activity yet' : 
             'No activity yet'}
          </p>
          {filterType !== 'system' && (
            <p className="text-gray-500 text-sm mt-1">Be the first to add a comment</p>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {timeline.map((item, index) => (
            item.type === 'system' ? (
              <div key={`system-${item.data.id}-${index}`}>
                {renderSystemNote(item.data as SystemNote)}
              </div>
            ) : (
              (() => {
                const comment = item.data as Comment
                return (
            <div
              key={comment.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
            >
              {editingCommentId === comment.id ? (
                /* Edit Mode */
                <div className="space-y-3">
                  <textarea
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    disabled={isUpdating}
                  />
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={cancelEditing}
                      disabled={isUpdating}
                      className="px-3 py-1.5 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleEditComment(comment.id)}
                      disabled={!editText.trim() || isUpdating}
                      className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isUpdating ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              ) : (
                /* View Mode */
                <>
                  {/* Comment Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {/* Avatar */}
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                        {(comment.author_name || 'U').charAt(0).toUpperCase()}
                      </div>
                      
                      {/* Author and timestamp */}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900">
                            {comment.author_name || 'Unknown User'}
                          </span>
                          {comment.author_id === user?.id && (
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
                              You
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <span>{formatDate(comment.created_at)}</span>
                          {comment.is_edited && (
                            <>
                              <span>•</span>
                              <span className="italic">
                                edited {comment.edited_at ? formatDate(comment.edited_at) : ''}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* Action buttons */}
                    {(canEditComment(comment) || canDeleteComment(comment)) && (
                      <div className="flex items-center gap-1">
                        {canEditComment(comment) && (
                          <button
                            onClick={() => startEditing(comment)}
                            className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                            title="Edit comment (within 15 minutes)"
                          >
                            <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                              <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                        )}
                        {canDeleteComment(comment) && (
                          <button
                            onClick={() => handleDeleteComment(comment.id)}
                            className="p-1.5 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                            title="Delete comment"
                          >
                            <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Comment Text */}
                  <div
                    className="text-gray-700 prose prose-sm max-w-none"
                    dangerouslySetInnerHTML={{ __html: formatCommentText(comment.comment_text) }}
                  />
                  
                  {/* Attachments (if any) */}
                  {comment.attachments && comment.attachments !== '[]' && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                          <path d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                        </svg>
                        <span>Has attachments</span>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
                )
              })()
            )
          ))}
        </div>
      )}
    </div>
  )
}
