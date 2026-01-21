/**
 * Program Modal Component
 * Create and edit programs (Admin only)
 */
import { useState, useEffect } from 'react'
import Modal from '../common/Modal'
import DateInput from '../common/DateInput'
import api from '../../services/api'
import OwnerSelector from '../ownership/OwnerSelector'
import { formatDateForAPI } from '../../utils/dateUtils'

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
    short_description: '',
    long_description: '',
    client_id: selectedClientId || '',
    status: 'Planning',
    start_date: '',
    end_date: ''
  })
  const [selectedOwners, setSelectedOwners] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isEditMode = !!program

  useEffect(() => {
    if (program) {
      setFormData({
        name: program.name || '',
        short_description: program.short_description || '',
        long_description: program.long_description || '',
        client_id: program.client_id || '',
        status: program.status || 'Planning',
        start_date: program.start_date || '', // Keep in YYYY-MM-DD format for DateInput
        end_date: program.end_date || '' // Keep in YYYY-MM-DD format for DateInput
      })
    } else {
      setFormData({
        name: '',
        short_description: '',
        long_description: '',
        client_id: selectedClientId || '',
        status: 'Planning',
        start_date: '',
        end_date: ''
      })
    }
    setSelectedOwners([])
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

    // Date validation - handle both YYYY-MM-DD and DD/MM/YYYY formats
    if (formData.start_date && formData.end_date) {
      let startDate: Date
      let endDate: Date
      
      try {
        // Handle both formats
        if (formData.start_date.includes('/')) {
          // DD/MM/YYYY format
          const apiStartDate = formatDateForAPI(formData.start_date)
          startDate = new Date(apiStartDate + 'T00:00:00')
        } else {
          // YYYY-MM-DD format
          startDate = new Date(formData.start_date + 'T00:00:00')
        }
        
        if (formData.end_date.includes('/')) {
          // DD/MM/YYYY format
          const apiEndDate = formatDateForAPI(formData.end_date)
          endDate = new Date(apiEndDate + 'T00:00:00')
        } else {
          // YYYY-MM-DD format
          endDate = new Date(formData.end_date + 'T00:00:00')
        }
        
        if (!isNaN(startDate.getTime()) && !isNaN(endDate.getTime()) && endDate < startDate) {
          setError('End date cannot be before start date')
          return
        }
      } catch (error) {
        console.error('Date validation error:', error)
      }
    }

    setLoading(true)
    setError('')

    try {
      let programId: string
      
      if (isEditMode) {
        await api.updateEntity('program', program.id, formData)
        programId = program.id
      } else {
        const newProgram = await api.createEntity('program', formData)
        programId = newProgram.id
      }
      
      // Handle owner assignments for new programs only (edit mode handles assignments directly)
      if (selectedOwners.length > 0 && !isEditMode) {
        try {
          // Create owner assignments
          for (const ownerId of selectedOwners) {
            await api.createAssignment({
              entity_type: 'program',
              entity_id: programId,
              user_id: ownerId,
              assignment_type: 'owner'
            })
          }
          console.log(`Successfully assigned ${selectedOwners.length} owners to program ${programId}`)
        } catch (ownerError) {
          console.error('Failed to assign owners:', ownerError)
          // Don't fail the entire operation, just show a warning
          setError('Program created successfully, but failed to assign some owners. You can assign them later from the program details.')
          return // Don't close modal immediately so user can see the message
        }
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
    
    // Clear error when user starts typing
    if (error) {
      setError('')
    }
  }

  // Helper function to check if dates are valid
  const isDateRangeValid = () => {
    if (!formData.start_date || !formData.end_date) return true
    
    try {
      let startDate: Date
      let endDate: Date
      
      // Handle both formats
      if (formData.start_date.includes('/')) {
        const apiStartDate = formatDateForAPI(formData.start_date)
        startDate = new Date(apiStartDate + 'T00:00:00')
      } else {
        startDate = new Date(formData.start_date + 'T00:00:00')
      }
      
      if (formData.end_date.includes('/')) {
        const apiEndDate = formatDateForAPI(formData.end_date)
        endDate = new Date(apiEndDate + 'T00:00:00')
      } else {
        endDate = new Date(formData.end_date + 'T00:00:00')
      }
      
      if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return true
      
      return endDate >= startDate
    } catch (error) {
      return true
    }
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
          {/* Owner Assignment - MOVED TO TOP */}
          {isAdmin && (
            <div className="mb-6 pb-4 border-b border-gray-200">
              <OwnerSelector
                entityType="program"
                selectedOwners={selectedOwners}
                onOwnersChange={setSelectedOwners}
                disabled={loading}
                existingEntityId={isEditMode ? program.id : undefined}
              />
            </div>
          )}

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

          {/* Short Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Short Description
            </label>
            <input
              type="text"
              value={formData.short_description}
              onChange={(e) => handleChange('short_description', e.target.value)}
              disabled={!isAdmin}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              placeholder="Brief description (max 500 characters)"
              maxLength={500}
            />
          </div>

          {/* Long Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Long Description
            </label>
            <textarea
              value={formData.long_description}
              onChange={(e) => handleChange('long_description', e.target.value)}
              disabled={!isAdmin}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              placeholder="Detailed program description"
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
              <DateInput
                value={formData.start_date}
                onChange={(value) => handleChange('start_date', value)}
                disabled={!isAdmin}
                className="w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                placeholder="DD/MM/YYYY"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <DateInput
                value={formData.end_date}
                onChange={(value) => handleChange('end_date', value)}
                disabled={!isAdmin}
                min={formData.start_date || undefined}
                className="w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                placeholder="DD/MM/YYYY"
              />
              {formData.start_date && formData.end_date && !isDateRangeValid() && (
                <p className="text-red-500 text-xs mt-1">End date cannot be before start date</p>
              )}
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
