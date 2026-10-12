import { motion } from 'framer-motion'

export default function OEEGauge({ value = 0, size = 160 }) {
  const radius = (size - 16) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (Math.min(100, Math.max(0, value)) / 100) * circumference
  const color = value >= 80 ? '#34d399' : value >= 60 ? '#f59e0b' : '#fb7185'

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} stroke="#1d2836" strokeWidth="10" fill="none" />
        <motion.circle
          cx={size / 2} cy={size / 2} r={radius} stroke={color} strokeWidth="10" fill="none" strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="font-display text-3xl font-bold">
          {value}%
        </motion.span>
        <span className="text-[10px] font-semibold uppercase tracking-widest text-mist">OEE</span>
      </div>
    </div>
  )
}
