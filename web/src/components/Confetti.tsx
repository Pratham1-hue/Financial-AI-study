import { useEffect } from 'react'

import { fireConfetti } from '../lib/confetti'

/** Triggers a confetti burst once when `fire` becomes true. */
export function Confetti({ fire, x, y, count }: { fire: boolean; x?: number; y?: number; count?: number }) {
  useEffect(() => {
    if (fire) void fireConfetti(x, y, count)
    // Bursts finish on their own; clearing here used to cut them short.
  }, [fire, x, y, count])
  return null
}
