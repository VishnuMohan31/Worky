import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useLanguage } from '../contexts/LanguageContext'

export default function LoginPage() {
  const [email, setEmail] = useState('admin@datalegos.com')
  const [password, setPassword] = useState('password')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const { t } = useLanguage()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center" 
         style={{ backgroundColor: 'var(--background-color)' }}>
      <div className="max-w-md w-full space-y-8 p-8 rounded-lg shadow-lg"
           style={{ backgroundColor: 'var(--surface-color)' }}>
        <div>
          <h2 className="text-center text-3xl font-bold"
              style={{ color: 'var(--text-color)' }}>
            {t('welcomeBack')}
          </h2>
          <p className="mt-2 text-center text-sm"
             style={{ color: 'var(--text-secondary)' }}>
            {t('loginToContinue')}
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="p-3 rounded" 
                 style={{ backgroundColor: 'var(--error-color)', color: 'white' }}>
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1"
                     style={{ color: 'var(--text-color)' }}>
                {t('email')}
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2"
                style={{
                  borderColor: 'var(--border-color)',
                  backgroundColor: 'var(--background-color)',
                  color: 'var(--text-color)'
                }}
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1"
                     style={{ color: 'var(--text-color)' }}>
                {t('password')}
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2"
                style={{
                  borderColor: 'var(--border-color)',
                  backgroundColor: 'var(--background-color)',
                  color: 'var(--text-color)'
                }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 rounded-md font-medium transition-colors"
            style={{
              backgroundColor: 'var(--primary-color)',
              color: 'white',
              opacity: loading ? 0.6 : 1
            }}
          >
            {loading ? t('loading') : t('login')}
          </button>
        </form>
        
        <div className="text-xs text-center" style={{ color: 'var(--text-secondary)' }}>
          Demo credentials: admin@datalegos.com / password
        </div>
      </div>
    </div>
  )
}
