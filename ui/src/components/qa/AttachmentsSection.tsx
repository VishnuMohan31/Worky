/**
 * AttachmentsSection Component
 * Displays list of attachments (screenshots, logs, videos)
 * Shows file name, type, size, uploader
 * Provides upload, download, and delete actions
 * Requirements: 6.12
 */
import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import api from '../../services/api'

interface Attachment {
  id: string
  file_name: string
  file_path: string
  file_type: string
  file_size: number
  uploaded_by: string
  uploader_name?: string
  uploaded_at: string
  is_deleted: boolean
}

interface AttachmentsSectionProps {
  entityType: 'bug' | 'test_case'
  entityId: string
  onAttachmentAdded?: () => void
}

export default function AttachmentsSection({
  entityType,
  entityId,
  onAttachmentAdded
}: AttachmentsSectionProps) {
  const { user } = useAuth()
  const [attachments, setAttachments] = useState<Attachment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  useEffect(() => {
    loadAttachments()
  }, [entityType, entityId])
  
  const loadAttachments = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const endpoint = entityType === 'bug'
        ? `/bugs/${entityId}/attachments`
        : `/test-cases/${entityId}/attachments`
      
      const data = await api.get(endpoint)
      setAttachments(data)
    } catch (err: any) {
      console.error('Failed to load attachments:', err)
      setError(err.message || 'Failed to load attachments')
      setAttachments([])
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return
    
    setIsUploading(true)
    setError(null)
    setUploadProgress(0)
    
    try {
      const endpoint = entityType === 'bug'
        ? `/bugs/${entityId}/attachments`
        : `/test-cases/${entityId}/attachments`
      
      // Upload files one by one
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        const formData = new FormData()
        formData.append('file', file)
        
        // Simulate progress (in real implementation, use axios onUploadProgress)
        setUploadProgress(Math.round(((i + 0.5) / files.length) * 100))
        
        await api.post(endpoint, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        setUploadProgress(Math.round(((i + 1) / files.length) * 100))
      }
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      
      // Reload attachments
      await loadAttachments()
      
      if (onAttachmentAdded) {
        onAttachmentAdded()
      }
    } catch (err: any) {
      console.error('Failed to upload attachments:', err)
      setError(err.message || 'Failed to upload attachments')
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }
  
  const handleDownload = async (attachment: Attachment) => {
    try {
      // In a real implementation, this would download the file from the server
      // For now, we'll just open the file path
      window.open(attachment.file_path, '_blank')
    } catch (err: any) {
      console.error('Failed to download attachment:', err)
      setError(err.message || 'Failed to download attachment')
    }
  }
  
  const handleDelete = async (attachmentId: string) => {
    if (!confirm('Are you sure you want to delete this attachment?')) return
    
    setError(null)
    
    try {
      await api.delete(`/attachments/${attachmentId}`)
      await loadAttachments()
    } catch (err: any) {
      console.error('Failed to delete attachment:', err)
      setError(err.message || 'Failed to delete attachment')
    }
  }
  
  const canDeleteAttachment = (attachment: Attachment) => {
    return attachment.uploaded_by === user?.id || user?.role === 'Admin'
  }
  
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) {
      return (
        <svg className="w-8 h-8 text-blue-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      )
    } else if (fileType.startsWith('video/')) {
      return (
        <svg className="w-8 h-8 text-purple-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      )
    } else if (fileType === 'application/pdf') {
      return (
        <svg className="w-8 h-8 text-red-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      )
    } else if (fileType.includes('text') || fileType.includes('log')) {
      return (
        <svg className="w-8 h-8 text-gray-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      )
    } else {
      return (
        <svg className="w-8 h-8 text-gray-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      )
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">Loading attachments...</div>
      </div>
    )
  }
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Attachments ({attachments.length})
        </h3>
        
        <div>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileSelect}
            className="hidden"
            accept="image/*,video/*,.pdf,.txt,.log,.json,.xml"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isUploading ? (
              <>
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading... {uploadProgress}%
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Upload Files
              </>
            )}
          </button>
        </div>
      </div>
      
      {/* Upload Progress Bar */}
      {isUploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">Uploading files...</span>
            <span className="text-sm text-blue-700">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}
      
      {/* Attachments List */}
      {attachments.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="text-gray-400 text-4xl mb-2">📎</div>
          <p className="text-gray-600">No attachments yet</p>
          <p className="text-gray-500 text-sm mt-1">Upload screenshots, logs, or videos to help document this {entityType === 'bug' ? 'bug' : 'test case'}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              {/* File Icon and Name */}
              <div className="flex items-start gap-3 mb-3">
                <div className="flex-shrink-0">
                  {getFileIcon(attachment.file_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate" title={attachment.file_name}>
                    {attachment.file_name}
                  </h4>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatFileSize(attachment.file_size)}
                  </p>
                </div>
              </div>
              
              {/* File Type Badge */}
              <div className="mb-3">
                <span className="inline-block px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-700">
                  {attachment.file_type.split('/')[1]?.toUpperCase() || 'FILE'}
                </span>
              </div>
              
              {/* Uploader Info */}
              <div className="flex items-center gap-2 mb-3 text-xs text-gray-600">
                <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>{attachment.uploader_name || 'Unknown'}</span>
                <span>•</span>
                <span>{formatDate(attachment.uploaded_at)}</span>
              </div>
              
              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDownload(attachment)}
                  className="flex-1 px-3 py-1.5 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors flex items-center justify-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download
                </button>
                
                {canDeleteAttachment(attachment) && (
                  <button
                    onClick={() => handleDelete(attachment.id)}
                    className="px-3 py-1.5 text-sm text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                    title="Delete attachment"
                  >
                    <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
              </div>
              
              {/* Image Preview for image files */}
              {attachment.file_type.startsWith('image/') && (
                <div className="mt-3 rounded-lg overflow-hidden border border-gray-200">
                  <img
                    src={attachment.file_path}
                    alt={attachment.file_name}
                    className="w-full h-32 object-cover cursor-pointer hover:opacity-90 transition-opacity"
                    onClick={() => handleDownload(attachment)}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      
      {/* File Type Info */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
        <p className="text-xs text-gray-600">
          <span className="font-medium">Supported file types:</span> Images (PNG, JPG, GIF), Videos (MP4, MOV), Documents (PDF), Logs (TXT, LOG, JSON, XML)
        </p>
        <p className="text-xs text-gray-600 mt-1">
          <span className="font-medium">Maximum file size:</span> 10 MB per file
        </p>
      </div>
    </div>
  )
}
