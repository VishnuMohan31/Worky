import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { useLanguage } from '../contexts/LanguageContext'

export default function ProfilePage() {
  const { user } = useAuth()
  const { theme, setTheme } = useTheme()
  const { language, setLanguage, t } = useLanguage()
  const [editing, setEditing] = useState(false)

  const themes = [
    { id: 'snow', name: t('snow'), icon: '❄️' },
    { id: 'greenery', name: t('greenery'), icon: '🌿' },
    { id: 'water', name: t('water'), icon: '💧' },
    { id: 'dracula', name: t('dracula'), icon: '🧛' },
    { id: 'dark', name: t('dark'), icon: '🌙' },
    { id: 'blackwhite', name: t('blackwhite'), icon: '⚫' }
  ]

  const languages = [
    { id: 'en', name: t('english'), icon: '🇬🇧' },
    { id: 'te', name: t('telugu'), icon: '🇮🇳' }
  ]

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text-color)' }}>
        {t('profile')}
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Information */}
        <div className="rounded-lg p-6 shadow-md"
             style={{ 
               backgroundColor: 'var(--surface-color)',
               border: '1px solid var(--border-color)'
             }}>
          <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
            User Information
          </h2>
          
          <div className="flex items-center gap-4 mb-6">
            <div className="w-20 h-20 rounded-full flex items-center justify-center text-3xl"
                 style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}>
              {user?.fullName.charAt(0)}
            </div>
            <div>
              <h3 className="text-xl font-semibold" style={{ color: 'var(--text-color)' }}>
                {user?.fullName}
              </h3>
              <p style={{ color: 'var(--text-secondary)' }}>{user?.email}</p>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-sm" style={{ color: 'var(--text-secondary)' }}>Role</label>
              <p className="font-medium" style={{ color: 'var(--text-color)' }}>{user?.role}</p>
            </div>
            <div>
              <label className="text-sm" style={{ color: 'var(--text-secondary)' }}>Client ID</label>
              <p className="font-medium" style={{ color: 'var(--text-color)' }}>{user?.clientId}</p>
            </div>
          </div>

          <button className="mt-6 px-4 py-2 rounded-md w-full"
                  style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}
                  onClick={() => setEditing(!editing)}>
            {editing ? 'Save Changes' : 'Edit Profile'}
          </button>
        </div>

        {/* Preferences */}
        <div className="rounded-lg p-6 shadow-md"
             style={{ 
               backgroundColor: 'var(--surface-color)',
               border: '1px solid var(--border-color)'
             }}>
          <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
            Preferences
          </h2>

          {/* Theme Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
              {t('theme')}
            </label>
            <div className="grid grid-cols-2 gap-2">
              {themes.map(th => (
                <button
                  key={th.id}
                  onClick={() => setTheme(th.id as any)}
                  className="flex items-center gap-2 p-3 rounded transition-colors"
                  style={{
                    backgroundColor: theme === th.id ? 'var(--primary-color)' : 'var(--secondary-color)',
                    color: theme === th.id ? 'white' : 'var(--text-color)'
                  }}
                >
                  <span>{th.icon}</span>
                  <span>{th.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Language Selection */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
              {t('language')}
            </label>
            <div className="grid grid-cols-2 gap-2">
              {languages.map(lang => (
                <button
                  key={lang.id}
                  onClick={() => setLanguage(lang.id as any)}
                  className="flex items-center gap-2 p-3 rounded transition-colors"
                  style={{
                    backgroundColor: language === lang.id ? 'var(--primary-color)' : 'var(--secondary-color)',
                    color: language === lang.id ? 'white' : 'var(--text-color)'
                  }}
                >
                  <span>{lang.icon}</span>
                  <span>{lang.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Security Section */}
      <div className="mt-6 rounded-lg p-6 shadow-md"
           style={{ 
             backgroundColor: 'var(--surface-color)',
             border: '1px solid var(--border-color)'
           }}>
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
          Security
        </h2>
        <button className="px-4 py-2 rounded-md"
                style={{ backgroundColor: 'var(--warning-color)', color: 'white' }}>
          Change Password
        </button>
      </div>
    </div>
  )
}
