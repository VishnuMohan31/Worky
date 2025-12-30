import { useState, useEffect } from 'react'
import api from '../../services/api'
import jsPDF from 'jspdf'

interface Project {
  id: string
  name: string
}

interface UseCase {
  id: string
  name: string
  project_id?: string
  projectId?: string
}

interface UserStory {
  id: string
  title?: string
  name?: string
  usecase_id?: string
  usecaseId?: string
}

interface Task {
  id: string
  title?: string
  name?: string
  user_story_id?: string
  userStoryId?: string
}

interface ProjectTreeReportModalProps {
  isOpen: boolean
  onClose: () => void
}

type Level = 'usecase' | 'userstory' | 'task'

export default function ProjectTreeReportModal({ isOpen, onClose }: ProjectTreeReportModalProps) {
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [selectedLevel, setSelectedLevel] = useState<Level>('usecase')
  const [loading, setLoading] = useState(false)
  const [treeData, setTreeData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      loadProjects()
    }
  }, [isOpen])

  useEffect(() => {
    if (selectedProjectId && isOpen) {
      loadTreeData()
    } else {
      setTreeData(null)
    }
  }, [selectedProjectId, selectedLevel, isOpen])

  const loadProjects = async () => {
    try {
      const data = await api.getProjects()
      setProjects(data)
    } catch (err: any) {
      console.error('Failed to load projects:', err)
      setError('Failed to load projects')
    }
  }

  const loadTreeData = async () => {
    if (!selectedProjectId) return

    setLoading(true)
    setError(null)

    try {
      const project = await api.getProject(selectedProjectId)
      const tree: any = {
        project: {
          id: project.id,
          name: project.name
        },
        useCases: []
      }

      if (selectedLevel === 'usecase' || selectedLevel === 'userstory' || selectedLevel === 'task') {
        // Load use cases
        const useCases = await api.getUseCases(selectedProjectId)
        tree.useCases = useCases.map((uc: UseCase) => ({
          id: uc.id,
          name: uc.name,
          userStories: []
        }))

        if (selectedLevel === 'userstory' || selectedLevel === 'task') {
          // Load user stories for each use case
          for (const useCase of tree.useCases) {
            try {
              const userStories = await api.getUserStories(useCase.id)
              useCase.userStories = userStories.map((us: UserStory) => ({
                id: us.id,
                title: us.title || us.name,
                tasks: []
              }))

              if (selectedLevel === 'task') {
                // Load tasks for each user story
                for (const userStory of useCase.userStories) {
                  try {
                    const tasks = await api.getEntityList('task', { user_story_id: userStory.id })
                    userStory.tasks = tasks.map((t: Task) => ({
                      id: t.id,
                      title: t.title || t.name
                    }))
                  } catch (err) {
                    console.error(`Failed to load tasks for user story ${userStory.id}:`, err)
                  }
                }
              }
            } catch (err) {
              console.error(`Failed to load user stories for use case ${useCase.id}:`, err)
            }
          }
        }
      }

      setTreeData(tree)
    } catch (err: any) {
      console.error('Failed to load tree data:', err)
      setError(err.message || 'Failed to load tree data')
    } finally {
      setLoading(false)
    }
  }

  const exportToPDF = () => {
    if (!treeData) return

    const doc = new jsPDF()
    const pageWidth = doc.internal.pageSize.getWidth()
    const pageHeight = doc.internal.pageSize.getHeight()
    const margin = 20
    let yPos = margin
    const lineHeight = 7
    const indent = 10

    // Helper function to check and add new page if needed
    const checkPageBreak = (requiredSpace: number = lineHeight) => {
      if (yPos + requiredSpace > pageHeight - margin) {
        doc.addPage()
        yPos = margin
        return true
      }
      return false
    }

    // Title
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    doc.text('Project Tree Report', margin, yPos)
    yPos += lineHeight * 2

    // Project name
    doc.setFontSize(14)
    doc.setFont('helvetica', 'bold')
    doc.text(`Project: ${treeData.project.name}`, margin, yPos)
    yPos += lineHeight * 1.5

    // Level and date
    doc.setFontSize(12)
    doc.setFont('helvetica', 'normal')
    doc.text(`Level: ${selectedLevel.charAt(0).toUpperCase() + selectedLevel.slice(1)}`, margin, yPos)
    yPos += lineHeight
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, margin, yPos)
    yPos += lineHeight * 2

    // Tree structure
    doc.setFontSize(10)
    treeData.useCases.forEach((useCase: any, ucIndex: number) => {
      checkPageBreak(lineHeight * 2)

      // Use Case
      doc.setFont('helvetica', 'bold')
      doc.text(`Use Case: ${useCase.name}`, margin, yPos)
      yPos += lineHeight

      if (selectedLevel === 'userstory' || selectedLevel === 'task') {
        if (useCase.userStories && useCase.userStories.length > 0) {
          useCase.userStories.forEach((userStory: any, usIndex: number) => {
            checkPageBreak(lineHeight * 2)

            // User Story
            doc.setFont('helvetica', 'normal')
            const prefix = usIndex === useCase.userStories.length - 1 ? '└─' : '├─'
            doc.text(`  ${prefix} User Story: ${userStory.title}`, margin + indent, yPos)
            yPos += lineHeight

            if (selectedLevel === 'task') {
              if (userStory.tasks && userStory.tasks.length > 0) {
                userStory.tasks.forEach((task: any, taskIndex: number) => {
                  checkPageBreak()

                  // Task
                  const taskPrefix = taskIndex === userStory.tasks.length - 1 ? '└─' : '├─'
                  doc.text(`    ${taskPrefix} Task: ${task.title}`, margin + indent * 2, yPos)
                  yPos += lineHeight
                })
              } else {
                checkPageBreak()
                doc.setFont('helvetica', 'italic')
                doc.text(`    └─ (No tasks)`, margin + indent * 2, yPos)
                doc.setFont('helvetica', 'normal')
                yPos += lineHeight
              }
            }
          })
        } else {
          checkPageBreak()
          doc.setFont('helvetica', 'italic')
          doc.text(`  └─ (No user stories)`, margin + indent, yPos)
          doc.setFont('helvetica', 'normal')
          yPos += lineHeight
        }
      }

      // Add spacing between use cases
      if (ucIndex < treeData.useCases.length - 1) {
        yPos += lineHeight * 0.5
      }
    })

    // Save the PDF
    const fileName = `Project_Tree_${treeData.project.name.replace(/\s+/g, '_')}_${selectedLevel}_${new Date().toISOString().split('T')[0]}.pdf`
    doc.save(fileName)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
         onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
           style={{ backgroundColor: 'var(--surface-color)' }}
           onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="p-6 border-b" style={{ borderColor: 'var(--border-color)' }}>
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>
              Project Tree Report 🌳
            </h2>
            <button
              onClick={onClose}
              className="text-2xl leading-none"
              style={{ color: 'var(--text-secondary)' }}
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Selection Controls */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
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
            </div>

            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-color)' }}>
                Select Level <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value as Level)}
                className="w-full p-2 rounded border"
                style={{
                  backgroundColor: 'var(--background-color)',
                  color: 'var(--text-color)',
                  borderColor: 'var(--border-color)'
                }}
              >
                <option value="usecase">Use Cases</option>
                <option value="userstory">User Stories</option>
                <option value="task">Tasks</option>
              </select>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 rounded-lg bg-red-50 border border-red-200">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Tree Display */}
          {loading && (
            <div className="text-center py-8">
              <p style={{ color: 'var(--text-secondary)' }}>Loading tree data...</p>
            </div>
          )}

          {!loading && treeData && (
            <div className="rounded-lg p-6 border" style={{ 
              backgroundColor: 'var(--background-color)',
              borderColor: 'var(--border-color)'
            }}>
              <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-color)' }}>
                {treeData.project.name}
              </h3>
              
              <div className="space-y-3">
                {treeData.useCases.length === 0 ? (
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    No {selectedLevel === 'usecase' ? 'use cases' : selectedLevel === 'userstory' ? 'user stories' : 'tasks'} found for this project.
                  </p>
                ) : (
                  treeData.useCases.map((useCase: any, ucIndex: number) => (
                    <div key={useCase.id} className="border-l-2 pl-4" style={{ borderColor: 'var(--border-color)' }}>
                      <div className="flex items-center py-2">
                        <span className="mr-2 text-lg">📁</span>
                        <span className="font-semibold text-base" style={{ color: 'var(--text-color)' }}>
                          {useCase.name}
                        </span>
                      </div>
                      
                      {(selectedLevel === 'userstory' || selectedLevel === 'task') && useCase.userStories && (
                        <div className="ml-4 mt-2 space-y-2">
                          {useCase.userStories.length === 0 ? (
                            <p className="text-sm italic" style={{ color: 'var(--text-secondary)' }}>
                              (No user stories)
                            </p>
                          ) : (
                            useCase.userStories.map((userStory: any, usIndex: number) => (
                              <div key={userStory.id} className="border-l-2 pl-3" style={{ borderColor: 'var(--border-color)' }}>
                                <div className="flex items-center py-1">
                                  <span className="mr-2">📝</span>
                                  <span className="font-medium" style={{ color: 'var(--text-color)' }}>
                                    {userStory.title}
                                  </span>
                                </div>
                                
                                {selectedLevel === 'task' && userStory.tasks && (
                                  <div className="ml-4 mt-1 space-y-1">
                                    {userStory.tasks.length === 0 ? (
                                      <p className="text-sm italic" style={{ color: 'var(--text-secondary)' }}>
                                        (No tasks)
                                      </p>
                                    ) : (
                                      userStory.tasks.map((task: any) => (
                                        <div key={task.id} className="flex items-center py-1">
                                          <span className="mr-2">✓</span>
                                          <span style={{ color: 'var(--text-color)' }}>
                                            {task.title}
                                          </span>
                                        </div>
                                      ))
                                    )}
                                  </div>
                                )}
                              </div>
                            ))
                          )}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t flex justify-end gap-4" style={{ borderColor: 'var(--border-color)' }}>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded"
            style={{
              backgroundColor: 'var(--secondary-color)',
              color: 'var(--text-color)'
            }}
          >
            Close
          </button>
          <button
            onClick={exportToPDF}
            disabled={!treeData || loading}
            className="px-4 py-2 rounded font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              backgroundColor: (!treeData || loading) ? 'var(--text-secondary)' : 'var(--primary-color)',
              color: 'white'
            }}
          >
            📄 Download PDF
          </button>
        </div>
      </div>
    </div>
  )
}

