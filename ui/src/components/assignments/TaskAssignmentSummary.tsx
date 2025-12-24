import { useState, useEffect } from 'react'
import api from '../../services/api'

interface AssignmentSummary {
  user_id: string
  user_name: string
  user_email: string
  task_count: number
  subtask_count: number
  total_assignments: number
}

interface TaskAssignmentSummaryProps {
  projectId?: string
  entityType?: string
  entityId?: string
}

export default function TaskAssignmentSummary({ 
  projectId, 
  entityType, 
  entityId 
}: TaskAssignmentSummaryProps) {
  const [assignments, setAssignments] = useState<any[]>([])
  const [summary, setSummary] = useState<AssignmentSummary[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadAssignments()
  }, [projectId, entityType, entityId])

  const loadAssignments = async () => {
    try {
      setLoading(true)
      let response
      
      if (entityType && entityId) {
        // Get assignments for specific entity
        response = await api.getAssignments({
          entity_type: entityType,
          entity_id: entityId
        })
      } else {
        // Get all assignments (could be filtered by project in future)
        response = await api.getAssignments()
      }
      
      setAssignments(response)
      generateSummary(response)
    } catch (error) {
      console.error('Failed to load assignments:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateSummary = (assignments: any[]) => {
    const userMap = new Map<string, AssignmentSummary>()
    
    assignments.forEach(assignment => {
      if (!assignment.is_active) return
      
      const userId = assignment.user_id
      if (!userMap.has(userId)) {
        userMap.set(userId, {
          user_id: userId,
          user_name: assignment.user_name || 'Unknown User',
          user_email: assignment.user_email || '',
          task_count: 0,
          subtask_count: 0,
          total_assignments: 0
        })
      }
      
      const userSummary = userMap.get(userId)!
      userSummary.total_assignments++
      
      if (assignment.entity_type === 'task') {
        userSummary.task_count++
      } else if (assignment.entity_type === 'subtask') {
        userSummary.subtask_count++
      }
    })
    
    setSummary(Array.from(userMap.values()).sort((a, b) => b.total_assignments - a.total_assignments))
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const getWorkloadColor = (count: number) => {
    if (count === 0) return 'bg-gray-100 text-gray-600'
    if (count <= 3) return 'bg-green-100 text-green-700'
    if (count <= 6) return 'bg-yellow-100 text-yellow-700'
    return 'bg-red-100 text-red-700'
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="text-center text-gray-500">Loading assignment summary...</div>
      </div>
    )
  }

  if (summary.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-3">Assignment Summary</h3>
        <div className="text-center text-gray-500 py-4">
          No assignments found
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
        <span className="mr-2">📊</span>
        Assignment Summary ({summary.length} developers)
      </h3>
      
      <div className="space-y-3">
        {summary.map((user) => (
          <div
            key={user.user_id}
            className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-blue-700">
                  {getInitials(user.user_name)}
                </span>
              </div>
              <div>
                <div className="font-medium text-gray-900">{user.user_name}</div>
                <div className="text-sm text-gray-500">{user.user_email}</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="text-right">
                <div className="text-sm text-gray-600">
                  {user.task_count} tasks, {user.subtask_count} subtasks
                </div>
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getWorkloadColor(user.total_assignments)}`}>
                  {user.total_assignments} total
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-500">
        <div className="flex items-center justify-between">
          <span>Total assignments: {assignments.filter(a => a.is_active).length}</span>
          <span>Active developers: {summary.length}</span>
        </div>
      </div>
    </div>
  )
}