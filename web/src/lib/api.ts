export class Unauthorized extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (res.status === 401 && path !== '/api/login') {
    window.dispatchEvent(new Event('laksh:unauthorized'))
    throw new Unauthorized('Not authenticated')
  }
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const body = await res.json()
      if (body?.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      /* keep the status text */
    }
    throw new Error(detail)
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PUT', body: body === undefined ? undefined : JSON.stringify(body) }),
}

/* ------------------------------------------------------------------ types */
export interface Session {
  auth_required: boolean
  authenticated: boolean
}

export interface Quote {
  text: string
  author: string
}

export interface Week {
  w: number
  phase: string
  title: string
  focus: string
  days: string[]
  milestone: string
}

export interface Bootstrap {
  profile: {
    name: string
    target_role: string
    target_date: string
    daily_hours: number
    level: string
    why: string
    dream_companies: string
    day_start: number
  }
  plan: {
    day: number
    days_total: number
    week: Week | null
    assignment: string
    phase_progress: { phase: string; done: number; total: number }[]
    current_week: Week | null
  }
  metrics: {
    day_score: number
    day_parts: { name: string; value: number; max: number }[]
    focus_min_today: number
    goal_min: number
    all_time_hours: number
    mastery_index: number
    mastery_parts: Record<string, number>
    streak: number
    xp: number
    level: number
    level_title: string
    locked_today_min: number
  }
  stock: {
    symbol: string
    price: number
    change_pct: number
    rating: string
    rating_avg: number
    series: { date: string; close: number; score: number }[]
  }
  loop: { name: string; done: boolean; to: string }[]
  focus: { today_min: number; sessions_today: number; week_min: number; total_hours: number; streak: number }
  rank: { current: [number, string, string]; next: [number, string] | null; pct: number }
  quote: Quote
  modules: { id: string; title: string; track: string; status: string; weeks: number[] }[]
  breaches: string[]
  comp: { role: string; comp: string }[]
  bootcamp: { name: string; mins: number; desc: string; start: string; end: string }[]
}

export interface ModuleSummary {
  id: string
  title: string
  track: string
  level: string
  weeks: number[]
  summary: string
  status: string
  lessons: number
  videos: number
  quiz_questions: number
}

export interface Resource {
  id: string
  title: string
  url: string
  type: string
  track: string
  cat: string
  desc: string
}

export interface Video {
  id: string
  title: string
  channel: string
  secs: number
  views: number
  watched?: boolean
}

export interface ModuleDetail {
  id: string
  title: string
  track: string
  level: string
  weeks: number[]
  summary: string
  lessons: string[]
  outcomes: string[]
  status: string
  missing_prereqs: string[]
  resources: Resource[]
  videos: Video[]
  watch: { done: number; total: number; minutes_left: number }
  quiz_questions: number
}

export interface Question {
  id: string
  track: string
  module: string
  diff: string
  q: string
  opts: string[]
}

export interface FocusState {
  status: 'idle' | 'running' | 'paused'
  phase: 'focus' | 'short_break' | 'long_break'
  phase_label: string
  phase_color: string
  mode: string
  modes: Record<string, { focus: number; short: number; long: number; every: number; desc: string }>
  subjects: string[]
  subject: string
  label: string
  cycles: number
  every: number
  auto_break: boolean
  sound: boolean
  ends_at: number | null
  remaining: number
  total: number
  custom: { focus: number; short: number; long: number; every: number }
}

export interface FocusPayload {
  state: FocusState
  stats: { today_min: number; sessions_today: number; week_min: number; total_hours: number; streak: number }
  goal_min: number
  rank: { current: [number, string, string]; next: [number, string] | null; pct: number; ladder: [number, string, string][] }
  log: { id: string; date: string; ended_at: string; minutes: number; subject: string; label: string; mode: string }[]
}

export interface DeskRound {
  round_id: string
  tick: number
  duration: number
  remaining: number
  done: boolean
  graded: boolean
  headline: string
  seed: number
  quotes: Record<string, { bid: number; mid: number; ask: number; name: string; kind: string }>
  positions: { sym: string; qty: number; avg: number; px: number; value: number; pnl: number }[]
  cash: number
  realized: number
  equity: number
  gross: number
  bench: number
  equity_curve: number[]
  bench_curve: number[]
  trades: { t: number; sym: string; qty: number; px: number; side: string }[]
  breaches: number
  tape: { t: number; sym: string; qty: number; px: number; side: string }[]
  limits: { start_cash: number; max_gross: number; max_name: number; max_trades: number }
  book?: { sym: string; bids: { px: number; size: number }[]; asks: { px: number; size: number }[] }
}

export interface DeskGrade {
  score: number
  ret: number
  bench: number
  dd: number
  trades: number
  breaches: number
  realized: number
  equity: number
  notes: string[]
  seed: number
}
