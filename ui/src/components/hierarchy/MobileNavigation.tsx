/**
 * Mobile Navigation Component for Hierarchy
 * 
 * Provides tab-based navigation for mobile devices to switch between
 * parent, current, and children views in the hierarchy.
 */
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

interface MobileNavigationProps {
  onTabChange: (tab: 'parent' | 'current' | 'children') => void
  hasParent: boolean
  hasChildren: boolean
  currentTab?: 'parent' | 'current' | 'children'
}

export default function MobileNavigation({
  onTabChange,
  hasParent,
  hasChildren,
  currentTab = 'current'
}: MobileNavigationProps) {
  // Use fallback text instead of translation to avoid i18n issues
  const t = (key: string) => {
    const translations: Record<string, string> = {
      parent: 'Parent',
      viewDetails: 'Details',
      children: 'Children'
    }
    return translations[key] || key
  }
  
  const [activeTab, setActiveTab] = useState<'parent' | 'current' | 'children'>(currentTab)

  useEffect(() => {
    setActiveTab(currentTab)
  }, [currentTab])

  const handleTabClick = (tab: 'parent' | 'current' | 'children') => {
    setActiveTab(tab)
    onTabChange(tab)
  }

  const tabsStyle = {
    display: 'flex',
    backgroundColor: '#ffffff',
    borderBottom: '2px solid #e5e7eb',
    overflowX: 'auto' as const
  }

  const getTabStyle = (isActive: boolean) => ({
    flex: 1,
    minWidth: '80px',
    padding: '0.75rem 1rem',
    background: 'none',
    border: 'none',
    borderBottom: isActive ? '3px solid #3b82f6' : '3px solid transparent',
    backgroundColor: isActive ? '#f9fafb' : 'transparent',
    color: isActive ? '#3b82f6' : '#6b7280',
    fontSize: '0.875rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
    whiteSpace: 'nowrap' as const
  })

  return (
    <div style={tabsStyle}>
      {hasParent && (
        <button
          style={getTabStyle(activeTab === 'parent')}
          onClick={() => handleTabClick('parent')}
          aria-label={t('parent')}
        >
          ← {t('parent')}
        </button>
      )}
      
      <button
        style={getTabStyle(activeTab === 'current')}
        onClick={() => handleTabClick('current')}
        aria-label={t('viewDetails')}
      >
        {t('viewDetails')}
      </button>
      
      {hasChildren && (
        <button
          style={getTabStyle(activeTab === 'children')}
          onClick={() => handleTabClick('children')}
          aria-label={t('children')}
        >
          {t('children')} →
        </button>
      )}
    </div>
  )
}
