/**
 * Breadcrumb Component
 * Displays full hierarchy path from Client to current entity
 */
import { useHierarchyStore, getEntityDisplayName } from '../../stores/hierarchyStore'

interface BreadcrumbProps {
  onItemClick?: (item: any) => void
}

export default function Breadcrumb({ onItemClick }: BreadcrumbProps) {
  const { breadcrumb } = useHierarchyStore()
  
  if (!breadcrumb || breadcrumb.length === 0) {
    return null
  }
  
  return (
    <nav className="flex items-center space-x-2 text-sm" aria-label="Breadcrumb">
      <svg
        className="w-4 h-4 text-gray-400"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
      
      {breadcrumb.map((item, index) => {
        const isLast = index === breadcrumb.length - 1
        const displayName = item.name.length > 30 
          ? item.name.substring(0, 30) + '...' 
          : item.name
        
        return (
          <div key={item.id} className="flex items-center space-x-2">
            {index > 0 && (
              <svg
                className="w-4 h-4 text-gray-400"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M9 5l7 7-7 7" />
              </svg>
            )}
            
            {isLast ? (
              <span className="font-semibold text-gray-900" title={item.name}>
                {displayName}
              </span>
            ) : (
              <button
                onClick={() => onItemClick?.(item)}
                className="text-blue-600 hover:text-blue-700 hover:underline transition-colors"
                title={item.name}
              >
                {displayName}
              </button>
            )}
            
            {!isLast && (
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                {getEntityDisplayName(item.type as any)}
              </span>
            )}
          </div>
        )
      })}
    </nav>
  )
}
