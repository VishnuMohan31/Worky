/**
 * Minimal Hierarchy Navigator
 * Stripped down version for testing basic functionality
 */
import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../services/api'

export default function MinimalHierarchyNavigator() {
  // Add CSS for spinner animation
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `
    document.head.appendChild(style)
    return () => {
      if (document.head.contains(style)) {
        document.head.removeChild(style)
      }
    }
  }, [])
  const { type, id } = useParams<{ type: string; id: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      if (!type || !id) {
        setError('Missing type or id parameter')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        
        const response = await api.getEntityWithContext(type, id)
        setData(response)
      } catch (err: any) {
        console.error('Error loading hierarchy:', err)
        setError(err.message || 'Failed to load hierarchy data')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [type, id])

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh',
        backgroundColor: '#f9fafb'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid #e5e7eb',
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{ color: '#6b7280' }}>Loading {type} {id}...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh',
        backgroundColor: '#f9fafb',
        padding: '16px'
      }}>
        <div style={{
          textAlign: 'center',
          padding: '32px',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
          maxWidth: '400px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#1f2937', marginBottom: '8px' }}>
            Error Loading Hierarchy
          </h2>
          <p style={{ color: '#ef4444', marginBottom: '16px' }}>{error}</p>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '24px' }}>
            Entity Type: <span style={{ fontFamily: 'monospace' }}>{type}</span><br />
            Entity ID: <span style={{ fontFamily: 'monospace' }}>{id}</span>
          </div>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '8px 16px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Retry
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Dashboard
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!data || !data.entity) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh',
        backgroundColor: '#f9fafb'
      }}>
        <div style={{ textAlign: 'center', padding: '32px' }}>
          <p style={{ color: '#6b7280' }}>No data found for {type} {id}</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ 
      display: 'grid', 
      gridTemplateRows: 'auto 1fr', 
      height: '100vh',
      backgroundColor: '#f9fafb'
    }}>
      {/* Header */}
      <div style={{ 
        padding: '16px 24px', 
        backgroundColor: 'white', 
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0, color: '#1f2937' }}>
            {data.entity.name || data.entity.title}
          </h1>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '4px 0 0 0' }}>
            {type} • {id}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {data.parent && (
            <button
              onClick={() => {
                // Navigate to parent
                if (type) {
                  const parentType = getParentType(type)
                  if (parentType) {
                    navigate(`/hierarchy/${parentType}/${data.parent.id}`)
                  }
                }
              }}
              style={{
                padding: '6px 12px',
                backgroundColor: '#f3f4f6',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              ↑ Parent
            </button>
          )}
          <button
            onClick={() => navigate('/dashboard')}
            style={{
              padding: '6px 12px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Dashboard
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 2fr 1fr', 
        gap: '16px', 
        padding: '16px',
        overflow: 'hidden'
      }}>
        {/* Parent */}
        <div style={{ 
          backgroundColor: 'white', 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px',
          padding: '16px',
          overflow: 'auto'
        }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '12px' }}>Parent</h3>
          {data.parent ? (
            <div>
              <p><strong>ID:</strong> {data.parent.id}</p>
              <p><strong>Name:</strong> {data.parent.name || data.parent.title}</p>
              <p><strong>Status:</strong> {data.parent.status || 'N/A'}</p>
            </div>
          ) : (
            <p style={{ color: '#6b7280' }}>No parent (top level)</p>
          )}
        </div>

        {/* Current */}
        <div style={{ 
          backgroundColor: 'white', 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px',
          padding: '16px',
          overflow: 'auto'
        }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '12px' }}>Current Entity</h3>
          <div style={{ marginBottom: '16px' }}>
            <p><strong>ID:</strong> {data.entity.id}</p>
            <p><strong>Name:</strong> {data.entity.name || data.entity.title}</p>
            <p><strong>Status:</strong> {data.entity.status || 'N/A'}</p>
            {data.entity.short_description && (
              <p><strong>Description:</strong> {data.entity.short_description}</p>
            )}
          </div>
          
          {/* Breadcrumb */}
          {data.breadcrumb && data.breadcrumb.length > 0 && (
            <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #e5e7eb' }}>
              <h4 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>Path</h4>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>
                {data.breadcrumb.map((item: any, index: number) => (
                  <span key={item.id}>
                    {index > 0 && ' > '}
                    <button
                      onClick={() => navigate(`/hierarchy/${item.type}/${item.id}`)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#3b82f6',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        fontSize: '12px'
                      }}
                    >
                      {item.name}
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Children */}
        <div style={{ 
          backgroundColor: 'white', 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px',
          padding: '16px',
          overflow: 'auto'
        }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '12px' }}>
            Children ({data.children?.length || 0})
          </h3>
          {data.children && data.children.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {data.children.map((child: any) => (
                <div 
                  key={child.id} 
                  style={{ 
                    padding: '8px', 
                    backgroundColor: '#f9fafb', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                  onClick={() => {
                    if (type) {
                      const childType = getChildType(type)
                      if (childType) {
                        navigate(`/hierarchy/${childType}/${child.id}`)
                      }
                    }
                  }}
                >
                  <p style={{ fontSize: '14px', fontWeight: 'bold', margin: 0 }}>
                    {child.name || child.title}
                  </p>
                  <p style={{ fontSize: '12px', color: '#6b7280', margin: '2px 0 0 0' }}>
                    {child.id} • {child.status || 'N/A'}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#6b7280' }}>No children</p>
          )}
        </div>
      </div>
    </div>
  )
}

// Helper functions
function getParentType(type: string): string | null {
  const hierarchy: Record<string, string | null> = {
    client: null,
    program: 'client',
    project: 'program',
    usecase: 'project',
    userstory: 'usecase',
    task: 'userstory',
    subtask: 'task',
    bug: null,
    phase: null,
    user: null,
  }
  return hierarchy[type]
}

function getChildType(type: string): string | null {
  const hierarchy: Record<string, string | null> = {
    client: 'program',
    program: 'project',
    project: 'usecase',
    usecase: 'userstory',
    userstory: 'task',
    task: 'subtask',
    subtask: null,
    bug: null,
    phase: null,
    user: null,
  }
  return hierarchy[type]
}