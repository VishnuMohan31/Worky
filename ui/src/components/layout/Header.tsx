import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useTheme } from '../../contexts/ThemeContext'
import { useLanguage } from '../../contexts/LanguageContext'

interface HeaderProps {
  onChatToggle?: () => void
  isChatOpen?: boolean
}

export default function Header({ onChatToggle, isChatOpen }: HeaderProps) {
  const { user, logout } = useAuth()
  const { theme, setTheme } = useTheme()
  const { language, setLanguage, t } = useLanguage()
  const [showThemeMenu, setShowThemeMenu] = useState(false)
  const [showLangMenu, setShowLangMenu] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

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
    <header className="h-16 border-b flex items-center justify-between px-6"
            style={{ 
              backgroundColor: 'var(--surface-color)',
              borderColor: 'var(--border-color)'
            }}>
      <div className="flex items-center gap-4">
        <h2 className="text-xl font-semibold" style={{ color: 'var(--text-color)' }}>
          {user?.fullName}
        </h2>
        <span className="px-2 py-1 text-xs rounded"
              style={{ 
                backgroundColor: 'var(--secondary-color)',
                color: 'var(--text-color)'
              }}>
          {user?.role}
        </span>
      </div>

      <div className="flex items-center gap-4">
        {/* Chat Assistant Toggle */}
        {onChatToggle && (
          <button
            onClick={onChatToggle}
            className="px-3 py-2 rounded-md transition-colors relative"
            style={{ 
              backgroundColor: isChatOpen ? 'var(--primary-color)' : 'var(--secondary-color)',
              color: isChatOpen ? 'white' : 'var(--text-color)'
            }}
            title="Chat Assistant (Ctrl+K or Cmd+K)"
            aria-label="Toggle chat assistant"
          >
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span className="hidden sm:inline">{t('chat') || 'Chat'}</span>
            </div>
          </button>
        )}
        
        {/* Theme Selector */}
        <div className="relative">
          <button
            onClick={() => setShowThemeMenu(!showThemeMenu)}
            className="px-3 py-2 rounded-md transition-colors"
            style={{ 
              backgroundColor: 'var(--secondary-color)',
              color: 'var(--text-color)'
            }}
          >
            🎨 {t('theme')}
          </button>
          
          {showThemeMenu && (
            <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg z-10"
                 style={{ 
                   backgroundColor: 'var(--surface-color)',
                   border: '1px solid var(--border-color)'
                 }}>
              {themes.map(th => (
                <button
                  key={th.id}
                  onClick={() => {
                    setTheme(th.id as any)
                    setShowThemeMenu(false)
                  }}
                  className="w-full text-left px-4 py-2 hover:opacity-80 transition-opacity flex items-center gap-2"
                  style={{ 
                    backgroundColor: theme === th.id ? 'var(--primary-color)' : 'transparent',
                    color: theme === th.id ? 'white' : 'var(--text-color)'
                  }}
                >
                  <span>{th.icon}</span>
                  <span>{th.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Language Selector */}
        <div className="relative">
          <button
            onClick={() => setShowLangMenu(!showLangMenu)}
            className="px-3 py-2 rounded-md transition-colors"
            style={{ 
              backgroundColor: 'var(--secondary-color)',
              color: 'var(--text-color)'
            }}
          >
            🌐 {t('language')}
          </button>
          
          {showLangMenu && (
            <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg z-10"
                 style={{ 
                   backgroundColor: 'var(--surface-color)',
                   border: '1px solid var(--border-color)'
                 }}>
              {languages.map(lang => (
                <button
                  key={lang.id}
                  onClick={() => {
                    setLanguage(lang.id as any)
                    setShowLangMenu(false)
                  }}
                  className="w-full text-left px-4 py-2 hover:opacity-80 transition-opacity flex items-center gap-2"
                  style={{ 
                    backgroundColor: language === lang.id ? 'var(--primary-color)' : 'transparent',
                    color: language === lang.id ? 'white' : 'var(--text-color)'
                  }}
                >
                  <span>{lang.icon}</span>
                  <span>{lang.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}
          >
            {user?.fullName.charAt(0)}
          </button>
          
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg z-10"
                 style={{ 
                   backgroundColor: 'var(--surface-color)',
                   border: '1px solid var(--border-color)'
                 }}>
              <button
                onClick={() => {
                  setShowUserMenu(false)
                  window.location.href = '/profile'
                }}
                className="w-full text-left px-4 py-2 hover:opacity-80 transition-opacity"
                style={{ color: 'var(--text-color)' }}
              >
                {t('profile')}
              </button>
              <button
                onClick={logout}
                className="w-full text-left px-4 py-2 hover:opacity-80 transition-opacity"
                style={{ color: 'var(--error-color)' }}
              >
                {t('logout')}
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
