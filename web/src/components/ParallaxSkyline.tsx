/** Parallax New York skyline scene.
 *  Three depth layers (far / mid / near) slide at different speeds as you
 *  scroll, with twinkling office windows, blinking aircraft beacons on the
 *  landmark spires, a drifting moon, and a gold street glow. Used as the
 *  immersive footer; children render as an overlay above the buildings.
 */
import { useEffect, useMemo, useRef, type ReactNode } from 'react'

import { cx } from './ui'

type Building = { x: number; w: number; h: number }

const H = 300 // viewBox height shared by all layers

/* --------------------------------------------------------- building arrays */

const FAR: Building[] = [
  { x: 0, w: 64, h: 120 }, { x: 60, w: 48, h: 96 }, { x: 104, w: 72, h: 150 },
  { x: 172, w: 52, h: 110 }, { x: 220, w: 66, h: 134 }, { x: 282, w: 44, h: 100 },
  { x: 322, w: 76, h: 158 }, { x: 394, w: 56, h: 118 }, { x: 446, w: 62, h: 142 },
  { x: 504, w: 48, h: 104 }, { x: 548, w: 72, h: 162 }, { x: 616, w: 54, h: 114 },
  { x: 666, w: 66, h: 138 }, { x: 728, w: 58, h: 124 }, { x: 782, w: 72, h: 154 },
  { x: 850, w: 46, h: 104 }, { x: 892, w: 62, h: 128 }, { x: 950, w: 52, h: 112 },
  { x: 998, w: 72, h: 148 }, { x: 1066, w: 56, h: 118 }, { x: 1118, w: 66, h: 136 },
  { x: 1180, w: 44, h: 100 },
]

// Mid layer includes three landmarks: Empire State (464), Chrysler (752), One WTC (1050)
const MID: Building[] = [
  { x: 8, w: 54, h: 140 }, { x: 58, w: 44, h: 118 }, { x: 98, w: 60, h: 168 },
  { x: 154, w: 50, h: 130 }, { x: 200, w: 66, h: 190 }, { x: 262, w: 48, h: 124 },
  { x: 306, w: 58, h: 156 }, { x: 360, w: 46, h: 134 }, { x: 402, w: 64, h: 182 },
  { x: 464, w: 40, h: 215 }, { x: 474, w: 20, h: 240 }, // Empire State
  { x: 510, w: 56, h: 150 }, { x: 562, w: 48, h: 128 }, { x: 606, w: 62, h: 186 },
  { x: 664, w: 52, h: 140 }, { x: 712, w: 44, h: 120 },
  { x: 752, w: 36, h: 196 }, // Chrysler
  { x: 796, w: 58, h: 158 }, { x: 850, w: 50, h: 136 }, { x: 896, w: 64, h: 196 },
  { x: 956, w: 46, h: 128 }, { x: 998, w: 54, h: 152 },
  { x: 1104, w: 50, h: 144 }, { x: 1150, w: 50, h: 168 },
]

const NEAR: Building[] = [
  { x: 0, w: 80, h: 90 }, { x: 76, w: 64, h: 120 }, { x: 136, w: 88, h: 76 },
  { x: 220, w: 70, h: 132 }, { x: 286, w: 60, h: 96 }, { x: 342, w: 84, h: 116 },
  { x: 422, w: 66, h: 84 }, { x: 484, w: 74, h: 140 }, { x: 554, w: 58, h: 102 },
  { x: 608, w: 86, h: 124 }, { x: 690, w: 62, h: 88 }, { x: 748, w: 70, h: 134 },
  { x: 814, w: 64, h: 100 }, { x: 874, w: 84, h: 118 }, { x: 954, w: 68, h: 92 },
  { x: 1018, w: 74, h: 128 }, { x: 1088, w: 60, h: 96 }, { x: 1144, w: 76, h: 114 },
]

/** Aircraft warning beacons at the spire tips (mid layer). */
const BEACONS = [
  { x: 484, y: 14 },  // Empire State spire
  { x: 770, y: 16 },  // Chrysler antenna
  { x: 1070, y: 16 }, // One WTC spire
]

/* --------------------------------------------------------- window generation */

type Win = { x: number; y: number; delay: number; dur: number }

function buildWindows(bldgs: Building[], step = 8): Win[] {
  const out: Win[] = []
  for (const b of bldgs) {
    const cols = Math.max(1, Math.floor((b.w - 6) / step))
    const rows = Math.max(1, Math.floor((b.h - 10) / step))
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const seed = b.x * 7 + c * 131 + r * 197
        if (seed % 10 < 4) continue // some windows stay dark
        out.push({
          x: b.x + 3 + c * step,
          y: H - b.h + 5 + r * step,
          delay: seed % 5000,
          dur: 3500 + (seed % 2500),
        })
      }
    }
  }
  return out
}

const MID_WINDOWS = buildWindows(MID, 8)
const NEAR_WINDOWS = buildWindows(NEAR, 7)

/* --------------------------------------------------------- scene */

export function ParallaxSkyline({
  height = 300,
  children,
  className,
}: {
  height?: number
  children?: ReactNode
  className?: string
}) {
  const ref = useRef<HTMLDivElement>(null)

  // Parallax: layers slide at different speeds while the scene crosses the viewport.
  useEffect(() => {
    const el = ref.current
    if (!el) return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const layers = Array.from(el.querySelectorAll<HTMLElement>('[data-depth]'))
    let raf = 0
    const update = () => {
      raf = 0
      const rect = el.getBoundingClientRect()
      const vh = window.innerHeight || 800
      if (rect.top > vh || rect.bottom < 0) return
      const p = (vh - rect.top) / (vh + rect.height) // 0 entering → 1 leaving
      for (const l of layers) {
        const depth = Number(l.dataset.depth || 0)
        l.style.transform = `translate3d(0, ${((0.5 - p) * depth).toFixed(2)}px, 0)`
      }
    }
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update)
    }
    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
      if (raf) cancelAnimationFrame(raf)
    }
  }, [])

  const starField = useMemo(
    () =>
      [
        'radial-gradient(1.5px 1.5px at 8% 22%, rgba(255,255,255,.8), transparent)',
        'radial-gradient(1px 1px at 18% 62%, rgba(255,255,255,.55), transparent)',
        'radial-gradient(1.5px 1.5px at 27% 14%, rgba(255,255,255,.7), transparent)',
        'radial-gradient(1px 1px at 38% 40%, rgba(255,255,255,.5), transparent)',
        'radial-gradient(1.5px 1.5px at 47% 20%, rgba(255,255,255,.75), transparent)',
        'radial-gradient(1px 1px at 58% 55%, rgba(255,255,255,.5), transparent)',
        'radial-gradient(1.5px 1.5px at 66% 12%, rgba(255,255,255,.7), transparent)',
        'radial-gradient(1px 1px at 74% 36%, rgba(255,255,255,.55), transparent)',
        'radial-gradient(1.5px 1.5px at 83% 18%, rgba(255,255,255,.8), transparent)',
        'radial-gradient(1px 1px at 92% 48%, rgba(255,255,255,.5), transparent)',
      ].join(', '),
    [],
  )

  return (
    <div ref={ref} className={cx('skyline-scene', className)} style={{ height }}>
      {/* dusk sky + night stars (dark theme) + gold street-line glow */}
      <div className="sky-stars" style={{ backgroundImage: starField }} aria-hidden="true" />
      <div className="sky-glow" aria-hidden="true" />
      <div className="sky-moon" data-depth={-18} aria-hidden="true" />

      {/* far */}
      <svg className="sky-layer" data-depth={14} viewBox={`0 0 1200 ${H}`} preserveAspectRatio="none" aria-hidden="true" style={{ height: '62%' }}>
        <g fill="var(--bldg-far)">
          {FAR.map((b, i) => (
            <rect key={i} x={b.x} y={H - b.h} width={b.w} height={b.h} />
          ))}
        </g>
      </svg>

      {/* mid — landmarks + twinkling windows + beacons */}
      <svg className="sky-layer" data-depth={30} viewBox={`0 0 1200 ${H}`} preserveAspectRatio="none" aria-hidden="true" style={{ height: '80%' }}>
        <g fill="var(--bldg-mid)">
          {MID.map((b, i) => (
            <rect key={i} x={b.x} y={H - b.h} width={b.w} height={b.h} />
          ))}
          {/* Empire State spire */}
          <rect x={481} y={30} width={6} height={30} />
          <polygon points="479,36 489,36 484,10" />
          {/* Chrysler crown + antenna */}
          <polygon points="752,116 788,116 770,64" />
          <rect x={768} y={30} width={4} height={36} />
          {/* One WTC taper */}
          <polygon points="1050,300 1090,300 1080,72 1060,72" />
          <rect x={1068} y={28} width={4} height={46} />
        </g>
        <g fill="var(--win-col)" opacity="0.75">
          {MID_WINDOWS.map((w, i) => (
            <rect key={i} x={w.x} y={w.y} width={3.2} height={4} className="win" style={{ animationDelay: `${w.delay}ms`, animationDuration: `${w.dur}ms` }} />
          ))}
        </g>
        {BEACONS.map((b, i) => (
          <circle key={i} cx={b.x} cy={b.y} r={3.4} className="beacon" style={{ animationDelay: `${i * 800}ms` }} />
        ))}
      </svg>

      {/* near — foreground rooftops */}
      <svg className="sky-layer" data-depth={52} viewBox={`0 0 1200 ${H}`} preserveAspectRatio="none" aria-hidden="true" style={{ height: '96%' }}>
        <g fill="var(--bldg-near)">
          {NEAR.map((b, i) => (
            <rect key={i} x={b.x} y={H - b.h} width={b.w} height={b.h} />
          ))}
        </g>
        <g fill="var(--win-col)" opacity="0.9">
          {NEAR_WINDOWS.map((w, i) => (
            <rect key={i} x={w.x} y={w.y} width={3} height={4} className="win" style={{ animationDelay: `${w.delay}ms`, animationDuration: `${w.dur}ms` }} />
          ))}
        </g>
        <rect x={0} y={H - 3} width={1200} height={3} fill="var(--gold)" opacity="0.55" />
      </svg>

      {/* street glow */}
      <div className="street-glow" aria-hidden="true" />

      {/* content overlay */}
      {children ? <div className="skyline-overlay">{children}</div> : null}
    </div>
  )
}
