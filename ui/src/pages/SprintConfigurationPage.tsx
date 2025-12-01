import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface Project {
  id: string
  name: string
  sprint_length_weeks?: string
  sprint_starting_day?: string
}

interface Sprint {
  id: string
  name: string
  start_date: string
  end_date: string
  status: string
  task_count?: number
}

const DAYS_OF_WEEK = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
]

export default function SprintConfigurationPage() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState<'config' | 'create'>('config')
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // Configuration tab state
  const [sprintLength, setSprintLength] = useState<string>('2')
  const [startingDay, setStartingDay] = useState<string>('Monday')

  // Create Sprint tab state
  const [createProjectId, setCreateProjectId] = useState<string>('')
  const [sprintName, setSprintName] = useState<string>('')
  const [sprintStartDate, setSprintStartDate] = useState<string>('')
  const [sprintEndDate, setSprintEndDate] = useState<string>('')
  const [sprintGoal, setSprintGoal] = useState<string>('')
  const [creatingSprint, setCreatingSprint] = useState(false)
  const [sprints, setSprints] = useState<Sprint[]>([])
  const [loadingSprints, setLoadingSprints] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProjectId) {
      loadProjectSettings()
    } else {
      setSelectedProject(null)
      setSprintLength('2')
      setStartingDay('Monday')
    }
  }, [selectedProjectId])

  useEffect(() => {
    if (createProjectId && activeTab === 'create') {
      loadDefaultDates()
      loadSprints()
    }
  }, [createProjectId, activeTab])

  const loadProjects = async () => {
    try {
      const data = await api.getProjects()
      setProjects(data)
    } catch (err: any) {
      console.error('Failed to load projects:', err)
      setError('Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  const loadProjectSettings = async () => {
    if (!selectedProjectId) return
    
    try {
      const project = await api.getProject(selectedProjectId)
      setSelectedProject(project)
      const length = project.sprint_length_weeks || '2'
      const day = project.sprint_starting_day || 'Monday'
      setSprintLength(length)
      setStartingDay(day)
    } catch (err: any) {
      console.error('Failed to load project settings:', err)
      setError('Failed to load project sprint configuration')
    }
  }

  const loadDefaultDates = async () => {
    if (!createProjectId) return
    
    try {
      const defaultDates = await api.getDefaultSprintDates(createProjectId)
      setSprintStartDate(defaultDates.start_date)
      setSprintEndDate(defaultDates.end_date)
      // Generate default sprint name
      const project = projects.find(p => p.id === createProjectId)
      if (project && !sprintName) {
        const sprintNum = sprints.length + 1
        setSprintName(`${project.name} Sprint ${sprintNum}`)
      }
    } catch (err: any) {
      console.error('Failed to load default dates:', err)
      setError('Failed to load default sprint dates')
    }
  }

  const loadSprints = async () => {
    if (!createProjectId) return
    
    try {
      setLoadingSprints(true)
      const data = await api.getProjectSprints(createProjectId, true) // Include past sprints
      setSprints(data || [])
    } catch (err: any) {
      console.error('Failed to load sprints:', err)
      setError('Failed to load sprints')
    } finally {
      setLoadingSprints(false)
    }
  }

  const handleSaveSprintConfig = async () => {
    if (!selectedProjectId) {
      setError('Please select a project')
      return
    }

    try {
      setSaving(true)
      setError(null)
      setSuccess(false)

      await api.updateProject(selectedProjectId, {
        sprint_length_weeks: sprintLength,
        sprint_starting_day: startingDay
      })

      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
      
      await new Promise(resolve => setTimeout(resolve, 300))
      await loadProjectSettings()
      setSaving(false)
    } catch (err: any) {
      console.error('Failed to update sprint configuration:', err)
      setError(err.response?.data?.detail || 'Failed to update sprint configuration')
      setSaving(false)
    }
  }

  const handleCreateSprint = async () => {
    if (!createProjectId) {
      setError('Please select a project')
      return
    }

    if (!sprintName || !sprintStartDate || !sprintEndDate) {
      setError('Please fill in all required fields')
      return
    }

    if (new Date(sprintStartDate) >= new Date(sprintEndDate)) {
      setError('Start date must be before end date')
      return
    }

    try {
      setCreatingSprint(true)
      setError(null)
      setSuccess(false)

      await api.createSprint({
        project_id: createProjectId,
        name: sprintName,
        start_date: sprintStartDate,
        end_date: sprintEndDate,
        goal: sprintGoal || null,
        status: 'Planning'
      })

      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
      
      // Reset form
      setSprintName('')
      setSprintGoal('')
      await loadDefaultDates()
      await loadSprints()
      setCreatingSprint(false)
    } catch (err: any) {
      console.error('Failed to create sprint:', err)
      const errorMsg = err.response?.data?.detail || 'Failed to create sprint'
      setError(errorMsg)
      setCreatingSprint(false)
    }
  }

  const handleDeleteSprint = async (sprintId: string) => {
    if (!window.confirm('Are you sure you want to delete this sprint? This action cannot be undone.')) {
      return
    }

    try {
      setError(null)
      setSuccess(false)
      await api.deleteSprint(sprintId)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
      await loadSprints()
    } catch (err: any) {
      console.error('Failed to delete sprint:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete sprint'
      setError(errorMsg)
      // Show error in alert since it might contain important info about tasks
      setTimeout(() => {
        alert(errorMsg)
      }, 100)
    }
  }

  const formatDate = (dateStr: string) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  // Check if user is Admin or Product Owner
  if (user?.role !== 'Admin' && user?.role !== 'Product Owner') {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-red-600 text-5xl mb-4">🔒</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Access Denied</h2>
          <p className="text-gray-600">Admin or Product Owner role required to configure sprint settings</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-blue-600 text-5xl mb-4">⏳</div>
          <p className="text-gray-600">Loading sprint configuration...</p>
        </div>
      </div>
    )
  }

  // Calculate end day based on starting day and length
  const getEndDay = () => {
    const startIndex = DAYS_OF_WEEK.indexOf(startingDay)
    const lengthDays = parseInt(sprintLength) * 7 - 1
    const endIndex = (startIndex + lengthDays) % 7
    return DAYS_OF_WEEK[endIndex]
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--text-color)' }}>
        Sprint Configuration ⚙️
      </h1>

      {/* Tabs */}
      <div className="mb-6 border-b" style={{ borderColor: 'var(--border-color)' }}>
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('config')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'config'
                ? 'border-b-2'
                : 'opacity-60 hover:opacity-100'
            }`}
            style={{
              color: activeTab === 'config' ? 'var(--primary-color)' : 'var(--text-secondary)',
              borderBottomColor: activeTab === 'config' ? 'var(--primary-color)' : 'transparent'
            }}
          >
            Configuration
          </button>
          <button
            onClick={() => setActiveTab('create')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'create'
                ? 'border-b-2'
                : 'opacity-60 hover:opacity-100'
            }`}
            style={{
              color: activeTab === 'create' ? 'var(--primary-color)' : 'var(--text-secondary)',
              borderBottomColor: activeTab === 'create' ? 'var(--primary-color)' : 'transparent'
            }}
          >
            Create Sprint
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 rounded-lg bg-green-50 border border-green-200">
          <p className="text-green-800">Operation completed successfully!</p>
        </div>
      )}

      {/* Configuration Tab */}
      {activeTab === 'config' && (
        <div className="bg-white rounded-lg shadow-md p-6" style={{ 
          backgroundColor: 'var(--surface-color)',
          border: '1px solid var(--border-color)'
        }}>
          <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
            Project Sprint Settings
          </h2>
          <div className="space-y-6">
            {/* Project Selection */}
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                Select Project <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedProjectId}
                onChange={(e) => setSelectedProjectId(e.target.value)}
                className="w-full p-2 rounded border"
                style={{
                  backgroundColor: 'var(--background-color)',
                  color: 'var(--text-color)',
                  borderColor: 'var(--border-color)'
                }}
              >
                <option value="">Select a project...</option>
                {projects.map(project => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
              <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
                Sprint configuration is set per project. Each project can have its own sprint length and starting day.
              </p>
            </div>

            {selectedProjectId && (
              <>
                {/* Sprint Length */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Sprint Length <span className="text-red-500">*</span>
                  </label>
                  <select
                    key={`sprint-length-${sprintLength}`}
                    value={sprintLength}
                    onChange={(e) => setSprintLength(e.target.value)}
                    className="w-full p-2 rounded border"
                    style={{
                      backgroundColor: 'var(--background-color)',
                      color: 'var(--text-color)',
                      borderColor: 'var(--border-color)'
                    }}
                  >
                    <option value="1">1 Week</option>
                    <option value="2">2 Weeks</option>
                  </select>
                  <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    Duration of each sprint cycle
                  </p>
                </div>

                {/* Starting Day */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                    Sprint Starting Day <span className="text-red-500">*</span>
                  </label>
                  <select
                    key={`sprint-day-${startingDay}`}
                    value={startingDay}
                    onChange={(e) => setStartingDay(e.target.value)}
                    className="w-full p-2 rounded border"
                    style={{
                      backgroundColor: 'var(--background-color)',
                      color: 'var(--text-color)',
                      borderColor: 'var(--border-color)'
                    }}
                  >
                    {DAYS_OF_WEEK.map(day => (
                      <option key={day} value={day}>{day}</option>
                    ))}
                  </select>
                  <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    Day of the week when sprints begin
                  </p>
                </div>

                {/* Preview */}
                <div className="p-4 rounded-lg" style={{ 
                  backgroundColor: 'var(--background-color)',
                  border: '1px solid var(--border-color)'
                }}>
                  <h3 className="font-semibold mb-2" style={{ color: 'var(--text-color)' }}>
                    Sprint Schedule Preview
                  </h3>
                  <div className="space-y-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    <p>
                      <strong>Sprint Length:</strong> {sprintLength} {sprintLength === '1' ? 'week' : 'weeks'}
                    </p>
                    <p>
                      <strong>Starts on:</strong> {startingDay}
                    </p>
                    <p>
                      <strong>Ends on:</strong> {getEndDay()} (the day before the next sprint starts)
                    </p>
                  </div>
                </div>

                {/* Save Button */}
                <div className="flex justify-end gap-4 pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
                  <button
                    onClick={handleSaveSprintConfig}
                    disabled={saving || !selectedProjectId}
                    className="px-6 py-2 rounded font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{
                      backgroundColor: saving || !selectedProjectId ? 'var(--text-secondary)' : 'var(--primary-color)',
                      color: 'white'
                    }}
                  >
                    {saving ? 'Saving...' : 'Save Sprint Configuration'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Create Sprint Tab */}
      {activeTab === 'create' && (
        <div className="space-y-6">
          {/* Create Sprint Form */}
          <div className="bg-white rounded-lg shadow-md p-6" style={{ 
            backgroundColor: 'var(--surface-color)',
            border: '1px solid var(--border-color)'
          }}>
            <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
              Create New Sprint
            </h2>
            <div className="space-y-4">
              {/* Project Selection */}
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                  Select Project <span className="text-red-500">*</span>
                </label>
                <select
                  value={createProjectId}
                  onChange={(e) => {
                    setCreateProjectId(e.target.value)
                    setSprintName('')
                    setSprintStartDate('')
                    setSprintEndDate('')
                  }}
                  className="w-full p-2 rounded border"
                  style={{
                    backgroundColor: 'var(--background-color)',
                    color: 'var(--text-color)',
                    borderColor: 'var(--border-color)'
                  }}
                >
                  <option value="">Select a project...</option>
                  {projects.map(project => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>

              {createProjectId && (
                <>
                  {/* Sprint Name */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                      Sprint Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={sprintName}
                      onChange={(e) => setSprintName(e.target.value)}
                      placeholder="e.g., Sprint 1"
                      className="w-full p-2 rounded border"
                      style={{
                        backgroundColor: 'var(--background-color)',
                        color: 'var(--text-color)',
                        borderColor: 'var(--border-color)'
                      }}
                    />
                  </div>

                  {/* Start Date */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                      Start Date <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      value={sprintStartDate}
                      onChange={(e) => setSprintStartDate(e.target.value)}
                      className="w-full p-2 rounded border"
                      style={{
                        backgroundColor: 'var(--background-color)',
                        color: 'var(--text-color)',
                        borderColor: 'var(--border-color)'
                      }}
                    />
                    <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      Default date is calculated based on project configuration. You can modify it.
                    </p>
                  </div>

                  {/* End Date */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                      End Date <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      value={sprintEndDate}
                      onChange={(e) => setSprintEndDate(e.target.value)}
                      className="w-full p-2 rounded border"
                      style={{
                        backgroundColor: 'var(--background-color)',
                        color: 'var(--text-color)',
                        borderColor: 'var(--border-color)'
                      }}
                    />
                    <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      Default date is calculated based on project configuration. You can modify it.
                    </p>
                  </div>

                  {/* Sprint Goal */}
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                      Sprint Goal (Optional)
                    </label>
                    <textarea
                      value={sprintGoal}
                      onChange={(e) => setSprintGoal(e.target.value)}
                      placeholder="Describe the goal for this sprint..."
                      rows={3}
                      className="w-full p-2 rounded border"
                      style={{
                        backgroundColor: 'var(--background-color)',
                        color: 'var(--text-color)',
                        borderColor: 'var(--border-color)'
                      }}
                    />
                  </div>

                  {/* Create Button */}
                  <div className="flex justify-end gap-4 pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
                    <button
                      onClick={handleCreateSprint}
                      disabled={creatingSprint || !createProjectId || !sprintName || !sprintStartDate || !sprintEndDate}
                      className="px-6 py-2 rounded font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      style={{
                        backgroundColor: creatingSprint || !createProjectId ? 'var(--text-secondary)' : 'var(--primary-color)',
                        color: 'white'
                      }}
                    >
                      {creatingSprint ? 'Creating...' : 'Create Sprint'}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Existing Sprints List */}
          {createProjectId && (
            <div className="bg-white rounded-lg shadow-md p-6" style={{ 
              backgroundColor: 'var(--surface-color)',
              border: '1px solid var(--border-color)'
            }}>
              <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                Existing Sprints
              </h2>
              {loadingSprints ? (
                <p style={{ color: 'var(--text-secondary)' }}>Loading sprints...</p>
              ) : sprints.length === 0 ? (
                <p style={{ color: 'var(--text-secondary)' }}>No sprints found for this project.</p>
              ) : (
                <div className="space-y-2">
                  {sprints.map((sprint) => (
                    <div
                      key={sprint.id}
                      className="p-4 rounded border flex justify-between items-center"
                      style={{
                        backgroundColor: 'var(--background-color)',
                        borderColor: 'var(--border-color)'
                      }}
                    >
                      <div>
                        <div className="font-medium" style={{ color: 'var(--text-color)' }}>
                          {sprint.name} ({sprint.id})
                        </div>
                        <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                          {formatDate(sprint.start_date)} - {formatDate(sprint.end_date)}
                        </div>
                        <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                          Status: {sprint.status} | Tasks: {sprint.task_count || 0}
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteSprint(sprint.id)}
                        className="px-3 py-1 text-sm rounded bg-red-600 text-white hover:bg-red-700"
                        disabled={sprint.task_count && sprint.task_count > 0}
                        title={sprint.task_count && sprint.task_count > 0 ? 'Cannot delete sprint with assigned tasks' : 'Delete sprint'}
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Information Box */}
      <div className="mt-6 p-4 rounded-lg" style={{ 
        backgroundColor: 'var(--surface-color)',
        border: '1px solid var(--border-color)'
      }}>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          💡 <strong>Note:</strong> Sprint creation is now manual. Configure sprint settings per project, then create sprints as needed. 
          The system will prevent overlapping sprints and ensure no sprint can be deleted if it has assigned tasks.
        </p>
      </div>
    </div>
  )
}
