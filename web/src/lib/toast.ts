/** Lightweight toast store. Callbacks so components can render their own toasts. */
export type Toast = {
  id: number
  title: string
  description?: string
  tone: 'ok' | 'bad' | 'warn' | 'gold' | 'info'
  duration?: number
}

let listeners = new Set<(toasts: Toast[]) => void>()
let toasts: Toast[] = []
let nextId = 0

export function subscribe(fn: (toasts: Toast[]) => void) {
  listeners.add(fn)
  fn(toasts)
  return () => listeners.delete(fn)
}

function push(toast: Omit<Toast, 'id'>) {
  const id = ++nextId
  const t = { ...toast, id }
  toasts = [...toasts, t]
  listeners.forEach((fn) => fn(toasts))
  window.setTimeout(() => remove(id), toast.duration ?? 4500)
  return id
}

function remove(id: number) {
  toasts = toasts.filter((t) => t.id !== id)
  listeners.forEach((fn) => fn(toasts))
}

export const toast = {
  ok: (title: string, description?: string, duration?: number) => push({ title, description, tone: 'ok', duration }),
  bad: (title: string, description?: string, duration?: number) => push({ title, description, tone: 'bad', duration }),
  warn: (title: string, description?: string, duration?: number) => push({ title, description, tone: 'warn', duration }),
  gold: (title: string, description?: string, duration?: number) => push({ title, description, tone: 'gold', duration }),
  info: (title: string, description?: string, duration?: number) => push({ title, description, tone: 'info', duration }),
  dismiss: (id?: number) => (id === undefined ? (toasts = []) : remove(id)),
}
