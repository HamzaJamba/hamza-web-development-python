import { motion } from 'framer-motion'

export default function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="min-h-screen grid md:grid-cols-2">
      <div className="hidden md:block relative">
        <img
          src="https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1000"
          alt="Travel"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-black/20 flex items-end p-10">
          <p className="text-white text-2xl font-bold max-w-sm">
            Your next adventure starts with TravelHub 🌍
          </p>
        </div>
      </div>
      <div className="flex items-center justify-center p-6 md:p-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-sm"
        >
          <h1 className="text-2xl font-bold mb-1">{title}</h1>
          <p className="text-sm text-black/50 dark:text-white/50 mb-8">{subtitle}</p>
          {children}
        </motion.div>
      </div>
    </div>
  )
}
