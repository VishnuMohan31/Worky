/**
 * User Stories Page
 * List and manage user stories
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useEntityList } from '../hooks/useEntity'

export default function UserStoriesPage() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterPriority, setFilterPriority] = useState('all')
  
  const { data: stories = [], isLoading, error } = useEntityList('userstory')
  
  const filteredStories = stories.filter((story: any) => {
    const matchesSearch = !searchQuery || 
      story.name?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = filterStatus === 'all' || story.status === filterStatus
    const matchesPriority = filterPriority === 'all' || story.priority === filterPriority
    return matchesSearch && matchesStatus && matchesPriority
  })
  
  const statuses = Array.from(new Set(stories.map((s: any) => s.status).filter(Boolean)))
  const priorities = Array.from(new Set(stories.map((s: any) => s.priority).filter(Boolean)))
  
  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'High': 'bg-red-100 text-red-800',
      'Medium': 'bg-yellow-100 text-yellow-800',
      'Low': 'bg-green-100 text-green-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="text-center text-red-600 p-8">
        Error loading user stories: {error.message}
      </div>
    )
  }
  
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">User Stories</h1>
        <p className="text-gray-600 mt-1">Manage user-centric features and requirements</p>
      </div>
      
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Search user stories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            {statuses.map((status: string) => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Priority</option>
            {priorities.map((priority: string) => (
              <option key={priority} value={priority}>{priority}</option>
            ))}
          </select>
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            + New User Story
          </button>
        </div>
      </div>
      
      {/* User Stories List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Story
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Story Points
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Use Case
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredStories.map((story: any) => (
              <tr
                key={story.id}
                onClick={() => navigate(`/hierarchy/userstory/${story.id}`)}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">{story.name}</div>
                  {story.short_description && (
                    <div className="text-sm text-gray-500 line-clamp-1">{story.short_description}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">
                    {story.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {story.priority && (
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(story.priority)}`}>
                      {story.priority}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {story.story_points || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {story.usecase_name || story.usecase_id}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredStories.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No user stories found</p>
          </div>
        )}
      </div>
    </div>
  )
}
