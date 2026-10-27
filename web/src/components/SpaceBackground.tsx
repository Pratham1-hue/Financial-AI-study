/** Moving space background: animated starfield + subtle nebula drift. */
import { useEffect, useRef } from 'react'

export function SpaceBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const g = ctx

    let width = 0
    let height = 0
    let stars: Array<{ x: number; y: number; z: number; speed: number; size: number }> = []
    let offsetX = 0
    let offsetY = 0

    function resize() {
      width = window.innerWidth
      height = window.innerHeight
      canvas!.width = width
      canvas!.height = height
      initStars()
    }

    function initStars() {
      stars = []
      const starCount = Math.min(Math.floor((width * height) / 8000), 150)
      for (let i = 0; i < starCount; i++) {
        stars.push({
          x: Math.random() * width,
          y: Math.random() * height,
          z: Math.random(),
          speed: 0.05 + Math.random() * 0.15,
          size: Math.random() * 1.5 + 0.5,
        })
      }
    }

    function draw() {
      const grad = g.createLinearGradient(0, 0, 0, height)
      grad.addColorStop(0, '#05070a')
      grad.addColorStop(0.5, '#0b0f17')
      grad.addColorStop(1, '#05070a')
      g.fillStyle = grad
      g.fillRect(0, 0, width, height)

      offsetX += 0.15
      offsetY += 0.1
      const nebula = g.createRadialGradient(
        width / 2 + Math.sin(offsetX * 0.5) * 100,
        height / 2 + Math.cos(offsetY * 0.5) * 80,
        0,
        width / 2 + Math.sin(offsetX * 0.5) * 100,
        height / 2 + Math.cos(offsetY * 0.5) * 80,
        Math.max(width, height)
      )
      nebula.addColorStop(0, 'rgba(168, 105, 26, 0.04)')
      nebula.addColorStop(0.4, 'rgba(30, 58, 138, 0.03)')
      nebula.addColorStop(1, 'rgba(5, 7, 10, 0)')
      g.fillStyle = nebula
      g.fillRect(0, 0, width, height)

      g.fillStyle = '#ffffff'
      for (const s of stars) {
        const x = (s.x + offsetX * s.speed) % width
        const y = (s.y + offsetY * s.speed * 0.5) % height
        const alpha = 0.4 + 0.6 * s.z
        g.globalAlpha = alpha
        g.beginPath()
        g.arc(x, y, s.size * s.z, 0, Math.PI * 2)
        g.fill()
      }
      g.globalAlpha = 1

      requestAnimationFrame(draw)
    }

    window.addEventListener('resize', resize)
    resize()
    draw()

    return () => {
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-[-10] pointer-events-none block"
      aria-hidden="true"
    />
  )
}
