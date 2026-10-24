import { useState } from 'react'

import { Skyline } from '../components/Skyline'
import { Button, Card, inputCls } from '../components/ui'
import { api } from '../lib/api'

export function Login({ onSuccess }: { onSuccess: () => void | Promise<void> }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await api.post('/api/login', { password })
      await onSuccess()
    } catch (err) {
      setError((err as Error).message || 'Wrong password.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid min-h-screen bg-bg lg:grid-cols-[1.1fr_1fr]">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-surface p-12 lg:flex">
        <div>
          <div className="font-display text-[2.2rem] leading-none font-bold text-ink">Project DEVI</div>
          <div className="mt-2 text-[0.72rem] font-semibold tracking-[0.28em] text-gold uppercase">
            Wall Street · AI · New York
          </div>
        </div>

        <blockquote className="relative z-10 max-w-lg">
          <p className="font-display text-[2rem] leading-snug font-semibold text-ink italic">
            &ldquo;The best way to predict your future is to create it.&rdquo;
          </p>
          <footer className="mt-4 text-[0.78rem] font-semibold tracking-[0.2em] text-gold uppercase">— Peter Drucker</footer>
          <p className="mt-8 max-w-md text-[0.95rem] leading-relaxed text-muted">
            One person, one plan, locked hours. Learn the machine, drill the reps, build the proof, then walk into New York
            already dangerous.
          </p>
        </blockquote>

        <Skyline height={150} className="absolute bottom-0 left-0 opacity-80" />
      </div>

      <div className="grid place-items-center p-6">
        <Card className="w-full max-w-sm p-7">
          <h1 className="font-display text-xl font-bold text-ink">Enter the vault</h1>
          <p className="mt-1 text-sm text-muted">This desk is private. One password, then you study.</p>
          <form onSubmit={submit} className="mt-5 space-y-3">
            <input
              type="password"
              autoFocus
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className={inputCls}
            />
            {error ? <div className="text-[0.82rem] font-medium text-bad">{error}</div> : null}
            <Button type="submit" variant="primary" size="lg" className="w-full" disabled={busy || !password}>
              {busy ? 'Checking…' : 'Unlock'}
            </Button>
          </form>
          <p className="mt-4 text-[0.72rem] text-muted">
            Set <code className="mono">DEVI_PASSWORD</code> to change it. Disabled when unset.
          </p>
        </Card>
      </div>
    </div>
  )
}
