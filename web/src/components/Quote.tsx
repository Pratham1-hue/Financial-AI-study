/** A pull-quote used across pages to keep the ambition visible. */
export function QuoteLine({
  text,
  author,
  tone = 'plain',
}: {
  text: string
  author?: string
  tone?: 'plain' | 'hero'
}) {
  if (tone === 'hero') {
    return (
      <blockquote className="relative">
        <p className="font-display text-[1.5rem] leading-snug font-semibold text-ink italic md:text-[1.75rem]">
          &ldquo;{text}&rdquo;
        </p>
        {author ? (
          <footer className="mt-3 text-[0.78rem] font-semibold tracking-[0.18em] text-gold uppercase">
            — {author}
          </footer>
        ) : null}
      </blockquote>
    )
  }

  return (
    <blockquote className="border-l-2 border-gold pl-4">
      <p className="font-display text-[1.02rem] leading-snug text-ink-soft italic">&ldquo;{text}&rdquo;</p>
      {author ? <footer className="mt-1 text-[0.74rem] font-semibold tracking-[0.14em] text-gold uppercase">{author}</footer> : null}
    </blockquote>
  )
}
