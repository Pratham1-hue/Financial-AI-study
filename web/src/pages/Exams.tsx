import { useEffect, useRef, useState } from 'react'

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
  xp_gain: number
}

type ExamQuestion = {
  id: string
  track: string
  module: string
  diff: string
  q: string
  opts: string[]
}

type ExamPayload = { id: string; title: string; time_limit: number; questions: ExamQuestion[] }

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
          <div className="text-[0.7rem] text-muted uppercase tracking-wider">
            {passed ? 'Best · mastered' : `Pass ≥ ${exam.pass_mark}%`}
          </div>
        </div>
      </div>
      <div className="px-4 pb-3">
        <Button variant={passed ? 'ghost' : 'primary'} onClick={onStart} className="w-full">
          {passed ? 'Retake for a better score' : exam.status === 'attempted' ? 'Retake exam' : 'Start exam'}
        </Button>
      </div>
    </Card>
  )
}

export function Exams() {
  const { ok, bad } = useToast()
  const { data, loading, error, reload } = useApi<{ exams: Exam[] }>('/api/exams')
  const [taking, setTaking] = useState<string | null>(null)
  const [examData, setExamData] = useState<ExamPayload | null>(null)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [startedAt, setStartedAt] = useState(0)
  const [now, setNow] = useState(() => Date.now())
  const [result, setResult] = useState<ExamResult | null>(null)
  const [busy, setBusy] = useState(false)

  // Refs keep the interval and the auto-submit effect from closing over stale
  // state: the clock used to tick against a frozen render and submit `{}`.
  const answersRef = useRef(answers)
  answersRef.current = answers
  const examRef = useRef(examData)
  examRef.current = examData
  const submittedRef = useRef(false)

  const exams = data?.exams ?? []
  const timeLeft =
    examData && startedAt ? Math.max(0, examData.time_limit - Math.floor((now - startedAt) / 1000)) : 0

  // Hooks first: these must run on every render, before any early return.
  useEffect(() => {
    if (!examData || !startedAt || result) return
    const id = window.setInterval(() => setNow(Date.now()), 500)
    return () => window.clearInterval(id)
  }, [examData, startedAt, result])

  useEffect(() => {
    if (!examData || !startedAt || result || timeLeft > 0) return
    void submitExam(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeLeft, examData, startedAt, result])

  async function submitExam(auto = false) {
    const exam = examRef.current
    if (!exam || submittedRef.current) return
    const payload = answersRef.current
    if (!auto && Object.keys(payload).length === 0) {
      bad('Nothing to submit.', 'Answer at least one question, or let the clock run.')
      return
    }
    submittedRef.current = true
    setBusy(true)
    try {
      const res = await api.post<ExamResult>(`/api/exams/${exam.id}/submit`, { answers: payload })
      setResult(res)
      if (res.passed) {
        void fireConfetti(window.innerWidth / 2, window.innerHeight / 3, 140)
        ok(
          'Exam mastered.',
          res.xp_gain > 0
            ? `+${res.xp_gain} XP · ${exam.title} now counts toward your Mastery Index.`
            : `Best score held. No extra XP for a retake of ${exam.title}.`,
        )
      } else {
        bad('Not yet.', `Scored ${res.pct}%. Re-study the weak topics and retake — unanswered questions count as wrong.`)
      }
      void reload(true)
    } catch (e) {
      submittedRef.current = false
      bad('Submit failed.', (e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function startExam(id: string) {
    const ex = exams.find((e) => e.id === id)
    if (!ex) return
    submittedRef.current = false
    setTaking(id)
    setAnswers({})
    answersRef.current = {}
    setResult(null)
    setExamData(null)
    setBusy(false)
    setStartedAt(0)
    try {
      const d = await api.get<ExamPayload>(`/api/exams/${id}`)
      setExamData(d)
      examRef.current = d
      setStartedAt(Date.now())
      setNow(Date.now())
    } catch (e) {
      bad('Could not load exam.', (e as Error).message)
      setTaking(null)
    }
  }

  function exitExam() {
    submittedRef.current = false
    setTaking(null)
    setExamData(null)
    setAnswers({})
    setResult(null)
    setStartedAt(0)
    setBusy(false)
  }

  if (loading && !data) return <Spinner label="Loading exams" />
  if (error) return <Empty>{error}</Empty>

  // exams list view
  if (!taking) {
    return (
      <div className="space-y-6">
        <PageHeader
          eyebrow="Formal mastery exams"
          title="Exams"
          subtitle="Timed, multi-module assessments drawn from the question bank. 80% to master. One sitting — the clock does not pause."
        />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {exams.map((ex) => (
            <ExamCard key={ex.id} exam={ex} onStart={() => void startExam(ex.id)} />
          ))}
        </div>
        <div className="rounded-xl border border-line bg-surface-2 p-5 text-[0.85rem] text-muted">
          <p className="font-semibold mb-1">How exams work</p>
          <ul className="space-y-1 list-disc list-inside text-muted">
            <li>Each exam draws real question-bank items from across its modules.</li>
            <li>The countdown runs while the exam is open and submits automatically at zero. Leaving the page abandons the attempt.</li>
            <li>Every question is graded — unanswered ones count as wrong. Score ≥ 80% to master.</li>
            <li>Exam results count toward your Mastery Index. Module gates are separate and still must be passed.</li>
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
        eyebrow={result ? 'Exam result' : 'Exam in progress'}
        title={examData.title}
        right={
          result ? (
            <ProgressRing
              pct={result.pct / 100}
              size={70}
              stroke={8}
              color={result.passed ? 'var(--ok)' : 'var(--bad)'}
              label={`${result.pct}%`}
              sub="score"
            />
          ) : (
            <div className="flex items-center gap-3">
              <ProgressRing pct={pctAnswered} size={70} stroke={8} label={fmtClock(timeLeft)} sub="remaining" />
              <Badge tone={timeLeft <= 60 ? 'bad' : 'neutral'}>{answered}/{examData.questions.length} answered</Badge>
            </div>
          )
        }
      />

      {!result && timeLeft <= 0 ? (
        <Card className="bg-bad-soft border-[color-mix(in_srgb,var(--bad)_30%,transparent)] p-5 text-center">
          <h3 className="font-display text-xl font-bold text-bad">Time is up.</h3>
          <p className="mt-1 text-muted">
            {busy ? 'Submitting the answers you had.' : 'The clock hit zero. Submit the attempt now so it is graded.'}
          </p>
          {!busy ? (
            <LoadingButton className="mt-4" onClick={() => void submitExam(true)}>
              Submit attempt
            </LoadingButton>
          ) : null}
        </Card>
      ) : null}

      {result ? (
        <Card className={cx('fade-up', result.passed ? 'border-[color-mix(in_srgb,var(--ok)_40%,transparent)]' : 'border-[color-mix(in_srgb,var(--bad)_40%,transparent)]')}>
          <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
            <div>
              <h3 className={cx('font-display text-[1.5rem] font-bold', result.passed ? 'text-ok' : 'text-bad')}>
                {result.passed ? 'Exam mastered.' : 'Not yet.'}
              </h3>
              <p className="mt-1 text-[0.9rem] text-muted">
                {result.score}/{result.total} correct · {result.pct}% · pass mark 80%
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="ghost" onClick={() => void startExam(examData.id)}>Retake</Button>
              <Button variant="secondary" onClick={exitExam}>Back to exams</Button>
            </div>
          </div>

          {result.passed ? (
            <div className="mb-4 rounded-xl border border-[color-mix(in_srgb,var(--ok)_30%,transparent)] bg-ok-soft px-4 py-3 text-[0.88rem] text-ok">
              {result.xp_gain > 0 ? `+${result.xp_gain} XP · ` : 'Best score held · '}
              {examData.title} counts toward your Mastery Index.
            </div>
          ) : null}

          {result.review && result.review.filter((r) => !r.ok).length > 0 ? (
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
          ) : null}

          {result.weak_topics.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {result.weak_topics.map((w) => (
                <Badge key={w} tone="bad">weak: {w}</Badge>
              ))}
            </div>
          ) : null}
        </Card>
      ) : null}

      {!result && timeLeft > 0 ? (
        <div className="space-y-5">
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
                      <span className="mono mt-0.5 text-[0.72rem] font-bold opacity-70">{['A', 'B', 'C', 'D'][oi]}</span>
                      <span>{opt}</span>
                    </button>
                  ))}
                </div>
              </Card>
            )
          })}
          <div className="sticky bottom-6 mt-8 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-line bg-surface/95 px-6 py-4 shadow-lg backdrop-blur">
            <span className="text-[0.86rem] text-muted">
              {answered} / {examData.questions.length} answered · {fmtClock(timeLeft)} left
            </span>
            <LoadingButton
              variant="primary"
              loading={busy}
              onClick={() => void submitExam(false)}
              disabled={answered === 0}
            >
              {busy ? 'Submitting…' : 'Submit exam'}
            </LoadingButton>
          </div>
        </div>
      ) : null}
    </div>
  )
}
