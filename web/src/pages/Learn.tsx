import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { QuoteLine } from '../components/Quote'
import { Badge, Bar, Button, Card, Empty, PageHeader, SectionTitle, Spinner, cx } from '../components/ui'
import { api, type ModuleDetail, type ModuleSummary } from '../lib/api'
import { fmtViews } from '../lib/format'
import { useApi } from '../lib/hooks'

function statusTone(status: string) {
  if (status === 'Passed' || status === 'Mastered') return 'ok' as const
  if (status === 'Ready' || status === 'In progress') return 'gold' as const
  if (status === 'Locked') return 'neutral' as const
  return 'warn' as const
}

function fmtSecs(secs: number) {
  const m = Math.round(secs / 60)
  return m >= 60 ? `${Math.floor(m / 60)}h ${m % 60}m` : `${m}m`
}

export function Learn() {
  const [params, setParams] = useSearchParams()
  const [track, setTrack] = useState<string>('ai')
  const [mid, setMid] = useState<string | null>(params.get('module'))
  const [error, setError] = useState<string | null>(null)
  const [detail, setDetail] = useState<ModuleDetail | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

  const { data: allModules } = useApi<ModuleSummary[]>('/api/modules')
  const { data: modules, loading: loadingList, reload: reloadList } = useApi<ModuleSummary[]>(`/api/modules?track=${track}`, [track])

  const tracks = useMemo(() => {
    const set = new Set((allModules ?? []).map((m) => m.track))
    return ['ai', ...Array.from(set).filter((t) => t !== 'ai')]
  }, [allModules])

  // follow the ?module= deep link
  useEffect(() => {
    const wanted = params.get('module')
    if (wanted) setMid(wanted)
  }, [params])

  useEffect(() => {
    if (!mid && modules && modules.length > 0) setMid(modules[0].id)
  }, [mid, modules])

  useEffect(() => {
    if (!mid) return
    let alive = true
    setLoadingDetail(true)
    api
      .get<ModuleDetail>(`/api/modules/${mid}`)
      .then((d) => alive && setDetail(d))
      .catch((e) => alive && setError((e as Error).message))
      .finally(() => alive && setLoadingDetail(false))
    return () => {
      alive = false
    }
  }, [mid])

  async function markWatched(videoId: string) {
    if (!detail) return
    try {
      await api.post(`/api/modules/${detail.id}/watch`, { video_id: videoId })
      setDetail(await api.get<ModuleDetail>(`/api/modules/${detail.id}`))
      void reloadList(true)
    } catch (e) {
      setError((e as Error).message)
    }
  }

  function selectModule(id: string) {
    setMid(id)
    setParams(id ? { module: id } : {}, { replace: true })
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="The curriculum"
        title="Learn"
        subtitle="Eighteen modules from first principles to research-grade. Read the map, then work one module until it is boring."
      />

      {error ? <Empty>{error}</Empty> : null}

      <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
        <div className="space-y-4">
          <Card padded={false} className="overflow-hidden">
            <div className="border-b border-line p-4">
              <div className="mb-2.5 text-[0.66rem] font-semibold tracking-[0.16em] text-muted uppercase">Track</div>
              <div className="flex flex-wrap gap-2">
                {tracks.map((t) => (
                  <button
                    key={t}
                    onClick={() => {
                      setTrack(t)
                      setMid(null)
                      setParams({}, { replace: true })
                    }}
                    className={cx(
                      'rounded-full border px-3 py-1 text-[0.76rem] font-semibold uppercase tracking-wider transition',
                      track === t ? 'border-gold bg-gold-soft text-gold' : 'border-line text-muted hover:text-ink',
                    )}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {loadingList && !modules ? (
              <Spinner label="Loading modules" />
            ) : (
              <div className="max-h-[560px] overflow-y-auto p-2">
                {(modules ?? []).map((m) => (
                  <button
                    key={m.id}
                    onClick={() => selectModule(m.id)}
                    className={cx(
                      'mb-1 w-full rounded-xl px-3.5 py-3 text-left transition',
                      mid === m.id ? 'bg-gold-soft' : 'hover:bg-surface-2',
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <span className={cx('mono text-[0.7rem] font-bold', mid === m.id ? 'text-gold' : 'text-muted')}>{m.id}</span>
                      <Badge tone={statusTone(m.status)}>{m.status}</Badge>
                    </div>
                    <div className="mt-1 text-[0.88rem] font-semibold text-ink">{m.title}</div>
                    <div className="text-[0.72rem] text-muted">
                      {m.lessons} lessons · {m.videos} videos · {m.quiz_questions} Qs
                    </div>
                  </button>
                ))}
              </div>
            )}
          </Card>

          <Card>
            <QuoteLine text="An investment in knowledge pays the best interest." author="Benjamin Franklin" />
          </Card>
        </div>

        <div>
          {loadingDetail && !detail ? (
            <Spinner label="Opening module" />
          ) : !detail ? (
            <Empty>Pick a module on the left.</Empty>
          ) : (
            <div className="space-y-5">
              <Card>
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <Badge tone="gold">{detail.id}</Badge>
                      <Badge tone={statusTone(detail.status)}>{detail.status}</Badge>
                      <span className="text-[0.72rem] font-semibold tracking-[0.12em] text-muted uppercase">{detail.level}</span>
                    </div>
                    <h2 className="mt-2.5 text-[1.6rem] font-bold text-ink">{detail.title}</h2>
                    <p className="mt-1 max-w-2xl text-[0.9rem] text-muted">{detail.summary}</p>
                  </div>
                  <div className="flex flex-col gap-2">
                    <Link to={`/quizzes?module=${detail.id}`}>
                      <Button variant="secondary">Practice quiz ({detail.quiz_questions})</Button>
                    </Link>
                    <Link to={`/quizzes?tab=gates&module=${detail.id}`}>
                      <Button variant="primary">Take the gate</Button>
                    </Link>
                  </div>
                </div>

                {detail.missing_prereqs.length > 0 ? (
                  <div className="mt-4 rounded-xl border border-[color-mix(in_srgb,var(--warn)_30%,transparent)] bg-warn-soft px-4 py-2.5 text-[0.83rem] text-warn">
                    Prerequisites still open: {detail.missing_prereqs.join(', ')}
                  </div>
                ) : null}

                <div className="mt-5">
                  <Bar
                    value={detail.watch.done}
                    max={detail.watch.total || 1}
                    label={`Video queue ${detail.watch.done}/${detail.watch.total} · ${fmtSecs(detail.watch.minutes_left * 60)} left`}
                  />
                </div>
              </Card>

              <div className="grid gap-5 xl:grid-cols-2">
                <Card>
                  <SectionTitle hint={`${detail.lessons.length} lessons`}>Syllabus</SectionTitle>
                  <ol className="space-y-2">
                    {detail.lessons.map((l, i) => (
                      <li key={i} className="flex gap-3 rounded-xl border border-line bg-surface-2 px-3.5 py-2.5">
                        <span className="mono text-[0.72rem] font-bold text-gold">{String(i + 1).padStart(2, '0')}</span>
                        <span className="text-[0.86rem] text-ink-soft">{l}</span>
                      </li>
                    ))}
                  </ol>

                  <div className="mt-5">
                    <div className="mb-2 text-[0.68rem] font-semibold tracking-[0.16em] text-muted uppercase">You will be able to</div>
                    <ul className="space-y-1.5">
                      {detail.outcomes.map((o, i) => (
                        <li key={i} className="flex gap-2 text-[0.85rem] text-ink-soft">
                          <span className="text-ok">✓</span>
                          {o}
                        </li>
                      ))}
                    </ul>
                  </div>
                </Card>

                <Card>
                  <SectionTitle hint={`${detail.videos.length} synced`}>Video queue</SectionTitle>
                  {detail.videos.length === 0 ? (
                    <Empty>No videos synced for this module yet.</Empty>
                  ) : (
                    <div className="max-h-[420px] space-y-2 overflow-y-auto pr-1">
                      {detail.videos.map((v) => (
                        <div
                          key={v.id}
                          className={cx(
                            'rounded-xl border px-3.5 py-2.5',
                            v.watched ? 'border-[color-mix(in_srgb,var(--ok)_30%,transparent)] bg-ok-soft' : 'border-line bg-surface-2',
                          )}
                        >
                          <div className="flex items-start gap-3">
                            <div className="min-w-0 flex-1">
                              <a
                                href={`https://www.youtube.com/watch?v=${v.id}`}
                                target="_blank"
                                rel="noreferrer"
                                className="block truncate text-[0.86rem] font-semibold text-ink hover:text-gold"
                              >
                                {v.title}
                              </a>
                              <div className="text-[0.72rem] text-muted">
                                {v.channel} · {fmtSecs(v.secs)} · {fmtViews(v.views)}
                              </div>
                            </div>
                            <button
                              onClick={() => void markWatched(v.id)}
                              disabled={v.watched}
                              className={cx(
                                'shrink-0 rounded-lg border px-2.5 py-1 text-[0.72rem] font-semibold transition',
                                v.watched ? 'border-transparent text-ok' : 'border-line-strong text-ink-soft hover:border-gold hover:text-gold',
                              )}
                            >
                              {v.watched ? 'Watched' : 'Mark'}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </div>

              <Card>
                <SectionTitle hint={`${detail.resources.length} curated`}>Reading &amp; resources</SectionTitle>
                <div className="grid gap-2.5 md:grid-cols-2">
                  {detail.resources.map((r) => (
                    <a
                      key={r.id}
                      href={r.url}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-xl border border-line bg-surface-2 px-4 py-3 transition hover:border-gold"
                    >
                      <div className="flex items-center gap-2">
                        <Badge tone="neutral">{r.type}</Badge>
                        <span className="text-[0.68rem] font-semibold tracking-[0.12em] text-muted uppercase">{r.cat}</span>
                      </div>
                      <div className="mt-1.5 text-[0.88rem] font-semibold text-ink">{r.title}</div>
                      <div className="text-[0.76rem] text-muted">{r.desc}</div>
                    </a>
                  ))}
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
