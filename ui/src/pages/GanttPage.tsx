import { useEffect, useState, useMemo } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../services/api'

interface Task {
  id: string
  title: string
  startDate?: string
  dueDate?: string
  assignedToName?: string
  status: string
  progress?: number
}

export default function GanttPage() {
  const { t } = useLanguage()
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'month' | 'week'>('month')

  useEffect(() => {
    loadTasks()
  }, [])

  const loadTasks = async () => {
    try {
      const data = await api.getTasks()
      // Add default dates if missing
      const tasksWithDates = data.map((task: any) => ({
        ...task,
        startDate: task.startDate || new Date().toISOString().split('T')[0],
        dueDate: task.dueDate || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      }))
      setTasks(tasksWithDates)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  // Calculate timeline range
  const { startDate, endDate, timelineMonths, timelineWeeks } = useMemo(() => {
    if (tasks.length === 0) {
      const today = new Date()
      return {
        startDate: today,
        endDate: new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000),
        timelineMonths: [],
        timelineWeeks: []
      }
    }

    const dates = tasks.flatMap(t => [
      new Date(t.startDate || Date.now()),
      new Date(t.dueDate || Date.now())
    ])
    
    const minDate = new Date(Math.min(...dates.map(d => d.getTime())))
    const maxDate = new Date(Math.max(...dates.map(d => d.getTime())))
    
    // Add padding
    minDate.setDate(minDate.getDate() - 7)
    maxDate.setDate(maxDate.getDate() + 7)
    
    // Generate months
    const months: { month: string; year: number; weeks: number }[] = []
    const current = new Date(minDate)
    current.setDate(1)
    
    while (current <= maxDate) {
      const daysInMonth = new Date(current.getFullYear(), current.getMonth() + 1, 0).getDate()
      months.push({
        month: current.toLocaleString('default', { month: 'short' }),
        year: current.getFullYear(),
        weeks: Math.ceil(daysInMonth / 7)
      })
      current.setMonth(current.getMonth() + 1)
    }
    
    // Generate weeks
    const weeks: Date[] = []
    const weekCurrent = new Date(minDate)
    weekCurrent.setDate(weekCurrent.getDate() - weekCurrent.getDay()) // Start of week
    
    while (weekCurrent <= maxDate) {
      weeks.push(new Date(weekCurrent))
      weekCurrent.setDate(weekCurrent.getDate() + 7)
    }
    
    return {
      startDate: minDate,
      endDate: maxDate,
      timelineMonths: months,
      timelineWeeks: weeks
    }
  }, [tasks])

  // Calculate task bar position and width
  const getTaskBarStyle = (task: Task) => {
    const taskStart = new Date(task.startDate || Date.now())
    const taskEnd = new Date(task.dueDate || Date.now())
    const totalDays = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
    const startOffset = (taskStart.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
    const duration = (taskEnd.getTime() - taskStart.getTime()) / (1000 * 60 * 60 * 24)
    
    const left = (startOffset / totalDays) * 100
    const width = (duration / totalDays) * 100
    
    return {
      left: `${Math.max(0, left)}%`,
      width: `${Math.max(2, width)}%`
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'To Do': '#94a3b8',
      'In Progress': '#3b82f6',
      'Done': '#22c55e',
      'Blocked': '#ef4444'
    }
    return colors[status] || '#94a3b8'
  }

  const exportToPDF = () => {
    alert('Export to PDF functionality - will use jsPDF library')
  }

  const exportToPNG = () => {
    alert('Export to PNG functionality - will use html2canvas library')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const totalWeeks = timelineMonths.reduce((sum, m) => sum + m.weeks, 0)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gantt Chart 📈</h1>
          <p className="text-gray-600 mt-1">Project timeline and task scheduling</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('month')}
            className={`px-4 py-2 rounded-md transition-colors ${
              viewMode === 'month'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Month View
          </button>
          <button
            onClick={() => setViewMode('week')}
            className={`px-4 py-2 rounded-md transition-colors ${
              viewMode === 'week'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Week View
          </button>
          <button
            onClick={exportToPDF}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            📄 Export PDF
          </button>
          <button
            onClick={exportToPNG}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
          >
            🖼️ Export PNG
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <div style={{ minWidth: '1200px' }}>
            {/* Timeline Header */}
            <div className="flex border-b-2 border-gray-300 bg-gray-50">
              {/* Task Name Column */}
              <div className="w-64 flex-shrink-0 border-r-2 border-gray-300">
                <div className="px-4 py-3 font-semibold text-gray-700 border-b border-gray-200">
                  Task Name
                </div>
                <div className="px-4 py-2 text-xs font-medium text-gray-600 border-b border-gray-200">
                  Duration
                </div>
                <div className="px-4 py-2 text-xs font-medium text-gray-600 border-b border-gray-200">
                  Start
                </div>
                <div className="px-4 py-2 text-xs font-medium text-gray-600">
                  End
                </div>
              </div>

              {/* Timeline Grid */}
              <div className="flex-1">
                {/* Month Headers */}
                <div className="flex border-b border-gray-200">
                  {timelineMonths.map((month, idx) => (
                    <div
                      key={idx}
                      className="flex-1 px-2 py-3 text-center font-semibold text-gray-700 border-r border-gray-200"
                      style={{ minWidth: `${month.weeks * 60}px` }}
                    >
                      {month.month} {month.year}
                    </div>
                  ))}
                </div>

                {/* Week Grid */}
                <div className="flex border-b border-gray-200 bg-gray-50">
                  {timelineMonths.map((month, monthIdx) =>
                    Array.from({ length: month.weeks }).map((_, weekIdx) => (
                      <div
                        key={`${monthIdx}-${weekIdx}`}
                        className="flex-1 px-1 py-2 text-center text-xs text-gray-600 border-r border-gray-100"
                        style={{ minWidth: '60px' }}
                      >
                        W{weekIdx + 1}
                      </div>
                    ))
                  )}
                </div>

                {/* Day Grid (for week view) */}
                {viewMode === 'week' && (
                  <div className="flex border-b border-gray-200 bg-gray-50">
                    {timelineMonths.map((month, monthIdx) =>
                      Array.from({ length: month.weeks * 7 }).map((_, dayIdx) => (
                        <div
                          key={`${monthIdx}-${dayIdx}`}
                          className="flex-1 px-1 py-1 text-center text-xs text-gray-500 border-r border-gray-100"
                          style={{ minWidth: '20px' }}
                        >
                          {['M', 'T', 'W', 'T', 'F', 'S', 'S'][dayIdx % 7]}
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Task Rows */}
            {tasks.map((task, taskIdx) => {
              const barStyle = getTaskBarStyle(task)
              const duration = task.dueDate && task.startDate
                ? Math.ceil((new Date(task.dueDate).getTime() - new Date(task.startDate).getTime()) / (1000 * 60 * 60 * 24))
                : 0

              return (
                <div key={task.id} className={`flex ${taskIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                  {/* Task Info Column */}
                  <div className="w-64 flex-shrink-0 border-r border-gray-200">
                    <div className="px-4 py-3 border-b border-gray-100">
                      <div className="font-medium text-sm text-gray-900 truncate" title={task.title}>
                        {task.title}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{task.assignedToName}</div>
                    </div>
                    <div className="px-4 py-2 text-xs text-gray-600 border-b border-gray-100">
                      {duration} days
                    </div>
                    <div className="px-4 py-2 text-xs text-gray-600 border-b border-gray-100">
                      {task.startDate ? new Date(task.startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '-'}
                    </div>
                    <div className="px-4 py-2 text-xs text-gray-600">
                      {task.dueDate ? new Date(task.dueDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '-'}
                    </div>
                  </div>

                  {/* Timeline Grid with Task Bar */}
                  <div className="flex-1 relative" style={{ height: '80px' }}>
                    {/* Grid Lines */}
                    <div className="absolute inset-0 flex">
                      {timelineMonths.map((month, monthIdx) =>
                        Array.from({ length: month.weeks }).map((_, weekIdx) => (
                          <div
                            key={`${monthIdx}-${weekIdx}`}
                            className="flex-1 border-r border-gray-100"
                            style={{ minWidth: '60px' }}
                          />
                        ))
                      )}
                    </div>

                    {/* Task Bar */}
                    <div
                      className="absolute top-1/2 transform -translate-y-1/2 h-8 rounded shadow-md flex items-center px-2 cursor-pointer hover:shadow-lg transition-shadow"
                      style={{
                        ...barStyle,
                        backgroundColor: getStatusColor(task.status),
                        minWidth: '40px'
                      }}
                      title={`${task.title}\n${task.startDate} - ${task.dueDate}\nStatus: ${task.status}`}
                    >
                      <span className="text-xs font-medium text-white truncate">
                        {task.title}
                      </span>
                      {task.progress !== undefined && (
                        <span className="ml-auto text-xs text-white font-semibold">
                          {task.progress}%
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Legend */}
        <div className="border-t border-gray-200 bg-gray-50 px-6 py-4">
          <div className="flex items-center gap-6 text-sm">
            <span className="font-medium text-gray-700">Status:</span>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#94a3b8' }}></div>
              <span className="text-gray-600">To Do</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#3b82f6' }}></div>
              <span className="text-gray-600">In Progress</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#22c55e' }}></div>
              <span className="text-gray-600">Done</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ef4444' }}></div>
              <span className="text-gray-600">Blocked</span>
            </div>
          </div>
        </div>
      </div>

      {tasks.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow mt-6">
          <p className="text-gray-500">No tasks available to display in Gantt chart</p>
        </div>
      )}
    </div>
  )
}
