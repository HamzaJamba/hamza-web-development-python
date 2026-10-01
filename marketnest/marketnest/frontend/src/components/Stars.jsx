import { Star } from 'lucide-react'

export default function Stars({ value = 0, size = 14, showNumber = false, count }) {
  const filled = Math.round(Number(value))
  return (
    <span className="inline-flex items-center gap-1" aria-label={`Rated ${Number(value).toFixed(1)} out of 5`}>
      <span className="inline-flex">
        {[1, 2, 3, 4, 5].map((n) => (
          <Star key={n} size={size} className={n <= filled ? 'fill-sun text-sun' : 'text-line'} strokeWidth={n <= filled ? 0 : 2} />
        ))}
      </span>
      {showNumber && <span className="text-xs font-semibold text-muted">{Number(value) ? Number(value).toFixed(1) : 'New'}</span>}
      {count != null && <span className="text-xs text-muted">({count})</span>}
    </span>
  )
}
