import { useEffect } from 'react'

import { fireConfetti, clearConfetti } from '../lib/confetti'

/** Triggers a confetti burst once when `fire` becomes true. */
export function Confetti({ fire, x, y, count }: { fire: boolean; x?: number; y?: number; count?: number }) {
  useEffect(() => {
    if (fire) {
      void fireConfetti(x, y, count)
    }
    return () => {
      // let the current burst finish; clear on unmount
      window.setTimeout(() => void clearConfetti(), 1500)
    }
  }, [fire, x, y, count])
  return null
}
