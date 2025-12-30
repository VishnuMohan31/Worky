import { Outlet } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import ChatWidget from '../chat/ChatWidget'
import { useChat } from '../../contexts/ChatContext'
import type { ChatMessage } from '../chat/ChatWidget'

export default function DashboardLayout() {
  const [isChatOpen, setIsChatOpen] = useState(false)
  const { sendMessage, initializeSession, isSessionActive } = useChat()

  // Initialize chat session when layout mounts
  useEffect(() => {
    if (!isSessionActive) {
      initializeSession()
    }
  }, [isSessionActive, initializeSession])

  // Keyboard shortcut: Ctrl+K or Cmd+K to toggle chat
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check for Ctrl+K (Windows/Linux) or Cmd+K (Mac)
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault()
        setIsChatOpen(prev => !prev)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Handle sending messages from the chat widget
  const handleSendMessage = async (message: string): Promise<ChatMessage> => {
    try {
      const response = await sendMessage(message)
      return response
    } catch (error) {
      throw error
    }
  }

  return (
    <div className="flex h-screen" style={{ backgroundColor: 'var(--background-color)' }}>
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onChatToggle={() => setIsChatOpen(prev => !prev)} isChatOpen={isChatOpen} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
      
      {/* Chat Widget - accessible on all authenticated pages */}
      <ChatWidget 
        onSendMessage={handleSendMessage} 
        isOpen={isChatOpen}
        onToggle={setIsChatOpen}
      />
    </div>
  )
}
