/**
 * Skeleton Loader for TODO Components
 * Provides loading placeholders for better UX
 * Requirements: 8.8
 */

import './todo.css'

interface TodoSkeletonLoaderProps {
  type?: 'pane' | 'item' | 'note' | 'dashboard'
  count?: number
}

/**
 * Skeleton for a single TODO item card
 */
export function TodoItemSkeleton() {
  return (
    <div className="todo-item-skeleton">
      <div className="skeleton skeleton-text" style={{ width: '70%', marginBottom: '8px' }} />
      <div className="skeleton skeleton-text" style={{ width: '90%', height: '12px', marginBottom: '12px' }} />
      <div style={{ display: 'flex', gap: '8px' }}>
        <div className="skeleton" style={{ width: '60px', height: '24px', borderRadius: '4px' }} />
        <div className="skeleton" style={{ width: '50px', height: '24px', borderRadius: '4px' }} />
      </div>
    </div>
  )
}

/**
 * Skeleton for a time pane
 */
export function TimePaneSkeleton() {
  return (
    <div className="time-pane-skeleton">
      <div className="pane-header-skeleton">
        <div className="skeleton skeleton-text" style={{ width: '120px', height: '20px', marginBottom: '4px' }} />
        <div className="skeleton skeleton-text" style={{ width: '100px', height: '14px', marginBottom: '8px' }} />
        <div className="skeleton skeleton-text" style={{ width: '60px', height: '12px' }} />
      </div>
      <div className="pane-content-skeleton">
        <TodoItemSkeleton />
        <TodoItemSkeleton />
        <TodoItemSkeleton />
      </div>
      <div className="skeleton" style={{ width: '100%', height: '40px', borderRadius: '8px', marginTop: '16px' }} />
    </div>
  )
}

/**
 * Skeleton for an ADHOC note
 */
export function AdhocNoteSkeleton() {
  return (
    <div className="adhoc-note-skeleton">
      <div className="skeleton skeleton-text" style={{ width: '80%', marginBottom: '8px' }} />
      <div className="skeleton skeleton-text" style={{ width: '100%', height: '12px', marginBottom: '4px' }} />
      <div className="skeleton skeleton-text" style={{ width: '90%', height: '12px' }} />
    </div>
  )
}

/**
 * Skeleton for ADHOC notes pane
 */
export function AdhocPaneSkeleton() {
  return (
    <div className="adhoc-pane-skeleton">
      <div className="pane-header-skeleton">
        <div className="skeleton skeleton-text" style={{ width: '140px', height: '20px', marginBottom: '4px' }} />
        <div className="skeleton skeleton-text" style={{ width: '120px', height: '14px', marginBottom: '8px' }} />
        <div className="skeleton skeleton-text" style={{ width: '50px', height: '12px' }} />
      </div>
      <div className="pane-content-skeleton">
        <AdhocNoteSkeleton />
        <AdhocNoteSkeleton />
        <AdhocNoteSkeleton />
      </div>
      <div className="skeleton" style={{ width: '100%', height: '40px', borderRadius: '8px', marginTop: '16px' }} />
    </div>
  )
}

/**
 * Skeleton for entire TODO dashboard
 */
export function TodoDashboardSkeleton() {
  return (
    <div className="h-full flex flex-col">
      {/* Header Skeleton */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="skeleton skeleton-text" style={{ width: '250px', height: '32px' }} />
          <div style={{ display: 'flex', gap: '8px' }}>
            <div className="skeleton" style={{ width: '48px', height: '40px', borderRadius: '8px' }} />
            <div className="skeleton" style={{ width: '80px', height: '40px', borderRadius: '8px' }} />
            <div className="skeleton" style={{ width: '48px', height: '40px', borderRadius: '8px' }} />
          </div>
        </div>
        <div className="skeleton skeleton-text" style={{ width: '400px', height: '16px' }} />
      </div>

      {/* Main Content Skeleton */}
      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Time Panes */}
        <div className="flex-1 flex gap-4 overflow-x-auto">
          <TimePaneSkeleton />
          <TimePaneSkeleton />
          <TimePaneSkeleton />
          <TimePaneSkeleton />
        </div>

        {/* ADHOC Pane */}
        <div className="w-80">
          <AdhocPaneSkeleton />
        </div>
      </div>
    </div>
  )
}

/**
 * Main skeleton loader component with type selection
 */
export default function TodoSkeletonLoader({ type = 'dashboard', count = 3 }: TodoSkeletonLoaderProps) {
  if (type === 'dashboard') {
    return <TodoDashboardSkeleton />
  }
  
  if (type === 'pane') {
    return <TimePaneSkeleton />
  }
  
  if (type === 'item') {
    return (
      <>
        {Array.from({ length: count }).map((_, index) => (
          <TodoItemSkeleton key={index} />
        ))}
      </>
    )
  }
  
  if (type === 'note') {
    return (
      <>
        {Array.from({ length: count }).map((_, index) => (
          <AdhocNoteSkeleton key={index} />
        ))}
      </>
    )
  }
  
  return null
}
