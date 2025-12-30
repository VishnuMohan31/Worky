/**
 * Simple Hierarchy Navigator for debugging
 * Minimal version to test if the basic functionality works
 */
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../../services/api'

export default function SimpleHierarchyNavigator() {
  const { type, id } = useParams<{ type: string; id: string }>()
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
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading {type} {id}...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center p-8 bg-red-50 rounded-lg max-w-md">
          <div className="text-red-600 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Error Loading Hierarchy</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <div className="text-sm text-gray-500 mb-6">
            Entity Type: <span className="font-mono">{type}</span><br />
            Entity ID: <span className="font-mono">{id}</span>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!data || !data.entity) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center p-8 bg-gray-50 rounded-lg max-w-md">
          <p className="text-gray-600">No data found for {type} {id}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Hierarchy Navigator - Debug Mode</h1>
      
      {/* Breadcrumb */}
      {data.breadcrumb && data.breadcrumb.length > 0 && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Breadcrumb</h2>
          <div className="flex items-center space-x-2">
            {data.breadcrumb.map((item: any, index: number) => (
              <div key={item.id} className="flex items-center">
                {index > 0 && <span className="mx-2 text-gray-400">/</span>}
                <span className="text-blue-600">{item.name}</span>
                <span className="text-xs text-gray-500 ml-1">({item.type})</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Current Entity */}
      <div className="mb-6 p-4 bg-white border rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-2">Current Entity</h2>
        <div className="space-y-2">
          <p><strong>ID:</strong> {data.entity.id}</p>
          <p><strong>Name/Title:</strong> {data.entity.name || data.entity.title}</p>
          <p><strong>Type:</strong> {type}</p>
          <p><strong>Status:</strong> {data.entity.status || 'N/A'}</p>
          {data.entity.short_description && (
            <p><strong>Description:</strong> {data.entity.short_description}</p>
          )}
        </div>
      </div>

      {/* Parent Entity */}
      {data.parent && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Parent Entity</h2>
          <div className="space-y-2">
            <p><strong>ID:</strong> {data.parent.id}</p>
            <p><strong>Name:</strong> {data.parent.name || data.parent.title}</p>
            <p><strong>Status:</strong> {data.parent.status || 'N/A'}</p>
          </div>
        </div>
      )}

      {/* Children */}
      {data.children && data.children.length > 0 && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Children ({data.children.length})</h2>
          <div className="space-y-2">
            {data.children.map((child: any) => (
              <div key={child.id} className="p-2 bg-white rounded border">
                <p><strong>{child.id}:</strong> {child.name || child.title}</p>
                <p className="text-sm text-gray-600">Status: {child.status || 'N/A'}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Raw Data (for debugging) */}
      <details className="mb-6">
        <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
          Show Raw Data (Debug)
        </summary>
        <pre className="mt-2 p-4 bg-gray-100 rounded text-xs overflow-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  )
}