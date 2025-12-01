/**
 * BugDetails Component
 * Displays detailed information about a bug with all fields, hierarchy path,
 * status update dropdown with validation, reassign button, linked test cases,
 * comments section, and status history timeline
 * Requirements: 6.3, 6.4, 6.5, 7.1, 7.2, 7.8, 8.5
 */
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Bug } from '../../types/entities'
import api from '../../services/api'
import Modal from '../common/Modal'
import BugForm from '../forms/BugForm'
import CommentsSection from '../qa/CommentsSection'
import AttachmentsSection from '../qa/AttachmentsSection'

interface BugDetailsProps {
  bug: Bug
  onUpdate?: () => void
  onClose?: () => void
}

export default function BugDetails({ bug, onUpdate, onClose }: BugDetailsProps) {
  const { t } = useTranslation()
  const [currentBug, setCurrentBug] = useState<Bug>(bug)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false)
  const [isResolveModalOpen, setIsResolveModalOpen] = useState(false)
  const [isStatusUpdateModalOpen, setIsStatusUpdateModalOpen] = useState(false)
  const [users, setUsers] = useState<any[]>([])
  const [selectedAssignee, setSelectedAssignee] = useState('')
  const [resolutionNotes, setResolutionNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [linkedTestCases, setLinkedTestCases] = useState<any[]>([])
  const [statusHistory, setStatusHistory] = useState<any[]>([])
  const [selectedStatus, setSelectedStatus] = useState('')
  const [resolutionType, setResolutionType] = useState('')
  
  useEffect(() => {
    setCurrentBug(bug)
  }, [bug])
  
  useEffect(() => {
    loadUsers()
    loadLinkedTestCases()
    loadStatusHistory()
  }, [currentBug.id])
  
  const loadUsers = async () => {
    try {
      const data = await api.getUsers()
      setUsers(data)
    } catch (error) {
      console.error('Failed to load users:', error)
    }
  }
  
  const loadLinkedTestCases = async () => {
    try {
      const data = await api.get(`/bugs/${currentBug.id}/test-cases`)
      setLinkedTestCases(data)
    } catch (error) {
      console.error('Failed to load linked test cases:', error)
      setLinkedTestCases([])
    }
  }
  
  const loadStatusHistory = async () => {
    try {
      const data = await api.get(`/bugs/${currentBug.id}/history`)
      setStatusHistory(data)
    } catch (error) {
      console.error('Failed to load status history:', error)
      setStatusHistory([])
    }
  }
  
  const handleUpdateBug = async (data: any) => {
    try {
      setLoading(true)
      await api.updateEntity('bug', currentBug.id, data)
      setIsEditModalOpen(false)
      if (onUpdate) onUpdate()
    } catch (error) {
      console.error('Failed to update bug:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleAssignBug = async () => {
    if (!selectedAssignee) return
    
    try {
      setLoading(true)
      await api.updateEntity('bug', currentBug.id, { 
        assigned_to: selectedAssignee,
        status: 'Assigned'
      })
      setIsAssignModalOpen(false)
      if (onUpdate) onUpdate()
    } catch (error) {
      console.error('Failed to assign bug:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleResolveBug = async () => {
    if (!resolutionNotes.trim()) {
      alert('Please provide resolution notes')
      return
    }
    
    try {
      setLoading(true)
      await api.updateEntity('bug', currentBug.id, {
        status: 'Fixed',
        resolution_notes: resolutionNotes,
        closed_at: new Date().toISOString()
      })
      setIsResolveModalOpen(false)
      if (onUpdate) onUpdate()
    } catch (error) {
      console.error('Failed to resolve bug:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleStatusUpdate = async () => {
    if (!selectedStatus) {
      alert('Please select a status')
      return
    }
    
    // Validate status transition
    if (selectedStatus === 'Fixed' && !resolutionType) {
      alert('Please select a resolution type when marking as Fixed')
      return
    }
    
    try {
      setLoading(true)
      const updateData: any = { status: selectedStatus }
      
      if (selectedStatus === 'Fixed' || selectedStatus === 'Verified' || selectedStatus === 'Closed') {
        updateData.closed_at = new Date().toISOString()
      }
      
      if (resolutionType) {
        updateData.resolution_type = resolutionType
      }
      
      await api.post(`/bugs/${currentBug.id}/status`, updateData)
      setIsStatusUpdateModalOpen(false)
      setSelectedStatus('')
      setResolutionType('')
      if (onUpdate) onUpdate()
    } catch (error) {
      console.error('Failed to update status:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      'Critical': 'bg-red-100 text-red-800 border-red-300',
      'High': 'bg-orange-100 text-orange-800 border-orange-300',
      'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Low': 'bg-green-100 text-green-800 border-green-300'
    }
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-300'
  }
  
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'New': 'bg-blue-100 text-blue-800 border-blue-300',
      'Assigned': 'bg-purple-100 text-purple-800 border-purple-300',
      'In Progress': 'bg-indigo-100 text-indigo-800 border-indigo-300',
      'Fixed': 'bg-teal-100 text-teal-800 border-teal-300',
      'Verified': 'bg-green-100 text-green-800 border-green-300',
      'Closed': 'bg-gray-100 text-gray-800 border-gray-300',
      'Reopened': 'bg-red-100 text-red-800 border-red-300'
    }
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300'
  }
  
  const formatDate = (date: string | undefined) => {
    if (!date) return 'N/A'
    return new Date(date).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  const getReporterName = () => {
    const reporter = users.find(u => u.id === currentBug.reported_by)
    return reporter ? (reporter.fullName || reporter.full_name) : currentBug.reported_by
  }
  
  const getAssigneeName = () => {
    if (!currentBug.assigned_to) return 'Unassigned'
    const assignee = users.find(u => u.id === currentBug.assigned_to)
    return assignee ? (assignee.fullName || assignee.full_name) : currentBug.assigned_to
  }
  
  const canAssign = currentBug.status === 'New' || currentBug.status === 'Reopened'
  const canResolve = currentBug.status === 'In Progress' || currentBug.status === 'Assigned'
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {currentBug.title}
          </h2>
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`px-3 py-1 text-sm font-medium rounded border ${getSeverityColor(currentBug.severity)}`}>
              {currentBug.severity}
            </span>
            <span className="px-3 py-1 text-sm font-medium rounded bg-gray-100 text-gray-800 border border-gray-300">
              {currentBug.priority}
            </span>
            <span className={`px-3 py-1 text-sm font-medium rounded border ${getStatusColor(currentBug.status)}`}>
              {currentBug.status}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsEditModalOpen(true)}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit
          </button>
          
          {onClose && (
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>
      
      {/* Short Description */}
      {currentBug.short_description && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-900">{currentBug.short_description}</p>
        </div>
      )}
      
      {/* Description */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p className="text-gray-700 whitespace-pre-wrap">
            {currentBug.long_description || 'No description provided'}
          </p>
        </div>
      </div>
      
      {/* Associated Entity */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Associated Entity</h3>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Entity Type</p>
              <p className="font-medium text-gray-900">{currentBug.entity_type}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Entity ID</p>
              <p className="font-mono text-sm text-gray-900">{currentBug.entity_id}</p>
            </div>
            <button
              onClick={() => {
                // Navigate to entity - would integrate with hierarchy navigator
                console.log('Navigate to:', currentBug.entity_type, currentBug.entity_id)
              }}
              className="px-3 py-1.5 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors flex items-center gap-1"
            >
              View Entity
              <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      {/* Reporter, Assignee, and QA Owner */}
      <div className="grid grid-cols-3 gap-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Reporter</h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <p className="font-medium text-gray-900">{getReporterName()}</p>
                <p className="text-sm text-gray-600">Reported on {formatDate(currentBug.created_at)}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Assignee</h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  currentBug.assigned_to ? 'bg-purple-100' : 'bg-gray-100'
                }`}>
                  <svg className={`w-6 h-6 ${currentBug.assigned_to ? 'text-purple-600' : 'text-gray-400'}`} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{getAssigneeName()}</p>
                  {currentBug.assigned_to && (
                    <p className="text-sm text-gray-600">Developer</p>
                  )}
                </div>
              </div>
              
              {canAssign && (
                <button
                  onClick={() => setIsAssignModalOpen(true)}
                  className="px-3 py-1.5 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                >
                  Assign
                </button>
              )}
            </div>
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">QA Owner</h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                (currentBug as any).qa_owner_id ? 'bg-teal-100' : 'bg-gray-100'
              }`}>
                <svg className={`w-6 h-6 ${(currentBug as any).qa_owner_id ? 'text-teal-600' : 'text-gray-400'}`} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="font-medium text-gray-900">
                  {(currentBug as any).qa_owner_id 
                    ? users.find(u => u.id === (currentBug as any).qa_owner_id)?.fullName || users.find(u => u.id === (currentBug as any).qa_owner_id)?.full_name || 'Unknown'
                    : 'Unassigned'}
                </p>
                {(currentBug as any).qa_owner_id && (
                  <p className="text-sm text-gray-600">QA Tester</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Category and Component */}
      {((currentBug as any).category || (currentBug as any).component_attached_to) && (
        <div className="grid grid-cols-2 gap-4">
          {(currentBug as any).category && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Category</h3>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <span className="px-3 py-1.5 text-sm font-medium rounded bg-indigo-100 text-indigo-800 border border-indigo-300">
                  {(currentBug as any).category}
                </span>
              </div>
            </div>
          )}
          
          {(currentBug as any).component_attached_to && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Component</h3>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <p className="text-gray-900 font-medium">{(currentBug as any).component_attached_to}</p>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Reproduction Path */}
      {((currentBug as any).reproduction_steps || (currentBug as any).expected_result || (currentBug as any).actual_result) && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Reproduction Path</h3>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-4">
            {(currentBug as any).reproduction_steps && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  Steps to Reproduce
                </h4>
                <p className="text-gray-900 whitespace-pre-wrap bg-white p-3 rounded border border-gray-200">{(currentBug as any).reproduction_steps}</p>
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-4">
              {(currentBug as any).expected_result && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <svg className="w-4 h-4 text-green-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Expected Result
                  </h4>
                  <p className="text-gray-900 whitespace-pre-wrap bg-green-50 p-3 rounded border border-green-200">{(currentBug as any).expected_result}</p>
                </div>
              )}
              
              {(currentBug as any).actual_result && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <svg className="w-4 h-4 text-red-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Actual Result
                  </h4>
                  <p className="text-gray-900 whitespace-pre-wrap bg-red-50 p-3 rounded border border-red-200">{(currentBug as any).actual_result}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Linked Items */}
      {((currentBug as any).linked_task_id || (currentBug as any).linked_commit || (currentBug as any).linked_pr) && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Linked Items</h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="grid grid-cols-3 gap-4">
              {(currentBug as any).linked_task_id && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Linked Task
                  </h4>
                  <p className="text-blue-600 font-mono text-sm hover:underline cursor-pointer">{(currentBug as any).linked_task_id}</p>
                </div>
              )}
              
              {(currentBug as any).linked_commit && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                    Linked Commit
                  </h4>
                  <p className="text-blue-600 font-mono text-sm hover:underline cursor-pointer">{(currentBug as any).linked_commit}</p>
                </div>
              )}
              
              {(currentBug as any).linked_pr && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                    </svg>
                    Pull Request
                  </h4>
                  <p className="text-blue-600 font-mono text-sm hover:underline cursor-pointer">{(currentBug as any).linked_pr}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Resolution Notes */}
      {currentBug.resolution_notes && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Resolution Notes</h3>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-900 whitespace-pre-wrap">{currentBug.resolution_notes}</p>
            {currentBug.closed_at && (
              <p className="text-sm text-green-700 mt-2">
                Resolved on {formatDate(currentBug.closed_at)}
              </p>
            )}
          </div>
        </div>
      )}
      
      {/* Category and Component */}
      <div className="grid grid-cols-2 gap-4">
        {(currentBug as any).category && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-1">Category</h3>
            <p className="text-gray-900">{(currentBug as any).category}</p>
          </div>
        )}
        
        {(currentBug as any).component_attached_to && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-1">Component</h3>
            <p className="text-gray-900">{(currentBug as any).component_attached_to}</p>
          </div>
        )}
      </div>
      
      {/* Reproduction Path */}
      {((currentBug as any).reproduction_steps || (currentBug as any).expected_result || (currentBug as any).actual_result) && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Reproduction Path</h3>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
            {(currentBug as any).reproduction_steps && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-1">Steps to Reproduce</h4>
                <p className="text-gray-900 whitespace-pre-wrap">{(currentBug as any).reproduction_steps}</p>
              </div>
            )}
            
            {(currentBug as any).expected_result && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-1">Expected Result</h4>
                <p className="text-gray-900 whitespace-pre-wrap">{(currentBug as any).expected_result}</p>
              </div>
            )}
            
            {(currentBug as any).actual_result && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-1">Actual Result</h4>
                <p className="text-gray-900 whitespace-pre-wrap">{(currentBug as any).actual_result}</p>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Linked Items */}
      {((currentBug as any).linked_task_id || (currentBug as any).linked_commit || (currentBug as any).linked_pr) && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Linked Items</h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="grid grid-cols-3 gap-4">
              {(currentBug as any).linked_task_id && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-1">Linked Task</h4>
                  <p className="text-blue-600 font-mono text-sm">{(currentBug as any).linked_task_id}</p>
                </div>
              )}
              
              {(currentBug as any).linked_commit && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-1">Linked Commit</h4>
                  <p className="text-blue-600 font-mono text-sm">{(currentBug as any).linked_commit}</p>
                </div>
              )}
              
              {(currentBug as any).linked_pr && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-1">Linked Pull Request</h4>
                  <p className="text-blue-600 font-mono text-sm">{(currentBug as any).linked_pr}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Additional Bug Information */}
      <div className="grid grid-cols-2 gap-4">
        {/* Bug Type */}
        {(currentBug as any).bug_type && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-1">Bug Type</h3>
            <p className="text-gray-900">{(currentBug as any).bug_type}</p>
          </div>
        )}
        
        {/* Environment */}
        {((currentBug as any).browser || (currentBug as any).os || (currentBug as any).device_type) && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-1">Environment</h3>
            <p className="text-gray-900">
              {[(currentBug as any).browser, (currentBug as any).os, (currentBug as any).device_type].filter(Boolean).join(', ')}
            </p>
          </div>
        )}
        
        {/* Versions */}
        {((currentBug as any).found_in_version || (currentBug as any).fixed_in_version) && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-1">Versions</h3>
            <p className="text-gray-900">
              {(currentBug as any).found_in_version && `Found in: ${(currentBug as any).found_in_version}`}
              {(currentBug as any).found_in_version && (currentBug as any).fixed_in_version && ' | '}
              {(currentBug as any).fixed_in_version && `Fixed in: ${(currentBug as any).fixed_in_version}`}
            </p>
          </div>
        )}
      </div>
      
      {/* Linked Test Cases */}
      {linkedTestCases.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Linked Test Cases</h3>
          <div className="space-y-2">
            {linkedTestCases.map(testCase => (
              <div key={testCase.id} className="bg-white border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{testCase.title}</p>
                    <p className="text-sm text-gray-600">{testCase.test_type} - {testCase.priority}</p>
                  </div>
                  <button
                    onClick={() => {/* Navigate to test case */}}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    View →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Status History Timeline */}
      {statusHistory.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Status History</h3>
          <div className="space-y-3">
            {statusHistory.map((history, index) => (
              <div key={history.id} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                  {index < statusHistory.length - 1 && (
                    <div className="w-0.5 h-full bg-gray-300 mt-1"></div>
                  )}
                </div>
                <div className="flex-1 pb-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-900">
                        {history.from_status ? `${history.from_status} → ${history.to_status}` : history.to_status}
                      </span>
                      <span className="text-xs text-gray-500">{formatDate(history.changed_at)}</span>
                    </div>
                    <p className="text-sm text-gray-600">Changed by {history.changed_by}</p>
                    {history.resolution_type && (
                      <p className="text-sm text-gray-600 mt-1">Resolution: {history.resolution_type}</p>
                    )}
                    {history.notes && (
                      <p className="text-sm text-gray-700 mt-2">{history.notes}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Comments Section */}
      <CommentsSection
        entityType="bug"
        entityId={currentBug.id}
        showSystemNotes={true}
      />
      
      {/* Attachments Section */}
      <AttachmentsSection
        entityType="bug"
        entityId={currentBug.id}
        onAttachmentAdded={() => {
          // Optionally refresh bug details or show notification
          console.log('Attachment added to bug:', currentBug.id)
        }}
      />
      
      {/* Actions */}
      <div className="flex items-center gap-3 pt-4 border-t">
        <button
          onClick={() => setIsStatusUpdateModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Update Status
        </button>
        
        {canAssign && (
          <button
            onClick={() => setIsAssignModalOpen(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
            Assign Bug
          </button>
        )}
        
        {canResolve && (
          <button
            onClick={() => setIsResolveModalOpen(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Resolve Bug
          </button>
        )}
        
        {currentBug.status === 'Closed' && (
          <button
            onClick={async () => {
              try {
                await api.updateEntity('bug', currentBug.id, { status: 'Reopened' })
                if (onUpdate) onUpdate()
              } catch (error) {
                console.error('Failed to reopen bug:', error)
              }
            }}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Reopen Bug
          </button>
        )}
      </div>
      
      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Bug"
        size="lg"
      >
        <BugForm
          initialData={currentBug}
          onSubmit={handleUpdateBug}
          onCancel={() => setIsEditModalOpen(false)}
          isLoading={loading}
          mode="edit"
        />
      </Modal>
      
      {/* Assign Modal */}
      <Modal
        isOpen={isAssignModalOpen}
        onClose={() => setIsAssignModalOpen(false)}
        title="Assign Bug"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label htmlFor="assignee" className="block text-sm font-medium mb-2">
              Select Assignee
            </label>
            <select
              id="assignee"
              value={selectedAssignee}
              onChange={(e) => setSelectedAssignee(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a user</option>
              {users.filter(u => u.role === 'Developer' || u.role === 'Tester').map(user => (
                <option key={user.id} value={user.id}>
                  {user.fullName || user.full_name} ({user.role})
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              onClick={() => setIsAssignModalOpen(false)}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              onClick={handleAssignBug}
              className="px-4 py-2 text-white bg-purple-600 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
              disabled={loading || !selectedAssignee}
            >
              {loading ? 'Assigning...' : 'Assign'}
            </button>
          </div>
        </div>
      </Modal>
      
      {/* Resolve Modal */}
      <Modal
        isOpen={isResolveModalOpen}
        onClose={() => setIsResolveModalOpen(false)}
        title="Resolve Bug"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label htmlFor="resolution_notes" className="block text-sm font-medium mb-2">
              Resolution Notes <span className="text-red-500">*</span>
            </label>
            <textarea
              id="resolution_notes"
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe how the bug was fixed..."
            />
          </div>
          
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              onClick={() => setIsResolveModalOpen(false)}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              onClick={handleResolveBug}
              className="px-4 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              disabled={loading || !resolutionNotes.trim()}
            >
              {loading ? 'Resolving...' : 'Resolve Bug'}
            </button>
          </div>
        </div>
      </Modal>
      
      {/* Status Update Modal */}
      <Modal
        isOpen={isStatusUpdateModalOpen}
        onClose={() => setIsStatusUpdateModalOpen(false)}
        title="Update Bug Status"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label htmlFor="status" className="block text-sm font-medium mb-2">
              New Status <span className="text-red-500">*</span>
            </label>
            <select
              id="status"
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select status</option>
              <option value="New">New</option>
              <option value="Open">Open</option>
              <option value="In Progress">In Progress</option>
              <option value="Fixed">Fixed</option>
              <option value="Ready for Testing">Ready for Testing</option>
              <option value="Retest">Retest</option>
              <option value="Verified">Verified</option>
              <option value="Closed">Closed</option>
              <option value="Reopened">Reopened</option>
              <option value="Deferred">Deferred</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>
          
          {selectedStatus === 'Fixed' && (
            <div>
              <label htmlFor="resolution_type" className="block text-sm font-medium mb-2">
                Resolution Type <span className="text-red-500">*</span>
              </label>
              <select
                id="resolution_type"
                value={resolutionType}
                onChange={(e) => setResolutionType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select resolution type</option>
                <option value="Fixed">Fixed</option>
                <option value="Duplicate">Duplicate</option>
                <option value="Cannot Reproduce">Cannot Reproduce</option>
                <option value="Won't Fix">Won't Fix</option>
                <option value="By Design">By Design</option>
              </select>
            </div>
          )}
          
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              onClick={() => {
                setIsStatusUpdateModalOpen(false)
                setSelectedStatus('')
                setResolutionType('')
              }}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              onClick={handleStatusUpdate}
              className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              disabled={loading || !selectedStatus || (selectedStatus === 'Fixed' && !resolutionType)}
            >
              {loading ? 'Updating...' : 'Update Status'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
