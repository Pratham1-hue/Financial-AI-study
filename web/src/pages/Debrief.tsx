import { useEffect, useState } from 'react'

import { fireConfetti } from '../lib/confetti'
import { QuoteLine } from '../components/Quote'
import { StaggerGroup } from '../components/motion'
import { Badge, Card, Empty, Field, LoadingButton, PageHeader, SectionTitle, Spinner, cx, inputCls } from '../components/ui'
import { api } from '../lib/api'
import { useApi } from '../lib/hooks'
import { useToast } from '../components/Toast'

type Entry = {
  concept: string
  explain: string
  gaps: string
  win: string
  first: string
  energy: number
  at: string
}

type Payload = {
  today: string
  entry: Entry | null
  history: ({ date: string } & Partial<Entry>)[]
  min_chars: number
  xp_reward: number
}

const EMPTY = { concept: '', explain: '', gaps: '', win: '', first: '', energy: 3 }

function Energy({ value }: { value: number }) {
  return (
    <span className="mono text-[0.78rem] font-bold text-gold">
      {'●'.repeat(Math.max(1, Math.min(5, value)))}
      <span className="text-muted">{'○'.repeat(5 - Math.max(1, Math.min(5, value)))}</span>
    </span>
  )
}

export function Debrief() {
  const { ok, bad, gold } = useToast()
  const { data, loading, error, reload } = useApi<Payload>('/api/debrief')
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!data?.entry) return
    setForm({
      concept: data.entry.concept ?? '',
      explain: data.entry.explain ?? '',
      gaps: data.entry.gaps ?? '',
      win: data.entry.win ?? '',
      first: data.entry.first ?? '',
      energy: data.entry.energy ?? 3,
    })
  }, [data])

  if (loading && !data) return <Spinner label="Opening your journal" />
  if (error) return <Empty>{error}</Empty>
  if (!data) return <Empty>No debrief data.</Empty>

  const chars = form.explain.trim().length
  const ready = chars >= data.min_chars && form.concept.trim().length > 0 && form.first.trim().length > 0

  async function save() {
    setSaving(true)
    try {
      const res = await api.post<{ is_new: boolean; xp_gain: number }>('/api/debrief', form)
      if (res.is_new) {
        void fireConfetti(window.innerWidth / 2, window.innerHeight / 3, 120)
        gold('Debrief filed.', `+${res.xp_gain} XP. Sleep — your brain does the rest tonight.`)
      } else {
        ok('Debrief updated.', 'Editing today’s entry does not earn XP twice.')
      }
      void reload(true)
    } catch (e) {
      bad('Could not save.', (e as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="The fifth step"
        title="Evening debrief"
        subtitle="The Feynman test: explain today's hardest idea like you are teaching a smart twelve-year-old. No jargon, no hiding."
        right={data.entry ? <Badge tone="ok">filed today</Badge> : <Badge tone="warn">open today</Badge>}
      />

      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <Card>
          <SectionTitle hint={data.entry ? 'edit and resubmit' : `+${data.xp_reward} XP, once per day`}>
            Today&apos;s entry
          </SectionTitle>

          <div className="space-y-4">
            <Field label="The hardest concept I worked on today">
              <input
                className={inputCls}
                value={form.concept}
                onChange={(e) => setForm({ ...form, concept: e.target.value })}
                placeholder="e.g. why a bond's duration is not its maturity"
              />
            </Field>

            <Field
              label="Explain it in plain English"
              hint={
                <span className={chars >= data.min_chars ? 'text-ok' : 'text-muted'}>
                  {chars}/{data.min_chars} characters{chars >= data.min_chars ? ' — long enough to count' : ' — keep going'}
                </span>
              }
            >
              <textarea
                className={cx(inputCls, 'min-h-[220px] resize-y leading-relaxed')}
                value={form.explain}
                onChange={(e) => setForm({ ...form, explain: e.target.value })}
                placeholder="Start from the thing itself, not the textbook definition. If a term is unavoidable, define it in the same sentence."
              />
            </Field>

            <Field label="Where did the explanation break down?" hint="These gaps are tomorrow's first study targets.">
              <textarea
                className={cx(inputCls, 'min-h-[80px] resize-y')}
                value={form.gaps}
                onChange={(e) => setForm({ ...form, gaps: e.target.value })}
                placeholder="I could describe the mechanics but not why the sign flips when rates fall."
              />
            </Field>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Biggest win today">
                <input
                  className={inputCls}
                  value={form.win}
                  onChange={(e) => setForm({ ...form, win: e.target.value })}
                  placeholder="One thing that actually moved."
                />
              </Field>
              <Field label="Tomorrow's first focus block">
                <input
                  className={inputCls}
                  value={form.first}
                  onChange={(e) => setForm({ ...form, first: e.target.value })}
                  placeholder="9:00–10:30 — re-derive duration from scratch."
                />
              </Field>
            </div>

            <Field label="Energy / focus today">
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min={1}
                  max={5}
                  step={1}
                  value={form.energy}
                  onChange={(e) => setForm({ ...form, energy: Number(e.target.value) })}
                  className="w-full accent-[var(--gold)]"
                />
                <Energy value={form.energy} />
              </div>
            </Field>

            <div className="flex flex-wrap items-center gap-3 border-t border-line pt-4">
              <LoadingButton loading={saving} disabled={!ready} onClick={() => void save()}>
                {saving ? 'Filing…' : data.entry ? 'Update debrief' : 'File debrief'}
              </LoadingButton>
              {!ready ? (
                <span className="text-[0.78rem] text-muted">
                  Name the concept, write {data.min_chars}+ characters, and commit to tomorrow&apos;s first block.
                </span>
              ) : null}
            </div>
          </div>
        </Card>

        <div className="space-y-5">
          <Card>
            <SectionTitle>Rules of the exercise</SectionTitle>
            <ol className="space-y-2 text-[0.84rem] text-muted">
              <li>1. Use your own words. Quoting the lecture is not understanding.</li>
              <li>2. No undefined jargon. If you need a term, define it.</li>
              <li>3. Name the crack. The gap you admit is the gap you can close.</li>
              <li>4. Pick tomorrow&apos;s first block before you sleep. Decide once.</li>
            </ol>
          </Card>

          <Card>
            <QuoteLine text="If you can't explain it simply, you don't understand it well enough." author="Richard Feynman" />
          </Card>
        </div>
      </div>

      <Card>
        <SectionTitle hint={`${data.history.length} entries`}>Learning journal</SectionTitle>
        {data.history.length === 0 ? (
          <Empty>No entries yet. Tonight is a good night to start.</Empty>
        ) : (
          <StaggerGroup as="div" className="space-y-2">
            {data.history.map((e) => (
              <details key={e.date} className="group rounded-xl border border-line bg-surface-2 px-4 py-3">
                <summary className="flex cursor-pointer flex-wrap items-center gap-2 text-[0.86rem]">
                  <span className="mono text-[0.75rem] font-bold text-gold">{e.date}</span>
                  <span className="font-semibold text-ink">{e.concept || 'Untitled'}</span>
                  {e.energy ? <Energy value={e.energy} /> : null}
                  <span className="ml-auto text-[0.72rem] text-muted">{e.at ? e.at.slice(11) : ''}</span>
                </summary>
                <div className="mt-3 space-y-2 border-t border-line pt-3 text-[0.84rem]">
                  <p className="text-ink-soft">{e.explain}</p>
                  {e.gaps ? <p className="text-muted"><span className="font-semibold text-bad">Gap:</span> {e.gaps}</p> : null}
                  {e.win ? <p className="text-muted"><span className="font-semibold text-ok">Win:</span> {e.win}</p> : null}
                  {e.first ? <p className="text-muted"><span className="font-semibold text-gold">Next:</span> {e.first}</p> : null}
                </div>
              </details>
            ))}
          </StaggerGroup>
        )}
      </Card>
    </div>
  )
}
