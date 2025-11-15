import { useEffect, useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

export default function UsersPage() {
  const { t } = useLanguage()
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const data = await api.getUsers()
      setUsers(data)
    } catch (error) {
      console.error('Failed to load users:', error)
    } finally {
      setLoading(false)
    }
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
        <button className="px-4 py-2 rounded-md"
                style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}>
          + Add User
        </button>
      </div>

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
                      {user.fullName.charAt(0)}
                    </div>
                    <span style={{ color: 'var(--text-color)' }}>{user.fullName}</span>
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
                  <span className={`px-3 py-1 rounded text-sm ${user.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {user.isActive ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="p-4">
                  <div className="flex gap-2">
                    <button className="px-3 py-1 text-sm rounded"
                            style={{ backgroundColor: 'var(--info-color)', color: 'white' }}>
                      Edit
                    </button>
                    <button className="px-3 py-1 text-sm rounded"
                            style={{ backgroundColor: 'var(--error-color)', color: 'white' }}>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
