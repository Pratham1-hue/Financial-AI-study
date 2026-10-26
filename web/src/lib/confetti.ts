/** Lightweight canvas confetti celebration. Call `fire()` on a gate pass, exam pass, or streak milestone. */

let canvas: HTMLCanvasElement | null = null
let ctx: CanvasRenderingContext2D | null = null
let width = 0
let height = 0
let particles: { x: number; y: number; vx: number; vy: number; color: string; rotation: number; vr: number; life: number }[] = []
let raf: number | null = null

const COLORS = ['#a8691a', '#c98b2b', '#047857', '#f0b64a', '#1e3a8a', '#eab308']

function ensure() {
  if (canvas) return
  canvas = document.createElement('canvas')
  canvas.style.position = 'fixed'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.width = '100vw'
  canvas.style.height = '100vh'
  canvas.style.pointerEvents = 'none'
  canvas.style.zIndex = '9999'
  document.body.appendChild(canvas)
  const c = canvas
  ctx = c.getContext('2d')
  resize()
  window.addEventListener('resize', resize)
}

function resize() {
  if (!canvas) return
  const dpr = Math.max(1, window.devicePixelRatio || 1)
  width = canvas.width = Math.round(window.innerWidth * dpr)
  height = canvas.height = Math.round(window.innerHeight * dpr)
  canvas.style.width = `${window.innerWidth}px`
  canvas.style.height = `${window.innerHeight}px`
  if (ctx) ctx.scale(dpr, dpr)
}

function burst(x: number, y: number, count = 90) {
  for (let i = 0; i < count; i++) {
    const angle = (Math.random() * Math.PI * 2)
    const speed = 4 + Math.random() * 12
    particles.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 4,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      rotation: Math.random() * Math.PI * 2,
      vr: (Math.random() - 0.5) * 0.4,
      life: 100 + Math.random() * 100,
    })
  }
}

function loop() {
  if (!ctx) return
  ctx.clearRect(0, 0, width, height)
  let alive = 0
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i]
    p.x += p.vx
    p.y += p.vy
    p.vy += 0.25 // gravity
    p.rotation += p.vr
    p.life -= 1
    if (p.life > 0) {
      alive++
      ctx.save()
      ctx.translate(p.x, p.y)
      ctx.rotate(p.rotation)
      ctx.fillStyle = p.color
      ctx.fillRect(-3, -6, 6, 12)
      ctx.restore()
    } else {
      particles.splice(i, 1)
    }
  }
  if (alive > 0) {
    raf = window.requestAnimationFrame(loop)
  } else {
    raf = null
  }
}

/** Fire a confetti burst at (x, y) in CSS pixels. */
export function fireConfetti(x = window.innerWidth / 2, y = window.innerHeight / 3, count = 90) {
  ensure()
  burst(x, y, count)
  if (raf === null) {
    raf = window.requestAnimationFrame(loop)
  }
}

export function clearConfetti() {
  if (raf !== null) {
    window.cancelAnimationFrame(raf)
    raf = null
  }
  particles = []
  if (ctx) ctx.clearRect(0, 0, width, height)
}
