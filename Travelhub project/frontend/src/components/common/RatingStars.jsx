import { Star } from 'lucide-react'

export default function RatingStars({ rating = 0, size = 14 }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          size={size}
          className={i <= Math.round(rating) ? 'fill-[var(--color-accent)] text-[var(--color-accent)]' : 'text-black/20 dark:text-white/20'}
        />
      ))}
    </div>
  )
}
