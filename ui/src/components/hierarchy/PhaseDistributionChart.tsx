/**
 * PhaseDistributionChart Component
 * Displays phase distribution using a pie chart with click handlers for filtering
 */
import { useState } from 'react'

// Fallback chart without recharts to avoid compatibility issues
let PieChart: any, Pie: any, Cell: any, ResponsiveContainer: any, Legend: any, Tooltip: any

try {
  const recharts = require('recharts')
  PieChart = recharts.PieChart
  Pie = recharts.Pie
  Cell = recharts.Cell
  ResponsiveContainer = recharts.ResponsiveContainer
  Legend = recharts.Legend
  Tooltip = recharts.Tooltip
} catch (error) {
  console.warn('Recharts not available, using fallback chart')
}

interface PhaseData {
  phase: string
  count: number
}

interface PhaseDistributionChartProps {
  data: PhaseData[]
  onPhaseClick?: (phase: string) => void
}

// Default phase colors matching the design document
const PHASE_COLORS: Record<string, string> = {
  'Development': '#3498db',
  'Analysis': '#9b59b6',
  'Design': '#e67e22',
  'Testing': '#1abc9c'
}

export default function PhaseDistributionChart({ data, onPhaseClick }: PhaseDistributionChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No phase data available
      </div>
    )
  }

  const handlePieClick = (entry: PhaseData, index: number) => {
    setActiveIndex(index)
    if (onPhaseClick) {
      onPhaseClick(entry.phase)
    }
  }

  const totalCount = data.reduce((sum, item) => sum + item.count, 0)

  // If recharts is not available, show a simple bar chart
  if (!PieChart || !ResponsiveContainer) {
    return (
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-900">Phase Distribution</h4>
        
        {/* Simple Bar Chart */}
        <div className="space-y-3">
          {data.map((item, index) => {
            const percentage = ((item.count / totalCount) * 100).toFixed(1)
            return (
              <div
                key={item.phase}
                className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
                  activeIndex === index
                    ? 'border-gray-400 bg-gray-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handlePieClick(item, index)}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: PHASE_COLORS[item.phase] || '#95a5a6' }}
                    />
                    <span className="font-medium text-gray-700">{item.phase}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-lg font-bold text-gray-900">{item.count}</span>
                    <span className="text-sm text-gray-500 ml-2">({percentage}%)</span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${percentage}%`,
                      backgroundColor: PHASE_COLORS[item.phase] || '#95a5a6'
                    }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Total Count */}
        <div className="text-center pt-4 border-t">
          <p className="text-sm text-gray-600">Total Items</p>
          <p className="text-3xl font-bold text-gray-900">{totalCount}</p>
        </div>

        {onPhaseClick && (
          <div className="text-center text-sm text-gray-500">
            Click on a phase to filter by that phase
          </div>
        )}
      </div>
    )
  }

  // Recharts version (if available)
  const renderCustomLabel = (entry: any) => {
    const percent = ((entry.value / totalCount) * 100).toFixed(1)
    return `${entry.name}: ${entry.value} (${percent}%)`
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0]
      const percent = ((data.value / totalCount) * 100).toFixed(1)
      
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="font-semibold text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">Count: {data.value}</p>
          <p className="text-sm text-gray-600">Percentage: {percent}%</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {data.map((item, index) => (
          <div
            key={item.phase}
            className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
              activeIndex === index
                ? 'border-gray-400 bg-gray-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => handlePieClick(item, index)}
          >
            <div className="flex items-center gap-2 mb-1">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: PHASE_COLORS[item.phase] || '#95a5a6' }}
              />
              <span className="text-xs font-medium text-gray-600">{item.phase}</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{item.count}</div>
            <div className="text-xs text-gray-500">
              {((item.count / totalCount) * 100).toFixed(1)}%
            </div>
          </div>
        ))}
      </div>

      {/* Pie Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="phase"
              cx="50%"
              cy="50%"
              outerRadius={100}
              innerRadius={60}
              paddingAngle={2}
              onClick={(entry, index) => handlePieClick(entry, index)}
              label={renderCustomLabel}
              labelLine={true}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={PHASE_COLORS[entry.phase] || '#95a5a6'}
                  stroke={activeIndex === index ? '#000' : '#fff'}
                  strokeWidth={activeIndex === index ? 2 : 1}
                  style={{
                    cursor: 'pointer',
                    opacity: activeIndex === null || activeIndex === index ? 1 : 0.6,
                    transition: 'opacity 0.3s'
                  }}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="bottom"
              height={36}
              iconType="circle"
              formatter={(value, entry: any) => {
                const item = data.find(d => d.phase === value)
                return `${value} (${item?.count || 0})`
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Total Count */}
      <div className="text-center pt-4 border-t">
        <p className="text-sm text-gray-600">Total Items</p>
        <p className="text-3xl font-bold text-gray-900">{totalCount}</p>
      </div>

      {onPhaseClick && (
        <div className="text-center text-sm text-gray-500">
          Click on a phase to filter by that phase
        </div>
      )}
    </div>
  )
}
