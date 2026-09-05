import { useEffect, useState } from 'react'
import TourCard from '../components/home/TourCard'
import Skeleton from '../components/common/Skeleton'
import { listTours } from '../api/endpoints'

export default function Tours() {
  const [tours, setTours] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listTours().then((res) => setTours(res.data.results || [])).finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl font-bold mb-2">Tour Packages</h1>
      <p className="text-black/50 dark:text-white/50 mb-10">Curated multi-day journeys, all-inclusive</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading
          ? Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-72" />)
          : tours.length > 0
          ? tours.map((t) => (
              <TourCard
                key={t.id}
                id={t.id}
                name={t.name}
                destination={t.destination}
                days={t.days}
                nights={t.nights}
                price={t.price}
                rating={t.rating}
                image={t.cover_image || 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600'}
              />
            ))
          : <p className="text-sm text-black/40 col-span-full">No tour packages found.</p>}
      </div>
    </div>
  )
}
