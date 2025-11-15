/**
 * AuditHistory Component
 * Displays audit log entries for an entity in reverse chronological order
 */
import { useState, useEffect } from 'react'
import api from '../../services/api'

interface AuditLogEntry {
  id: string
  user_id: string
  user_name?: string
  action: string
  entity_type: string
  entity_id: string
  changes: Record<string, { old: any; new: any }> | null
  created_at: string
  ip_address?: string
  user_agent?: string
}

interface AuditHistoryProps {
  entityType: string
  entityId: string
}

export default function AuditHistory({ entityType, entityId }: AuditHistoryProps) {
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [hasMore, setHasMore] = useState(false)
  
  // Filters
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [actionFilter, setActionFilter] = useState('')
  
  const pageSize = 100

  useEffect(() => {
    loadAuditLogs()
  }, [entityType, entityId, page, dateFrom, dateTo, actionFilter])

  const loadAuditLogs = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const filters: any = {
        page,
        page_size: pageSize
      }
      
      if (dateFrom) filters.date_from = dateFrom
      if (dateTo) filters.date_to = dateTo
      if (actionFilter) filters.action = actionFilter
      
      const response = await api.getAuditLogs(entityType, entityId, filters)
      
      setAuditLogs(response.items || response)
      setTotalPages(Math.ceil((response.total || response.length) / pageSize))
      setHasMore(response.has_more || false)
    } catch (err: any) {
      setError(err.message || 'Failed to load audit history')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getActionColor = (action: string) => {
    const colors: Record<string, string> = {
      'CREATE': 'bg-green-100 text-green-800',
      'UPDATE': 'bg-blue-100 text-blue-800',
      'DELETE': 'bg-red-100 text-red-800',
      'VIEW': 'bg-gray-100 text-gray-800'
    }
    return colors[action] || 'bg-gray-100 text-gray-800'
  }

  const getActionIcon = (action: string) => {
    const icons: Record<string, string> = {
      'CREATE': '➕',
      'UPDATE': '✏️',
      'DELETE': '🗑️',
      'VIEW': '👁️'
    }
    return icons[action] || '•'
  }

  const renderChanges = (changes: Record<string, { old: any; new: any }> | null) => {
    if (!changes || Object.keys(changes).length === 0) {
      return <span className="text-gray-500 text-sm">No field changes recorded</span>
    }

    return (
      <div className="mt-2 space-y-1">
        {Object.entries(changes).map(([field, change]) => (
          <div key={field} className="text-sm">
            <span className="font-medium text-gray-700">{field}:</span>
            <div className="ml-4 flex items-center gap-2">
              <span className="text-red-600 line-through">
                {change.old !== null && change.old !== undefined 
                  ? String(change.old) 
                  : '(empty)'}
              </span>
              <span className="text-gray-400">→</span>
              <span className="text-green-600">
                {change.new !== null && change.new !== undefined 
                  ? String(change.new) 
                  : '(empty)'}
              </span>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const handleClearFilters = () => {
    setDateFrom('')
    setDateTo('')
    setActionFilter('')
    setPage(1)
  }

  if (loading && page === 1) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading audit history...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error: {error}</p>
        <button
          onClick={loadAuditLogs}
          className="mt-2 text-sm text-red-600 hover:text-red-700 underline"
        >
          Try again
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Audit History</h3>
        <span className="text-sm text-gray-500">
          {auditLogs.length} {auditLogs.length === 1 ? 'entry' : 'entries'}
        </span>
      </div>

      {/* Filters */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              From Date
            </label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value)
                setPage(1)
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              To Date
            </label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value)
                setPage(1)
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Action Type
            </label>
            <select
              value={actionFilter}
              onChange={(e) => {
                setActionFilter(e.target.value)
                setPage(1)
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Actions</option>
              <option value="CREATE">Create</option>
              <option value="UPDATE">Update</option>
              <option value="DELETE">Delete</option>
              <option value="VIEW">View</option>
            </select>
          </div>
        </div>
        
        {(dateFrom || dateTo || actionFilter) && (
          <button
            onClick={handleClearFilters}
            className="text-sm text-blue-600 hover:text-blue-700 underline"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Audit Log Entries */}
      {auditLogs.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No audit history found</p>
          {(dateFrom || dateTo || actionFilter) && (
            <button
              onClick={handleClearFilters}
              className="mt-2 text-sm text-blue-600 hover:text-blue-700 underline"
            >
              Clear filters to see all entries
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {auditLogs.map((log) => (
            <div
              key={log.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  {/* Action Badge */}
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getActionColor(log.action)} flex items-center gap-1`}>
                    <span>{getActionIcon(log.action)}</span>
                    {log.action}
                  </span>
                  
                  {/* Details */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-gray-900">
                        {log.user_name || `User ${log.user_id.substring(0, 8)}`}
                      </span>
                      <span className="text-gray-400">•</span>
                      <span className="text-sm text-gray-600">
                        {formatDate(log.created_at)}
                      </span>
                    </div>
                    
                    {/* Changed Fields */}
                    {log.action === 'UPDATE' && renderChanges(log.changes)}
                    
                    {log.action === 'CREATE' && (
                      <p className="text-sm text-gray-600 mt-1">
                        Created new {entityType}
                      </p>
                    )}
                    
                    {log.action === 'DELETE' && (
                      <p className="text-sm text-gray-600 mt-1">
                        Deleted {entityType}
                      </p>
                    )}
                    
                    {log.action === 'VIEW' && (
                      <p className="text-sm text-gray-600 mt-1">
                        Viewed {entityType}
                      </p>
                    )}
                    
                    {/* Additional metadata */}
                    {log.ip_address && (
                      <div className="mt-2 text-xs text-gray-500">
                        IP: {log.ip_address}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4 border-t">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          <span className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages || !hasMore}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
      
      {loading && page > 1 && (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
      )}
    </div>
  )
}
