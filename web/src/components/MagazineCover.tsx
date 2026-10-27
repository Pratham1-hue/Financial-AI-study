/** Motivational magazine cover using user's image.png.
 * Old School Money aesthetic: gold foil accents, masthead typography,
 * subtle vignette overlay. Acts as the hero visual on the dashboard.
 */
import { ScrollReveal } from './ScrollReveal'

export function MagazineCover({ className }: { className?: string }) {
  return (
    <ScrollReveal variant="fade-up" delay={100} once>
      <div className={`magazine-cover relative overflow-hidden rounded-2xl border border-line bg-surface shadow-lg ${className ?? ''}`}>
        <img
          src="/image.png"
          alt="Motivational magazine cover — Wall Street · AI"
          loading="eager"
          decoding="async"
        />
        <div className="absolute inset-0 flex flex-col justify-between p-6 pointer-events-none">
          {/* Masthead */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-gold" />
              <span className="font-display text-[0.7rem] font-bold tracking-wider text-gold uppercase">
                L a k s h
              </span>
            </div>
            <span className="text-[0.65rem] font-semibold tracking-wider text-gold/80 uppercase">
              Wall Street · AI
            </span>
          </div>
          {/* Motivational tagline */}
          <div className="mt-auto mb-8">
            <h2 className="font-display text-[1.5rem] md:text-[2rem] font-bold text-white leading-[1.05] mb-2 shadow-md">
              The harder you work,
            </h2>
            <h2 className="font-display text-[1.5rem] md:text-[2rem] font-bold text-gold leading-[1.05] shadow-md">
              the harder it is to surrender.
            </h2>
            <div className="mt-3 h-px w-24 bg-gold-2" />
            <p className="mt-2 text-[0.72rem] font-semibold text-gold-soft tracking-[0.1em] uppercase">
              Discipline · Mastery · New York
            </p>
          </div>
        </div>
      </div>
    </ScrollReveal>
  )
}
