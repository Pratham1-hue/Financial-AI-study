/** NYC skyline - prominent Manhattan silhouette with twinkling window lights.
 * The skyline sits at the bottom of hero sections with animated lights for
 * that old-school Wall Street / city-that-never-sleeps feel.
 */
import { useEffect, useState } from 'react'

export function Skyline({ height = 90, className }: { height?: number; className?: string }) {
  const [lights, setLights] = useState<Set<number>>(new Set())

  // Randomly twinkle some windows on each frame
  useEffect(() => {
    const interval = setInterval(() => {
      const next = new Set<number>()
      // ~12% of windows lit at any time
      for (let i = 0; i < 40; i++) {
        if (Math.random() < 0.14) next.add(i)
      }
      setLights(next)
    }, 700)
    return () => clearInterval(interval)
  }, [])

  const buildings = [
    [10, 46, 26, 74],
    [40, 28, 22, 92],
    [66, 58, 30, 62],
    [100, 14, 20, 106],
    [124, 40, 26, 80],
    [154, 22, 18, 98],
    [176, 52, 30, 68],
    [210, 34, 22, 86],
    [236, 60, 26, 60],
    [266, 18, 20, 102],
    [290, 44, 28, 76],
    [322, 30, 22, 90],
    [348, 54, 26, 66],
    [378, 38, 20, 82],
    [402, 62, 30, 58],
    [436, 24, 22, 96],
    [462, 48, 26, 72],
    [492, 36, 20, 84],
    [516, 58, 28, 62],
    [548, 26, 22, 94],
    [574, 44, 26, 76],
  ] as const

  // Grid positions for window lights inside each building
  function windowPositions(x: number, y: number, w: number, h: number): [number, number][] {
    const cols = Math.max(1, Math.floor(w / 5))
    const rows = Math.max(1, Math.floor(h / 5))
    const out: [number, number][] = []
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        out.push([x + c * 5 + 2, y + r * 5 + 2])
      }
    }
    return out
  }

  return (
    <svg
      viewBox="0 0 600 120"
      preserveAspectRatio="none"
      className={className}
      style={{ width: '100%', height, display: 'block' }}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="laksh-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--gold)" stopOpacity="0.25" />
          <stop offset="100%" stopColor="var(--gold)" stopOpacity="0.0" />
        </linearGradient>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="1.5" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>
      {/* Night sky gradient behind skyline */}
      <rect x={0} y={0} width={600} height={120} fill="var(--bg)" />
      {/* Buildings - dark navy / ink color */}
      {buildings.map(([x, y, w, h], i) => (
        <g key={i}>
          <rect x={x} y={y} width={w} height={h} rx={1} fill="var(--ink)" />
          {/* Twinkling window lights */}
          {windowPositions(x, y, w, h).map(([wx, wy], wi) => (
            <rect
              key={wi}
              x={wx}
              y={wy}
              width={2.5}
              height={2.5}
              fill={lights.has(i * 100 + wi) ? 'var(--gold)' : 'transparent'}
              opacity={lights.has(i * 100 + wi) ? 0.9 : 0}
              filter="glow"
            />
          ))}
        </g>
      ))}
      {/* Horizon line */}
      <rect x={0} y={118} width={600} height={2} fill="var(--gold)" opacity="0.4" />
    </svg>
  )
}
