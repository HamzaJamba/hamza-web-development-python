import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import SearchBox from '../components/home/SearchBox'
import DestinationCard from '../components/home/DestinationCard'
import HotelCard from '../components/home/HotelCard'
import TourCard from '../components/home/TourCard'
import Skeleton from '../components/common/Skeleton'
import { listHotels, listTours } from '../api/endpoints'

const DESTINATIONS = [
  { name: 'Paris', price: 120, rating: 4.7, hotels: 240, image: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600' },
  { name: 'Dubai', price: 150, rating: 4.8, hotels: 310, image: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600' },
  { name: 'Turkey', price: 90, rating: 4.6, hotels: 180, image: 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=600' },
  { name: 'Italy', price: 130, rating: 4.9, hotels: 275, image: 'https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=600' },
  { name: 'Switzerland', price: 200, rating: 4.9, hotels: 150, image: 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?w=600' },
  { name: 'Bali', price: 80, rating: 4.7, hotels: 320, image: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600' },
]

const TESTIMONIALS = [
  { name: 'Ayesha K.', text: 'Amazing experience booking our Bali trip — smooth from search to checkout.' },
  { name: 'Bilal R.', text: 'Found a great hotel deal in Dubai. Booking process was quick and easy.' },
  { name: 'Sara M.', text: 'The tour package to Turkey exceeded expectations. Will use TravelHub again.' },
]

export default function Home() {
  const [hotels, setHotels] = useState([])
  const [tours, setTours] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([listHotels(), listTours()])
      .then(([h, t]) => {
        if (h.status === 'fulfilled') setHotels(h.value.data.results || [])
        if (t.status === 'fulfilled') setTours(t.value.data.results || [])
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      {/* Hero */}
      <section className="relative h-[85vh] min-h-[560px] flex items-center justify-center text-center overflow-hidden">
        <video
          autoPlay
          muted
          loop
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
          poster="https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1600"
        >
          <source src="https://cdn.coverr.co/videos/coverr-flying-over-clouds-2633/1080p.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black/70" />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative z-10 px-4 flex flex-col items-center gap-8"
        >
          <h1 className="text-white text-4xl md:text-6xl font-bold max-w-3xl leading-tight">
            Explore the World with <span className="text-[var(--color-accent)]">TravelHub</span>
          </h1>
          <p className="text-white/80 max-w-xl text-sm md:text-base">
            Flights, hotels & tour packages — search, compare and book your entire trip in one place.
          </p>
          <SearchBox />
        </motion.div>
      </section>

      {/* Popular Destinations */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-2xl md:text-3xl font-bold mb-2">Popular Destinations</h2>
        <p className="text-black/50 dark:text-white/50 mb-8">Handpicked spots our travelers love most</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {DESTINATIONS.map((d) => (
            <DestinationCard key={d.name} {...d} />
          ))}
        </div>
      </section>

      {/* Trending Hotels */}
      <section className="bg-black/[0.02] dark:bg-white/[0.03] py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl md:text-3xl font-bold mb-2">Trending Hotels</h2>
          <p className="text-black/50 dark:text-white/50 mb-8">Top-rated stays picked by our travelers</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {loading
              ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-72" />)
              : hotels.length > 0
              ? hotels.slice(0, 8).map((h) => (
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
              : (
                <p className="text-sm text-black/40 col-span-full">
                  No hotels yet — once hotel owners add listings and admin approves them, they'll show up here.
                </p>
              )}
          </div>
        </div>
      </section>

      {/* Tour Packages */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-2xl md:text-3xl font-bold mb-2">Tour Packages</h2>
        <p className="text-black/50 dark:text-white/50 mb-8">Curated multi-day journeys with everything included</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {loading
            ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-72" />)
            : tours.length > 0
            ? tours.slice(0, 8).map((t) => (
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
            : (
              <p className="text-sm text-black/40 col-span-full">
                No tour packages yet — once tour operators publish packages and admin approves them, they'll show up here.
              </p>
            )}
        </div>
      </section>

      {/* Testimonials */}
      <section className="bg-[var(--color-primary)]/5 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl md:text-3xl font-bold mb-10 text-center">What Our Travelers Say</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t) => (
              <motion.div
                key={t.name}
                whileHover={{ y: -4 }}
                className="bg-white dark:bg-[#0f2422] rounded-2xl p-6 shadow-sm border border-black/5 dark:border-white/10"
              >
                <div className="text-[var(--color-accent)] mb-2">★★★★★</div>
                <p className="text-sm italic text-black/70 dark:text-white/70">"{t.text}"</p>
                <p className="mt-4 text-sm font-semibold">{t.name}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
