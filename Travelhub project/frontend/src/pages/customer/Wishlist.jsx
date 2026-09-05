import { useEffect, useState } from 'react'
import { Heart } from 'lucide-react'
import { listWishlist } from '../../api/endpoints'
import Skeleton from '../../components/common/Skeleton'

export default function Wishlist() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listWishlist().then((res) => setItems(res.data.results || res.data || [])).finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-2xl font-bold mb-1 flex items-center gap-2"><Heart className="text-[var(--color-accent)]" /> My Wishlist</h1>
      <p className="text-black/50 dark:text-white/50 mb-8">Saved hotels & tours</p>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">{Array.from({length:4}).map((_,i)=><Skeleton key={i} className="h-40"/>)}</div>
      ) : items.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {items.map((item) => (
            <div key={item.id} className="bg-white dark:bg-[#0f2422] border border-black/5 dark:border-white/10 rounded-xl p-4 text-sm">
              {item.hotel ? `Hotel #${item.hotel}` : `Tour #${item.tour_package}`}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-black/40">Nothing saved yet — browse hotels & tours and tap the heart icon to save them here.</p>
      )}
    </div>
  )
}
