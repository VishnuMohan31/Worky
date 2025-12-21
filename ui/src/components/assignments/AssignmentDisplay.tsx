import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../../services/api';

interface Assignment {
  id: string;
  entity_type: string;
  entity_id: string;
  user_id: string;
  assignment_type: string;
  assigned_at: string;
  is_active: boolean;
  user_name?: string;
  user_email?: string;
  entity_name?: string;
}

interface AssignmentDisplayProps {
  entityType: string;
  entityId: string;
  showActions?: boolean;
  onAssignmentChange?: () => void;
}

export const AssignmentDisplay: React.FC<AssignmentDisplayProps> = ({
  entityType,
  entityId,
  showActions = false,
  onAssignmentChange
}) => {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(false);
  const loadTimeoutRef = useRef<NodeJS.Timeout>();

  const loadAssignments = useCallback(async () => {
    // Clear any existing timeout
    if (loadTimeoutRef.current) {
      clearTimeout(loadTimeoutRef.current);
    }

    // Debounce the API call
    loadTimeoutRef.current = setTimeout(async () => {
      try {
        setLoading(true);
        const response = await api.getAssignments(entityType, entityId);
        setAssignments(response);
      } catch (error) {
        console.error('Failed to load assignments:', error);
      } finally {
        setLoading(false);
      }
    }, 100); // 100ms debounce
  }, [entityType, entityId]);

  useEffect(() => {
    loadAssignments();

    // Cleanup timeout on unmount
    return () => {
      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current);
      }
    };
  }, [loadAssignments]);

  const handleRemoveAssignment = async (assignmentId: string) => {
    try {
      await api.deleteAssignment(assignmentId);
      
      alert('Assignment removed successfully');
      
      loadAssignments();
      onAssignmentChange?.();
    } catch (error: any) {
      console.error('Failed to remove assignment:', error);
      alert(error.response?.data?.detail || 'Failed to remove assignment');
    }
  };

  const getAssignmentTypeIcon = (type: string) => {
    switch (type) {
      case 'owner':
        return '🛡️';
      case 'contact_person':
        return '👤';
      case 'developer':
        return '💻';
      default:
        return '👤';
    }
  };

  const getAssignmentTypeColor = (type: string) => {
    switch (type) {
      case 'owner':
        return 'bg-red-100 text-red-800';
      case 'contact_person':
        return 'bg-blue-100 text-blue-800';
      case 'developer':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getAssignmentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'owner': 'Owner',
      'contact_person': 'Contact Person',
      'developer': 'Developer'
    };
    return labels[type] || type;
  };

  const getInitials = (name?: string) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="p-6">
          <div className="text-center">Loading assignments...</div>
        </div>
      </div>
    );
  }

  if (assignments.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Current Assignments</h3>
        </div>
        <div className="p-6">
          <div className="text-center py-4 text-gray-500 text-sm">
            No assignments found
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-sm font-medium text-gray-900">Current Assignments ({assignments.length})</h3>
      </div>
      <div className="p-6">
        <div className="space-y-3">
          {assignments.map((assignment) => (
            <div
              key={assignment.id}
              className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                  <span className="text-xs font-medium text-gray-600">
                    {getInitials(assignment.user_name)}
                  </span>
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-sm text-gray-900">{assignment.user_name || 'Unknown User'}</span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getAssignmentTypeColor(assignment.assignment_type)}`}>
                      <span className="flex items-center">
                        <span className="mr-1">{getAssignmentTypeIcon(assignment.assignment_type)}</span>
                        <span>{getAssignmentTypeLabel(assignment.assignment_type)}</span>
                      </span>
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-3 mt-1 text-xs text-gray-500">
                    {assignment.user_email && (
                      <div className="flex items-center">
                        <span className="mr-1">📧</span>
                        {assignment.user_email}
                      </div>
                    )}
                    <div className="flex items-center">
                      <span className="mr-1">📅</span>
                      {formatDate(assignment.assigned_at)}
                    </div>
                  </div>
                </div>
              </div>

              {showActions && (
                <button
                  onClick={() => handleRemoveAssignment(assignment.id)}
                  className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
                  title="Remove assignment"
                >
                  🗑️
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};