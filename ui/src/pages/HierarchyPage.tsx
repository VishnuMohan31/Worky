/**
 * Hierarchy Page
 * Wrapper page for HierarchyNavigator component
 */
import { useState, useEffect } from 'react'
import HierarchyNavigator from '../components/hierarchy/HierarchyNavigator'
import SimpleHierarchyNavigator from '../components/hierarchy/SimpleHierarchyNavigator'
import MinimalHierarchyNavigator from '../components/hierarchy/MinimalHierarchyNavigator'
import ErrorBoundary from '../components/common/ErrorBoundary'

export default function HierarchyPage() {
  const [hasError, setHasError] = useState(false)
  
  // Check URL parameters for debug modes
  const urlParams = new URLSearchParams(window.location.search)
  const debugMode = urlParams.get('debug')
  const minimalMode = urlParams.get('minimal') === 'true'
  
  // Error boundary fallback
  const ErrorFallback = () => (
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
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>💥</div>
        <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#1f2937', marginBottom: '8px' }}>
          Component Error
        </h2>
        <p style={{ color: '#6b7280', marginBottom: '16px' }}>
          The hierarchy component encountered an error. Try the minimal version.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            onClick={() => window.location.href = window.location.pathname + '?minimal=true'}
            style={{
              padding: '8px 16px',
              backgroundColor: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            Minimal Mode
          </button>
          <button
            onClick={() => window.location.href = window.location.pathname + '?debug=true'}
            style={{
              padding: '8px 16px',
              backgroundColor: '#f59e0b',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            Debug Mode
          </button>
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
            Reload
          </button>
        </div>
      </div>
    </div>
  )
  
  // Choose component based on mode
  if (minimalMode) {
    return <MinimalHierarchyNavigator />
  }
  
  if (debugMode === 'true') {
    return <SimpleHierarchyNavigator />
  }
  
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <HierarchyNavigator />
    </ErrorBoundary>
  )
}
