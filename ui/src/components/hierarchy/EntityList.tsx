/**
 * EntityList Component
 * Displays list of child entities in the bottom context pane
 */
import { useState } from 'react'
import { EntityType, getEntityPluralName } from '../../stores/hierarchyStore'
import EntityCard from './EntityCard'
import Modal from '../common/Modal'
import EntityForm from '../forms/EntityForm'
import { useCreateEntity } from '../../hooks/useEntity'

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
      // Add parent ID based on entity type
      const parentField = getParentFieldName(entityType)
      const entityData = {
        ...data,
        [parentField]: parentId
      }
      
      await createEntity.mutateAsync(entityData)
      setIsCreateModalOpen(false)
    } catch (error) {
      console.error('Failed to create entity:', error)
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
        <EntityForm
          onSubmit={handleCreateEntity}
          onCancel={() => setIsCreateModalOpen(false)}
          isLoading={createEntity.isPending}
          mode="create"
          entityType={getEntityPluralName(entityType).slice(0, -1)}
        />
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
