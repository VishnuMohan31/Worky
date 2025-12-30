import { useEffect, useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'
import ClientDetailView from '../components/clients/ClientDetailView'
import OwnerSelector from '../components/ownership/OwnerSelector'

interface ClientStatistics {
  total_clients: number
  clients_with_ongoing_projects: number
  clients_with_no_projects: number
  total_projects_across_clients: number
  total_ongoing_projects: number
  clients: ClientDetail[]
}

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

export default function ClientsPage() {
  const { t } = useLanguage()
  const [statistics, setStatistics] = useState<ClientStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingClient, setEditingClient] = useState<ClientDetail | null>(null)
  const [selectedClient, setSelectedClient] = useState<ClientDetail | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [isInteracting, setIsInteracting] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    short_description: '',
    long_description: '',
    email: '',
    phone: '',
    is_active: true
  })
  const [selectedOwners, setSelectedOwners] = useState<string[]>([])

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      const data = await api.getClientStatistics()
      setStatistics(data)
    } catch (error) {
      console.error('Failed to load client statistics:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
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

  const handleCreateClick = () => {
    setEditingClient(null)
    setFormData({
      name: '',
      short_description: '',
      long_description: '',
      email: '',
      phone: '',
      is_active: true
    })
    setShowModal(true)
  }

  const handleClientClick = (client: ClientDetail) => {
    setSelectedClient(client)
  }

  const handleEditClick = (client: ClientDetail, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingClient(client)
    setFormData({
      name: client.name,
      short_description: client.description || '',
      long_description: '',
      email: client.contact_email || '',
      phone: client.contact_phone || '',
      is_active: client.is_active
    })
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    
    try {
      let clientId: string
      
      if (editingClient) {
        // Update existing client
        await api.updateClient(editingClient.id, formData)
        clientId = editingClient.id
      } else {
        // Create new client
        const newClient = await api.createClient(formData)
        clientId = newClient.id
      }
      
      // Handle owner assignments for new clients or when owners are selected
      if (selectedOwners.length > 0) {
        try {
          // Create owner assignments
          for (const ownerId of selectedOwners) {
            await api.createAssignment({
              entity_type: 'client',
              entity_id: clientId,
              user_id: ownerId,
              assignment_type: 'owner'
            })
          }
          console.log(`Successfully assigned ${selectedOwners.length} owners to client ${clientId}`)
        } catch (ownerError) {
          console.error('Failed to assign owners:', ownerError)
          // Don't fail the entire operation, just show a warning
          alert('Client created successfully, but failed to assign some owners. You can assign them later from the client details page.')
        }
      }
      
      setShowModal(false)
      setEditingClient(null)
      setFormData({
        name: '',
        short_description: '',
        long_description: '',
        email: '',
        phone: '',
        is_active: true
      })
      setSelectedOwners([])
      
      // Reload statistics to show the updated/new client
      await loadStatistics()
    } catch (error) {
      console.error(`Failed to ${editingClient ? 'update' : 'create'} client:`, error)
      alert(`Failed to ${editingClient ? 'update' : 'create'} client. Please try again.`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingClient(null)
    setFormData({
      name: '',
      short_description: '',
      long_description: '',
      email: '',
      phone: '',
      is_active: true
    })
    setSelectedOwners([])
  }

  if (loading) {
    return <div style={{ color: 'var(--text-color)' }}>{t('loading')}</div>
  }

  if (!statistics) {
    return <div style={{ color: 'var(--text-color)' }}>Failed to load data</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-color)' }}>
          {t('clients')}
        </h1>
        <button 
          className="px-4 py-2 rounded-md hover:opacity-90 transition-opacity"
          style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}
          onClick={handleCreateClick}
        >
          + Create Client
        </button>
      </div>

      {/* Dashboard Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div 
          className="rounded-lg p-6 shadow-md"
          style={{ 
            backgroundColor: 'var(--surface-color)',
            border: '1px solid var(--border-color)'
          }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Total Clients
              </p>
              <p className="text-3xl font-bold mt-2" style={{ color: 'var(--text-color)' }}>
                {statistics.total_clients}
              </p>
            </div>
            <div 
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ backgroundColor: 'var(--primary-color)', opacity: 0.1 }}
            >
              <span style={{ color: 'var(--primary-color)', fontSize: '24px' }}>👥</span>
            </div>
          </div>
        </div>

        <div 
          className="rounded-lg p-6 shadow-md"
          style={{ 
            backgroundColor: 'var(--surface-color)',
            border: '1px solid var(--border-color)'
          }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                With Ongoing Projects
              </p>
              <p className="text-3xl font-bold mt-2" style={{ color: 'var(--text-color)' }}>
                {statistics.clients_with_ongoing_projects}
              </p>
            </div>
            <div 
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#10b981', opacity: 0.1 }}
            >
              <span style={{ color: '#10b981', fontSize: '24px' }}>🚀</span>
            </div>
          </div>
        </div>

        <div 
          className="rounded-lg p-6 shadow-md"
          style={{ 
            backgroundColor: 'var(--surface-color)',
            border: '1px solid var(--border-color)'
          }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Total Projects
              </p>
              <p className="text-3xl font-bold mt-2" style={{ color: 'var(--text-color)' }}>
                {statistics.total_projects_across_clients}
              </p>
            </div>
            <div 
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#8b5cf6', opacity: 0.1 }}
            >
              <span style={{ color: '#8b5cf6', fontSize: '24px' }}>📊</span>
            </div>
          </div>
        </div>

        <div 
          className="rounded-lg p-6 shadow-md"
          style={{ 
            backgroundColor: 'var(--surface-color)',
            border: '1px solid var(--border-color)'
          }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Ongoing Projects
              </p>
              <p className="text-3xl font-bold mt-2" style={{ color: 'var(--text-color)' }}>
                {statistics.total_ongoing_projects}
              </p>
            </div>
            <div 
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#f59e0b', opacity: 0.1 }}
            >
              <span style={{ color: '#f59e0b', fontSize: '24px' }}>⚡</span>
            </div>
          </div>
        </div>
      </div>

      {/* Create/Edit Client Modal */}
      {showModal && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={(e) => {
            // Only close if clicking on the backdrop itself, not on any child elements
            // AND not currently interacting with form fields
            if (e.target === e.currentTarget && !isInteracting) {
              handleCloseModal()
            }
          }}
        >
          <div 
            className="rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
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
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
                {editingClient ? 'Edit Client' : 'Create New Client'}
              </h2>
              <button 
                onClick={handleCloseModal}
                className="text-2xl hover:opacity-70"
                style={{ color: 'var(--text-secondary)' }}
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                {/* Client Name */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Client Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    onClick={(e) => e.stopPropagation()}
                    onFocus={(e) => e.stopPropagation()}
                    onMouseDown={(e) => e.stopPropagation()}
                    onMouseUp={(e) => e.stopPropagation()}
                    onSelect={(e) => e.stopPropagation()}
                    required
                    className="w-full px-4 py-2 rounded-md border"
                    style={{ 
                      backgroundColor: 'var(--background-color)',
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-color)'
                    }}
                    placeholder="Enter client name"
                  />
                </div>

                {/* Short Description */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Short Description
                  </label>
                  <input
                    type="text"
                    name="short_description"
                    value={formData.short_description}
                    onChange={handleInputChange}
                    onClick={(e) => e.stopPropagation()}
                    onFocus={(e) => e.stopPropagation()}
                    onMouseDown={(e) => e.stopPropagation()}
                    onMouseUp={(e) => e.stopPropagation()}
                    onSelect={(e) => e.stopPropagation()}
                    className="w-full px-4 py-2 rounded-md border"
                    style={{ 
                      backgroundColor: 'var(--background-color)',
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-color)'
                    }}
                    placeholder="Brief description (max 500 characters)"
                    maxLength={500}
                  />
                </div>

                {/* Long Description */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Long Description
                  </label>
                  <textarea
                    name="long_description"
                    value={formData.long_description}
                    onChange={handleInputChange}
                    onClick={(e) => e.stopPropagation()}
                    onFocus={(e) => e.stopPropagation()}
                    onMouseDown={(e) => e.stopPropagation()}
                    onMouseUp={(e) => e.stopPropagation()}
                    onSelect={(e) => e.stopPropagation()}
                    rows={4}
                    className="w-full px-4 py-2 rounded-md border"
                    style={{ 
                      backgroundColor: 'var(--background-color)',
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-color)'
                    }}
                    placeholder="Detailed description of the client"
                  />
                </div>

                {/* Contact Email */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Contact Email
                  </label>
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
                      backgroundColor: 'var(--background-color)',
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-color)'
                    }}
                    placeholder="contact@client.com"
                  />
                </div>

                {/* Contact Phone */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Contact Phone
                  </label>
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
                      backgroundColor: 'var(--background-color)',
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-color)'
                    }}
                    placeholder="+1-555-0123"
                  />
                </div>

                {/* Active Status */}
                <div className="flex items-center">
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

                {/* Owner Assignment - NEW */}
                {!editingClient && (
                  <div className="pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
                    <OwnerSelector
                      entityType="client"
                      selectedOwners={selectedOwners}
                      onOwnersChange={setSelectedOwners}
                      disabled={submitting}
                    />
                  </div>
                )}
              </div>

              {/* Form Actions */}
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={handleCloseModal}
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
                  type="submit"
                  className="px-4 py-2 rounded-md hover:opacity-90"
                  style={{ 
                    backgroundColor: 'var(--primary-color)',
                    color: 'white'
                  }}
                  disabled={submitting}
                >
                  {submitting 
                    ? (editingClient ? 'Updating...' : 'Creating...') 
                    : (editingClient ? 'Update Client' : 'Create Client')
                  }
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Client Detail View Modal */}
      {selectedClient && (
        <ClientDetailView
          client={selectedClient}
          onClose={() => setSelectedClient(null)}
          onUpdate={() => {
            loadStatistics()
            setSelectedClient(null)
          }}
        />
      )}

      {/* Client Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statistics.clients.map(client => (
          <div 
            key={client.id}
            onClick={() => handleClientClick(client)}
            className="rounded-lg p-6 shadow-md hover:shadow-lg transition-all cursor-pointer"
            style={{ 
              backgroundColor: 'var(--surface-color)',
              border: '1px solid var(--border-color)'
            }}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-1" style={{ color: 'var(--text-color)' }}>
                  {client.name}
                </h3>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  {client.industry}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => handleEditClick(client, e)}
                  className="p-1.5 rounded-md hover:opacity-80 transition-opacity"
                  style={{ 
                    backgroundColor: 'var(--primary-color)',
                    color: 'white'
                  }}
                  title="Edit client"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                </button>
                <span 
                  className={`px-2 py-1 text-xs rounded ${
                    client.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {client.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            {/* Description */}
            <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
              {client.description}
            </p>

            {/* Contact Info */}
            <div className="mb-4 space-y-1">
              <div className="flex items-center text-xs" style={{ color: 'var(--text-secondary)' }}>
                <span className="mr-2">📧</span>
                <span>{client.contact_email}</span>
              </div>
              <div className="flex items-center text-xs" style={{ color: 'var(--text-secondary)' }}>
                <span className="mr-2">📞</span>
                <span>{client.contact_phone}</span>
              </div>
            </div>

            {/* Project Stats */}
            <div 
              className="grid grid-cols-3 gap-2 p-3 rounded-md mb-4"
              style={{ backgroundColor: 'var(--background-color)' }}
            >
              <div className="text-center">
                <p className="text-lg font-bold" style={{ color: 'var(--text-color)' }}>
                  {client.total_projects}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  Total
                </p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold" style={{ color: '#10b981' }}>
                  {client.ongoing_projects}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  Ongoing
                </p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold" style={{ color: '#6b7280' }}>
                  {client.completed_projects}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  Done
                </p>
              </div>
            </div>

            {/* Latest Project */}
            {client.latest_project && (
              <div 
                className="p-3 rounded-md"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
                  Latest Project
                </p>
                <p className="text-sm font-medium" style={{ color: 'var(--text-color)' }}>
                  {client.latest_project.name}
                </p>
                <span 
                  className={`inline-block mt-1 px-2 py-0.5 text-xs rounded ${
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
            )}

            {!client.latest_project && (
              <div 
                className="p-3 rounded-md text-center"
                style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  No projects yet
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
