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

interface HierarchyNavigatorProps {
  initialEntityId?: string
  initialEntityType?: EntityType
}

export default function HierarchyNavigator({
  initialEntityId,
  initialEntityType
}: HierarchyNavigatorProps) {
  const { type, id } = useParams<{ type: string; id: string }>()
  const navigate = useNavigate()
  const { isMobile, isTablet, isDesktop } = useResponsive()
  
  const entityType = (type || initialEntityType) as EntityType
  const entityId = id || initialEntityId
  
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
      <div className="hierarchy-navigator">
        <div className="breadcrumb">
          <SkeletonLoader type="list" count={1} />
        </div>
        <div className="hierarchy-content" style={{ padding: '1rem' }}>
          <SkeletonLoader type="details" />
        </div>
      </div>
    )
  }
  
  if (error) {
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
  
  // Mobile: Single pane with tabs
  if (isMobile) {
    return (
      <div className="hierarchy-navigator">
        {/* Breadcrumb */}
        <div className="breadcrumb">
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
        <div className="hierarchy-content">
          {/* Parent Pane */}
          {activeTab === 'parent' && parentEntity && parentType && (
            <div className="context-pane active">
              <div className="pane-header">
                <h3>Parent {parentType}</h3>
                <button
                  onClick={handleParentClick}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  View Details →
                </button>
              </div>
              <div className="main-pane">
                <EntityDetails entity={parentEntity} type={parentType} compact />
              </div>
            </div>
          )}
          
          {/* Current Entity Pane */}
          {activeTab === 'current' && (
            <div className="context-pane main-pane active">
              <div className="main-pane">
                <EntityDetails entity={currentEntity} type={entityType} />
              </div>
            </div>
          )}
          
          {/* Children Pane */}
          {activeTab === 'children' && childType && (
            <div className="context-pane bottom-pane active">
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
      <div className="hierarchy-navigator">
        {/* Breadcrumb */}
        <div className="breadcrumb">
          <Breadcrumb onItemClick={handleBreadcrumbClick} />
        </div>
        
        <div className="hierarchy-content">
          {/* Current Entity Pane */}
          <div className="context-pane main-pane">
            <div className="main-pane">
              <EntityDetails entity={currentEntity} type={entityType} />
            </div>
          </div>
          
          {/* Children Pane */}
          {childType && (
            <div className="context-pane bottom-pane">
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
    <div className="hierarchy-navigator">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <Breadcrumb onItemClick={handleBreadcrumbClick} />
      </div>
      
      <div className="hierarchy-content">
        {/* Parent Pane */}
        {parentEntity && parentType ? (
          <div className="context-pane top-pane">
            <div className="pane-header">
              <h3>Parent {parentType}</h3>
              <button
                onClick={handleParentClick}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                View Details →
              </button>
            </div>
            <div className="entity-list">
              <EntityDetails entity={parentEntity} type={parentType} compact />
            </div>
          </div>
        ) : (
          <div className="context-pane top-pane">
            <div className="pane-header">
              <h3>Top Level</h3>
            </div>
            <div className="entity-list">
              <p className="text-gray-500 text-sm p-4">This is a top-level entity</p>
            </div>
          </div>
        )}
        
        {/* Current Entity Pane */}
        <div className="context-pane main-pane">
          <div className="main-pane">
            <EntityDetails entity={currentEntity} type={entityType} />
          </div>
        </div>
        
        {/* Children Pane */}
        {childType ? (
          <div className="context-pane bottom-pane">
            <EntityList
              entities={childEntities}
              entityType={childType}
              onEntityClick={handleChildClick}
              parentId={entityId}
            />
          </div>
        ) : (
          <div className="context-pane bottom-pane">
            <div className="pane-header">
              <h3>No Children</h3>
            </div>
            <div className="entity-list">
              <p className="text-gray-500 text-sm p-4">This is a leaf-level entity</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
