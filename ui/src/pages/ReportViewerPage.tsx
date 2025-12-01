/**
 * Report Viewer Page
 * Generic page for viewing and downloading reports with filters
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'

interface ReportConfig {
  title: string
  icon: string
  description: string
  filters: FilterConfig[]
  endpoint: string
}

interface FilterConfig {
  name: string
  label: string
  type: 'date' | 'select' | 'number'
  options?: { value: string; label: string }[]
  required?: boolean
  default?: any
}

const reportConfigs: Record<string, ReportConfig> = {
  'utilization': {
    title: 'Utilization Report',
    icon: '📊',
    description: 'Resource allocation vs actual usage analysis',
    endpoint: 'utilization',
    filters: [
      { name: 'start_date', label: 'Start Date', type: 'date', required: true },
      { name: 'end_date', label: 'End Date', type: 'date', required: true }
    ]
  },
  'engagement': {
    title: 'Engagement Report',
    icon: '📈',
    description: 'Developer activity and contribution metrics',
    endpoint: 'engagement',
    filters: [
      { name: 'start_date', label: 'Start Date', type: 'date', required: true },
      { name: 'end_date', label: 'End Date', type: 'date', required: true }
    ]
  },
  'occupancy-forecast': {
    title: 'Occupancy Forecast',
    icon: '📅',
    description: 'Time booking predictions for upcoming periods',
    endpoint: 'occupancy-forecast',
    filters: [
      { name: 'weeks_ahead', label: 'Weeks Ahead', type: 'number', default: 4, required: true }
    ]
  },
  'bug-density': {
    title: 'Bug Density Report',
    icon: '🐛',
    description: 'Bug trends and resolution metrics by project',
    endpoint: 'bug-density',
    filters: [
      { name: 'project_id', label: 'Project', type: 'select', options: [] }
    ]
  },
  'sprint-velocity': {
    title: 'Sprint Velocity',
    icon: '🏃',
    description: 'Team velocity and sprint completion trends',
    endpoint: 'sprint-velocity',
    filters: [
      { name: 'project_id', label: 'Project', type: 'select', options: [] },
      { name: 'sprint_count', label: 'Number of Sprints', type: 'number', default: 10 }
    ]
  },
  'project-health': {
    title: 'Project Health',
    icon: '💚',
    description: 'Overall project status and risk assessment',
    endpoint: 'project-health',
    filters: [
      { name: 'project_id', label: 'Project', type: 'select', options: [] }
    ]
  },
  'project-tree': {
    title: 'Project Tree',
    icon: '🌳',
    description: 'Hierarchical view of project structure',
    endpoint: 'project-tree',
    filters: [
      { name: 'project_id', label: 'Project', type: 'select', options: [], required: true }
    ]
  }
}

export default function ReportViewerPage() {
  const { reportType } = useParams<{ reportType: string }>()
  const navigate = useNavigate()
  
  const config = reportType ? reportConfigs[reportType] : null
  
  const [filters, setFilters] = useState<Record<string, any>>({})
  const [reportData, setReportData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [projects, setProjects] = useState<any[]>([])
  
  // Load projects for project filter
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const projectsData = await api.getProjects()
        setProjects(projectsData)
        
        // Update filter options
        if (config) {
          config.filters.forEach(filter => {
            if (filter.name === 'project_id') {
              filter.options = projectsData.map((p: any) => ({
                value: p.id,
                label: p.name
              }))
            }
          })
        }
      } catch (err) {
        console.error('Failed to load projects:', err)
      }
    }
    
    loadProjects()
  }, [config])
  
  // Set default filter values
  useEffect(() => {
    if (config) {
      const defaults: Record<string, any> = {}
      
      config.filters.forEach(filter => {
        if (filter.type === 'date') {
          if (filter.name === 'end_date') {
            defaults[filter.name] = new Date().toISOString().split('T')[0]
          } else if (filter.name === 'start_date') {
            const date = new Date()
            date.setDate(date.getDate() - 30)
            defaults[filter.name] = date.toISOString().split('T')[0]
          }
        } else if (filter.default !== undefined) {
          defaults[filter.name] = filter.default
        }
      })
      
      setFilters(defaults)
    }
  }, [config])
  
  if (!config) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Report Not Found</h2>
          <button
            onClick={() => navigate('/reports')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Reports
          </button>
        </div>
      </div>
    )
  }
  
  const handleFilterChange = (name: string, value: any) => {
    setFilters(prev => ({ ...prev, [name]: value }))
  }
  
  const handleGenerateReport = async () => {
    // Validate required filters
    const missingFilters = config.filters
      .filter(f => f.required && !filters[f.name])
      .map(f => f.label)
    
    if (missingFilters.length > 0) {
      setError(`Please fill in required fields: ${missingFilters.join(', ')}`)
      return
    }
    
    setLoading(true)
    setError('')
    
    try {
      // Build query params
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value.toString())
        }
      })
      
      // Fetch report data (without format param to get JSON)
      const response = await fetch(`/api/v1/reports/${config.endpoint}?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to generate report')
      }
      
      const data = await response.json()
      setReportData(data)
    } catch (err: any) {
      setError(err.message || 'Failed to generate report')
    } finally {
      setLoading(false)
    }
  }
  
  const handleDownload = async (format: 'pdf' | 'csv') => {
    if (!reportData) return
    
    try {
      // Build query params
      const params = new URLSearchParams()
      params.append('format', format)
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value.toString())
        }
      })
      
      // Download file
      const url = `/api/v1/reports/${config.endpoint}?${params}`
      window.open(url, '_blank')
    } catch (err: any) {
      setError(err.message || 'Failed to download report')
    }
  }
  
  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/reports')}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to Reports
          </button>
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <span>{config.icon}</span>
              <span>{config.title}</span>
            </h1>
            <p className="text-gray-600 mt-1">{config.description}</p>
          </div>
        </div>
      </div>
      
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Report Filters</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          {config.filters.map(filter => (
            <div key={filter.name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {filter.label} {filter.required && <span className="text-red-500">*</span>}
              </label>
              
              {filter.type === 'date' && (
                <input
                  type="date"
                  value={filters[filter.name] || ''}
                  onChange={(e) => handleFilterChange(filter.name, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              )}
              
              {filter.type === 'number' && (
                <input
                  type="number"
                  value={filters[filter.name] || ''}
                  onChange={(e) => handleFilterChange(filter.name, parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                />
              )}
              
              {filter.type === 'select' && (
                <select
                  value={filters[filter.name] || ''}
                  onChange={(e) => handleFilterChange(filter.name, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All {filter.label}s</option>
                  {filter.options?.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              )}
            </div>
          ))}
        </div>
        
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}
        
        <button
          onClick={handleGenerateReport}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>
      
      {/* Report Display */}
      {reportData && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold">{reportData.title}</h2>
              <p className="text-sm text-gray-600">
                Period: {reportData.period} | Generated: {reportData.generated_at}
              </p>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => handleDownload('pdf')}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
              >
                📄 Download PDF
              </button>
              <button
                onClick={() => handleDownload('csv')}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                📊 Download CSV
              </button>
            </div>
          </div>
          
          {/* Report Table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {reportData.headers.map((header: string, index: number) => (
                    <th
                      key={index}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reportData.rows.map((row: any[], rowIndex: number) => (
                  <tr key={rowIndex} className="hover:bg-gray-50">
                    {row.map((cell: any, cellIndex: number) => (
                      <td
                        key={cellIndex}
                        className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {reportData.rows.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No data available for the selected filters
            </div>
          )}
        </div>
      )}
      
      {!reportData && !loading && (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <p className="text-gray-600">
            Select your filters above and click "Generate Report" to view the data
          </p>
        </div>
      )}
    </div>
  )
}
