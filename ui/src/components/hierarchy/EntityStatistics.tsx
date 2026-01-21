/**
 * EntityStatistics Component
 * Displays statistics for an entity including status distribution, phase distribution, and rollup counts
 */
import { useEffect, useState, useCallback, useRef } from 'react'
import { EntityType } from '../../stores/hierarchyStore'
import { EntityStatistics as EntityStatsType } from '../../types/entities'
import api from '../../services/api'
import PhaseDistributionChart from './PhaseDistributionChart'

// Add error boundary for statistics
function SafePhaseDistributionChart({ data }: { data: any }) {
  try {
    return <PhaseDistributionChart data={data} />
  } catch (error) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-800">Chart temporarily unavailable</p>
        <p className="text-sm text-yellow-600">Phase distribution data is available but chart rendering failed.</p>
      </div>
    )
  }
}

interface EntityStatisticsProps {
  entityId: string
  entityType: EntityType
  refreshKey?: number // Add refresh key to trigger reload
}

export default function EntityStatistics({ entityId, entityType, refreshKey = 0 }: EntityStatisticsProps) {
  const [stats, setStats] = useState<EntityStatsType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const loadTimeoutRef = useRef<NodeJS.Timeout>()

  const loadStatistics = useCallback(async () => {
    // Clear any existing timeout
    if (loadTimeoutRef.current) {
      clearTimeout(loadTimeoutRef.current)
    }

    // Debounce the API call
    loadTimeoutRef.current = setTimeout(async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Validate that entityId matches entityType pattern
      const idPrefixes: Record<string, string> = {
        'client': 'CLI',
        'program': 'PRG', 
        'project': 'PRJ',
        'usecase': 'USC',
        'userstory': 'UST',
        'task': 'TSK',
        'subtask': 'SUB',
        'bug': 'BUG',
        'phase': 'PHS',
        'user': 'USR'
      }
      
      const expectedPrefix = idPrefixes[entityType]
      if (expectedPrefix && !entityId.startsWith(expectedPrefix)) {
        setStats({
          status_counts: {},
          phase_distribution: undefined,
          rollup_counts: {},
          completion_percentage: 0.0
        })
        return
      }
      
      const data = await api.getEntityStatistics(entityType, entityId)
      setStats(data)
    } catch (err) {
      setError('Failed to load statistics')
    } finally {
      setLoading(false)
    }
    }, 50) // Reduced debounce for faster refresh
  }, [entityType, entityId, refreshKey]) // Add refreshKey to dependencies

  useEffect(() => {
    loadStatistics()

    // Cleanup timeout on unmount
    return () => {
      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current)
      }
    }
  }, [loadStatistics])

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-red-600">{error || 'No statistics available'}</p>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'Not Started': 'bg-gray-100 text-gray-800',
      'To Do': 'bg-gray-100 text-gray-800',
      'Planning': 'bg-gray-100 text-gray-800',
      'In Progress': 'bg-blue-100 text-blue-800',
      'In Review': 'bg-yellow-100 text-yellow-800',
      'Completed': 'bg-green-100 text-green-800',
      'Done': 'bg-green-100 text-green-800',
      'Blocked': 'bg-red-100 text-red-800',
      'On Hold': 'bg-yellow-100 text-yellow-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const totalItems = Object.values(stats.status_counts).reduce((sum, count) => sum + count, 0)

  return (
    <div style={{ 
      padding: '0.5rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {/* Status Distribution */}
      <div style={{ 
        backgroundColor: '#ffffff',
        borderRadius: '0.5rem',
        border: '1px solid #e5e7eb',
        padding: '1rem'
      }}>
        <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#111827', marginBottom: '0.75rem' }}>
          Status Distribution
        </h3>
        
        {totalItems > 0 ? (
          <>
            {/* Status Counts */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              {Object.entries(stats.status_counts).map(([status, count]) => (
                <div key={status} className="text-center">
                  <div className={`inline-flex items-center justify-center px-2 py-1 rounded-md ${getStatusColor(status)}`}>
                    <span className="text-lg font-bold">{count}</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">{status}</p>
                </div>
              ))}
            </div>

            {/* Completion Progress Bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-gray-600">
                <span>Completion</span>
                <span className="font-semibold">{stats.completion_percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-green-500 h-full rounded-full transition-all duration-500 ease-out flex items-center justify-center text-xs text-white font-medium"
                  style={{ width: `${stats.completion_percentage}%` }}
                >
                  {stats.completion_percentage > 15 && `${stats.completion_percentage}%`}
                </div>
              </div>
            </div>
          </>
        ) : (
          <p className="text-gray-500 text-center py-4">No items to display</p>
        )}
      </div>

      {/* Phase Distribution (for User Stories and above) */}
      {stats.phase_distribution && stats.phase_distribution.length > 0 && (
        <div style={{ 
          backgroundColor: '#ffffff',
          borderRadius: '0.5rem',
          border: '1px solid #e5e7eb',
          padding: '1rem'
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#111827', marginBottom: '0.75rem' }}>
            Phase Distribution
          </h3>
          <div style={{ minHeight: '120px' }}>
            <SafePhaseDistributionChart data={stats.phase_distribution} />
          </div>
        </div>
      )}

      {/* Rollup Counts */}
      {stats.rollup_counts && Object.keys(stats.rollup_counts).length > 0 && (
        <div style={{ 
          backgroundColor: '#ffffff',
          borderRadius: '0.5rem',
          border: '1px solid #e5e7eb',
          padding: '1rem'
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#111827', marginBottom: '0.75rem' }}>
            Hierarchy Summary
          </h3>
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Count
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(stats.rollup_counts).map(([entityType, count]) => (
                  <tr key={entityType} className="hover:bg-gray-50">
                    <td className="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">
                      {entityType}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 text-right font-semibold">
                      {count}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
