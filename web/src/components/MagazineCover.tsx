/** Motivational magazine cover using image.png.
 * Old School Money aesthetic: gold foil border + motivational tagline.
 * Sized as a proper magazine card (not a full-width banner) so it sits
 * beside the hero without pushing dashboard content off-screen.
 */
export function MagazineCover({ className }: { className?: string }) {
  return (
    <div className={`magazine-cover relative overflow-hidden rounded-2xl border border-line bg-surface shadow-lg ${className ?? ''}`}>
      <img
        src="/image.png"
        alt="Motivational magazine cover — the harder you work, the harder it is to surrender"
        loading="eager"
        decoding="async"
      />
      {/* Bottom scrim + tagline, kept clear of the cover's own printed masthead */}
      <div className="absolute inset-x-0 bottom-0 p-4 sm:p-5 pointer-events-none bg-gradient-to-t from-black/70 via-black/30 to-transparent">
        <h2 className="font-display text-[1.05rem] sm:text-[1.25rem] font-bold text-white leading-tight drop-shadow">
          The harder you work,
        </h2>
        <h2 className="font-display text-[1.05rem] sm:text-[1.25rem] font-bold text-gold-2 leading-tight drop-shadow">
          the harder it is to surrender.
        </h2>
        <div className="mt-2 h-px w-20 bg-gold-2/80" />
        <p className="mt-1.5 text-[0.62rem] sm:text-[0.66rem] font-semibold text-white/85 tracking-[0.14em] uppercase">
          Discipline · Mastery · New York
        </p>
      </div>
      {/* Gold foil corner accent */}
      <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-[color-mix(in_srgb,var(--gold)_35%,transparent)] to-transparent pointer-events-none" aria-hidden="true" />
    </div>
  )
}
