/** Skeleton loading placeholders with a subtle shimmer. */

export function SkeletonLine({ className = '', width = '100%', height = '1rem' }: { className?: string; width?: string; height?: string }) {
  return (
    <div
      className={cx(
        'animate-pulse rounded-full bg-bg-soft',
        className,
      )}
      style={{ width, height }}
    />
  )
}

export function SkeletonCircle({ className = '', size = '2.5rem' }: { className?: string; size?: string }) {
  return (
    <div
      className={cx('animate-pulse rounded-full bg-bg-soft', className)}
      style={{ width: size, height: size }}
    />
  )
}

export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={cx('rounded-xl border border-line bg-surface-2', className)}>
      <div className="p-5 space-y-4">
        <SkeletonLine width="40%" height="0.85rem" />
        <SkeletonLine width="70%" height="0.65rem" />
        <SkeletonLine width="55%" height="0.65rem" />
        <SkeletonLine width="100%" height="0.65rem" />
      </div>
    </div>
  )
}

export function SkeletonList({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-xl border border-line bg-surface-2 p-4 flex gap-3">
          <SkeletonCircle className="shrink-0" size="3rem" />
          <div className="flex flex-col gap-2">
            <SkeletonLine width="60%" />
            <SkeletonLine width="90%" />
          </div>
        </div>
      ))}
    </div>
  )
}

function cx(...parts: (string | false | null | undefined)[]) {
  return parts.filter(Boolean).join(' ')
}
