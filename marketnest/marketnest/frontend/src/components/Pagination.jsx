import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function Pagination({ page, count, pageSize, onPage }) {
  const pages = Math.ceil(count / pageSize)
  if (pages <= 1) return null
  const btn = 'grid h-10 min-w-10 place-items-center rounded-full px-3 text-sm font-bold transition-colors'
  return (
    <nav className="mt-10 flex flex-wrap items-center justify-center gap-1.5" aria-label="Pages">
      <button className={`${btn} hover:bg-mist disabled:opacity-30`} disabled={page <= 1} onClick={() => onPage(page - 1)} aria-label="Previous page"><ChevronLeft size={18} /></button>
      {Array.from({ length: pages }, (_, i) => i + 1).map((n) => (
        <button key={n} onClick={() => onPage(n)} aria-current={n === page ? 'page' : undefined}
          className={`${btn} ${n === page ? 'bg-midnight text-white' : 'hover:bg-mist'}`}>{n}</button>
      ))}
      <button className={`${btn} hover:bg-mist disabled:opacity-30`} disabled={page >= pages} onClick={() => onPage(page + 1)} aria-label="Next page"><ChevronRight size={18} /></button>
    </nav>
  )
}
