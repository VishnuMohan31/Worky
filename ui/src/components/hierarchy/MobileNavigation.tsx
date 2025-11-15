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
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<'parent' | 'current' | 'children'>(currentTab)

  useEffect(() => {
    setActiveTab(currentTab)
  }, [currentTab])

  const handleTabClick = (tab: 'parent' | 'current' | 'children') => {
    setActiveTab(tab)
    onTabChange(tab)
  }

  return (
    <div className="mobile-tabs">
      {hasParent && (
        <button
          className={`mobile-tab ${activeTab === 'parent' ? 'active' : ''}`}
          onClick={() => handleTabClick('parent')}
          aria-label={t('parent')}
        >
          ← {t('parent')}
        </button>
      )}
      
      <button
        className={`mobile-tab ${activeTab === 'current' ? 'active' : ''}`}
        onClick={() => handleTabClick('current')}
        aria-label={t('viewDetails')}
      >
        {t('viewDetails')}
      </button>
      
      {hasChildren && (
        <button
          className={`mobile-tab ${activeTab === 'children' ? 'active' : ''}`}
          onClick={() => handleTabClick('children')}
          aria-label={t('children')}
        >
          {t('children')} →
        </button>
      )}
    </div>
  )
}
