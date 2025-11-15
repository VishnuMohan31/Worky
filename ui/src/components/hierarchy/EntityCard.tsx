/**
 * EntityCard Component
 * Individual card for displaying entity in list view
 */
import { EntityType } from '../../stores/hierarchyStore'

interface EntityCardProps {
  entity: any
  type: EntityType
  onClick: () => void
}

export default function EntityCard({ entity, type, onClick }: EntityCardProps) {
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'Planning': 'bg-gray-100 text-gray-800 border-gray-300',
      'To Do': 'bg-gray-100 text-gray-800 border-gray-300',
      'In Progress': 'bg-blue-100 text-blue-800 border-blue-300',
      'Completed': 'bg-green-100 text-green-800 border-green-300',
      'Done': 'bg-green-100 text-green-800 border-green-300',
      'On Hold': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Blocked': 'bg-red-100 text-red-800 border-red-300'
    }
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300'
  }
  
  const getPriorityIcon = (priority: string) => {
    if (priority === 'High') {
      return (
        <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
        </svg>
      )
    }
    if (priority === 'Low') {
      return (
        <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
        </svg>
      )
    }
    return null
  }
  
  const formatDate = (date: string | undefined) => {
    if (!date) return null
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
  }
  
  return (
    <div
      onClick={onClick}
      className="entity-card"
    >
      {/* Header */}
      <div className="entity-card-header">
        <h4 className="entity-card-title">
          {entity.name || entity.title}
        </h4>
        {entity.priority && (
          <div className="ml-2 flex-shrink-0">
            {getPriorityIcon(entity.priority)}
          </div>
        )}
      </div>
      
      {/* Short Description */}
      {entity.short_description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {entity.short_description}
        </p>
      )}
      
      {/* Metadata */}
      <div className="entity-card-meta">
        {/* Status Badge */}
        {entity.status && (
          <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(entity.status)}`}>
            {entity.status}
          </span>
        )}
        
        {/* Phase Badge (for Tasks and Subtasks) */}
        {(type === 'task' || type === 'subtask') && entity.phase_name && (
          <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-purple-100 text-purple-800 border border-purple-300">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-600 mr-1.5"></span>
            {entity.phase_name}
          </span>
        )}
        
        {/* Story Points */}
        {entity.story_points !== undefined && (
          <span className="px-2 py-1 text-xs font-medium rounded bg-indigo-100 text-indigo-800 border border-indigo-300">
            {entity.story_points} pts
          </span>
        )}
      </div>
      
      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-3">
          {/* Assigned To */}
          {entity.assigned_to && (
            <div className="flex items-center gap-1">
              <svg className="w-3.5 h-3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span>{entity.assigned_to_name || 'Assigned'}</span>
            </div>
          )}
          
          {/* Due Date */}
          {entity.due_date && (
            <div className="flex items-center gap-1">
              <svg className="w-3.5 h-3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{formatDate(entity.due_date)}</span>
            </div>
          )}
          
          {/* Estimated Hours */}
          {entity.estimated_hours !== undefined && (
            <div className="flex items-center gap-1">
              <svg className="w-3.5 h-3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{entity.estimated_hours}h</span>
            </div>
          )}
        </div>
        
        {/* Progress Indicator */}
        {entity.progress !== undefined && (
          <div className="flex items-center gap-1">
            <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 rounded-full transition-all"
                style={{ width: `${entity.progress}%` }}
              />
            </div>
            <span className="text-xs font-medium">{entity.progress}%</span>
          </div>
        )}
      </div>
      
      {/* Hover Arrow */}
      <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-end opacity-0 group-hover:opacity-100 transition-opacity">
        <span className="text-xs text-blue-600 font-medium flex items-center gap-1">
          View Details
          <svg className="w-3 h-3" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M9 5l7 7-7 7" />
          </svg>
        </span>
      </div>
    </div>
  )
}
