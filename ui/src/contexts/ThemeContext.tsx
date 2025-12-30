import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

type Theme = 'snow' | 'greenery' | 'water' | 'dracula' | 'dark' | 'blackwhite'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    return (localStorage.getItem('theme') as Theme) || 'snow'
  })

  useEffect(() => {
    // Remove all theme stylesheets
    const existingTheme = document.getElementById('theme-stylesheet')
    if (existingTheme) {
      existingTheme.remove()
    }

    // Add new theme stylesheet
    const link = document.createElement('link')
    link.id = 'theme-stylesheet'
    link.rel = 'stylesheet'
    link.href = `/themes/${theme}.css`
    document.head.appendChild(link)

    // Save to localStorage
    localStorage.setItem('theme', theme)
  }, [theme])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
