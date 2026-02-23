import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

interface User {
  id: string
  email: string
  fullName: string
  role: string
  clientId: string
  theme: string
  language: string
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  isLoading: boolean
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token')
    if (token) {
      // Verify token and get user info
      api.getCurrentUser()
        .then(userData => setUser(userData))
        .catch(() => {
          localStorage.removeItem('token')
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      console.log('🔐 Starting login process...')
      const response = await api.login(email, password)
      console.log('✅ Login API response received:', { token: response.token ? 'present' : 'missing', user: response.user })
      
      // Save token first
      localStorage.setItem('token', response.token)
      console.log('💾 Token saved to localStorage')
      
      // Update user state
      setUser(response.user)
      console.log('👤 User state updated:', response.user)
      
      // Wait a bit to ensure state is fully updated
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // Navigate to dashboard
      console.log('🚀 Navigating to dashboard...')
      navigate('/dashboard', { replace: true })
      console.log('✅ Navigation triggered')
    } catch (error) {
      console.error('❌ Login error:', error)
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    navigate('/login')
  }

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      isAuthenticated: !!user,
      isLoading
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
