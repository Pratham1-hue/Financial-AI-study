import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { Confetti } from '../components/Confetti'
import { LineChart } from '../components/LineChart'
import { MagazineCover } from '../components/MagazineCover'
import { QuoteLine } from '../components/Quote'
import { ScrollReveal } from '../components/ScrollReveal'
import { Skyline } from '../components/Skyline'
import { Badge, Bar, Button, Card, Chip, Empty, ProgressRing, SectionTitle, Spinner, cx } from '../components/ui'
import { fireConfetti } from '../lib/confetti'
import { fmtHM, fmtMoney, fmtSigned } from '../lib/format'
import { api } from '../lib/api'
import { useApp } from '../state/app'

function DayScoreRing({ pct, value }: { pct: number; value: number }) {
  const color = pct >= 80 ? 'var(--ok)' : pct >= 60 ? 'var(--gold)' : 'var(--bad)'
  return (
    <Card className="relative p-5">
      <ProgressRing pct={pct} size={140} stroke={11} color={color} label={`${value}%`} sub="day score" />
      <div className="absolute -top-3 -right-3 flex items-center gap-1 px-2 py-0.5 rounded-full border border-line bg-surface-2 text-[0.68rem] font-semibold text-muted">
        <span className="w-2 h-2 rounded-full bg-gold animate-ok" />
        vs yesterday
      </div>
    </Card>
  )
}

/* ---------------------------------------------------------------- daily challenge */
type DailyQ = { id: string; track: string; module: string; diff: string; q: string; opts: string[] }

export function DailyChallenge() {
  const [challenge, setChallenge] = useState<{ completed: boolean; date: string; question?: DailyQ; xp_bonus: number; message?: string } | null>(null)
  const [answer, setAnswer] = useState<number | null>(null)
  const [result, setResult] = useState<{ correct: boolean; xp_bonus: number; xp: number; explanation: string; correct_answer: string } | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.get<{ completed: boolean; date: string; question?: DailyQ; xp_bonus: number; message?: string }>('/api/daily-challenge')
      .then(setChallenge)
      .catch(() => { /* silent — challenge is optional */ })
  }, [])

  if (!challenge) return null

  if (challenge.completed) {
    return (
      <ScrollReveal variant="fade-up" delay={200} once>
        <Card className="bg-surface-2 border border-line">
          <div className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <Badge tone="ok">✓ Daily challenge done</Badge>
              <span className="ml-auto text-[0.72rem] font-semibold text-muted">{challenge.date}</span>
            </div>
            <p className="text-[0.85rem] text-muted">{challenge.message}</p>
          </div>
        </Card>
      </ScrollReveal>
    )
  }

  const q = challenge.question!
  const disabled = !!result || busy

  async function submit() {
    if (answer === null) return
    setBusy(true)
    try {
      const res = await api.post<{ completed: boolean; correct: boolean; xp_bonus: number; xp: number; explanation: string; correct_answer: string }>('/api/daily-challenge/complete', { qid: q.id, answer })
      setResult(res)
      if (res.correct) {
        void fireConfetti(window.innerWidth / 2, window.innerHeight / 3, 120)
      }
    } catch {
      /* silent */
    } finally {
      setBusy(false)
    }
  }

  return (
    <ScrollReveal variant="fade-up" delay={150} once>
      <Card className="hero fade-up relative overflow-hidden p-0" padded={false}>
        <div className="relative z-10 p-7">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Badge tone="gold">Daily challenge</Badge>
              <span className="ml-auto text-[0.72rem] font-semibold text-gold">+{challenge.xp_bonus} XP</span>
            </div>
            <span className="text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">{q.module} · {q.diff}</span>
          </div>
          <h3 className="font-display text-[1.25rem] font-bold text-ink mb-3">{q.q}</h3>
          <div className="space-y-2">
            {q.opts.map((opt, oi) => (
              <button
                key={oi}
                disabled={disabled}
                onClick={() => setAnswer(oi)}
                className={cx(
                  'flex w-full items-start gap-3 rounded-xl border px-3.5 py-2.5 text-left text-[0.88rem] transition disabled:cursor-default',
                  disabled && result && result.correct && answer === oi
                    ? 'border-[color-mix(in_srgb,var(--ok)_45%,transparent)] bg-ok-soft text-ok'
                    : disabled && result && answer === oi && !result.correct
                      ? 'border-[color-mix(in_srgb,var(--bad)_45%,transparent)] bg-bad-soft text-bad'
                      : answer === oi
                        ? 'border-gold bg-gold-soft text-ink'
                        : 'border-line bg-surface-2 text-ink-soft hover:border-line-strong',
                )}
              >
                <span className="mono mt-0.5 text-[0.72rem] font-bold opacity-70">{['A', 'B', 'C', 'D'][oi]}</span>
                <span>{opt}</span>
              </button>
            ))}
          </div>
          {!result && !disabled ? (
            <div className="mt-5 flex gap-2">
              <Button variant="primary" onClick={submit} className="flex-1">
                Submit answer
              </Button>
            </div>
          ) : null}
          {result ? (
            <div className="mt-5 rounded-xl p-4 bg-surface-2 border border-line">
              <div className="flex items-center gap-2 mb-2">
                {result.correct ? <span className="text-ok font-bold">✓ Correct!</span> : <span className="text-bad font-bold">Not quite.</span>}
                <span className="ml-auto text-[0.72rem] font-semibold text-gold">+{result.xp_bonus} XP</span>
              </div>
              <p className="text-[0.85rem] text-muted">{result.explanation}</p>
              <p className="mt-2 text-[0.75rem] text-muted">Correct answer: {result.correct_answer}</p>
            </div>
          ) : null}
        </div>
        <Skyline height={48} className="opacity-60" />
      </Card>
    </ScrollReveal>
  )
}

export function Dashboard() {
  const { data, loading, error } = useApp()
  const [streakFire, setStreakFire] = useState(false)

  // Must run before any early returns so hook order is stable across renders.
  useEffect(() => {
    if (!data) return
    const streak = data.metrics.streak
    if (streak > 0 && streak % 5 === 0) setStreakFire(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data])

  if (loading && !data) return <Spinner label="Loading your desk" />
  if (error) return <Empty>{error}</Empty>
  if (!data) return <Empty>No data yet.</Empty>

  const { profile, plan, metrics, stock, loop, rank, quote, modules, breaches, comp, bootcamp } = data
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'
  const goalPct = metrics.goal_min ? metrics.focus_min_today / metrics.goal_min : 0
  const stockSeries = stock.series.map((s) => s.close)
  const streak = metrics.streak

  return (
    <div className="space-y-6 pb-24">
      <Confetti fire={streakFire} />

      {/* Magazine cover hero */}
      <ScrollReveal variant="fade-up" once delay={50}>
        <MagazineCover className="w-full max-w-[1480px] mx-auto" />
      </ScrollReveal>

      {/* hero */}
      <ScrollReveal variant="fade-up" delay={100} once>
        <Card className="hero relative overflow-hidden p-0" padded={false}>
          <div className="relative grid gap-8 p-7 md:grid-cols-[1fr_340px] md:items-start">
            <div className="relative z-10 min-w-0 max-w-2xl">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[0.68rem] font-semibold tracking-[0.26em] text-gold uppercase">
                  Day {plan.day} of {plan.days_total} · {profile.target_role || 'the mission'}
                </span>
                {streak > 0 ? (
                  <Chip tone="gold" className="animate-streak">🔥 {streak}-day streak</Chip>
                ) : null}
              </div>
              <h1 className="font-display text-[2.1rem] leading-[1.1] font-bold text-ink">
                {greeting}. {profile.name || 'Trader'} — today is a rep.
              </h1>
              <p className="mt-3 max-w-2xl text-[0.95rem] text-muted">{plan.assignment}</p>
              {profile.why ? (
                <p className="mt-3 max-w-2xl border-l-2 border-gold pl-3 text-[0.88rem] italic text-ink-soft">
                  {profile.why}
                </p>
              ) : null}
              <div className="mt-5 flex flex-wrap gap-2.5">
                <p className="w-full text-[0.68rem] font-semibold tracking-[0.2em] text-gold uppercase mb-2">
                  Start your day →
                </p>
                <Link to="/focus?start=1">
                  <Button variant="primary" size="lg">
                    Start locked session
                  </Button>
                </Link>
                <Link to="/learn">
                  <Button size="lg">Open the curriculum</Button>
                </Link>
                <Link to="/desk">
                  <Button size="lg">Trade a round</Button>
                </Link>
              </div>
              <div className="mt-5 max-w-xl">
                <QuoteLine text={quote.text} author={quote.author} />
              </div>
            </div>

            <div className="flex flex-col items-center gap-6 min-w-0 max-w-[340px]">
              <ProgressRing pct={goalPct * 100} size={124} stroke={11} label={fmtHM(metrics.focus_min_today).replace(' ', '')} sub="focus goal" />
              <DayScoreRing pct={metrics.day_score} value={metrics.day_score} />
            </div>
          </div>
          <Skyline height={64} className="opacity-60" />
        </Card>
      </ScrollReveal>

      {/* metrics */}
      <ScrollReveal variant="fade-up" delay={150} once>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <div className="text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">Focus today</div>
            <div className="mono mt-1.5 text-[1.35rem] font-bold text-ink">{fmtHM(metrics.focus_min_today)}</div>
            <div className="mt-2">
              <Bar
                value={metrics.focus_min_today}
                max={metrics.goal_min || 1}
                tone={metrics.focus_min_today >= metrics.goal_min ? 'ok' : 'gold'}
                label={`${Math.round((metrics.focus_min_today / (metrics.goal_min || 1)) * 100)}% of today's locked-hours goal · ${data.focus.sessions_today} sessions`}
              />
            </div>
          </Card>
          <Card>
            <div className="text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">Streak</div>
            <div className={cx('mono mt-1.5 text-[1.6rem] leading-none font-bold', streak > 0 ? 'text-gold' : 'text-ink')}>
              {streak} days
            </div>
            <div className="mt-2 text-[0.78rem] text-muted">{fmtHM(metrics.all_time_hours * 60)} locked all-time</div>
          </Card>
          <Card>
            <div className="text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">Mastery index</div>
            <div className="mono mt-1.5 text-[1.35rem] font-bold text-gold">{metrics.mastery_index}%</div>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {Object.entries(metrics.mastery_parts).map(([k, v]) => (
                <Badge key={k} tone="neutral">
                  {k} {Math.round(v)}%
                </Badge>
              ))}
            </div>
          </Card>
          <Card>
            <div className="text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">XP</div>
            <div className="mono mt-1.5 text-[1.35rem] font-bold text-ink">{fmtMoney(metrics.xp)}</div>
            <div className="mt-2 text-[0.78rem] text-muted">
              {metrics.level_title}
              {rank.next ? ` · ${rank.next[0]} XP → ${rank.next[1]}` : ' · top rank'}
            </div>
          </Card>
        </div>
      </ScrollReveal>

      {/* loop + stock */}
      <ScrollReveal variant="fade-up" delay={200} once>
        <div className="grid gap-5 lg:grid-cols-[1.15fr_1fr]">
          <Card>
            <SectionTitle hint={`${loop.filter((l) => l.done).length}/${loop.length} complete`}>Today&apos;s loop</SectionTitle>
            <div className="space-y-2.5">
              {loop.map((step, i) => (
                <Link
                  key={step.name}
                  to={step.to}
                  className={cx(
                    'flex items-center gap-3 rounded-xl border px-4 py-3 transition',
                    step.done ? 'border-[color-mix(in_srgb,var(--ok)_30%,transparent)] bg-ok-soft' : 'border-line bg-surface-2 hover:border-line-strong',
                  )}
                >
                  <span
                    className={cx(
                      'mono grid h-7 w-7 shrink-0 place-items-center rounded-full text-[0.72rem] font-bold',
                      step.done ? 'bg-ok text-white' : 'bg-bg-soft text-muted',
                    )}
                  >
                    {step.done ? '✓' : i + 1}
                  </span>
                  <span className={cx('font-semibold', step.done ? 'text-ok' : 'text-ink')}>{step.name}</span>
                  <span className="ml-auto text-[0.75rem] text-muted">{step.done ? 'done' : 'open →'}</span>
                </Link>
              ))}
            </div>

            <div className="mt-5 space-y-3">
              <div className="text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">Day parts</div>
              {metrics.day_parts.map((p) => (
                <div key={p.name}>
                  <div className="mb-1 flex justify-between text-[0.78rem]">
                    <span className="text-ink-soft">{p.name}</span>
                    <span className="mono text-muted">{p.value}/{p.max}</span>
                  </div>
                  <Bar value={p.value} max={p.max} />
                </div>
              ))}
            </div>
          </Card>

          <div className="space-y-5">
            <Card>
              <SectionTitle hint={<Link to="/desk" className="text-gold">trade →</Link>}>$LAKSH — stock of you</SectionTitle>
              <div className="flex items-end justify-between">
                <div>
                  <div className="mono text-[2rem] leading-none font-bold text-ink">${stock.price.toFixed(2)}</div>
                  <div className={cx('mono mt-1.5 text-[0.85rem] font-semibold', stock.change_pct >= 0 ? 'text-ok' : 'text-bad')}>
                    {fmtSigned(stock.change_pct)}% today
                  </div>
                </div>
                <Badge tone={stock.rating_avg >= 60 ? 'ok' : stock.rating_avg >= 40 ? 'warn' : 'bad'}>
                  {stock.rating} · {Math.round(stock.rating_avg)}
                </Badge>
              </div>
              <div className="mt-3">
                <LineChart series={stockSeries} height={110} />
              </div>
              <div className="mono mt-2 flex justify-between text-[0.68rem] text-muted">
                <span>{stock.series[0]?.date ?? ''}</span>
                <span>{stock.series[stock.series.length - 1]?.date ?? ''}</span>
              </div>
            </Card>

            <Card>
              <SectionTitle hint={`${plan.phase_progress.length} phases`}>Phase progress</SectionTitle>
              <div className="space-y-3">
                {plan.phase_progress.map((p) => (
                  <div key={p.phase}>
                    <div className="mb-1 flex justify-between text-[0.78rem]">
                      <span className="text-ink-soft">{p.phase}</span>
                      <span className="mono text-muted">{p.done}/{p.total}</span>
                    </div>
                    <Bar value={p.done} max={p.total} tone="navy" />
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </ScrollReveal>

      {/* modules + market */}
      <ScrollReveal variant="fade-up" delay={250} once>
        <div className="grid gap-5 lg:grid-cols-[1.4fr_1fr]">
          <Card>
            <SectionTitle hint={`${modules.length} modules`}>Open modules</SectionTitle>
            {modules.length === 0 ? (
              <Empty>Nothing started. Open the curriculum and begin A1.</Empty>
            ) : (
              <div className="grid gap-2.5 sm:grid-cols-2">
                {modules.map((m) => (
                  <Link
                    key={m.id}
                    to={`/learn?module=${m.id}`}
                    className="rounded-xl border border-line bg-surface-2 px-4 py-3 transition hover:border-line-strong"
                  >
                    <div className="flex items-center gap-2">
                      <Badge tone="gold">{m.id}</Badge>
                      <span className="text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">{m.status}</span>
                    </div>
                    <div className="mt-1.5 text-[0.9rem] font-semibold text-ink">{m.title}</div>
                    <div className="text-[0.75rem] text-muted">{m.track} · weeks {m.weeks.join(', ')}</div>
                  </Link>
                ))}
              </div>
            )}
          </Card>

          <div className="space-y-5">
            <Card>
              <SectionTitle>Comp trajectory</SectionTitle>
              <div className="space-y-2">
                {comp.map((c) => (
                  <div key={c.role} className="flex items-center justify-between rounded-lg border border-line bg-surface-2 px-3.5 py-2.5">
                    <span className="text-[0.85rem] text-ink-soft">{c.role}</span>
                    <span className="mono text-[0.85rem] font-bold text-gold">{c.comp}</span>
                  </div>
                ))}
              </div>
            </Card>

            {breaches.length > 0 ? (
              <Card>
                <SectionTitle>Discipline log</SectionTitle>
                <ul className="space-y-1.5 text-[0.83rem] text-muted">
                  {breaches.slice(-6).map((b, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-bad">•</span>
                      {b}
                    </li>
                  ))}
                </ul>
              </Card>
            ) : null}
          </div>
        </div>
      </ScrollReveal>

      {/* bootcamp */}
      <ScrollReveal variant="fade-up" delay={300} once>
        <Card>
          <SectionTitle hint="the daily rhythm">Bootcamp schedule</SectionTitle>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {bootcamp.map((b) => (
              <div key={b.name} className="rounded-xl border border-line bg-surface-2 p-4">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-ink">{b.name}</span>
                  <Badge tone="neutral">{b.mins}m</Badge>
                </div>
                <div className="mono mt-2 text-[0.76rem] text-gold">{b.start} – {b.end}</div>
                <p className="mt-1.5 text-[0.82rem] text-muted">{b.desc}</p>
              </div>
            ))}
          </div>
        </Card>
      </ScrollReveal>
    </div>
  )
}
