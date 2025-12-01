import { useLanguage } from '../contexts/LanguageContext'

export default function ReportsPage() {
  const { t } = useLanguage()

  const reports = [
    {
      id: 1,
      title: 'Utilization Report',
      description: 'Resource allocation vs actual usage analysis',
      icon: '📊',
      color: 'var(--primary-color)'
    },
    {
      id: 2,
      title: 'Engagement Report',
      description: 'Developer activity and contribution metrics',
      icon: '📈',
      color: 'var(--info-color)'
    },
    {
      id: 3,
      title: 'Occupancy Forecast',
      description: 'Time booking predictions for upcoming periods',
      icon: '📅',
      color: 'var(--success-color)'
    },
    {
      id: 4,
      title: 'Bug Density Report',
      description: 'Bug trends and resolution metrics by project',
      icon: '🐛',
      color: 'var(--error-color)'
    },
    {
      id: 5,
      title: 'Sprint Velocity',
      description: 'Team velocity and sprint completion trends',
      icon: '🏃',
      color: 'var(--warning-color)'
    },
    {
      id: 6,
      title: 'Project Health',
      description: 'Overall project status and risk assessment',
      icon: '💚',
      color: 'var(--success-color)'
    },
    {
      id: 7,
      title: 'Project Tree',
      description: 'Hierarchical view of project structure (Use Cases, User Stories, Tasks)',
      icon: '🌳',
      color: 'var(--primary-color)',
      isProjectTree: true
    }
  ]

  const handleGenerateReport = (report: typeof reports[0]) => {
    // Navigate to dedicated report page
    const routeMap: Record<number, string> = {
      1: 'utilization',
      2: 'engagement',
      3: 'occupancy-forecast',
      4: 'bug-density',
      5: 'sprint-velocity',
      6: 'project-health',
      7: 'project-tree'
    }
    
    const route = routeMap[report.id]
    if (route) {
      window.location.href = `/reports/${route}`
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text-color)' }}>
        {t('reports')} 📑
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map(report => (
          <div key={report.id}
               className="rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
               onClick={() => handleGenerateReport(report)}
               style={{ 
                 backgroundColor: 'var(--surface-color)',
                 border: '1px solid var(--border-color)'
               }}>
            <div className="flex items-start justify-between mb-4">
              <div className="text-4xl" style={{ color: report.color }}>
                {report.icon}
              </div>
              <button 
                className="px-3 py-1 text-sm rounded hover:opacity-80 transition-opacity"
                style={{ 
                  backgroundColor: 'var(--secondary-color)',
                  color: 'var(--text-color)'
                }}
                onClick={(e) => {
                  e.stopPropagation()
                  handleGenerateReport(report)
                }}>
                View Report →
              </button>
            </div>
            <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-color)' }}>
              {report.title}
            </h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              {report.description}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-lg p-6"
           style={{ 
             backgroundColor: 'var(--surface-color)',
             border: '1px solid var(--border-color)'
           }}>
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
          Recent Reports
        </h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded"
               style={{ backgroundColor: 'var(--background-color)' }}>
            <div>
              <p className="font-medium" style={{ color: 'var(--text-color)' }}>
                Utilization Report - Q1 2025
              </p>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Generated on 2025-01-10
              </p>
            </div>
            <div className="flex gap-2">
              <button className="px-3 py-1 text-sm rounded"
                      style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}>
                📄 PDF
              </button>
              <button className="px-3 py-1 text-sm rounded"
                      style={{ backgroundColor: 'var(--info-color)', color: 'white' }}>
                📊 CSV
              </button>
            </div>
          </div>
          <div className="flex items-center justify-between p-3 rounded"
               style={{ backgroundColor: 'var(--background-color)' }}>
            <div>
              <p className="font-medium" style={{ color: 'var(--text-color)' }}>
                Engagement Report - December 2024
              </p>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Generated on 2025-01-05
              </p>
            </div>
            <div className="flex gap-2">
              <button className="px-3 py-1 text-sm rounded"
                      style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}>
                📄 PDF
              </button>
              <button className="px-3 py-1 text-sm rounded"
                      style={{ backgroundColor: 'var(--info-color)', color: 'white' }}>
                📊 CSV
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
