export function TimerRing({
  remaining,
  total,
  color = 'var(--gold)',
  size = 240,
  clock,
  label,
  sub,
}: {
  remaining: number
  total: number
  color?: string
  size?: number
  clock: string
  label?: string
  sub?: string
}) {
  const stroke = 12
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const pct = total > 0 ? Math.max(0, Math.min(1, remaining / total)) : 0

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--border)" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - pct)}
          style={{ transition: 'stroke-dashoffset 0.9s linear, stroke 0.4s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="mono text-[2.6rem] leading-none font-bold text-ink">{clock}</div>
        {label ? <div className="mt-2 text-[0.78rem] font-semibold tracking-wide text-muted">{label}</div> : null}
        {sub ? <div className="mt-1 max-w-[70%] truncate text-[0.75rem] text-muted">{sub}</div> : null}
      </div>
    </div>
  )
}
