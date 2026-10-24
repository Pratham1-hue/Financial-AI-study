import { useCallback, useEffect, useRef, useState } from 'react'

import { Unauthorized, api } from './api'

export function useApi<T>(path: string | null, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(!!path)

  const load = useCallback(
    async (quiet = false) => {
      if (!path) return
      if (!quiet) setLoading(true)
      try {
        setData(await api.get<T>(path))
        setError(null)
      } catch (e) {
        if (!(e instanceof Unauthorized)) setError((e as Error).message)
      } finally {
        setLoading(false)
      }
    },
    [path],
  )

  useEffect(() => {
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, ...deps])

  return { data, error, loading, reload: load, setData }
}

/** Poll an async function on an interval. Stops when `active` is false. */
export function usePoll(fn: () => void | Promise<void>, ms: number, active = true) {
  const saved = useRef(fn)
  saved.current = fn
  useEffect(() => {
    if (!active || ms <= 0) return
    const id = window.setInterval(() => void saved.current(), ms)
    return () => window.clearInterval(id)
  }, [ms, active])
}

export function useLocalStorage<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw = window.localStorage.getItem(key)
      return raw ? (JSON.parse(raw) as T) : initial
    } catch {
      return initial
    }
  })
  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value))
    } catch {
      /* ignore quota errors */
    }
  }, [key, value])
  return [value, setValue] as const
}
