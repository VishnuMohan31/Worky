/**
 * EntityDetails Component
 * Displays detailed information about an entity
 */
import { useState } from 'react'
import { EntityType, getEntityDisplayName } from '../../stores/hierarchyStore'
import EntityStatistics from './EntityStatistics'
import AuditHistory from './AuditHistory'
import EntityNotes from './EntityNotes'
import Modal from '../common/Modal'
import EntityForm from '../forms/EntityForm'
import api from '../../services/api'

interface EntityDetailsProps {
  entity: any
  type: EntityType
  compact?: boolean
}

export default function EntityDetails({ entity, type, compact = false }: EntityDetailsProps) {
  const [showAuditHistory, setShowAuditHistory] = useState(false)
  const [showNotes, setShowNotes] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)
  
  if (!entity) return null
  
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'Planning': 'bg-gray-100 text-gray-800',
      'To Do': 'bg-gray-100 text-gray-800',
      'In Progress': 'bg-blue-100 text-blue-800',
      'Completed': 'bg-green-100 text-green-800',
      'Done': 'bg-green-100 text-green-800',
      'On Hold': 'bg-yellow-100 text-yellow-800',
      'Blocked': 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }
  
  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'High': 'bg-red-100 text-red-800',
      'Medium': 'bg-yellow-100 text-yellow-800',
      'Low': 'bg-green-100 text-green-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }
  
  const formatDate = (date: string | undefined) => {
    if (!date) return 'Not set'
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  // Format date for HTML date input (YYYY-MM-DD)
  const formatDateForInput = (date: string | Date | undefined): string => {
    if (!date) return ''
    try {
      // If it's already in YYYY-MM-DD format, return as is
      if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) {
        return date
      }
      
      // Handle date-only strings (YYYY-MM-DD) that might have timezone issues
      if (typeof date === 'string' && date.includes('T')) {
        // ISO string with time - extract date part
        const datePart = date.split('T')[0]
        if (/^\d{4}-\d{2}-\d{2}$/.test(datePart)) {
          return datePart
        }
      }
      
      const dateObj = typeof date === 'string' ? new Date(date) : date
      if (isNaN(dateObj.getTime())) return ''
      
      // Use UTC methods to avoid timezone issues
      const year = dateObj.getFullYear()
      const month = String(dateObj.getMonth() + 1).padStart(2, '0')
      const day = String(dateObj.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    } catch (error) {
      console.error('Error formatting date:', error, date)
      return ''
    }
  }
  
  if (compact) {
    return (
      <div className="space-y-2">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{entity.name || entity.title}</h3>
            {entity.short_description && (
              <p className="text-sm text-gray-600 mt-1">{entity.short_description}</p>
            )}
          </div>
          {entity.status && (
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(entity.status)}`}>
              {entity.status}
            </span>
          )}
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            {getEntityDisplayName(type)}
          </span>
          {entity.status && (
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(entity.status)}`}>
              {entity.status}
            </span>
          )}
          {entity.priority && (
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(entity.priority)}`}>
              {entity.priority}
            </span>
          )}
        </div>
        <h1 className="text-3xl font-bold text-gray-900">{entity.name || entity.title}</h1>
      </div>
      
      {/* Short Description */}
      {entity.short_description && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
          <p className="text-gray-700">{entity.short_description}</p>
        </div>
      )}
      
      {/* Metadata Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {entity.start_date && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Start Date</dt>
            <dd className="mt-1 text-sm text-gray-900">{formatDate(entity.start_date)}</dd>
          </div>
        )}
        
        {entity.end_date && (
          <div>
            <dt className="text-sm font-medium text-gray-500">End Date</dt>
            <dd className="mt-1 text-sm text-gray-900">{formatDate(entity.end_date)}</dd>
          </div>
        )}
        
        {entity.due_date && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Due Date</dt>
            <dd className="mt-1 text-sm text-gray-900">{formatDate(entity.due_date)}</dd>
          </div>
        )}
        
        {entity.assigned_to && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Assigned To</dt>
            <dd className="mt-1 text-sm text-gray-900">{entity.assigned_to_name || entity.assigned_to}</dd>
          </div>
        )}
        
        {entity.estimated_hours !== undefined && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Estimated Hours</dt>
            <dd className="mt-1 text-sm text-gray-900">{entity.estimated_hours || 0}h</dd>
          </div>
        )}
        
        {entity.actual_hours !== undefined && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Actual Hours</dt>
            <dd className="mt-1 text-sm text-gray-900">{entity.actual_hours || 0}h</dd>
          </div>
        )}
        
        {entity.story_points !== undefined && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Story Points</dt>
            <dd className="mt-1 text-sm text-gray-900">{entity.story_points || 0}</dd>
          </div>
        )}
        
        {entity.repository_url && (
          <div className="col-span-2">
            <dt className="text-sm font-medium text-gray-500">Repository</dt>
            <dd className="mt-1 text-sm">
              <a
                href={entity.repository_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 hover:underline"
              >
                {entity.repository_url}
              </a>
            </dd>
          </div>
        )}
      </div>
      
      {/* Phase Badge (for Tasks and Subtasks) */}
      {(type === 'task' || type === 'subtask') && entity.phase_id && (
        <div>
          <dt className="text-sm font-medium text-gray-500 mb-2">Phase</dt>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
            <span className="w-2 h-2 rounded-full bg-purple-600 mr-2"></span>
            {entity.phase_name || 'Development'}
          </span>
        </div>
      )}
      
      {/* Long Description */}
      {entity.long_description && (
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Description</h3>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{entity.long_description}</p>
          </div>
        </div>
      )}
      
      {/* Acceptance Criteria (for User Stories) */}
      {type === 'userstory' && entity.acceptance_criteria && (
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Acceptance Criteria</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-700 whitespace-pre-wrap">{entity.acceptance_criteria}</p>
          </div>
        </div>
      )}
      
      {/* Timestamps */}
      <div className="pt-4 border-t">
        <dl className="grid grid-cols-2 gap-4 text-xs text-gray-500">
          {entity.created_at && (
            <div>
              <dt className="font-medium">Created</dt>
              <dd className="mt-1">{formatDate(entity.created_at)}</dd>
            </div>
          )}
          {entity.updated_at && (
            <div>
              <dt className="font-medium">Last Updated</dt>
              <dd className="mt-1">{formatDate(entity.updated_at)}</dd>
            </div>
          )}
          {entity.completed_at && (
            <div>
              <dt className="font-medium">Completed</dt>
              <dd className="mt-1">{formatDate(entity.completed_at)}</dd>
            </div>
          )}
        </dl>
      </div>
      
      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t">
        <button 
          onClick={() => setIsEditModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Edit
        </button>
        <button 
          onClick={() => setShowAuditHistory(!showAuditHistory)}
          className={`px-4 py-2 rounded-lg transition-colors ${
            showAuditHistory 
              ? 'bg-blue-600 text-white hover:bg-blue-700' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {showAuditHistory ? 'Hide History' : 'View History'}
        </button>
        <button
          onClick={() => setShowNotes(!showNotes)}
          className={`px-4 py-2 rounded-lg transition-colors ${
            showNotes 
              ? 'bg-blue-600 text-white hover:bg-blue-700' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {showNotes ? 'Hide Notes' : 'View Notes'}
        </button>
      </div>
      
      {/* Notes Section */}
      {showNotes && (
        <div className="pt-6 border-t">
          <EntityNotes entityType={type} entityId={entity.id} />
        </div>
      )}
      
      {/* Audit History Section */}
      {showAuditHistory && (
        <div className="pt-6 border-t">
          <AuditHistory entityType={type} entityId={entity.id} />
        </div>
      )}
      
      {/* Statistics Section */}
      <div className="pt-6 border-t">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Statistics</h2>
        <EntityStatistics entityId={entity.id} entityType={type} />
      </div>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title={`Edit ${getEntityDisplayName(type)}`}
        size="lg"
      >
        <EntityForm
          initialData={{
            name: entity.name || entity.title || '',
            title: entity.title || entity.name || '',
            short_description: entity.short_description || '',
            long_description: entity.long_description || '',
            status: entity.status || '',
            priority: entity.priority || '',
            start_date: (entity.start_date || entity.startDate) ? formatDateForInput(entity.start_date || entity.startDate) : '',
            end_date: (entity.end_date || entity.endDate) ? formatDateForInput(entity.end_date || entity.endDate) : (entity.due_date || entity.dueDate) ? formatDateForInput(entity.due_date || entity.dueDate) : '',
            due_date: (entity.due_date || entity.dueDate) ? formatDateForInput(entity.due_date || entity.dueDate) : '',
            acceptance_criteria: entity.acceptance_criteria || entity.acceptanceCriteria || '',
            story_points: entity.story_points || entity.storyPoints || 0
          }}
          onSubmit={async (data) => {
            setIsUpdating(true)
            try {
              // Map name/title based on entity type
              const updateData: any = { ...data }
              if (type === 'userstory' || type === 'task') {
                if (data.title) updateData.title = data.title
                if (data.name && !data.title) updateData.title = data.name
                delete updateData.name
              } else {
                if (data.name) updateData.name = data.name
                if (data.title && !data.name) updateData.name = data.title
                delete updateData.title
              }
              
              await api.updateEntity(type, entity.id, updateData)
              setIsEditModalOpen(false)
              // Reload the page to refresh data
              window.location.reload()
            } catch (error: any) {
              console.error('Failed to update entity:', error)
              alert(error.response?.data?.detail || error.message || 'Failed to update entity')
            } finally {
              setIsUpdating(false)
            }
          }}
          onCancel={() => setIsEditModalOpen(false)}
          isLoading={isUpdating}
          mode="edit"
          entityType={getEntityDisplayName(type)}
        />
      </Modal>
    </div>
  )
}
