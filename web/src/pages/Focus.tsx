import { useCallback, useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { TimerRing } from '../components/TimerRing'
import { QuoteLine } from '../components/Quote'
import { StaggerGroup } from '../components/motion'
import { useFocusEngine } from '../components/FocusTimer'
import { Badge, Bar, Button, Card, Empty, Field, PageHeader, SectionTitle, Spinner, cx, inputCls } from '../components/ui'
import { api, type FocusPayload } from '../lib/api'
import { fmtClock, fmtHM } from '../lib/format'
import { usePoll } from '../lib/hooks'

export function Focus() {
  const [params] = useSearchParams()
  const [data, setData] = useState<FocusPayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const autoStarted = useRef(false)

  // the engine owns the clock and is the only caller of /api/focus/tick
  const { state, remaining: displayRemaining, busy, act: engineAct } = useFocusEngine()

  const load = useCallback(async (quiet = false) => {
    if (!quiet) setLoading(true)
    try {
      setData(await api.get<FocusPayload>('/api/focus'))
      setError(null)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  // resync this page's stats/log with the server
  usePoll(() => load(true), 10_000, !!data)

  const running = state?.status === 'running'

  // wrap the engine's act so this page surfaces errors in its own banner
  const act = useCallback(
    async (path: string, body?: unknown) => {
      const res = await engineAct(path, body)
      if (!res) setError('That action did not go through. Try again.')
      await load(true)
      return res
    },
    [engineAct, load],
  )

  // deep link: /focus?start=1
  useEffect(() => {
    if (autoStarted.current || !state) return
    if (params.get('start') === '1' && state.status === 'idle') {
      autoStarted.current = true
      void act('/api/focus/start', { mode: state.mode, subject: state.subject })
    }
  }, [params, state, act])

  if (loading && !data) return <Spinner label="Loading the clock" />
  if (error && !data) return <Empty>{error}</Empty>
  if (!state || !data) return <Empty>Waiting for the clock…</Empty>

  const { stats, goal_min, rank, log } = data
  const phaseColor = state.phase_color
  const statusLabel = running ? state.phase_label : state.status === 'paused' ? 'Paused' : 'Ready'
  const btn = (label: string, onClick: () => void, variant: 'primary' | 'secondary' | 'ghost' | 'danger' = 'secondary', disabled = false) => (
    <Button variant={variant} size="lg" onClick={onClick} disabled={busy || disabled}>
      {label}
    </Button>
  )

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Locked-in hours"
        title="The Focus Room"
        subtitle="Flip the hourglass, close the tabs, and put in the work. The clock runs on the server, so it keeps honest even if you leave."
        right={
          <Badge tone={running ? 'ok' : state.status === 'paused' ? 'warn' : 'neutral'}>
            {statusLabel} · {state.phase_label}
          </Badge>
        }
      />

      {error ? (
        <div className="rounded-xl border border-[color-mix(in_srgb,var(--bad)_35%,transparent)] bg-bad-soft px-4 py-3 text-[0.88rem] font-medium text-bad">
          {error}
          <button onClick={() => setError(null)} className="ml-3 text-[0.75rem] underline opacity-70">
            dismiss
          </button>
        </div>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-[auto_1fr]">
        <Card className="flex flex-col items-center gap-6 py-8">
          <div className={cx('relative rounded-full', running && 'animate-pulse-ring')}>
            <TimerRing
              remaining={displayRemaining}
              total={state.total || 1}
              color={phaseColor}
              clock={fmtClock(displayRemaining)}
              label={statusLabel}
              sub={state.label || state.subject}
            />
          </div>

          <div className="flex flex-wrap items-center justify-center gap-2.5">
            {state.status === 'idle'
              ? btn('Start', () => void act('/api/focus/start', { mode: state.mode, subject: state.subject }), 'primary')
              : null}
            {running ? btn('Pause', () => void act('/api/focus/pause')) : null}
            {state.status === 'paused' ? btn('Resume', () => void act('/api/focus/start'), 'primary') : null}
            {state.status !== 'idle' ? btn('Skip phase', () => void act('/api/focus/skip'), 'ghost') : null}
            {state.status !== 'idle' ? btn('Stop & log', () => void act('/api/focus/stop')) : null}
            <Button variant="ghost" size="lg" onClick={() => void act('/api/focus/reset')} disabled={busy}>
              Reset
            </Button>
          </div>

          <div className="mono text-[0.76rem] text-muted">
            cycle {state.cycles % (state.every || 1)} / {state.every} · {state.subject}
          </div>
        </Card>

        <div className="space-y-5">
          <Card>
            <SectionTitle hint={`goal ${fmtHM(goal_min)} / day`}>Today</SectionTitle>
            <StaggerGroup className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                ['Locked today', fmtHM(stats.today_min)],
                ['Sessions', String(stats.sessions_today)],
                ['This week', fmtHM(stats.week_min)],
                ['All time', `${stats.total_hours}h`],
              ].map(([k, v]) => (
                <div key={k}>
                  <div className="text-[0.66rem] font-semibold tracking-[0.14em] text-muted uppercase">{k}</div>
                  <div className="mono mt-1 text-[1.15rem] font-bold text-ink">{v}</div>
                </div>
              ))}
            </StaggerGroup>
            <div className="mt-5">
              <Bar
                value={stats.today_min}
                max={goal_min || 1}
                tone={stats.today_min >= goal_min ? 'ok' : 'gold'}
                label={`${Math.round((stats.today_min / (goal_min || 1)) * 100)}% of today's locked-hours goal · streak ${stats.streak} days`}
              />
            </div>
          </Card>

          <Card>
            <SectionTitle hint={rank.next ? `${rank.next[0]}h to ${rank.next[1]}` : 'top of the ladder'}>Rank</SectionTitle>
            <div className="mb-3 flex items-baseline gap-3">
              <span className="font-display text-[1.4rem] font-bold text-gold">{rank.current[1]}</span>
              <span className="text-[0.82rem] text-muted">{rank.current[2]}</span>
            </div>
            <Bar value={rank.pct * 100} max={100} />
            <StaggerGroup className="mt-4 grid gap-1.5">
              {rank.ladder.map(([hours, title]) => (
                <div
                  key={`${hours}-${title}`}
                  className={cx(
                    'flex items-center justify-between rounded-lg px-3 py-1.5 text-[0.82rem]',
                    title === rank.current[1] ? 'bg-gold-soft font-semibold text-gold' : 'text-muted',
                  )}
                >
                  <span>{title}</span>
                  <span className="mono">{hours}h</span>
                </div>
              ))}
            </StaggerGroup>
          </Card>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1fr_1.1fr]">
        <Card>
          <SectionTitle>Session setup</SectionTitle>
          <div className="space-y-4">
            <Field label="Mode">
              <div className="flex flex-wrap gap-2">
                {Object.entries(state.modes).map(([name, cfg]) => (
                  <button
                    key={name}
                    disabled={state.status !== 'idle'}
                    onClick={() => void act('/api/focus/config', { mode: name })}
                    className={cx(
                      'rounded-xl border px-3 py-2 text-left text-[0.82rem] transition disabled:opacity-50',
                      state.mode === name ? 'border-gold bg-gold-soft text-gold' : 'border-line bg-surface-2 text-ink-soft hover:border-line-strong',
                    )}
                  >
                    <div className="font-semibold">{name}</div>
                    <div className="mono text-[0.7rem] text-muted">
                      {cfg.focus}/{cfg.short}
                    </div>
                  </button>
                ))}
              </div>
            </Field>

            <Field label="Subject" hint={state.modes[state.mode]?.desc}>
              <select className={inputCls} value={state.subject} disabled={state.status !== 'idle'} onChange={(e) => void act('/api/focus/config', { subject: e.target.value })}>
                {state.subjects.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="What exactly are you doing?">
              <input
                className={inputCls}
                defaultValue={state.label}
                placeholder="e.g. A1 · pandas groupby drills"
                onBlur={(e) => void act('/api/focus/config', { label: e.target.value })}
              />
            </Field>

            <div className="flex flex-wrap gap-5 pt-1">
              <label className="flex items-center gap-2 text-[0.84rem] text-ink-soft">
                <input
                  type="checkbox"
                  checked={state.auto_break}
                  onChange={(e) => void act('/api/focus/config', { auto_break: e.target.checked })}
                />
                Auto-start breaks
              </label>
              <label className="flex items-center gap-2 text-[0.84rem] text-ink-soft">
                <input
                  type="checkbox"
                  checked={state.sound}
                  onChange={(e) => void act('/api/focus/config', { sound: e.target.checked })}
                />
                Chime at phase change
              </label>
            </div>
          </div>

          <div className="mt-5">
            <QuoteLine text="We are what we repeatedly do. Excellence, then, is not an act, but a habit." author="Will Durant" />
          </div>
        </Card>

        <Card>
          <SectionTitle hint={`${log.length} recent`}>Session log</SectionTitle>
          {log.length === 0 ? (
            <Empty>No logged blocks yet. The first one is the hardest.</Empty>
          ) : (
            <div className="overflow-hidden rounded-xl border border-line">
              <table className="w-full text-left text-[0.82rem]">
                <thead className="bg-surface-2 text-[0.68rem] tracking-[0.12em] text-muted uppercase">
                  <tr>
                    <th className="px-3 py-2 font-semibold">When</th>
                    <th className="px-3 py-2 font-semibold">Minutes</th>
                    <th className="px-3 py-2 font-semibold">Subject</th>
                    <th className="px-3 py-2 font-semibold">Task</th>
                  </tr>
                </thead>
                <tbody>
                  {log.map((row, i) => (
                    <tr key={row.id ?? i} className="fade-up border-t border-line" style={{ animationDelay: `${Math.min(i, 8) * 60}ms` }}>
                      <td className="mono px-3 py-2 text-muted">{row.ended_at?.slice(5, 16) ?? row.date}</td>
                      <td className="mono px-3 py-2 font-semibold text-ink">{row.minutes}m</td>
                      <td className="px-3 py-2 text-ink-soft">{row.subject}</td>
                      <td className="px-3 py-2 text-muted">{row.label || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
