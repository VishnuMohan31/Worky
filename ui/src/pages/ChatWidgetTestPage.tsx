/**
 * Chat Widget Test Page
 * Development page to test the ChatWidget component
 */

import { ChatWidget, ChatMessage } from '../components/chat'

export default function ChatWidgetTestPage() {
  // Mock handler for testing
  const handleSendMessage = async (message: string): Promise<ChatMessage> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500))

    // Mock response based on message content
    const messageLower = message.toLowerCase()

    // Test entity cards
    if (messageLower.includes('task') || messageLower.includes('show')) {
      return {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: 'Here are your recent tasks:',
        timestamp: new Date(),
        cards: [
          {
            entity_type: 'task',
            entity_id: 'TSK-001',
            title: 'Complete project documentation',
            status: 'In Progress',
            assignee: 'John Doe',
            due_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
            priority: 'High',
            deep_link: '/tasks/TSK-001',
            metadata: {
              'Story Points': 5,
              'Phase': 'Development'
            }
          },
          {
            entity_type: 'task',
            entity_id: 'TSK-002',
            title: 'Review pull requests',
            status: 'To Do',
            assignee: 'Jane Smith',
            due_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
            priority: 'Medium',
            deep_link: '/tasks/TSK-002'
          }
        ],
        actions: [
          { action_type: 'view_entity', label: 'View All Tasks', deep_link: '/tasks' },
          { action_type: 'set_reminder', label: 'Set Reminder', entity_type: 'task', entity_id: 'TSK-001' }
        ]
      }
    }

    // Test data table
    if (messageLower.includes('list') || messageLower.includes('table')) {
      return {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: 'Here\'s a summary of all tasks:',
        timestamp: new Date(),
        table: {
          columns: ['ID', 'Title', 'Status', 'Priority', 'Assignee', 'Due Date'],
          rows: [
            ['TSK-001', 'Complete documentation', 'In Progress', 'High', 'John Doe', '2025-12-01'],
            ['TSK-002', 'Review PRs', 'To Do', 'Medium', 'Jane Smith', '2025-12-04'],
            ['TSK-003', 'Update tests', 'Done', 'Low', 'Bob Wilson', '2025-11-28'],
            ['TSK-004', 'Fix bug', 'Blocked', 'Critical', 'Alice Brown', '2025-11-30'],
            ['TSK-005', 'Deploy to staging', 'In Progress', 'High', 'John Doe', '2025-12-02']
          ],
          total_count: 15,
          has_more: true
        },
        actions: [
          { action_type: 'suggest_report', label: 'Export to CSV', deep_link: '/reports/tasks' }
        ]
      }
    }

    // Test chart visualization
    if (messageLower.includes('chart') || messageLower.includes('report') || messageLower.includes('stats')) {
      return {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: 'Here\'s the task distribution by status:',
        timestamp: new Date(),
        chart: {
          title: 'Task Status Distribution',
          labels: ['To Do', 'In Progress', 'Done', 'Blocked'],
          datasets: [
            {
              label: 'Tasks',
              data: [12, 8, 25, 3]
            }
          ],
          type: 'bar'
        },
        actions: [
          { action_type: 'suggest_report', label: 'View Full Report', deep_link: '/reports' }
        ]
      }
    }

    // Test bugs with cards
    if (messageLower.includes('bug')) {
      return {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: 'Found 3 critical bugs that need attention:',
        timestamp: new Date(),
        cards: [
          {
            entity_type: 'bug',
            entity_id: 'BUG-123',
            title: 'Login authentication fails on mobile',
            status: 'New',
            assignee: 'Security Team',
            priority: 'P0',
            deep_link: '/bugs/BUG-123',
            metadata: {
              'Severity': 'Critical',
              'Reported': '2 hours ago'
            }
          },
          {
            entity_type: 'bug',
            entity_id: 'BUG-124',
            title: 'UI alignment issue on dashboard',
            status: 'In Progress',
            assignee: 'Jane Smith',
            priority: 'P1',
            deep_link: '/bugs/BUG-124'
          }
        ],
        actions: [
          { action_type: 'view_entity', label: 'View All Bugs', deep_link: '/bugs' },
          { action_type: 'create_comment', label: 'Add Comment', entity_type: 'bug', entity_id: 'BUG-123' }
        ]
      }
    }

    // Test project cards
    if (messageLower.includes('project')) {
      return {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: 'You have 3 active projects:',
        timestamp: new Date(),
        cards: [
          {
            entity_type: 'project',
            entity_id: 'PRJ-001',
            title: 'Worky Platform',
            status: 'In Progress',
            deep_link: '/projects/PRJ-001',
            metadata: {
              'Tasks': 45,
              'Completion': '67%'
            }
          },
          {
            entity_type: 'project',
            entity_id: 'PRJ-002',
            title: 'Mobile App',
            status: 'Planning',
            deep_link: '/projects/PRJ-002',
            metadata: {
              'Tasks': 12,
              'Completion': '15%'
            }
          }
        ],
        actions: [
          { action_type: 'view_entity', label: 'View All Projects', deep_link: '/projects' }
        ]
      }
    }

    // Help message
    if (messageLower.includes('help')) {
      return {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: 'I can help you with:\n\n• Finding tasks and projects\n• Viewing bugs and issues\n• Setting reminders\n• Generating reports\n\nTry asking:\n• "Show me my tasks"\n• "List all bugs"\n• "Show me a chart"\n• "What projects am I working on?"',
        timestamp: new Date()
      }
    }

    // Default response
    return {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: `I received your message: "${message}"\n\nThis is a test response. Try these commands:\n• "show tasks" - See entity cards\n• "list tasks" - See data table\n• "show chart" - See visualization\n• "show bugs" - See bug cards\n• "show projects" - See project cards`,
      timestamp: new Date(),
      actions: [
        { action_type: 'view_entity', label: 'View Dashboard', deep_link: '/dashboard' }
      ]
    }
  }

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">Chat Widget Test Page</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-3">Instructions</h2>
          <p className="text-gray-600 mb-4">
            The chat widget should appear in the bottom-right corner of the screen.
            Click the chat icon to open it and start testing.
          </p>
          
          <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-4">
            <h3 className="font-semibold text-blue-900 mb-2">Test Queries:</h3>
            <ul className="list-disc list-inside text-blue-800 space-y-1">
              <li><strong>show tasks</strong> - Display entity cards</li>
              <li><strong>list tasks</strong> - Display data table</li>
              <li><strong>show chart</strong> - Display chart visualization</li>
              <li><strong>show bugs</strong> - Display bug cards</li>
              <li><strong>show projects</strong> - Display project cards</li>
              <li><strong>help</strong> - Show help message</li>
            </ul>
          </div>

          <div className="bg-green-50 border border-green-200 rounded p-4">
            <h3 className="font-semibold text-green-900 mb-2">Features to Test:</h3>
            <ul className="list-disc list-inside text-green-800 space-y-1">
              <li>✓ Open/close widget</li>
              <li>✓ Minimize/expand widget</li>
              <li>✓ Send messages</li>
              <li>✓ Typing indicator</li>
              <li>✓ <strong>Entity cards with deep links</strong></li>
              <li>✓ <strong>Data tables with sorting</strong></li>
              <li>✓ <strong>Chart visualizations (bar, pie, line)</strong></li>
              <li>✓ <strong>Action buttons with icons</strong></li>
              <li>✓ Error handling (disconnect network to test)</li>
              <li>✓ Keyboard shortcuts (Enter to send, Shift+Enter for new line)</li>
              <li>✓ Auto-scroll to latest message</li>
            </ul>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
          <h3 className="font-semibold text-yellow-900 mb-2">⚠️ Note:</h3>
          <p className="text-yellow-800">
            This is a test page with mock responses. In production, the chat widget will be
            integrated with the actual chat API endpoints and will provide real data from
            the Worky platform.
          </p>
        </div>
      </div>

      {/* Chat Widget */}
      <ChatWidget onSendMessage={handleSendMessage} />
    </div>
  )
}
