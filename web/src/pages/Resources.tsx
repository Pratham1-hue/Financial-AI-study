import { useMemo, useState } from 'react'

import { Badge, Card, Empty, PageHeader, SectionTitle, Spinner, cx, inputCls } from '../components/ui'
import { QuoteLine } from '../components/Quote'
import { type Resource } from '../lib/api'
import { useApi } from '../lib/hooks'

type Filter = {
  q: string
  track: string
  cat: string
  type: string
}

export function Resources() {
  const { data, loading, error } = useApi<{ total: number; items: Resource[] }>('/api/resources?limit=1000')
  const [filter, setFilter] = useState<Filter>({ q: '', track: 'all', cat: 'all', type: 'all' })
  const [view, setView] = useState<'list' | 'grid'>('list')

  const items = useMemo(() => {
    let list = data?.items ?? []
    if (filter.q) {
      const n = filter.q.toLowerCase()
      list = list.filter((r) =>
        `${r.title} ${r.desc} ${r.cat} ${r.type} ${r.track}`.toLowerCase().includes(n),
      )
    }
    if (filter.track !== 'all') list = list.filter((r) => r.track === filter.track)
    if (filter.cat !== 'all') list = list.filter((r) => r.cat === filter.cat)
    if (filter.type !== 'all') list = list.filter((r) => r.type === filter.type)
    return list
  }, [data, filter])

  const tracks = useMemo(() => [...new Set((data?.items ?? []).map((r) => r.track))], [data])
  const cats = useMemo(() => [...new Set((data?.items ?? []).map((r) => r.cat))], [data])
  const types = useMemo(() => [...new Set((data?.items ?? []).map((r) => r.type))], [data])

  if (loading && !data) return <Spinner label="Loading resources" />
  if (error) return <Empty>{error}</Empty>

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Verified library"
        title="Resources"
        subtitle={`${data?.total ?? 0} curated, link-checked resources across finance, AI, quant, career and research. No dead links.`}
      />

      <div className="grid gap-4 lg:grid-cols-[1fr_300px]">
        <div className="space-y-5">
          <Card>
            <SectionTitle hint={`${items.length} matching`}>Browse</SectionTitle>
            <div className="space-y-3">
              <div className="relative">
                <svg className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" strokeLinecap="round" /><path d="M21 21l-4.3-4.3" strokeLinecap="round" />
                </svg>
                <input
                  className={cx(inputCls, 'pl-9')}
                  placeholder="Search title, topic, channel…"
                  value={filter.q}
                  onChange={(e) => setFilter({ ...filter, q: e.target.value })}
                />
              </div>

              <div className="grid gap-2 sm:grid-cols-2">
                <FilterChip label="Track" options={tracks} value={filter.track} onChange={(v) => setFilter({ ...filter, track: v })} />
                <FilterChip label="Category" options={cats} value={filter.cat} onChange={(v) => setFilter({ ...filter, cat: v })} />
                <FilterChip label="Type" options={types} value={filter.type} onChange={(v) => setFilter({ ...filter, type: v })} />
              </div>

              <div className="flex items-center gap-2 pt-2">
                <button onClick={() => setView('list')} className={cx('rounded-lg px-2.5 py-1.5 text-[0.72rem] transition', view === 'list' ? 'bg-gold text-white' : 'text-muted hover:text-ink')}>List</button>
                <button onClick={() => setView('grid')} className={cx('rounded-lg px-2.5 py-1.5 text-[0.72rem] transition', view === 'grid' ? 'bg-gold text-white' : 'text-muted hover:text-ink')}>Grid</button>
              </div>
            </div>

            {items.length === 0 ? (
              <Empty>No resources match your filters.</Empty>
            ) : view === 'list' ? (
              <div className="space-y-2">
                {items.map((r) => (
                  <a
                    key={r.id}
                    href={r.url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-start gap-3 rounded-xl border px-3.5 py-3 transition hover:border-gold"
                  >
                    <div className="mt-0.5 shrink-0 rounded-lg border px-2.5 py-1 text-[0.68rem] font-semibold uppercase tracking-wider">
                      {r.track}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <Badge tone="neutral">{r.type}</Badge>
                        <Badge tone="neutral">{r.cat}</Badge>
                      </div>
                      <h4 className="mt-1 text-[0.9rem] font-semibold text-ink">{r.title}</h4>
                      <p className="text-[0.78rem] text-muted">{r.desc}</p>
                    </div>
                    <span className="text-[0.7rem] text-muted underline">Open →</span>
                  </a>
                ))}
              </div>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {items.map((r) => (
                  <a
                    key={r.id}
                    href={r.url}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-xl border border-line bg-surface-2 p-4 transition hover:border-gold hover:shadow-sm"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <Badge tone="neutral">{r.type}</Badge>
                      <span className="text-[0.68rem] font-semibold text-muted uppercase">{r.track}</span>
                    </div>
                    <h4 className="text-[0.9rem] font-semibold text-ink line-clamp-2">{r.title}</h4>
                    <p className="mt-1.5 text-[0.78rem] text-muted line-clamp-2">{r.desc}</p>
                    <div className="mt-3 flex items-center gap-2 text-[0.7rem]">
                      <Badge tone="neutral">{r.cat}</Badge>
                      <span className="ml-auto text-muted underline">Open external →</span>
                    </div>
                  </a>
                ))}
              </div>
            )}
          </Card>
        </div>

        <div className="space-y-5">
          <Card>
            <SectionTitle hint="verified, not assumed">About the library</SectionTitle>
            <p className="text-[0.85rem] text-muted">
              Every resource has been checked with an automated link checker — no dead links, no
              paywall-only traps where avoidable. Resources open in a new tab so you never lose your
              place in DEVI.
            </p>
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2 text-[0.82rem]">
                <span className="w-2 h-2 rounded-full bg-gold" />
                <span className="text-ink-soft">Add a resource: edit <code className="mono text-[0.7rem] text-gold">lib/resources.py</code> and re-run <code className="mono text-[0.7rem] text-gold">scripts/check_links.py</code>.</span>
              </div>
            </div>
          </Card>

          <Card>
            <QuoteLine text="The best investment you can make is in yourself." author="Warren Buffett" />
          </Card>
        </div>
      </div>
    </div>
  )
}

function FilterChip({ label, options, value, onChange }: { label: string; options: string[]; value: string; onChange: (v: string) => void }) {
  return (
    <div className="space-y-1">
      <span className="text-[0.64rem] font-semibold uppercase tracking-[0.14em] text-muted">{label}</span>
      <div className="flex flex-wrap gap-1.5">
        {['all', ...options].map((o) => (
          <button
            key={o}
            onClick={() => onChange(o)}
            className={cx(
              'rounded-lg border px-2.5 py-1 text-[0.72rem] font-semibold transition',
              value === o ? 'border-gold bg-gold-soft text-gold' : 'border-line text-muted hover:text-ink hover:border-line-strong',
            )}
          >
            {o}
          </button>
        ))}
      </div>
    </div>
  )

}
