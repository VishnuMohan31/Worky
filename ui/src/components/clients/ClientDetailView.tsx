import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'
import EntityNotes from '../hierarchy/EntityNotes'
import OwnershipDisplay from '../ownership/OwnershipDisplay'

interface ClientDetail {
  id: string
  name: string
  description: string
  industry: string
  contact_email: string
  contact_phone: string
  is_active: boolean
  total_projects: number
  ongoing_projects: number
  completed_projects: number
  latest_project: {
    id: string
    name: string
    status: string
    created_at: string
  } | null
  created_at: string
  updated_at: string
}

interface ClientDetailViewProps {
  client: ClientDetail
  onClose: () => void
  onUpdate: () => void
}

const ClientDetailView: React.FC<ClientDetailViewProps> = ({ client, onClose, onUpdate }) => {
  const navigate = useNavigate()
  const [isEditing, setIsEditing] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [isInteracting, setIsInteracting] = useState(false)
  const [formData, setFormData] = useState({
    name: client.name,
    short_description: client.description,
    long_description: '',
    email: client.contact_email,
    phone: client.contact_phone,
    is_active: client.is_active
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }))
  }

  // Helper function to handle all input events and prevent modal closing
  const handleInputEvent = (e: React.SyntheticEvent) => {
    e.stopPropagation()
    // Don't preventDefault() - we want normal input behavior to work
  }

  // Helper function to handle focus events
  const handleInputFocus = (e: React.FocusEvent) => {
    e.stopPropagation()
    setIsInteracting(true)
  }

  // Helper function to handle blur events
  const handleInputBlur = (e: React.FocusEvent) => {
    e.stopPropagation()
    // Delay clearing interaction state to prevent race conditions
    setTimeout(() => setIsInteracting(false), 100)
  }

  const handleSave = async () => {
    setSubmitting(true)
    try {
      await api.updateClient(client.id, formData)
      setIsEditing(false)
      onUpdate()
    } catch (error) {
      console.error('Failed to update client:', error)
      alert('Failed to update client. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      name: client.name,
      short_description: client.description,
      long_description: '',
      email: client.contact_email,
      phone: client.contact_phone,
      is_active: client.is_active
    })
    setIsEditing(false)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={(e) => {
        // Only close if clicking on the backdrop itself, not on any child elements
        // AND not currently interacting with form fields
        if (e.target === e.currentTarget && !isInteracting) {
          onClose()
        }
      }}
    >
      <div 
        className="rounded-lg w-full max-w-5xl max-h-[90vh] flex flex-col"
        style={{ 
          backgroundColor: 'var(--surface-color)',
          border: '1px solid var(--border-color)'
        }}
        onClick={(e) => {
          // Prevent any clicks inside the modal from bubbling up
          e.stopPropagation()
          // Don't preventDefault() - we want normal click behavior inside modal
        }}
        onMouseDown={(e) => {
          // Prevent mouse events during text selection from bubbling up
          e.stopPropagation()
        }}
        onMouseUp={(e) => {
          // Prevent mouse events during text selection from bubbling up
          e.stopPropagation()
        }}
      >
        {/* Header */}
        <div 
          className="flex items-center justify-between p-6 border-b"
          style={{ borderColor: 'var(--border-color)' }}
        >
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
              {isEditing ? 'Edit Client' : 'Client Details'}
            </h2>
            <span 
              className={`px-3 py-1 text-sm rounded ${
                client.is_active 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {client.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 rounded-md hover:opacity-90 transition-opacity"
                style={{ 
                  backgroundColor: 'var(--primary-color)',
                  color: 'white'
                }}
              >
                Edit
              </button>
            ) : (
              <>
                <button
                  onClick={handleCancel}
                  className="px-4 py-2 rounded-md border hover:opacity-80"
                  style={{ 
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="px-4 py-2 rounded-md hover:opacity-90"
                  style={{ 
                    backgroundColor: 'var(--primary-color)',
                    color: 'white'
                  }}
                  disabled={submitting}
                >
                  {submitting ? 'Saving...' : 'Save Changes'}
                </button>
              </>
            )}
            <button 
              onClick={onClose}
              className="text-2xl hover:opacity-70 ml-2"
              style={{ color: 'var(--text-secondary)' }}
            >
              ×
            </button>
          </div>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Client Information */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* Ownership Section - TOP PRIORITY */}
              <div 
                className="rounded-lg p-6 border-l-4"
                style={{ 
                  backgroundColor: 'var(--card-background)',
                  border: '1px solid var(--border-color)',
                  borderLeftColor: '#3b82f6',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
                }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-100">
                    <span className="text-blue-600 text-lg font-semibold">👥</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-blue-700">Client Ownership</h3>
                    <p className="text-sm text-gray-600">Manage who owns and is responsible for this client</p>
                  </div>
                </div>
                
                <OwnershipDisplay 
                  entityType="client"
                  entityId={client.id}
                  onOwnershipChange={() => {
                    console.log('Ownership changed for client', client.id)
                    // Optionally refresh client data
                  }}
                />
              </div>

              {/* Basic Information */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                  Basic Information
                </h3>
                
                <div className="space-y-4">
                  {/* Client Name */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Client Name
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        onClick={(e) => e.stopPropagation()}
                        onFocus={(e) => e.stopPropagation()}
                        onBlur={(e) => e.stopPropagation()}
                        onMouseDown={(e) => e.stopPropagation()}
                        onMouseUp={(e) => e.stopPropagation()}
                        onMouseLeave={(e) => e.stopPropagation()}
                        onMouseEnter={(e) => e.stopPropagation()}
                        onSelect={(e) => e.stopPropagation()}
                        onKeyDown={(e) => e.stopPropagation()}
                        onKeyUp={(e) => e.stopPropagation()}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                      />
                    ) : (
                      <p className="text-base" style={{ color: 'var(--text-color)' }}>
                        {client.name}
                      </p>
                    )}
                  </div>

                  {/* Short Description */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Short Description
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        name="short_description"
                        value={formData.short_description}
                        onChange={handleInputChange}
                        onClick={(e) => e.stopPropagation()}
                        onFocus={(e) => e.stopPropagation()}
                        onBlur={(e) => e.stopPropagation()}
                        onMouseDown={(e) => e.stopPropagation()}
                        onMouseUp={(e) => e.stopPropagation()}
                        onMouseLeave={(e) => e.stopPropagation()}
                        onMouseEnter={(e) => e.stopPropagation()}
                        onSelect={(e) => e.stopPropagation()}
                        onKeyDown={(e) => e.stopPropagation()}
                        onKeyUp={(e) => e.stopPropagation()}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                        placeholder="Brief description (max 500 characters)"
                        maxLength={500}
                      />
                    ) : (
                      <p className="text-base" style={{ color: 'var(--text-color)' }}>
                        {client.description || 'No description provided'}
                      </p>
                    )}
                  </div>

                  {/* Long Description */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Long Description
                    </label>
                    {isEditing ? (
                      <textarea
                        name="long_description"
                        value={formData.long_description}
                        onChange={handleInputChange}
                        onClick={(e) => e.stopPropagation()}
                        onFocus={(e) => e.stopPropagation()}
                        onBlur={(e) => e.stopPropagation()}
                        onMouseDown={(e) => e.stopPropagation()}
                        onMouseUp={(e) => e.stopPropagation()}
                        onMouseLeave={(e) => e.stopPropagation()}
                        onMouseEnter={(e) => e.stopPropagation()}
                        onSelect={(e) => e.stopPropagation()}
                        onKeyDown={(e) => e.stopPropagation()}
                        onKeyUp={(e) => e.stopPropagation()}
                        rows={4}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                        placeholder="Detailed description of the client"
                      />
                    ) : (
                      <p className="text-base" style={{ color: 'var(--text-color)' }}>
                        {formData.long_description || 'No detailed description provided'}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                  Contact Information
                </h3>
                
                <div className="space-y-4">
                  {/* Email */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Email
                    </label>
                    {isEditing ? (
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        onClick={handleInputEvent}
                        onFocus={handleInputFocus}
                        onBlur={handleInputBlur}
                        onMouseDown={handleInputEvent}
                        onMouseUp={handleInputEvent}
                        onMouseLeave={handleInputEvent}
                        onMouseEnter={handleInputEvent}
                        onSelect={handleInputEvent}
                        onKeyDown={handleInputEvent}
                        onKeyUp={handleInputEvent}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                        placeholder="contact@client.com"
                      />
                    ) : (
                      <p className="text-base flex items-center" style={{ color: 'var(--text-color)' }}>
                        <span className="mr-2">📧</span>
                        {client.contact_email || 'No email provided'}
                      </p>
                    )}
                  </div>

                  {/* Phone */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Phone
                    </label>
                    {isEditing ? (
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        onClick={handleInputEvent}
                        onFocus={handleInputFocus}
                        onBlur={handleInputBlur}
                        onMouseDown={handleInputEvent}
                        onMouseUp={handleInputEvent}
                        onMouseLeave={handleInputEvent}
                        onMouseEnter={handleInputEvent}
                        onSelect={handleInputEvent}
                        onKeyDown={handleInputEvent}
                        onKeyUp={handleInputEvent}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                        placeholder="+1-555-0123"
                      />
                    ) : (
                      <p className="text-base flex items-center" style={{ color: 'var(--text-color)' }}>
                        <span className="mr-2">📞</span>
                        {client.contact_phone || 'No phone provided'}
                      </p>
                    )}
                  </div>

                  {/* Active Status (only in edit mode) */}
                  {isEditing && (
                    <div className="flex items-center pt-2">
                      <input
                        type="checkbox"
                        name="is_active"
                        checked={formData.is_active}
                        onChange={handleInputChange}
                        className="w-4 h-4 rounded"
                        style={{ accentColor: 'var(--primary-color)' }}
                      />
                      <label className="ml-2 text-sm" style={{ color: 'var(--text-color)' }}>
                        Active Client
                      </label>
                    </div>
                  )}
                </div>
              </div>

              {/* Notes Section - Scrollable */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)',
                  borderLeft: '4px solid var(--primary-color)'
                }}
              >
                <EntityNotes entityType="client" entityId={client.id} />
              </div>
            </div>

            {/* Right Column - Statistics & Metadata */}
            <div className="space-y-6">
              {/* Project Statistics */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                  Project Statistics
                </h3>
                
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      Total Projects
                    </span>
                    <span className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
                      {client.total_projects}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      Ongoing
                    </span>
                    <span className="text-2xl font-bold" style={{ color: '#10b981' }}>
                      {client.ongoing_projects}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      Completed
                    </span>
                    <span className="text-2xl font-bold" style={{ color: '#6b7280' }}>
                      {client.completed_projects}
                    </span>
                  </div>
                </div>

                {/* Show All Programs Button */}
                <button
                  onClick={() => {
                    navigate('/programs', { state: { selectedClientId: client.id, selectedClientName: client.name } })
                    onClose()
                  }}
                  className="w-full mt-4 px-4 py-2 rounded-md hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                  style={{ 
                    backgroundColor: 'var(--primary-color)',
                    color: 'white'
                  }}
                >
                  <span>📊</span>
                  <span>Show All Programs</span>
                </button>
              </div>

              {/* Latest Project */}
              {client.latest_project && (
                <div 
                  className="rounded-lg p-6"
                  style={{ 
                    backgroundColor: 'var(--background-color)',
                    border: '1px solid var(--border-color)'
                  }}
                >
                  <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                    Latest Project
                  </h3>
                  
                  <div>
                    <p className="text-base font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                      {client.latest_project.name}
                    </p>
                    <span 
                      className={`inline-block px-2 py-1 text-xs rounded ${
                        client.latest_project.status === 'In Progress' 
                          ? 'bg-blue-100 text-blue-800'
                          : client.latest_project.status === 'Completed'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {client.latest_project.status}
                    </span>
                  </div>
                </div>
              )}

              {/* Metadata */}
              <div 
                className="rounded-lg p-6"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                  Metadata
                </h3>
                
                <div className="space-y-3">
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Created
                    </p>
                    <p className="text-sm" style={{ color: 'var(--text-color)' }}>
                      {formatDate(client.created_at)}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Last Updated
                    </p>
                    <p className="text-sm" style={{ color: 'var(--text-color)' }}>
                      {formatDate(client.updated_at)}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
                      Client ID
                    </p>
                    <p className="text-xs font-mono" style={{ color: 'var(--text-color)' }}>
                      {client.id}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  )
}

export default ClientDetailView
