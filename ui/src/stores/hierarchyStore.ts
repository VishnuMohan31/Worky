/**
 * Zustand store for hierarchy navigation state
 * Manages current entity, parent, and children for three-pane navigation
 */
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export type EntityType = 'client' | 'program' | 'project' | 'usecase' | 'userstory' | 'task' | 'subtask' | 'bug' | 'phase' | 'user'

export interface Entity {
  id: string
  name: string
  description?: string
  status?: string
  [key: string]: any
}

export interface BreadcrumbItem {
  id: string
  name: string
  type: EntityType
}

interface HierarchyState {
  // Current state
  currentEntity: Entity | null
  currentEntityType: EntityType | null
  parentEntity: Entity | null
  parentEntityType: EntityType | null
  childEntities: Entity[]
  childEntityType: EntityType | null
  breadcrumb: BreadcrumbItem[]
  
  // Loading states
  isLoading: boolean
  error: string | null
  
  // Actions
  setCurrentEntity: (entity: Entity | null, type: EntityType | null) => void
  setParentEntity: (entity: Entity | null, type: EntityType | null) => void
  setChildEntities: (entities: Entity[], type: EntityType | null) => void
  setBreadcrumb: (breadcrumb: BreadcrumbItem[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  navigateToEntity: (entityId: string, entityType: EntityType) => void
  reset: () => void
}

const initialState = {
  currentEntity: null,
  currentEntityType: null,
  parentEntity: null,
  parentEntityType: null,
  childEntities: [],
  childEntityType: null,
  breadcrumb: [],
  isLoading: false,
  error: null
}

export const useHierarchyStore = create<HierarchyState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,
        
        setCurrentEntity: (entity, type) => {
          set({ currentEntity: entity, currentEntityType: type })
        },
        
        setParentEntity: (entity, type) => {
          set({ parentEntity: entity, parentEntityType: type })
        },
        
        setChildEntities: (entities, type) => {
          set({ childEntities: entities, childEntityType: type })
        },
        
        setBreadcrumb: (breadcrumb) => {
          set({ breadcrumb })
        },
        
        setLoading: (loading) => {
          set({ isLoading: loading })
        },
        
        setError: (error) => {
          set({ error })
        },
        
        navigateToEntity: async (entityId: string, entityType: EntityType) => {
          // This will be implemented with API calls in the component
          // Store just manages the state
          set({ 
            isLoading: true, 
            error: null,
            currentEntity: null,
            parentEntity: null,
            childEntities: []
          })
        },
        
        reset: () => {
          set(initialState)
        }
      }),
      {
        name: 'hierarchy-navigation',
        partialize: (state) => ({
          // Only persist the current navigation state, not loading/error
          currentEntity: state.currentEntity,
          currentEntityType: state.currentEntityType,
          breadcrumb: state.breadcrumb
        })
      }
    ),
    { name: 'HierarchyStore' }
  )
)

// Helper functions for entity type relationships
export const getParentType = (entityType: EntityType): EntityType | null => {
  const hierarchy: Record<EntityType, EntityType | null> = {
    client: null,
    program: 'client',
    project: 'program',
    usecase: 'project',
    userstory: 'usecase',
    task: 'userstory',
    subtask: 'task'
  }
  return hierarchy[entityType]
}

export const getChildType = (entityType: EntityType): EntityType | null => {
  const hierarchy: Record<EntityType, EntityType | null> = {
    client: 'program',
    program: 'project',
    project: 'usecase',
    usecase: 'userstory',
    userstory: 'task',
    task: 'subtask',
    subtask: null
  }
  return hierarchy[entityType]
}

export const getEntityDisplayName = (entityType: EntityType): string => {
  const names: Record<EntityType, string> = {
    client: 'Client',
    program: 'Program',
    project: 'Project',
    usecase: 'Use Case',
    userstory: 'User Story',
    task: 'Task',
    subtask: 'Subtask'
  }
  return names[entityType]
}

export const getEntityPluralName = (entityType: EntityType): string => {
  const names: Record<EntityType, string> = {
    client: 'Clients',
    program: 'Programs',
    project: 'Projects',
    usecase: 'Use Cases',
    userstory: 'User Stories',
    task: 'Tasks',
    subtask: 'Subtasks'
  }
  return names[entityType]
}
