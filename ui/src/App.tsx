import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'

import { queryClient } from './lib/queryClient'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { LanguageProvider } from './contexts/LanguageContext'
import { ChatProvider } from './contexts/ChatContext'
import { ToastProvider } from './components/common/ToastContainer'
import LoginPage from './pages/LoginPage'
import DashboardLayout from './components/layout/DashboardLayout'
import ProtectedRoute from './components/auth/ProtectedRoute'

// Pages
import DashboardPage from './pages/DashboardPage'
import ClientsPage from './pages/ClientsPage'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import TasksPage from './pages/TasksPage'
import GanttPage from './pages/GanttPage'
import KanbanPage from './pages/KanbanPage'
import SprintPage from './pages/SprintPage'
import BugsPage from './pages/BugsPage'
import ReportsPage from './pages/ReportsPage'
import UsersPage from './pages/UsersPage'
import ProfilePage from './pages/ProfilePage'
import HierarchyPage from './pages/HierarchyPage'
import ProgramsPage from './pages/ProgramsPage'
import ProgramDetailPage from './pages/ProgramDetailPage'
import UseCasesPage from './pages/UseCasesPage'
import UserStoriesPage from './pages/UserStoriesPage'
import PhasesPage from './pages/PhasesPage'
import OrganizationsPage from './pages/OrganizationsPage'
import SprintConfigurationPage from './pages/SprintConfigurationPage'
import AuditHistoryTestPage from './pages/AuditHistoryTestPage'
import BugDetails from './components/bugs/BugDetails'
import TestRunsPage from './pages/TestRunsPage'
import TestCasesPage from './pages/TestCasesPage'
import BugLifecyclePage from './pages/BugLifecyclePage'
import SubtasksPage from './pages/SubtasksPage'
import TodoPage from './pages/TodoPage'
import ChatWidgetTestPage from './pages/ChatWidgetTestPage'
import ReportViewerPage from './pages/ReportViewerPage'
import TeamsPage from './pages/TeamsPage'
import DecisionsPage from './pages/DecisionsPage'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <LanguageProvider>
          <ToastProvider>
            <Router>
              <AuthProvider>
                <ChatProvider>
                  <Routes>
                    <Route path="/login" element={<LoginPage />} />
                
                <Route path="/" element={
                  <ProtectedRoute>
                    <DashboardLayout />
                  </ProtectedRoute>
                }>
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="dashboard" element={<DashboardPage />} />
                  <Route path="clients" element={<ClientsPage />} />
                  <Route path="projects" element={<ProjectsPage />} />
                  <Route path="projects/:id" element={<ProjectDetailPage />} />
                  <Route path="tasks" element={<TasksPage />} />
                  <Route path="gantt" element={<GanttPage />} />
                  <Route path="kanban" element={<KanbanPage />} />
                  <Route path="sprint" element={<SprintPage />} />
                  <Route path="bugs" element={<BugsPage />} />
                  <Route path="bugs/:id" element={<BugDetails />} />
                  <Route path="reports" element={<ReportsPage />} />
                  
                  {/* TODO Page */}
                  <Route path="todos" element={<TodoPage />} />
                  
                  {/* Team Management */}
                  <Route path="teams" element={<TeamsPage />} />
                  
                  {/* Decision Management */}
                  <Route path="decisions" element={<DecisionsPage />} />
                  
                  {/* QA Pages */}
                  <Route path="test-runs" element={<TestRunsPage />} />
                  <Route path="test-cases" element={<TestCasesPage />} />
                  <Route path="bug-lifecycle" element={<BugLifecyclePage />} />
                  
                  <Route path="users" element={<UsersPage />} />
                  <Route path="profile" element={<ProfilePage />} />
                  
                  {/* Hierarchy Pages */}
                  <Route path="programs" element={<ProgramsPage />} />
                  <Route path="programs/:id" element={<ProgramDetailPage />} />
                  <Route path="usecases" element={<UseCasesPage />} />
                  <Route path="userstories" element={<UserStoriesPage />} />
                  <Route path="user-stories" element={<UserStoriesPage />} /> {/* Alias for compatibility */}
                  <Route path="subtasks" element={<SubtasksPage />} />
                  
                  {/* Admin Pages */}
                  <Route path="admin/phases" element={<PhasesPage />} />
                  <Route path="phases" element={<PhasesPage />} /> {/* Keep legacy route for compatibility */}
                  <Route path="organizations" element={<OrganizationsPage />} />
                  <Route path="sprint-configuration" element={<SprintConfigurationPage />} />
                  
                  {/* Test Pages */}
                  <Route path="test/audit-history" element={<AuditHistoryTestPage />} />
                  <Route path="test/chat-widget" element={<ChatWidgetTestPage />} />
                  
                  {/* Reports Viewer */}
                  <Route path="reports/:reportType" element={<ReportViewerPage />} />
                  
                  {/* Hierarchy Navigation */}
                  <Route path="hierarchy/:type/:id" element={<HierarchyPage />} />
                </Route>
              </Routes>
                </ChatProvider>
            </AuthProvider>
          </Router>
          </ToastProvider>
        </LanguageProvider>
      </ThemeProvider>

    </QueryClientProvider>
  )
}

export default App
