import React from 'react';

interface Decision {
  id: string;
  entity_type: string;
  entity_id: string;
  entity_name?: string;
  note_text: string;
  decision_status: string;
  created_by: string;
  created_at: string;
  creator_name?: string;
}

interface DecisionListProps {
  decisions: Decision[];
  onStatusUpdate: (decisionId: string, newStatus: string) => void;
  isLoading: boolean;
}

const DecisionList: React.FC<DecisionListProps> = ({ decisions, onStatusUpdate, isLoading }) => {
  const statusColors = {
    'Active': 'bg-green-100 text-green-800',
    'Canceled': 'bg-red-100 text-red-800',
    'Postponed': 'bg-yellow-100 text-yellow-800',
    'On-Hold': 'bg-orange-100 text-orange-800',
    'Closed': 'bg-gray-100 text-gray-800'
  };

  const statusOptions = ['Active', 'Canceled', 'Postponed', 'On-Hold', 'Closed'];

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading decisions...</p>
        </div>
      </div>
    );
  }

  if (decisions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No decisions found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new decision.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="divide-y divide-gray-200">
        {decisions.map((decision) => (
          <div key={decision.id} className="p-6 hover:bg-gray-50">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                {/* Decision Header */}
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-sm font-medium text-gray-900">
                    {decision.entity_type}
                  </span>
                  <span className="text-sm text-gray-500">
                    {decision.entity_name || decision.entity_id}
                  </span>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    statusColors[decision.decision_status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'
                  }`}>
                    {decision.decision_status}
                  </span>
                </div>

                {/* Decision Content */}
                <p className="text-gray-900 mb-3">{decision.note_text}</p>

                {/* Decision Meta */}
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>
                    By {decision.creator_name || 'Unknown User'}
                  </span>
                  <span>
                    {new Date(decision.created_at).toLocaleDateString()} at{' '}
                    {new Date(decision.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>

              {/* Status Update Dropdown */}
              <div className="ml-4 flex-shrink-0">
                <select
                  value={decision.decision_status}
                  onChange={(e) => onStatusUpdate(decision.id, e.target.value)}
                  className="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {statusOptions.map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DecisionList;