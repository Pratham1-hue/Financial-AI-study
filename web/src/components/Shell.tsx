import { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom'

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
  { to: '/desk', label: 'The Desk', hotkey: 'D', icon: 'M3 17l5-6 4 3 5-7 4 5M3 21h18' },
  { to: '/labs', label: 'Labs', hotkey: 'B', icon: 'M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.7 3h10.6a2 2 0 0 0 1.7-3l-5-9V3' },
  { to: '/exams', label: 'Exams', hotkey: 'X', icon: 'M9 12l2 2 4-4M7 8h10v8H7z' },
  { to: '/resources', label: 'Resources', hotkey: 'R', icon: 'M12 6.5V10m0 0v8.5M12 6.5h6.5M12 6.5l4-4' },
  { to: '/profile', label: 'Profile', hotkey: 'P', icon: 'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM16 7v1.5M16 7h-2.5M12 19.5A9.5 9.5 0 0 1 4.5 10c0-1.64.34-3.23.93-4.7' },
]

function Icon({ d }: { d: string }) {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px] shrink-0" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d={d} />
    </svg>
  )
}

function Ticker() {
  const { data } = useApp()
  const stock = data?.stock
  const items = [
    { k: 'DEVI', v: stock ? `$${stock.price.toFixed(2)}` : '—', d: stock ? `${fmtSigned(stock.change_pct)}%` : '' },
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
    <div className="ticker-mask relative overflow-hidden border-b border-line bg-surface-2/70">
      <div className="marquee py-2">
        {line.map((it, i) => (
          <span key={i} className="mono inline-flex items-center gap-2 px-5 text-[0.74rem] whitespace-nowrap">
            <span className="font-semibold tracking-[0.14em] text-muted">{it.k}</span>
            <span className="font-bold text-ink">{it.v}</span>
            {it.d ? <span className={cx('text-muted', it.d.startsWith('+') && 'text-ok', it.d.startsWith('-') && 'text-bad')}>{it.d}</span> : null}
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

  // global hotkey navigate
  useEffect(() => {
    const onNav = (e: CustomEvent) => navigate((e as CustomEvent<{ to: string }>).detail.to, { replace: true })
    window.addEventListener('devi:navigate', onNav as EventListener)
    return () => window.removeEventListener('devi:navigate', onNav as EventListener)
  }, [navigate])

  async function signOut() {
    try {
      await api.post('/api/logout')
    } catch {
      /* ignore */
    }
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-full">
      {/* mobile drawer overlay */}
      {open ? (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm md:hidden"
          onClick={() => setOpen(false)}
        />
      ) : null}

      {/* sidebar */}
      <aside
        className={cx(
          'z-40 border-r border-line bg-surface flex flex-col',
          open ? 'fixed inset-y-0 left-0 w-[250px] md:relative md:w-[250px] md:top-0 md:h-screen md:overflow-y-auto' : 'hidden md:block',
        )}
      >
        <div className="flex h-full flex-col p-5">
          <NavLink to="/" className="mb-7 flex items-center gap-3" onClick={() => setOpen(false)}>
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-gold text-[0.95rem] font-bold text-white shadow-[0_4px_14px_rgba(168,105,26,0.35)]">
              D
            </span>
            <span>
              <span className="font-display block text-[1.15rem] leading-none font-bold text-ink">DEVI</span>
              <span className="block text-[0.62rem] font-semibold tracking-[0.22em] text-muted uppercase">Wall St · AI</span>
            </span>
          </NavLink>

          <nav className="flex flex-col gap-0.5">
            {NAV.map((item) => {
              const isActive = location.pathname === item.to || (item.to !== '/' && location.pathname.startsWith(item.to + '/'))
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  onClick={() => setOpen(false)}
                  className={({ isActive: ia }) =>
                    cx(
                      'flex items-center gap-3 rounded-xl px-3 py-2.5 text-[0.86rem] font-semibold transition group',
                      ia || isActive
                        ? 'bg-gold-soft text-gold shadow-[inset_0_0_0_1px_color-mix(in_srgb,var(--gold)_25%,transparent)]'
                        : 'text-ink-soft hover:bg-surface-2 hover:text-ink',
                    )
                  }
                >
                  <Icon d={item.icon} />
                  <span className="font-semibold">{item.label}</span>
                  <span className="ml-auto text-[0.62rem] font-mono text-muted opacity-50 group-hover:opacity-70">{item.hotkey}</span>
                </NavLink>
              )
            })}
          </nav>

          <div className="mt-auto pt-6">
            <div className="rounded-xl border border-line bg-surface-2 p-3.5">
              <div className="text-[0.62rem] font-semibold tracking-[0.18em] text-muted uppercase">Rank</div>
              <div className="mt-1 text-[0.92rem] font-bold text-ink">{metrics?.level_title ?? '—'}</div>
              {rank?.next ? (
                <div className="mt-0.5 text-[0.72rem] text-muted">
                  {rank.next[0]} XP to {rank.next[1]}
                </div>
              ) : null}
              <div className="mt-2.5 h-1.5 w-full overflow-hidden rounded-full bg-bg-soft">
                <div className="h-full rounded-full bg-gold" style={{ width: `${rank?.pct ?? 0}%` }} />
              </div>
            </div>

            <div className="mt-3 flex items-center gap-2 border-t border-line pt-3">
              <Badge tone="gold">{metrics ? `${fmtMoney(metrics.xp)} XP` : '— XP'}</Badge>
              <button
                onClick={signOut}
                className="ml-auto text-[0.75rem] font-semibold text-muted transition hover:text-bad"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* main */}
      <div className="flex min-h-screen min-w-0 flex-col">
        <div className="sticky top-0 z-20 backdrop-blur">
          <Ticker />
          <div className="flex items-center gap-3 border-b border-line bg-surface/80 px-4 py-2.5 md:px-6">
            <button
              onClick={() => setOpen(true)}
              className="grid h-9 w-9 place-items-center rounded-lg border border-line-strong text-ink md:hidden"
              aria-label="Open navigation"
            >
              <Icon d="M4 7h16M4 12h16M4 17h16" />
            </button>
            <div className="hidden text-[0.8rem] text-muted md:block">
              {data ? `${data.plan.assignment}` : 'Loading your plan…'}
            </div>
            <div className="ml-auto flex items-center gap-2">
              <Badge tone={metrics && metrics.day_score >= 60 ? 'ok' : 'neutral'}>
                Day {data?.metrics.day_score ?? 0}%
              </Badge>
              <Avatar name={data?.profile?.name ?? 'Trader'} size={28} />
              <button
                onClick={toggle}
                className="grid h-9 w-9 place-items-center rounded-lg border border-line-strong text-ink transition hover:bg-surface-2"
                aria-label="Toggle theme"
                title={theme === 'light' ? 'Switch to dark' : 'Switch to light'}
              >
                {theme === 'light' ? (
                  <Icon d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
                ) : (
                  <Icon d="M12 4V2m0 20v-2m8-8h2M2 12h2m13.7-5.7 1.4-1.4M4.9 19.1l1.4-1.4m0-11.4L4.9 4.9m14.2 14.2-1.4-1.4M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z" />
                )}
              </button>
            </div>
          </div>
        </div>

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-7 md:px-8">
          <Outlet />
        </main>

        <footer className="border-t border-line px-6 py-5 text-center text-[0.75rem] text-muted">
          Built for one person with one goal. &ldquo;The harder you work, the harder it is to surrender.&rdquo;
        </footer>
      </div>
    </div>
  )
}
