/**
 * EntityStatistics Component
 * Displays statistics for an entity including status distribution, phase distribution, and rollup counts
 */
import { useEffect, useState } from 'react'
import { EntityType } from '../../stores/hierarchyStore'
import { EntityStatistics as EntityStatsType } from '../../types/entities'
import api from '../../services/api'
import PhaseDistributionChart from './PhaseDistributionChart'

interface EntityStatisticsProps {
  entityId: string
  entityType: EntityType
}

export default function EntityStatistics({ entityId, entityType }: EntityStatisticsProps) {
  const [stats, setStats] = useState<EntityStatsType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStatistics()
  }, [entityId, entityType])

  const loadStatistics = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getEntityStatistics(entityType, entityId)
      setStats(data)
    } catch (err) {
      console.error('Failed to load statistics:', err)
      setError('Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

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
    <div className="space-y-6">
      {/* Status Distribution */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Status Distribution</h3>
        
        {totalItems > 0 ? (
          <>
            {/* Status Counts */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {Object.entries(stats.status_counts).map(([status, count]) => (
                <div key={status} className="text-center">
                  <div className={`inline-flex items-center justify-center px-3 py-2 rounded-lg ${getStatusColor(status)}`}>
                    <span className="text-2xl font-bold">{count}</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">{status}</p>
                </div>
              ))}
            </div>

            {/* Completion Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Completion Progress</span>
                <span className="font-semibold">{stats.completion_percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  className="bg-green-500 h-full rounded-full transition-all duration-500 ease-out flex items-center justify-center text-xs text-white font-medium"
                  style={{ width: `${stats.completion_percentage}%` }}
                >
                  {stats.completion_percentage > 10 && `${stats.completion_percentage}%`}
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
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Phase Distribution</h3>
          <PhaseDistributionChart data={stats.phase_distribution} />
        </div>
      )}

      {/* Rollup Counts */}
      {stats.rollup_counts && Object.keys(stats.rollup_counts).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hierarchy Summary</h3>
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Entity Type
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Count
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(stats.rollup_counts).map(([entityType, count]) => (
                  <tr key={entityType} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">
                      {entityType}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-semibold">
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
