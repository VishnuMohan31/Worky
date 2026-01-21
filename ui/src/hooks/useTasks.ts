/**
 * React Query hooks for task operations
 * Provides shared cache and automatic synchronization across pages
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'

// Query keys for tasks
export const taskKeys = {
  all: ['tasks'] as const,
  lists: () => [...taskKeys.all, 'list'] as const,
  list: (filters?: Record<string, any>) => 
    [...taskKeys.lists(), filters] as const,
  details: () => [...taskKeys.all, 'detail'] as const,
  detail: (id: string) => [...taskKeys.details(), id] as const,
  sprint: (sprintId: string) => [...taskKeys.all, 'sprint', sprintId] as const,
  userStory: (userStoryId: string) => [...taskKeys.all, 'userStory', userStoryId] as const,
}

/**
 * Hook to fetch all tasks
 */
export function useTasks(projectId?: string) {
  return useQuery({
    queryKey: taskKeys.list({ projectId }),
    queryFn: () => api.getTasks(projectId),
    staleTime: 30 * 1000, // 30 seconds
    refetchOnWindowFocus: true,
  })
}

/**
 * Hook to fetch tasks for a specific sprint
 */
export function useSprintTasks(sprintId: string) {
  return useQuery({
    queryKey: taskKeys.sprint(sprintId),
    queryFn: () => api.getSprintTasks(sprintId),
    enabled: !!sprintId,
    staleTime: 30 * 1000,
    refetchOnWindowFocus: true,
  })
}

/**
 * Hook to fetch tasks for a specific user story
 */
export function useUserStoryTasks(userStoryId: string) {
  return useQuery({
    queryKey: taskKeys.userStory(userStoryId),
    queryFn: async () => {
      const allTasks = await api.getTasks()
      // Filter tasks by user story
      return allTasks.filter((t: any) => 
        (t.userStoryId === userStoryId || t.user_story_id === userStoryId)
      )
    },
    enabled: !!userStoryId,
    staleTime: 30 * 1000,
    refetchOnWindowFocus: true,
  })
}

/**
 * Hook to update a task
 * Automatically invalidates relevant caches to sync across pages
 */
export function useUpdateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => 
      api.updateTask(id, data),
    onSuccess: (updatedTask, variables) => {
      // Invalidate all task-related queries to sync across pages
      queryClient.invalidateQueries({ queryKey: taskKeys.all })
      
      // Also update the specific task in cache if it exists
      queryClient.setQueryData(
        taskKeys.detail(variables.id),
        updatedTask
      )
    },
    onError: (error) => {
      console.error('Failed to update task:', error)
    },
  })
}
