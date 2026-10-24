import type { ButtonHTMLAttributes, ReactNode } from 'react'

export function cx(...parts: (string | false | null | undefined)[]) {
  return parts.filter(Boolean).join(' ')
}

export function Card({
  children,
  className,
  padded = true,
}: {
  children: ReactNode
  className?: string
  padded?: boolean
}) {
  return <div className={cx('card', padded && 'p-5', className)}>{children}</div>
}

export function SectionTitle({ children, hint }: { children: ReactNode; hint?: ReactNode }) {
  return (
    <div className="mb-3 flex items-end justify-between gap-4">
      <h2 className="text-[1.05rem] font-semibold tracking-tight text-ink">{children}</h2>
      {hint ? <span className="text-xs text-muted">{hint}</span> : null}
    </div>
  )
}

export function PageHeader({
  eyebrow,
  title,
  subtitle,
  right,
}: {
  eyebrow?: string
  title: ReactNode
  subtitle?: ReactNode
  right?: ReactNode
}) {
  return (
    <header className="fade-up mb-6 flex flex-wrap items-end justify-between gap-4">
      <div className="max-w-3xl">
        {eyebrow ? (
          <div className="mb-1 text-[0.68rem] font-semibold uppercase tracking-[0.24em] text-gold">{eyebrow}</div>
        ) : null}
        <h1 className="text-[2rem] leading-tight font-bold text-ink">{title}</h1>
        {subtitle ? <p className="mt-1.5 text-[0.95rem] text-muted">{subtitle}</p> : null}
      </div>
      {right}
    </header>
  )
}

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'

const VARIANTS: Record<Variant, string> = {
  primary:
    'bg-gold text-white border border-transparent hover:brightness-[1.06] shadow-[0_2px_10px_rgba(168,105,26,0.25)]',
  secondary: 'bg-surface text-ink border border-line-strong hover:bg-surface-2',
  ghost: 'bg-transparent text-ink-soft border border-transparent hover:bg-surface-2',
  danger: 'bg-bad text-white border border-transparent hover:brightness-110',
}

export function Button({
  children,
  variant = 'secondary',
  className,
  size = 'md',
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: 'sm' | 'md' | 'lg' }) {
  const sizes = { sm: 'px-3 py-1.5 text-[0.8rem]', md: 'px-4 py-2 text-[0.86rem]', lg: 'px-5 py-2.5 text-[0.95rem]' }
  return (
    <button
      {...rest}
      className={cx(
        'inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition disabled:cursor-not-allowed disabled:opacity-45',
        VARIANTS[variant],
        sizes[size],
        className,
      )}
    >
      {children}
    </button>
  )
}

export function Badge({
  children,
  tone = 'neutral',
  className,
}: {
  children: ReactNode
  tone?: 'neutral' | 'gold' | 'ok' | 'bad' | 'warn' | 'navy'
  className?: string
}) {
  const tones = {
    neutral: 'bg-surface-2 text-muted border-line',
    gold: 'bg-gold-soft text-gold border-[color-mix(in_srgb,var(--gold)_35%,transparent)]',
    ok: 'bg-ok-soft text-ok border-[color-mix(in_srgb,var(--ok)_30%,transparent)]',
    bad: 'bg-bad-soft text-bad border-[color-mix(in_srgb,var(--bad)_30%,transparent)]',
    warn: 'bg-warn-soft text-warn border-[color-mix(in_srgb,var(--warn)_30%,transparent)]',
    navy: 'bg-[color-mix(in_srgb,var(--navy)_12%,transparent)] text-navy border-[color-mix(in_srgb,var(--navy)_30%,transparent)]',
  }
  return (
    <span
      className={cx(
        'inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[0.7rem] font-semibold',
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}

export function Stat({
  label,
  value,
  sub,
  tone,
}: {
  label: string
  value: ReactNode
  sub?: ReactNode
  tone?: 'gold' | 'ok' | 'bad'
}) {
  const color = tone === 'gold' ? 'text-gold' : tone === 'ok' ? 'text-ok' : tone === 'bad' ? 'text-bad' : 'text-ink'
  return (
    <Card className="min-w-0">
      <div className="truncate text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-muted">{label}</div>
      <div className={cx('mono mt-1.5 text-[1.35rem] leading-none font-bold', color)}>{value}</div>
      {sub ? <div className="mt-1.5 text-[0.78rem] text-muted">{sub}</div> : null}
    </Card>
  )
}

export function Bar({
  value,
  max = 1,
  label,
  tone = 'gold',
}: {
  value: number
  max?: number
  label?: ReactNode
  tone?: 'gold' | 'ok' | 'bad' | 'navy'
}) {
  const pct = Math.max(0, Math.min(1, max ? value / max : 0)) * 100
  const bg = { gold: 'var(--gold)', ok: 'var(--ok)', bad: 'var(--bad)', navy: 'var(--navy)' }[tone]
  return (
    <div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-bg-soft">
        <div className="h-full rounded-full transition-[width] duration-500" style={{ width: `${pct}%`, background: bg }} />
      </div>
      {label ? <div className="mt-1.5 text-[0.76rem] text-muted">{label}</div> : null}
    </div>
  )
}

export function Tabs<T extends string>({
  tabs,
  value,
  onChange,
}: {
  tabs: { id: T; label: string }[]
  value: T
  onChange: (id: T) => void
}) {
  return (
    <div className="mb-5 inline-flex gap-1 rounded-xl border border-line bg-surface-2 p-1">
      {tabs.map((t) => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          className={cx(
            'rounded-lg px-3.5 py-1.5 text-[0.82rem] font-semibold transition',
            value === t.id ? 'bg-surface text-ink shadow-sm' : 'text-muted hover:text-ink',
          )}
        >
          {t.label}
        </button>
      ))}
    </div>
  )
}

export function Field({ label, children, hint }: { label: string; children: ReactNode; hint?: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-muted">{label}</span>
      {children}
      {hint ? <span className="mt-1 block text-[0.75rem] text-muted">{hint}</span> : null}
    </label>
  )
}

export const inputCls =
  'w-full rounded-xl border border-line-strong bg-surface px-3 py-2 text-[0.9rem] text-ink outline-none transition placeholder:text-muted focus:border-gold focus:ring-2 focus:ring-[color-mix(in_srgb,var(--gold)_25%,transparent)]'

export function Spinner({ label = 'Loading' }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 py-10 text-muted">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-line-strong border-t-gold" />
      <span className="text-sm">{label}…</span>
    </div>
  )
}

export function Empty({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-xl border border-dashed border-line-strong bg-surface-2 px-5 py-8 text-center text-sm text-muted">
      {children}
    </div>
  )
}

export function Notice({
  tone = 'info',
  children,
}: {
  tone?: 'info' | 'ok' | 'bad' | 'warn' | 'gold'
  children: ReactNode
}) {
  const tones = {
    info: 'border-line bg-surface-2 text-ink-soft',
    ok: 'border-[color-mix(in_srgb,var(--ok)_30%,transparent)] bg-ok-soft text-ok',
    bad: 'border-[color-mix(in_srgb,var(--bad)_30%,transparent)] bg-bad-soft text-bad',
    warn: 'border-[color-mix(in_srgb,var(--warn)_30%,transparent)] bg-warn-soft text-warn',
    gold: 'border-[color-mix(in_srgb,var(--gold)_35%,transparent)] bg-gold-soft text-gold',
  }
  return <div className={cx('rounded-xl border px-4 py-3 text-[0.85rem]', tones[tone])}>{children}</div>
}
