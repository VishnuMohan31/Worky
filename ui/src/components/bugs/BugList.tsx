/**
 * BugList Component
 * Displays list of bugs with filtering capabilities
 * Requirements: 2.1, 2.2, 2.3, 2.4
 */
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Bug, SEVERITY_OPTIONS } from '../../types/entities'
import api from '../../services/api'
import Modal from '../common/Modal'
import BugForm from '../forms/BugForm'
import BugDetails from './BugDetails'

interface BugListProps {
  entityType?: string
  entityId?: string
}

export default function BugList({ entityType, entityId }: BugListProps) {
  const { t } = useTranslation()
  const [bugs, setBugs] = useState<Bug[]>([])
  const [filteredBugs, setFilteredBugs] = useState<Bug[]>([])
  const [loading, setLoading] = useState(true)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [selectedBug, setSelectedBug] = useState<Bug | null>(null)
  
  // Filters
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterAssignee, setFilterAssignee] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  
  // Load bugs
  useEffect(() => {
    loadBugs()
  }, [entityType, entityId])
  
  // Apply filters
  useEffect(() => {
    applyFilters()
  }, [bugs, filterSeverity, filterStatus, filterAssignee, searchQuery])
  
  const loadBugs = async () => {
    try {
      setLoading(true)
      const data = await api.getBugs(entityId)
      setBugs(data)
    } catch (error) {
      console.error('Failed to load bugs:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const applyFilters = () => {
    let filtered = [...bugs]
    
    // Filter by severity
    if (filterSeverity !== 'all') {
      filtered = filtered.filter(bug => bug.severity === filterSeverity)
    }
    
    // Filter by status
    if (filterStatus !== 'all') {
      filtered = filtered.filter(bug => bug.status === filterStatus)
    }
    
    // Filter by assignee
    if (filterAssignee !== 'all') {
      filtered = filtered.filter(bug => bug.assigned_to === filterAssignee)
    }
    
    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(bug =>
        bug.title.toLowerCase().includes(query) ||
        bug.short_description?.toLowerCase().includes(query) ||
        bug.long_description?.toLowerCase().includes(query)
      )
    }
    
    setFilteredBugs(filtered)
  }
  
  const handleCreateBug = async (data: any) => {
    try {
      await api.createBug(data)
      setIsCreateModalOpen(false)
      loadBugs()
    } catch (error) {
      console.error('Failed to create bug:', error)
    }
  }
  
  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      'Critical': 'bg-red-100 text-red-800 border-red-300',
      'High': 'bg-orange-100 text-orange-800 border-orange-300',
      'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Low': 'bg-green-100 text-green-800 border-green-300'
    }
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-300'
  }
  
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'New': 'bg-blue-100 text-blue-800 border-blue-300',
      'Assigned': 'bg-purple-100 text-purple-800 border-purple-300',
      'In Progress': 'bg-indigo-100 text-indigo-800 border-indigo-300',
      'Fixed': 'bg-teal-100 text-teal-800 border-teal-300',
      'Verified': 'bg-green-100 text-green-800 border-green-300',
      'Closed': 'bg-gray-100 text-gray-800 border-gray-300',
      'Reopened': 'bg-red-100 text-red-800 border-red-300'
    }
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300'
  }
  
  const getPriorityIcon = (priority: string) => {
    if (priority === 'P0' || priority === 'P1') {
      return (
        <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
        </svg>
      )
    }
    return null
  }
  
  const formatDate = (date: string | undefined) => {
    if (!date) return null
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }
  
  // Get unique values for filters
  const uniqueStatuses = Array.from(new Set(bugs.map(b => b.status)))
  const uniqueAssignees = Array.from(new Set(bugs.map(b => b.assigned_to).filter(Boolean)))
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
        <div className="flex items-center gap-4 flex-1">
          <h2 className="text-xl font-semibold text-gray-900">
            Bugs
            <span className="ml-2 text-gray-500 text-base">({filteredBugs.length})</span>
          </h2>
          
          {/* Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <input
                type="text"
                placeholder="Search bugs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <svg
                className="absolute left-3 top-2.5 w-5 h-5 text-gray-400"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
        
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M12 4v16m8-8H4" />
          </svg>
          Create Bug
        </button>
      </div>
      
      {/* Filters */}
      <div className="flex items-center gap-4 px-6 py-3 border-b bg-white">
        {/* Severity Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Severity:</label>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All</option>
            {SEVERITY_OPTIONS.map(severity => (
              <option key={severity} value={severity}>{severity}</option>
            ))}
          </select>
        </div>
        
        {/* Status Filter */}
        {uniqueStatuses.length > 0 && (
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Status:</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All</option>
              {uniqueStatuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
        )}
        
        {/* Assignee Filter */}
        {uniqueAssignees.length > 0 && (
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Assignee:</label>
            <select
              value={filterAssignee}
              onChange={(e) => setFilterAssignee(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All</option>
              {uniqueAssignees.map(assignee => (
                <option key={assignee} value={assignee}>{assignee}</option>
              ))}
            </select>
          </div>
        )}
        
        {/* Clear Filters */}
        {(filterSeverity !== 'all' || filterStatus !== 'all' || filterAssignee !== 'all' || searchQuery) && (
          <button
            onClick={() => {
              setFilterSeverity('all')
              setFilterStatus('all')
              setFilterAssignee('all')
              setSearchQuery('')
            }}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Clear Filters
          </button>
        )}
      </div>
      
      {/* Bug List */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredBugs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <svg
              className="w-16 h-16 text-gray-300 mb-4"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-1">
              {bugs.length === 0 ? 'No Bugs Yet' : 'No Bugs Match Filters'}
            </h3>
            <p className="text-gray-500 mb-4">
              {bugs.length === 0 
                ? 'Get started by creating a new bug report'
                : 'Try adjusting your filters to see more results'
              }
            </p>
            {bugs.length === 0 && (
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create First Bug
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {filteredBugs.map(bug => (
              <div
                key={bug.id}
                onClick={() => setSelectedBug(bug)}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-blue-300 transition-all cursor-pointer group"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {getPriorityIcon(bug.priority)}
                      <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {bug.title}
                      </h3>
                    </div>
                    {bug.short_description && (
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {bug.short_description}
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Badges */}
                <div className="flex items-center gap-2 flex-wrap mb-3">
                  {/* Severity Badge */}
                  <span className={`px-2 py-1 text-xs font-medium rounded border ${getSeverityColor(bug.severity)}`}>
                    {bug.severity}
                  </span>
                  
                  {/* Priority Badge */}
                  <span className="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-800 border border-gray-300">
                    {bug.priority}
                  </span>
                  
                  {/* Status Badge */}
                  <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(bug.status)}`}>
                    {bug.status}
                  </span>
                </div>
                
                {/* Associated Entity */}
                {bug.entity_type && bug.entity_id && (
                  <div className="mb-3 text-sm text-gray-600">
                    <span className="font-medium">Associated with:</span>{' '}
                    <span className="text-blue-600">{bug.entity_type}</span>
                  </div>
                )}
                
                {/* Footer */}
                <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
                  <div className="flex items-center gap-4">
                    {/* Reporter */}
                    {bug.reported_by && (
                      <div className="flex items-center gap-1">
                        <svg className="w-3.5 h-3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                          <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        <span>Reported by {bug.reported_by}</span>
                      </div>
                    )}
                    
                    {/* Assignee */}
                    {bug.assigned_to && (
                      <div className="flex items-center gap-1">
                        <svg className="w-3.5 h-3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <span>Assigned to {bug.assigned_to}</span>
                      </div>
                    )}
                    
                    {/* Created Date */}
                    <div className="flex items-center gap-1">
                      <svg className="w-3.5 h-3.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span>{formatDate(bug.created_at)}</span>
                    </div>
                  </div>
                  
                  {/* View Details Arrow */}
                  <span className="text-blue-600 font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    View Details
                    <svg className="w-3 h-3" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M9 5l7 7-7 7" />
                    </svg>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Create Bug Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create Bug"
        size="lg"
      >
        <BugForm
          onSubmit={handleCreateBug}
          onCancel={() => setIsCreateModalOpen(false)}
          initialData={entityType && entityId ? { entity_type: entityType, entity_id: entityId } : undefined}
        />
      </Modal>
      
      {/* Bug Details Modal */}
      {selectedBug && (
        <Modal
          isOpen={!!selectedBug}
          onClose={() => setSelectedBug(null)}
          title=""
          size="xl"
        >
          <BugDetails
            bug={selectedBug}
            onUpdate={() => {
              setSelectedBug(null)
              loadBugs()
            }}
            onClose={() => setSelectedBug(null)}
          />
        </Modal>
      )}
    </div>
  )
}
