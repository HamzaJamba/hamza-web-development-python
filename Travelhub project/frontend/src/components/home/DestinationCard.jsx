import { motion } from 'framer-motion'
import RatingStars from '../common/RatingStars'

export default function DestinationCard({ name, image, price, rating, hotels }) {
  return (
    <motion.div
      whileHover={{ y: -6 }}
      className="relative rounded-2xl overflow-hidden shadow-md group cursor-pointer h-72"
    >
      <img src={image} alt={name} className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition duration-500" />
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent" />
      <div className="absolute bottom-0 p-5 text-white w-full">
        <h3 className="text-xl font-bold">{name}</h3>
        <div className="flex items-center justify-between mt-1 text-sm">
          <span>From ${price}</span>
          <RatingStars rating={rating} />
        </div>
        <p className="text-xs text-white/70 mt-1">{hotels} hotels available</p>
      </div>
    </motion.div>
  )
}
