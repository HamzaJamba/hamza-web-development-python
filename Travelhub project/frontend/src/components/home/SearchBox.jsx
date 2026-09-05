import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, MapPin, Calendar, Users } from 'lucide-react'

export default function SearchBox() {
  const [form, setForm] = useState({ destination: '', checkIn: '', checkOut: '', guests: 1 })
  const navigate = useNavigate()

  const handleSearch = (e) => {
    e.preventDefault()
    const params = new URLSearchParams(form).toString()
    navigate(`/hotels?${params}`)
  }

  return (
    <form
      onSubmit={handleSearch}
      className="bg-white/95 dark:bg-[#0f2422]/95 backdrop-blur rounded-2xl shadow-xl p-4 md:p-5 grid grid-cols-1 md:grid-cols-5 gap-3 max-w-4xl w-full"
    >
      <div className="flex items-center gap-2 border md:border-r md:border-t-0 md:border-b-0 md:border-l-0 border-black/10 dark:border-white/10 px-2">
        <MapPin size={16} className="text-[var(--color-primary)]" />
        <input
          type="text"
          placeholder="Destination"
          value={form.destination}
          onChange={(e) => setForm({ ...form, destination: e.target.value })}
          className="w-full py-2 bg-transparent outline-none text-sm"
        />
      </div>
      <div className="flex items-center gap-2 border md:border-r md:border-t-0 md:border-b-0 md:border-l-0 border-black/10 dark:border-white/10 px-2">
        <Calendar size={16} className="text-[var(--color-primary)]" />
        <input
          type="date"
          value={form.checkIn}
          onChange={(e) => setForm({ ...form, checkIn: e.target.value })}
          className="w-full py-2 bg-transparent outline-none text-sm"
        />
      </div>
      <div className="flex items-center gap-2 border md:border-r md:border-t-0 md:border-b-0 md:border-l-0 border-black/10 dark:border-white/10 px-2">
        <Calendar size={16} className="text-[var(--color-primary)]" />
        <input
          type="date"
          value={form.checkOut}
          onChange={(e) => setForm({ ...form, checkOut: e.target.value })}
          className="w-full py-2 bg-transparent outline-none text-sm"
        />
      </div>
      <div className="flex items-center gap-2 px-2">
        <Users size={16} className="text-[var(--color-primary)]" />
        <input
          type="number"
          min="1"
          value={form.guests}
          onChange={(e) => setForm({ ...form, guests: e.target.value })}
          className="w-full py-2 bg-transparent outline-none text-sm"
        />
      </div>
      <button
        type="submit"
        className="flex items-center justify-center gap-2 bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] text-white font-medium rounded-xl py-2.5 transition"
      >
        <Search size={16} /> Search
      </button>
    </form>
  )
}
