/**
 * Skeleton Loader Component
 * 
 * Provides loading placeholders for hierarchy components
 * to improve perceived performance.
 */
import React from 'react'

interface SkeletonLoaderProps {
  type?: 'card' | 'list' | 'details' | 'statistics'
  count?: number
}

export default function SkeletonLoader({ type = 'card', count = 3 }: SkeletonLoaderProps) {
  if (type === 'card') {
    return (
      <div className="entity-list">
        {Array.from({ length: count }).map((_, index) => (
          <div key={index} className="skeleton skeleton-card" />
        ))}
      </div>
    )
  }

  if (type === 'list') {
    return (
      <div className="entity-list">
        {Array.from({ length: count }).map((_, index) => (
          <div key={index} style={{ marginBottom: 'var(--spacing-sm)' }}>
            <div className="skeleton skeleton-text" style={{ width: '70%' }} />
            <div className="skeleton skeleton-text" style={{ width: '50%' }} />
          </div>
        ))}
      </div>
    )
  }

  if (type === 'details') {
    return (
      <div className="entity-details">
        <div className="skeleton skeleton-title" />
        <div style={{ marginBottom: 'var(--spacing-md)' }}>
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text" style={{ width: '80%' }} />
        </div>
        <div className="skeleton skeleton-card" />
      </div>
    )
  }

  if (type === 'statistics') {
    return (
      <div className="entity-statistics">
        <div className="skeleton skeleton-title" style={{ width: '40%', marginBottom: 'var(--spacing-md)' }} />
        <div className="stat-summary">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="skeleton" style={{ height: '48px' }} />
          ))}
        </div>
        <div className="skeleton" style={{ height: '120px', marginTop: 'var(--spacing-md)' }} />
      </div>
    )
  }

  return null
}

/**
 * Skeleton for breadcrumb
 */
export function BreadcrumbSkeleton() {
  return (
    <div className="breadcrumb">
      <div className="skeleton skeleton-text" style={{ width: '80px', height: '14px' }} />
      <span className="breadcrumb-separator">/</span>
      <div className="skeleton skeleton-text" style={{ width: '100px', height: '14px' }} />
      <span className="breadcrumb-separator">/</span>
      <div className="skeleton skeleton-text" style={{ width: '120px', height: '14px' }} />
    </div>
  )
}

/**
 * Skeleton for entity card
 */
export function EntityCardSkeleton() {
  return (
    <div className="entity-card">
      <div className="skeleton skeleton-text" style={{ width: '70%', marginBottom: 'var(--spacing-xs)' }} />
      <div className="skeleton skeleton-text" style={{ width: '50%', height: '12px' }} />
    </div>
  )
}

/**
 * Skeleton for pane header
 */
export function PaneHeaderSkeleton() {
  return (
    <div className="pane-header">
      <div className="skeleton skeleton-text" style={{ width: '150px', height: '20px' }} />
      <div className="skeleton" style={{ width: '80px', height: '32px', borderRadius: 'var(--radius-sm)' }} />
    </div>
  )
}
