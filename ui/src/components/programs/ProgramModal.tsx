/**
 * Program Modal Component
 * Create and edit programs (Admin only)
 */
import { useState, useEffect } from 'react'
import Modal from '../common/Modal'
import api from '../../services/api'

interface ProgramModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  program?: any
  selectedClientId?: string
  clients: any[]
  isAdmin: boolean
}

export default function ProgramModal({
  isOpen,
  onClose,
  onSuccess,
  program,
  selectedClientId,
  clients,
  isAdmin
}: ProgramModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    client_id: selectedClientId || '',
    status: 'Planning',
    start_date: '',
    end_date: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isEditMode = !!program

  useEffect(() => {
    if (program) {
      setFormData({
        name: program.name || '',
        description: program.description || '',
        client_id: program.client_id || '',
        status: program.status || 'Planning',
        start_date: program.start_date || '',
        end_date: program.end_date || ''
      })
    } else {
      setFormData({
        name: '',
        description: '',
        client_id: selectedClientId || '',
        status: 'Planning',
        start_date: '',
        end_date: ''
      })
    }
    setError('')
  }, [program, selectedClientId, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isAdmin) {
      setError('Only Admin users can create or edit programs')
      return
    }

    if (!formData.name.trim()) {
      setError('Program name is required')
      return
    }

    if (!formData.client_id) {
      setError('Please select a client')
      return
    }

    setLoading(true)
    setError('')

    try {
      if (isEditMode) {
        await api.updateEntity('program', program.id, formData)
      } else {
        await api.createEntity('program', formData)
      }
      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.message || 'Failed to save program')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  if (!isAdmin && isEditMode) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Access Denied">
        <div className="p-6 text-center">
          <p className="text-red-600">Only Admin users can edit programs.</p>
          <button
            onClick={onClose}
            className="mt-4 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Close
          </button>
        </div>
      </Modal>
    )
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditMode ? 'Edit Program' : 'Create New Program'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="p-6">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {!isAdmin && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm">
            Note: Only Admin users can create programs.
          </div>
        )}

        <div className="space-y-4">
          {/* Client Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Client <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.client_id}
              onChange={(e) => handleChange('client_id', e.target.value)}
              disabled={isEditMode || !isAdmin}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              required
            >
              <option value="">Select a client</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
            {isEditMode && (
              <p className="text-xs text-gray-500 mt-1">Client cannot be changed after creation</p>
            )}
          </div>

          {/* Program Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Program Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              disabled={!isAdmin}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              placeholder="Enter program name"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              disabled={!isAdmin}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              placeholder="Enter program description"
              rows={4}
            />
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              disabled={!isAdmin}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="Planning">Planning</option>
              <option value="Active">Active</option>
              <option value="On Hold">On Hold</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>

          {/* Date Range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => handleChange('start_date', e.target.value)}
                disabled={!isAdmin}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => handleChange('end_date', e.target.value)}
                disabled={!isAdmin}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          {isAdmin && (
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : isEditMode ? 'Update Program' : 'Create Program'}
            </button>
          )}
        </div>
      </form>
    </Modal>
  )
}
