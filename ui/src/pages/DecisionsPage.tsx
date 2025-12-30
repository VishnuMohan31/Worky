import React, { useState, useEffect } from 'react';
import DecisionList from '../components/decisions/DecisionList';
import DecisionForm from '../components/decisions/DecisionForm';
import api from '../services/api';

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

interface DecisionStats {
  total_decisions: number;
  by_status: Record<string, number>;
  by_entity_type: Record<string, number>;
}

const DecisionsPage: React.FC = () => {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [stats, setStats] = useState<DecisionStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [filters, setFilters] = useState({
    entity_type: '',
    decision_status: ''
  });

  // Load decisions and stats
  const loadData = async () => {
    try {
      setIsLoading(true);
      
      // Build query parameters
      const params = new URLSearchParams();
      if (filters.entity_type) params.append('entity_type', filters.entity_type);
      if (filters.decision_status) params.append('decision_status', filters.decision_status);
      
      // Load decisions and stats in parallel
      const [decisionsResponse, statsResponse] = await Promise.all([
        api.get(`/decisions/?${params.toString()}`),
        api.get('/decisions/stats')
      ]);
      
      setDecisions(Array.isArray(decisionsResponse) ? decisionsResponse : []);
      setStats(statsResponse || {});
    } catch (error) {
      console.error('Error loading decisions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters]);

  // Create new decision
  const handleCreateDecision = async (decisionData: {
    note_text: string;
    entity_type: string;
    entity_id: string;
    decision_status: string;
  }) => {
    try {
      setIsCreating(true);
      await api.post('/decisions/', decisionData);
      setShowCreateForm(false);
      await loadData(); // Reload data
    } catch (error) {
      console.error('Error creating decision:', error);
      alert('Failed to create decision. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  // Update decision status
  const handleStatusUpdate = async (decisionId: string, newStatus: string) => {
    try {
      await api.put(`/decisions/${decisionId}/status`, {
        decision_status: newStatus
      });
      await loadData(); // Reload data
    } catch (error) {
      console.error('Error updating decision status:', error);
      alert('Failed to update decision status. Please try again.');
    }
  };

  // Filter options
  const entityTypes = ['Client', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask'];
  const decisionStatuses = ['Active', 'Canceled', 'Postponed', 'On-Hold', 'Closed'];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Decisions</h1>
              <p className="mt-2 text-gray-600">
                Track and manage decisions across all project entities
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            >
              <svg
                className="w-5 h-5 inline-block mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              New Decision
            </button>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-2xl font-bold text-blue-600">{stats.total_decisions}</div>
                <div className="text-sm text-gray-600">Total Decisions</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-2xl font-bold text-green-600">
                  {stats.by_status.Active || 0}
                </div>
                <div className="text-sm text-gray-600">Active</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-2xl font-bold text-yellow-600">
                  {(stats.by_status.Postponed || 0) + (stats.by_status['On-Hold'] || 0)}
                </div>
                <div className="text-sm text-gray-600">Pending</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-2xl font-bold text-gray-600">
                  {(stats.by_status.Closed || 0) + (stats.by_status.Canceled || 0)}
                </div>
                <div className="text-sm text-gray-600">Resolved</div>
              </div>
            </div>
          )}
        </div>

        {/* Create Form Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
              <div className="p-6">
                <DecisionForm
                  onSubmit={handleCreateDecision}
                  onCancel={() => setShowCreateForm(false)}
                  isLoading={isCreating}
                />
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow mb-6 p-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-48">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Entity Type
              </label>
              <select
                value={filters.entity_type}
                onChange={(e) => setFilters(prev => ({ ...prev, entity_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                {entityTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div className="flex-1 min-w-48">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filters.decision_status}
                onChange={(e) => setFilters(prev => ({ ...prev, decision_status: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                {decisionStatuses.map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={() => setFilters({ entity_type: '', decision_status: '' })}
                className="px-4 py-2 text-sm text-gray-600 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Decisions List */}
        <DecisionList
          decisions={decisions}
          onStatusUpdate={handleStatusUpdate}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
};

export default DecisionsPage;