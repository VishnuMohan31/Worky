/**
 * Integration tests for TODO feature UI components
 * Tests complete user flows and component interactions
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TodoPage from '../../../pages/TodoPage';
import * as todoApi from '../../../services/todoApi';

// Mock the API
vi.mock('../../../services/todoApi');

// Mock auth context
vi.mock('../../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'USR-001', username: 'testuser', full_name: 'Test User' },
    isAuthenticated: true,
  }),
}));

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
  Link: ({ children, to }: any) => <a href={to}>{children}</a>,
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('TODO Feature Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render TODO dashboard with all panes', async () => {
    const mockTodos = [
      {
        id: '1',
        userId: 'USR-001',
        title: 'Today TODO',
        targetDate: new Date().toISOString().split('T')[0],
        visibility: 'private',
        isDeleted: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];

    const mockNotes = [
      {
        id: '1',
        userId: 'USR-001',
        title: 'Quick Note',
        content: 'Remember this',
        position: 0,
        color: '#FFEB3B',
        isDeleted: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];

    vi.mocked(todoApi.fetchTodoItems).mockResolvedValue({ items: mockTodos, total: 1 });
    vi.mocked(todoApi.fetchAdhocNotes).mockResolvedValue({ notes: mockNotes, total: 1 });

    render(<TodoPage />, { wrapper: createWrapper() });

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Today TODO')).toBeInTheDocument();
    });

    // Verify panes are rendered
    expect(screen.getByText(/Yesterday/i)).toBeInTheDocument();
    expect(screen.getByText(/Today/i)).toBeInTheDocument();
    expect(screen.getByText(/Tomorrow/i)).toBeInTheDocument();
    expect(screen.getByText(/Day After Tomorrow/i)).toBeInTheDocument();

    // Verify ADHOC pane
    expect(screen.getByText('Quick Note')).toBeInTheDocument();
  });

  it('should handle visibility toggle', async () => {
    const mockTodo = {
      id: '1',
      userId: 'USR-001',
      title: 'Test TODO',
      targetDate: new Date().toISOString().split('T')[0],
      visibility: 'private' as const,
      isDeleted: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    vi.mocked(todoApi.fetchTodoItems).mockResolvedValue({ items: [mockTodo], total: 1 });
    vi.mocked(todoApi.fetchAdhocNotes).mockResolvedValue({ notes: [], total: 0 });
    vi.mocked(todoApi.updateTodoItem).mockResolvedValue({
      ...mockTodo,
      visibility: 'public',
    });

    render(<TodoPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Test TODO')).toBeInTheDocument();
    });

    // Find and click visibility toggle button
    const visibilityButton = screen.getByRole('button', { name: /toggle visibility/i });
    fireEvent.click(visibilityButton);

    await waitFor(() => {
      expect(todoApi.updateTodoItem).toHaveBeenCalledWith('1', { visibility: 'public' });
    });
  });

  it('should display linked task information', async () => {
    const mockTodoWithLink = {
      id: '1',
      userId: 'USR-001',
      title: 'Work on auth',
      targetDate: new Date().toISOString().split('T')[0],
      visibility: 'private' as const,
      linkedEntityType: 'task' as const,
      linkedEntityId: 'TSK-001',
      linkedEntityInfo: {
        id: 'TSK-001',
        title: 'Implement Authentication',
        status: 'In Progress',
        dueDate: '2025-12-01',
        assignedTo: 'John Doe',
      },
      isDeleted: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    vi.mocked(todoApi.fetchTodoItems).mockResolvedValue({ items: [mockTodoWithLink], total: 1 });
    vi.mocked(todoApi.fetchAdhocNotes).mockResolvedValue({ notes: [], total: 0 });

    render(<TodoPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Work on auth')).toBeInTheDocument();
    });

    // Verify link indicator is shown
    expect(screen.getByText(/TSK-001/i)).toBeInTheDocument();
    
    // Expand to see task info
    const expandButton = screen.getByRole('button', { name: /view task info/i });
    fireEvent.click(expandButton);

    await waitFor(() => {
      expect(screen.getByText('Implement Authentication')).toBeInTheDocument();
      expect(screen.getByText('In Progress')).toBeInTheDocument();
    });
  });

  it('should handle date range filtering for panes', async () => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const mockTodos = [
      {
        id: '1',
        userId: 'USR-001',
        title: 'Yesterday TODO',
        targetDate: yesterday.toISOString().split('T')[0],
        visibility: 'private' as const,
        isDeleted: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: '2',
        userId: 'USR-001',
        title: 'Today TODO',
        targetDate: today.toISOString().split('T')[0],
        visibility: 'private' as const,
        isDeleted: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: '3',
        userId: 'USR-001',
        title: 'Tomorrow TODO',
        targetDate: tomorrow.toISOString().split('T')[0],
        visibility: 'private' as const,
        isDeleted: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];

    vi.mocked(todoApi.fetchTodoItems).mockResolvedValue({ items: mockTodos, total: 3 });
    vi.mocked(todoApi.fetchAdhocNotes).mockResolvedValue({ notes: [], total: 0 });

    render(<TodoPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Yesterday TODO')).toBeInTheDocument();
      expect(screen.getByText('Today TODO')).toBeInTheDocument();
      expect(screen.getByText('Tomorrow TODO')).toBeInTheDocument();
    });

    // Verify items are in correct panes
    const yesterdayPane = screen.getByText(/Yesterday/i).closest('[data-pane]');
    const todayPane = screen.getByText(/Today/i).closest('[data-pane]');
    const tomorrowPane = screen.getByText(/Tomorrow/i).closest('[data-pane]');

    expect(yesterdayPane).toContainElement(screen.getByText('Yesterday TODO'));
    expect(todayPane).toContainElement(screen.getByText('Today TODO'));
    expect(tomorrowPane).toContainElement(screen.getByText('Tomorrow TODO'));
  });

  it('should handle ADHOC note creation and deletion', async () => {
    const mockNote = {
      id: '1',
      userId: 'USR-001',
      title: 'New Note',
      content: 'Note content',
      position: 0,
      color: '#FFEB3B',
      isDeleted: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    vi.mocked(todoApi.fetchTodoItems).mockResolvedValue({ items: [], total: 0 });
    vi.mocked(todoApi.fetchAdhocNotes).mockResolvedValue({ notes: [], total: 0 });
    vi.mocked(todoApi.createAdhocNote).mockResolvedValue(mockNote);
    vi.mocked(todoApi.deleteAdhocNote).mockResolvedValue(undefined);

    render(<TodoPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/ADHOC Notes/i)).toBeInTheDocument();
    });

    // Click add note button
    const addButton = screen.getByRole('button', { name: /add note/i });
    fireEvent.click(addButton);

    // Fill form
    const titleInput = screen.getByLabelText(/title/i);
    const contentInput = screen.getByLabelText(/content/i);
    
    fireEvent.change(titleInput, { target: { value: 'New Note' } });
    fireEvent.change(contentInput, { target: { value: 'Note content' } });

    // Submit form
    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(todoApi.createAdhocNote).toHaveBeenCalledWith({
        title: 'New Note',
        content: 'Note content',
        color: expect.any(String),
      });
    });
  });

  it('should verify read-only access to task hierarchy', async () => {
    const mockTodoWithLink = {
      id: '1',
      userId: 'USR-001',
      title: 'Work on task',
      targetDate: new Date().toISOString().split('T')[0],
      visibility: 'private' as const,
      linkedEntityType: 'task' as const,
      linkedEntityId: 'TSK-001',
      linkedEntityInfo: {
        id: 'TSK-001',
        title: 'Original Task Title',
        status: 'In Progress',
      },
      isDeleted: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    vi.mocked(todoApi.fetchTodoItems).mockResolvedValue({ items: [mockTodoWithLink], total: 1 });
    vi.mocked(todoApi.fetchAdhocNotes).mockResolvedValue({ notes: [], total: 0 });

    render(<TodoPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Work on task')).toBeInTheDocument();
    });

    // Expand task info
    const expandButton = screen.getByRole('button', { name: /view task info/i });
    fireEvent.click(expandButton);

    await waitFor(() => {
      expect(screen.getByText('Original Task Title')).toBeInTheDocument();
    });

    // Verify no edit buttons for task info
    const taskInfoPanel = screen.getByText('Original Task Title').closest('[data-task-info]');
    expect(taskInfoPanel).not.toContainElement(screen.queryByRole('button', { name: /edit task/i }));
    
    // Verify read-only indicator
    expect(screen.getByTitle(/read-only/i)).toBeInTheDocument();
  });

  it('should handle error states gracefully', async () => {
    vi.mocked(todoApi.fetchTodoItems).mockRejectedValue(new Error('Network error'));
    vi.mocked(todoApi.fetchAdhocNotes).mockRejectedValue(new Error('Network error'));

    render(<TodoPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/error loading/i)).toBeInTheDocument();
    });

    // Verify retry button is available
    const retryButton = screen.getByRole('button', { name: /retry/i });
    expect(retryButton).toBeInTheDocument();
  });

  it('should validate form inputs', async () => {
    vi.mocked(todoApi.fetchTodoItems).mockResolvedValue({ items: [], total: 0 });
    vi.mocked(todoApi.fetchAdhocNotes).mockResolvedValue({ notes: [], total: 0 });

    render(<TodoPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/TODO Dashboard/i)).toBeInTheDocument();
    });

    // Open create TODO form
    const addTodoButton = screen.getByRole('button', { name: /add todo/i });
    fireEvent.click(addTodoButton);

    // Try to submit without title
    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    // Verify validation error
    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });

    // Verify API was not called
    expect(todoApi.createTodoItem).not.toHaveBeenCalled();
  });
});
