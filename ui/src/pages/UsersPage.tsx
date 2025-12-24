import { useEffect, useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

export default function UsersPage() {
  const { t } = useLanguage()
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState<any>(null)
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    role: 'Developer',
    isActive: true
  })

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const data = await api.getUsers()
      setUsers(data || [])
    } catch (error) {
      console.error('Failed to load users:', error)
      setUsers([])
    } finally {
      setLoading(false)
    }
  }

  const handleAddUser = () => {
    setFormData({
      fullName: '',
      email: '',
      role: 'Developer',
      isActive: true
    })
    setShowAddModal(true)
  }

  const handleEditUser = (user: any) => {
    setSelectedUser(user)
    setFormData({
      fullName: user.fullName || user.full_name || '',
      email: user.email || '',
      role: user.role || 'Developer',
      isActive: user.isActive !== undefined ? user.isActive : (user.is_active !== undefined ? user.is_active : true)
    })
    setShowEditModal(true)
  }

  const handleCreateUser = async () => {
    if (!formData.fullName.trim()) {
      alert('Please enter a full name')
      return
    }
    if (!formData.email.trim()) {
      alert('Please enter an email address')
      return
    }
    if (!formData.role) {
      alert('Please select a role')
      return
    }

    try {
      // Get first available client for new user
      const clients = await api.getClients()
      const clientId = clients?.clients?.[0]?.id || clients?.[0]?.id || 'CLI-001'
      
      await api.createUser({
        full_name: formData.fullName.trim(),
        email: formData.email.trim(),
        role: formData.role,
        password: 'password123', // Default password
        client_id: clientId,
        language: 'en',
        theme: 'snow'
      })
      
      await loadUsers()
      handleCloseModals()
      alert('User created successfully! Default password: password123')
    } catch (error: any) {
      console.error('Failed to create user:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create user. Please try again.'
      alert(errorMessage)
    }
  }

  const handleUpdateUser = async () => {
    if (!selectedUser) return
    
    if (!formData.fullName.trim()) {
      alert('Please enter a full name')
      return
    }
    if (!formData.email.trim()) {
      alert('Please enter an email address')
      return
    }
    if (!formData.role) {
      alert('Please select a role')
      return
    }
    
    try {
      await api.updateUser(selectedUser.id, {
        full_name: formData.fullName.trim(),
        email: formData.email.trim(),
        role: formData.role,
        is_active: formData.isActive
      })
      await loadUsers()
      handleCloseModals()
      alert('User updated successfully!')
    } catch (error: any) {
      console.error('Failed to update user:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to update user. Please try again.'
      alert(errorMessage)
    }
  }

  const handleDeleteUser = async (user: any) => {
    if (user.id === currentUser?.id) {
      alert('You cannot delete your own account')
      return
    }
    
    if (window.confirm(`Are you sure you want to permanently delete user "${user.fullName || user.full_name}"?\n\nThis action cannot be undone and will remove all user data.`)) {
      try {
        await api.deleteUser(user.id)
        // Remove user from the list immediately
        setUsers(prevUsers => prevUsers.filter(u => u.id !== user.id))
        alert('User permanently deleted!')
      } catch (error: any) {
        console.error('Failed to delete user:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete user. Please try again.'
        alert(errorMessage)
      }
    }
  }

  const handleCloseModals = () => {
    setShowAddModal(false)
    setShowEditModal(false)
    setSelectedUser(null)
    setFormData({
      fullName: '',
      email: '',
      role: 'Developer',
      isActive: true
    })
  }

  const isAdmin = currentUser?.role === 'Admin'

  if (loading) {
    return <div style={{ color: 'var(--text-color)' }}>{t('loading')}</div>
  }

  if (!isAdmin) {
    return (
      <div className="text-center py-12">
        <p className="text-xl" style={{ color: 'var(--error-color)' }}>
          ⚠️ Access Denied
        </p>
        <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
          Only administrators can access user management.
        </p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-color)' }}>
          {t('users')} 👥
        </h1>
        <button 
          className="px-4 py-2 rounded-md hover:opacity-80 transition-opacity"
          style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}
          onClick={handleAddUser}>
          + Add User
        </button>
      </div>

      {users.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-xl" style={{ color: 'var(--text-secondary)' }}>
            No users found
          </p>
        </div>
      ) : (
        <div className="rounded-lg shadow-md overflow-hidden"
             style={{ 
               backgroundColor: 'var(--surface-color)',
               border: '1px solid var(--border-color)'
             }}>
          <table className="w-full">
            <thead>
              <tr style={{ backgroundColor: 'var(--secondary-color)' }}>
                <th className="text-left p-4" style={{ color: 'var(--text-color)' }}>Name</th>
                <th className="text-left p-4" style={{ color: 'var(--text-color)' }}>Email</th>
                <th className="text-left p-4" style={{ color: 'var(--text-color)' }}>Role</th>
                <th className="text-left p-4" style={{ color: 'var(--text-color)' }}>Status</th>
                <th className="text-left p-4" style={{ color: 'var(--text-color)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
              <tr key={user.id}
                  className="border-t"
                  style={{ borderColor: 'var(--border-color)' }}>
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full flex items-center justify-center"
                         style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}>
                      {user.fullName?.charAt(0) || user.full_name?.charAt(0) || '?'}
                    </div>
                    <span style={{ color: 'var(--text-color)' }}>{user.fullName || user.full_name || 'Unknown'}</span>
                  </div>
                </td>
                <td className="p-4" style={{ color: 'var(--text-secondary)' }}>
                  {user.email}
                </td>
                <td className="p-4">
                  <span className="px-3 py-1 rounded text-sm"
                        style={{ 
                          backgroundColor: 'var(--secondary-color)',
                          color: 'var(--text-color)'
                        }}>
                    {user.role}
                  </span>
                </td>
                <td className="p-4">
                  <span className={`px-3 py-1 rounded text-sm ${(user.isActive || user.is_active) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {(user.isActive || user.is_active) ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="p-4">
                  <div className="flex gap-2">
                    <button 
                      className="px-3 py-1 text-sm rounded hover:opacity-80 transition-opacity"
                      style={{ backgroundColor: 'var(--info-color)', color: 'white' }}
                      onClick={() => handleEditUser(user)}>
                      Edit
                    </button>
                    <button 
                      className="px-3 py-1 text-sm rounded hover:opacity-80 transition-opacity"
                      style={{ backgroundColor: 'var(--error-color)', color: 'white' }}
                      onClick={() => handleDeleteUser(user)}>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add User Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-90vw" style={{ backgroundColor: 'var(--surface-color)' }}>
            <h2 className="text-xl font-bold mb-4" style={{ color: 'var(--text-color)' }}>Add New User</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-color)' }}>
                  Full Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border rounded-md"
                  style={{ 
                    backgroundColor: 'var(--surface-color)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                  placeholder="Enter full name"
                  value={formData.fullName}
                  onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-color)' }}>
                  Email
                </label>
                <input
                  type="email"
                  className="w-full px-3 py-2 border rounded-md"
                  style={{ 
                    backgroundColor: 'var(--surface-color)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                  placeholder="Enter email address"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-color)' }}>
                  Role
                </label>
                <select
                  className="w-full px-3 py-2 border rounded-md"
                  style={{ 
                    backgroundColor: 'var(--surface-color)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}>
                  <option value="Developer">Developer</option>
                  <option value="Project Manager">Project Manager</option>
                  <option value="Tester">Tester</option>
                  <option value="DevOps">DevOps</option>
                  <option value="Admin">Admin</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                className="px-4 py-2 rounded-md hover:opacity-80 transition-opacity"
                style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}
                onClick={handleCreateUser}>
                Create User
              </button>
              <button
                className="px-4 py-2 rounded-md border hover:opacity-80 transition-opacity"
                style={{ 
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-color)',
                  backgroundColor: 'transparent'
                }}
                onClick={handleCloseModals}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {showEditModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-90vw" style={{ backgroundColor: 'var(--surface-color)' }}>
            <h2 className="text-xl font-bold mb-4" style={{ color: 'var(--text-color)' }}>
              Edit User: {selectedUser.fullName || selectedUser.full_name}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-color)' }}>
                  Full Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border rounded-md"
                  style={{ 
                    backgroundColor: 'var(--surface-color)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                  value={formData.fullName}
                  onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-color)' }}>
                  Email
                </label>
                <input
                  type="email"
                  className="w-full px-3 py-2 border rounded-md"
                  style={{ 
                    backgroundColor: 'var(--surface-color)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-color)' }}>
                  Role
                </label>
                <select
                  className="w-full px-3 py-2 border rounded-md"
                  style={{ 
                    backgroundColor: 'var(--surface-color)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}>
                  <option value="Developer">Developer</option>
                  <option value="Project Manager">Project Manager</option>
                  <option value="Tester">Tester</option>
                  <option value="DevOps">DevOps</option>
                  <option value="Admin">Admin</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-color)' }}>
                  Status
                </label>
                <select
                  className="w-full px-3 py-2 border rounded-md"
                  style={{ 
                    backgroundColor: 'var(--surface-color)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                  value={formData.isActive ? 'active' : 'inactive'}
                  onChange={(e) => setFormData({...formData, isActive: e.target.value === 'active'})}>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                className="px-4 py-2 rounded-md hover:opacity-80 transition-opacity"
                style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}
                onClick={handleUpdateUser}>
                Update User
              </button>
              <button
                className="px-4 py-2 rounded-md border hover:opacity-80 transition-opacity"
                style={{ 
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-color)',
                  backgroundColor: 'transparent'
                }}
                onClick={handleCloseModals}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
