/**
 * MessageCard Component
 * Displays entity information as rich cards with deep links
 * Requirements: 8.1, 8.2
 */

import { useNavigate } from 'react-router-dom'

export interface EntityCard {
  entity_type: string
  entity_id: string
  title: string
  status?: string
  assignee?: string
  due_date?: string
  priority?: string
  deep_link?: string
  metadata?: Record<string, any>
}

interface MessageCardProps {
  card: EntityCard
}

export default function MessageCard({ card }: MessageCardProps) {
  const navigate = useNavigate()

  const handleCardClick = () => {
    if (card.deep_link) {
      navigate(card.deep_link)
    }
  }

  const getEntityIcon = (entityType: string) => {
    switch (entityType.toLowerCase()) {
      case 'project':
        return (
          <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
        )
      case 'task':
        return (
          <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        )
      case 'subtask':
        return (
          <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        )
      case 'bug':
        return (
          <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
      case 'user_story':
        return (
          <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        )
      case 'usecase':
        return (
          <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        )
      case 'test_case':
        return (
          <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      default:
        return (
          <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        )
    }
  }

  const getStatusColor = (status?: string) => {
    if (!status) return 'bg-gray-100 text-gray-700'
    
    const statusLower = status.toLowerCase()
    if (statusLower.includes('done') || statusLower.includes('completed') || statusLower.includes('closed')) {
      return 'bg-green-100 text-green-700'
    }
    if (statusLower.includes('progress')) {
      return 'bg-blue-100 text-blue-700'
    }
    if (statusLower.includes('blocked') || statusLower.includes('failed')) {
      return 'bg-red-100 text-red-700'
    }
    if (statusLower.includes('hold') || statusLower.includes('pending')) {
      return 'bg-yellow-100 text-yellow-700'
    }
    return 'bg-gray-100 text-gray-700'
  }

  const getPriorityColor = (priority?: string) => {
    if (!priority) return 'text-gray-500'
    
    const priorityLower = priority.toLowerCase()
    if (priorityLower.includes('critical') || priorityLower === 'p0' || priorityLower === 'high') {
      return 'text-red-600'
    }
    if (priorityLower === 'p1' || priorityLower === 'medium') {
      return 'text-orange-600'
    }
    if (priorityLower === 'p2' || priorityLower === 'low') {
      return 'text-yellow-600'
    }
    if (priorityLower === 'p3') {
      return 'text-gray-600'
    }
    return 'text-gray-500'
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return null
    
    try {
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = date.getTime() - now.getTime()
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) {
        return { text: `${Math.abs(diffDays)}d overdue`, color: 'text-red-600' }
      } else if (diffDays === 0) {
        return { text: 'Due today', color: 'text-orange-600' }
      } else if (diffDays === 1) {
        return { text: 'Due tomorrow', color: 'text-orange-600' }
      } else if (diffDays <= 7) {
        return { text: `Due in ${diffDays}d`, color: 'text-yellow-600' }
      } else {
        return { text: date.toLocaleDateString(), color: 'text-gray-600' }
      }
    } catch {
      return null
    }
  }

  const dueDate = formatDate(card.due_date)

  return (
    <div
      onClick={handleCardClick}
      className={`
        message-card
        ${card.deep_link ? 'cursor-pointer hover:shadow-md' : ''}
      `}
      role={card.deep_link ? 'button' : 'article'}
      tabIndex={card.deep_link ? 0 : undefined}
      onKeyPress={(e) => {
        if (card.deep_link && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault()
          handleCardClick()
        }
      }}
    >
      <div className="message-card-header">
        <div className="message-card-icon">
          {getEntityIcon(card.entity_type)}
        </div>
        <div className="message-card-type">
          {card.entity_type.replace('_', ' ')}
        </div>
      </div>

      <div className="message-card-body">
        <h4 className="message-card-title">{card.title}</h4>
        
        <div className="message-card-details">
          {card.status && (
            <span className={`message-card-badge ${getStatusColor(card.status)}`}>
              {card.status}
            </span>
          )}
          
          {card.priority && (
            <span className={`message-card-priority ${getPriorityColor(card.priority)}`}>
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              {card.priority}
            </span>
          )}
        </div>

        {(card.assignee || dueDate) && (
          <div className="message-card-meta">
            {card.assignee && (
              <div className="message-card-meta-item">
                <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>{card.assignee}</span>
              </div>
            )}
            
            {dueDate && (
              <div className={`message-card-meta-item ${dueDate.color}`}>
                <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>{dueDate.text}</span>
              </div>
            )}
          </div>
        )}

        {card.metadata && Object.keys(card.metadata).length > 0 && (
          <div className="message-card-metadata">
            {Object.entries(card.metadata).slice(0, 3).map(([key, value]) => (
              <div key={key} className="message-card-metadata-item">
                <span className="message-card-metadata-key">{key}:</span>
                <span className="message-card-metadata-value">{String(value)}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {card.deep_link && (
        <div className="message-card-footer">
          <span className="message-card-link">
            View details
            <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </div>
      )}
    </div>
  )
}
