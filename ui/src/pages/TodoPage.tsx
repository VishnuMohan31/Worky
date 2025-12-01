/**
 * TODO Dashboard Page Component
 * 
 * Main container for the TODO feature that displays:
 * - Four time-based panes (Yesterday, Today, Tomorrow, Day After Tomorrow)
 * - ADHOC notes pane for standalone sticky notes
 * 
 * Requirements: 1.5, 7.2, 7.5, 8.8
 */

import { useState, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useLanguage } from '../contexts/LanguageContext'
import { useToast } from '../components/common/ToastContainer'
import ErrorBoundary from '../components/common/ErrorBoundary'
import TodoSkeletonLoader from '../components/todo/TodoSkeletonLoader'
import TodoItemFormModal from '../components/todo/TodoItemFormModal'
import AdhocNoteFormModal from '../components/todo/AdhocNoteFormModal'
import TodoItemCard from '../components/todo/TodoItemCard'
import AdhocNoteCard from '../components/todo/AdhocNoteCard'
import { useResponsive } from '../hooks/useResponsive'
import {
  fetchTodoItems,
  fetchAdhocNotes,
  createTodoItem,
  updateTodoItem,
  deleteTodoItem,
  moveTodoItem,
  createAdhocNote,
  updateAdhocNote,
  deleteAdhocNote,
  reorderAdhocNote
} from '../services/todoApi'
import type {
  TodoItem,
  AdhocNote,
  Pane,
  CreateTodoItemRequest,
  UpdateTodoItemRequest,
  MoveTodoItemRequest,
  CreateAdhocNoteRequest,
  UpdateAdhocNoteRequest
} from '../types/todo'

/**
 * Calculate the four time-based panes relative to the selected date
 */
function calculatePanes(selectedDate: Date, todoItems: TodoItem[]): Pane[] {
  const panes: Pane[] = []
  const labels: Array<'Yesterday' | 'Today' | 'Tomorrow' | 'Day After Tomorrow'> = [
    'Yesterday',
    'Today',
    'Tomorrow',
    'Day After Tomorrow'
  ]

  for (let i = 0; i < 4; i++) {
    const date = new Date(selectedDate)
    date.setDate(date.getDate() + (i - 1)) // -1, 0, 1, 2 days from selected date
    
    const dateString = date.toISOString().split('T')[0] // YYYY-MM-DD format
    
    // Filter TODO items for this pane's date
    const items = todoItems.filter(item => item.target_date === dateString)
    
    panes.push({
      label: labels[i],
      date,
      dateString,
      items
    })
  }

  return panes
}

/**
 * Format date for display
 */
function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

function TodoPageContent() {
  const { t } = useLanguage()
  const queryClient = useQueryClient()
  const toast = useToast()
  const { isMobile, isTablet } = useResponsive()
  
  // State for date selection (defaults to today)
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  
  // State for mobile tab selection (0-3 for panes, 4 for ADHOC)
  const [activeTab, setActiveTab] = useState<number>(1) // Default to "Today"
  
  // State for modals
  const [isTodoModalOpen, setIsTodoModalOpen] = useState(false)
  const [isAdhocModalOpen, setIsAdhocModalOpen] = useState(false)
  const [selectedTodoDate, setSelectedTodoDate] = useState<string>('')
  const [editingTodoItem, setEditingTodoItem] = useState<TodoItem | undefined>(undefined)
  const [editingAdhocNote, setEditingAdhocNote] = useState<AdhocNote | undefined>(undefined)
  
  // State for drag and drop
  const [draggedItem, setDraggedItem] = useState<TodoItem | null>(null)

  // Calculate date range for fetching TODO items (yesterday to day after tomorrow)
  const dateRange = useMemo(() => {
    const startDate = new Date(selectedDate)
    startDate.setDate(startDate.getDate() - 1) // Yesterday
    
    const endDate = new Date(selectedDate)
    endDate.setDate(endDate.getDate() + 2) // Day after tomorrow
    
    return {
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    }
  }, [selectedDate])

  // Fetch TODO items using React Query
  const {
    data: todoItemsData,
    isLoading: todoItemsLoading,
    error: todoItemsError,
    refetch: refetchTodoItems
  } = useQuery({
    queryKey: ['todoItems', dateRange.start_date, dateRange.end_date],
    queryFn: () => fetchTodoItems({
      start_date: dateRange.start_date,
      end_date: dateRange.end_date,
      include_public: true
    }),
    staleTime: 30 * 1000, // 30 seconds
    refetchOnWindowFocus: true
  })

  // Fetch ADHOC notes using React Query
  const {
    data: adhocNotesData,
    isLoading: adhocNotesLoading,
    error: adhocNotesError,
    refetch: refetchAdhocNotes
  } = useQuery({
    queryKey: ['adhocNotes'],
    queryFn: fetchAdhocNotes,
    staleTime: 30 * 1000, // 30 seconds
    refetchOnWindowFocus: true
  })

  // Calculate panes from TODO items
  const panes = useMemo(() => {
    const items = todoItemsData?.items || []
    return calculatePanes(selectedDate, items)
  }, [selectedDate, todoItemsData])

  // Get ADHOC notes
  const adhocNotes = adhocNotesData?.notes || []

  // Loading state
  const isLoading = todoItemsLoading || adhocNotesLoading

  // Error state
  const error = todoItemsError || adhocNotesError

  // Handle date change
  const handleDateChange = (newDate: Date) => {
    setSelectedDate(newDate)
  }

  // Navigate to previous day
  const handlePreviousDay = () => {
    const newDate = new Date(selectedDate)
    newDate.setDate(newDate.getDate() - 1)
    setSelectedDate(newDate)
  }

  // Navigate to next day
  const handleNextDay = () => {
    const newDate = new Date(selectedDate)
    newDate.setDate(newDate.getDate() + 1)
    setSelectedDate(newDate)
  }

  // Reset to today
  const handleToday = () => {
    setSelectedDate(new Date())
  }

  // TODO Item Handlers
  const handleEditTodoItem = (item: TodoItem) => {
    setEditingTodoItem(item)
    setIsTodoModalOpen(true)
  }

  const handleDeleteTodoItem = async (itemId: string) => {
    try {
      await deleteTodoItem(itemId)
      toast.showSuccess('TODO item deleted successfully')
      refetchTodoItems()
    } catch (error: any) {
      console.error('Failed to delete TODO item:', error)
      toast.showError(error?.userMessage || 'Failed to delete TODO item')
    }
  }

  const handleUpdateTodoItem = async (item: TodoItem) => {
    try {
      await updateTodoItem(item.id, {
        title: item.title,
        description: item.description,
        target_date: item.target_date,
        visibility: item.visibility
      })
      toast.showSuccess('TODO item updated successfully')
      refetchTodoItems()
    } catch (error: any) {
      console.error('Failed to update TODO item:', error)
      toast.showError(error?.userMessage || 'Failed to update TODO item')
    }
  }

  // Drag and Drop Handlers
  const handleDragStart = (item: TodoItem) => {
    setDraggedItem(item)
  }

  const handleDragEnd = () => {
    setDraggedItem(null)
  }

  const handleDrop = async (targetDate: string) => {
    if (!draggedItem) return
    
    // Don't do anything if dropped on the same pane
    if (draggedItem.target_date === targetDate) {
      setDraggedItem(null)
      return
    }

    try {
      await moveTodoItem(draggedItem.id, { target_date: targetDate })
      toast.showSuccess('TODO item moved successfully')
      refetchTodoItems()
    } catch (error: any) {
      console.error('Failed to move TODO item:', error)
      toast.showError(error?.userMessage || 'Failed to move TODO item')
    } finally {
      setDraggedItem(null)
    }
  }

  // ADHOC Note Handlers
  const handleEditAdhocNote = (note: AdhocNote) => {
    setEditingAdhocNote(note)
    setIsAdhocModalOpen(true)
  }

  const handleDeleteAdhocNote = async (noteId: string) => {
    try {
      await deleteAdhocNote(noteId)
      toast.showSuccess('Note deleted successfully')
      refetchAdhocNotes()
    } catch (error: any) {
      console.error('Failed to delete note:', error)
      toast.showError(error?.userMessage || 'Failed to delete note')
    }
  }

  // Render loading state with skeleton
  if (isLoading) {
    return <TodoSkeletonLoader type="dashboard" />
  }

  // Render error state
  if (error) {
    const errorMessage = (error as any)?.userMessage || 
                        (error instanceof Error ? error.message : 'An unexpected error occurred')
    
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-color)' }}>
            Failed to Load TODO Items
          </h2>
          <p className="mb-4" style={{ color: 'var(--text-secondary)' }}>
            {errorMessage}
          </p>
          <button
            onClick={() => {
              toast.showInfo('Retrying...')
              refetchTodoItems()
              refetchAdhocNotes()
            }}
            className="px-4 py-2 rounded-lg font-medium"
            style={{
              backgroundColor: 'var(--primary-color)',
              color: 'white'
            }}
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col" role="main" aria-label="TODO Dashboard">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
          <h1 className="text-3xl font-bold" style={{ color: 'var(--text-color)' }} id="page-title">
            📝 {t('todo') || 'TODO Dashboard'}
          </h1>
          
          {/* Date Navigation */}
          <nav className="flex items-center gap-2" aria-label="Date navigation">
            <button
              onClick={handlePreviousDay}
              className="px-3 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
              style={{
                backgroundColor: 'var(--surface-color)',
                color: 'var(--text-color)',
                border: '1px solid var(--border-color)'
              }}
              title="Previous Day"
              aria-label="Go to previous day"
            >
              ←
            </button>
            
            <button
              onClick={handleToday}
              className="px-4 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
              style={{
                backgroundColor: 'var(--primary-color)',
                color: 'white'
              }}
              aria-label="Go to today"
            >
              Today
            </button>
            
            <button
              onClick={handleNextDay}
              className="px-3 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
              style={{
                backgroundColor: 'var(--surface-color)',
                color: 'var(--text-color)',
                border: '1px solid var(--border-color)'
              }}
              title="Next Day"
              aria-label="Go to next day"
            >
              →
            </button>
          </nav>
        </div>
        
        <p style={{ color: 'var(--text-secondary)' }}>
          Organize your work across time-based panes and capture quick notes
        </p>
      </div>

      {/* Mobile Tab Navigation */}
      {isMobile && (
        <nav className="mb-4 overflow-x-auto" role="tablist" aria-label="TODO sections">
          <div className="flex gap-2 min-w-max pb-2">
            {panes.map((pane, index) => (
              <button
                key={pane.label}
                role="tab"
                aria-selected={activeTab === index}
                aria-controls={`pane-${index}`}
                id={`tab-${index}`}
                onClick={() => setActiveTab(index)}
                className="px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-offset-2"
                style={{
                  backgroundColor: activeTab === index ? 'var(--primary-color)' : 'var(--surface-color)',
                  color: activeTab === index ? 'white' : 'var(--text-color)',
                  border: activeTab === index ? 'none' : '1px solid var(--border-color)'
                }}
              >
                {pane.label}
                <span className="ml-2 text-xs opacity-75">({pane.items.length})</span>
              </button>
            ))}
            <button
              role="tab"
              aria-selected={activeTab === 4}
              aria-controls="pane-4"
              id="tab-4"
              onClick={() => setActiveTab(4)}
              className="px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-offset-2"
              style={{
                backgroundColor: activeTab === 4 ? '#F59E0B' : 'var(--surface-color)',
                color: activeTab === 4 ? 'white' : 'var(--text-color)',
                border: activeTab === 4 ? 'none' : '1px solid var(--border-color)'
              }}
            >
              📌 ADHOC
              <span className="ml-2 text-xs opacity-75">({adhocNotes.length})</span>
            </button>
          </div>
        </nav>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Desktop/Tablet: Show all panes */}
        {!isMobile && (
          <>
            {/* Time Panes Container */}
            <div className={`flex-1 flex gap-4 overflow-x-auto ${isTablet ? 'flex-wrap' : ''}`}>
              {panes.map((pane, index) => (
                <div
                  key={pane.label}
                  className={`${isTablet ? 'w-[calc(50%-0.5rem)]' : 'flex-1'} min-w-[280px] flex flex-col rounded-lg p-4`}
                  style={{
                    backgroundColor: 'var(--surface-color)',
                    border: '1px solid var(--border-color)'
                  }}
                  role="region"
                  aria-labelledby={`pane-header-${index}`}
                >
                  {/* Pane Header */}
                  <div className="mb-4">
                    <h2 id={`pane-header-${index}`} className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
                      {pane.label}
                    </h2>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      {formatDate(pane.date)}
                    </p>
                    <div className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }} aria-live="polite">
                      {pane.items.length} {pane.items.length === 1 ? 'item' : 'items'}
                    </div>
                  </div>

                  {/* Pane Content - Placeholder for TODO items */}
                  <div className="flex-1 space-y-2 overflow-y-auto">
                    {pane.items.length === 0 ? (
                      <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }} role="status">
                        <p className="text-sm">No items for this day</p>
                      </div>
                    ) : (
                      <div 
                        className="space-y-2"
                        onDragOver={(e) => {
                          e.preventDefault()
                          e.dataTransfer.dropEffect = 'move'
                        }}
                        onDrop={(e) => {
                          e.preventDefault()
                          handleDrop(pane.dateString)
                        }}
                      >
                        {pane.items.map((item) => (
                          <TodoItemCard
                            key={item.id}
                            item={item}
                            onDragStart={handleDragStart}
                            onDragEnd={handleDragEnd}
                            onUpdate={handleUpdateTodoItem}
                            onDelete={handleDeleteTodoItem}
                            onEdit={handleEditTodoItem}
                            draggable={true}
                          />
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Add Button */}
                  <button
                    onClick={() => {
                      setSelectedTodoDate(pane.dateString)
                      setIsTodoModalOpen(true)
                    }}
                    className="mt-4 w-full py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
                    style={{
                      backgroundColor: 'var(--background-color)',
                      color: 'var(--text-color)',
                      border: '1px dashed var(--border-color)'
                    }}
                    aria-label={`Add item to ${pane.label}`}
                  >
                    + Add Item
                  </button>
                </div>
              ))}
            </div>

            {/* ADHOC Notes Pane */}
            <div
              className={`${isTablet ? 'w-full mt-4' : 'w-80'} flex flex-col rounded-lg p-4`}
              style={{
                backgroundColor: 'var(--surface-color)',
                border: '1px solid var(--border-color)'
              }}
              role="region"
              aria-labelledby="adhoc-header"
            >
              {/* ADHOC Header */}
              <div className="mb-4">
                <h2 id="adhoc-header" className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
                  📌 ADHOC Notes
                </h2>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  Quick notes and reminders
                </p>
                <div className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }} aria-live="polite">
                  {adhocNotes.length} {adhocNotes.length === 1 ? 'note' : 'notes'}
                </div>
              </div>

              {/* ADHOC Content - Placeholder for notes */}
              <div className="flex-1 space-y-3 overflow-y-auto">
                {adhocNotes.length === 0 ? (
                  <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }} role="status">
                    <p className="text-sm">No notes yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {adhocNotes.map((note) => (
                      <AdhocNoteCard
                        key={note.id}
                        note={note}
                        onEdit={handleEditAdhocNote}
                        onDelete={handleDeleteAdhocNote}
                        onReorder={async (noteId, newPosition) => {
                          try {
                            await reorderAdhocNote(noteId, { position: newPosition })
                            refetchAdhocNotes()
                          } catch (error: any) {
                            console.error('Failed to reorder note:', error)
                            toast.showError(error?.userMessage || 'Failed to reorder note')
                          }
                        }}
                      />
                    ))}
                  </div>
                )}
              </div>

              {/* Add Note Button */}
              <button
                onClick={() => setIsAdhocModalOpen(true)}
                className="mt-4 w-full py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
                style={{
                  backgroundColor: '#FFEB3B',
                  color: '#000',
                  border: '1px solid rgba(0,0,0,0.1)'
                }}
                aria-label="Add new ADHOC note"
              >
                + Add Note
              </button>
            </div>
          </>
        )}

        {/* Mobile: Show active tab only */}
        {isMobile && (
          <div className="flex-1 overflow-hidden">
            {activeTab < 4 ? (
              // Time Pane
              <div
                className="h-full flex flex-col rounded-lg p-4"
                style={{
                  backgroundColor: 'var(--surface-color)',
                  border: '1px solid var(--border-color)'
                }}
                role="tabpanel"
                id={`pane-${activeTab}`}
                aria-labelledby={`tab-${activeTab}`}
              >
                {/* Pane Header */}
                <div className="mb-4">
                  <h2 className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
                    {panes[activeTab].label}
                  </h2>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    {formatDate(panes[activeTab].date)}
                  </p>
                  <div className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }} aria-live="polite">
                    {panes[activeTab].items.length} {panes[activeTab].items.length === 1 ? 'item' : 'items'}
                  </div>
                </div>

                {/* Pane Content */}
                <div className="flex-1 space-y-2 overflow-y-auto">
                  {panes[activeTab].items.length === 0 ? (
                    <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }} role="status">
                      <p className="text-sm">No items for this day</p>
                    </div>
                  ) : (
                    <div 
                      className="space-y-2"
                      onDragOver={(e) => {
                        e.preventDefault()
                        e.dataTransfer.dropEffect = 'move'
                      }}
                      onDrop={(e) => {
                        e.preventDefault()
                        handleDrop(panes[activeTab].dateString)
                      }}
                    >
                      {panes[activeTab].items.map((item) => (
                        <TodoItemCard
                          key={item.id}
                          item={item}
                          onDragStart={handleDragStart}
                          onDragEnd={handleDragEnd}
                          onUpdate={handleUpdateTodoItem}
                          onDelete={handleDeleteTodoItem}
                          onEdit={handleEditTodoItem}
                          draggable={true}
                        />
                      ))}
                    </div>
                  )}
                </div>

                {/* Add Button */}
                <button
                  onClick={() => {
                    setSelectedTodoDate(panes[activeTab].dateString)
                    setIsTodoModalOpen(true)
                  }}
                  className="mt-4 w-full py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
                  style={{
                    backgroundColor: 'var(--background-color)',
                    color: 'var(--text-color)',
                    border: '1px dashed var(--border-color)'
                  }}
                  aria-label={`Add item to ${panes[activeTab].label}`}
                >
                  + Add Item
                </button>
              </div>
            ) : (
              // ADHOC Notes Pane
              <div
                className="h-full flex flex-col rounded-lg p-4"
                style={{
                  backgroundColor: 'var(--surface-color)',
                  border: '1px solid var(--border-color)'
                }}
                role="tabpanel"
                id="pane-4"
                aria-labelledby="tab-4"
              >
                {/* ADHOC Header */}
                <div className="mb-4">
                  <h2 className="text-lg font-semibold" style={{ color: 'var(--text-color)' }}>
                    📌 ADHOC Notes
                  </h2>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    Quick notes and reminders
                  </p>
                  <div className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }} aria-live="polite">
                    {adhocNotes.length} {adhocNotes.length === 1 ? 'note' : 'notes'}
                  </div>
                </div>

                {/* ADHOC Content */}
                <div className="flex-1 space-y-3 overflow-y-auto">
                  {adhocNotes.length === 0 ? (
                    <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }} role="status">
                      <p className="text-sm">No notes yet</p>
                    </div>
                  ) : (
                    <ul className="space-y-3" role="list" aria-label="ADHOC notes">
                      {adhocNotes.map((note) => (
                        <li
                          key={note.id}
                          className="p-3 rounded-lg shadow-sm"
                          style={{
                            backgroundColor: note.color,
                            border: '1px solid rgba(0,0,0,0.1)'
                          }}
                        >
                          <h3 className="font-medium mb-1" style={{ color: '#000' }}>
                            {note.title}
                          </h3>
                          {note.content && (
                            <p className="text-sm" style={{ color: '#333' }}>
                              {note.content}
                            </p>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Add Note Button */}
                <button
                  onClick={() => setIsAdhocModalOpen(true)}
                  className="mt-4 w-full py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
                  style={{
                    backgroundColor: '#FFEB3B',
                    color: '#000',
                    border: '1px solid rgba(0,0,0,0.1)'
                  }}
                  aria-label="Add new ADHOC note"
                >
                  + Add Note
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* TODO Item Form Modal */}
      <TodoItemFormModal
        isOpen={isTodoModalOpen}
        onClose={() => {
          setIsTodoModalOpen(false)
          setSelectedTodoDate('')
          setEditingTodoItem(undefined)
        }}
        onSuccess={() => {
          refetchTodoItems()
          setIsTodoModalOpen(false)
          setSelectedTodoDate('')
          setEditingTodoItem(undefined)
        }}
        item={editingTodoItem}
        initialDate={selectedTodoDate}
      />
      
      {/* ADHOC Note Form Modal */}
      <AdhocNoteFormModal
        isOpen={isAdhocModalOpen}
        onClose={() => {
          setIsAdhocModalOpen(false)
          setEditingAdhocNote(undefined)
        }}
        onSuccess={() => {
          refetchAdhocNotes()
          setIsAdhocModalOpen(false)
          setEditingAdhocNote(undefined)
        }}
        note={editingAdhocNote}
      />
    </div>
  )
}

/**
 * Wrap TodoPage with ErrorBoundary for error handling
 * Requirements: 8.8
 */
export default function TodoPage() {
  return (
    <ErrorBoundary
      fallback={
        <div className="flex items-center justify-center h-full">
          <div className="text-center max-w-md">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-color)' }}>
              TODO Feature Error
            </h2>
            <p className="mb-4" style={{ color: 'var(--text-secondary)' }}>
              Something went wrong with the TODO feature. Please refresh the page to try again.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 rounded-lg font-medium"
              style={{
                backgroundColor: 'var(--primary-color)',
                color: 'white'
              }}
            >
              Refresh Page
            </button>
          </div>
        </div>
      }
      onError={(error, errorInfo) => {
        console.error('TODO Feature Error:', error, errorInfo)
      }}
    >
      <TodoPageContent />
    </ErrorBoundary>
  )
}
