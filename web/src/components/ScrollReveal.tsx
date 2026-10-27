/** Scroll reveal component using Intersection Observer.
 * Wrap any element to fade it in as it scrolls into view.
 * Variants: 'fade-up', 'fade-in', 'slide-left', 'slide-right', 'zoom-in'
 */
import { useEffect, useRef, useState } from 'react'

type Variant = 'fade-up' | 'fade-in' | 'slide-left' | 'slide-right' | 'zoom-in'

interface ScrollRevealProps {
  children: React.ReactNode
  variant?: Variant
  threshold?: number
  rootMargin?: string
  once?: boolean
  delay?: number
}

const VARIANT_STYLES: Record<Variant, string> = {
  'fade-up': 'opacity-0 translate-y-4',
  'fade-in': 'opacity-0',
  'slide-left': 'opacity-0 translate-x-4',
  'slide-right': 'opacity-0 -translate-x-4',
  'zoom-in': 'opacity-0 scale-95',
}

export function ScrollReveal({
  children,
  variant = 'fade-up',
  threshold = 0.12,
  rootMargin = '0px 0px -40px 0px',
  once = true,
  delay = 0,
}: ScrollRevealProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const el = ref.current
    if (!el) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true)
          if (once) observer.unobserve(el)
        } else if (!once) {
          setVisible(false)
        }
      },
      { threshold, rootMargin }
    )

    observer.observe(el)
    return () => observer.disconnect()
  }, [threshold, rootMargin, once])

  const style = {
    opacity: visible ? 1 : 0,
    transform: visible ? 'none' : VARIANT_STYLES[variant].includes('translate-y')
      ? 'translateY(20px)'
      : VARIANT_STYLES[variant].includes('translate-x-4')
        ? 'translateX(16px)'
        : VARIANT_STYLES[variant].includes('-translate-x-4')
          ? 'translateX(-16px)'
          : 'scale(0.95)',
    transitionDelay: `${delay}ms`,
    transition: 'opacity 0.6s ease, transform 0.6s ease',
  }

  return (
    <div
      ref={ref}
      style={style}
      className={`scroll-reveal transition-all duration-700 ease-out ${mounted ? '' : 'opacity-0'}`}
    >
      {children}
    </div>
  )
}

/** Hook-based scroll reveal for imperative use */
export function useScrollReveal(options: { threshold?: number; rootMargin?: string; once?: boolean } = {}) {
  const ref = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true)
          if (options.once) observer.unobserve(el)
        } else if (!options.once) {
          setVisible(false)
        }
      },
      { threshold: options.threshold ?? 0.12, rootMargin: options.rootMargin ?? '0px 0px -40px 0px' }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [options.threshold, options.rootMargin, options.once])

  return { ref, visible }
}
