import { useCallback, useEffect, useRef, useState } from 'react'

import { LineChart } from '../components/LineChart'
import { QuoteLine } from '../components/Quote'
import { Badge, Bar, Button, Card, Empty, PageHeader, SectionTitle, Spinner, cx, inputCls } from '../components/ui'
import { api, type DeskGrade, type DeskRound } from '../lib/api'
import { fmtMoney, fmtPct } from '../lib/format'
import { usePoll } from '../lib/hooks'

interface HistoryRow {
  date: string
  score: number
  ret: number
  bench: number
  dd: number
  trades: number
  breaches: number
  equity: number
  seed: number
}

export function Desk() {
  const [rid, setRid] = useState<string | null>(null)
  const [round, setRound] = useState<DeskRound | null>(null)
  const [sym, setSym] = useState('NVX')
  const [qty, setQty] = useState(100)
  const [message, setMessage] = useState<{ text: string; ok: boolean } | null>(null)
  const [result, setResult] = useState<DeskGrade | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const creating = useRef(false)

  const startRound = useCallback(async () => {
    if (creating.current) return
    creating.current = true
    setBusy(true)
    setResult(null)
    setMessage(null)
    try {
      const r = await api.post<DeskRound>('/api/desk/new')
      setRid(r.round_id)
      setRound(r)
      setError(null)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
      creating.current = false
    }
  }, [])

  useEffect(() => {
    void startRound()
  }, [startRound])

  const refresh = useCallback(async () => {
    if (!rid) return
    try {
      setRound(await api.get<DeskRound>(`/api/desk/${rid}?sym=${sym}`))
    } catch (e) {
      setError((e as Error).message)
    }
  }, [rid, sym])

  usePoll(refresh, 1500, !!rid && !result)

  useEffect(() => {
    void refresh()
  }, [refresh])

  async function trade(direction: 1 | -1) {
    if (!rid || !round || round.done) return
    setBusy(true)
    try {
      const res = await api.post<DeskRound & { ok: boolean; message: string }>(`/api/desk/${rid}/trade`, {
        sym,
        qty: qty * direction,
      })
      setMessage({ text: res.message, ok: res.ok })
      setRound({ ...res, book: res.book ?? round.book })
    } catch (e) {
      setMessage({ text: (e as Error).message, ok: false })
    } finally {
      setBusy(false)
    }
  }

  async function grade() {
    if (!rid) return
    setBusy(true)
    try {
      const res = await api.post<DeskGrade>(`/api/desk/${rid}/grade`)
      setResult(res)
      setMessage(null)
      void reloadHistory()
    } catch (e) {
      setMessage({ text: (e as Error).message, ok: false })
    } finally {
      setBusy(false)
    }
  }

  const { data: history, reload: reloadHistory } = useApiHistory()

  if (error && !round) return <Empty>{error}</Empty>
  if (!round) return <Spinner label="Opening the desk" />

  const greeks = round.gross
  const breaches = round.breaches
  const pnl = round.equity - round.limits.start_cash
  const counts: Record<string, number> = {}
  for (const t of round.trades) counts[t.sym] = (counts[t.sym] ?? 0) + 1

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="The Desk"
        title="Trade the tape"
        subtitle="A three-minute synthetic market. Make decisions, size them sensibly, and let the grade judge your process — not your luck."
        right={
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={round.done ? 'neutral' : 'ok'}>{round.done ? 'round over' : `live · ${round.remaining}s`}</Badge>
            {breaches > 0 ? <Badge tone="bad">{breaches} breaches</Badge> : null}
            <Button onClick={() => void startRound()} disabled={busy}>
              New round
            </Button>
          </div>
        }
      />

      <Card>
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
          <div className="text-[0.85rem] text-muted">
            <span className="font-semibold text-ink">{round.headline}</span> · seed {round.seed}
          </div>
          <div className="mono text-[0.8rem] text-muted">trades {round.trades.length}/{round.limits.max_trades}</div>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-[0.72rem] font-semibold tracking-[0.14em] text-muted uppercase">Round clock</span>
            <div className="h-1.5 w-40 overflow-hidden rounded-full bg-bg-soft">
              <div
                className="h-full rounded-full bg-gold transition-[width] duration-1000"
                style={{ width: `${(round.remaining / (round.duration || 1)) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </Card>

      {result ? (
        <Card className={cx('fade-up', result.score >= 60 ? 'border-[color-mix(in_srgb,var(--ok)_40%,transparent)]' : 'border-[color-mix(in_srgb,var(--bad)_40%,transparent)]')}>
          <div className="flex flex-wrap items-start gap-6">
            <div className="text-center">
              <div className="mono text-[2.6rem] leading-none font-bold text-ink">{result.score}</div>
              <div className="mt-1 text-[0.7rem] font-semibold tracking-[0.16em] text-muted uppercase">score / 100</div>
            </div>
            <div className="grid flex-1 grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                ['Return', fmtPct(result.ret)],
                ['Benchmark', fmtPct(result.bench)],
                ['Alpha', fmtPct(result.ret - result.bench)],
                ['Max DD', fmtPct(result.dd)],
              ].map(([k, v]) => (
                <div key={k}>
                  <div className="text-[0.66rem] font-semibold tracking-[0.14em] text-muted uppercase">{k}</div>
                  <div className="mono mt-1 text-[1.05rem] font-bold text-ink">{v}</div>
                </div>
              ))}
            </div>
          </div>
          <ul className="mt-4 space-y-1.5">
            {result.notes.map((n, i) => (
              <li key={i} className="flex gap-2 text-[0.86rem] text-ink-soft">
                <span className="text-gold">▸</span>
                {n}
              </li>
            ))}
          </ul>
        </Card>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-[1fr_340px]">
        <div className="space-y-5">
          <Card padded={false}>
            <div className="border-b border-line px-5 py-3.5">
              <h2 className="text-[1rem] font-semibold text-ink">Market</h2>
            </div>
            <table className="w-full text-left text-[0.86rem]">
              <thead className="bg-surface-2 text-[0.66rem] tracking-[0.12em] text-muted uppercase">
                <tr>
                  <th className="px-5 py-2.5 font-semibold">Instrument</th>
                  <th className="px-3 py-2.5 font-semibold">Bid</th>
                  <th className="px-3 py-2.5 font-semibold">Mid</th>
                  <th className="px-3 py-2.5 font-semibold">Ask</th>
                  <th className="px-3 py-2.5 font-semibold">Position</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(round.quotes).map(([s, q]) => {
                  const pos = round.positions.find((p) => p.sym === s)
                  return (
                    <tr
                      key={s}
                      onClick={() => setSym(s)}
                      className={cx('cursor-pointer border-t border-line transition', sym === s ? 'bg-gold-soft' : 'hover:bg-surface-2')}
                    >
                      <td className="px-5 py-2.5">
                        <div className="font-semibold text-ink">{s}</div>
                        <div className="text-[0.72rem] text-muted">{q.name}</div>
                      </td>
                      <td className="mono px-3 py-2.5 text-bad">{fmtMoney(q.bid, 2)}</td>
                      <td className="mono px-3 py-2.5 font-semibold text-ink">{fmtMoney(q.mid, 2)}</td>
                      <td className="mono px-3 py-2.5 text-ok">{fmtMoney(q.ask, 2)}</td>
                      <td className="mono px-3 py-2.5 text-ink-soft">
                        {pos ? (
                          <span className={pos.pnl >= 0 ? 'text-ok' : 'text-bad'}>
                            {pos.qty > 0 ? '+' : ''}
                            {pos.qty} ({pos.pnl >= 0 ? '+' : ''}
                            {fmtMoney(pos.pnl, 0)})
                          </span>
                        ) : (
                          <span className="text-muted">—</span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </Card>

          <Card>
            <SectionTitle hint="your equity vs the S&P">Performance</SectionTitle>
            <div className="mb-3 flex flex-wrap gap-6">
              <div>
                <div className="text-[0.66rem] font-semibold tracking-[0.14em] text-muted uppercase">Equity</div>
                <div className={cx('mono text-[1.3rem] font-bold', pnl >= 0 ? 'text-ok' : 'text-bad')}>{fmtMoney(round.equity, 0)}</div>
              </div>
              <div>
                <div className="text-[0.66rem] font-semibold tracking-[0.14em] text-muted uppercase">vs bench</div>
                <div className="mono text-[1.3rem] font-bold text-ink">{fmtMoney(round.bench, 0)}</div>
              </div>
              <div>
                <div className="text-[0.66rem] font-semibold tracking-[0.14em] text-muted uppercase">Realized</div>
                <div className={cx('mono text-[1.3rem] font-bold', round.realized >= 0 ? 'text-ok' : 'text-bad')}>
                  {fmtMoney(round.realized, 0)}
                </div>
              </div>
              <div>
                <div className="text-[0.66rem] font-semibold tracking-[0.14em] text-muted uppercase">Gross</div>
                <div className="mono text-[1.3rem] font-bold text-ink">{Math.round(greeks * 100)}%</div>
              </div>
            </div>
            <LineChart series={round.equity_curve} compare={round.bench_curve} height={130} />
          </Card>

          <div className="grid gap-5 sm:grid-cols-2">
            <Card>
              <SectionTitle hint={`${round.positions.length} open`}>Book</SectionTitle>
              {round.positions.length === 0 ? (
                <Empty>Flat. Nothing at risk.</Empty>
              ) : (
                <div className="space-y-2">
                  {round.positions.map((p) => (
                    <div key={p.sym} className="rounded-xl border border-line bg-surface-2 px-3.5 py-2.5">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-ink">{p.sym}</span>
                        <span className={cx('mono font-bold', p.pnl >= 0 ? 'text-ok' : 'text-bad')}>
                          {p.pnl >= 0 ? '+' : ''}
                          {fmtMoney(p.pnl, 0)}
                        </span>
                      </div>
                      <div className="mono text-[0.75rem] text-muted">
                        {p.qty} @ avg {fmtMoney(p.avg, 2)} · now {fmtMoney(p.px, 2)} · {fmtMoney(p.value, 0)} notional
                      </div>
                    </div>
                  ))}
                  <div className="mono flex justify-between px-1 pt-1 text-[0.78rem] text-muted">
                    <span>cash {fmtMoney(round.cash, 0)}</span>
                    <span>gross limit {round.limits.max_gross * 100}%</span>
                  </div>
                </div>
              )}
            </Card>

            <Card>
              <SectionTitle>Time &amp; sales</SectionTitle>
              <div className="space-y-1.5">
                {round.tape.map((t, i) => (
                  <div key={i} className="mono flex items-center justify-between text-[0.78rem]">
                    <span className="text-muted">t+{t.t}</span>
                    <span className="font-semibold text-ink">{t.sym}</span>
                    <span className={t.side === 'BUY' ? 'text-ok' : 'text-bad'}>{t.side}</span>
                    <span className="text-muted">{Math.abs(t.qty)} @ {fmtMoney(t.px, 2)}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>

        <div className="space-y-5">
          <Card>
            <SectionTitle hint={round.quotes[sym]?.name}>Order ticket · {sym}</SectionTitle>
            <label className="block">
              <span className="mb-1 block text-[0.68rem] font-semibold tracking-[0.14em] text-muted uppercase">Size</span>
              <input
                type="number"
                min={1}
                className={inputCls}
                value={qty}
                onChange={(e) => setQty(Math.max(1, Number(e.target.value) || 0))}
              />
            </label>
            <div className="mt-3 grid grid-cols-2 gap-2.5">
              <Button variant="primary" size="lg" disabled={busy || round.done} onClick={() => void trade(1)}>
                Buy
              </Button>
              <Button variant="danger" size="lg" disabled={busy || round.done} onClick={() => void trade(-1)}>
                Sell
              </Button>
            </div>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {[10, 50, 100, 250].map((n) => (
                <button key={n} onClick={() => setQty(n)} className="rounded-lg border border-line px-2.5 py-1 text-[0.75rem] text-muted transition hover:border-gold hover:text-gold">
                  {n}
                </button>
              ))}
            </div>

            {message ? (
              <div
                className={cx(
                  'mt-3.5 rounded-xl border px-3.5 py-2.5 text-[0.83rem]',
                  message.ok ? 'border-[color-mix(in_srgb,var(--ok)_30%,transparent)] bg-ok-soft text-ok' : 'border-[color-mix(in_srgb,var(--bad)_30%,transparent)] bg-bad-soft text-bad',
                )}
              >
                {message.text}
              </div>
            ) : null}

            {round.book ? (
              <div className="mt-4 grid grid-cols-2 gap-3">
                <div>
                  <div className="mb-1 text-[0.66rem] font-semibold tracking-[0.14em] text-ok uppercase">Bids</div>
                  {round.book.bids.map((l, i) => (
                    <div key={i} className="mono flex justify-between text-[0.76rem] text-muted">
                      <span className="text-ok">{fmtMoney(l.px, 2)}</span>
                      <span>{l.size}</span>
                    </div>
                  ))}
                </div>
                <div>
                  <div className="mb-1 text-[0.66rem] font-semibold tracking-[0.14em] text-bad uppercase">Asks</div>
                  {round.book.asks.map((l, i) => (
                    <div key={i} className="mono flex justify-between text-[0.76rem] text-muted">
                      <span className="text-bad">{fmtMoney(l.px, 2)}</span>
                      <span>{l.size}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            <div className="mt-4">
              {round.done && !result ? (
                <Button variant="primary" size="lg" className="w-full" disabled={busy} onClick={() => void grade()}>
                  {busy ? 'Grading…' : 'Close the book & grade'}
                </Button>
              ) : null}
              {!round.done ? (
                <div className="text-center text-[0.75rem] text-muted">Sizing rules: max {round.limits.max_gross * 100}% gross, {round.limits.max_name * 100}% single name, {round.limits.max_trades} trades.</div>
              ) : null}
            </div>
          </Card>

          <Card>
            <SectionTitle hint="trade distribution">Activity</SectionTitle>
            {Object.keys(counts).length === 0 ? (
              <Empty>No trades yet.</Empty>
            ) : (
              <div className="space-y-2.5">
                {Object.entries(counts).map(([s, n]) => (
                  <div key={s}>
                    <div className="mb-1 flex justify-between text-[0.8rem]">
                      <span className="text-ink-soft">{s}</span>
                      <span className="mono text-muted">{n}</span>
                    </div>
                    <Bar value={n} max={Math.max(...Object.values(counts))} tone={s === sym ? 'gold' : 'navy'} />
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card>
            <SectionTitle hint={history ? `${history.total} rounds` : ''}>Recent grades</SectionTitle>
            {!history || history.rounds.length === 0 ? (
              <Empty>No graded rounds yet.</Empty>
            ) : (
              <div className="space-y-2">
                {history.rounds.map((h, i) => (
                  <div key={i} className="flex items-center justify-between rounded-lg border border-line bg-surface-2 px-3 py-2 text-[0.8rem]">
                    <span className="mono text-muted">{h.date.slice(5)}</span>
                    <span className={cx('mono font-bold', h.ret >= 0 ? 'text-ok' : 'text-bad')}>{fmtPct(h.ret)}</span>
                    <span className="mono font-bold text-gold">{h.score}</span>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card>
            <QuoteLine text="The market is a device for transferring money from the impatient to the patient." author="Warren Buffett" />
          </Card>
        </div>
      </div>
    </div>
  )
}

function useApiHistory() {
  const [data, setData] = useState<{ rounds: HistoryRow[]; total: number } | null>(null)
  const load = useCallback(() => {
    api
      .get<{ rounds: HistoryRow[]; total: number }>('/api/desk-history')
      .then(setData)
      .catch(() => undefined)
  }, [])
  useEffect(() => {
    load()
  }, [load])
  return { data, reload: load }
}
