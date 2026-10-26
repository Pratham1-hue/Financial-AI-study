import { useEffect, useState } from 'react'

import { fireConfetti } from '../lib/confetti'
import { LoadingButton, Card, Empty, Field, PageHeader, SectionTitle, Spinner, cx, inputCls } from '../components/ui'
import { api } from '../lib/api'
import { fmtMoney } from '../lib/format'
import { useApi } from '../lib/hooks'
import { useToast } from '../components/Toast'

export function Profile() {
  const { ok, bad, gold } = useToast()
  const { data: profile, error: profileError } = useApi<{ name: string; target_role: string; target_date: string; daily_hours: number; level: string; why: string; dream_companies: string; day_start: number }>('/api/profile')
  const { data: backupPreview, loading: backupLoading } = useApi<{
    xp: number; tasks: number; modules_done: number; modules_total: number; watched: number; has_profile: boolean; has_focus: boolean; desk_rounds: number; lab_runs: number; labs_solved: number;
  }>('/api/backup/inspect')
  const [exporting, setExporting] = useState(false)
  const [importing, setImporting] = useState(false)
  const [saving, setSaving] = useState(false)
  const [file, setFile] = useState<File | null>(null)

  const [form, setForm] = useState({
    name: '',
    target_role: '',
    daily_hours: '6',
    day_start: '9',
    why: '',
    dream_companies: '',
  })

  // The profile arrives after the first render. Copy it into the form once it
  // does, instead of freezing the blank initial state forever.
  useEffect(() => {
    if (!profile) return
    setForm({
      name: profile.name ?? '',
      target_role: profile.target_role ?? '',
      daily_hours: String(profile.daily_hours ?? 6),
      day_start: String(profile.day_start ?? 9),
      why: profile.why ?? '',
      dream_companies: profile.dream_companies ?? '',
    })
  }, [profile])

  async function saveProfile() {
    setSaving(true)
    try {
      await api.put('/api/profile', {
        name: form.name.trim() || undefined,
        target_role: form.target_role.trim() || undefined,
        daily_hours: Math.min(16, Math.max(1, parseInt(form.daily_hours, 10) || 6)),
        day_start: Math.min(12, Math.max(6, parseInt(form.day_start, 10) || 9)),
        why: form.why.trim() || undefined,
        dream_companies: form.dream_companies.trim() || undefined,
      })
      ok('Profile saved.', 'Your plan recalculates from these targets.')
    } catch (e) {
      bad('Save failed.', (e as Error).message)
    } finally {
      setSaving(false)
    }
  }

  async function exportBackup() {
    setExporting(true)
    try {
      const res = await api.get<{ backup: any; as_json: string }>('/api/backup/export')
      const blob = new Blob([res.as_json], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `laksh-backup-${new Date().toISOString().slice(0, 10)}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      gold('Backup downloaded.', 'Keep this file safe — it is your only restore point on Render’s free tier.')
    } catch (e) {
      bad('Export failed.', (e as Error).message)
    } finally {
      setExporting(false)
    }
  }

  async function importBackup() {
    if (!file) return
    setImporting(true)
    try {
      const text = await file.text()
      const res = await api.post<{ ok: boolean; written: string[]; inspect: any }>('/api/backup/import', { backup: text })
      if (res.ok) {
        void fireConfetti(window.innerWidth / 2, window.innerHeight / 3, 140)
        ok('Backup restored.', `Restored: ${res.written.join(', ')}. Reloading…`)
        window.setTimeout(() => window.location.reload(), 1200)
      }
    } catch (e) {
      bad('Restore failed.', (e as Error).message)
    } finally {
      setImporting(false)
      setFile(null)
    }
  }

  if (profileError) return <Empty>{profileError}</Empty>
  if (!profile || backupLoading) return <Spinner label="Loading your profile" />

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Your account"
        title="Profile"
        subtitle="Set your targets, review your stats, and back up before you deploy."
      />

      {/* profile card */}
      <Card>
        <SectionTitle>Who you are</SectionTitle>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Field label="Name">
            <input className={inputCls} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </Field>
          <Field label="Target role (NYC)">
            <input className={inputCls} value={form.target_role} onChange={(e) => setForm({ ...form, target_role: e.target.value })} />
          </Field>
          <Field label="Daily focus goal (hours)">
            <input className={inputCls} type="number" min={1} max={16} value={form.daily_hours} onChange={(e) => setForm({ ...form, daily_hours: e.target.value })} />
          </Field>
          <Field label="Day starts at (hour)">
            <input className={inputCls} type="number" min={6} max={12} value={form.day_start} onChange={(e) => setForm({ ...form, day_start: e.target.value })} />
          </Field>
          <Field label="Why">
            <textarea
              className={cx(inputCls, 'min-h-[90px] resize-y')}
              value={form.why}
              onChange={(e) => setForm({ ...form, why: e.target.value })}
              placeholder="The reason you will not quit."
            />
            <span className="mt-1 block text-[0.72rem] text-muted">Shown on the dashboard when the day gets hard.</span>
          </Field>
          <Field label="Dream companies">
            <textarea
              className={cx(inputCls, 'min-h-[70px] resize-y')}
              value={form.dream_companies}
              onChange={(e) => setForm({ ...form, dream_companies: e.target.value })}
              placeholder="Jane Street, Two Sigma, Citadel…"
            />
            <span className="mt-1 block text-[0.72rem] text-muted">Comma-separated. Used for the NYC dream board.</span>
          </Field>
          <div className="col-span-3 pt-3">
            <LoadingButton variant="primary" loading={saving} onClick={() => void saveProfile()}>
              {saving ? 'Saving…' : 'Save changes'}
            </LoadingButton>
          </div>
        </div>
      </Card>

      {/* stats */}
      <Card>
        <SectionTitle hint="your numbers">Stats</SectionTitle>
        <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {[
            ['XP', fmtMoney(backupPreview?.xp ?? 0), 'lifetime'],
            ['Modules mastered', String(backupPreview?.modules_done ?? 0), `of ${backupPreview?.modules_total ?? 18}`],
            ['Videos watched', String(backupPreview?.watched ?? 0), 'lessons'],
            ['Desk rounds', String(backupPreview?.desk_rounds ?? 0), 'graded'],
            ['Labs solved', String(backupPreview?.labs_solved ?? 0), `${backupPreview?.lab_runs ?? 0} attempts`],
          ].map(([label, value, sub]) => (
            <Card key={label} className="p-4 text-center">
              <div className="mono text-[1.5rem] font-bold text-ink">{value}</div>
              <div className="mt-1 text-[0.68rem] font-semibold uppercase text-muted">{label}</div>
              <div className="mt-0.5 text-[0.68rem] text-muted">{sub}</div>
            </Card>
          ))}
        </div>
      </Card>

      {/* backup */}
      <Card>
        <SectionTitle hint="Render free tier wipes the filesystem on every restart">Backup &amp; restore</SectionTitle>
        <p className="text-[0.85rem] text-muted mb-4">
          Your progress, profile and focus session live in JSON on the server. Render&rsquo;s free tier
          deletes them on every deploy, restart and spin-down. Download a backup at the end of every
          session; restore it after you redeploy.
        </p>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-[0.68rem] font-semibold uppercase text-muted">Last backup preview</div>
              <div className="text-[0.85rem] text-ink-soft">
                {backupPreview?.xp ?? 0} XP · {backupPreview?.modules_done ?? 0} modules · {backupPreview?.watched ?? 0} videos
              </div>
            </div>
            <LoadingButton variant="primary" loading={exporting} onClick={() => void exportBackup()} className="w-auto">
              {exporting ? 'Preparing…' : 'Download backup'}
            </LoadingButton>
          </div>

          <div className="rounded-xl border border-line bg-surface-2 p-4">
            <div className="mb-3 text-[0.68rem] font-semibold uppercase text-muted">Restore from file</div>
            <input
              type="file"
              accept=".json"
              className="w-full text-[0.78rem] text-muted"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            {file && (
              <p className="mt-2 text-[0.78rem] text-muted">{file.name} ({Math.round(file.size / 1024)} KB)</p>
            )}
            <LoadingButton variant="secondary" loading={importing} disabled={!file} onClick={() => void importBackup()} className="mt-3 w-auto">
              {importing ? 'Restoring…' : 'Restore backup'}
            </LoadingButton>
            <p className="mt-2 text-[0.72rem] text-muted">
              Restoring replaces your current progress, profile and focus state. This cannot be undone.
            </p>
          </div>
        </div>
      </Card>

      <Card>
        <SectionTitle>Data honesty</SectionTitle>
        <p className="text-[0.85rem] text-muted">
          Gates and exams are self-reported for the teach-back rubric — claim only points you truly
          covered. The desk clock runs server-side so it cannot be paused by closing the tab. Your
          streak is earned, not given.
        </p>
      </Card>
    </div>
  )
}
