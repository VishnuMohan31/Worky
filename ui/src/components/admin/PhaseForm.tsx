/**
 * PhaseForm Component
 * Form for creating and editing phases
 * - Add name and description inputs
 * - Add color picker for phase color
 * - Add active/inactive toggle
 * - Validate unique phase name
 */
import { useState, FormEvent } from 'react'

interface Phase {
  id: string
  name: string
  description: string
  color: string
  isActive: boolean
  displayOrder: number
}

interface PhaseFormProps {
  phase: Phase
  onSave: (phaseData: Omit<Phase, 'id' | 'usageCount'>) => Promise<void>
  onCancel: () => void
  existingPhaseNames: string[]
}

export default function PhaseForm({
  phase,
  onSave,
  onCancel,
  existingPhaseNames
}: PhaseFormProps) {
  const [formData, setFormData] = useState({
    name: phase.name,
    description: phase.description,
    color: phase.color,
    isActive: phase.isActive,
    displayOrder: phase.displayOrder
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [saving, setSaving] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Validate name
    if (!formData.name.trim()) {
      newErrors.name = 'Phase name is required'
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Phase name must be at least 2 characters'
    } else if (formData.name.trim().length > 100) {
      newErrors.name = 'Phase name must not exceed 100 characters'
    } else if (existingPhaseNames.some(name => name.toLowerCase() === formData.name.trim().toLowerCase())) {
      newErrors.name = 'A phase with this name already exists'
    }

    // Validate color
    if (!formData.color) {
      newErrors.color = 'Phase color is required'
    } else if (!/^#[0-9A-Fa-f]{6}$/.test(formData.color)) {
      newErrors.color = 'Invalid color format (must be hex color like #4A90E2)'
    }

    // Validate display order
    if (formData.displayOrder < 0) {
      newErrors.displayOrder = 'Display order must be a positive number'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      setSaving(true)
      await onSave({
        name: formData.name.trim(),
        description: formData.description.trim(),
        color: formData.color,
        isActive: formData.isActive,
        displayOrder: formData.displayOrder
      })
    } catch (err: any) {
      setErrors({ submit: err.message || 'Failed to save phase' })
    } finally {
      setSaving(false)
    }
  }

  const handleChange = (field: keyof typeof formData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  // Predefined color palette
  const colorPalette = [
    '#3498db', // Blue
    '#9b59b6', // Purple
    '#e67e22', // Orange
    '#1abc9c', // Teal
    '#e74c3c', // Red
    '#f39c12', // Yellow
    '#2ecc71', // Green
    '#34495e', // Dark Gray
    '#16a085', // Dark Teal
    '#c0392b', // Dark Red
    '#8e44ad', // Dark Purple
    '#2980b9'  // Dark Blue
  ]

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name Field */}
      <div>
        <label htmlFor="phase-name" className="block text-sm font-medium text-gray-700 mb-1">
          Phase Name <span className="text-red-500">*</span>
        </label>
        <input
          id="phase-name"
          type="text"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.name ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="e.g., Development, Testing, Design"
          maxLength={100}
          autoFocus
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          {formData.name.length}/100 characters
        </p>
      </div>

      {/* Description Field */}
      <div>
        <label htmlFor="phase-description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="phase-description"
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Describe the purpose of this phase..."
          rows={3}
          maxLength={500}
        />
        <p className="mt-1 text-xs text-gray-500">
          {formData.description.length}/500 characters
        </p>
      </div>

      {/* Color Picker */}
      <div>
        <label htmlFor="phase-color" className="block text-sm font-medium text-gray-700 mb-2">
          Phase Color <span className="text-red-500">*</span>
        </label>
        
        {/* Color Palette */}
        <div className="grid grid-cols-6 gap-2 mb-3">
          {colorPalette.map((color) => (
            <button
              key={color}
              type="button"
              onClick={() => handleChange('color', color)}
              className={`w-full h-10 rounded-lg border-2 transition-all ${
                formData.color === color
                  ? 'border-blue-600 ring-2 ring-blue-200'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              style={{ backgroundColor: color }}
              title={color}
            />
          ))}
        </div>

        {/* Custom Color Input */}
        <div className="flex items-center gap-3">
          <input
            id="phase-color"
            type="color"
            value={formData.color}
            onChange={(e) => handleChange('color', e.target.value)}
            className="w-16 h-10 rounded border border-gray-300 cursor-pointer"
          />
          <input
            type="text"
            value={formData.color}
            onChange={(e) => handleChange('color', e.target.value)}
            className={`flex-1 px-3 py-2 border rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.color ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="#4A90E2"
            pattern="^#[0-9A-Fa-f]{6}$"
          />
        </div>
        {errors.color && (
          <p className="mt-1 text-sm text-red-600">{errors.color}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          Choose from the palette or enter a custom hex color
        </p>
      </div>

      {/* Display Order */}
      <div>
        <label htmlFor="phase-order" className="block text-sm font-medium text-gray-700 mb-1">
          Display Order
        </label>
        <input
          id="phase-order"
          type="number"
          value={formData.displayOrder}
          onChange={(e) => handleChange('displayOrder', parseInt(e.target.value) || 0)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.displayOrder ? 'border-red-500' : 'border-gray-300'
          }`}
          min={0}
        />
        {errors.displayOrder && (
          <p className="mt-1 text-sm text-red-600">{errors.displayOrder}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          Lower numbers appear first in lists
        </p>
      </div>

      {/* Active/Inactive Toggle */}
      <div>
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={formData.isActive}
            onChange={(e) => handleChange('isActive', e.target.checked)}
            className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <div>
            <span className="text-sm font-medium text-gray-700">Active Phase</span>
            <p className="text-xs text-gray-500">
              Inactive phases cannot be assigned to new tasks or subtasks
            </p>
          </div>
        </label>
      </div>

      {/* Submit Error */}
      {errors.submit && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{errors.submit}</p>
        </div>
      )}

      {/* Form Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          disabled={saving}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          disabled={saving}
        >
          {saving && (
            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          )}
          {saving ? 'Saving...' : phase.id ? 'Update Phase' : 'Create Phase'}
        </button>
      </div>
    </form>
  )
}
