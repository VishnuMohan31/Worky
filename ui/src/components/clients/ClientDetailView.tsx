import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import EntityNotes from '../hierarchy/EntityNotes'

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
  const [isEditing, setIsEditing] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    name: client.name,
    description: client.description,
    industry: client.industry,
    contact_email: client.contact_email,
    contact_phone: client.contact_phone,
    is_active: client.is_active
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }))
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
      description: client.description,
      industry: client.industry,
      contact_email: client.contact_email,
      contact_phone: client.contact_phone,
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
      onClick={onClose}
    >
      <div 
        className="rounded-lg w-full max-w-5xl max-h-[90vh] flex flex-col"
        style={{ 
          backgroundColor: 'var(--surface-color)',
          border: '1px solid var(--border-color)'
        }}
        onClick={(e) => e.stopPropagation()}
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

                  {/* Industry */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Industry
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        name="industry"
                        value={formData.industry}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                      />
                    ) : (
                      <p className="text-base" style={{ color: 'var(--text-color)' }}>
                        {client.industry}
                      </p>
                    )}
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                      Description
                    </label>
                    {isEditing ? (
                      <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleInputChange}
                        rows={4}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                      />
                    ) : (
                      <p className="text-base" style={{ color: 'var(--text-color)' }}>
                        {client.description || 'No description provided'}
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
                        name="contact_email"
                        value={formData.contact_email}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                      />
                    ) : (
                      <p className="text-base flex items-center" style={{ color: 'var(--text-color)' }}>
                        <span className="mr-2">📧</span>
                        {client.contact_email}
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
                        name="contact_phone"
                        value={formData.contact_phone}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 rounded-md border"
                        style={{ 
                          backgroundColor: 'var(--surface-color)',
                          borderColor: 'var(--border-color)',
                          color: 'var(--text-color)'
                        }}
                      />
                    ) : (
                      <p className="text-base flex items-center" style={{ color: 'var(--text-color)' }}>
                        <span className="mr-2">📞</span>
                        {client.contact_phone}
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
