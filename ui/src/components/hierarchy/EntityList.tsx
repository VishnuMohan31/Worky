/**
 * EntityList Component
 * Displays list of child entities in the bottom context pane
 */
import { useState, useEffect } from 'react'
import { EntityType, getEntityPluralName } from '../../stores/hierarchyStore'
import EntityCard from './EntityCard'
import Modal from '../common/Modal'
import EntityForm from '../forms/EntityForm'
import { useCreateEntity } from '../../hooks/useEntity'
import api from '../../services/api'

// Task Form with Phase Support
function TaskFormWithPhase({ 
  onSubmit, 
  onCancel, 
  isLoading 
}: { 
  onSubmit: (data: any) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
}) {
  const [phases, setPhases] = useState<any[]>([])
  const [loadingPhases, setLoadingPhases] = useState(false)
  const [phaseId, setPhaseId] = useState('') // Will be set when phases load

  useEffect(() => {
    const loadPhases = async () => {
      setLoadingPhases(true)
      try {
        const data = await api.getPhases(false) // Only active phases
        setPhases(data)
        // Set default phase to first one (usually Planning)
        if (data.length > 0) {
          setPhaseId(data[0].id)
        }
      } catch (error) {
        console.error('Failed to load phases:', error)
      } finally {
        setLoadingPhases(false)
      }
    }
    loadPhases()
  }, [])

  const handleSubmit = async (formData: any) => {
    // Ensure phase_id is set
    if (!phaseId) {
      alert('Please select a phase')
      return
    }
    await onSubmit({ ...formData, phase_id: phaseId })
  }

  return (
    <EntityForm
      initialData={{ name: '', phase_id: phaseId }}
      onSubmit={handleSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      mode="create"
      entityType="Task"
      additionalFields={
        <div>
          <label htmlFor="phase_id" className="block text-sm font-medium mb-2">
            Phase <span className="text-red-500">*</span>
          </label>
          <select
            id="phase_id"
            value={phaseId}
            onChange={(e) => setPhaseId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loadingPhases || isLoading}
            required
          >
            <option value="">Select phase...</option>
            {phases.map((phase) => (
              <option key={phase.id} value={phase.id}>
                {phase.name}
              </option>
            ))}
          </select>
          {loadingPhases && (
            <p className="text-xs text-gray-500 mt-1">Loading phases...</p>
          )}
        </div>
      }
    />
  )
}

// Subtask Form with required fields
function SubtaskFormSimple({ 
  parentId, 
  onSubmit, 
  onCancel, 
  isLoading 
}: { 
  parentId?: string
  onSubmit: (data: any) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
}) {
  const [formData, setFormData] = useState({
    name: '',
    short_description: '',
    estimated_hours: 1,
    duration_days: 1,
    status: 'To Do'
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate required fields
    if (!formData.name.trim()) {
      alert('Name is required')
      return
    }
    
    if (!parentId) {
      alert('Parent task is required')
      return
    }
    
    if (formData.estimated_hours <= 0) {
      alert('Estimated hours must be greater than 0')
      return
    }
    
    if (formData.duration_days <= 0) {
      alert('Duration days must be greater than 0')
      return
    }
    
    try {
      await onSubmit({
        ...formData,
        task_id: parentId,
        name: formData.name.trim()
      })
    } catch (error) {
      console.error('Error submitting subtask form:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium mb-2">
          Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          value={formData.name}
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter subtask name"
          required
          disabled={isLoading}
        />
      </div>
      
      <div>
        <label htmlFor="short_description" className="block text-sm font-medium mb-2">
          Description
        </label>
        <textarea
          id="short_description"
          value={formData.short_description}
          onChange={(e) => setFormData(prev => ({ ...prev, short_description: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Brief description of the subtask"
          rows={3}
          disabled={isLoading}
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="estimated_hours" className="block text-sm font-medium mb-2">
            Estimated Hours <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="estimated_hours"
            value={formData.estimated_hours}
            onChange={(e) => setFormData(prev => ({ ...prev, estimated_hours: parseFloat(e.target.value) || 1 }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            min="0.5"
            step="0.5"
            required
            disabled={isLoading}
          />
        </div>
        
        <div>
          <label htmlFor="duration_days" className="block text-sm font-medium mb-2">
            Duration Days <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="duration_days"
            value={formData.duration_days}
            onChange={(e) => setFormData(prev => ({ ...prev, duration_days: parseInt(e.target.value) || 1 }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            min="1"
            required
            disabled={isLoading}
          />
        </div>
      </div>
      
      <div className="flex justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          disabled={isLoading}
        >
          {isLoading ? 'Creating...' : 'Create Subtask'}
        </button>
      </div>
    </form>
  )
}

interface EntityListProps {
  entities: any[]
  entityType: EntityType
  onEntityClick: (entity: any) => void
  parentId?: string
}

export default function EntityList({
  entities,
  entityType,
  onEntityClick,
  parentId
}: EntityListProps) {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  
  // Safety checks
  if (!entityType) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>Entity type not specified</p>
      </div>
    )
  }
  
  const createEntity = useCreateEntity(entityType)
  
  const handleCreateEntity = async (data: any) => {
    try {

      
      // Add parent ID based on entity type
      const parentField = getParentFieldName(entityType)
      const entityData: any = {
        ...data
      }
      
      // Set parent field
      if (parentField && parentId) {
        entityData[parentField] = parentId
      }
      
      // Handle entity-specific field mappings
      // Note: Tasks, user stories, and subtasks now use 'name' field (matching the API schema)
      if (entityType === 'task' || entityType === 'userstory' || entityType === 'subtask') {
        // Convert old 'title' field to 'name' if present (for backwards compatibility)
        if (data.title && !data.name) {
          entityData.name = data.title
          delete entityData.title
        }
        // Ensure name is set for these entity types
        if (!entityData.name) {
          throw new Error('Name is required')
        }
      }
      
      // For tasks, ensure user_story_id and phase_id are set
      if (entityType === 'task') {
        if (parentId && !entityData.user_story_id) {
          entityData.user_story_id = parentId
        }
        // Ensure phase_id is set (required field)
        if (!entityData.phase_id) {
          throw new Error('Phase is required for tasks')
        }
      }
      
      // For tasks, map end_date to due_date (tasks use due_date, not end_date)
      if (entityType === 'task') {
        if (entityData.end_date && !entityData.due_date) {
          entityData.due_date = entityData.end_date
          delete entityData.end_date
        }
        // Ensure dates are in YYYY-MM-DD format (remove time if present)
        if (entityData.start_date) {
          entityData.start_date = formatDateForAPI(entityData.start_date)
        }
        if (entityData.due_date) {
          entityData.due_date = formatDateForAPI(entityData.due_date)
        }
      }
      
      // For user stories, ensure usecase_id is set
      if (entityType === 'userstory' && parentId && !entityData.usecase_id) {
        entityData.usecase_id = parentId
      }
      
      // For subtasks, ensure task_id is set and handle field mapping
      if (entityType === 'subtask') {
        // Ensure task_id is set (required field)
        if (!entityData.task_id && parentId) {
          entityData.task_id = parentId
        }
        
        // Validate required task_id
        if (!entityData.task_id) {
          throw new Error('Task ID is required for subtasks')
        }
        
        // Subtasks use 'name' field (same as API schema)
        // If title was provided but not name, convert it
        if (data.title && !data.name) {
          entityData.name = data.title
          delete entityData.title
        }
        
        // Ensure name is set (required field)
        if (!entityData.name) {
          entityData.name = data.name || data.title || 'New Subtask'
        }
        
        // Validate required name
        if (!entityData.name || entityData.name.trim() === '') {
          throw new Error('Name is required for subtasks')
        }
        
        // Remove fields that subtasks don't use
        delete entityData.end_date
        delete entityData.start_date
        delete entityData.due_date
        delete entityData.title  // API uses 'name', not 'title'
        
        // Ensure subtask-specific fields are properly set with defaults
        if (entityData.estimated_hours === undefined || entityData.estimated_hours === null || entityData.estimated_hours === '') {
          entityData.estimated_hours = 1
        }
        if (entityData.duration_days === undefined || entityData.duration_days === null || entityData.duration_days === '') {
          entityData.duration_days = 1
        }
        
        // Convert string numbers to actual numbers
        if (typeof entityData.estimated_hours === 'string') {
          entityData.estimated_hours = parseFloat(entityData.estimated_hours) || 1
        }
        if (typeof entityData.duration_days === 'string') {
          entityData.duration_days = parseInt(entityData.duration_days) || 1
        }
        
        // Set default status if not provided
        if (!entityData.status) {
          entityData.status = 'To Do'
        }
        
        // Clean up data for subtasks
        Object.keys(entityData).forEach(key => {
          const value = entityData[key]
          
          // Remove undefined values
          if (value === undefined) {
            delete entityData[key]
          }
          
          // Convert null to undefined for optional fields, or remove entirely
          if (value === null) {
            if (['phase_id', 'assigned_to', 'short_description', 'long_description', 'scrum_points', 'actual_hours'].includes(key)) {
              // Keep null for optional fields
            } else {
              delete entityData[key]
            }
          }
          
          // Remove empty strings for optional fields
          if (value === '' && ['phase_id', 'assigned_to', 'short_description', 'long_description'].includes(key)) {
            entityData[key] = null
          }
        })
        
        // Ensure required fields are present and valid
        if (!entityData.name || entityData.name.trim() === '') {
          throw new Error('Name is required for subtasks')
        }
        if (!entityData.task_id) {
          throw new Error('Task ID is required for subtasks')
        }
        if (!entityData.estimated_hours || entityData.estimated_hours <= 0) {
          entityData.estimated_hours = 1
        }
        if (!entityData.duration_days || entityData.duration_days <= 0) {
          entityData.duration_days = 1
        }
      }
      
      // Format dates for other entity types
      if (entityType !== 'task') {
        if (entityData.start_date) {
          entityData.start_date = formatDateForAPI(entityData.start_date)
        }
        if (entityData.end_date) {
          entityData.end_date = formatDateForAPI(entityData.end_date)
        }
      }
      
      // Remove empty string values and convert to null (except for required fields)
      Object.keys(entityData).forEach(key => {
        if (entityData[key] === '') {
          // Don't null out phase_id for tasks - it's required
          if (!(entityType === 'task' && key === 'phase_id')) {
            entityData[key] = null
          }
        }
      })
      
      // Additional validation for subtasks
      if (entityType === 'subtask') {
        
        if (!entityData.name || !entityData.task_id) {
          throw new Error('Missing required fields for subtask creation')
        }
      }
      
      await createEntity.mutateAsync(entityData)
      setIsCreateModalOpen(false)
      // React Query will automatically refetch the data via cache invalidation
    } catch (error: any) {
      console.error('Failed to create entity:', error)
      
      let errorMessage = 'Failed to create entity'
      
      if (error.response) {
        // API error response
        const status = error.response.status
        const data = error.response.data
        
        if (status === 401) {
          errorMessage = 'Authentication failed. Please log in again.'
          // Redirect to login if authentication failed
          window.location.href = '/login'
          return
        } else if (status === 403) {
          errorMessage = 'You do not have permission to create this entity.'
        } else if (status === 404) {
          errorMessage = 'The parent entity was not found. Please refresh the page and try again.'
        } else if (status === 422) {
          // Validation error
          if (data?.detail) {
            if (Array.isArray(data.detail)) {
              errorMessage = data.detail.map((err: any) => `${err.loc?.join('.')}: ${err.msg}`).join(', ')
            } else {
              errorMessage = data.detail
            }
          } else {
            errorMessage = 'Validation error. Please check your input.'
          }
        } else if (status === 500) {
          errorMessage = 'Server error. Please try again later.'
        } else {
          errorMessage = data?.detail || data?.message || `Server error (${status})`
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      alert(errorMessage)
    }
  }
  
  // Helper function to format date for API (YYYY-MM-DD)
  const formatDateForAPI = (date: string | Date | undefined): string | null => {
    if (!date) return null
    try {
      // If already in YYYY-MM-DD format, return as is
      if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) {
        return date
      }
      
      // Extract date part from ISO string
      if (typeof date === 'string' && date.includes('T')) {
        const datePart = date.split('T')[0]
        if (/^\d{4}-\d{2}-\d{2}$/.test(datePart)) {
          return datePart
        }
      }
      
      const dateObj = typeof date === 'string' ? new Date(date) : date
      if (isNaN(dateObj.getTime())) return null
      
      const year = dateObj.getFullYear()
      const month = String(dateObj.getMonth() + 1).padStart(2, '0')
      const day = String(dateObj.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    } catch (error) {
      console.error('Error formatting date for API:', error)
      return null
    }
  }
  
  // Filter entities
  const filteredEntities = entities.filter(entity => {
    const matchesSearch = !searchQuery || 
      entity.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entity.title?.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesStatus = filterStatus === 'all' || entity.status === filterStatus
    
    return matchesSearch && matchesStatus
  })
  
  // Get unique statuses for filter
  const statuses = Array.from(new Set(entities.map(e => e.status).filter(Boolean)))
  
  return (
    <div className="h-full flex flex-col bg-gray-50" style={{ minHeight: 0 }}>
      {/* Modern Header */}
      <div className="flex-shrink-0 bg-white border-b border-gray-200 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-5 h-5 text-white" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  {getEntityPluralName(entityType)}
                </h3>
                <p className="text-sm text-gray-600">
                  {filteredEntities.length} {filteredEntities.length === 1 ? 'item' : 'items'}
                  {searchQuery && ` matching "${searchQuery}"`}
                  {filterStatus !== 'all' && ` with status "${filterStatus}"`}
                </p>
              </div>
            </div>
            
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-medium rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-200 flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M12 4v16m8-8H4" />
              </svg>
              Add New
            </button>
          </div>
          
          {/* Enhanced Search and Filter Bar */}
          <div className="flex items-center gap-3">
            <div className="flex-1 relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="w-4 h-4 text-gray-400" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder={`Search ${getEntityPluralName(entityType).toLowerCase()}...`}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-sm"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  <svg className="w-4 h-4 text-gray-400 hover:text-gray-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
            
            {/* Status Filter */}
            {statuses.length > 0 && (
              <div className="relative">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="appearance-none bg-white border border-gray-200 rounded-xl px-4 py-2.5 pr-8 text-sm font-medium text-gray-700 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 cursor-pointer"
                >
                  <option value="all">All Status</option>
                  {statuses.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <svg className="w-4 h-4 text-gray-400" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Entity List with Modern Styling */}
      <div className="flex-1 overflow-y-auto px-6 py-4" style={{ minHeight: 0 }}>
        {filteredEntities.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
              <svg className="w-12 h-12 text-gray-400" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {searchQuery || filterStatus !== 'all' ? 'No Results Found' : `No ${getEntityPluralName(entityType)} Yet`}
            </h3>
            
            <p className="text-gray-600 mb-8 max-w-md leading-relaxed">
              {searchQuery || filterStatus !== 'all' 
                ? `Try adjusting your search or filter criteria to find what you're looking for.`
                : `Get started by creating your first ${getEntityPluralName(entityType).toLowerCase().slice(0, -1)}. You can organize and track progress from here.`
              }
            </p>
            
            {(!searchQuery && filterStatus === 'all') && (
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M12 4v16m8-8H4" />
                </svg>
                Create First {getEntityPluralName(entityType).slice(0, -1)}
              </button>
            )}
            
            {(searchQuery || filterStatus !== 'all') && (
              <div className="flex gap-3">
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors duration-200 text-sm font-medium"
                  >
                    Clear Search
                  </button>
                )}
                {filterStatus !== 'all' && (
                  <button
                    onClick={() => setFilterStatus('all')}
                    className="px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors duration-200 text-sm font-medium"
                  >
                    Clear Filter
                  </button>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredEntities.map(entity => (
              <EntityCard
                key={entity.id}
                entity={entity}
                type={entityType}
                onClick={() => onEntityClick(entity)}
                onAssignmentChange={() => {
                  // Refresh the entity list to show updated assignment info
                  // This could trigger a parent refresh if needed
                }}
              />
            ))}
          </div>
        )}
      </div>
      
      {/* Create Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title={`Create ${getEntityPluralName(entityType).slice(0, -1)}`}
        size="lg"
      >
        {entityType === 'task' ? (
          <TaskFormWithPhase
            onSubmit={handleCreateEntity}
            onCancel={() => setIsCreateModalOpen(false)}
            isLoading={createEntity.isPending}
          />
        ) : entityType === 'subtask' ? (
          <SubtaskFormSimple
            parentId={parentId}
            onSubmit={handleCreateEntity}
            onCancel={() => setIsCreateModalOpen(false)}
            isLoading={createEntity.isPending}
          />
        ) : (
          <EntityForm
            initialData={{ name: '' }}
            onSubmit={handleCreateEntity}
            onCancel={() => setIsCreateModalOpen(false)}
            isLoading={createEntity.isPending}
            mode="create"
            entityType={getEntityPluralName(entityType).slice(0, -1)}
          />
        )}
      </Modal>
    </div>
  )
}

// Helper function to get parent field name
function getParentFieldName(entityType: EntityType): string {
  const fieldMap: Record<EntityType, string> = {
    client: '',
    program: 'client_id',
    project: 'program_id',
    usecase: 'project_id',
    userstory: 'usecase_id',
    task: 'user_story_id',
    subtask: 'task_id',
    bug: 'project_id', // Bugs are typically associated with projects
    phase: '', // Phases are top-level entities
    user: '' // Users are top-level entities
  }
  return fieldMap[entityType]
}
