import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'

import { api } from '../lib/api'
import { fmtMoney, fmtSigned } from '../lib/format'
import { useApp } from '../state/app'
import { useTheme } from '../theme'
import { Avatar, Badge, cx } from './ui'

const NAV = [
  { to: '/', label: 'Dashboard', hotkey: 'H', icon: 'M3 11.5 12 4l9 7.5M5.5 10v9h13v-9' },
  { to: '/learn', label: 'Learn', hotkey: 'L', icon: 'M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5zM4 18.5A2.5 2.5 0 0 1 6.5 16H20' },
  { to: '/focus', label: 'Focus', hotkey: 'F', icon: 'M12 7v5l3 2M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z' },
  { to: '/quizzes', label: 'Quizzes', hotkey: 'Q', icon: 'M9 11l2 2 4-4M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v13A2.5 2.5 0 0 1 17.5 21h-11A2.5 2.5 0 0 1 4 18.5z' },
  { to: '/debrief', label: 'Debrief', hotkey: 'E', icon: 'M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z' },
  { to: '/desk', label: 'The Desk', hotkey: 'D', icon: 'M3 17l5-6 4 3 5-7 4 5M3 21h18' },
  { to: '/labs', label: 'Labs', hotkey: 'B', icon: 'M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.7 3h10.6a2 2 0 0 0 1.7-3l-5-9V3' },
  { to: '/exams', label: 'Exams', hotkey: 'X', icon: 'M9 12l2 2 4-4M7 8h10v8H7z' },
  { to: '/resources', label: 'Resources', hotkey: 'R', icon: 'M12 6.5V10m0 0v8.5M12 6.5h6.5M12 6.5l4-4' },
  { to: '/profile', label: 'Profile', hotkey: 'P', icon: 'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM16 7v1.5M16 7h-2.5M12 19.5A9.5 9.5 0 0 1 4.5 10c0-1.64.34-3.23.93-4.7' },
]

function Icon({ d, className }: { d: string; className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={cx('h-[18px] w-[18px] shrink-0', className)}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={d} />
    </svg>
  )
}

function navLinkCls({ isActive }: { isActive: boolean }) {
  return cx('nav-link', isActive && 'nav-link-active')
}

function Ticker() {
  const { data } = useApp()
  const stock = data?.stock
  const items = [
    { k: 'LAKSH', v: stock ? `$${stock.price.toFixed(2)}` : '—', d: stock ? `${fmtSigned(stock.change_pct)}%` : '' },
    { k: 'RATING', v: stock?.rating ?? '—', d: '' },
    { k: 'DAY', v: data ? `${data.metrics.day_score}%` : '—', d: data ? `week ${data.plan.week?.w ?? '—'}/${data.plan.phase_progress.length}` : '' },
    { k: 'STREAK', v: data ? `${data.metrics.streak}d` : '—', d: '' },
    { k: 'XP', v: data ? fmtMoney(data.metrics.xp) : '—', d: data ? data.metrics.level_title : '' },
    { k: 'FOCUS', v: data ? `${data.focus.today_min}m` : '—', d: data ? `goal ${data.metrics.goal_min}m` : '' },
    { k: 'MASTERY', v: data ? `${data.metrics.mastery_index}%` : '—', d: '' },
    { k: 'NEW YORK', v: 'NYC', d: 'the goal' },
  ]
  const line = [...items, ...items]

  return (
    <div className="ticker-glass ticker-mask relative overflow-hidden">
      <div className="marquee py-1.5">
        {line.map((it, i) => (
          <span key={i} className="mono inline-flex items-center gap-2 px-4 text-[0.7rem] whitespace-nowrap">
            <span className="h-1 w-1 rounded-full bg-gold/70" />
            <span className="font-semibold tracking-[0.16em] text-muted">{it.k}</span>
            <span className="font-bold text-ink">{it.v}</span>
            {it.d ? (
              <span className={cx('text-muted', it.d.startsWith('+') && 'text-ok', it.d.startsWith('-') && 'text-bad')}>{it.d}</span>
            ) : null}
          </span>
        ))}
      </div>
    </div>
  )
}

export function Shell() {
  const { data } = useApp()
  const { theme, toggle } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const [open, setOpen] = useState(false)

  const metrics = data?.metrics
  const rank = data?.rank
  const name = data?.profile?.name || 'Trader'

  // global hotkey navigate
  useEffect(() => {
    const onNav = (e: CustomEvent) => navigate((e as CustomEvent<{ to: string }>).detail.to, { replace: true })
    window.addEventListener('laksh:navigate', onNav as EventListener)
    return () => window.removeEventListener('laksh:navigate', onNav as EventListener)
  }, [navigate])

  // close the mobile sheet whenever the route changes
  useEffect(() => {
    setOpen(false)
  }, [location.pathname])

  // Escape closes the mobile sheet
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

  async function signOut() {
    try {
      await api.post('/api/logout')
    } catch {
      /* ignore */
    }
    navigate('/login', { replace: true })
  }

  return (
    <div className="relative min-h-screen">
      <div className="aurora" aria-hidden="true" />

      {/* mobile scrim */}
      {open ? (
        <div
          className="fade-in fixed inset-0 z-30 bg-[color-mix(in_srgb,var(--ink)_28%,transparent)] backdrop-blur-[3px] md:hidden"
          onClick={() => setOpen(false)}
          aria-hidden="true"
        />
      ) : null}

      <header className="sticky top-0 z-40 px-3 pt-3 sm:px-5 sm:pt-4">
        <div
          className="pointer-events-none absolute inset-x-0 -top-px h-28 bg-gradient-to-b from-bg via-bg/80 to-transparent"
          aria-hidden="true"
        />

        <div className="nav-dock relative z-10 mx-auto max-w-[1480px]">
          <div className="relative z-10 flex items-center gap-2 px-2.5 py-2 sm:gap-3 sm:px-3.5">
            {/* brand */}
            <NavLink to="/" end className="group flex shrink-0 items-center gap-2.5 pr-1" aria-label="Project Laksh home">
              <span className="brand-mark font-display grid h-9 w-9 place-items-center rounded-[13px] text-[1rem] font-bold text-white">
                L
              </span>
              <span className="leading-none">
                <span className="font-display block text-[1.08rem] font-bold tracking-tight text-ink">Laksh</span>
                <span className="mt-1 block text-[0.54rem] font-semibold tracking-[0.24em] text-muted uppercase">
                  Wall St · AI
                </span>
              </span>
            </NavLink>

            <div className="mx-1 hidden h-7 w-px bg-gradient-to-b from-transparent via-[var(--glass-border)] to-transparent xl:block" />

            {/* wide nav */}
            <nav aria-label="Primary" className="hidden min-w-0 flex-1 items-center gap-0.5 xl:flex">
              {NAV.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  title={`${item.label} (${item.hotkey})`}
                  className={navLinkCls}
                >
                  <Icon d={item.icon} className="h-4 w-4 opacity-75" />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>

            <div className="flex-1 xl:hidden" />

            {/* status + actions */}
            <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
              <span className="hidden items-center gap-1.5 rounded-full border border-[var(--glass-border)] bg-[var(--glass-lo)] px-2.5 py-1 text-[0.7rem] font-semibold text-muted lg:flex">
                <span
                  className={cx(
                    'h-1.5 w-1.5 rounded-full',
                    (metrics?.day_score ?? 0) >= 60 ? 'bg-ok' : 'bg-gold',
                  )}
                />
                Day {metrics?.day_score ?? 0}%
              </span>

              <Badge tone="gold" className="mono hidden sm:inline-flex">
                {fmtMoney(metrics?.xp ?? 0)} XP
              </Badge>

              <Link
                to="/profile"
                title={`${name} · profile`}
                className="hidden items-center gap-2 rounded-full border border-[var(--glass-border)] bg-[var(--chip-off)] py-1 pl-1 pr-1 transition hover:border-gold/50 md:flex min-[1420px]:pr-3"
              >
                <Avatar name={name} size={28} />
                <span className="hidden max-w-[8.5rem] truncate text-[0.76rem] font-semibold text-ink min-[1420px]:block">
                  {name}
                </span>
              </Link>

              <button
                onClick={toggle}
                className="icon-btn"
                aria-label="Toggle theme"
                title={theme === 'light' ? 'Switch to NYC night' : 'Switch to daylight'}
              >
                {theme === 'light' ? (
                  <Icon d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
                ) : (
                  <Icon d="M12 4V2m0 20v-2m8-8h2M2 12h2m13.7-5.7 1.4-1.4M4.9 19.1l1.4-1.4m0-11.4L4.9 4.9m14.2 14.2-1.4-1.4M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z" />
                )}
              </button>

              <button
                onClick={() => void signOut()}
                className="icon-btn hidden sm:inline-grid"
                aria-label="Sign out"
                title="Sign out"
              >
                <Icon d="M15 12H3m4-4-4 4 4 4M10 4h9a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-9" />
              </button>

              <button
                onClick={() => setOpen((v) => !v)}
                className="icon-btn md:hidden"
                aria-label={open ? 'Close navigation' : 'Open navigation'}
                aria-expanded={open}
                aria-controls="laksh-mobile-nav"
              >
                {open ? (
                  <Icon d="M6 6l12 12M18 6 6 18" />
                ) : (
                  <Icon d="M4 7h16M4 12h16M4 17h16" />
                )}
              </button>
            </div>
          </div>

          {/* tablet rail */}
          <div className="nav-rail relative z-10 hidden gap-1 overflow-x-auto border-t border-[var(--glass-border)] px-2.5 pb-2 pt-2 md:flex xl:hidden">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                title={`${item.label} (${item.hotkey})`}
                className={navLinkCls}
              >
                <Icon d={item.icon} className="h-4 w-4 opacity-75" />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        </div>

        {/* mobile glass sheet */}
        <div className="md:hidden">
          {open ? (
            <div
              id="laksh-mobile-nav"
              className="nav-sheet fade-in mx-auto mt-2 max-h-[calc(100dvh-6.5rem)] max-w-[1480px] overflow-y-auto p-3"
            >
              <div className="grid grid-cols-2 gap-1">
                {NAV.map((item) => (
                  <NavLink key={item.to} to={item.to} end={item.to === '/'} className={navLinkCls}>
                    <Icon d={item.icon} />
                    <span>{item.label}</span>
                    <span className="mono ml-auto text-[0.62rem] font-medium text-muted opacity-60">{item.hotkey}</span>
                  </NavLink>
                ))}
              </div>

              <div className="mt-3 rounded-2xl border border-[var(--glass-border)] bg-[var(--glass-lo)] p-3">
                <div className="flex items-baseline justify-between gap-2">
                  <span className="text-[0.6rem] font-semibold tracking-[0.18em] text-muted uppercase">Rank</span>
                  <span className="mono text-[0.7rem] font-semibold text-gold">{fmtMoney(metrics?.xp ?? 0)} XP</span>
                </div>
                <div className="mt-1 text-[0.9rem] font-bold text-ink">{metrics?.level_title ?? '—'}</div>
                {rank?.next ? (
                  <div className="mt-0.5 text-[0.72rem] text-muted">
                    {rank.next[0]} XP to {rank.next[1]}
                  </div>
                ) : null}
                <div className="mt-2.5 h-1.5 w-full overflow-hidden rounded-full bg-[var(--glass-lo)]">
                  <div className="h-full rounded-full bg-gold" style={{ width: `${rank?.pct ?? 0}%` }} />
                </div>
              </div>

              <button
                onClick={() => void signOut()}
                className="glass-btn mt-2 flex w-full items-center justify-center gap-2 rounded-xl px-3 py-2.5 text-[0.84rem] font-semibold text-ink"
              >
                <Icon d="M15 12H3m4-4-4 4 4 4M10 4h9a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-9" />
                Sign out
              </button>
            </div>
          ) : null}
        </div>
      </header>

      <div className="mx-auto w-full max-w-[1480px] px-3 pt-2.5 sm:px-5">
        <Ticker />
      </div>

      <main className="mx-auto w-full max-w-[1480px] flex-1 px-3 py-6 sm:px-5 md:px-7 md:py-8">
        <Outlet />
      </main>

      <footer className="mx-auto w-full max-w-[1480px] px-4 pb-6 md:px-7">
        <div className="flex flex-col items-center gap-1.5 border-t border-[var(--glass-border)] pt-5 text-center text-[0.75rem] text-muted">
          <span className="font-display text-[0.98rem] text-ink-soft italic">
            &ldquo;The harder you work, the harder it is to surrender.&rdquo;
          </span>
          <span>Built for one person with one goal. · Laksh · New York</span>
        </div>
      </footer>
    </div>
  )
}
