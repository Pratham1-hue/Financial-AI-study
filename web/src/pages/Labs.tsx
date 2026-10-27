import { useEffect, useState } from 'react'

import { QuoteLine } from '../components/Quote'
import { StaggerGroup } from '../components/motion'
import { Badge, Bar, Button, Card, Empty, PageHeader, SectionTitle, Spinner, Tabs, cx, inputCls } from '../components/ui'
import { api } from '../lib/api'
import { fmtMoney, fmtPct } from '../lib/format'
import { useApi } from '../lib/hooks'

type Tab = 'sql' | 'credit' | 'valuation'

interface SqlTask {
  id: string
  level: string
  prompt: string
  cols: string
  hint: string
}

interface SqlResult {
  ok: boolean
  error: string | null
  preview?: { columns: string[]; rows: (string | number | null)[][] }
  rows?: number
  cols?: number
  expected_rows?: number
  expected_cols?: number
  hint?: string
  reference?: string | null
  recorded?: boolean
}

function DataTable({ preview }: { preview: { columns: string[]; rows: (string | number | null)[][] } }) {
  return (
    <div className="max-h-72 overflow-auto rounded-xl border border-line">
      <table className="w-full text-left text-[0.8rem]">
        <thead className="sticky top-0 bg-surface-2 text-[0.64rem] tracking-[0.1em] text-muted uppercase">
          <tr>
            {preview.columns.map((c) => (
              <th key={c} className="px-3 py-2 font-semibold whitespace-nowrap">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {preview.rows.map((row, i) => (
            <tr key={i} className="border-t border-line">
              {row.map((cell, j) => (
                <td key={j} className="mono px-3 py-1.5 whitespace-nowrap text-ink-soft">
                  {cell === null ? <span className="text-muted">NULL</span> : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/* ----------------------------------------------------------------------- SQL */
function SqlLab({ tasks, schema }: { tasks: SqlTask[]; schema: string }) {
  const [taskId, setTaskId] = useState(tasks[0]?.id ?? '')
  const [sql, setSql] = useState('')
  const [attempts, setAttempts] = useState<Record<string, number>>({})
  const [result, setResult] = useState<SqlResult | null>(null)
  const [preview, setPreview] = useState<SqlResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const task = tasks.find((t) => t.id === taskId) ?? tasks[0]
  const { data: log, reload: reloadLog } = useApi<{ today_attempts: number; today_correct: number; sql_solved: string[]; recent: { lab: string; ok: boolean; detail: string; date: string }[] }>('/api/labs/log')

  useEffect(() => {
    setSql('')
    setResult(null)
    setPreview(null)
    setError(null)
  }, [taskId])

  async function run() {
    setBusy(true)
    setError(null)
    try {
      const res = await api.post<SqlResult>('/api/labs/sql/run', { sql })
      setPreview(res)
      setResult(null)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function check() {
    setBusy(true)
    setError(null)
    const attempt = (attempts[taskId] ?? 0) + 1
    setAttempts((a) => ({ ...a, [taskId]: attempt }))
    try {
      const res = await api.post<SqlResult>('/api/labs/sql/check', { task_id: taskId, sql, attempt })
      setResult(res)
      setPreview(null)
      void reloadLog(true)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
      <div className="space-y-5">
        <Card>
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="gold">{task?.level}</Badge>
            <span className="mono text-[0.72rem] text-muted">{task?.cols}</span>
            {log?.sql_solved.includes(taskId) ? <Badge tone="ok">solved</Badge> : null}
            {attempts[taskId] ? <Badge tone="neutral">attempt {attempts[taskId]}</Badge> : null}
            <select className={cx(inputCls, 'ml-auto w-auto')} value={taskId} onChange={(e) => setTaskId(e.target.value)}>
              {tasks.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.id} · {t.level}
                </option>
              ))}
            </select>
          </div>
          <p className="mt-3 text-[0.98rem] font-medium text-ink">{task?.prompt}</p>

          <textarea
            className={cx(inputCls, 'mono mt-3.5 min-h-[160px] resize-y text-[0.85rem]')}
            placeholder={'SELECT ...\nFROM ...'}
            value={sql}
            spellCheck={false}
            onChange={(e) => setSql(e.target.value)}
          />

          <div className="mt-3 flex flex-wrap items-center gap-2.5">
            <Button onClick={() => void run()} disabled={busy || !sql.trim()}>
              Run
            </Button>
            <Button variant="primary" onClick={() => void check()} disabled={busy || !sql.trim()}>
              Check answer
            </Button>
            <button onClick={() => setSql('')} className="text-[0.78rem] text-muted underline">
              clear
            </button>
            <span className="ml-auto text-[0.75rem] text-muted">Read-only. One statement. SELECT or WITH.</span>
          </div>

          {error ? <div className="mt-3 rounded-xl border border-[color-mix(in_srgb,var(--bad)_30%,transparent)] bg-bad-soft px-3.5 py-2.5 text-[0.83rem] text-bad">{error}</div> : null}

          {result ? (
            <div className={cx('mt-4 rounded-xl border px-4 py-3', result.ok ? 'border-[color-mix(in_srgb,var(--ok)_35%,transparent)] bg-ok-soft' : 'border-[color-mix(in_srgb,var(--warn)_30%,transparent)] bg-warn-soft')}>
              <div className="flex flex-wrap items-center gap-2">
                <span className={cx('font-display text-[1.05rem] font-bold', result.ok ? 'text-ok' : 'text-warn')}>
                  {result.ok ? 'Correct.' : 'Not yet.'}
                </span>
                {result.ok ? <Badge tone="ok">+15 XP{result.recorded ? '' : ' (already solved)'}</Badge> : null}
                {!result.ok ? (
                  <span className="mono text-[0.76rem] text-muted">
                    got {result.rows}×{result.cols} · want {result.expected_rows}×{result.expected_cols}
                  </span>
                ) : null}
              </div>
              {result.error ? <p className="mt-1.5 text-[0.83rem] text-ink-soft">{result.error}</p> : null}
              {!result.ok && result.hint ? <p className="mt-1.5 text-[0.83rem] text-muted">Hint: {result.hint}</p> : null}
              {result.reference ? (
                <pre className="mono mt-3 overflow-auto rounded-lg bg-surface px-3 py-2.5 text-[0.78rem] text-ink-soft">{result.reference}</pre>
              ) : null}
            </div>
          ) : null}

          {preview?.ok ? (
            <div className="mt-4">
              <div className="mb-2 text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">Preview · {preview.preview?.rows.length} rows</div>
              {preview.preview ? <DataTable preview={preview.preview} /> : null}
            </div>
          ) : null}
          {preview && !preview.ok ? (
            <div className="mt-3 rounded-xl border border-[color-mix(in_srgb,var(--bad)_30%,transparent)] bg-bad-soft px-3.5 py-2.5 text-[0.83rem] text-bad">{preview.error}</div>
          ) : null}
        </Card>
      </div>

      <div className="space-y-5">
        <Card>
          <SectionTitle>Schema</SectionTitle>
          <pre className="mono overflow-auto rounded-xl bg-surface-2 px-3.5 py-3 text-[0.76rem] leading-relaxed text-ink-soft">{schema}</pre>
        </Card>

        <Card>
          <SectionTitle hint={`${log?.sql_solved.length ?? 0}/${tasks.length}`}>Progress</SectionTitle>
          <div className="mb-3">
            <Bar value={log?.sql_solved.length ?? 0} max={tasks.length} label={`Today ${log?.today_correct ?? 0}/${log?.today_attempts ?? 0} correct`} />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {tasks.map((t) => (
              <span
                key={t.id}
                className={cx(
                  'mono rounded-lg border px-2 py-1 text-[0.72rem] font-semibold',
                  log?.sql_solved.includes(t.id) ? 'border-transparent bg-ok-soft text-ok' : 'border-line text-muted',
                )}
              >
                {t.id}
              </span>
            ))}
          </div>
        </Card>

        <Card>
          <QuoteLine text="The analyst who cannot query the data is at the mercy of the analyst who can." author="Desk proverb" />
        </Card>
      </div>
    </div>
  )
}

/* -------------------------------------------------------------------- credit */
interface CreditMetrics {
  error?: string
  auc: number
  accuracy: number
  precision: number
  recall: number
  f1: number
  base: number
  n_test: number
  confusion: number[][]
  missed_defaults: number
  total_defaults: number
  weights: { name: string; value: number }[]
  usable: boolean
  features: string[]
  model: string
  threshold: number
  xp_gain?: number
}

function CreditLab({ features, models, usableAuc }: { features: string[]; models: string[]; usableAuc: number }) {
  const [picked, setPicked] = useState<string[]>(features.filter((f) => f !== 'income_k'))
  const [model, setModel] = useState(models[0])
  const [threshold, setThreshold] = useState(0.3)
  const [metrics, setMetrics] = useState<CreditMetrics | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [banked, setBanked] = useState<number | null>(null)

  async function train(bank = false) {
    setBusy(true)
    setError(null)
    try {
      const res = await api.post<CreditMetrics>(bank ? '/api/labs/credit/bank' : '/api/labs/credit', {
        features: picked,
        model,
        threshold,
      })
      setMetrics(res)
      if (bank) setBanked(res.xp_gain ?? 0)
      else setBanked(null)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
      <div className="space-y-5">
        <Card>
          <SectionTitle>Build the model</SectionTitle>
          <div className="space-y-4">
            <div>
              <div className="mb-2 text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">Features</div>
              <div className="space-y-1.5">
                {features.map((f) => (
                  <label key={f} className="flex items-center gap-2.5 text-[0.84rem] text-ink-soft">
                    <input
                      type="checkbox"
                      checked={picked.includes(f)}
                      onChange={(e) => setPicked((p) => (e.target.checked ? [...p, f] : p.filter((x) => x !== f)))}
                    />
                    <span className="mono">{f}</span>
                  </label>
                ))}
              </div>
            </div>

            <label className="block">
              <span className="mb-1 block text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">Model</span>
              <select className={inputCls} value={model} onChange={(e) => setModel(e.target.value)}>
                {models.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-1 flex justify-between text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">
                <span>Approval threshold</span>
                <span className="mono text-gold">{threshold.toFixed(2)}</span>
              </span>
              <input type="range" min={0.05} max={0.8} step={0.01} value={threshold} onChange={(e) => setThreshold(Number(e.target.value))} className="w-full accent-[var(--gold)]" />
              <span className="mt-1 block text-[0.74rem] text-muted">Lower = stricter. Deny anyone above this default probability.</span>
            </label>

            <div className="flex gap-2">
              <Button variant="primary" size="lg" className="flex-1" disabled={busy || picked.length === 0} onClick={() => void train(false)}>
                {busy ? 'Training…' : 'Train'}
              </Button>
              <Button size="lg" disabled={busy || !metrics} onClick={() => void train(true)}>
                Bank result
              </Button>
            </div>
            {banked !== null ? (
              <div className="text-[0.78rem] text-ok">
                {banked > 0
                  ? `+${banked} XP banked. An AUC above ${usableAuc.toFixed(2)} is desk-usable.`
                  : `Recorded. This model already paid out its XP - retraining is practice.`}
              </div>
            ) : null}
          </div>
        </Card>
        <Card>
          <QuoteLine text="Risk comes from not knowing what you are doing." author="Warren Buffett" />
        </Card>
      </div>

      <div className="space-y-5">
        {error ? <Empty>{error}</Empty> : null}
        {!metrics ? (
          <Empty>Pick features, hit Train, and watch what actually moves default risk.</Empty>
        ) : (
          <>
            <Card>
              <div className="flex flex-wrap items-center gap-3">
                <div>
                  <div className="text-[0.66rem] font-semibold tracking-[0.14em] text-muted uppercase">ROC AUC</div>
                  <div className={cx('mono text-[1.9rem] leading-none font-bold', metrics.usable ? 'text-ok' : 'text-bad')}>{metrics.auc.toFixed(3)}</div>
                </div>
                <Badge tone={metrics.usable ? 'ok' : 'bad'}>{metrics.usable ? 'desk-usable' : 'below the bar'}</Badge>
                <div className="ml-auto grid grid-cols-3 gap-4">
                  {[
                    ['Precision', fmtPct(metrics.precision, 1)],
                    ['Recall', fmtPct(metrics.recall, 1)],
                    ['F1', fmtPct(metrics.f1, 1)],
                  ].map(([k, v]) => (
                    <div key={k}>
                      <div className="text-[0.64rem] font-semibold tracking-[0.12em] text-muted uppercase">{k}</div>
                      <div className="mono text-[0.95rem] font-bold text-ink">{v}</div>
                    </div>
                  ))}
                </div>
              </div>
              <p className="mt-3 text-[0.85rem] text-muted">
                Naive accuracy if you always predicted the majority class: {fmtPct(metrics.base, 1)}. Accuracy alone is a trap;
                AUC is what separates a model from a coin toss.
              </p>
            </Card>

            <div className="grid gap-5 sm:grid-cols-2">
              <Card>
                <SectionTitle hint="test set">Confusion matrix</SectionTitle>
                <div className="grid grid-cols-2 gap-2.5">
                  {[
                    ['True negative', metrics.confusion[0][0], 'ok'],
                    ['False positive', metrics.confusion[0][1], 'warn'],
                    ['False negative', metrics.confusion[1][0], 'bad'],
                    ['True positive', metrics.confusion[1][1], 'ok'],
                  ].map(([label, val, tone]) => (
                    <div key={label as string} className="rounded-xl border border-line bg-surface-2 p-3.5">
                      <div className="text-[0.64rem] font-semibold tracking-[0.12em] text-muted uppercase">{label}</div>
                      <div className={cx('mono mt-1 text-[1.2rem] font-bold', tone === 'ok' ? 'text-ok' : tone === 'warn' ? 'text-warn' : 'text-bad')}>
                        {val as number}
                      </div>
                    </div>
                  ))}
                </div>
                <p className="mt-3 text-[0.83rem] text-muted">
                  Missed {metrics.missed_defaults} of {metrics.total_defaults} defaults at a {metrics.threshold.toFixed(2)} cut-off.
                </p>
              </Card>

              <Card>
                <SectionTitle hint={metrics.model}>What drives default</SectionTitle>
                <div className="space-y-2.5">
                  {metrics.weights.map((w) => {
                    const max = Math.max(...metrics.weights.map((x) => Math.abs(x.value))) || 1
                    return (
                      <div key={w.name}>
                        <div className="mb-1 flex justify-between text-[0.78rem]">
                          <span className="mono text-ink-soft">{w.name}</span>
                        </div>
                        <div className="h-2 w-full overflow-hidden rounded-full bg-bg-soft">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${(Math.abs(w.value) / max) * 100}%`,
                              background: w.value >= 0 ? 'var(--bad)' : 'var(--ok)',
                            }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
                <p className="mt-3 text-[0.78rem] text-muted">Red increases default odds, green lowers them.</p>
              </Card>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

/* ----------------------------------------------------------------- valuation */
interface ValCase {
  seed: number
  wacc: number
  g: number
  gt: number
  fcf0: number
  shares: number
  net_debt: number
}

interface ValResult {
  passed: number
  of: number
  correct: boolean
  checks: { label: string; you: number; answer: number; ok: boolean }[]
  workings: { fcfs: number[]; pv: number; tv: number; pv_tv: number; ev: number; equity: number; per_share: number }
  case: ValCase
  xp_gain?: number
}

function ValuationLab() {
  const [c, setC] = useState<ValCase | null>(null)
  const [ev, setEv] = useState('')
  const [equity, setEquity] = useState('')
  const [perShare, setPerShare] = useState('')
  const [result, setResult] = useState<ValResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function newCase() {
    setBusy(true)
    setResult(null)
    setEv('')
    setEquity('')
    setPerShare('')
    try {
      const res = await api.post<{ case: ValCase }>('/api/labs/valuation', {})
      setC(res.case)
      setError(null)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    void newCase()
  }, [])

  async function submit() {
    if (!c) return
    setBusy(true)
    setError(null)
    try {
      const res = await api.post<ValResult>('/api/labs/valuation', {
        seed: c.seed,
        ev: Number(ev),
        equity: Number(equity),
        per_share: Number(perShare),
      })
      setResult(res)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  if (!c) return <Spinner label="Building a case" />

  return (
    <div className="grid gap-5 lg:grid-cols-[340px_1fr]">
      <div className="space-y-5">
        <Card>
          <SectionTitle hint={`seed ${c.seed}`}>The case</SectionTitle>
          <dl className="space-y-2 text-[0.86rem]">
            {[
              ['WACC', fmtPct(c.wacc, 2)],
              ['Stage-1 growth (5y)', fmtPct(c.g, 2)],
              ['Terminal growth', fmtPct(c.gt, 2)],
              ['FCF₀', `$${fmtMoney(c.fcf0, 1)}m`],
              ['Net debt', `$${fmtMoney(c.net_debt, 1)}m`],
              ['Shares outstanding', `${fmtMoney(c.shares, 1)}m`],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between border-b border-line pb-2">
                <dt className="text-muted">{k}</dt>
                <dd className="mono font-semibold text-ink">{v}</dd>
              </div>
            ))}
          </dl>
          <Button className="mt-4 w-full" onClick={() => void newCase()} disabled={busy}>
            New case
          </Button>
        </Card>

        <Card>
          <SectionTitle>Method</SectionTitle>
          <ol className="space-y-1.5 text-[0.82rem] text-muted">
            <li>1. Project FCF for years 1–5: FCF₀ × (1+g)ᵗ.</li>
            <li>2. Discount each at WACCᵗ and sum → PV of stage 1.</li>
            <li>3. Terminal value: FCF₅ × (1+gₜ) / (WACC − gₜ).</li>
            <li>4. Discount TV back 5 years → EV = PV + PV(TV).</li>
            <li>5. Equity = EV − net debt. Per share = equity ÷ shares.</li>
          </ol>
        </Card>
      </div>

      <div className="space-y-5">
        {error ? <Empty>{error}</Empty> : null}
        <Card>
          <SectionTitle hint="to the nearest dollar-ish">Your DCF</SectionTitle>
          <div className="grid gap-3.5 sm:grid-cols-3">
            {[
              ['Enterprise value ($m)', ev, setEv],
              ['Equity value ($m)', equity, setEquity],
              ['Value per share ($)', perShare, setPerShare],
            ].map(([label, val, set]) => (
              <label key={label as string} className="block">
                <span className="mb-1 block text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">{label as string}</span>
                <input
                  className={cx(inputCls, 'mono')}
                  inputMode="decimal"
                  value={val as string}
                  onChange={(e) => (set as (v: string) => void)(e.target.value)}
                  placeholder="0"
                />
              </label>
            ))}
          </div>
          <Button variant="primary" size="lg" className="mt-4" disabled={busy || !ev || !equity || !perShare} onClick={() => void submit()}>
            {busy ? 'Checking…' : 'Check the DCF'}
          </Button>
        </Card>

        {result ? (
          <Card className={cx('fade-up', result.correct ? 'border-[color-mix(in_srgb,var(--ok)_40%,transparent)]' : '')}>
            <div className="flex items-center gap-3">
              <h3 className="font-display text-[1.3rem] font-bold text-ink">
                {result.passed} / {result.of} correct
              </h3>
              {result.correct ? (
                <Badge tone="ok">
                  {result.xp_gain ? `+${result.xp_gain} XP · clean sheet` : 'Clean sheet · practice'}
                </Badge>
              ) : (
                <Badge tone="warn">keep going</Badge>
              )}
            </div>
            <StaggerGroup className="mt-4 space-y-2">
              {result.checks.map((c2) => (
                <div key={c2.label} className={cx('rounded-xl border px-3.5 py-2.5', c2.ok ? 'border-[color-mix(in_srgb,var(--ok)_35%,transparent)] bg-ok-soft' : 'border-[color-mix(in_srgb,var(--bad)_35%,transparent)] bg-bad-soft')}>
                  <div className="flex items-center justify-between text-[0.86rem]">
                    <span className={cx('font-semibold', c2.ok ? 'text-ok' : 'text-bad')}>{c2.label}</span>
                    <span className="mono text-muted">
                      you {fmtMoney(c2.you, 2)} · answer {fmtMoney(c2.answer, 2)}
                    </span>
                  </div>
                </div>
              ))}
            </StaggerGroup>

            <div className="mt-5">
              <div className="mb-2 text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">Workings</div>
              <div className="grid gap-2 text-[0.82rem] sm:grid-cols-2">
                <div className="rounded-xl border border-line bg-surface-2 px-3.5 py-2.5">
                  <div className="text-[0.64rem] tracking-[0.12em] text-muted uppercase">Projected FCFs (1–5)</div>
                  <div className="mono mt-1 text-ink-soft">{result.workings.fcfs.map((f) => fmtMoney(f, 1)).join(' · ')}</div>
                </div>
                <div className="rounded-xl border border-line bg-surface-2 px-3.5 py-2.5">
                  <div className="text-[0.64rem] tracking-[0.12em] text-muted uppercase">PV stage 1 / PV terminal</div>
                  <div className="mono mt-1 text-ink-soft">
                    {fmtMoney(result.workings.pv, 1)} / {fmtMoney(result.workings.pv_tv, 1)}
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ) : null}
      </div>
    </div>
  )
}

/* ---------------------------------------------------------------------- page */
export function Labs() {
  const [tab, setTab] = useState<Tab>('sql')
  const { data, loading, error } = useApi<{
    schema: string
    sql: SqlTask[]
    credit: { features: string[]; models: string[]; n_borrowers: number; usable_auc: number }
    valuation: { time_limit_secs: number }
  }>('/api/labs')

  if (loading && !data) return <Spinner label="Loading the labs" />
  if (error) return <Empty>{error}</Empty>
  if (!data) return <Empty>No labs available.</Empty>

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Build it"
        title="Labs"
        subtitle="Three stations: query real tables in SQL, train a credit model, and value a company from its cash flows. Everything is auto-graded."
      />

      <Tabs
        tabs={[
          { id: 'sql', label: 'SQL' },
          { id: 'credit', label: 'Credit ML' },
          { id: 'valuation', label: 'Valuation' },
        ]}
        value={tab}
        onChange={setTab}
      />

      {tab === 'sql' ? <SqlLab tasks={data.sql} schema={data.schema} /> : null}
      {tab === 'credit' ? <CreditLab features={data.credit.features} models={data.credit.models} usableAuc={data.credit.usable_auc} /> : null}
      {tab === 'valuation' ? <ValuationLab /> : null}
    </div>
  )
}
