import React, { useState, useEffect } from 'react';
import api from '../../services/api';

interface DecisionFormProps {
  onSubmit: (data: {
    note_text: string;
    entity_type: string;
    entity_id: string;
    decision_status: string;
  }) => void;
  onCancel: () => void;
  isLoading: boolean;
}

interface Entity {
  id: string;
  name?: string;
  title?: string;
}

const DecisionForm: React.FC<DecisionFormProps> = ({ onSubmit, onCancel, isLoading }) => {
  const [formData, setFormData] = useState({
    note_text: '',
    entity_type: 'Client',
    entity_id: '',
    decision_status: 'Active'
  });

  const [entities, setEntities] = useState<Entity[]>([]);
  const [loadingEntities, setLoadingEntities] = useState(false);

  const entityTypes = [
    { value: 'Client', label: 'Client' },
    { value: 'Project', label: 'Project' },
    { value: 'UseCase', label: 'Use Case' },
    { value: 'UserStory', label: 'User Story' },
    { value: 'Task', label: 'Task' },
    { value: 'Subtask', label: 'Subtask' }
  ];

  const statusOptions = [
    { value: 'Active', label: 'Active' },
    { value: 'Canceled', label: 'Canceled' },
    { value: 'Postponed', label: 'Postponed' },
    { value: 'On-Hold', label: 'On-Hold' },
    { value: 'Closed', label: 'Closed' }
  ];

  // Load entities when entity type changes
  useEffect(() => {
    loadEntities();
  }, [formData.entity_type]);

  const loadEntities = async () => {
    setLoadingEntities(true);
    try {
      let entityList: Entity[] = [];
      
      switch (formData.entity_type) {
        case 'Client':
          entityList = await api.getClients();
          break;
        case 'Project':
          entityList = (await api.getProjects()).filter(p => p !== null);
          break;
        case 'UseCase':
          entityList = (await api.getUseCases()).filter(uc => uc !== null);
          break;
        case 'UserStory':
          entityList = await api.getUserStories();
          break;
        case 'Task':
          entityList = await api.getTasks();
          break;
        case 'Subtask':
          entityList = await api.getSubtasks();
          break;
        default:
          entityList = [];
      }
      
      setEntities(entityList || []);
      
      // Reset entity_id when changing types
      setFormData(prev => ({ ...prev, entity_id: '' }));
    } catch (error) {
      console.error('Failed to load entities:', error);
      setEntities([]);
    } finally {
      setLoadingEntities(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.note_text.trim() || !formData.entity_id) {
      return;
    }
    onSubmit(formData);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Create New Decision</h2>
        <button
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Decision Text */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Decision Description *
          </label>
          <textarea
            value={formData.note_text}
            onChange={(e) => handleInputChange('note_text', e.target.value)}
            placeholder="Describe the decision made..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        {/* Entity Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Entity Type *
          </label>
          <select
            value={formData.entity_type}
            onChange={(e) => handleInputChange('entity_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          >
            {entityTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Entity Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select {formData.entity_type} *
          </label>
          {loadingEntities ? (
            <div className="flex items-center justify-center py-3 border border-gray-300 rounded-md">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-sm text-gray-600">Loading...</span>
            </div>
          ) : (
            <select
              value={formData.entity_id}
              onChange={(e) => handleInputChange('entity_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select {formData.entity_type}...</option>
              {entities.map((entity) => (
                <option key={entity.id} value={entity.id}>
                  {entity.name || entity.title || entity.id}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Decision Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            value={formData.decision_status}
            onChange={(e) => handleInputChange('decision_status', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {statusOptions.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>

        {/* Form Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading || !formData.note_text.trim() || !formData.entity_id}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating...
              </div>
            ) : (
              'Create Decision'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default DecisionForm;