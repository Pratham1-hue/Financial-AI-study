import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { fireConfetti } from '../lib/confetti'
import { fmtClock } from '../lib/format'
import { Badge, Button, Card, Empty, LoadingButton, PageHeader, ProgressRing, SectionTitle, Spinner, cx } from '../components/ui'
import { api } from '../lib/api'
import { useApi } from '../lib/hooks'
import { useToast } from '../components/Toast'

type Exam = {
  id: string
  title: string
  modules: string[]
  questions: number
  time_limit: number
  pass_mark: number
  status: 'open' | 'attempted' | 'mastered'
  score: number | null
  at: string | null
}

type ExamResult = {
  score: number
  total: number
  pct: number
  passed: boolean
  review: { id: string; q: string; module: string; diff: string; you: string | null; correct: string; ok: boolean; exp: string }[]
  weak_topics: string[]
  xp: number
}

type ExamQuestion = {
  id: string
  track: string
  module: string
  diff: string
  q: string
  opts: string[]
}

function ExamCard({ exam, onStart }: { exam: Exam; onStart: () => void }) {
  const passed = exam.status === 'mastered'
  return (
    <Card className={cx('transition hover:shadow-lg', passed ? 'border-[color-mix(in_srgb,var(--ok)_30%,transparent)]' : '')}>
      <div className="flex items-center justify-between px-4 py-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge tone={passed ? 'ok' : exam.status === 'attempted' ? 'warn' : 'gold'}>
              {exam.status === 'mastered' ? 'Mastered' : exam.status === 'attempted' ? 'Attempted' : 'Open'}
            </Badge>
            <Badge tone="neutral">{exam.questions} Q</Badge>
            <Badge tone="neutral">{Math.round(exam.time_limit / 60)} min</Badge>
          </div>
          <h3 className="font-display text-[1.1rem] font-bold text-ink">{exam.title}</h3>
          <p className="text-[0.8rem] text-muted">{exam.modules.join(' · ')}</p>
        </div>
        <div className="text-right">
          {exam.score !== null ? (
            <div className={cx('mono text-[1.3rem] font-bold', passed ? 'text-ok' : 'text-bad')}>
              {exam.score}%
            </div>
          ) : (
            <div className="text-[0.8rem] text-muted">Not yet taken</div>
          )}
          <div className="text-[0.7rem] text-muted uppercase tracking-wider">{passed ? 'Gate-grade pass' : `Pass ≥ ${exam.pass_mark}%`}</div>
        </div>
      </div>
      <div className="px-4 pb-3">
        <Button
          variant={passed ? 'ghost' : 'primary'}
          onClick={onStart}
          disabled={passed}
          className="w-full"
        >
          {passed ? 'Already mastered' : exam.status === 'attempted' ? 'Retake exam' : 'Start exam'}
        </Button>
      </div>
    </Card>
  )
}

export function Exams() {
  const navigate = useNavigate()
  const { ok, bad } = useToast()
  const { data, loading, error, reload } = useApi<{ exams: Exam[] }>('/api/exams')
  const [taking, setTaking] = useState<string | null>(null)
  const [examData, setExamData] = useState<{ id: string; title: string; time_limit: number; questions: ExamQuestion[] } | null>(null)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [startedAt, setStartedAt] = useState(0)
  const [result, setResult] = useState<ExamResult | null>(null)
  const [busy, setBusy] = useState(false)
  const timerRef = useRef(0)

  // countdown timer hook - must come before any early return (Rules of Hooks)
  useEffect(() => {
    if (!examData || !startedAt || result) return
    timerRef.current = window.setInterval(() => {
      const left = Math.max(0, examData.time_limit - Math.floor((Date.now() - startedAt) / 1000))
      if (left === 0) {
        void autoSubmit()
      }
    }, 1000)
    return () => window.clearInterval(timerRef.current)
  }, [examData, startedAt, result])

  if (loading && !data) return <Spinner label="Loading exams" />
  if (error) return <Empty>{error}</Empty>

  const exams = data?.exams ?? []

  // countdown (for display)
  let timeLeft = 0
  if (examData && startedAt) {
    timeLeft = Math.max(0, examData.time_limit - Math.floor((Date.now() - startedAt) / 1000))
  }

  async function autoSubmit() {
    if (!examData) return
    setBusy(true)
    try {
      const res = (await api.post<ExamResult>(`/api/exams/${examData.id}/submit`, { answers })) as ExamResult
      setResult(res)
      if (res.passed) {
        void fireConfetti(window.innerWidth / 2, window.innerHeight / 3, 140)
        ok('Exam passed.', `+150 XP. ${examData.title} is mastered.`)
      } else {
        bad('Not yet.', `Scored ${res.pct}%. Re-study the weak topics and retake.`)
      }
      void reload(true)
    } catch (e) {
      bad('Submit failed.', (e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function startExam(id: string) {
    const ex = exams.find((e) => e.id === id)
    if (!ex) return
    setTaking(id)
    setAnswers({})
    setResult(null)
    try {
      const d = await api.get<{ id: string; title: string; time_limit: number; questions: ExamQuestion[] }>(`/api/exams/${id}`)
      setExamData(d)
      setStartedAt(Date.now())
    } catch (e) {
      bad('Could not load exam.', (e as Error).message)
      setTaking(null)
    }
  }

  // exams list view
  if (!taking) {
    return (
      <div className="space-y-6">
        <PageHeader
          eyebrow="Formal mastery exams"
          title="Exams"
          subtitle="Proctored-style, multi-module assessments. 80% to master. No notes, no pausing the clock."
        />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {exams.map((ex) => (
            <ExamCard key={ex.id} exam={ex} onStart={() => void startExam(ex.id)} />
          ))}
        </div>
        <div className="rounded-xl border border-line bg-surface-2 p-5 text-[0.85rem] text-muted">
          <p className="font-semibold mb-1">How exams work</p>
          <ul className="space-y-1 list-disc list-inside text-muted">
            <li>Each exam draws from real question-bank items across its modules.</li>
            <li>A timer runs server-side; you can leave and return, but the clock keeps ticking.</li>
            <li>Score ≥ 80% to master — that unlocks the module gate and counts toward your Mastery Index.</li>
            <li>Wrong answers are reviewed with explanations; weak topics feed your daily drill.</li>
          </ul>
        </div>
      </div>
    )
  }

  // taking the exam
  if (!examData) return <Empty>Exam not found.</Empty>

  const answered = Object.keys(answers).length
  const pctAnswered = examData.questions.length ? Math.round((answered / examData.questions.length) * 100) : 0

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Exam in progress"
        title={examData.title}
        right={
          <div className="flex items-center gap-3">
            <ProgressRing pct={pctAnswered} size={70} stroke={8} label={fmtClock(timeLeft)} sub="remaining" />
            <Badge tone={timeLeft <= 60 ? 'bad' : 'neutral'}>{answered}/{examData.questions.length} answered</Badge>
          </div>
        }
      />

      {timeLeft <= 0 && !result ? (
        <Card className="bg-bad-soft border-[color-mix(in_srgb,var(--bad)_30%,transparent)] p-5 text-center">
          <h3 className="font-display text-xl font-bold text-bad">Time is up.</h3>
          <p className="mt-1 text-muted">The exam is being submitted automatically.</p>
        </Card>
      ) : null}

      {result ? (
        <Card className={cx('fade-up', result.passed ? 'border-[color-mix(in_srgb,var(--ok)_40%,transparent)]' : 'border-[color-mix(in_srgb,var(--bad)_40%,transparent)]')}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className={cx('font-display text-[1.5rem] font-bold', result.passed ? 'text-ok' : 'text-bad')}>
                {result.passed ? 'Exam mastered.' : 'Not yet.'}
              </h3>
              <p className="mt-1 text-[0.9rem] text-muted">
                {result.score}/{result.total} correct · {result.pct}% · pass mark 80%
              </p>
            </div>
            <div className="ml-auto flex gap-2">
              {!result.passed && <Button variant="ghost" onClick={() => navigate('/exams')}>Retake</Button>}
              <Button variant="secondary" onClick={() => navigate('/exams')}>Back to exams</Button>
            </div>
          </div>

          {result.passed && (
            <div className="mb-4 rounded-xl border border-[color-mix(in_srgb,var(--ok)_30%,transparent)] bg-ok-soft px-4 py-3 text-[0.88rem] text-ok">
              +150 XP · {examData.title} added to your Mastery Index.
            </div>
          )}

          {result.review && result.review.filter((r) => !r.ok).length > 0 && (
            <div className="mb-4">
              <SectionTitle>Review — get these right next time</SectionTitle>
              <div className="space-y-2.5">
                {result.review.filter((r) => !r.ok).map((r) => (
                  <div key={r.id} className="rounded-xl border border-line bg-surface-2 px-3.5 py-2.5">
                    <p className="text-[0.87rem] font-medium text-ink">{r.q}</p>
                    <p className="mt-1 text-[0.8rem] text-ok">✓ {r.correct}</p>
                    {r.you ? <p className="text-[0.8rem] text-bad">✗ {r.you}</p> : null}
                    <p className="mt-1 text-[0.8rem] text-muted">{r.exp}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.weak_topics.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {result.weak_topics.map((w) => (
                <Badge key={w} tone="bad">weak: {w}</Badge>
              ))}
            </div>
          )}
        </Card>
      ) : null}

      {!result && timeLeft > 0 && (
        <form onSubmit={(e) => { e.preventDefault(); void autoSubmit() }} className="space-y-5">
          {examData.questions.map((q, i) => {
            const chosen = answers[q.id]
            return (
              <Card key={q.id} className="fade-up">
                <div className="mb-3 flex items-center gap-2">
                  <span className="mono text-[0.72rem] font-bold text-gold">Q{i + 1}</span>
                  <Badge tone="neutral">{q.module}</Badge>
                  <Badge tone="neutral">{q.diff}</Badge>
                  <span className="ml-auto text-[0.72rem] text-muted">{chosen !== undefined ? 'answered' : 'unanswered'}</span>
                </div>
                <p className="text-[0.98rem] font-medium text-ink">{q.q}</p>
                <div className="mt-3.5 space-y-2">
                  {q.opts.map((opt, oi) => (
                    <button
                      key={oi}
                      type="button"
                      onClick={() => setAnswers((a) => ({ ...a, [q.id]: oi }))}
                      className={cx(
                        'flex w-full items-start gap-3 rounded-xl border px-3.5 py-2.5 text-left text-[0.87rem] transition',
                        chosen === oi ? 'border-gold bg-gold-soft text-ink' : 'border-line bg-surface-2 text-ink-soft hover:border-line-strong',
                      )}
                    >
                      <span className="mono mt-0.5 text-[0.72rem] font-bold opacity-70">{['A','B','C','D'][oi]}</span>
                      <span>{opt}</span>
                    </button>
                  ))}
                </div>
              </Card>
            )
          })}
          <div className="sticky bottom-6 mt-8 flex items-center justify-between rounded-2xl border border-line bg-surface/95 px-6 py-4 shadow-lg backdrop-blur">
            <span className="text-[0.86rem] text-muted">{answered} / {examData.questions.length} answered · {fmtClock(timeLeft)} left</span>
            <LoadingButton variant="primary" loading={busy} onClick={() => void autoSubmit()} disabled={answered === 0}>
              {busy ? 'Submitting…' : 'Submit exam'}
            </LoadingButton>
          </div>
        </form>
      )}
    </div>
  )
}
