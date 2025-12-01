import { useState, useEffect } from 'react'
import api from '../../services/api'

interface BugSummaryMetrics {
  total_bugs: number
  open_bugs: number
  closed_bugs: number
  resolution_rate: number
  average_resolution_time: number
  by_severity: Record<string, number>
  by_priority: Record<string, number>
  by_status: Record<string, number>
}

interface BugTrendData {
  dates: string[]
  created: number[]
  resolved: number[]
}

interface BugAgingReport {
  age_ranges: Array<{
    range: string
    count: number
    percentage: number
  }>
  average_age_by_severity: Record<string, number>
}

interface TestExecutionMetrics {
  total_executions: number
  passed: number
  failed: number
  blocked: number
  skipped: number
  pass_rate: number
  fail_rate: number
  execution_coverage: number
  total_test_cases?: number
  executed_test_cases?: number
}

interface TestVelocityData {
  dates: string[]
  executions: number[]
}

interface BugMetricsDashboardProps {
  hierarchyFilter?: {
    clientId?: string
    programId?: string
    projectId?: string
    usecaseId?: string
    userStoryId?: string
    taskId?: string
    subtaskId?: string
  }
}

export default function BugMetricsDashboard({ hierarchyFilter }: BugMetricsDashboardProps) {
  const [loading, setLoading] = useState(true)
  const [summaryMetrics, setSummaryMetrics] = useState<BugSummaryMetrics | null>(null)
  const [trendData, setTrendData] = useState<BugTrendData | null>(null)
  const [agingReport, setAgingReport] = useState<BugAgingReport | null>(null)
  const [testMetrics, setTestMetrics] = useState<TestExecutionMetrics | null>(null)
  const [testVelocity, setTestVelocity] = useState<TestVelocityData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadMetrics()
  }, [hierarchyFilter])

  const loadMetrics = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Build hierarchy filter params
      const hierarchyParams: any = {}
      if (hierarchyFilter?.clientId) hierarchyParams.client_id = hierarchyFilter.clientId
      if (hierarchyFilter?.programId) hierarchyParams.program_id = hierarchyFilter.programId
      if (hierarchyFilter?.projectId) hierarchyParams.project_id = hierarchyFilter.projectId
      if (hierarchyFilter?.usecaseId) hierarchyParams.usecase_id = hierarchyFilter.usecaseId
      if (hierarchyFilter?.userStoryId) hierarchyParams.user_story_id = hierarchyFilter.userStoryId
      if (hierarchyFilter?.taskId) hierarchyParams.task_id = hierarchyFilter.taskId
      if (hierarchyFilter?.subtaskId) hierarchyParams.subtask_id = hierarchyFilter.subtaskId
      
      // Fetch all metrics in parallel
      const [summaryData, trendData, agingData, testMetricsData] = await Promise.all([
        api.getBugSummaryMetrics(hierarchyParams),
        api.getBugTrends(undefined, undefined, hierarchyParams),
        api.getBugAgingReport(hierarchyParams),
        api.getTestExecutionMetrics(undefined, hierarchyParams)
      ])
      
      setSummaryMetrics(summaryData)
      setTrendData(trendData)
      setAgingReport(agingData)
      setTestMetrics(testMetricsData)
      
      // Generate test velocity data (last 7 days)
      // In a real implementation, this would come from the API
      const velocityDates = []
      const velocityExecutions = []
      const today = new Date()
      
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(date.getDate() - i)
        velocityDates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))
        // Mock data - in production this would come from API
        velocityExecutions.push(Math.floor(Math.random() * 30) + 20)
      }
      
      setTestVelocity({ dates: velocityDates, executions: velocityExecutions })
      
    } catch (err: any) {
      console.error('Error loading metrics:', err)
      setError(err.message || 'Failed to load metrics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading metrics...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error: {error}</p>
        <button
          onClick={loadMetrics}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Total Bugs"
          value={summaryMetrics?.total_bugs || 0}
          icon="🐛"
          color="blue"
        />
        <MetricCard
          title="Open Bugs"
          value={summaryMetrics?.open_bugs || 0}
          icon="📂"
          color="yellow"
        />
        <MetricCard
          title="Closed Bugs"
          value={summaryMetrics?.closed_bugs || 0}
          icon="✅"
          color="green"
        />
        <MetricCard
          title="Resolution Rate"
          value={`${summaryMetrics?.resolution_rate.toFixed(1) || 0}%`}
          icon="📊"
          color="purple"
        />
        <MetricCard
          title="Avg Resolution Time"
          value={`${summaryMetrics?.average_resolution_time.toFixed(1) || 0} days`}
          icon="⏱️"
          color="indigo"
        />
      </div>

      {/* Charts Row 1: Bug Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bug Distribution by Severity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Bugs by Severity</h3>
          {summaryMetrics && (
            <PieChart
              data={summaryMetrics.by_severity}
              colors={['#ef4444', '#f97316', '#eab308', '#3b82f6', '#6b7280']}
            />
          )}
        </div>

        {/* Bug Distribution by Priority */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Bugs by Priority</h3>
          {summaryMetrics && (
            <PieChart
              data={summaryMetrics.by_priority}
              colors={['#dc2626', '#ea580c', '#ca8a04', '#16a34a']}
            />
          )}
        </div>
      </div>

      {/* Charts Row 2: Trends and Aging */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bug Trend Line Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Bug Trends (Last 7 Days)</h3>
          {trendData && (
            <LineChart
              labels={trendData.dates}
              datasets={[
                { label: 'Created', data: trendData.created, color: '#ef4444' },
                { label: 'Resolved', data: trendData.resolved, color: '#10b981' }
              ]}
            />
          )}
        </div>

        {/* Bug Aging Bar Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Bug Aging Distribution</h3>
          {agingReport && (
            <BarChart
              data={agingReport.age_ranges.map(r => ({
                label: r.range,
                value: r.count
              }))}
              color="#3b82f6"
            />
          )}
        </div>
      </div>

      {/* Test Execution Metrics */}
      {testMetrics && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Test Execution Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <MetricCard
              title="Total Executions"
              value={testMetrics.total_executions}
              icon="🧪"
              color="blue"
              small
            />
            <MetricCard
              title="Pass Rate"
              value={`${testMetrics.pass_rate.toFixed(1)}%`}
              icon="✅"
              color="green"
              small
            />
            <MetricCard
              title="Fail Rate"
              value={`${testMetrics.fail_rate.toFixed(1)}%`}
              icon="❌"
              color="red"
              small
            />
            <MetricCard
              title="Coverage"
              value={`${testMetrics.execution_coverage.toFixed(1)}%`}
              icon="📈"
              color="purple"
              small
            />
          </div>
          
          {/* Test Execution Pass/Fail Pie Chart */}
          <div className="max-w-md mx-auto">
            <PieChart
              data={{
                'Passed': testMetrics.passed,
                'Failed': testMetrics.failed,
                'Blocked': testMetrics.blocked,
                'Skipped': testMetrics.skipped
              }}
              colors={['#10b981', '#ef4444', '#f59e0b', '#6b7280']}
            />
          </div>
          
          {/* Execution Coverage Progress Bar */}
          <div className="mt-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Test Execution Coverage</span>
              <span>{testMetrics.execution_coverage.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="bg-purple-600 h-4 rounded-full transition-all duration-500"
                style={{ width: `${testMetrics.execution_coverage}%` }}
              />
            </div>
            {testMetrics.total_test_cases && (
              <div className="text-sm text-gray-600 mt-2 text-center">
                {testMetrics.executed_test_cases} of {testMetrics.total_test_cases} test cases executed
              </div>
            )}
          </div>
        </div>
      )}

      {/* Test Velocity Trend */}
      {testVelocity && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Test Execution Velocity (Last 7 Days)</h3>
          <LineChart
            labels={testVelocity.dates}
            datasets={[
              { label: 'Executions', data: testVelocity.executions, color: '#8b5cf6' }
            ]}
          />
          <div className="mt-4 text-center text-sm text-gray-600">
            Average: {(testVelocity.executions.reduce((a, b) => a + b, 0) / testVelocity.executions.length).toFixed(1)} executions per day
          </div>
        </div>
      )}

      {/* Bug Status Distribution */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Bugs by Status</h3>
        {summaryMetrics && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(summaryMetrics.by_status).map(([status, count]) => (
              <div key={status} className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-800">{count}</div>
                <div className="text-sm text-gray-600 mt-1">{status}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Average Age by Severity */}
      {agingReport && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Average Bug Age by Severity</h3>
          <div className="space-y-3">
            {Object.entries(agingReport.average_age_by_severity).map(([severity, avgAge]) => (
              <div key={severity} className="flex items-center">
                <div className="w-32 text-sm font-medium text-gray-700">{severity}</div>
                <div className="flex-1">
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-6 mr-3">
                      <div
                        className={`h-6 rounded-full ${getSeverityColor(severity)}`}
                        style={{ width: `${Math.min((avgAge / 60) * 100, 100)}%` }}
                      />
                    </div>
                    <div className="text-sm font-medium text-gray-700 w-20 text-right">
                      {avgAge.toFixed(1)} days
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Helper Components

interface MetricCardProps {
  title: string
  value: string | number
  icon: string
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'indigo'
  small?: boolean
}

function MetricCard({ title, value, icon, color, small }: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    red: 'bg-red-50 text-red-600',
    purple: 'bg-purple-50 text-purple-600',
    indigo: 'bg-indigo-50 text-indigo-600'
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className={`text-sm text-gray-600 ${small ? 'mb-1' : 'mb-2'}`}>{title}</p>
          <p className={`font-bold text-gray-800 ${small ? 'text-xl' : 'text-2xl'}`}>{value}</p>
        </div>
        <div className={`${colorClasses[color]} rounded-full p-3 ${small ? 'text-2xl' : 'text-3xl'}`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

interface PieChartProps {
  data: Record<string, number>
  colors: string[]
}

function PieChart({ data, colors }: PieChartProps) {
  const entries = Object.entries(data)
  const total = entries.reduce((sum, [, value]) => sum + value, 0)
  
  let currentAngle = 0
  const segments = entries.map(([label, value], index) => {
    const percentage = (value / total) * 100
    const angle = (value / total) * 360
    const startAngle = currentAngle
    currentAngle += angle
    
    return {
      label,
      value,
      percentage,
      color: colors[index % colors.length],
      startAngle,
      angle
    }
  })

  return (
    <div className="flex flex-col items-center">
      {/* SVG Pie Chart */}
      <svg viewBox="0 0 200 200" className="w-64 h-64">
        {segments.map((segment, index) => {
          const startAngle = (segment.startAngle - 90) * (Math.PI / 180)
          const endAngle = (segment.startAngle + segment.angle - 90) * (Math.PI / 180)
          
          const x1 = 100 + 80 * Math.cos(startAngle)
          const y1 = 100 + 80 * Math.sin(startAngle)
          const x2 = 100 + 80 * Math.cos(endAngle)
          const y2 = 100 + 80 * Math.sin(endAngle)
          
          const largeArcFlag = segment.angle > 180 ? 1 : 0
          
          const pathData = [
            `M 100 100`,
            `L ${x1} ${y1}`,
            `A 80 80 0 ${largeArcFlag} 1 ${x2} ${y2}`,
            `Z`
          ].join(' ')
          
          return (
            <path
              key={index}
              d={pathData}
              fill={segment.color}
              stroke="white"
              strokeWidth="2"
            />
          )
        })}
      </svg>
      
      {/* Legend */}
      <div className="mt-4 grid grid-cols-2 gap-2 w-full">
        {segments.map((segment, index) => (
          <div key={index} className="flex items-center text-sm">
            <div
              className="w-3 h-3 rounded-full mr-2"
              style={{ backgroundColor: segment.color }}
            />
            <span className="text-gray-700">
              {segment.label}: {segment.value} ({segment.percentage.toFixed(1)}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

interface LineChartProps {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    color: string
  }>
}

function LineChart({ labels, datasets }: LineChartProps) {
  const maxValue = Math.max(...datasets.flatMap(d => d.data))
  const height = 200
  const width = 600
  const padding = 40
  
  const xStep = (width - 2 * padding) / (labels.length - 1)
  const yScale = (height - 2 * padding) / maxValue
  
  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height + 40}`} className="w-full">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((factor, i) => {
          const y = height - padding - (height - 2 * padding) * factor
          return (
            <g key={i}>
              <line
                x1={padding}
                y1={y}
                x2={width - padding}
                y2={y}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
              <text
                x={padding - 10}
                y={y + 5}
                textAnchor="end"
                fontSize="12"
                fill="#6b7280"
              >
                {Math.round(maxValue * factor)}
              </text>
            </g>
          )
        })}
        
        {/* X-axis labels */}
        {labels.map((label, i) => (
          <text
            key={i}
            x={padding + i * xStep}
            y={height + 20}
            textAnchor="middle"
            fontSize="12"
            fill="#6b7280"
          >
            {label}
          </text>
        ))}
        
        {/* Data lines */}
        {datasets.map((dataset, datasetIndex) => {
          const points = dataset.data.map((value, i) => ({
            x: padding + i * xStep,
            y: height - padding - value * yScale
          }))
          
          const pathData = points
            .map((point, i) => `${i === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
            .join(' ')
          
          return (
            <g key={datasetIndex}>
              <path
                d={pathData}
                fill="none"
                stroke={dataset.color}
                strokeWidth="2"
              />
              {points.map((point, i) => (
                <circle
                  key={i}
                  cx={point.x}
                  cy={point.y}
                  r="4"
                  fill={dataset.color}
                />
              ))}
            </g>
          )
        })}
        
        {/* Legend */}
        {datasets.map((dataset, i) => (
          <g key={i} transform={`translate(${width - padding - 150}, ${20 + i * 20})`}>
            <line
              x1={0}
              y1={0}
              x2={20}
              y2={0}
              stroke={dataset.color}
              strokeWidth="2"
            />
            <text x={25} y={5} fontSize="12" fill="#374151">
              {dataset.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  )
}

interface BarChartProps {
  data: Array<{ label: string; value: number }>
  color: string
}

function BarChart({ data, color }: BarChartProps) {
  const maxValue = Math.max(...data.map(d => d.value))
  const height = 200
  const width = 600
  const padding = 40
  
  const barWidth = (width - 2 * padding) / data.length - 10
  const yScale = (height - 2 * padding) / maxValue
  
  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height + 60}`} className="w-full">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((factor, i) => {
          const y = height - padding - (height - 2 * padding) * factor
          return (
            <g key={i}>
              <line
                x1={padding}
                y1={y}
                x2={width - padding}
                y2={y}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
              <text
                x={padding - 10}
                y={y + 5}
                textAnchor="end"
                fontSize="12"
                fill="#6b7280"
              >
                {Math.round(maxValue * factor)}
              </text>
            </g>
          )
        })}
        
        {/* Bars */}
        {data.map((item, i) => {
          const x = padding + i * ((width - 2 * padding) / data.length) + 5
          const barHeight = item.value * yScale
          const y = height - padding - barHeight
          
          return (
            <g key={i}>
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                fill={color}
                rx="4"
              />
              <text
                x={x + barWidth / 2}
                y={y - 5}
                textAnchor="middle"
                fontSize="12"
                fill="#374151"
                fontWeight="bold"
              >
                {item.value}
              </text>
              <text
                x={x + barWidth / 2}
                y={height + 20}
                textAnchor="middle"
                fontSize="12"
                fill="#6b7280"
                transform={`rotate(-45, ${x + barWidth / 2}, ${height + 20})`}
              >
                {item.label}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    'Blocker': 'bg-red-600',
    'Critical': 'bg-orange-500',
    'Major': 'bg-yellow-500',
    'Minor': 'bg-blue-500',
    'Trivial': 'bg-gray-400'
  }
  return colors[severity] || 'bg-gray-400'
}
