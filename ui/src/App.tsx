import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { queryClient } from './lib/queryClient'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { LanguageProvider } from './contexts/LanguageContext'
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
import AuditHistoryTestPage from './pages/AuditHistoryTestPage'
import BugDetails from './components/bugs/BugDetails'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <LanguageProvider>
          <Router>
            <AuthProvider>
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
                  <Route path="users" element={<UsersPage />} />
                  <Route path="profile" element={<ProfilePage />} />
                  
                  {/* Hierarchy Pages */}
                  <Route path="programs" element={<ProgramsPage />} />
                  <Route path="programs/:id" element={<ProgramDetailPage />} />
                  <Route path="usecases" element={<UseCasesPage />} />
                  <Route path="userstories" element={<UserStoriesPage />} />
                  
                  {/* Admin Pages */}
                  <Route path="admin/phases" element={<PhasesPage />} />
                  <Route path="phases" element={<PhasesPage />} /> {/* Keep legacy route for compatibility */}
                  
                  {/* Test Pages */}
                  <Route path="test/audit-history" element={<AuditHistoryTestPage />} />
                  
                  {/* Hierarchy Navigation */}
                  <Route path="hierarchy/:type/:id" element={<HierarchyPage />} />
                </Route>
              </Routes>
            </AuthProvider>
          </Router>
        </LanguageProvider>
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

export default App
