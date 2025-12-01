/**
 * API Service Integration Tests for Subtasks
 * 
 * This test file verifies that the API service correctly handles subtask operations:
 * - getSubtasks() method exists and works
 * - createEntity('subtask', data) works
 * - updateEntity('subtask', id, data) works
 * - Error handling and response parsing
 * 
 * Requirements: 4.11, 4.12
 */

import api from '../api';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Service - Subtask Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'mock-token');
  });

  describe('getSubtasks', () => {
    it('should fetch subtasks without filters', async () => {
      const mockSubtasks = [
        {
          id: 'subtask-1',
          task_id: 'task-1',
          title: 'Test Subtask 1',
          status: 'To Do',
          estimated_hours: 4,
          duration_days: 2
        },
        {
          id: 'subtask-2',
          task_id: 'task-1',
          title: 'Test Subtask 2',
          status: 'In Progress',
          estimated_hours: 8,
          duration_days: 3
        }
      ];

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn().mockResolvedValue({ data: mockSubtasks }),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() }
        }
      } as any));

      const result = await api.getSubtasks();
      
      expect(result).toEqual(mockSubtasks);
      expect(result).toHaveLength(2);
      expect(result[0].title).toBe('Test Subtask 1');
    });

    it('should fetch subtasks filtered by task_id', async () => {
      const mockSubtasks = [
        {
          id: 'subtask-1',
          task_id: 'task-123',
          title: 'Filtered Subtask',
          status: 'Done',
          estimated_hours: 2,
          duration_days: 1
        }
      ];

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn().mockResolvedValue({ data: mockSubtasks }),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() }
        }
      } as any));

      const result = await api.getSubtasks('task-123');
      
      expect(result).toEqual(mockSubtasks);
      expect(result[0].task_id).toBe('task-123');
    });

    it('should handle empty subtask list', async () => {
      mockedAxios.create = jest.fn(() => ({
        get: jest.fn().mockResolvedValue({ data: [] }),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() }
        }
      } as any));

      const result = await api.getSubtasks('task-999');
      
      expect(result).toEqual([]);
      expect(result).toHaveLength(0);
    });
  });

  describe('createEntity - subtask', () => {
    it('should create a new subtask with required fields', async () => {
      const newSubtaskData = {
        task_id: 'task-1',
        title: 'New Subtask',
        status: 'To Do',
        estimated_hours: 5,
        duration_days: 2
      };

      const mockCreatedSubtask = {
        id: 'subtask-new',
        ...newSubtaskData,
        created_at: '2025-01-15T10:00:00Z',
        updated_at: '2025-01-15T10:00:00Z'
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn(),
        post: jest.fn().mockResolvedValue({ data: mockCreatedSubtask }),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() }
        }
      } as any));

      const result = await api.createEntity('subtask', newSubtaskData);
      
      expect(result).toEqual(mockCreatedSubtask);
      expect(result.id).toBe('subtask-new');
      expect(result.title).toBe('New Subtask');
      expect(result.estimated_hours).toBe(5);
      expect(result.duration_days).toBe(2);
    });

    it('should create a subtask with optional fields', async () => {
      const newSubtaskData = {
        task_id: 'task-1',
        title: 'Complete Subtask',
        status: 'In Progress',
        estimated_hours: 10,
        duration_days: 5,
        scrum_points: 3,
        phase_id: 'phase-1',
        assigned_to: 'user-1',
        short_description: 'Short desc',
        long_description: 'Long description here'
      };

      const mockCreatedSubtask = {
        id: 'subtask-complete',
        ...newSubtaskData,
        created_at: '2025-01-15T10:00:00Z'
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn(),
        post: jest.fn().mockResolvedValue({ data: mockCreatedSubtask }),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() }
        }
      } as any));

      const result = await api.createEntity('subtask', newSubtaskData);
      
      expect(result.scrum_points).toBe(3);
      expect(result.phase_id).toBe('phase-1');
      expect(result.assigned_to).toBe('user-1');
    });
  });

  describe('updateEntity - subtask', () => {
    it('should update an existing subtask', async () => {
      const updateData = {
        title: 'Updated Subtask Title',
        status: 'Done',
        estimated_hours: 6
      };

      const mockUpdatedSubtask = {
        id: 'subtask-1',
        task_id: 'task-1',
        ...updateData,
        duration_days: 2,
        updated_at: '2025-01-15T11:00:00Z'
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn(),
        post: jest.fn(),
        put: jest.fn().mockResolvedValue({ data: mockUpdatedSubtask }),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() }
        }
      } as any));

      const result = await api.updateEntity('subtask', 'subtask-1', updateData);
      
      expect(result).toEqual(mockUpdatedSubtask);
      expect(result.title).toBe('Updated Subtask Title');
      expect(result.status).toBe('Done');
      expect(result.estimated_hours).toBe(6);
    });

    it('should update subtask status', async () => {
      const updateData = {
        status: 'In Progress'
      };

      const mockUpdatedSubtask = {
        id: 'subtask-1',
        task_id: 'task-1',
        title: 'Original Title',
        status: 'In Progress',
        estimated_hours: 4,
        duration_days: 2
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn(),
        post: jest.fn(),
        put: jest.fn().mockResolvedValue({ data: mockUpdatedSubtask }),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() }
        }
      } as any));

      const result = await api.updateEntity('subtask', 'subtask-1', updateData);
      
      expect(result.status).toBe('In Progress');
    });
  });

  describe('Error Handling', () => {
    it('should handle 404 error when subtask not found', async () => {
      const error = {
        response: {
          status: 404,
          data: { detail: 'Subtask not found' }
        }
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn().mockRejectedValue(error),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn((success, error) => error(error)), eject: jest.fn() }
        }
      } as any));

      await expect(api.getSubtasks('invalid-task')).rejects.toEqual(error);
    });

    it('should handle 400 validation error on create', async () => {
      const error = {
        response: {
          status: 400,
          data: { 
            detail: {
              title: 'Title is required',
              estimated_hours: 'Must be a positive number'
            }
          }
        }
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn(),
        post: jest.fn().mockRejectedValue(error),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn((success, error) => error(error)), eject: jest.fn() }
        }
      } as any));

      const invalidData = {
        task_id: 'task-1',
        title: '',
        estimated_hours: -1
      };

      await expect(api.createEntity('subtask', invalidData)).rejects.toEqual(error);
    });

    it('should handle 403 authorization error', async () => {
      const error = {
        response: {
          status: 403,
          data: { detail: 'You can only update subtasks assigned to you' }
        }
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn(),
        post: jest.fn(),
        put: jest.fn().mockRejectedValue(error),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn((success, error) => error(error)), eject: jest.fn() }
        }
      } as any));

      await expect(
        api.updateEntity('subtask', 'subtask-1', { status: 'Done' })
      ).rejects.toEqual(error);
    });

    it('should handle 500 server error', async () => {
      const error = {
        response: {
          status: 500,
          data: { detail: 'Internal server error' }
        }
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn().mockRejectedValue(error),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn((success, error) => error(error)), eject: jest.fn() }
        }
      } as any));

      await expect(api.getSubtasks()).rejects.toEqual(error);
    });

    it('should handle network error', async () => {
      const error = {
        message: 'Network Error',
        code: 'ERR_NETWORK'
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn().mockRejectedValue(error),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn((success, error) => error(error)), eject: jest.fn() }
        }
      } as any));

      await expect(api.getSubtasks()).rejects.toEqual(error);
    });
  });

  describe('Response Parsing', () => {
    it('should correctly parse subtask response with all fields', async () => {
      const mockSubtask = {
        id: 'subtask-full',
        task_id: 'task-1',
        phase_id: 'phase-1',
        title: 'Full Subtask',
        short_description: 'Short',
        long_description: 'Long description',
        status: 'In Progress',
        assigned_to: 'user-1',
        estimated_hours: 10.5,
        actual_hours: 8.25,
        duration_days: 5,
        scrum_points: 3.5,
        completed_at: '2025-01-15T12:00:00Z',
        created_at: '2025-01-10T10:00:00Z',
        updated_at: '2025-01-15T12:00:00Z',
        created_by: 'user-admin',
        updated_by: 'user-1'
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn().mockResolvedValue({ data: [mockSubtask] }),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() }
        }
      } as any));

      const result = await api.getSubtasks();
      
      expect(result[0]).toEqual(mockSubtask);
      expect(result[0].estimated_hours).toBe(10.5);
      expect(result[0].scrum_points).toBe(3.5);
      expect(result[0].duration_days).toBe(5);
    });

    it('should handle subtask with minimal fields', async () => {
      const mockSubtask = {
        id: 'subtask-minimal',
        task_id: 'task-1',
        title: 'Minimal Subtask',
        status: 'To Do',
        estimated_hours: 1,
        duration_days: 1
      };

      mockedAxios.create = jest.fn(() => ({
        get: jest.fn().mockResolvedValue({ data: [mockSubtask] }),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn(), eject: jest.fn() },
          response: { use: jest.fn(), eject: jest.fn() }
        }
      } as any));

      const result = await api.getSubtasks();
      
      expect(result[0]).toEqual(mockSubtask);
      expect(result[0].phase_id).toBeUndefined();
      expect(result[0].assigned_to).toBeUndefined();
      expect(result[0].scrum_points).toBeUndefined();
    });
  });
});
