import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Clock } from 'lucide-react'
import RatingStars from '../common/RatingStars'

export default function TourCard({ id, name, destination, days, nights, price, rating, image }) {
  return (
    <motion.div whileHover={{ y: -4 }} className="bg-white dark:bg-[#0f2422] rounded-2xl overflow-hidden shadow-sm border border-black/5 dark:border-white/10">
      <div className="h-44 overflow-hidden">
        <img src={image} alt={name} className="w-full h-full object-cover hover:scale-105 transition duration-500" />
      </div>
      <div className="p-4">
        <h3 className="font-semibold truncate">{name}</h3>
        <p className="text-xs text-black/50 dark:text-white/50">{destination}</p>
        <div className="flex items-center justify-between mt-2 text-xs text-black/50 dark:text-white/50">
          <span className="flex items-center gap-1"><Clock size={12} /> {days}D / {nights}N</span>
          <RatingStars rating={rating} />
        </div>
        <div className="flex items-center justify-between mt-3">
          <span className="font-bold text-[var(--color-primary)]">${price}</span>
          <Link
            to={`/tours/${id}`}
            className="text-sm font-medium px-4 py-1.5 rounded-full bg-[var(--color-accent)] text-white hover:bg-[var(--color-accent-dark)] transition"
          >
            View
          </Link>
        </div>
      </div>
    </motion.div>
  )
}
