/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree
 */
import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to console
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo
    })
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default fallback UI
      return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
          <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-lg">
            <div className="text-red-600 text-5xl mb-4">💥</div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Something went wrong</h2>
            <p className="text-gray-600 mb-4">
              The application encountered an unexpected error.
            </p>
            
            {this.state.error && (
              <div className="text-left mb-4 p-3 bg-gray-100 rounded text-sm">
                <p className="font-semibold text-red-600 mb-2">Error Details:</p>
                <p className="font-mono text-xs text-gray-700 break-all">
                  {this.state.error.message}
                </p>
              </div>
            )}
            
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Reload Page
              </button>
              <button
                onClick={() => window.history.back()}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Go Back
              </button>
            </div>
            
            {/* Debug info (only in development) */}
            {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
              <details className="mt-4 text-left">
                <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
                  Show Stack Trace (Development)
                </summary>
                <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-auto max-h-40">
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary