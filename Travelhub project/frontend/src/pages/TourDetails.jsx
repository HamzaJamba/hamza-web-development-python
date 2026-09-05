import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Clock, CheckCircle, XCircle } from 'lucide-react'
import RatingStars from '../components/common/RatingStars'
import Skeleton from '../components/common/Skeleton'
import { getTour } from '../api/endpoints'

export default function TourDetails() {
  const { id } = useParams()
  const [tour, setTour] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getTour(id).then((res) => setTour(res.data)).finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 space-y-4">
        <Skeleton className="h-96 w-full" />
        <Skeleton className="h-8 w-1/2" />
      </div>
    )
  }

  if (!tour) return <div className="max-w-7xl mx-auto px-4 py-16">Tour not found.</div>

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="rounded-3xl overflow-hidden h-96 mb-8">
        <img
          src={tour.cover_image || 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1200'}
          alt={tour.name}
          className="w-full h-full object-cover"
        />
      </div>

      <div className="grid md:grid-cols-3 gap-10">
        <div className="md:col-span-2">
          <h1 className="text-3xl font-bold">{tour.name}</h1>
          <p className="text-black/50 dark:text-white/50 mt-1">{tour.destination}</p>
          <div className="flex items-center gap-4 mt-2">
            <RatingStars rating={tour.rating} />
            <span className="flex items-center gap-1 text-xs text-black/50 dark:text-white/50">
              <Clock size={12} /> {tour.days} Days / {tour.nights} Nights
            </span>
          </div>

          <p className="mt-6 text-sm leading-relaxed text-black/70 dark:text-white/70">
            {tour.description || 'No description provided yet.'}
          </p>

          <div className="grid sm:grid-cols-2 gap-6 mt-8">
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-1 text-green-600"><CheckCircle size={16}/> Included</h3>
              <ul className="text-sm space-y-1 text-black/70 dark:text-white/70">
                {tour.included_services?.length > 0 ? tour.included_services.map((s) => <li key={s}>• {s}</li>) : <li className="text-black/40">—</li>}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-1 text-red-500"><XCircle size={16}/> Excluded</h3>
              <ul className="text-sm space-y-1 text-black/70 dark:text-white/70">
                {tour.excluded_services?.length > 0 ? tour.excluded_services.map((s) => <li key={s}>• {s}</li>) : <li className="text-black/40">—</li>}
              </ul>
            </div>
          </div>

          {tour.schedule?.length > 0 && (
            <div className="mt-10">
              <h3 className="font-semibold mb-4">Itinerary</h3>
              <div className="space-y-4 border-l-2 border-[var(--color-primary)]/30 pl-5">
                {tour.schedule.map((day) => (
                  <div key={day.id}>
                    <p className="text-sm font-semibold text-[var(--color-primary)]">Day {day.day_number}: {day.title}</p>
                    <p className="text-sm text-black/60 dark:text-white/60">{day.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="bg-white dark:bg-[#0f2422] border border-black/5 dark:border-white/10 rounded-2xl p-6 h-fit sticky top-24">
          <p className="text-2xl font-bold text-[var(--color-primary)]">${tour.price}</p>
          <p className="text-xs text-black/40 mb-4">per person</p>
          <Link
            to={`/booking/tour/${tour.id}`}
            className="block text-center bg-[var(--color-primary)] text-white font-medium py-2.5 rounded-xl hover:bg-[var(--color-primary-dark)] transition"
          >
            Book Tour
          </Link>
        </div>
      </div>
    </div>
  )
}
