/**
 * Task Link Info Panel Component
 * Displays read-only task/subtask information for linked TODO items
 * Requirements: 3.3, 3.6
 */

import type { LinkedTaskInfo, TodoEntityType } from '../../types/todo'

interface TaskLinkInfoPanelProps {
  linkedEntity: LinkedTaskInfo
  entityType: TodoEntityType
}

export default function TaskLinkInfoPanel({
  linkedEntity,
  entityType
}: TaskLinkInfoPanelProps) {
  /**
   * Get status color based on status value
   */
  const getStatusColor = (status: string): string => {
    const statusColors: Record<string, string> = {
      'Planning': 'bg-gray-100 text-gray-800 border-gray-300',
      'To Do': 'bg-gray-100 text-gray-800 border-gray-300',
      'In Progress': 'bg-blue-100 text-blue-800 border-blue-300',
      'Completed': 'bg-green-100 text-green-800 border-green-300',
      'Done': 'bg-green-100 text-green-800 border-green-300',
      'On Hold': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Blocked': 'bg-red-100 text-red-800 border-red-300',
      'Cancelled': 'bg-gray-100 text-gray-800 border-gray-300'
    }
    return statusColors[status] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  /**
   * Format date for display
   */
  const formatDate = (dateString?: string): string | null => {
    if (!dateString) return null
    
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    } catch {
      return null
    }
  }

  /**
   * Get link to view full entity in hierarchy
   */
  const getEntityLink = (): string => {
    // This would link to the hierarchy view with the entity selected
    // The actual implementation depends on your routing structure
    if (entityType === 'task') {
      return `/hierarchy?task=${linkedEntity.id}`
    } else {
      return `/hierarchy?subtask=${linkedEntity.id}`
    }
  }

  return (
    <div className="task-link-info-panel" role="region" aria-label="Linked task information">
      {/* Read-Only Indicator */}
      <div className="task-link-header">
        <div className="flex items-center gap-2">
          <svg
            className="w-4 h-4 text-gray-500"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-label="Read-only"
          >
            <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <span className="task-link-label">
            {entityType === 'task' ? 'Linked Task' : 'Linked Subtask'} (Read-Only)
          </span>
        </div>
      </div>

      {/* Entity Information */}
      <div className="task-link-content">
        {/* Entity ID and Title */}
        <div className="task-link-row">
          <div className="task-link-field">
            <span className="task-link-field-label">ID:</span>
            <span className="task-link-field-value task-link-id">{linkedEntity.id}</span>
          </div>
        </div>

        <div className="task-link-row">
          <div className="task-link-field task-link-field-full">
            <span className="task-link-field-label">Title:</span>
            <span className="task-link-field-value">{linkedEntity.title}</span>
          </div>
        </div>

        {/* Status */}
        <div className="task-link-row">
          <div className="task-link-field">
            <span className="task-link-field-label">Status:</span>
            <span className={`task-link-status-badge ${getStatusColor(linkedEntity.status)}`}>
              {linkedEntity.status}
            </span>
          </div>
        </div>

        {/* Due Date */}
        {linkedEntity.due_date && (
          <div className="task-link-row">
            <div className="task-link-field">
              <span className="task-link-field-label">Due Date:</span>
              <div className="flex items-center gap-1 task-link-field-value">
                <svg
                  className="w-3.5 h-3.5 text-gray-500"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>{formatDate(linkedEntity.due_date)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Assigned To */}
        {linkedEntity.assigned_to && (
          <div className="task-link-row">
            <div className="task-link-field">
              <span className="task-link-field-label">Assigned To:</span>
              <div className="flex items-center gap-1 task-link-field-value">
                <svg
                  className="w-3.5 h-3.5 text-gray-500"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>{linkedEntity.assigned_to}</span>
              </div>
            </div>
          </div>
        )}

        {/* Parent ID */}
        {linkedEntity.parent_id && (
          <div className="task-link-row">
            <div className="task-link-field">
              <span className="task-link-field-label">
                {entityType === 'task' ? 'User Story:' : 'Task:'}
              </span>
              <span className="task-link-field-value task-link-id">{linkedEntity.parent_id}</span>
            </div>
          </div>
        )}
      </div>

      {/* View Full Details Link */}
      <div className="task-link-footer">
        <a
          href={getEntityLink()}
          className="task-link-view-button"
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`View full ${entityType} details in hierarchy`}
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
            <path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          <span>View in Hierarchy</span>
        </a>
      </div>
    </div>
  )
}
