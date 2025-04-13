import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import DarkModeToggle from './DarkModeToggle.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <DarkModeToggle />
    <App />
  </StrictMode>,
)
