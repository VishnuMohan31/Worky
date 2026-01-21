/**
 * Status transition utilities
 * COMPLETELY DISABLED - Allow all status transitions for flexible kanban workflow
 */

// All valid statuses for tasks/subtasks
export const VALID_TASK_STATUSES = [
  "Planning", "In Progress", "Completed", "Blocked", "In Review", "On-Hold", "Canceled"
]

/**
 * Get allowed status transitions from a current status
 * ALWAYS returns all valid statuses - no restrictions
 */
export function getAllowedStatusTransitions(currentStatus: string | null | undefined): string[] {
  return VALID_TASK_STATUSES
}

/**
 * Check if a status transition is valid
 * ALWAYS returns true - no restrictions
 */
export function isValidStatusTransition(fromStatus: string | null | undefined, toStatus: string): boolean {
  return true
}

/**
 * Get all valid statuses for tasks/subtasks
 */
export function getAllValidTaskStatuses(): string[] {
  return [...VALID_TASK_STATUSES]
}

/**
 * Map Kanban board column to actual task status
 * Based on requirements:
 * - Any section → In Progress: "In Progress"
 * - Any section → Done: "Completed"
 * - Any section → To Do: "Planning"
 */
export function mapKanbanColumnToStatus(kanbanColumn: string): string {
  switch (kanbanColumn) {
    case 'In Progress':
      return 'In Progress'
    case 'Done':
      return 'Completed'
    case 'To Do':
      return 'Planning'
    default:
      // Fallback to Planning for unknown columns
      return 'Planning'
  }
}