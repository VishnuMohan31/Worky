/**
 * EntityCard Component
 * Individual card for displaying entity in list view
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { EntityType } from '../../stores/hierarchyStore'
import AssignmentButton from '../assignments/AssignmentButton'
import api from '../../services/api'

interface Assignment {
  id: string
  user_id: string
  user_name?: string
  user_email?: string
  assignment_type: string
  is_active: boolean
}

interface EntityCardProps {
  entity: any
  type: EntityType
  onClick: () => void
  onAssignmentChange?: () => void
}

export default function EntityCard({ entity, type, onClick, onAssignmentChange }: EntityCardProps) {
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const loadTimeoutRef = useRef<number | null>(null)

  const loadAssignments = useCallback(async () => {
    // Clear any existing timeout
    if (loadTimeoutRef.current !== null) {
      window.clearTimeout(loadTimeoutRef.current)
    }

    // Debounce the API call
    loadTimeoutRef.current = window.setTimeout(async () => {
      try {
        console.log(`Loading assignments for ${type}:${entity.id}`)
        const response = await api.getAssignments({
          entity_type: type,
          entity_id: entity.id
        })
        console.log(`Loaded ${response.length} assignments:`, response)
        
        // Filter to only active assignments to prevent duplicates
        const activeAssignments = response.filter((a: Assignment) => a.is_active === true)
        setAssignments(activeAssignments)
      } catch (error) {
        console.error('Failed to load assignments:', error)
        setAssignments([]) // Clear assignments on error
      }
    }, 100) // 100ms debounce
  }, [type, entity.id])

  useEffect(() => {
    if (type === 'task' || type === 'subtask') {
      loadAssignments()
    }

    // Cleanup timeout on unmount
    return () => {
      if (loadTimeoutRef.current !== null) {
        window.clearTimeout(loadTimeoutRef.current)
      }
    }
  }, [loadAssignments, type])

  const handleAssignmentChange = () => {
    console.log('Assignment changed, reloading assignments')
    // Clear current assignments immediately to prevent showing stale data
    setAssignments([])
    loadAssignments()
    onAssignmentChange?.()
  }

  // Find the current assignment for this entity (tasks/subtasks use 'assignee' type)
  const currentAssignment = assignments.find((a: Assignment) => a.is_active && a.assignment_type === 'assignee')
  
  // Get assigned person name
  const assignedPersonName = currentAssignment?.user_name || entity.assigned_to_name || null
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'Planning': 'bg-gray-50 text-gray-700 border border-gray-200',
      'To Do': 'bg-slate-50 text-slate-700 border border-slate-200',
      'In Progress': 'bg-blue-50 text-blue-700 border border-blue-200',
      'Completed': 'bg-green-50 text-green-700 border border-green-200',
      'Done': 'bg-emerald-50 text-emerald-700 border border-emerald-200',
      'On Hold': 'bg-yellow-50 text-yellow-700 border border-yellow-200',
      'Blocked': 'bg-red-50 text-red-700 border border-red-200'
    }
    return colors[status] || 'bg-gray-50 text-gray-700 border border-gray-200'
  }
  
  const getPriorityIcon = (priority: string) => {
    if (priority === 'High') {
      return (
        <div className="flex items-center justify-center w-6 h-6 bg-red-100 rounded-full">
          <svg className="w-3.5 h-3.5 text-red-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
          </svg>
        </div>
      )
    }
    if (priority === 'Medium') {
      return (
        <div className="flex items-center justify-center w-6 h-6 bg-yellow-100 rounded-full">
          <svg className="w-3.5 h-3.5 text-yellow-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M9 12l2 2 4-4" />
          </svg>
        </div>
      )
    }
    if (priority === 'Low') {
      return (
        <div className="flex items-center justify-center w-6 h-6 bg-green-100 rounded-full">
          <svg className="w-3.5 h-3.5 text-green-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" transform="rotate(180 12 12)" />
          </svg>
        </div>
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
      className="group bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all duration-200 cursor-pointer overflow-hidden"
    >
      {/* Main Content */}
      <div className="p-5">
        {/* Header with Title and Actions */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 truncate mb-1">
              {entity.name || entity.title}
            </h3>
            {entity.short_description && (
              <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                {entity.short_description}
              </p>
            )}
          </div>
          
          {/* Action Area */}
          <div className="flex items-center gap-2 ml-3 flex-shrink-0">
            {entity.priority && (
              <div className="flex-shrink-0" title={`${entity.priority} Priority`}>
                {getPriorityIcon(entity.priority)}
              </div>
            )}
            
            {/* Assignment Button for Tasks and Subtasks */}
            {(type === 'task' || type === 'subtask') && (
              <AssignmentButton
                entityType={type}
                entityId={entity.id}
                currentAssignment={currentAssignment}
                allAssignments={assignments}
                onAssignmentChange={handleAssignmentChange}
                size="md"
              />
            )}
          </div>
        </div>

        {/* Status and Metadata Row */}
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          {/* Status Badge */}
          {entity.status && (
            <span className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(entity.status)}`}>
              {entity.status}
            </span>
          )}
          
          {/* Phase Badge */}
          {(type === 'task' || type === 'subtask') && entity.phase_name && (
            <span className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full bg-purple-50 text-purple-700 border border-purple-200">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-500 mr-2"></span>
              {entity.phase_name}
            </span>
          )}
          
          {/* Story Points */}
          {entity.story_points !== undefined && (
            <span className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
              {entity.story_points} pts
            </span>
          )}
        </div>

        {/* Assignment and Details Row */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-gray-600">
            {/* Assigned Person - More Prominent */}
            {assignedPersonName ? (
              <div className="flex items-center gap-2 bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                  <svg className="w-3.5 h-3.5 text-blue-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <span className="font-medium text-blue-900" title="Assigned Person">
                  {assignedPersonName}
                </span>
              </div>
            ) : (type === 'task' || type === 'subtask') ? (
              <div className="flex items-center gap-2 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
                <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center">
                  <svg className="w-3.5 h-3.5 text-gray-400" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <span className="text-gray-500" title="No person assigned">
                  Unassigned
                </span>
              </div>
            ) : null}
            
            {/* Due Date */}
            {entity.due_date && (
              <div className="flex items-center gap-1.5">
                <svg className="w-4 h-4 text-gray-400" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>{formatDate(entity.due_date)}</span>
              </div>
            )}
            
            {/* Estimated Hours */}
            {entity.estimated_hours !== undefined && (
              <div className="flex items-center gap-1.5">
                <svg className="w-4 h-4 text-gray-400" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{entity.estimated_hours}h</span>
              </div>
            )}
          </div>
          
          {/* Progress Indicator */}
          {entity.progress !== undefined && (
            <div className="flex items-center gap-2">
              <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-300"
                  style={{ width: `${entity.progress}%` }}
                />
              </div>
              <span className="text-sm font-medium text-gray-700 min-w-[3rem] text-right">
                {entity.progress}%
              </span>
            </div>
          )}
        </div>
      </div>
      
      {/* Hover Action Bar */}
      <div className="px-5 py-3 bg-gray-50 border-t border-gray-100 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">
            Click to view details
          </span>
          <svg className="w-4 h-4 text-blue-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  )
}
