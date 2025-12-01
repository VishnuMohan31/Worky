/**
 * ChartVisualization Component
 * Renders charts and visualizations for aggregate data
 * Requirements: 8.4
 */

import { useState } from 'react'

export interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    color?: string
  }>
  title?: string
  type?: 'bar' | 'pie' | 'line'
}

interface ChartVisualizationProps {
  data: ChartData
}

export default function ChartVisualization({ data }: ChartVisualizationProps) {
  const [chartType, setChartType] = useState<'bar' | 'pie' | 'line'>(data.type || 'bar')

  const colors = [
    '#667eea',
    '#10b981',
    '#f59e0b',
    '#ef4444',
    '#8b5cf6',
    '#ec4899',
    '#06b6d4',
    '#84cc16'
  ]

  const getColor = (index: number, customColor?: string): string => {
    return customColor || colors[index % colors.length]
  }

  const renderBarChart = () => {
    const maxValue = Math.max(
      ...data.datasets.flatMap(dataset => dataset.data)
    )

    return (
      <div className="chart-bar-container" style={{ width: '100%', height: '200px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', height: '100%', gap: '8px' }}>
          {data.labels.map((label, index) => {
            const values = data.datasets.map(dataset => dataset.data[index] || 0)
            const total = values.reduce((sum, val) => sum + val, 0)
            const percentage = maxValue > 0 ? (total / maxValue) * 100 : 0

            return (
              <div
                key={index}
                style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <div
                  style={{
                    width: '100%',
                    height: `${percentage}%`,
                    minHeight: total > 0 ? '20px' : '0',
                    background: getColor(index, data.datasets[0]?.color),
                    borderRadius: '4px 4px 0 0',
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'center',
                    padding: '4px',
                    fontSize: '11px',
                    fontWeight: '600',
                    color: 'white',
                    transition: 'all 0.3s ease'
                  }}
                  title={`${label}: ${total}`}
                >
                  {total > 0 && total}
                </div>
                <div
                  style={{
                    fontSize: '11px',
                    color: '#6b7280',
                    textAlign: 'center',
                    wordBreak: 'break-word',
                    maxWidth: '100%'
                  }}
                >
                  {label}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  const renderPieChart = () => {
    const total = data.datasets[0]?.data.reduce((sum, val) => sum + val, 0) || 0
    
    if (total === 0) {
      return (
        <div className="chart-empty">
          <p>No data to display</p>
        </div>
      )
    }

    let currentAngle = 0
    const segments = data.labels.map((label, index) => {
      const value = data.datasets[0]?.data[index] || 0
      const percentage = (value / total) * 100
      const angle = (value / total) * 360
      const startAngle = currentAngle
      currentAngle += angle

      return {
        label,
        value,
        percentage,
        startAngle,
        angle,
        color: getColor(index, data.datasets[0]?.color)
      }
    })

    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
        <div style={{ position: 'relative', width: '180px', height: '180px' }}>
          <svg width="180" height="180" viewBox="0 0 180 180">
            {segments.map((segment, index) => {
              const startAngle = (segment.startAngle - 90) * (Math.PI / 180)
              const endAngle = (segment.startAngle + segment.angle - 90) * (Math.PI / 180)
              
              const x1 = 90 + 80 * Math.cos(startAngle)
              const y1 = 90 + 80 * Math.sin(startAngle)
              const x2 = 90 + 80 * Math.cos(endAngle)
              const y2 = 90 + 80 * Math.sin(endAngle)
              
              const largeArc = segment.angle > 180 ? 1 : 0
              
              const pathData = [
                `M 90 90`,
                `L ${x1} ${y1}`,
                `A 80 80 0 ${largeArc} 1 ${x2} ${y2}`,
                `Z`
              ].join(' ')

              return (
                <g key={index}>
                  <path
                    d={pathData}
                    fill={segment.color}
                    stroke="white"
                    strokeWidth="2"
                  />
                  <title>{`${segment.label}: ${segment.value} (${segment.percentage.toFixed(1)}%)`}</title>
                </g>
              )
            })}
            <circle cx="90" cy="90" r="40" fill="white" />
            <text
              x="90"
              y="90"
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="20"
              fontWeight="600"
              fill="#1f2937"
            >
              {total}
            </text>
          </svg>
        </div>
        
        <div className="chart-legend">
          {segments.map((segment, index) => (
            <div key={index} className="chart-legend-item">
              <div
                className="chart-legend-color"
                style={{ background: segment.color }}
              />
              <span>
                {segment.label}: {segment.value} ({segment.percentage.toFixed(1)}%)
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderLineChart = () => {
    const maxValue = Math.max(
      ...data.datasets.flatMap(dataset => dataset.data)
    )
    const minValue = Math.min(
      ...data.datasets.flatMap(dataset => dataset.data)
    )
    const range = maxValue - minValue || 1

    const width = 300
    const height = 180
    const padding = 20
    const chartWidth = width - padding * 2
    const chartHeight = height - padding * 2

    return (
      <div style={{ width: '100%', maxWidth: '400px' }}>
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, index) => {
            const y = padding + chartHeight * (1 - ratio)
            return (
              <line
                key={index}
                x1={padding}
                y1={y}
                x2={width - padding}
                y2={y}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            )
          })}

          {/* Data lines */}
          {data.datasets.map((dataset, datasetIndex) => {
            const points = dataset.data.map((value, index) => {
              const x = padding + (chartWidth / (data.labels.length - 1)) * index
              const y = padding + chartHeight * (1 - (value - minValue) / range)
              return `${x},${y}`
            }).join(' ')

            const color = getColor(datasetIndex, dataset.color)

            return (
              <g key={datasetIndex}>
                <polyline
                  points={points}
                  fill="none"
                  stroke={color}
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                {dataset.data.map((value, index) => {
                  const x = padding + (chartWidth / (data.labels.length - 1)) * index
                  const y = padding + chartHeight * (1 - (value - minValue) / range)
                  return (
                    <circle
                      key={index}
                      cx={x}
                      cy={y}
                      r="4"
                      fill={color}
                      stroke="white"
                      strokeWidth="2"
                    >
                      <title>{`${data.labels[index]}: ${value}`}</title>
                    </circle>
                  )
                })}
              </g>
            )
          })}

          {/* X-axis labels */}
          {data.labels.map((label, index) => {
            const x = padding + (chartWidth / (data.labels.length - 1)) * index
            return (
              <text
                key={index}
                x={x}
                y={height - 5}
                textAnchor="middle"
                fontSize="10"
                fill="#6b7280"
              >
                {label}
              </text>
            )
          })}
        </svg>

        {data.datasets.length > 1 && (
          <div className="chart-legend">
            {data.datasets.map((dataset, index) => (
              <div key={index} className="chart-legend-item">
                <div
                  className="chart-legend-color"
                  style={{ background: getColor(index, dataset.color) }}
                />
                <span>{dataset.label}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  const renderChart = () => {
    if (!data.labels || data.labels.length === 0) {
      return (
        <div className="chart-empty">
          <svg className="w-12 h-12 text-gray-300" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p>No data to display</p>
        </div>
      )
    }

    switch (chartType) {
      case 'bar':
        return renderBarChart()
      case 'pie':
        return renderPieChart()
      case 'line':
        return renderLineChart()
      default:
        return renderBarChart()
    }
  }

  return (
    <div className="chart-container">
      <div className="chart-header">
        <h4 className="chart-title">{data.title || 'Chart'}</h4>
        <div className="chart-type-selector">
          <button
            className={`chart-type-button ${chartType === 'bar' ? 'active' : ''}`}
            onClick={() => setChartType('bar')}
            title="Bar Chart"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
            </svg>
          </button>
          <button
            className={`chart-type-button ${chartType === 'pie' ? 'active' : ''}`}
            onClick={() => setChartType('pie')}
            title="Pie Chart"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
              <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
            </svg>
          </button>
          <button
            className={`chart-type-button ${chartType === 'line' ? 'active' : ''}`}
            onClick={() => setChartType('line')}
            title="Line Chart"
          >
            <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
          </button>
        </div>
      </div>
      
      <div className="chart-body">
        {renderChart()}
      </div>
    </div>
  )
}
