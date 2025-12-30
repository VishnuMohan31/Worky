/**
 * PhaseManager Component
 * Admin interface for managing phases
 * - Display table of all phases with name, description, color, status
 * - Add "Create Phase" button (Admin only)
 * - Show usage count for each phase
 * - Add Edit and Deactivate buttons
 */
import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import api from '../../services/api'
import Modal from '../common/Modal'
import PhaseForm from './PhaseForm'

interface Phase {
  id: string
  name: string
  description: string
  color: string
  isActive: boolean
  displayOrder: number
  usageCount?: number
}

interface PhaseUsage {
  totalCount: number
  taskCount: number
  subtaskCount: number
  taskStatusBreakdown: Record<string, number>
  subtaskStatusBreakdown: Record<string, number>
}

export default function PhaseManager() {
  const { user } = useAuth()
  const [phases, setPhases] = useState<Phase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingPhase, setEditingPhase] = useState<Phase | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [includeInactive, setIncludeInactive] = useState(false)
  const [phaseUsage, setPhaseUsage] = useState<Record<string, PhaseUsage>>({})

  // Check if user is Admin
  if (user?.role !== 'Admin') {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-red-600 text-5xl mb-4">🔒</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Access Denied</h2>
          <p className="text-gray-600">Admin role required to manage phases</p>
        </div>
      </div>
    )
  }

  useEffect(() => {
    loadPhases()
  }, [includeInactive])

  const loadPhases = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getPhases(includeInactive)
      setPhases(data)
      
      // Load usage counts for all phases
      const usageCounts: Record<string, PhaseUsage> = {}
      for (const phase of data) {
        try {
          const usage = await api.getPhaseUsage(phase.id)
          usageCounts[phase.id] = usage
        } catch (err) {
          console.error(`Failed to load usage for phase ${phase.id}:`, err)
        }
      }
      setPhaseUsage(usageCounts)
    } catch (err: any) {
      setError(err.message || 'Failed to load phases')
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePhase = () => {
    setEditingPhase({
      id: '',
      name: '',
      description: '',
      color: '#4A90E2',
      isActive: true,
      displayOrder: phases.length + 1
    })
    setIsModalOpen(true)
  }

  const handleEditPhase = (phase: Phase) => {
    setEditingPhase(phase)
    setIsModalOpen(true)
  }

  const handleSavePhase = async (phaseData: Omit<Phase, 'id' | 'usageCount'>) => {
    try {
      if (editingPhase?.id) {
        // Update existing phase
        await api.updatePhase(editingPhase.id, phaseData)
      } else {
        // Create new phase
        await api.createPhase(phaseData)
      }
      
      setIsModalOpen(false)
      setEditingPhase(null)
      await loadPhases()
    } catch (err: any) {
      throw new Error(err.message || 'Failed to save phase')
    }
  }

  const handleDeactivatePhase = async (phase: Phase) => {
    const usage = phaseUsage[phase.id]
    const totalUsage = usage?.totalCount || 0
    
    if (totalUsage > 0) {
      alert(
        `Cannot deactivate phase "${phase.name}": ${totalUsage} tasks/subtasks are using it.\n\n` +
        `Tasks: ${usage.taskCount}\n` +
        `Subtasks: ${usage.subtaskCount}\n\n` +
        `Please reassign these items to another phase before deactivating.`
      )
      return
    }

    if (!confirm(`Are you sure you want to deactivate the phase "${phase.name}"?`)) {
      return
    }

    try {
      await api.deactivatePhase(phase.id)
      await loadPhases()
    } catch (err: any) {
      alert(`Failed to deactivate phase: ${err.message}`)
    }
  }

  const handleViewUsage = async (phase: Phase) => {
    const usage = phaseUsage[phase.id]
    if (!usage) return

    const message = `
Phase Usage: ${phase.name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total: ${usage.totalCount} items

Tasks: ${usage.taskCount}
${Object.entries(usage.taskStatusBreakdown || {})
  .map(([status, count]) => `  • ${status}: ${count}`)
  .join('\n')}

Subtasks: ${usage.subtaskCount}
${Object.entries(usage.subtaskStatusBreakdown || {})
  .map(([status, count]) => `  • ${status}: ${count}`)
  .join('\n')}
    `.trim()

    alert(message)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading phases...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-red-600 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Error Loading Phases</h2>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={loadPhases}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Phase Management</h1>
        <p className="text-gray-600">
          Manage work phases for tasks and subtasks. Phases categorize work by activity type.
        </p>
      </div>

      {/* Actions Bar */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={handleCreatePhase}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create New Phase
          </button>

          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(e) => setIncludeInactive(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            Show inactive phases
          </label>
        </div>

        <div className="text-sm text-gray-600">
          {phases.length} phase{phases.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Phases Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Phase
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Color
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Usage
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {phases.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                  No phases found. Create your first phase to get started.
                </td>
              </tr>
            ) : (
              phases.map((phase) => {
                const usage = phaseUsage[phase.id]
                const totalUsage = usage?.totalCount || 0

                return (
                  <tr key={phase.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: phase.color }}
                          title={phase.color}
                        />
                        <span className="text-sm font-medium text-gray-900">{phase.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-600">{phase.description || '—'}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <input
                          type="color"
                          value={phase.color}
                          disabled
                          className="w-8 h-8 rounded border border-gray-300 cursor-not-allowed"
                        />
                        <span className="text-xs text-gray-500 font-mono">{phase.color}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {phase.isActive ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {usage ? (
                        <button
                          onClick={() => handleViewUsage(phase)}
                          className="text-sm text-blue-600 hover:text-blue-700 hover:underline"
                          title="Click to view detailed usage"
                        >
                          {totalUsage} item{totalUsage !== 1 ? 's' : ''}
                        </button>
                      ) : (
                        <span className="text-sm text-gray-400">Loading...</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleEditPhase(phase)}
                          className="text-blue-600 hover:text-blue-700 px-3 py-1 rounded hover:bg-blue-50 transition-colors"
                        >
                          Edit
                        </button>
                        {phase.isActive && (
                          <button
                            onClick={() => handleDeactivatePhase(phase)}
                            className="text-red-600 hover:text-red-700 px-3 py-1 rounded hover:bg-red-50 transition-colors"
                            disabled={totalUsage > 0}
                            title={
                              totalUsage > 0
                                ? `Cannot deactivate: ${totalUsage} items are using this phase`
                                : 'Deactivate this phase'
                            }
                          >
                            Deactivate
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Phase Form Modal */}
      {isModalOpen && editingPhase && (
        <Modal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false)
            setEditingPhase(null)
          }}
          title={editingPhase.id ? 'Edit Phase' : 'Create New Phase'}
          size="md"
        >
          <PhaseForm
            phase={editingPhase}
            onSave={handleSavePhase}
            onCancel={() => {
              setIsModalOpen(false)
              setEditingPhase(null)
            }}
            existingPhaseNames={phases.filter(p => p.id !== editingPhase.id).map(p => p.name)}
          />
        </Modal>
      )}
    </div>
  )
}
