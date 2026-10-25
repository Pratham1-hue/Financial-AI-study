import { useEffect, useState } from 'react'

import { toast, subscribe, type Toast } from '../lib/toast'
import { cx } from './ui'

const TONE_COLORS: Record<Toast['tone'], { bg: string; text: string; border: string; dot: string }> = {
  ok: { bg: 'bg-ok-soft', text: 'text-ok', border: 'border-[color-mix(in_srgb,var(--ok)_35%,transparent)]', dot: 'bg-ok' },
  bad: { bg: 'bg-bad-soft', text: 'text-bad', border: 'border-[color-mix(in_srgb,var(--bad)_35%,transparent)]', dot: 'bg-bad' },
  warn: { bg: 'bg-warn-soft', text: 'text-warn', border: 'border-[color-mix(in_srgb,var(--warn)_35%,transparent)]', dot: 'bg-warn' },
  gold: { bg: 'bg-gold-soft', text: 'text-gold', border: 'border-[color-mix(in_srgb,var(--gold)_35%,transparent)]', dot: 'bg-gold' },
  info: { bg: 'bg-surface-2', text: 'text-ink-soft', border: 'border-line', dot: 'bg-muted' },
}

export function ToastItem({ toast: t }: { toast: Toast }) {
  const c = TONE_COLORS[t.tone]
  return (
    <div
      className={cx(
        'flex items-start gap-3 rounded-xl border p-3.5 text-[0.86rem] shadow-lg animate-in fade-in slide-in-from-top-2',
        c.bg,
        c.border,
      )}
    >
      <div className={cx('mt-0.5 shrink-0 rounded-full px-2', c.dot)} />
      <div className="flex flex-col leading-snug">
        <div className={cx('font-semibold', c.text)}>{t.title}</div>
        {t.description ? <div className="mt-0.5 text-[0.78rem] text-muted">{t.description}</div> : null}
      </div>
      <button
        onClick={() => toast.dismiss(t.id)}
        className="ml-auto shrink-0 rounded-lg p-1 text-muted hover:bg-bg-soft hover:text-ink transition"
        aria-label="Dismiss"
      >
        <span className="sr-only">Dismiss</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
        </svg>
      </button>
    </div>
  )
}

export function Toaster() {
  const [items, setItems] = useState<Toast[]>([])

  useEffect(() => {
    const unsub = subscribe((ts) => setItems(ts))
    return () => {
      unsub()
    }
  }, [])

  return (
    <div className="fixed top-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
      {items.map((t) => (
        <div key={t.id} className="pointer-events-auto w-full max-w-xs">
          <ToastItem toast={t} />
        </div>
      ))}
    </div>
  )
}

export function useToast() {
  return {
    ok: toast.ok,
    bad: toast.bad,
    warn: toast.warn,
    gold: toast.gold,
    info: toast.info,
    dismiss: toast.dismiss,
  }
}
