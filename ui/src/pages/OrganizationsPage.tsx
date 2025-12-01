import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface Organization {
  id: string
  name: string
  logo_url?: string
  logo_data?: string
  description?: string
  website?: string
  email?: string
  phone?: string
  address?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export default function OrganizationsPage() {
  const { user } = useAuth()
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null)

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    website: '',
    email: '',
    phone: '',
    address: '',
    is_active: true
  })
  const [logoPreview, setLogoPreview] = useState<string | null>(null)
  const [logoFile, setLogoFile] = useState<File | null>(null)

  useEffect(() => {
    loadOrganizations()
  }, [])

  const loadOrganizations = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getOrganizations()
      setOrganizations(data)
    } catch (err: any) {
      console.error('Failed to load organizations:', err)
      setError(err.response?.data?.detail || 'Failed to load organizations')
    } finally {
      setLoading(false)
    }
  }

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file')
        return
      }
      if (file.size > 2 * 1024 * 1024) {
        setError('Logo file size must be less than 2MB')
        return
      }
      setLogoFile(file)
      setError(null)
      const reader = new FileReader()
      reader.onloadend = () => {
        setLogoPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleOpenModal = (org?: Organization) => {
    if (org) {
      setEditingOrg(org)
      setFormData({
        name: org.name,
        description: org.description || '',
        website: org.website || '',
        email: org.email || '',
        phone: org.phone || '',
        address: org.address || '',
        is_active: org.is_active
      })
      setLogoPreview(org.logo_data || org.logo_url || null)
    } else {
      setEditingOrg(null)
      setFormData({
        name: '',
        description: '',
        website: '',
        email: '',
        phone: '',
        address: '',
        is_active: true
      })
      setLogoPreview(null)
      setLogoFile(null)
    }
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingOrg(null)
    setLogoFile(null)
  }

  const handleSave = async () => {
    try {
      setError(null)
      const updateData: any = { ...formData }

      if (logoFile) {
        const reader = new FileReader()
        reader.onloadend = async () => {
          const base64Logo = reader.result as string
          updateData.logo_data = base64Logo
          updateData.logo_url = null

          try {
            if (editingOrg) {
              await api.updateOrganization(editingOrg.id, updateData)
            } else {
              await api.createOrganization(updateData)
            }
            await loadOrganizations()
            handleCloseModal()
          } catch (err: any) {
            console.error('Failed to save organization:', err)
            setError(err.response?.data?.detail || 'Failed to save organization')
          }
        }
        reader.readAsDataURL(logoFile)
      } else {
        if (!logoPreview && editingOrg?.logo_data) {
          updateData.logo_data = null
          updateData.logo_url = null
        }
        
        if (editingOrg) {
          await api.updateOrganization(editingOrg.id, updateData)
        } else {
          await api.createOrganization(updateData)
        }
        await loadOrganizations()
        handleCloseModal()
      }
    } catch (err: any) {
      console.error('Failed to save organization:', err)
      setError(err.response?.data?.detail || 'Failed to save organization')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this organization?')) return

    try {
      await api.deleteOrganization(id)
      await loadOrganizations()
    } catch (err: any) {
      console.error('Failed to delete organization:', err)
      setError(err.response?.data?.detail || 'Failed to delete organization')
    }
  }

  if (user?.role !== 'Admin') {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-red-600 text-5xl mb-4">🔒</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Access Denied</h2>
          <p className="text-gray-600">Admin role required to manage organizations</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-color)' }}>
          Organizations 🏢
        </h1>
        {organizations.length === 0 && (
          <button
            onClick={() => handleOpenModal()}
            className="px-4 py-2 rounded font-medium"
            style={{
              backgroundColor: 'var(--primary-color)',
              color: 'white'
            }}
          >
            + Add Organization
          </button>
        )}
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <p style={{ color: 'var(--text-secondary)' }}>Loading organizations...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {organizations.map(org => (
            <div
              key={org.id}
              className="rounded-lg p-6 shadow-md"
              style={{
                backgroundColor: 'var(--surface-color)',
                border: '1px solid var(--border-color)'
              }}
            >
              <div className="flex items-start justify-between mb-4">
                {org.logo_data || org.logo_url ? (
                  <img
                    src={org.logo_data || org.logo_url}
                    alt={org.name}
                    className="h-12 object-contain"
                  />
                ) : (
                  <div className="h-12 w-12 rounded-full flex items-center justify-center text-2xl"
                       style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}>
                    {org.name.charAt(0).toUpperCase()}
                  </div>
                )}
                <span
                  className={`px-2 py-1 text-xs rounded ${
                    org.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {org.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-color)' }}>
                {org.name}
              </h3>
              {org.description && (
                <p className="text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
                  {org.description}
                </p>
              )}
              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => handleOpenModal(org)}
                  className="flex-1 px-3 py-1 text-sm rounded"
                  style={{
                    backgroundColor: 'var(--secondary-color)',
                    color: 'var(--text-color)'
                  }}
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(org.id)}
                  className="px-3 py-1 text-sm rounded text-white bg-red-500 hover:bg-red-600"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
             onClick={handleCloseModal}>
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
               style={{ backgroundColor: 'var(--surface-color)' }}
               onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b" style={{ borderColor: 'var(--border-color)' }}>
              <h2 className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
                {editingOrg ? 'Edit Organization' : 'Create Organization'}
              </h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                  Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full p-2 rounded border"
                  style={{
                    backgroundColor: 'var(--background-color)',
                    color: 'var(--text-color)',
                    borderColor: 'var(--border-color)'
                  }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                  Logo
                </label>
                {logoPreview && (
                  <img src={logoPreview} alt="Logo" className="h-20 mb-2 object-contain" />
                )}
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleLogoChange}
                  className="w-full p-2 rounded border"
                  style={{
                    backgroundColor: 'var(--background-color)',
                    color: 'var(--text-color)',
                    borderColor: 'var(--border-color)'
                  }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full p-2 rounded border"
                  style={{
                    backgroundColor: 'var(--background-color)',
                    color: 'var(--text-color)',
                    borderColor: 'var(--border-color)'
                  }}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Website
                  </label>
                  <input
                    type="url"
                    value={formData.website}
                    onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                    className="w-full p-2 rounded border"
                    style={{
                      backgroundColor: 'var(--background-color)',
                      color: 'var(--text-color)',
                      borderColor: 'var(--border-color)'
                    }}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full p-2 rounded border"
                    style={{
                      backgroundColor: 'var(--background-color)',
                      color: 'var(--text-color)',
                      borderColor: 'var(--border-color)'
                    }}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full p-2 rounded border"
                    style={{
                      backgroundColor: 'var(--background-color)',
                      color: 'var(--text-color)',
                      borderColor: 'var(--border-color)'
                    }}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Status
                  </label>
                  <select
                    value={formData.is_active ? 'true' : 'false'}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.value === 'true' })}
                    className="w-full p-2 rounded border"
                    style={{
                      backgroundColor: 'var(--background-color)',
                      color: 'var(--text-color)',
                      borderColor: 'var(--border-color)'
                    }}
                  >
                    <option value="true">Active</option>
                    <option value="false">Inactive</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                  Address
                </label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  rows={2}
                  className="w-full p-2 rounded border"
                  style={{
                    backgroundColor: 'var(--background-color)',
                    color: 'var(--text-color)',
                    borderColor: 'var(--border-color)'
                  }}
                />
              </div>
            </div>
            <div className="p-6 border-t flex justify-end gap-4" style={{ borderColor: 'var(--border-color)' }}>
              <button
                onClick={handleCloseModal}
                className="px-4 py-2 rounded"
                style={{
                  backgroundColor: 'var(--secondary-color)',
                  color: 'var(--text-color)'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={!formData.name}
                className="px-4 py-2 rounded font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: !formData.name ? 'var(--text-secondary)' : 'var(--primary-color)',
                  color: 'white'
                }}
              >
                {editingOrg ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

