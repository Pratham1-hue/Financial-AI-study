import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { QuoteLine } from '../components/Quote'
import { fireConfetti } from '../lib/confetti'
import { StaggerGroup } from '../components/motion'
import { Badge, Bar, Button, Card, Empty, PageHeader, SectionTitle, Spinner, Tabs, cx, inputCls } from '../components/ui'
import { api, type Question } from '../lib/api'
import { useApi } from '../lib/hooks'

type Tab = 'practice' | 'drill' | 'gates'

const LETTERS = ['A', 'B', 'C', 'D', 'E']

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

/* ------------------------------------------------------------------ practice */
function Practice({ initialModule }: { initialModule: string | null }) {
  const { data: bank } = useApi<{ questions: Question[]; counts: { tracks: string[]; modules: string[]; diffs: string[] } }>('/api/quiz/bank')
  const [track, setTrack] = useState<string>('all')
  const [mod, setMod] = useState<string>(initialModule ?? 'all')
  const [diff, setDiff] = useState<string>('all')
  const [size, setSize] = useState(10)
  const [run, setRun] = useState<Question[] | null>(null)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [result, setResult] = useState<null | {
    score: number
    total: number
    pct: number
    review: { id: string; q: string; module: string; diff: string; you: string | null; correct: string; ok: boolean; exp: string }[]
    weak_topics: string[]
    xp: number
  }>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (initialModule) setMod(initialModule)
  }, [initialModule])

  const pool = useMemo(() => {
    let qs = bank?.questions ?? []
    if (track !== 'all') qs = qs.filter((q) => q.track === track)
    if (mod !== 'all') qs = qs.filter((q) => q.module === mod)
    if (diff !== 'all') qs = qs.filter((q) => q.diff === diff)
    return qs
  }, [bank, track, mod, diff])

  function start() {
    if (pool.length === 0) return
    setRun(shuffle(pool).slice(0, Math.min(size, pool.length)))
    setAnswers({})
    setResult(null)
    setError(null)
  }

  async function submit() {
    if (!run) return
    setBusy(true)
    setError(null)
    try {
      const res = await api.post<typeof result>('/api/quiz/submit', {
        quiz_id: `practice-${track}-${mod}-${diff}`,
        qids: run.map((q) => q.id),
        answers,
      })
      setResult(res)
      if (res && res.pct >= 80) {
        void fireConfetti(window.innerWidth / 2, window.innerHeight / 3, 140)
      }
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
      <div className="space-y-4">
        <Card>
          <SectionTitle>Build a set</SectionTitle>
          <div className="space-y-3.5">
            <label className="block">
              <span className="mb-1 block text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">Track</span>
              <select className={inputCls} value={track} onChange={(e) => setTrack(e.target.value)}>
                <option value="all">All tracks</option>
                {(bank?.counts.tracks ?? []).map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">Module</span>
              <select className={inputCls} value={mod} onChange={(e) => setMod(e.target.value)}>
                <option value="all">All modules</option>
                {(bank?.counts.modules ?? []).map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">Difficulty</span>
              <select className={inputCls} value={diff} onChange={(e) => setDiff(e.target.value)}>
                <option value="all">Any</option>
                {(bank?.counts.diffs ?? []).map((d) => (
                  <option key={d}>{d}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">Questions</span>
              <input type="number" min={3} max={40} className={inputCls} value={size} onChange={(e) => setSize(Number(e.target.value) || 10)} />
            </label>
            <Button variant="primary" size="lg" className="w-full" onClick={start} disabled={pool.length === 0}>
              {run ? 'New set' : 'Start set'}
            </Button>
            <div className="text-center text-[0.75rem] text-muted">{pool.length} questions match</div>
          </div>
        </Card>
        <Card>
          <QuoteLine text="The more I practice, the luckier I get." author="Gary Player" />
        </Card>
      </div>

      <div className="space-y-5">
        {error ? <Empty>{error}</Empty> : null}

        {result ? (
          <Card className="fade-up">
            <div className="flex flex-wrap items-center gap-5">
              <div className="relative grid h-24 w-24 place-items-center">
                <svg viewBox="0 0 100 100" className="absolute h-24 w-24 -rotate-90">
                  <circle cx="50" cy="50" r="44" fill="none" stroke="var(--border)" strokeWidth="9" />
                  <circle
                    cx="50"
                    cy="50"
                    r="44"
                    fill="none"
                    stroke={result.pct >= 80 ? 'var(--ok)' : result.pct >= 60 ? 'var(--gold)' : 'var(--bad)'}
                    strokeWidth="9"
                    strokeLinecap="round"
                    strokeDasharray={2 * Math.PI * 44}
                    strokeDashoffset={2 * Math.PI * 44 * (1 - result.pct / 100)}
                  />
                </svg>
                <span className="mono text-[1.4rem] font-bold text-ink">{result.pct}%</span>
              </div>
              <div>
                <h3 className="font-display text-[1.3rem] font-bold text-ink">
                  {result.score} / {result.total} correct
                </h3>
                <p className="mt-1 text-[0.86rem] text-muted">
                  {result.pct >= 80
                    ? 'Gate-grade. This is the standard.'
                    : result.pct >= 60
                      ? 'Close. Miss the same idea twice and it goes on the board.'
                      : 'Below the bar. Re-read the module, then run it again.'}
                </p>
                {result.weak_topics.length > 0 ? (
                  <div className="mt-2.5 flex flex-wrap gap-1.5">
                    {result.weak_topics.map((w) => (
                      <Badge key={w} tone="bad">
                        weak: {w}
                      </Badge>
                    ))}
                  </div>
                ) : null}
              </div>
              <div className="ml-auto flex gap-2">
                <Button onClick={start}>Run another set</Button>
                <Button variant="ghost" onClick={() => setResult(null)}>
                  Review only
                </Button>
              </div>
            </div>
          </Card>
        ) : null}

        {run ? (
          <StaggerGroup className="space-y-4">
            {run.map((q, i) => {
              const rv = result?.review.find((r) => r.id === q.id)
              return (
                <Card key={q.id} className={cx(rv && (rv.ok ? 'border-[color-mix(in_srgb,var(--ok)_35%,transparent)]' : 'border-[color-mix(in_srgb,var(--bad)_35%,transparent)]'))}>
                  <div className="mb-3 flex items-center gap-2">
                    <span className="mono text-[0.72rem] font-bold text-gold">Q{i + 1}</span>
                    <Badge tone="neutral">{q.module}</Badge>
                    <Badge tone="neutral">{q.diff}</Badge>
                    {rv ? <Badge tone={rv.ok ? 'ok' : 'bad'}>{rv.ok ? 'correct' : 'wrong'}</Badge> : null}
                  </div>
                  <p className="text-[0.98rem] font-medium text-ink">{q.q}</p>
                  <div className="mt-3.5 space-y-2">
                    {q.opts.map((opt, oi) => {
                      const chosen = answers[q.id] === oi
                      const showCorrect = !!result && rv?.correct === opt
                      const showWrong = !!result && chosen && !rv?.ok
                      return (
                        <button
                          key={oi}
                          disabled={!!result}
                          onClick={() => setAnswers((a) => ({ ...a, [q.id]: oi }))}
                          className={cx(
                            'press flex w-full items-start gap-3 rounded-xl border px-3.5 py-2.5 text-left text-[0.88rem] transition disabled:cursor-default',
                            showCorrect
                              ? 'animate-correct border-[color-mix(in_srgb,var(--ok)_45%,transparent)] bg-ok-soft text-ok'
                              : showWrong
                                ? 'animate-wrong border-[color-mix(in_srgb,var(--bad)_45%,transparent)] bg-bad-soft text-bad'
                                : chosen
                                  ? 'animate-answer-pop border-gold bg-gold-soft text-ink'
                                  : 'border-line bg-surface-2 text-ink-soft hover:border-line-strong',
                          )}
                        >
                          <span className="mono mt-0.5 text-[0.72rem] font-bold opacity-70">{LETTERS[oi]}</span>
                          <span>{opt}</span>
                        </button>
                      )
                    })}
                  </div>
                  {rv ? <p className="mt-3 rounded-lg bg-surface-2 px-3.5 py-2.5 text-[0.83rem] text-muted">{rv.exp}</p> : null}
                </Card>
              )
            })}

            {!result ? (
              <div className="sticky bottom-4 flex items-center gap-3 rounded-2xl border border-line bg-surface/95 px-5 py-3.5 shadow-lg backdrop-blur">
                <span className="text-[0.86rem] text-muted">
                  {Object.keys(answers).length} / {run.length} answered
                </span>
                <Button
                  variant="primary"
                  size="lg"
                  className="ml-auto"
                  disabled={busy || Object.keys(answers).length === 0}
                  onClick={() => void submit()}
                >
                  {busy ? 'Grading…' : 'Submit set'}
                </Button>
              </div>
            ) : null}
          </StaggerGroup>
        ) : (
          <Empty>Pick a filter and start a set. Ten questions, no notes, no pausing.</Empty>
        )}
      </div>
    </div>
  )
}

/* --------------------------------------------------------------------- drill */
interface Card {
  id: string
  box: number
  module: string
  diff: string
  q: string
  opts: string[]
}

function Drill() {
  const { data, loading, reload } = useApi<{
    due: Card[]
    new: Card[]
    due_count: number
    new_count: number
    retention: number
    mastery: { module: string; cards: number; retention: number }[]
  }>('/api/drill')

  const [queue, setQueue] = useState<Card[] | null>(null)
  const [picked, setPicked] = useState<number | null>(null)
  const [revealed, setRevealed] = useState(false)
  const [done, setDone] = useState(0)

  useEffect(() => {
    if (data && queue === null) {
      setQueue([...data.due, ...data.new.slice(0, 12)])
    }
  }, [data, queue])

  const card = queue && queue.length > 0 ? queue[0] : null

  const grade = useCallback(
    async (correct: boolean) => {
      if (!card) return
      try {
        await api.post('/api/drill/grade', { qid: card.id, correct })
      } catch {
        /* keep moving */
      }
      setQueue((q) => (q ? q.slice(1) : q))
      setPicked(null)
      setRevealed(false)
      setDone((d) => d + 1)
      void reload(true)
    },
    [card, reload],
  )

  if (loading && !data) return <Spinner label="Loading the deck" />
  if (!data) return <Empty>No drill data.</Empty>

  const total = queue?.length ?? 0

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
      <div className="space-y-5">
        {!card ? (
          <Card className="text-center">
            <h3 className="font-display text-[1.4rem] font-bold text-ink">Deck clear.</h3>
            <p className="mt-1.5 text-[0.88rem] text-muted">
              {done > 0 ? `${done} cards graded this sitting. ` : ''}
              Cards come back when they are due. That is the point.
            </p>
          </Card>
        ) : (
          <Card key={card.q} className="fade-up">
            <div className="mb-3 flex items-center gap-2">
              <span className="mono text-[0.72rem] font-bold text-gold">card {(done + 1).toString().padStart(2, '0')}</span>
              <Badge tone="neutral">{card.module}</Badge>
              <Badge tone="neutral">{card.diff}</Badge>
              <Badge tone={card.box === 0 ? 'warn' : 'ok'}>box {card.box}</Badge>
              <span className="ml-auto text-[0.75rem] text-muted">{total} left</span>
            </div>

            <p className="text-[1.05rem] font-medium text-ink">{card.q}</p>

            <div className="mt-4 space-y-2">
              {card.opts.map((opt, oi) => (
                <button
                  key={oi}
                  disabled={revealed}
                  onClick={() => setPicked(oi)}
                  className={cx(
                    'press flex w-full items-start gap-3 rounded-xl border px-3.5 py-2.5 text-left text-[0.88rem] transition',
                    picked === oi ? 'animate-answer-pop border-gold bg-gold-soft text-ink' : 'border-line bg-surface-2 text-ink-soft hover:border-line-strong',
                  )}
                >
                  <span className="mono mt-0.5 text-[0.72rem] font-bold opacity-70">{LETTERS[oi]}</span>
                  <span>{opt}</span>
                </button>
              ))}
            </div>

            {!revealed ? (
              <Button variant="primary" size="lg" className="mt-4 w-full" disabled={picked === null} onClick={() => setRevealed(true)}>
                Reveal
              </Button>
            ) : (
              <div className="mt-4 flex gap-2.5 slide-up">
                <Button variant="danger" size="lg" className="flex-1" onClick={() => void grade(false)}>
                  I missed it
                </Button>
                <Button variant="primary" size="lg" className="flex-1" onClick={() => void grade(true)}>
                  I knew it
                </Button>
              </div>
            )}
            <p className="mt-3 text-center text-[0.75rem] text-muted">Be honest — the schedule is only as good as your honesty.</p>
          </Card>
        )}
      </div>

      <div className="space-y-4">
        <Card>
          <SectionTitle>Deck health</SectionTitle>
          <div className="space-y-3">
            <div className="flex justify-between text-[0.86rem]">
              <span className="text-ink-soft">Due now</span>
              <span className="mono font-bold text-ink">{data.due_count}</span>
            </div>
            <div className="flex justify-between text-[0.86rem]">
              <span className="text-ink-soft">Fresh cards</span>
              <span className="mono font-bold text-ink">{data.new_count}</span>
            </div>
            <div>
              <Bar value={data.retention * 100} max={100} tone={data.retention >= 0.8 ? 'ok' : 'gold'} label={`Retention ${Math.round(data.retention * 100)}%`} />
            </div>
          </div>
        </Card>

        <Card>
          <SectionTitle>Mastery by module</SectionTitle>
          {data.mastery.length === 0 ? (
            <Empty>No cards graded yet.</Empty>
          ) : (
            <div className="space-y-2.5">
              {data.mastery.map((m) => (
                <div key={m.module}>
                  <div className="mb-1 flex justify-between text-[0.8rem]">
                    <span className="text-ink-soft">{m.module}</span>
                    <span className="mono text-muted">
                      {m.cards} cards · {Math.round(m.retention * 100)}%
                    </span>
                  </div>
                  <Bar value={m.retention * 100} max={100} tone={m.retention >= 0.8 ? 'ok' : 'navy'} />
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}

/* --------------------------------------------------------------------- gates */
interface GateDetail {
  module: string
  title: string
  status: string
  missing_prereqs: string[]
  cooldown_hours: number | null
  pass_marks: { mcq: number; oral: number; min_chars: number }
  mcq: Question[]
  oral: { prompt: string; points: string[] }[]
}

function Gates({ initialModule }: { initialModule: string | null }) {
  const { data: gates, loading, reload } = useApi<{ id: string; title: string; track: string; status: string; missing_prereqs: string[]; mcq: number; attempts: number }[]>('/api/gates')
  const [mid, setMid] = useState<string | null>(initialModule)
  const [detail, setDetail] = useState<GateDetail | null>(null)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [texts, setTexts] = useState<string[]>([])
  const [claims, setClaims] = useState<boolean[][]>([])
  const [result, setResult] = useState<null | { passed: boolean; mcq_pct: number; oral_pct: number; status: string; review: { id: string; q: string; ok: boolean; correct: string; exp: string; you: string | null }[] }>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (initialModule) setMid(initialModule)
  }, [initialModule])

  useEffect(() => {
    if (!mid) return
    let alive = true
    setResult(null)
    setError(null)
    setDetail(null)
    api
      .get<GateDetail>(`/api/gates/${mid}`)
      .then((d) => {
        if (!alive) return
        setDetail(d)
        setAnswers({})
        setTexts(d.oral.map(() => ''))
        setClaims(d.oral.map((o) => o.points.map(() => false)))
      })
      .catch((e) => alive && setError((e as Error).message))
    return () => {
      alive = false
    }
  }, [mid])

  async function submit() {
    if (!detail) return
    setBusy(true)
    setError(null)
    try {
      const res = await api.post<typeof result>(`/api/gates/${detail.module}/submit`, {
        answers,
        oral_hits: claims.map((row) => row.filter(Boolean).length),
        texts,
      })
      setResult(res)
      if (res?.passed) {
        void fireConfetti(window.innerWidth / 2, window.innerHeight / 3, 140)
      }
      void reload(true)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  if (loading && !gates) return <Spinner label="Loading gates" />

  return (
    <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
      <Card padded={false} className="overflow-hidden">
        <div className="border-b border-line p-4 text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">
          Mastery gates
        </div>
        <div className="max-h-[600px] overflow-y-auto p-2">
          <StaggerGroup className="space-y-0.5">
            {(gates ?? []).map((g) => (
              <button
                key={g.id}
                onClick={() => setMid(g.id)}
                className={cx('press mb-1 w-full rounded-xl px-3.5 py-3 text-left transition', mid === g.id ? 'bg-gold-soft' : 'hover:bg-surface-2')}
              >
              <div className="flex items-center gap-2">
                <span className={cx('mono text-[0.7rem] font-bold', mid === g.id ? 'text-gold' : 'text-muted')}>{g.id}</span>
                <Badge tone={g.status === 'Passed' || g.status === 'Mastered' ? 'ok' : g.status === 'Ready' ? 'gold' : 'neutral'}>{g.status}</Badge>
              </div>
              <div className="mt-1 text-[0.86rem] font-semibold text-ink">{g.title}</div>
              <div className="text-[0.72rem] text-muted">
                {g.mcq} questions · {g.attempts} attempts
              </div>
            </button>
            ))}
          </StaggerGroup>
        </div>
      </Card>

      <div className="space-y-5">
        {error ? <Empty>{error}</Empty> : null}
        {result ? (
          <Card className={cx('fade-up', result.passed ? 'border-[color-mix(in_srgb,var(--ok)_45%,transparent)]' : 'border-[color-mix(in_srgb,var(--bad)_40%,transparent)]')}>
            <h3 className="font-display text-[1.5rem] font-bold text-ink">
              {result.passed ? 'Gate passed.' : 'Not yet.'}
            </h3>
            <p className="mt-1 text-[0.9rem] text-muted">
              MCQ {result.mcq_pct}% · teach-back {result.oral_pct}% · required {detail?.pass_marks.mcq}% / {detail?.pass_marks.oral}%
            </p>
            <p className="mt-2 text-[0.88rem] text-ink-soft">
              {result.passed
                ? '+150 XP. That module is yours now — say so out loud.'
                : 'The weak spots are below. Fix them, come back after the cooldown.'}
            </p>
            {result.review ? (
              <StaggerGroup className="mt-4 space-y-2">
                {result.review.filter((r) => !r.ok).map((r) => (
                  <div key={r.id} className="rounded-xl border border-line bg-surface-2 px-3.5 py-2.5">
                    <p className="text-[0.87rem] font-medium text-ink">{r.q}</p>
                    <p className="mt-1 text-[0.8rem] text-ok">✓ {r.correct}</p>
                    {r.you ? <p className="text-[0.8rem] text-bad">✗ {r.you}</p> : null}
                    <p className="mt-1 text-[0.8rem] text-muted">{r.exp}</p>
                  </div>
                ))}
              </StaggerGroup>
            ) : null}
          </Card>
        ) : null}

        {!detail ? (
          loading ? null : (
            <Empty>Pick a gate. The gate is the only thing that proves a module is finished.</Empty>
          )
        ) : (
          <div key={mid} className="space-y-5 page-enter">
            <Card>
              <div className="flex flex-wrap items-center gap-3">
                <h2 className="font-display text-[1.5rem] font-bold text-ink">{detail.title}</h2>
                <Badge tone={detail.status === 'Passed' ? 'ok' : detail.status === 'Ready' ? 'gold' : 'neutral'}>{detail.status}</Badge>
                {detail.cooldown_hours ? <Badge tone="bad">cooldown {detail.cooldown_hours}h</Badge> : null}
              </div>
              <p className="mt-2 text-[0.87rem] text-muted">
                Two parts: {detail.mcq.length} multiple-choice for {detail.pass_marks.mcq}%, then a written teach-back for{' '}
                {detail.pass_marks.oral}%. Type at least {detail.pass_marks.min_chars} characters per answer — half-answers do not count.
              </p>
              {detail.missing_prereqs.length > 0 ? (
                <div className="mt-3 rounded-xl border border-[color-mix(in_srgb,var(--warn)_30%,transparent)] bg-warn-soft px-4 py-2.5 text-[0.83rem] text-warn">
                  Prerequisites open: {detail.missing_prereqs.join(', ')}
                </div>
              ) : null}
            </Card>

            <Card>
              <SectionTitle hint={`${detail.mcq.length} questions`}>Part 1 — Multiple choice</SectionTitle>
              <StaggerGroup className="space-y-5">
                {detail.mcq.map((q, i) => (
                  <div key={q.id}>
                    <div className="mb-2 flex items-center gap-2">
                      <span className="mono text-[0.72rem] font-bold text-gold">Q{i + 1}</span>
                      <Badge tone="neutral">{q.diff}</Badge>
                    </div>
                    <p className="text-[0.95rem] font-medium text-ink">{q.q}</p>
                    <div className="mt-2.5 space-y-2">
                      {q.opts.map((opt, oi) => (
                        <button
                          key={oi}
                          onClick={() => setAnswers((a) => ({ ...a, [q.id]: oi }))}
                          className={cx(
                            'press flex w-full items-start gap-3 rounded-xl border px-3.5 py-2.5 text-left text-[0.87rem] transition',
                            answers[q.id] === oi ? 'animate-answer-pop border-gold bg-gold-soft text-ink' : 'border-line bg-surface-2 text-ink-soft hover:border-line-strong',
                          )}
                        >
                          <span className="mono mt-0.5 text-[0.72rem] font-bold opacity-70">{LETTERS[oi]}</span>
                          <span>{opt}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </StaggerGroup>
            </Card>

            <Card>
              <SectionTitle hint="be honest, the rubric is yours to hit">Part 2 — Teach it back</SectionTitle>
              <StaggerGroup className="space-y-6">
                {detail.oral.map((o, i) => (
                  <div key={i} className="rounded-xl border border-line bg-surface-2 p-4">
                    <p className="text-[0.95rem] font-semibold text-ink">{o.prompt}</p>
                    <div className="mt-3 space-y-1.5">
                      {o.points.map((pt, pi) => (
                        <label key={pi} className="flex items-start gap-2.5 text-[0.84rem] text-ink-soft">
                          <input
                            type="checkbox"
                            className="mt-0.5"
                            checked={claims[i]?.[pi] ?? false}
                            onChange={(e) =>
                              setClaims((all) => {
                                const next = all.map((row) => [...row])
                                next[i][pi] = e.target.checked
                                return next
                              })
                            }
                          />
                          {pt}
                        </label>
                      ))}
                    </div>
                    <div className="mt-3 flex items-center gap-2 text-[0.78rem] text-muted">
                      <span className="mono font-bold text-gold">
                        {(claims[i] ?? []).filter(Boolean).length}/{o.points.length}
                      </span>{' '}
                      rubric points claimed
                      <span className="text-muted">· claim one per bullet you truly covered</span>
                    </div>
                    <textarea
                      className={cx(inputCls, 'mt-3 min-h-[130px] resize-y')}
                      placeholder="Explain it like you are teaching a smart friend who has never seen it…"
                      value={texts[i] ?? ''}
                      onChange={(e) => setTexts((t) => t.map((v, vi) => (vi === i ? e.target.value : v)))}
                    />
                    <div className={cx('mt-1 text-[0.74rem]', (texts[i]?.length ?? 0) >= detail.pass_marks.min_chars ? 'text-ok' : 'text-muted')}>
                      {texts[i]?.length ?? 0} / {detail.pass_marks.min_chars} characters
                    </div>
                  </div>
                ))}
              </StaggerGroup>

              <div className="sticky bottom-4 mt-5 flex items-center gap-3 rounded-2xl border border-line bg-surface/95 px-5 py-3.5 shadow-lg backdrop-blur">
                <span className="text-[0.84rem] text-muted">
                  {Object.keys(answers).length}/{detail.mcq.length} MCQ answered
                </span>
                <Button variant="primary" size="lg" className="ml-auto" disabled={busy} onClick={() => void submit()}>
                  {busy ? 'Submitting…' : 'Submit the gate'}
                </Button>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

/* ---------------------------------------------------------------------- page */
export function Quizzes() {
  const [params, setParams] = useSearchParams()
  const raw = params.get('tab')
  const tab: Tab = raw === 'drill' || raw === 'gates' ? raw : 'practice'
  const moduleParam = params.get('module')

  function changeTab(id: Tab) {
    const next = new URLSearchParams(params)
    if (id === 'practice') next.delete('tab')
    else next.set('tab', id)
    setParams(next, { replace: true })
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Prove it"
        title="Quizzes &amp; Gates"
        subtitle="Practice sets, spaced-repetition drilling, and the oral-style mastery gates that actually end a module."
      />

      <Tabs
        tabs={[
          { id: 'practice', label: 'Practice' },
          { id: 'drill', label: 'Daily drill' },
          { id: 'gates', label: 'Mastery gates' },
        ]}
        value={tab}
        onChange={changeTab}
      />

      {tab === 'practice' ? <Practice initialModule={moduleParam} /> : null}
      {tab === 'drill' ? <Drill /> : null}
      {tab === 'gates' ? <Gates initialModule={moduleParam} /> : null}
    </div>
  )
}
