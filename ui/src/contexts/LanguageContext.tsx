import { createContext, useContext, ReactNode, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

type Language = 'en' | 'te'

interface LanguageContextType {
  language: Language
  setLanguage: (lang: Language) => void
  t: (key: string) => string
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const { i18n, t } = useTranslation()

  // Initialize language from localStorage on mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language') as Language
    if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'te')) {
      i18n.changeLanguage(savedLanguage)
    }
  }, [i18n])

  const setLanguage = (lang: Language) => {
    i18n.changeLanguage(lang)
    localStorage.setItem('language', lang)
  }

  return (
    <LanguageContext.Provider value={{ 
      language: (i18n.language as Language) || 'en', 
      setLanguage,
      t 
    }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider')
  }
  return context
}
