import { useId } from 'react'

export function LineChart({
  series,
  compare,
  height = 120,
  color = 'var(--gold)',
  compareColor = 'var(--muted)',
  className,
}: {
  series: number[]
  compare?: number[]
  height?: number
  color?: string
  compareColor?: string
  className?: string
}) {
  const w = 600
  const h = height
  // Unique per chart instance. A fixed id made every chart on the page share
  // the first gradient (and React warned about duplicate ids).
  const gradientId = `devi-area-${useId().replace(/[^a-zA-Z0-9_-]/g, '')}`
  const all = [...series, ...(compare ?? [])]
  if (all.length < 2) {
    return <div className={className} style={{ height }} />
  }
  const min = Math.min(...all)
  const max = Math.max(...all)
  const span = max - min || 1
  const pad = 6

  const path = (data: number[]) =>
    data
      .map((v, i) => {
        const x = (i / Math.max(1, data.length - 1)) * w
        const y = h - pad - ((v - min) / span) * (h - pad * 2)
        return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
      })
      .join(' ')

  const area = `${path(series)} L${w},${h} L0,${h} Z`

  return (
    <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" className={className} style={{ width: '100%', height }}>
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.22" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#${gradientId})`} />
      {compare && compare.length > 1 ? (
        <path d={path(compare)} fill="none" stroke={compareColor} strokeWidth="1.5" strokeDasharray="4 4" opacity="0.7" />
      ) : null}
      <path d={path(series)} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  )
}

export function Sparkline({ series, height = 34, color = 'var(--gold)' }: { series: number[]; height?: number; color?: string }) {
  return <LineChart series={series} height={height} color={color} className="overflow-visible" />
}
