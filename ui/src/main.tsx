import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import './i18n'

// Version logging for cache verification
console.log('%c🚀 Worky App Version 2.3.7 Loaded - Task Transform Bug Fixed', 'color: #4CAF50; font-size: 16px; font-weight: bold;')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
