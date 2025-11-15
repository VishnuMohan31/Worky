import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useLanguage } from '../../contexts/LanguageContext'

interface NavGroup {
  label: string
  icon: string
  items: NavItem[]
  defaultOpen?: boolean
}

interface NavItem {
  path: string
  label: string
  icon: string
}

export default function Sidebar() {
  const { t } = useLanguage()
  
  // Track which groups are expanded
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    hierarchy: true,
    planning: true,
    tracking: true,
    admin: true
  })
  
  const toggleGroup = (groupKey: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupKey]: !prev[groupKey]
    }))
  }

  // Standalone navigation items (not in groups)
  const standaloneItems: NavItem[] = [
    { path: '/dashboard', label: t('dashboard'), icon: '📊' }
  ]

  // Grouped navigation items
  const navGroups: Record<string, NavGroup> = {
    hierarchy: {
      label: 'Hierarchy',
      icon: '🏗️',
      defaultOpen: true,
      items: [
        { path: '/clients', label: t('clients'), icon: '🏢' },
        { path: '/programs', label: 'Programs', icon: '📦' },
        { path: '/projects', label: t('projects'), icon: '📁' },
        { path: '/usecases', label: 'Use Cases', icon: '🎯' },
        { path: '/userstories', label: 'User Stories', icon: '📝' },
        { path: '/tasks', label: t('tasks'), icon: '✓' }
      ]
    },
    planning: {
      label: 'Planning & Views',
      icon: '📅',
      defaultOpen: true,
      items: [
        { path: '/gantt', label: t('gantt'), icon: '📈' },
        { path: '/kanban', label: t('kanban'), icon: '📋' },
        { path: '/sprint', label: t('sprint'), icon: '🏃' }
      ]
    },
    tracking: {
      label: 'Tracking',
      icon: '🔍',
      defaultOpen: true,
      items: [
        { path: '/bugs', label: t('bugs'), icon: '🐛' },
        { path: '/reports', label: t('reports'), icon: '📑' }
      ]
    },
    admin: {
      label: 'Administration',
      icon: '⚙️',
      defaultOpen: false,
      items: [
        { path: '/users', label: t('users'), icon: '👥' },
        { path: '/phases', label: 'Phases', icon: '🔄' }
      ]
    }
  }

  return (
    <aside className="w-64 border-r overflow-y-auto" 
           style={{ 
             backgroundColor: 'var(--surface-color)',
             borderColor: 'var(--border-color)'
           }}>
      <div className="p-6">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--primary-color)' }}>
          Worky
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
          Project Management
        </p>
      </div>

      <nav className="px-3 pb-6">
        {/* Standalone Items */}
        {standaloneItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-3 px-3 py-2 rounded-md mb-1 transition-colors
              ${isActive ? 'font-medium' : ''}
            `}
            style={({ isActive }) => ({
              backgroundColor: isActive ? 'var(--primary-color)' : 'transparent',
              color: isActive ? 'white' : 'var(--text-color)'
            })}
          >
            <span className="text-xl">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}

        {/* Grouped Items */}
        {Object.entries(navGroups).map(([groupKey, group]) => (
          <div key={groupKey} className="mt-4">
            {/* Group Header */}
            <button
              onClick={() => toggleGroup(groupKey)}
              className="w-full flex items-center justify-between px-3 py-2 rounded-md mb-1 transition-colors hover:bg-opacity-10"
              style={{ 
                color: 'var(--text-secondary)',
                backgroundColor: 'transparent'
              }}
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">{group.icon}</span>
                <span className="text-sm font-semibold uppercase tracking-wide">
                  {group.label}
                </span>
              </div>
              <svg
                className={`w-4 h-4 transition-transform ${expandedGroups[groupKey] ? 'rotate-90' : ''}`}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M9 5l7 7-7 7" />
              </svg>
            </button>

            {/* Group Items */}
            {expandedGroups[groupKey] && (
              <div className="ml-2 space-y-1">
                {group.items.map(item => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) => `
                      flex items-center gap-3 px-3 py-2 rounded-md transition-colors
                      ${isActive ? 'font-medium' : ''}
                    `}
                    style={({ isActive }) => ({
                      backgroundColor: isActive ? 'var(--primary-color)' : 'transparent',
                      color: isActive ? 'white' : 'var(--text-color)'
                    })}
                  >
                    <span className="text-lg">{item.icon}</span>
                    <span className="text-sm">{item.label}</span>
                  </NavLink>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>
    </aside>
  )
}
