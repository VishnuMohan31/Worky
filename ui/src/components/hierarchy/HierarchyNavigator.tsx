/**
 * HierarchyNavigator Component
 * Responsive three-pane layout for navigating entity hierarchy
 * - Desktop: Three columns (Parent | Current | Children)
 * - Tablet: Two columns (Current | Children)
 * - Mobile: Single column with tabs
 */
import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useHierarchyStore, getParentType, getChildType, EntityType } from '../../stores/hierarchyStore'
import { useEntityWithContext } from '../../hooks/useEntity'
import { useResponsive } from '../../hooks/useResponsive'
import Breadcrumb from './Breadcrumb'
import EntityDetails from './EntityDetails'
import EntityList from './EntityList'
import MobileNavigation from './MobileNavigation'
import SkeletonLoader from './SkeletonLoader'
import { AssignmentDisplay } from '../assignments/AssignmentDisplay'

interface HierarchyNavigatorProps {
  initialEntityId?: string
  initialEntityType?: EntityType
}

function HierarchyNavigatorInner({
  initialEntityId,
  initialEntityType
}: HierarchyNavigatorProps) {
  const { type, id } = useParams<{ type: string; id: string }>()
  const navigate = useNavigate()
  const { isMobile, isTablet } = useResponsive()
  
  const entityType = (type || initialEntityType) as EntityType
  const entityId = id || initialEntityId
  
  // Validate required parameters
  if (!entityType || !entityId) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
        <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-md">
          <div className="text-yellow-600 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Missing Parameters</h2>
          <p className="text-gray-600 mb-4">Entity type or ID is missing from the URL.</p>
          <div className="text-sm text-gray-500 mb-6">
            Entity Type: <span className="font-mono">{entityType || 'undefined'}</span><br />
            Entity ID: <span className="font-mono">{entityId || 'undefined'}</span>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    )
  }
  
  const {
    currentEntity,
    parentEntity,
    childEntities,
    setCurrentEntity,
    setParentEntity,
    setChildEntities,
    setBreadcrumb
  } = useHierarchyStore()
  
  // Mobile tab state
  const [activeTab, setActiveTab] = useState<'parent' | 'current' | 'children'>('current')
  
  // Fetch entity with context (parent and children)
  const { data: contextData, isLoading, error } = useEntityWithContext(entityType, entityId)
  
  // Update store when data is fetched
  useEffect(() => {
    if (contextData) {
      try {
        // Ensure we have valid data before updating store
        if (contextData.entity) {
          setCurrentEntity(contextData.entity, entityType)
          setParentEntity(contextData.parent, getParentType(entityType))
          setChildEntities(contextData.children || [], getChildType(entityType))
          setBreadcrumb(contextData.breadcrumb || [])
        } else {
          console.error('Context data missing entity:', contextData)
        }
      } catch (err) {
        console.error('Error updating hierarchy store:', err)
      }
    }
  }, [contextData, entityType, setCurrentEntity, setParentEntity, setChildEntities, setBreadcrumb])
  
  // Reset to current tab when entity changes
  useEffect(() => {
    if (isMobile) {
      setActiveTab('current')
    }
  }, [entityId, isMobile])
  
  const handleParentClick = () => {
    if (parentEntity) {
      const parentType = getParentType(entityType)
      if (parentType) {
        navigate(`/hierarchy/${parentType}/${parentEntity.id}`)
      }
    }
  }
  
  const handleChildClick = (child: any) => {
    const childType = getChildType(entityType)
    if (childType) {
      navigate(`/hierarchy/${childType}/${child.id}`)
    }
  }
  
  const handleBreadcrumbClick = (item: any) => {
    navigate(`/hierarchy/${item.type}/${item.id}`)
  }
  
  if (isLoading) {
    return (
      <div style={{
        display: 'grid',
        gridTemplateRows: 'auto 1fr',
        height: '100vh',
        backgroundColor: '#f9fafb'
      }}>
        <div style={{
          padding: '1rem',
          backgroundColor: '#ffffff',
          borderBottom: '1px solid #e5e7eb'
        }}>
          <SkeletonLoader type="list" count={1} />
        </div>
        <div style={{
          padding: '1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem',
            padding: '2rem',
            width: '100%',
            maxWidth: '600px'
          }}>
            <SkeletonLoader type="details" />
          </div>
        </div>
      </div>
    )
  }
  
  if (error) {
    console.error('HierarchyNavigator error:', error)
    const errorMessage = (error as any)?.response?.data?.detail || 
                        (error as any)?.message || 
                        'Failed to load entity'
    
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
        <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-md">
          <div className="text-red-600 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Error Loading {entityType}</h2>
          <p className="text-gray-600 mb-4">{errorMessage}</p>
          <div className="text-sm text-gray-500 mb-6">
            Entity Type: <span className="font-mono">{entityType}</span><br />
            Entity ID: <span className="font-mono">{entityId}</span>
          </div>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => navigate(-1)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Go Back
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => window.location.href = `/hierarchy/${entityType}/${entityId}?debug=true`}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Debug Mode
            </button>
          </div>
        </div>
      </div>
    )
  }
  
  if (!currentEntity) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center p-6">
          <p className="text-gray-600">No entity found</p>
        </div>
      </div>
    )
  }
  
  const parentType = getParentType(entityType)
  const childType = getChildType(entityType)
  
  // Base styles for consistent layout
  const baseStyles = {
    navigator: {
      display: 'grid',
      gridTemplateRows: 'auto 1fr',
      height: '100vh',
      backgroundColor: '#f9fafb',
      color: '#111827',
      overflow: 'hidden'
    },
    breadcrumb: {
      display: 'flex',
      alignItems: 'center',
      padding: '1rem',
      backgroundColor: '#ffffff',
      borderBottom: '1px solid #e5e7eb',
      fontSize: '0.875rem',
      overflowX: 'auto' as const,
      whiteSpace: 'nowrap' as const
    },
    content: {
      display: 'grid',
      gap: '1rem',
      padding: '1rem',
      overflow: 'hidden',
      height: '100%'
    },
    pane: {
      backgroundColor: '#ffffff',
      border: '1px solid #e5e7eb',
      borderRadius: '0.5rem',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column' as const,
      height: '100%',
      minHeight: 0
    },
    paneHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '1rem',
      backgroundColor: '#f9fafb',
      borderBottom: '1px solid #e5e7eb'
    },
    paneContent: {
      flex: 1,
      padding: '1rem',
      overflowY: 'auto' as const,
      minHeight: 0,
      maxHeight: 'calc(100vh - 150px)'
    }
  }

  // Mobile: Single pane with tabs
  if (isMobile) {
    return (
      <div style={baseStyles.navigator}>
        {/* Breadcrumb */}
        <div style={baseStyles.breadcrumb}>
          <Breadcrumb onItemClick={handleBreadcrumbClick} />
        </div>
        
        {/* Mobile Tabs */}
        <MobileNavigation
          onTabChange={setActiveTab}
          hasParent={!!parentEntity}
          hasChildren={childEntities.length > 0}
          currentTab={activeTab}
        />
        
        {/* Content based on active tab */}
        <div style={{ ...baseStyles.content, gridTemplateColumns: '1fr', padding: 0 }}>
          {/* Parent Pane */}
          {activeTab === 'parent' && parentEntity && parentType && (
            <div style={{ ...baseStyles.pane, borderRadius: 0, border: 'none' }}>
              <div style={baseStyles.paneHeader}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', margin: 0 }}>Parent {parentType}</h3>
                <button
                  onClick={handleParentClick}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  View Details →
                </button>
              </div>
              <div style={baseStyles.paneContent}>
                <EntityDetails entity={parentEntity} type={parentType} compact />
              </div>
            </div>
          )}
          
          {/* Current Entity Pane */}
          {activeTab === 'current' && (
            <div style={{ ...baseStyles.pane, borderRadius: 0, border: 'none' }}>
              <div style={baseStyles.paneContent}>
                <EntityDetails entity={currentEntity} type={entityType} />
              </div>
            </div>
          )}
          
          {/* Children Pane */}
          {activeTab === 'children' && childType && (
            <div style={{ ...baseStyles.pane, borderRadius: 0, border: 'none' }}>
              <EntityList
                entities={childEntities}
                entityType={childType}
                onEntityClick={handleChildClick}
                parentId={entityId}
              />
            </div>
          )}
        </div>
      </div>
    )
  }
  
  // Tablet: Two columns (Current | Children)
  if (isTablet) {
    return (
      <div style={baseStyles.navigator}>
        {/* Breadcrumb */}
        <div style={baseStyles.breadcrumb}>
          <Breadcrumb onItemClick={handleBreadcrumbClick} />
        </div>
        
        <div style={{ ...baseStyles.content, gridTemplateColumns: '1fr 350px' }}>
          {/* Current Entity Pane */}
          <div style={baseStyles.pane}>
            <div style={baseStyles.paneContent}>
              <EntityDetails entity={currentEntity} type={entityType} />
            </div>
          </div>
          
          {/* Children Pane */}
          {childType && (
            <div style={baseStyles.pane}>
              <EntityList
                entities={childEntities}
                entityType={childType}
                onEntityClick={handleChildClick}
                parentId={entityId}
              />
            </div>
          )}
        </div>
      </div>
    )
  }
  
  // Desktop: Three columns (Parent | Current | Children)
  return (
    <div style={baseStyles.navigator}>
      {/* Breadcrumb */}
      <div style={baseStyles.breadcrumb}>
        <Breadcrumb onItemClick={handleBreadcrumbClick} />
      </div>
      
      <div style={{ ...baseStyles.content, gridTemplateColumns: '280px 1fr 350px' }}>
        {/* Parent Pane */}
        {parentEntity && parentType ? (
          <div style={baseStyles.pane}>
            <div style={baseStyles.paneHeader}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', margin: 0 }}>Parent {parentType}</h3>
              <button
                onClick={handleParentClick}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                View Details →
              </button>
            </div>
            <div style={baseStyles.paneContent}>
              <EntityDetails entity={parentEntity} type={parentType} compact />
              {/* Assignment Display for Parent */}
              <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e5e7eb' }}>
                <AssignmentDisplay 
                  entityType={parentType} 
                  entityId={parentEntity.id}
                  showActions={false}
                />
              </div>
            </div>
          </div>
        ) : (
          <div style={baseStyles.pane}>
            <div style={baseStyles.paneHeader}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', margin: 0 }}>Top Level</h3>
            </div>
            <div style={baseStyles.paneContent}>
              <p className="text-gray-500 text-sm">This is a top-level entity</p>
            </div>
          </div>
        )}
        
        {/* Current Entity Pane */}
        <div style={baseStyles.pane}>
          <div style={baseStyles.paneContent}>
            <EntityDetails entity={currentEntity} type={entityType} />
          </div>
        </div>
        
        {/* Children Pane */}
        {childType ? (
          <div style={baseStyles.pane}>
            <EntityList
              entities={childEntities}
              entityType={childType}
              onEntityClick={handleChildClick}
              parentId={entityId}
            />
          </div>
        ) : (
          <div style={baseStyles.pane}>
            <div style={baseStyles.paneHeader}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', margin: 0 }}>No Children</h3>
            </div>
            <div style={baseStyles.paneContent}>
              <p className="text-gray-500 text-sm">This is a leaf-level entity</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Main component with error boundary
export default function HierarchyNavigator(props: HierarchyNavigatorProps) {
  try {
    return <HierarchyNavigatorInner {...props} />
  } catch (error) {
    console.error('HierarchyNavigator error:', error)
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
        <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-md">
          <div className="text-red-600 text-5xl mb-4">💥</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Component Error</h2>
          <p className="text-gray-600 mb-4">The hierarchy component encountered an error.</p>
          <div className="text-sm text-gray-500 mb-6">
            Error: <span className="font-mono text-red-600">{(error as Error).message}</span>
          </div>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Reload Page
            </button>
            <button
              onClick={() => window.location.href = window.location.pathname + '?debug=true'}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Debug Mode
            </button>
          </div>
        </div>
      </div>
    )
  }
}
