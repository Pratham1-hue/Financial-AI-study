import { useCallback, useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { Shell } from './components/Shell'
import { Toaster } from './components/Toast'
import { Button, Card, Spinner } from './components/ui'
import { Skyline } from './components/Skyline'
import { api, type Session } from './lib/api'
import { Dashboard } from './pages/Dashboard'
import { Debrief } from './pages/Debrief'
import { Desk } from './pages/Desk'
import { Exams } from './pages/Exams'
import { Focus } from './pages/Focus'
import { Labs } from './pages/Labs'
import { Learn } from './pages/Learn'
import { Login } from './pages/Login'
import { Profile } from './pages/Profile'
import { Quizzes } from './pages/Quizzes'
import { Resources } from './pages/Resources'
import { AppProvider } from './state/app'
import { ThemeProvider } from './theme'

function Splash() {
  return (
    <div className="relative grid min-h-screen place-items-center overflow-hidden px-6">
      <div className="aurora" aria-hidden="true" />
      <div className="w-full max-w-sm text-center">
        <div className="font-display mb-2 text-3xl font-bold text-ink">Project Laksh</div>
        <div className="mb-8 text-[0.8rem] font-semibold tracking-[0.22em] text-muted uppercase">Finance · AI · New York</div>
        <Skyline height={90} className="opacity-70" />
        <Spinner label="Waking up" />
      </div>
    </div>
  )
}

function Fatal({ message, retry }: { message: string; retry: () => void }) {
  return (
    <div className="relative grid min-h-screen place-items-center p-6">
      <div className="aurora" aria-hidden="true" />
      <Card className="relative max-w-md text-center">
        <h1 className="font-display text-xl font-bold text-ink">The API is not answering</h1>
        <p className="mt-2 text-sm text-muted">{message}</p>
        <p className="mt-3 text-sm text-muted">
          Start the backend with <code className="mono text-ink">uvicorn api.main:app --port 8000</code> and try again.
        </p>
        <Button variant="primary" className="mt-5" onClick={retry}>
          Retry
        </Button>
      </Card>
    </div>
  )
}

export default function App() {
  const [session, setSession] = useState<Session | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loadSession = useCallback(async () => {
    try {
      setSession(await api.get<Session>('/api/session'))
      setError(null)
    } catch (e) {
      setError((e as Error).message)
    }
  }, [])

  useEffect(() => {
    void loadSession()
  }, [loadSession])

  useEffect(() => {
    const onUnauthorized = () => void loadSession()
    window.addEventListener('laksh:unauthorized', onUnauthorized)
    return () => window.removeEventListener('laksh:unauthorized', onUnauthorized)
  }, [loadSession])

  // global quick-jump hotkeys: d desk · f focus · l learn · q quizzes · x exams · r resources · p profile · e debrief · h home
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement)
        return
      if (e.ctrlKey || e.metaKey || e.altKey) return
      const key = e.key.toLowerCase()
      const map: Record<string, string> = {
        d: '/desk',
        f: '/focus',
        l: '/learn',
        q: '/quizzes',
        x: '/exams',
        r: '/resources',
        p: '/profile',
        e: '/debrief',
        h: '/',
      }
      const to = map[key]
      if (to) {
        e.preventDefault()
        window.dispatchEvent(new CustomEvent('laksh:navigate', { detail: { to } }))
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  return (
    <ThemeProvider>
      {error ? (
        <Fatal message={error} retry={() => void loadSession()} />
      ) : !session ? (
        <Splash />
      ) : session.auth_required && !session.authenticated ? (
        <Login onSuccess={loadSession} />
      ) : (
        <BrowserRouter>
          <AppProvider>
            <Toaster />
            <Routes>
              <Route element={<Shell />}>
                <Route index element={<Dashboard />} />
                <Route path="learn" element={<Learn />} />
                <Route path="focus" element={<Focus />} />
                <Route path="quizzes" element={<Quizzes />} />
                <Route path="debrief" element={<Debrief />} />
                <Route path="desk" element={<Desk />} />
                <Route path="labs" element={<Labs />} />
                <Route path="exams" element={<Exams />} />
                <Route path="resources" element={<Resources />} />
                <Route path="profile" element={<Profile />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </AppProvider>
        </BrowserRouter>
      )}
    </ThemeProvider>
  )
}
