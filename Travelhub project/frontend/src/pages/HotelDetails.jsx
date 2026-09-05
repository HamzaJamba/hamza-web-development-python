import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { MapPin, Wifi, Tv, Wind } from 'lucide-react'
import RatingStars from '../components/common/RatingStars'
import Skeleton from '../components/common/Skeleton'
import { getHotel, listRooms } from '../api/endpoints'

export default function HotelDetails() {
  const { id } = useParams()
  const [hotel, setHotel] = useState(null)
  const [rooms, setRooms] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([getHotel(id), listRooms({ hotel: id })])
      .then(([h, r]) => {
        if (h.status === 'fulfilled') setHotel(h.value.data)
        if (r.status === 'fulfilled') setRooms(r.value.data.results || [])
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 space-y-4">
        <Skeleton className="h-96 w-full" />
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="h-4 w-1/3" />
      </div>
    )
  }

  if (!hotel) return <div className="max-w-7xl mx-auto px-4 py-16">Hotel not found.</div>

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="rounded-3xl overflow-hidden h-96 mb-8">
        <img
          src={hotel.cover_image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1200'}
          alt={hotel.name}
          className="w-full h-full object-cover"
        />
      </div>

      <div className="grid md:grid-cols-3 gap-10">
        <div className="md:col-span-2">
          <h1 className="text-3xl font-bold">{hotel.name}</h1>
          <p className="text-black/50 dark:text-white/50 flex items-center gap-1 mt-1">
            <MapPin size={14} /> {hotel.city}, {hotel.country}
          </p>
          <div className="mt-2"><RatingStars rating={hotel.rating} /></div>

          <p className="mt-6 text-sm leading-relaxed text-black/70 dark:text-white/70">
            {hotel.description || 'No description provided yet.'}
          </p>

          {hotel.facilities?.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-6">
              {hotel.facilities.map((f) => (
                <span key={f} className="px-3 py-1 rounded-full bg-black/5 dark:bg-white/10 text-xs">{f}</span>
              ))}
            </div>
          )}

          <h2 className="text-xl font-bold mt-10 mb-4">Available Rooms</h2>
          <div className="space-y-4">
            {rooms.length > 0 ? rooms.map((room) => (
              <div key={room.id} className="flex items-center justify-between bg-white dark:bg-[#0f2422] border border-black/5 dark:border-white/10 rounded-2xl p-4">
                <div>
                  <h3 className="font-semibold">{room.title}</h3>
                  <div className="flex gap-3 text-xs text-black/50 dark:text-white/50 mt-1">
                    {room.has_wifi && <span className="flex items-center gap-1"><Wifi size={12}/> WiFi</span>}
                    {room.has_ac && <span className="flex items-center gap-1"><Wind size={12}/> AC</span>}
                    {room.has_tv && <span className="flex items-center gap-1"><Tv size={12}/> TV</span>}
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-[var(--color-primary)]">${room.price_per_night}<span className="text-xs font-normal text-black/40">/night</span></p>
                  <Link
                    to={`/booking/hotel/${hotel.id}/room/${room.id}`}
                    className="mt-2 inline-block text-sm bg-[var(--color-primary)] text-white px-4 py-1.5 rounded-full hover:bg-[var(--color-primary-dark)]"
                  >
                    Book Now
                  </Link>
                </div>
              </div>
            )) : <p className="text-sm text-black/40">No rooms listed yet.</p>}
          </div>
        </div>

        <div className="bg-white dark:bg-[#0f2422] border border-black/5 dark:border-white/10 rounded-2xl p-6 h-fit">
          <h3 className="font-semibold mb-3">Reviews</h3>
          <p className="text-sm text-black/40">Customer reviews will appear here.</p>
        </div>
      </div>
    </div>
  )
}
