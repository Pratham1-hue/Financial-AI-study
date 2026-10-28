import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { api, type FocusPayload } from '../lib/api'
import { fmtClock } from '../lib/format'
import { Button, cx } from './ui'

type FocusState = FocusPayload['state']

/** A phase event surfaced by /api/focus/tick. */
export type PhaseEvent = {
  type: 'focus_done' | 'break_done' | string
  minutes?: number
  subject?: string
}

/* ---------------------------------------------------------------- chime */

/** Short two-tone chime. Respects the caller's sound flag; never throws. */
function chime(kind: 'focus' | 'break') {
  try {
    const Ctx = window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext
    const ctx = new Ctx()
    // focus done rises, break done falls — you can hear which without looking
    const notes = kind === 'focus' ? [660, 880] : [880, 587]
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      const t0 = ctx.currentTime + i * 0.16
      osc.type = 'sine'
      osc.frequency.value = freq
      gain.gain.setValueAtTime(0.0001, t0)
      gain.gain.exponentialRampToValueAtTime(0.13, t0 + 0.02)
      gain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.5)
      osc.connect(gain).connect(ctx.destination)
      osc.start(t0)
      osc.stop(t0 + 0.55)
    })
    window.setTimeout(() => void ctx.close(), 1600)
  } catch {
    /* audio is a nicety */
  }
}

function notify(title: string, body: string) {
  try {
    if (typeof Notification === 'undefined' || Notification.permission !== 'granted') return
    new Notification(title, { body, silent: true })
  } catch {
    /* notifications are a nicety */
  }
}

/* ------------------------------------------------------ completion modal */

function CompletionModal({
  event,
  onAction,
  onClose,
  busy,
}: {
  event: PhaseEvent
  onAction: (kind: 'start-next' | 'open-room' | 'start') => void
  onClose: () => void
  busy: boolean
}) {
  const isFocus = event.type === 'focus_done'
  const minutes = event.minutes ?? 0

  // Escape closes; focus lands on the primary action so it is keyboard-first.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div className="fixed inset-0 z-[60] grid place-items-center p-4" role="dialog" aria-modal="true" aria-labelledby="focus-done-title">
      <div className="fade-in absolute inset-0 bg-[color-mix(in_srgb,var(--ink)_45%,transparent)] backdrop-blur-[3px]" onClick={onClose} aria-hidden="true" />

      <div className="fade-up relative w-full max-w-sm rounded-2xl border border-[var(--glass-border)] bg-surface p-6 text-center shadow-2xl">
        {/* celebratory ring */}
        <div
          className={cx(
            'mx-auto grid h-16 w-16 place-items-center rounded-full text-[1.6rem] animate-correct',
            isFocus ? 'bg-ok-soft text-ok' : 'bg-gold-soft text-gold',
          )}
          aria-hidden="true"
        >
          {isFocus ? '✓' : '☕'}
        </div>

        <h2 id="focus-done-title" className="font-display mt-4 text-[1.4rem] font-bold text-ink">
          {isFocus ? 'Block banked.' : 'Break over.'}
        </h2>

        <p className="mt-1.5 text-[0.88rem] text-muted">
          {isFocus
            ? minutes > 0
              ? `${minutes} minute${minutes === 1 ? '' : 's'} logged${event.subject ? ` · ${event.subject}` : ''}. +${minutes * 2} XP.`
              : `Block finished${event.subject ? ` · ${event.subject}` : ''}.`
            : 'Back in. The tape does not wait.'}
        </p>

        <div className="mt-5 flex gap-2.5">
          {isFocus ? (
            <>
              <Button variant="primary" size="lg" className="flex-1" autoFocus disabled={busy} onClick={() => onAction('start-next')}>
                Start next block
              </Button>
              <Button variant="secondary" size="lg" disabled={busy} onClick={() => onAction('open-room')}>
                Focus Room
              </Button>
            </>
          ) : (
            <>
              <Button variant="primary" size="lg" className="flex-1" autoFocus disabled={busy} onClick={() => onAction('start')}>
                Back in
              </Button>
              <Button variant="ghost" size="lg" disabled={busy} onClick={onClose}>
                Later
              </Button>
            </>
          )}
        </div>

        <button onClick={onClose} className="mt-3 text-[0.74rem] text-muted underline opacity-70 hover:opacity-100">
          dismiss
        </button>
      </div>
    </div>
  )
}

/* ------------------------------------------------------------ mini timer */

const POS_KEY = 'laksh:minitimer'
const DEFAULT_POS = { bottom: 76, right: 20 }

function loadPos() {
  try {
    const raw = localStorage.getItem(POS_KEY)
    if (!raw) return DEFAULT_POS
    const p = JSON.parse(raw) as { bottom: number; right: number }
    if (typeof p.bottom !== 'number' || typeof p.right !== 'number') return DEFAULT_POS
    return p
  } catch {
    return DEFAULT_POS
  }
}

/** Floating pill: countdown + phase, draggable, links to the Focus Room. */
function MiniTimer({ state, remaining }: { state: FocusState; remaining: number }) {
  const navigate = useNavigate()
  const [pos, setPos] = useState(loadPos)
  const dragging = useRef<{ dx: number; dy: number } | null>(null)
  const moved = useRef(false)

  const clamp = (x: number, y: number) => {
    const w = window.innerWidth
    const h = window.innerHeight
    // keep the whole pill reachable on any screen
    return {
      right: Math.max(10, Math.min(w - 200, w - x)),
      bottom: Math.max(10, Math.min(h - 60, h - y)),
    }
  }

  const onPointerDown = (e: React.PointerEvent) => {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
    dragging.current = { dx: e.clientX - rect.left, dy: e.clientY - rect.top }
    moved.current = false
    ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
  }

  const onPointerMove = (e: React.PointerEvent) => {
    if (!dragging.current) return
    moved.current = true
    const next = clamp(e.clientX - dragging.current.dx, e.clientY - dragging.current.dy)
    setPos(next)
  }

  const onPointerUp = (e: React.PointerEvent) => {
    if (!dragging.current) return
    dragging.current = null
    ;(e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId)
    if (moved.current) {
      try {
        localStorage.setItem(POS_KEY, JSON.stringify(pos))
      } catch {
        /* private mode */
      }
    }
  }

  const running = state.status === 'running'
  const paused = state.status === 'paused'
  const phaseTint = state.phase === 'focus' ? 'text-gold' : 'text-ok'

  return (
    <div
      className="fixed z-50 select-none"
      style={{ bottom: pos.bottom, right: pos.right }}
    >
      <button
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onClick={() => {
          // a drag is not a click
          if (!moved.current) navigate('/focus')
        }}
        title="Focus Room"
        aria-label={`Focus timer: ${state.phase_label}, ${fmtClock(remaining)}. Open the Focus Room.`}
        className={cx(
          'group flex items-center gap-2.5 rounded-2xl border border-[var(--glass-border)] bg-surface/92 px-3.5 py-2 shadow-lg backdrop-blur-xl',
          'cursor-grab active:cursor-grabbing transition hover:border-gold/50',
          running && 'animate-pulse-ring',
        )}
      >
        {/* live dot */}
        <span
          className={cx(
            'h-2 w-2 shrink-0 rounded-full',
            running ? 'animate-pulse bg-ok' : paused ? 'bg-warn' : 'bg-muted',
          )}
          aria-hidden="true"
        />

        <span className="flex flex-col items-start leading-none">
          <span className={cx('text-[0.56rem] font-semibold tracking-[0.16em] uppercase', phaseTint)}>
            {state.phase_label}
          </span>
          <span className="mono mt-0.5 text-[1rem] font-bold tabular-nums text-ink">
            {fmtClock(remaining)}
          </span>
        </span>

        <span className="ml-1 hidden text-[0.62rem] font-semibold text-muted group-hover:inline">open →</span>
      </button>
    </div>
  )
}

/* ------------------------------------------------------------------ store */

type FocusCtx = {
  state: FocusState | null
  /** seconds left in the current phase, ticking locally off the server clock */
  remaining: number
  busy: boolean
  act: (path: string, body?: unknown) => Promise<{ state?: FocusState; event?: PhaseEvent | null } | null>
}

const FocusCtx = createContext<FocusCtx | null>(null)

/**
 * Owns the focus clock for the whole app: a floating mini-timer on every page,
 * and the single caller of /api/focus/tick (which advances the state machine).
 * Returns the pieces Focus.tsx needs to stay the source of truth on its page.
 */
export function FocusEngine({ children }: { children: ReactNode }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [state, setState] = useState<FocusState | null>(null)
  const [now, setNow] = useState(() => Date.now())
  const [busy, setBusy] = useState(false)
  const [modal, setModal] = useState<PhaseEvent | null>(null)
  const advancing = useRef(false)
  const loadedOnce = useRef(false)

  const load = useCallback(async () => {
    try {
      const res = await api.get<FocusPayload>('/api/focus')
      setState(res.state)
      loadedOnce.current = true
    } catch {
      /* transient; the next poll retries */
    }
  }, [])

  // local clock for a smooth countdown between polls
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(id)
  }, [])

  // server resync — it owns the clock. 5s catches a session started elsewhere
  // quickly; the countdown itself ticks locally between polls.
  useEffect(() => {
    void load()
    const id = window.setInterval(() => void load(), 5_000)
    return () => window.clearInterval(id)
  }, [load])

  const remaining = useMemo(() => {
    if (!state) return 0
    if (state.status === 'running' && state.ends_at) return Math.max(0, state.ends_at - now / 1000)
    return state.remaining ?? 0
  }, [state, now])

  const act = useCallback(
    async (path: string, body?: unknown) => {
      setBusy(true)
      try {
        const res = (await api.post(path, body)) as { state?: FocusState; event?: PhaseEvent | null }
        if (res.state) setState(res.state)
        return res
      } catch {
        return null
      } finally {
        setBusy(false)
      }
    },
    [],
  )

  // phase ended -> the ONE place that advances the machine
  useEffect(() => {
    if (!state || state.status !== 'running' || remaining > 0 || advancing.current) return
    advancing.current = true
    void (async () => {
      const res = await act('/api/focus/tick')
      advancing.current = false
      const ev = res?.event
      if (!ev) return
      if (state.sound) chime(ev.type === 'focus_done' ? 'focus' : 'break')
      notify(
        ev.type === 'focus_done' ? 'Block banked' : 'Break over',
        ev.type === 'focus_done'
          ? `${ev.minutes ?? 0} minutes logged. Take the break — you earned it.`
          : 'Back in. The tape does not wait.',
      )
      setModal(ev)
    })()
  }, [state, remaining, act])

  // hide the mini-timer on the Focus page (the big ring is there) and on login
  const hidden = location.pathname === '/focus' || location.pathname === '/login'

  const ctx: FocusCtx = { state, remaining, busy, act }

  return (
    <FocusCtx.Provider value={ctx}>
      {children}
      {/* only while a session is live — no dead pill on every page when idle */}
      {state && !hidden && state.status !== 'idle' ? <MiniTimer state={state} remaining={remaining} /> : null}
      {modal ? (
        <CompletionModal
          event={modal}
          busy={busy}
          onClose={() => setModal(null)}
          onAction={async (kind) => {
            if (kind === 'open-room') {
              setModal(null)
              navigate('/focus')
              return
            }
            if (kind === 'start-next') {
              // from a running break, skip back to focus first; start() alone
              // would silently resume the break phase it is meant to exit
              if (state?.status === 'running') await act('/api/focus/skip')
              const res = await act('/api/focus/start')
              setModal(null)
              if (res?.event) setModal(res.event)
              return
            }
            const res = await act('/api/focus/start')
            setModal(null)
            if (res?.event) setModal(res.event)
          }}
        />
      ) : null}
    </FocusCtx.Provider>
  )
}

/** Read the live focus clock (state, remaining, act) from anywhere under Shell. */
export function useFocusEngine() {
  const ctx = useContext(FocusCtx)
  if (!ctx) throw new Error('useFocusEngine must be used inside <FocusEngine>')
  return ctx
}
