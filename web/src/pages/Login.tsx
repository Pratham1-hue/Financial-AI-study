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
    <div className="relative grid min-h-screen lg:grid-cols-[1.08fr_1fr]">
      <div className="aurora" aria-hidden="true" />

      <div className="relative hidden flex-col justify-between overflow-hidden border-r border-[var(--glass-border)] bg-[color-mix(in_srgb,var(--surface)_32%,transparent)] p-12 backdrop-blur-2xl lg:flex">
        <div className="flex items-center gap-3">
          <span className="brand-mark font-display grid h-11 w-11 place-items-center rounded-[15px] text-[1.15rem] font-bold text-white">
            L
          </span>
          <div>
            <div className="font-display text-[1.5rem] leading-none font-bold text-ink">Project Laksh</div>
            <div className="mt-1.5 text-[0.62rem] font-semibold tracking-[0.28em] text-gold uppercase">
              Wall Street · AI · New York
            </div>
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

        <div className="relative z-10 flex items-center gap-2 text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">
          <span className="h-1.5 w-1.5 rounded-full bg-gold" />
          Private desk · one password
        </div>

        <Skyline height={150} className="absolute bottom-0 left-0 opacity-80" />
      </div>

      <div className="grid place-items-center p-6">
        <div className="w-full max-w-sm">
          <div className="mb-5 flex items-center gap-3 lg:hidden">
            <span className="brand-mark font-display grid h-10 w-10 place-items-center rounded-[14px] text-[1.05rem] font-bold text-white">
              L
            </span>
            <div>
              <div className="font-display text-[1.25rem] leading-none font-bold text-ink">Project Laksh</div>
              <div className="mt-1 text-[0.58rem] font-semibold tracking-[0.24em] text-gold uppercase">Wall St · AI</div>
            </div>
          </div>

          <Card className="w-full p-7">
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
              Set <code className="mono">LAKSH_PASSWORD</code> to change it. Disabled when unset.
            </p>
          </Card>
        </div>
      </div>
    </div>
  )
}
