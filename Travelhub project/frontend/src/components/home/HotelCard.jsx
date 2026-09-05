import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { MapPin } from 'lucide-react'
import RatingStars from '../common/RatingStars'

export default function HotelCard({ id, name, city, country, price, rating, image }) {
  return (
    <motion.div whileHover={{ y: -4 }} className="bg-white dark:bg-[#0f2422] rounded-2xl overflow-hidden shadow-sm border border-black/5 dark:border-white/10">
      <div className="h-44 overflow-hidden">
        <img src={image} alt={name} className="w-full h-full object-cover hover:scale-105 transition duration-500" />
      </div>
      <div className="p-4">
        <h3 className="font-semibold truncate">{name}</h3>
        <p className="text-xs text-black/50 dark:text-white/50 flex items-center gap-1 mt-1">
          <MapPin size={12} /> {city}, {country}
        </p>
        <div className="flex items-center justify-between mt-3">
          <RatingStars rating={rating} />
          <span className="font-bold text-[var(--color-primary)]">${price}<span className="text-xs font-normal text-black/40">/night</span></span>
        </div>
        <Link
          to={`/hotels/${id}`}
          className="mt-4 block text-center bg-[var(--color-primary)] text-white text-sm font-medium py-2 rounded-full hover:bg-[var(--color-primary-dark)] transition"
        >
          Book Now
        </Link>
      </div>
    </motion.div>
  )
}
