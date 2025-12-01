/**
 * ActionButton Component
 * Renders clickable action buttons for chat responses
 * Requirements: 8.3
 */

import { useNavigate } from 'react-router-dom'

export interface UIAction {
  action_type: string
  label: string
  entity_type?: string
  entity_id?: string
  deep_link?: string
  parameters?: Record<string, any>
}

interface ActionButtonProps {
  action: UIAction
  onActionClick?: (action: UIAction) => void
}

export default function ActionButton({ action, onActionClick }: ActionButtonProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    // Call custom handler if provided
    if (onActionClick) {
      onActionClick(action)
      return
    }

    // Default behavior based on action type
    switch (action.action_type) {
      case 'view_entity':
        if (action.deep_link) {
          navigate(action.deep_link)
        }
        break
      
      case 'set_reminder':
        // This would typically open a reminder modal
        console.log('Set reminder action:', action)
        break
      
      case 'update_status':
        // This would typically open a status update modal
        console.log('Update status action:', action)
        break
      
      case 'create_comment':
        // This would typically open a comment modal
        console.log('Create comment action:', action)
        break
      
      case 'link_commit':
        // This would typically open a commit linking modal
        console.log('Link commit action:', action)
        break
      
      case 'suggest_report':
        if (action.deep_link) {
          navigate(action.deep_link)
        }
        break
      
      default:
        console.log('Unknown action type:', action.action_type)
    }
  }

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case 'view_entity':
        return (
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        )
      
      case 'set_reminder':
        return (
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        )
      
      case 'update_status':
        return (
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        )
      
      case 'create_comment':
        return (
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
          </svg>
        )
      
      case 'link_commit':
        return (
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
        )
      
      case 'suggest_report':
        return (
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        )
      
      default:
        return (
          <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        )
    }
  }

  const getActionStyle = (actionType: string) => {
    switch (actionType) {
      case 'view_entity':
        return 'action-button-primary'
      
      case 'set_reminder':
        return 'action-button-info'
      
      case 'update_status':
        return 'action-button-warning'
      
      case 'create_comment':
        return 'action-button-secondary'
      
      case 'link_commit':
        return 'action-button-secondary'
      
      case 'suggest_report':
        return 'action-button-success'
      
      default:
        return 'action-button-default'
    }
  }

  return (
    <button
      onClick={handleClick}
      className={`action-button ${getActionStyle(action.action_type)}`}
      title={action.action_type.replace('_', ' ')}
    >
      {getActionIcon(action.action_type)}
      <span>{action.label}</span>
    </button>
  )
}
