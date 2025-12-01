/**
 * DataTable Component
 * Displays tabular data for list results in chat responses
 * Requirements: 8.2, 8.5
 */

import { useState } from 'react'

export interface DataTableData {
  columns: string[]
  rows: any[][]
  total_count: number
  has_more?: boolean
}

interface DataTableProps {
  data: DataTableData
  onLoadMore?: () => void
}

export default function DataTable({ data, onLoadMore }: DataTableProps) {
  const [sortColumn, setSortColumn] = useState<number | null>(null)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')

  const handleSort = (columnIndex: number) => {
    if (sortColumn === columnIndex) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(columnIndex)
      setSortDirection('asc')
    }
  }

  const getSortedRows = () => {
    if (sortColumn === null) return data.rows

    return [...data.rows].sort((a, b) => {
      const aVal = a[sortColumn]
      const bVal = b[sortColumn]

      // Handle null/undefined values
      if (aVal == null && bVal == null) return 0
      if (aVal == null) return sortDirection === 'asc' ? 1 : -1
      if (bVal == null) return sortDirection === 'asc' ? -1 : 1

      // Compare values
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
      }

      const aStr = String(aVal).toLowerCase()
      const bStr = String(bVal).toLowerCase()
      
      if (sortDirection === 'asc') {
        return aStr.localeCompare(bStr)
      } else {
        return bStr.localeCompare(aStr)
      }
    })
  }

  const formatCellValue = (value: any): string => {
    if (value == null) return '-'
    if (typeof value === 'boolean') return value ? 'Yes' : 'No'
    if (typeof value === 'object') return JSON.stringify(value)
    return String(value)
  }

  const getCellClassName = (value: any, columnName: string): string => {
    const baseClass = 'data-table-cell'
    
    // Status column styling
    if (columnName.toLowerCase().includes('status')) {
      const statusLower = String(value).toLowerCase()
      if (statusLower.includes('done') || statusLower.includes('completed') || statusLower.includes('closed')) {
        return `${baseClass} data-table-cell-success`
      }
      if (statusLower.includes('progress')) {
        return `${baseClass} data-table-cell-info`
      }
      if (statusLower.includes('blocked') || statusLower.includes('failed')) {
        return `${baseClass} data-table-cell-danger`
      }
      if (statusLower.includes('hold') || statusLower.includes('pending')) {
        return `${baseClass} data-table-cell-warning`
      }
    }

    // Priority column styling
    if (columnName.toLowerCase().includes('priority')) {
      const priorityLower = String(value).toLowerCase()
      if (priorityLower.includes('critical') || priorityLower === 'p0' || priorityLower === 'high') {
        return `${baseClass} data-table-cell-danger`
      }
      if (priorityLower === 'p1' || priorityLower === 'medium') {
        return `${baseClass} data-table-cell-warning`
      }
    }

    return baseClass
  }

  const sortedRows = getSortedRows()

  if (data.rows.length === 0) {
    return (
      <div className="data-table-empty">
        <svg className="w-12 h-12 text-gray-300" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p>No data to display</p>
      </div>
    )
  }

  return (
    <div className="data-table-container">
      <div className="data-table-wrapper">
        <table className="data-table">
          <thead className="data-table-header">
            <tr>
              {data.columns.map((column, index) => (
                <th
                  key={index}
                  className="data-table-header-cell"
                  onClick={() => handleSort(index)}
                >
                  <div className="data-table-header-content">
                    <span>{column}</span>
                    {sortColumn === index && (
                      <svg
                        className={`w-4 h-4 transition-transform ${
                          sortDirection === 'desc' ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path d="M5 15l7-7 7 7" />
                      </svg>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="data-table-body">
            {sortedRows.map((row, rowIndex) => (
              <tr key={rowIndex} className="data-table-row">
                {row.map((cell, cellIndex) => (
                  <td
                    key={cellIndex}
                    className={getCellClassName(cell, data.columns[cellIndex])}
                  >
                    {formatCellValue(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer with count and load more */}
      <div className="data-table-footer">
        <div className="data-table-count">
          Showing {data.rows.length} of {data.total_count} results
        </div>
        
        {data.has_more && onLoadMore && (
          <button
            onClick={onLoadMore}
            className="data-table-load-more"
          >
            Load more
            <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
}
