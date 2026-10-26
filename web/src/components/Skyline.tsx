/** A small, deterministic Manhattan-ish skyline drawn with plain SVG. */
export function Skyline({ height = 120, className }: { height?: number; className?: string }) {
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
          <stop offset="0%" stopColor="var(--gold)" stopOpacity="0.30" />
          <stop offset="100%" stopColor="var(--gold)" stopOpacity="0.05" />
        </linearGradient>
      </defs>
      {buildings.map(([x, y, w, h], i) => (
        <rect key={i} x={x} y={y} width={w} height={h} rx={1.5} fill="url(#laksh-sky)" />
      ))}
      <rect x={0} y={118} width={600} height={2} fill="var(--gold)" opacity="0.35" />
    </svg>
  )
}
