/**
 * React Query hooks for entity operations
 * 
 * These hooks provide a consistent interface for entity CRUD operations
 * with automatic cache management and invalidation strategies.
 * 
 * Requirements: 26.1, 26.2, 26.3, 26.4
 */
import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query'
import api from '../services/api'
import { EntityType } from '../stores/hierarchyStore'

// Query keys factory - provides consistent cache key structure
export const entityKeys = {
  all: ['entities'] as const,
  lists: () => [...entityKeys.all, 'list'] as const,
  list: (type: EntityType, filters?: Record<string, any>) => 
    [...entityKeys.lists(), type, filters] as const,
  details: () => [...entityKeys.all, 'detail'] as const,
  detail: (type: EntityType, id: string) => 
    [...entityKeys.details(), type, id] as const,
  context: (type: EntityType, id: string) =>
    [...entityKeys.detail(type, id), 'context'] as const,
  statistics: (type: EntityType, id: string) => 
    [...entityKeys.detail(type, id), 'statistics'] as const,
  search: (query: string, types?: EntityType[]) => 
    [...entityKeys.all, 'search', query, types] as const,
  children: (type: EntityType, id: string) =>
    [...entityKeys.detail(type, id), 'children'] as const,
  parent: (type: EntityType, id: string) =>
    [...entityKeys.detail(type, id), 'parent'] as const,
  breadcrumb: (type: EntityType, id: string) =>
    [...entityKeys.detail(type, id), 'breadcrumb'] as const,
}

// Helper to get parent entity type
function getParentType(type: EntityType): EntityType | null {
  const hierarchy: Record<EntityType, EntityType | null> = {
    client: null,
    program: 'client',
    project: 'program',
    usecase: 'project',
    userstory: 'usecase',
    task: 'userstory',
    subtask: 'task',
    bug: null,
    phase: null,
    user: null,
  }
  return hierarchy[type]
}

// Helper to get child entity type
function getChildType(type: EntityType): EntityType | null {
  const hierarchy: Record<EntityType, EntityType | null> = {
    client: 'program',
    program: 'project',
    project: 'usecase',
    usecase: 'userstory',
    userstory: 'task',
    task: 'subtask',
    subtask: null,
    bug: null,
    phase: null,
    user: null,
  }
  return hierarchy[type]
}

// Hook to fetch a single entity
export function useEntity(type: EntityType, id: string | undefined) {
  return useQuery({
    queryKey: entityKeys.detail(type, id || ''),
    queryFn: () => api.getEntity(type, id!),
    enabled: !!id,
  })
}

// Hook to fetch entity list
export function useEntityList(type: EntityType, filters?: Record<string, any>) {
  return useQuery({
    queryKey: entityKeys.list(type, filters),
    queryFn: () => api.getEntityList(type, filters),
  })
}

// Hook to fetch entity statistics
export function useEntityStatistics(type: EntityType, id: string | undefined) {
  return useQuery({
    queryKey: entityKeys.statistics(type, id || ''),
    queryFn: () => api.getEntityStatistics(type, id!),
    enabled: !!id,
  })
}

// Hook to search entities
export function useEntitySearch(query: string, types?: EntityType[]) {
  return useQuery({
    queryKey: entityKeys.search(query, types),
    queryFn: () => api.searchEntities(query, types),
    enabled: query.length >= 2,
  })
}

// Hook to create entity with comprehensive cache invalidation
export function useCreateEntity(type: EntityType) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: any) => api.createEntity(type, data),
    onSuccess: (newEntity, variables) => {
      // Invalidate all entity lists
      queryClient.invalidateQueries({ queryKey: entityKeys.lists() })
      
      // Invalidate parent's children cache if parent exists
      const parentType = getParentType(type)
      if (parentType && variables[`${parentType}_id`]) {
        const parentId = variables[`${parentType}_id`]
        queryClient.invalidateQueries({ 
          queryKey: entityKeys.children(parentType, parentId) 
        })
        queryClient.invalidateQueries({ 
          queryKey: entityKeys.detail(parentType, parentId) 
        })
        queryClient.invalidateQueries({ 
          queryKey: entityKeys.statistics(parentType, parentId) 
        })
      }
      
      // Invalidate search results
      queryClient.invalidateQueries({ queryKey: entityKeys.all })
    },
  })
}

// Hook to update entity with comprehensive cache invalidation
export function useUpdateEntity(type: EntityType) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => 
      api.updateEntity(type, id, data),
    onSuccess: (updatedEntity, variables) => {
      // Invalidate specific entity and all its related queries
      queryClient.invalidateQueries({ 
        queryKey: entityKeys.detail(type, variables.id) 
      })
      queryClient.invalidateQueries({ 
        queryKey: entityKeys.context(type, variables.id) 
      })
      queryClient.invalidateQueries({ 
        queryKey: entityKeys.statistics(type, variables.id) 
      })
      queryClient.invalidateQueries({ 
        queryKey: entityKeys.children(type, variables.id) 
      })
      
      // Invalidate entity lists
      queryClient.invalidateQueries({ queryKey: entityKeys.lists() })
      
      // Invalidate parent's queries
      const parentType = getParentType(type)
      if (parentType && updatedEntity[`${parentType}_id`]) {
        const parentId = updatedEntity[`${parentType}_id`]
        queryClient.invalidateQueries({ 
          queryKey: entityKeys.children(parentType, parentId) 
        })
        queryClient.invalidateQueries({ 
          queryKey: entityKeys.statistics(parentType, parentId) 
        })
      }
      
      // Invalidate search results
      queryClient.invalidateQueries({ queryKey: entityKeys.all })
    },
  })
}

// Hook to delete entity with comprehensive cache invalidation
export function useDeleteEntity(type: EntityType) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => api.deleteEntity(type, id),
    onSuccess: (_, deletedId) => {
      // Remove entity from cache
      queryClient.removeQueries({ 
        queryKey: entityKeys.detail(type, deletedId) 
      })
      
      // Invalidate entity lists
      queryClient.invalidateQueries({ queryKey: entityKeys.lists() })
      
      // Invalidate parent's children cache
      // Note: We'd need the parent ID here, which should be passed or fetched
      const parentType = getParentType(type)
      if (parentType) {
        queryClient.invalidateQueries({ 
          queryKey: entityKeys.lists() 
        })
      }
      
      // Invalidate search results
      queryClient.invalidateQueries({ queryKey: entityKeys.all })
    },
  })
}

// Hook to fetch entity with context (parent and children)
export function useEntityWithContext(type: EntityType, id: string | undefined) {
  return useQuery({
    queryKey: [...entityKeys.detail(type, id || ''), 'context'],
    queryFn: () => api.getEntityWithContext(type, id!),
    enabled: !!id,
  })
}
