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
      initialData={{ title: '', phase_id: phaseId }}
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
  
  const createEntity = useCreateEntity(entityType)
  
  const handleCreateEntity = async (data: any) => {
    try {
      console.log('Creating entity with data:', data)
      
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
      if (entityType === 'task' || entityType === 'userstory') {
        // Tasks and user stories use 'title' instead of 'name'
        if (data.name && !data.title) {
          entityData.title = data.name
          delete entityData.name
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
      
      console.log('Final entity data being sent to API:', entityData)
      
      await createEntity.mutateAsync(entityData)
      setIsCreateModalOpen(false)
      // Reload the page to refresh the entity list
      window.location.reload()
    } catch (error: any) {
      console.error('Failed to create entity:', error)
      const errorMessage = error.response?.data?.detail || 
                          (typeof error.response?.data === 'string' ? error.response.data : null) ||
                          error.message || 
                          'Failed to create entity'
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
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b bg-gray-50">
        <div className="flex items-center gap-4 flex-1">
          <h3 className="text-sm font-semibold text-gray-700 uppercase">
            {getEntityPluralName(entityType)}
            <span className="ml-2 text-gray-500">({filteredEntities.length})</span>
          </h3>
          
          {/* Search */}
          <div className="flex-1 max-w-xs">
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-1 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          {/* Status Filter */}
          {statuses.length > 0 && (
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              {statuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          )}
        </div>
        
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
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
            <path d="M12 4v16m8-8H4" />
          </svg>
          Add {getEntityPluralName(entityType).slice(0, -1)}
        </button>
      </div>
      
      {/* Entity List */}
      <div className="entity-list">
        {filteredEntities.length === 0 ? (
          <div className="entity-list-empty">
            <svg
              className="w-16 h-16 text-gray-300 mb-4 mx-auto"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-1">
              No {getEntityPluralName(entityType)} Yet
            </h3>
            <p className="text-gray-500 mb-4 text-sm">
              Get started by creating a new {getEntityPluralName(entityType).toLowerCase().slice(0, -1)}
            </p>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              Create First {getEntityPluralName(entityType).slice(0, -1)}
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredEntities.map(entity => (
              <EntityCard
                key={entity.id}
                entity={entity}
                type={entityType}
                onClick={() => onEntityClick(entity)}
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
            parentId={parentId}
            onSubmit={handleCreateEntity}
            onCancel={() => setIsCreateModalOpen(false)}
            isLoading={createEntity.isPending}
          />
        ) : (
          <EntityForm
            initialData={
              entityType === 'userstory'
                ? { title: '' } // Use title for user stories
                : { name: '' }  // Use name for other entities
            }
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
    subtask: 'task_id'
  }
  return fieldMap[entityType]
}
