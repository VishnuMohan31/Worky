import { useState, useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { useLanguage } from '../../contexts/LanguageContext'
import api from '../../services/api'
import { fetchTodoItems } from '../../services/todoApi'

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
  entityType?: string
}

export default function Sidebar() {
  const { t } = useLanguage()
  const location = useLocation()
  const [companyName, setCompanyName] = useState<string>('Worky')
  const [todayTodoCount, setTodayTodoCount] = useState<number>(0)
  
  // Track which groups are expanded
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    hierarchy: true,
    planning: true,
    tracking: true,
    management: true,
    qa: true,
    admin: true
  })

  // Load organization name
  useEffect(() => {
    const loadOrganizationName = async () => {
      try {
        const organizations = await api.getOrganizations(true) // Only active organizations
        if (organizations.length > 0) {
          const org = organizations[0] // Use the first active organization
          if (org.name) {
            setCompanyName(org.name)
          }
        }
      } catch (error) {
        // If organizations don't exist, use defaults
        console.error('Failed to load organization:', error)
      }
    }
    loadOrganizationName()
  }, [])

  // Load today's TODO count for badge
  useEffect(() => {
    const loadTodayTodoCount = async () => {
      try {
        const today = new Date().toISOString().split('T')[0]
        const response = await fetchTodoItems({
          start_date: today,
          end_date: today
        })
        setTodayTodoCount(response.total || 0)
      } catch (error) {
        // Silently fail - badge will show 0
        console.error('Failed to load TODO count:', error)
      }
    }
    loadTodayTodoCount()
    
    // Refresh count every 60 seconds
    const interval = setInterval(loadTodayTodoCount, 60000)
    return () => clearInterval(interval)
  }, [])
  
  const toggleGroup = (groupKey: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupKey]: !prev[groupKey]
    }))
  }

  // Helper function to check if a nav item should be active
  // This handles both exact path matches and hierarchy detail pages
  const isNavItemActive = (path: string, entityType?: string): boolean => {
    const currentPath = location.pathname
    
    // Check exact match
    if (currentPath === path || currentPath.startsWith(path + '/')) {
      return true
    }
    
    // Check hierarchy detail pages
    if (entityType) {
      // Map entity types to their hierarchy route patterns
      const hierarchyPatterns: Record<string, string[]> = {
        '/clients': ['/hierarchy/client/'],
        '/programs': ['/hierarchy/program/'],
        '/projects': ['/hierarchy/project/', '/projects/'],
        '/usecases': ['/hierarchy/usecase/'],
        '/userstories': ['/hierarchy/userstory/', '/hierarchy/user_story/'],
        '/tasks': ['/hierarchy/task/'],
        '/subtasks': ['/hierarchy/subtask/']
      }
      
      const patterns = hierarchyPatterns[path] || []
      return patterns.some(pattern => currentPath.startsWith(pattern))
    }
    
    return false
  }

  // Standalone navigation items (not in groups)
  const standaloneItems: NavItem[] = [
    { path: '/dashboard', label: t('dashboard'), icon: '📊' },
    { path: '/todos', label: 'TODO', icon: '✅' }
  ]

  // Grouped navigation items
  const navGroups: Record<string, NavGroup> = {
    hierarchy: {
      label: 'Hierarchy',
      icon: '🏗️',
      defaultOpen: true,
      items: [
        { path: '/clients', label: t('clients'), icon: '🏢', entityType: 'client' },
        { path: '/programs', label: 'Programs', icon: '📦', entityType: 'program' },
        { path: '/projects', label: t('projects'), icon: '📁', entityType: 'project' },
        { path: '/usecases', label: 'Use Cases', icon: '🎯', entityType: 'usecase' },
        { path: '/userstories', label: 'User Stories', icon: '📝', entityType: 'userstory' },
        { path: '/tasks', label: t('tasks'), icon: '✓', entityType: 'task' },
        { path: '/subtasks', label: 'Subtasks', icon: '📌', entityType: 'subtask' }
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
    qa: {
      label: 'QA',
      icon: '🧪',
      defaultOpen: true,
      items: [
        { path: '/test-runs', label: 'Test Runs', icon: '🏃' },
        { path: '/test-cases', label: 'Test Cases', icon: '📋' },
        { path: '/bug-lifecycle', label: 'Bug Lifecycle', icon: '🐛' }
      ]
    },
    management: {
      label: 'Management',
      icon: '👥',
      defaultOpen: true,
      items: [
        { path: '/teams', label: 'Teams', icon: '👥' },
        { path: '/decisions', label: 'Decisions', icon: '📋' }
      ]
    },
    admin: {
      label: 'Administration',
      icon: '⚙️',
      defaultOpen: false,
      items: [
        { path: '/users', label: t('users'), icon: '👤' },
        { path: '/phases', label: 'Phases', icon: '🔄' },
        { path: '/organizations', label: 'Organizations', icon: '🏢' },
        { path: '/sprint-configuration', label: 'Sprint Configuration', icon: '🏃' }
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
        {/* Company Name */}
        {companyName && companyName !== 'Worky' && (
          <h2 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-color)' }}>
            {companyName}
          </h2>
        )}
        
        {/* WORKY App Name */}
        <h1 className="text-2xl font-bold mb-1" style={{ color: 'var(--primary-color)' }}>
          WORKY
        </h1>
        
        {/* Tagline */}
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Plan. Execute. Win.
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
            <span className="flex-1">{item.label}</span>
            {/* Show badge for TODO items */}
            {item.path === '/todos' && todayTodoCount > 0 && (
              <span 
                className="px-2 py-0.5 text-xs font-semibold rounded-full"
                style={{
                  backgroundColor: 'var(--primary-color)',
                  color: 'white',
                  minWidth: '20px',
                  textAlign: 'center'
                }}
              >
                {todayTodoCount}
              </span>
            )}
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
                {group.items.map(item => {
                  const isActive = isNavItemActive(item.path, item.entityType)
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={`
                        flex items-center gap-3 px-3 py-2 rounded-md transition-colors
                        ${isActive ? 'font-medium' : ''}
                      `}
                      style={{
                        backgroundColor: isActive ? 'var(--primary-color)' : 'transparent',
                        color: isActive ? 'white' : 'var(--text-color)'
                      }}
                    >
                      <span className="text-lg">{item.icon}</span>
                      <span className="text-sm">{item.label}</span>
                    </NavLink>
                  )
                })}
              </div>
            )}
          </div>
        ))}
      </nav>
    </aside>
  )
}
