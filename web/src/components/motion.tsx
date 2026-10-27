/** Modern study-motion components: count-up stats, scroll progress,
 *  staggered grid entrances, and a live New York clock.
 *  All respect prefers-reduced-motion and degrade gracefully without
 *  IntersectionObserver.
 */
import { useEffect, useRef, useState, type ReactNode } from 'react'

import { cx } from './ui'

function prefersReduced(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/* ---------------------------------------------------------------- count up */

/** Number that animates up from 0 when it scrolls into view, and re-animates
 *  smoothly whenever the value changes (e.g. XP gained mid-session). */
export function CountUp({
  value,
  duration = 900,
  decimals = 0,
  prefix = '',
  suffix = '',
  format,
  className,
}: {
  value: number
  duration?: number
  decimals?: number
  prefix?: string
  suffix?: string
  format?: (n: number) => string
  className?: string
}) {
  const reduced = useRef(prefersReduced()).current
  const ref = useRef<HTMLSpanElement>(null)
  const [display, setDisplay] = useState(() => (reduced ? value : 0))
  const displayRef = useRef(reduced ? value : 0)
  const valueRef = useRef(value)
  const revealedRef = useRef(reduced)
  const rafRef = useRef(0)

  valueRef.current = value

  const set = (n: number) => {
    displayRef.current = n
    setDisplay(n)
  }

  const animate = (from: number, to: number) => {
    cancelAnimationFrame(rafRef.current)
    if (reduced || from === to) {
      set(to)
      return
    }
    const start = performance.now()
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      set(from + (to - from) * eased)
      if (t < 1) rafRef.current = requestAnimationFrame(tick)
    }
    rafRef.current = requestAnimationFrame(tick)
  }

  // reveal once in view
  useEffect(() => {
    const el = ref.current
    if (reduced) return
    if (!el || typeof IntersectionObserver === 'undefined') {
      revealedRef.current = true
      animate(displayRef.current, valueRef.current)
      return
    }
    const io = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return
        io.disconnect()
        revealedRef.current = true
        animate(displayRef.current, valueRef.current)
      },
      { threshold: 0.3 },
    )
    io.observe(el)
    return () => {
      io.disconnect()
      cancelAnimationFrame(rafRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // value changed after reveal (XP, streak, focus...)
  useEffect(() => {
    if (reduced) {
      set(value)
      return
    }
    if (revealedRef.current) animate(displayRef.current, value)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value])

  const text = format ? format(display) : display.toFixed(decimals)
  return (
    <span ref={ref} className={cx('tabular-nums', className)}>
      {prefix}
      {text}
      {suffix}
    </span>
  )
}

/* ---------------------------------------------------------------- scroll progress */

/** Thin gold progress line pinned to the very top of the window. */
export function ScrollProgress() {
  const [pct, setPct] = useState(0)

  useEffect(() => {
    const onScroll = () => {
      const h = document.documentElement.scrollHeight - window.innerHeight
      setPct(h > 4 ? Math.min(100, Math.max(0, (window.scrollY / h) * 100)) : 0)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }, [])

  return <div className="scroll-progress" style={{ ['--sp' as string]: `${pct}%` }} aria-hidden="true" />
}

/* ---------------------------------------------------------------- stagger group */

/** Grid/list whose children pop in one-by-one when it scrolls into view. */
export function StaggerGroup({
  children,
  className,
  threshold = 0.12,
}: {
  children: ReactNode
  className?: string
  threshold?: number
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [shown, setShown] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el || typeof IntersectionObserver === 'undefined') {
      setShown(true)
      return
    }
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setShown(true)
          io.disconnect()
        }
      },
      { threshold },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [threshold])

  return (
    <div ref={ref} data-revealed={shown} className={cx('stagger-group', className)}>
      {children}
    </div>
  )
}

/* ---------------------------------------------------------------- NYC clock */

/** Live clock ticking in America/New_York. */
export function NYCClock({ className }: { className?: string }) {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 1000)
    return () => window.clearInterval(id)
  }, [])

  let t = ''
  try {
    t = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/New_York',
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    }).format(now)
  } catch {
    t = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', second: '2-digit', hour12: true })
  }

  return (
    <time className={cx('mono', className)} dateTime={now.toISOString()}>
      {t}
    </time>
  )
}
