import { Link } from 'react-router-dom'
import { MapPin } from 'lucide-react'
import Awning from './Awning'
import Stars from './Stars'

export default function StallCard({ stall }) {
  return (
    <Link to={`/stall/${stall.slug}`} className="group block">
      <div className="origin-top transition-transform duration-300 group-hover:scale-y-[1.06]">
        <Awning primary={stall.awning_primary} secondary={stall.awning_secondary} stripes={8} />
      </div>
      <div className="-mt-px rounded-b-2xl border border-t-0 border-line bg-white px-5 pb-5 pt-4">
        <h3 className="font-display text-[15px] font-semibold leading-snug group-hover:text-lapis">{stall.shop_name}</h3>
        <p className="mt-1.5 line-clamp-2 min-h-[2.6em] text-sm text-muted">{stall.tagline}</p>
        <div className="mt-3 flex items-center justify-between text-xs font-semibold text-muted">
          <span className="inline-flex items-center gap-1"><MapPin size={13} /> {stall.city}</span>
          <span>{stall.product_count} products</span>
        </div>
        {stall.rating_avg > 0 && <div className="mt-2"><Stars value={stall.rating_avg} showNumber /></div>}
      </div>
    </Link>
  )
}
