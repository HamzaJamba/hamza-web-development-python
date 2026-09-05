import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import HotelCard from '../components/home/HotelCard'
import Skeleton from '../components/common/Skeleton'
import { listHotels } from '../api/endpoints'

export default function Hotels() {
  const [searchParams] = useSearchParams()
  const [hotels, setHotels] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    listHotels({ search: searchParams.get('destination') || undefined })
      .then((res) => setHotels(res.data.results || []))
      .finally(() => setLoading(false))
  }, [searchParams])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl font-bold mb-2">Find Your Stay</h1>
      <p className="text-black/50 dark:text-white/50 mb-10">
        {searchParams.get('destination') ? `Hotels matching "${searchParams.get('destination')}"` : 'Browse all approved hotels'}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading
          ? Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-72" />)
          : hotels.length > 0
          ? hotels.map((h) => (
              <HotelCard
                key={h.id}
                id={h.id}
                name={h.name}
                city={h.city}
                country={h.country}
                price={h.rooms?.[0]?.price_per_night || '—'}
                rating={h.rating}
                image={h.cover_image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600'}
              />
            ))
          : <p className="text-sm text-black/40 col-span-full">No hotels found.</p>}
      </div>
    </div>
  )
}
